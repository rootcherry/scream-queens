import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pika

# retry config
MAX_JOB_ATTEMPTS = 3

# rabbit config
RABBIT_HOST = "localhost"
RABBIT_USER = "guest"
RABBIT_PASS = "guest"
QUEUE_NAME = "horrorverse_jobs"

# sqlite db path
DB_PATH = Path("data/db/horrorverse.sqlite3")


# get current UTC time in ISO format
def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# open sqlite connection
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), timeout=10, check_same_thread=False)

    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")  # better perf xFULL

    return conn


# insert new job as queued
def create_job(job_type: str, queen_id: int | None, created_at: str) -> int:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO jobs (job_type, queen_id, status, created_at)
        VALUES (?, ?, ?, ?);
        """,
        (job_type, queen_id, "queued", created_at),
    )

    conn.commit()
    job_id = int(cur.lastrowid)
    conn.close()

    return job_id


# mark job as running
def mark_job_running(job_id: int) -> None:
    conn = get_conn()

    conn.execute(
        """
        UPDATE jobs
        SET status = ?, started_at = ?
        WHERE id = ?;
        """,
        ("running", utc_now_iso(), job_id),
    )

    conn.commit()
    conn.close()


# mark job as completed
def mark_job_completed(job_id: int) -> None:
    conn = get_conn()

    conn.execute(
        """
        UPDATE jobs
        SET status = ?, finished_at = ?
        WHERE id = ?;
        """,
        ("completed", utc_now_iso(), job_id),
    )

    conn.commit()
    conn.close()


# mark job as failed and increment attempts
def mark_job_failed(job_id: int, message: str) -> int:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE jobs
        SET status = ?, finished_at = ?, error = ?, attempts = attempts + 1
        WHERE id = ?;
        """,
        ("failed", utc_now_iso(), message[:1000], job_id),
    )

    conn.commit()

    cur.execute("SELECT attempts FROM jobs WHERE id = ?", (job_id,))
    attempts = int(cur.fetchone()[0])

    conn.close()
    return attempts


# compute stats for a queen and store in queen_stats
def recompute_stats_for_queen(queen_id: int) -> None:
    conn = get_conn()

    row = conn.execute(
        """
        SELECT
          COUNT(*) AS movies_count,
          COALESCE(SUM(COALESCE(m.box_office, 0)), 0) AS box_office_total,
          SUM(CASE WHEN m.box_office IS NOT NULL THEN 1 ELSE 0 END) AS box_office_known_count,
          MIN(m.year) AS first_movie_year,
          MAX(m.year) AS last_movie_year
        FROM appearances a
        JOIN movies m ON m.id = a.movie_id
        WHERE a.scream_queen_id = ?;
        """,
        (queen_id,),
    ).fetchone()

    movies_count = int(row[0] or 0)
    box_office_total = int(row[1] or 0)
    box_office_known_count = int(row[2] or 0)
    first_movie_year = row[3]
    last_movie_year = row[4]

    conn.execute(
        """
        INSERT INTO queen_stats (
          scream_queen_id, movies_count, box_office_total, box_office_known_count,
          first_movie_year, last_movie_year, recomputed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(scream_queen_id) DO UPDATE SET
          movies_count = excluded.movies_count,
          box_office_total = excluded.box_office_total,
          box_office_known_count = excluded.box_office_known_count,
          first_movie_year = excluded.first_movie_year,
          last_movie_year = excluded.last_movie_year,
          recomputed_at = excluded.recomputed_at;
        """,
        (
            queen_id,
            movies_count,
            box_office_total,
            box_office_known_count,
            first_movie_year,
            last_movie_year,
            utc_now_iso(),
        ),
    )

    conn.commit()
    conn.close()

    print(
        "Recomputed stats:",
        f"queen_id={queen_id}",
        f"movies_count={movies_count}",
        f"box_office_total={box_office_total}",
    )


# safe payload parser
def parse_payload(raw):
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:
            return {}
    return raw or {}


def main() -> int:
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    params = pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)

    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    print(f"Worker connected. Waiting for messages on '{QUEUE_NAME}'...")

    def on_message(ch, method, properties, body: bytes) -> None:
        job_id: int | None = None
        parsed_job = None

        try:
            parsed_job = json.loads(body.decode("utf-8"))

            print("Received job:")
            print(json.dumps(parsed_job, indent=2))

            # correct fields from API
            job_type = str(parsed_job.get("job_type", "UNKNOWN"))
            created_at = str(parsed_job.get("created_at", utc_now_iso()))

            # parse payload safely
            payload = parse_payload(parsed_job.get("payload"))
            queen_id = payload.get("queenId")

            if queen_id is not None:
                queen_id = int(queen_id)

            # create job in DB
            job_id = create_job(job_type, queen_id, created_at)
            print(f"Job created: id={job_id}")

            # mark running
            mark_job_running(job_id)
            print(f"Job running: id={job_id}")

            # execute
            if job_type == "RECOMPUTE_STATS":
                if queen_id is None:
                    raise ValueError("queenId is required")
                recompute_stats_for_queen(queen_id)
            else:
                raise ValueError(f"Unsupported job type: {job_type}")

            # mark completed
            mark_job_completed(job_id)
            print(f"Job completed: id={job_id}")

        except Exception as exc:
            print("Worker failed:", exc)
            print("Raw body:", body)

            if job_id is not None:
                attempts = mark_job_failed(job_id, str(exc))
                print(f"Job failed: id={job_id}, attempts={attempts}")

                if attempts < MAX_JOB_ATTEMPTS and parsed_job is not None:
                    ch.basic_publish(
                        exchange="",
                        routing_key=QUEUE_NAME,
                        body=json.dumps(parsed_job),
                        properties=pika.BasicProperties(delivery_mode=2),
                    )
                    print(f"Job requeued: id={job_id}")

        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nStopping worker...")
    finally:
        try:
            connection.close()
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
