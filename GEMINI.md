# Gemini Instructional Context - Estonian Traditional Music Scraper

This project is a specialized web scraping and data collection tool for the **Anthology of Estonian Traditional Music** (Online Edition, 2016). It is designed for research purposes to build a structured dataset for NLP and musicological analysis.

## Project Overview

- **Purpose**: Automates the extraction of traditional Estonian songs, including archival audio, music notation images, and dual-language lyrics.
- **Technologies**: Python 3, `BeautifulSoup4` (web parsing), `requests` (HTTP), and `json` (metadata management).
- **Core Logic**:
    - Scrapes `folklore.ee` to discover and iterate through 115 song recordings.
    - Preserves linguistic nuances by keeping `<sup>` tags in transcriptions.
    - Maps performer names to their profile URLs and extracts geographic recording regions.
    - Aggregates all individual song data into a single root `metadata.json` for easy programmatic iteration.

## Building and Running

### Prerequisites
- Python 3.x
- Required libraries: `pip install requests beautifulsoup4`

### Commands
- **Execute Full Scrape**: `python3 scraper.py`
- **Limited Scrape (Test)**: `python3 scraper.py <count>` (e.g., `python3 scraper.py 5`)
- **Metadata Catalog**: The scraper automatically updates the root `metadata.json` upon completion (via the aggregation logic).

## Data Structure

- **`data/`**: Subdirectories for each song named as `{ID}_{Title}`.
    - `lyrics_estonian.txt`: Original Estonian lyrics with transcriptive markups.
    - `lyrics_english.txt`: English translations (where available).
    - `{ID}_notation.png`: Archival notation image.
    - `{ID}.mp3` / `{ID}.ogg`: Audio recordings.
    - `{ID}_metadata.json`: Song-specific details.
- **`metadata.json`**: Root catalog containing all metadata and relative paths to local files.

## Development Conventions

- **Scraping Ethics**: The script checks for existing files (`os.path.exists`) to avoid redundant requests.
- **Text Preservation**: The `clean_text` function in `scraper.py` is critical—it ensures HTML rendering (like `<br>` and `<p>`) is accurately reflected in the text files while preserving `<sup>` tags.
- **Metadata schema**: Always include `id`, `title`, `performer_name`, `performer_url`, and `region`.
