import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

import pika

RABBIT_HOST = "localhost"
RABBIT_USER = "guest"
RABBIT_PASS = "guest"
QUEUE_NAME = "horrorverse_jobs"

DB_PATH = Path("data/db/horrorverse.sqlite3")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def insert_job_record(job_type: str, queen_id: int | None, status: str, created_at: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO jobs (job_type, queen_id, status, created_at, finished_at)
        VALUES (?, ?, ?, ?, ?);
        """,
        (job_type, queen_id, status, created_at, utc_now_iso()),
    )
    conn.commit()
    job_id = int(cur.lastrowid)
    conn.close()

    return job_id


def main() -> int:
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    params = pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)

    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    print(f"🐇 Worker connected. Waiting for messages on '{QUEUE_NAME}'...")

    def on_message(ch, method, properties, body: bytes) -> None:
        try:
            payload = json.loads(body.decode("utf-8"))
            print("✅ Received job:")
            print(json.dumps(payload, indent=2))

            job_type = str(payload.get("type", "UNKNOWN"))
            created_at = str(payload.get("createdAt", utc_now_iso()))

            raw_queen_id = payload.get("payload", {}).get("queenId")
            queen_id = int(raw_queen_id) if isinstance(raw_queen_id, int) else None

            job_id = insert_job_record(
                job_type=job_type,
                queen_id=queen_id,
                status="completed",
                created_at=created_at,
            )

            print(f"🗄️  Stored job in SQLite: id={job_id}")

        except Exception as exc:
            print("❌ Worker failed:", exc)
            print("Raw body:", body)
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
