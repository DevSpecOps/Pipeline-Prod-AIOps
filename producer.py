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
MAX_MESSAGES = int(os.getenv('MAX_MESSAGES', 0))  # 0 = infinite

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

def generate_order():
    """Generate realistic order data with weighted categories and lognormal distribution."""
    # Weighted categories (realistic distribution)
    categories = ['Electronics', 'Clothing', 'Books', 'Home']
    weights = [0.4, 0.3, 0.2, 0.1]
    category = random.choices(categories, weights=weights)[0]

    # Base amount by category + lognormal distribution
    base_amounts = {'Electronics': 300, 'Clothing': 150, 'Books': 80, 'Home': 200}
    base = base_amounts[category]
    amount = round(random.lognormvariate(4.5, 0.8), 2)
    amount = max(10, min(500, amount))

    return {
        'order_id': str(uuid.uuid4()),
        'user_id': random.randint(1, 1000),
        'amount': amount,
        'product_category': category,
        'timestamp': int(time.time())
    }

def main():
    if not wait_for_kafka():
        sys.exit(1)
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print(f"Producer started, topic '{TOPIC}', interval {SLEEP_INTERVAL}s")
    print(f"Max messages: {'unlimited' if MAX_MESSAGES == 0 else MAX_MESSAGES}")

    count = 0
    while running:
        order = generate_order()
        try:
            producer.send(TOPIC, value=order)
            print(f"Sent: {order}")
            count += 1
            if MAX_MESSAGES > 0 and count >= MAX_MESSAGES:
                print(f"Reached max messages: {MAX_MESSAGES}. Shutting down.")
                break
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(SLEEP_INTERVAL)
    producer.flush()
    producer.close()
    print("Producer stopped.")

if __name__ == "__main__":
    main()