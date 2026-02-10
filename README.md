# Eesti Rahvamuusika Antoloogia Scraper

This project contains a Python-based scraper for the **Anthology of Estonian Traditional Music** (Online Edition, 2016), sourced from [folklore.ee](https://www.folklore.ee/pubte/eraamat/rahvamuusika/en/index).

**Research Notice**: This scraper was developed for research purposes. Please note that the downloaded data (audio, notation, and lyrics) is **not shared** in this repository. Users must run the scraper themselves at their own risk to populate the dataset.

## Data Structure

The dataset is organized into the `data/` directory, with one folder per song.

- `data/`
  - `{ID}_{Title}/`
    - `{ID}.mp3`: Audio recording (MP3 format).
    - `{ID}.ogg`: Audio recording (OGG format).
    - `{ID}_notation.png`: Music notation image.
    - `lyrics_estonian.txt`: Original Estonian lyrics (if available).
    - `lyrics_english.txt`: English translation (if available).
    - `{ID}_metadata.json`: Song-specific metadata.

## Catalog

A root-level `metadata.json` file provides a comprehensive catalog of all 115 recordings. This allows for computational analysis without traversing the directory structure.

Each entry includes:
- `id`: Three-digit song identifier.
- `title`: English title of the song.
- `performer_name`: Name of the primary performer.
- `performer_url`: Link to the performer's profile.
- `region`: The Estonian region/parish where the song was recorded.
- `original_url`: The source URL of the song page.
- `local_files`: Relative paths to the downloaded assets.

## Scraper Usage

The `scraper.py` script can be used to re-fetch or update the data.

### Dependencies
- Python 3.x
- `requests`
- `beautifulsoup4`

Install dependencies:
```bash
pip install beautifulsoup4 requests
```

### Running the Scraper
Run the full scrape:
```bash
python3 scraper.py
```

Run a test scrape (limited to first N songs):
```bash
python3 scraper.py 5
```