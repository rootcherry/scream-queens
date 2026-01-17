import json
import pika

RABBIT_HOST = "localhost"
RABBIT_USER = "guest"
RABBIT_PASS = "guest"
QUEUE_NAME = "horrorverse_jobs"


def main() -> int:
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    params = pika.ConnectionParameters(
        host=RABBIT_HOST,
        credentials=credentials,
    )

    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    print(f"🐇 Worker connected. Waiting for messages on '{QUEUE_NAME}'...")

    def on_message(ch, method, properties, body: bytes) -> None:
        try:
            payload = json.loads(body.decode("utf-8"))
            print("✅ Received job:")
            print(json.dumps(payload, indent=2))
        except Exception as exc:
            print("❌ Failed to parse message:", exc)
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
