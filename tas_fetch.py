"""
Adobe Stock data fetcher (Apify actor: kawsar/adobe-stock-scraper) - Improved

Token set karo:
    $env:APIFY_TOKEN = "apify_api_xxxxx"

Chalane ka tareeqa:
  python tas_fetch.py "ghibli,studio ghibli,miyazaki" 800 downloads
"""
import csv
import json
import os
import re
import sys
import time
from datetime import datetime
import requests

ACTOR = "kawsar~adobe-stock-scraper"
URL = f"https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items"
HARD_MAX = 1000
DEFAULT_MAX = 200
DEFAULT_ORDER = "downloads"
SLEEP_BETWEEN = 3


def build_input(query, max_items, order):
    return {
        "query": query,
        "maxItems": max_items,
        "assetType": "all",
        "priceFilter": "all",
        "orientation": "all",
        "aiFilter": "all",
        "iconOption": "all",
        "order": order,
        "timeoutSecs": 400,
        "requestTimeoutSecs": 40,
        "proxyConfiguration": {"useApifyProxy": True},
    }


def flatten(row, prefix=""):
    out = {}
    for k, v in row.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(flatten(v, key + "."))
        elif isinstance(v, list):
            if all(not isinstance(i, (dict, list)) for i in v):
                out[key] = ", ".join(map(str, v))
            else:
                out[key] = json.dumps(v, ensure_ascii=False)
        else:
            out[key] = v
    return out


def slugify(text):
    return re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_") or "query"


def save_single(items, query, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    slug = slugify(query)
    raw_path = os.path.join(out_dir, f"{slug}_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    rows = [flatten(i) for i in items]
    columns = []
    for r in rows:
        for k in r:
            if k not in columns:
                columns.append(k)
    csv_path = os.path.join(out_dir, f"{slug}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return raw_path, csv_path, columns


def save_combined(all_items, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    seen = set()
    unique = []
    for item in all_items:
        aid = item.get("assetId")
        if aid is None or aid in seen:
            continue
        seen.add(aid)
        unique.append(item)
    raw_path = os.path.join(out_dir, "all_combined_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)
    rows = [flatten(i) for i in unique]
    columns = []
    for r in rows:
        for k in r:
            if k not in columns:
                columns.append(k)
    csv_path = os.path.join(out_dir, "all_combined.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return raw_path, csv_path, len(unique), len(all_items) - len(unique)


def fetch_one(token, query, max_items, order):
    print(f"\n[*] Searching: '{query}'  (maxItems={max_items}, order={order})")
    try:
        resp = requests.post(
            URL,
            params={"token": token},
            json=build_input(query, max_items, order),
            timeout=420,
        )
    except requests.exceptions.RequestException as e:
        print(f"[!] Network error: {e}")
        return None
    if resp.status_code not in (200, 201):
        print(f"[!] Apify error {resp.status_code}: {resp.text[:400]}")
        if resp.status_code == 401:
            print("    -> Token galat/expired hai.")
        elif resp.status_code == 402:
            print("    -> Apify credits khatam hain.")
        elif resp.status_code == 400:
            print("    -> Input galat ho sakti hai.")
        return None
    items = resp.json()
    if not isinstance(items, list):
        print("[!] Unexpected response format.")
        return None
    if not items:
        print("[!] Is keyword pe koi result nahi mila.")
        return []
    return items


def parse_args():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    keywords_raw = sys.argv[1]
    keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]
    max_items = DEFAULT_MAX
    order = DEFAULT_ORDER
    if len(sys.argv) > 2:
        try:
            max_items = int(sys.argv[2])
        except ValueError:
            print("[!] maxItems number hona chahiye.")
            sys.exit(1)
    if len(sys.argv) > 3:
        order = sys.argv[3].lower()
    if max_items > HARD_MAX:
        print(f"[!] maxItems {max_items} > {HARD_MAX}. Actor limit ki wajah se {HARD_MAX} set kar raha hoon.")
        max_items = HARD_MAX
    if max_items < 1:
        max_items = DEFAULT_MAX
    return keywords, max_items, order


def main():
    keywords, max_items, order = parse_args()
    token = os.environ.get("APIFY_TOKEN", "").strip()
    if not token:
        print("APIFY_TOKEN set nahi hai.")
        sys.exit(1)
    out_dir = "tas_output"
    print("=" * 60)
    print(f"Keywords     : {len(keywords)}")
    for i, k in enumerate(keywords, 1):
        print(f"  {i}. {k}")
    print(f"Max per query: {max_items}")
    print(f"Order        : {order}")
    print(f"Output folder: {out_dir}/")
    print("=" * 60)
    all_items = []
    success_count = 0
    total_fetched = 0
    for idx, query in enumerate(keywords):
        items = fetch_one(token, query, max_items, order)
        if items is None:
            print(f"[!] '{query}' skip ho gaya (error).")
            continue
        if items:
            raw_path, csv_path, columns = save_single(items, query, out_dir)
            print(f"[+] {len(items)} assets mile → {csv_path}")
            all_items.extend(items)
            total_fetched += len(items)
            success_count += 1
        else:
            print(f"[+] 0 assets (empty result)")
        if idx < len(keywords) - 1:
            print(f"    ... {SLEEP_BETWEEN}s wait (next keyword) ...")
            time.sleep(SLEEP_BETWEEN)
    if all_items:
        print("\n" + "=" * 60)
        print("[*] Combining all results + removing duplicates by assetId ...")
        raw_path, csv_path, unique_count, dup_count = save_combined(all_items, out_dir)
        print(f"[+] Total fetched      : {total_fetched}")
        print(f"[+] Unique assets      : {unique_count}")
        print(f"[+] Duplicates removed : {dup_count}")
        print(f"[+] Combined CSV       : {csv_path}")
        print(f"[+] Combined Raw JSON  : {raw_path}")
        print("=" * 60)
        print(f"Done! {success_count}/{len(keywords)} keywords successful.")
    else:
        print("\n[!] Koi data nahi mila. Keywords ya token check karo.")


if __name__ == "__main__":
    main()
