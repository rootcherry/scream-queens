# 🎃 Horrorverse (Scream Queens) 🧛‍♀️

A **backend-first data project** that combines data engineering, DSA in JavaScript, REST APIs, and message queues to process and serve information about “Scream Queens” in horror cinema.

This project was built locally on **Linux**, using **Python, Node.js, SQLite, Express, RabbitMQ, and tmux automation**.

---

## 🎯 What this project does

Horrorverse currently provides:

* A **Python data pipeline** that scrapes and cleans data into structured JSON.
* A **local SQLite database** as the source of truth.
* A **Map-based DSA layer in JavaScript** for rankings and filters.
* A **REST API (Express)** that reads directly from SQLite.
* An **asynchronous job system** using **RabbitMQ + Python worker**.
* A **one-command dev environment** using **tmux**.

---

## 🧱 High-level architecture

```
Pipeline (Python)
        ↓
Processed JSON
        ↓
SQLite (horrorverse.sqlite3)
        ↓
DSA (Node + Maps)   →   Express API
                            ↓
                      RabbitMQ Queue
                            ↓
                        Python Worker
                            ↓
                         Jobs Table
```

---

## ✅ Prerequisites

You need to have installed:

* Node.js 20+
* Python 3.12+
* Docker & docker-compose
* tmux
* xclip (optional, for clipboard support in tmux)

---

## 🚀 Quick start (recommended)

From the project root:

```bash
./bin/horrorverse
```

This will open a tmux session named **horrorverse** with 6 windows:

1. **project** – main working directory
2. **git** – for commits and status
3. **api** – runs `npm run dev`
4. **worker** – runs the Python RabbitMQ worker
5. **docker** – starts RabbitMQ + shows logs
6. **client** – for curl/sqlite tests

To exit tmux without stopping services:

```
Ctrl + b, then d
```

To return:

```bash
tmux a -t horrorverse
```

---

## 🛠️ Manual start (without tmux)

If you **do not have tmux** or prefer a simple terminal setup, you can start everything in separate terminals:

### 1) Start RabbitMQ (Docker)

```bash
docker-compose up -d
```

### 2) Start the API

```bash
npm run dev
```

(keeps running on [http://localhost:3000](http://localhost:3000))

### 3) Start the Python worker

```bash
source .venv/bin/activate
python src/worker/worker.py
```

You can then use `curl` from any terminal exactly as shown in the examples below.

---

## 🌐 API Endpoints

> The examples below use `| jq` for readability (optional).
> You can omit `| jq` if you don’t have it installed.

### Health

```bash
GET /health
```

### Rankings

```bash
GET /rankings
GET /rankings/:key
```

Example:

```bash
curl -s http://localhost:3000/rankings/filmCount | jq
```

### Scream Queens

```bash
GET /scream-queens
GET /scream-queens/:id
GET /scream-queens/:id/films?order=desc&limit=10
```

Example:

```bash
curl -s "http://localhost:3000/scream-queens/1/films?order=desc&limit=5" | jq
```

### Jobs (asynchronous processing)

Enqueue a job:

```bash
curl -X POST http://localhost:3000/jobs/recompute \
  -H "Content-Type: application/json" \
  -d '{"queenId": 1}'
```

List recent jobs:

```bash
curl -s http://localhost:3000/jobs | jq
```

Get one job by id:

```bash
curl -s http://localhost:3000/jobs/1 | jq
```

---

## 🐇 RabbitMQ

RabbitMQ runs in Docker and is available at:

```
http://localhost:15672
```

Default credentials:

* user: **guest**
* password: **guest**

Queue used by the project:

```
horrorverse_jobs
```

---

## 🗄️ Database

Local SQLite database:

```
data/db/horrorverse.sqlite3
```

Key tables:

* `scream_queens`
* `movies`
* `appearances`
* `jobs` (queue persistence)

You can inspect it with:

```bash
sqlite3 data/db/horrorverse.sqlite3
```

---

## 📁 Project structure (simplified)

```
.
├── api/
│   └── routes/
├── src/
│   ├── db/
│   ├── queue/
│   └── worker/
├── scripts/py/
├── data/
│   ├── raw/
│   ├── processed/
│   └── db/
├── docker-compose.yml
├── bin/horrorverse
└── scripts/start_horrorverse.sh
```

---

## 📌 What’s next (roadmap)

Possible next steps:

* Add **ESLint + Prettier** (code quality + formatting)
* Make the worker **actually recompute stats** in SQLite
* Add **API tests** with Jest + Supertest
* Improve SQL queries and indexes

---

Made with ☕, 🐍, and 🎃
