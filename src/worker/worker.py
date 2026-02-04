import json
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timezone

import pika

RABBIT_HOST = "localhost"
RABBIT_USER = "guest"
RABBIT_PASS = "guest"
QUEUE_NAME = "horrorverse_jobs"

DB_PATH = Path("data/db/horrorverse.sqlite3")


def utc_now_iso() -> str:
    # Ex: 2026-01-22T14:12:33+00:00
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_job(job_type: str, queen_id: int | None, created_at: str) -> int:
    """
    Create a new job in SQLite with status 'queued'.
    (Worker V2: we will transition queued -> running -> completed/failed)
    """
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


def mark_job_failed(job_id: int, message: str) -> None:
    conn = get_conn()
    conn.execute(
        """
        UPDATE jobs
        SET status = ?, finished_at = ?, error = ?
        WHERE id = ?;
        """,
        ("failed", utc_now_iso(), message[:1000], job_id),
    )
    conn.commit()
    conn.close()


def recompute_stats_for_queen(queen_id: int) -> None:
    # Real work: compute derived stats from appearances + movies and persist them.

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

    movies_count = int(row[0])
    box_office_total = int(row[1])
    box_office_known_count = int(row[2])
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


def main() -> int:
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    params = pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)

    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    print(f"Worker connected. Waiting for messages on '{QUEUE_NAME}'...")


    def on_message(ch, method, properties, body: bytes) -> None:
        job_id: int | None = None
        try:
            payload = json.loads(body.decode("utf-8"))
            print("Received job:")
            print(json.dumps(payload, indent=2))

            job_type = str(payload.get("type", "UNKNOWN"))
            created_at = str(payload.get("createdAt", utc_now_iso()))

            raw_queen_id = payload.get("payload", {}).get("queenId")
            queen_id = int(raw_queen_id) if isinstance(raw_queen_id, int) else None

            # 1) Create job as queued (persist first!)
            job_id = create_job(job_type=job_type, queen_id=queen_id, created_at=created_at)
            print(f"Created job in SQLite: id={job_id} status=queued")

            # 2) Mark running
            mark_job_running(job_id)
            print(f"Job running: id={job_id}")

            # 3) Do real work later. For V2-min, just simulate work.
            # time.sleep(1)
            # 3) Do real work (V2 real)
            if job_type == "RECOMPUTE_STATS":
                if queen_id is None:
                    raise ValueError("queenId is required for RECOMPUTE_STATS")
                recompute_stats_for_queen(queen_id)
            else:
                # For unknown job types, fail fast (keeps status trustworthy).
                raise ValueError(f"Unsupported job type: {job_type}")


            # 4) Mark completed
            mark_job_completed(job_id)
            print(f"Job completed: id={job_id}")

        except Exception as exc:
            print("Worker failed:", exc)
            print("Raw body:", body)

            # If we managed to create the job, mark it failed too.
            if job_id is not None:
                mark_job_failed(job_id, str(exc))
                print(f"Job failed recorded: id={job_id}")

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
