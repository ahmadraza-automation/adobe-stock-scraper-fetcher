# Adobe Stock Scraper Fetcher

Adobe Stock data fetcher using Apify actor [`kawsar/adobe-stock-scraper`](https://apify.com/kawsar/adobe-stock-scraper).

Fetches assets by keywords, saves individual + combined results as **CSV** and **JSON**.

## Setup

1. Get your Apify API token from [Apify Console](https://console.apify.com/account/integrations)
2. Set the environment variable:

**Windows (PowerShell):**
```powershell
$env:APIFY_TOKEN = "apify_api_xxxxx"
```

**Linux / macOS:**
```bash
export APIFY_TOKEN="apify_api_xxxxx"
```

3. Install dependency:
```bash
pip install requests
```

## Usage

```bash
python tas_actor_fetch.py "keyword1,keyword2,keyword3" [max_items] [order]
```

### Examples

```bash
# Default: 200 items per keyword, ordered by downloads
python tas_actor_fetch.py "ghibli,studio ghibli,miyazaki"

# 800 items per keyword, ordered by downloads
python tas_actor_fetch.py "ghibli,studio ghibli,miyazaki" 800 downloads

# Custom order (relevance / newest / downloads etc.)
python tas_actor_fetch.py "nature,landscape" 500 relevance
```

## Output

All files are saved in the `tas_output/` folder:

- `{keyword}.csv` + `{keyword}_raw.json` → per keyword
- `all_combined.csv` + `all_combined_raw.json` → all results combined (duplicates removed by `assetId`)

## Notes

- Max items per query is capped at **1000** (actor limit)
- Default order: `downloads`
- 3 second delay between keywords to be polite to the API
