# Scraper Price Pulse

A Python-based web scraping tool that extracts business information from YellowPages.com. This tool performs a two-step scraping process: first collecting URLs, then scraping detailed information from each page.

## Overview

This scraper helps automate the collection of business data including:
- Business name (username)
- Email addresses (auto-generated)
- Phone numbers
- Addresses
- GPS coordinates (latitude/longitude)
- Provider types
- Additional business details

## Architecture

The project follows a two-phase approach:

### Phase 1: URL Collection (`main.py`)
- Scrapes YellowPages.com to collect business URLs for specific cities and provider types
- Saves URLs to CSV files for later processing
- Handles pagination and multiple cities
- Uses undetected Chrome driver to bypass bot detection

### Phase 2: Data Scraping (`scrape_urls.py`)
- Reads URLs from CSV files generated in Phase 1
- Visits each URL and extracts detailed business information
- Saves extracted data to CSV files
- Implements retry logic and error handling
- Handles Cloudflare challenges and bot detection

## Requirements

- Python 3.12 or higher
- Google Chrome browser
- ChromeDriver (compatible with Chrome version)
- Required Python packages (see Installation)

## Installation

1. **Clone or download the repository**
   ```bash
   cd scrapper_price_pulse
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate    # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   If requirements.txt doesn't exist, install manually:
   ```bash
   pip install selenium
   pip install undetected-chromedriver
   ```

4. **Install ChromeDriver**
   - Download ChromeDriver from: https://chromedriver.chromium.org/
   - Place it in your system PATH or specify the path in the code
   - Or let undetected-chromedriver handle it automatically

## Configuration Parameters

### Before Running - Check These Parameters:

#### In `main.py` (Lines 327-348)

**State to scrape:**
```python
states = ["ga"]  # Change to your desired state abbreviation
# Available: ak, al, ar, az, ca, co, ct, de, fl, ga, hi, etc.
```

**Alphabet page (for city listing):**
```python
alphabets = ["a"]  # Change to scrape different city groups (a-z)
# Options: ["a", "b", "c", ..., "z"] for all cities
```

**Cities to scrape:**
```python
cities_url = ["https://www.yellowpages.com/alpharetta-ga"]
cities = ["alpharetta"]
# Add more cities as needed:
# cities_url = ["https://www.yellowpages.com/atlanta-ga", "https://www.yellowpages.com/savannah-ga"]
# cities = ["atlanta", "savannah"]
```

**Provider types to scrape:**
```python
provider_types = {
    'chiropractics': 'chiropractics',
    #'dental-care': 'dental care',
    # Uncomment additional types:
    # 'diagnostic-center': 'medical diagnostic center',
    # 'primary-care': 'primary care',
    # 'urgent-care': 'urgent care',
    # 'vision-care': 'medical vision care',
    # 'imaging-labs': 'medical imaging labs',
    # 'physiotherapy': 'physiotherapy'
}
```

**Output folder:**
```python
folder = "Georgia"  # Line 66, 95 - Change to match your state
```

#### In `scrape_urls.py` (Lines 299-302)

**Configuration for scraping URLs:**
```python
state = "ga"           # State abbreviation
city_name = "alpharetta"  # City name (must match Phase 1)
key = "chiropractics"  # Provider type (must match Phase 1)
```

**Output folder:**
```python
folder = "Georgia/alpharetta"  # Line 139 - Update to match your state/city
```

## Usage

### Step 1: Collect URLs (Run `main.py`)

This script scrapes business URLs from YellowPages.com and saves them to CSV files.

```bash
python main.py
```

**What it does:**
- Navigates to YellowPages.com
- Searches for businesses in specified cities
- Filters by provider type (chiropractics, dental care, etc.)
- Collects all business URLs across multiple pages
- Saves URLs to: `{State}/{city}/{state}_{city}_{provider_type}_urls.csv`

**Output example:**
```
Georgia/alpharetta/ga_alpharetta_chiropractics_urls.csv
```

### Step 2: Scrape Data (Run `scrape_urls.py`)

This script reads URLs from CSV files and extracts detailed information.

```bash
python scrape_urls.py
```

**What it does:**
- Reads URLs from the CSV file generated in Step 1
- Visits each URL to extract business details
- Handles Cloudflare challenges and anti-bot measures
- Implements retry logic for failed requests
- Saves data to: `{State}/{city}/{state}_{city}_{provider_type}.csv`

**Output example:**
```
Georgia/alpharetta/ga_alpharetta_chiropractics.csv
```

**Scraped data includes:**
- Username (business name)
- Email (auto-generated)
- Phone Number
- Password (auto-generated)
- Address
- Latitude
- Longitude
- Provider Type
- Provider Name
- State
- City

### Important Notes

1. **Run `main.py` FIRST** - Always collect URLs before attempting to scrape data
2. **Configure parameters** - Update state, city, and provider type before running
3. **Chrome will open** - The scraper runs a visible Chrome browser window (not headless)
4. **Respect rate limits** - The script includes delays to avoid overloading servers
5. **Driver auto-refresh** - The driver reinitializes every 10 minutes to avoid detection
6. **Failed URLs** - Failed scrapes are saved to `*_failed.csv` for retry

## Output Structure

```
Georgia/
  └── alpharetta/
      ├── ga_alpharetta_chiropractics_urls.csv  # URLs from Phase 1
      ├── ga_alpharetta_chiropractics.csv        # Data from Phase 2
      ├── ga_alpharetta_dental-care_urls.csv
      ├── ga_alpharetta_dental-care.csv
      └── ga_alpharetta_chiropractics_failed.csv  # Failed URLs (if any)
