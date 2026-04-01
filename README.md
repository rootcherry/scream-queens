# Horrorverse

Horrorverse is a backend-focused data platform for analyzing "Scream Queens" (actresses in horror films). It combines scraping, data processing, a SQLite database, and a Node.js API to expose rankings and insights.

---

## 🚀 Features

* Scraping and ingestion of actress data (Python)
* Data processing pipelines (cleaning, enrichment)
* SQLite database storage
* Ranking engine (DSA-focused logic in JavaScript)
* REST API (Node.js + Express)
* Queue/worker system for async jobs

---

## 📁 Project Structure

```
.
├── api/                # Express API (routes)
├── bin/                # CLI entrypoint
├── data/               # Raw, processed, cache, and DB
├── db/                 # Migrations
├── docs/               # Ideas and notes
├── domain/                # Ranking + filtering logic
├── scripts/            # Python + JS scripts
├── src/                # Core Python logic (scraper, processing, worker)
├── tests/              # Tests
├── docker-compose.yml
├── README.md
```

---

## ⚙️ Setup

### 1. Install dependencies

#### Python

```
pip install -r requirements.txt
```

#### Node.js

```
npm install
```

---

## 🧠 Data Pipeline

1. Scrape raw data → `data/raw/`
2. Process data → `data/processed/`
3. Enrich (box office, survival stats, etc.)
4. Store in SQLite → `data/db/horrorverse.sqlite3`

Run scripts from `scripts/py/` as needed.

---

## 🗄️ Database

SQLite database located at:

```
data/db/horrorverse.sqlite3
```

Run migrations:

```
sqlite3 data/db/horrorverse.sqlite3 < db/migrations/002_add_queen_stats.sql
```

---

## 🔌 API

Start server:

```
node api/server.js
```

Server runs at:

```
http://localhost:3000
```

---

## 📊 Endpoints

### Rankings

```
GET /rankings/:key
```

Example:

```
curl http://localhost:3000/rankings/filmCount
```

Response:

```
{
  "key": "filmCount",
  "order": "desc",
  "limit": 10,
  "results": [
    {
      "name": "Anya Taylor-Joy",
      "films": 1
    }
  ]
}
```

---

## 🧮 Ranking System (DSA)

Located in:

```
domain/
```

Includes:

* Filters (film count, survival, box office, etc.)
* Ranking strategies
* Registry pattern for extensibility

Run manually:

```
node scripts/js/testCoordinate.js
```

---

## ⚡ Worker & Queue

Queue system for async processing:

* Publisher: `src/queue/publish.js`
* Worker: `apps/worker/worker.py`

Used for heavy jobs (scraping, enrichment, updates)

---

## 🐳 Docker (optional)

```
docker-compose up --build
```

---

## 🧪 Tests

```
pytest
```

---

## 📌 Notes

* Hybrid architecture: Python (data) + Node.js (API)
* Focus on backend engineering and data pipelines
* Designed to be extensible (new rankings, filters, data sources)

---

## 🎯 Next Steps

* Add more actresses (scale dataset)
* Improve rankings (weighting, scoring)
* Add authentication (optional)
* Deploy API (Render, Railway, etc.)
* Build simple frontend (optional)

---

## 👤 Author

Cristiano Noga (Chris)

Backend Developer — Python, APIs, Scraping, Data Systems
