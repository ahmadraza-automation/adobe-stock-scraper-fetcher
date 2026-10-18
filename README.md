# Adobe Stock Scraper Fetcher

> Professional Adobe Stock data fetcher powered by Apify actor [`kawsar/adobe-stock-scraper`](https://apify.com/kawsar/adobe-stock-scraper)

Fetches high-quality stock assets by keywords, exports clean **CSV** + **JSON**, and automatically removes duplicates.

---

## Features

- Multi-keyword support in one run
- Automatic duplicate removal (by `assetId`)
- Flattened CSV output (nested fields handled)
- Configurable max items & sort order
- Rate-limit friendly (delay between keywords)
- Clean project structure

---

## Quick Start

### 1. Install dependency

```bash
pip install -r requirements.txt
```

### 2. Set your Apify token

**Windows (PowerShell)**
```powershell
$env:APIFY_TOKEN = "apify_api_xxxxx"
```

**Linux / macOS**
```bash
export APIFY_TOKEN="apify_api_xxxxx"
```

### 3. Run

```bash
python tas_fetch.py "keyword1,keyword2,keyword3" [max_items] [order]
```

### Examples

```bash
# Default (200 items, ordered by downloads)
python tas_fetch.py "ghibli,studio ghibli,miyazaki"

# 800 items per keyword
python tas_fetch.py "ghibli,studio ghibli,miyazaki" 800 downloads

# Custom order
python tas_fetch.py "nature,landscape,mountain" 500 relevance
```

---

## Output Structure

```
tas_output/
├── ghibli.csv
├── ghibli_raw.json
├── studio_ghibli.csv
├── studio_ghibli_raw.json
├── all_combined.csv          ← final clean file
└── all_combined_raw.json
```

---

## Notes

- Max items per query is capped at **1000** (actor limit)
- Default order: `downloads`
- 3-second delay between keywords
- Output folder is auto-created and ignored by git

---

## Author

**Ahmad Raza**  
[GitHub](https://github.com/ahmadraza-automation)