```

## Features

- **Anti-Bot Detection**: Uses undetected-chromedriver to bypass bot detection
- **Cloudflare Bypass**: Handles Cloudflare challenges automatically
- **Error Handling**: Retry logic for failed requests (3 attempts per URL)
- **Resume Capability**: Can re-run scrape_urls.py to handle new URLs
- **Multiple Provider Types**: Scrape different business categories
- **State & City Scraping**: Configurable for any US state and city
- **Human-like Delays**: Random delays between requests to appear more human

## Configuration Tips

### For Maximum URLs

In `main.py`, uncomment all provider types:
```python
provider_types = {
    'chiropractics': 'chiropractics',
    'dental-care': 'dental care',
    'diagnostic-center': 'medical diagnostic center',
    'primary-care': 'primary care',
    'urgent-care': 'urgent care',
    'vision-care': 'medical vision care',
    'imaging-labs': 'medical imaging labs',
    'physiotherapy': 'physiotherapy'
}
```

### For Multiple States/Cities

In `main.py`:
```python
states = ["ga", "wa", "ny"]  # Multiple states

cities_url = [
    "https://www.yellowpages.com/atlanta-ga",
    "https://www.yellowpages.com/seattle-wa",
    "https://www.yellowpages.com/new-york-ny"
]
cities = ["atlanta", "seattle", "new-york"]
```

## Troubleshooting

### ChromeDriver Issues
- Ensure Chrome and ChromeDriver versions match
- Use `version_main=141` in the code to specify Chrome version
- Or let undetected-chromedriver auto-detect

### Cloudflare Blocks
- The script already includes bypass mechanisms
- If still blocked, increase delay times
- Try using proxies (configure in `PROXIES` list)

### Page Timeouts
- Increase `set_page_load_timeout` if internet is slow
- Check network connection
- Some pages may take longer to load

### No Results Found
- Verify city name and URL are correct
- Check if provider type exists in that city
- Some cities may not have certain provider types

## License

This project is for educational and research purposes. Please respect the terms of service of YellowPages.com and use responsibly.

## Disclaimer

This scraper is provided as-is for educational purposes. Always respect website terms of service and use web scraping responsibly. Be mindful of rate limits and don't overload servers with requests.

