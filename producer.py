import os
import time
import json
import uuid
import random
import signal
import sys
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

# Configuration from environment variables
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
TOPIC = os.getenv('KAFKA_TOPIC', 'orders_topic')
SLEEP_INTERVAL = float(os.getenv('PRODUCER_SLEEP', '1.0'))

running = True

def signal_handler(sig, frame):
    global running
    print("\nShutting down producer...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def wait_for_kafka(retries=20, delay=3):
    """Wait for Kafka to become available."""
    for i in range(retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            producer.close()
            print(f"Kafka ready at {KAFKA_BOOTSTRAP_SERVERS}")
            return True
        except NoBrokersAvailable:
            print(f"Waiting for Kafka... ({i+1}/{retries})")
            time.sleep(delay)
    print("ERROR: Kafka not available")
    return False

def main():
    if not wait_for_kafka():
        sys.exit(1)
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print(f"Producer started, topic '{TOPIC}', interval {SLEEP_INTERVAL}s")
    while running:
        order = {
            'order_id': str(uuid.uuid4()),
            'user_id': random.randint(1, 1000),
            'amount': round(random.uniform(10, 500), 2),
            'product_category': random.choice(['Electronics', 'Clothing', 'Books', 'Home']),
            'timestamp': int(time.time())
        }
        try:
            producer.send(TOPIC, value=order)
            print(f"Sent: {order}")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(SLEEP_INTERVAL)
    producer.flush()
    producer.close()
    print("Producer stopped.")

if __name__ == "__main__":
    main()