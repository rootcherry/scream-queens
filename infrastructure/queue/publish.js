import amqp from "amqplib";

const RABBIT_URL = "amqp://localhost:5672";

export async function publishToQueue(queueName, message) {
  const connection = await amqp.connect(RABBIT_URL);
  const channel = await connection.createChannel();

  await channel.assertQueue(queueName, { durable: true });

  const payload = Buffer.from(JSON.stringify(message));

  channel.sendToQueue(queueName, payload, {
    persistent: true,
  });

  console.log("📨 Sent to queue:", queueName, message);

  await channel.close();
  await connection.close();
}
