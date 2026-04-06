# Horrorverse

Horrorverse is a data pipeline project that analyzes "Scream Queens" — actresses known for roles in horror films.

The system collects, processes, enriches, and ranks film data using a full ETL pipeline built with Python, SQLite, and Node.js.

---

## Features

* Web scraping of actress filmography (Wikipedia)
* Data cleaning and normalization pipeline
* Enrichment using OMDb API (box office, genres)
* SQLite database ingestion
* Ranking system based on custom scoring logic
* CLI script to display top actresses
* Optional Node.js API for querying rankings

---

## How It Works (ETL Pipeline)

1. **Extract**

   * Scrapes filmography data from Wikipedia

2. **Transform**

   * Filters horror movies
   * Normalizes fields (year, title, genres)
   * Enriches data with OMDb API

3. **Load**

   * Stores structured data in SQLite database

4. **Analyze**

   * Computes statistics and ranking scores

---

## Setup

### 1. Install dependencies

```bash
pip install -e .
npm install
```

---

## Run the Pipeline

```bash
./scripts/full_pipeline.sh
```

This will:

* Scrape data
* Enrich with OMDb
* Transform and clean
* Load into SQLite
* Generate final dataset

---

## Show Rankings

```bash
python -m scripts.show_top
```

Example output:

```
=== TOP SCREAM QUEENS ===

1. Lin Shaye
2. Dee Wallace
3. Danielle Harris
...
```

---

## Database

SQLite database:

```
data/db/horrorverse.sqlite3
```

Contains:

* actresses
* movies
* appearances
* computed stats

Note: The database is generated automatically by running the pipeline.
A sample dataset is provided in `data/sample/`.

---

## Project Structure

```
.
├── src/scream_queens/   # Scraper + pipeline logic (Python)
├── pipeline/            # ETL pipeline (transformation, ingestion)
├── domain/              # Ranking logic (JavaScript)
├── apps/                # API and worker
├── scripts/             # CLI + automation scripts
├── data/sample/         # Example output data
```

---

## Notes

* Some data (e.g. "survival" in horror movies) is not reliably available via APIs and is not fully implemented.
* Box office data depends on OMDb availability.

---

## Tech Stack

* Python (data pipeline)
* SQLite (storage)
* Node.js (API & ranking logic)
* Shell scripts (automation)

---

## Purpose

This project was built as a backend/data engineering exercise, focusing on:

* Data pipelines (ETL)
* API integration
* Data modeling
* Ranking algorithms
* Real-world project structure

---

## Author

Cristiano Noga (Chris)
Backend Developer — Python, APIs, Scraping, Data Systems
