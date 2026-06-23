import os
import time
import json
import signal
import sys
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from clickhouse_driver import Client

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
TOPIC = os.getenv('KAFKA_TOPIC', 'orders_topic')
CLICKHOUSE_HOST = os.getenv('CLICKHOUSE_HOST', 'clickhouse')
CLICKHOUSE_USER = os.getenv('CLICKHOUSE_USER', 'default')
CLICKHOUSE_PASSWORD = os.getenv('CLICKHOUSE_PASSWORD', '')

running = True

def signal_handler(sig, frame):
    global running
    print("\nShutting down consumer...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def wait_for_kafka(retries=20, delay=3):
    for i in range(retries):
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                auto_offset_reset='earliest',
                enable_auto_commit=True
            )
            consumer.close()
            print(f"Kafka ready at {KAFKA_BOOTSTRAP_SERVERS}")
            return True
        except NoBrokersAvailable:
            print(f"Waiting for Kafka... ({i+1}/{retries})")
            time.sleep(delay)
    return False

def wait_for_clickhouse(retries=20, delay=3):
    for i in range(retries):
        try:
            client = Client(host=CLICKHOUSE_HOST, user=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD)
            client.execute('SELECT 1')
            print(f"ClickHouse ready at {CLICKHOUSE_HOST}")
            return client
        except Exception as e:
            print(f"Waiting for ClickHouse... ({i+1}/{retries}) - {e}")
            time.sleep(delay)
    raise Exception("ClickHouse not available")

def create_table(client):
    client.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id String,
            user_id Int32,
            timestamp Int64,
            product_category String,
            product_name String,
            brand String,
            price Float32,
            quantity Int32,
            total_amount Float32,
            total_with_discount Float32,
            discount Float32,
            channel String,
            city String,
            user_type String,
            promo String,
            experiment_group String,
            is_returned UInt8,
            is_weekend UInt8,
            has_card UInt8,
            card_discount Float32,
            bonus_earned Float32
        ) ENGINE = MergeTree()
        ORDER BY timestamp
    ''')

def main():
    if not wait_for_kafka():
        sys.exit(1)
    client = wait_for_clickhouse()
    create_table(client)

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    print(f"Consumer started, listening to '{TOPIC}'")

    for message in consumer:
        if not running:
            break
        order = message.value
        try:
            client.execute('INSERT INTO orders FORMAT JSONEachRow', [order])
            print(f"Inserted: {order}")
        except Exception as e:
            print(f"Insert error: {e}")

    consumer.close()
    print("Consumer stopped.")

if __name__ == "__main__":
    main()