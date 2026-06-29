import os
import time
import json
import uuid
import random
import signal
import sys
from datetime import datetime, timedelta
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

# ==================== CONFIGURATION ====================
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
TOPIC = os.getenv('KAFKA_TOPIC', 'orders_topic')
SLEEP_INTERVAL = float(os.getenv('PRODUCER_SLEEP', '0.5'))
MAX_MESSAGES = int(os.getenv('MAX_MESSAGES', 0))

running = True

# ==================== DOMAIN DATA ====================
PRODUCT_CATALOG = {
    'Clothing': {
        'subcategories': ['T-shirt', 'Jacket', 'Hoodie', 'Shorts', 'Pants'],
        'brands': ['Nike', 'Adidas', 'Puma', 'Columbia', 'Demix'],
        'price_range': (1500, 15000)
    },
    'Footwear': {
        'subcategories': ['Running Shoes', 'Sneakers', 'Hiking Boots', 'Sandals'],
        'brands': ['Nike', 'Adidas', 'Reebok', 'Puma', 'ECCO'],
        'price_range': (3000, 25000)
    },
    'Equipment': {
        'subcategories': ['Dumbbells', 'Yoga Mat', 'Resistance Bands', 'Kettlebell', 'Treadmill'],
        'brands': ['Demix', 'Kettler', 'Athlex', 'Torneo'],
        'price_range': (1000, 150000)
    },
    'Accessories': {
        'subcategories': ['Water Bottle', 'Gym Bag', 'Headband', 'Sunglasses', 'Smart Watch'],
        'brands': ['Soulway', 'Joss', 'Delamare'],
        'price_range': (500, 30000)
    },
    'Nutrition': {
        'subcategories': ['Protein Powder', 'Energy Bars', 'BCAA', 'Vitamins', 'Pre-workout'],
        'brands': ['MRM Nutrition', 'GENETICSLAB', 'Now Foods'],
        'price_range': (300, 6000)
    }
}

CATEGORY_WEIGHTS = [0.35, 0.25, 0.20, 0.12, 0.08]

CHANNELS = ['online_web', 'online_app', 'offline_store']
CHANNEL_WEIGHTS = [0.4, 0.3, 0.3]

USER_TYPES = ['new', 'regular', 'vip', 'club_member']
USER_TYPE_WEIGHTS = [0.2, 0.5, 0.1, 0.2]

PROMO_TYPES = ['', '10% off', '20% off', 'Buy 1 Get 1', 'Free Shipping']
PROMO_WEIGHTS = [0.6, 0.15, 0.1, 0.05, 0.1]

CITIES = ['Moscow', 'Saint Petersburg', 'Novosibirsk', 'Yekaterinburg', 'Kazan', 'Nizhny Novgorod', 'Chelyabinsk', 'Samara']

# ==================== HELPERS ====================
def weighted_choice(items, weights):
    return random.choices(items, weights=weights)[0]

def generate_price(category):
    price_range = PRODUCT_CATALOG[category]['price_range']
    base_price = random.uniform(price_range[0], price_range[1])
    final_price = base_price * random.uniform(0.8, 1.2)
    return round(final_price, 2)

def generate_quantity():
    return random.choices([1, 2, 3, 4, 5], weights=[0.7, 0.2, 0.05, 0.03, 0.02])[0]

def generate_order_id():
    return str(uuid.uuid4())

def generate_user_id():
    return random.randint(1, 10000)

def generate_timestamp():
    now = datetime.now()
    days_ago = random.randint(0, 7)
    hours_ago = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    dt = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
    return int(dt.timestamp())

def is_weekend(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    return dt.weekday() >= 5

def generate_experiment_group():
    return 'A' if random.random() < 0.5 else 'B'

def generate_returned():
    return random.random() < 0.05

def generate_loyalty(user_type):
    if user_type == 'vip':
        return {
            'has_card': True,
            'card_discount': round(random.uniform(10, 20), 1),
            'bonus_earned': round(random.uniform(50, 500), 2)
        }
    elif user_type == 'club_member':
        return {
            'has_card': True,
            'card_discount': round(random.uniform(5, 15), 1),
            'bonus_earned': round(random.uniform(20, 300), 2)
        }
    elif user_type == 'regular':
        if random.random() < 0.4:
            return {
                'has_card': True,
                'card_discount': round(random.uniform(3, 10), 1),
                'bonus_earned': round(random.uniform(10, 150), 2)
            }
    return {'has_card': False, 'card_discount': 0, 'bonus_earned': 0}

# ==================== ORDER GENERATION ====================
def generate_order():
    category = weighted_choice(list(PRODUCT_CATALOG.keys()), CATEGORY_WEIGHTS)
    product = random.choice(PRODUCT_CATALOG[category]['subcategories'])
    brand = random.choice(PRODUCT_CATALOG[category]['brands'])
    price = generate_price(category)
    quantity = generate_quantity()
    total = round(price * quantity, 2)
    timestamp = generate_timestamp()

    user_type = weighted_choice(USER_TYPES, USER_TYPE_WEIGHTS)
    loyalty = generate_loyalty(user_type)

    if loyalty['has_card']:
        discount = loyalty['card_discount']
        total_with_discount = round(total * (1 - discount / 100), 2)
    else:
        discount = 0
        total_with_discount = total

    return {
        'order_id': generate_order_id(),
        'user_id': generate_user_id(),
        'timestamp': timestamp,
        'product_category': category,
        'product_name': product,
        'brand': brand,
        'price': price,
        'quantity': quantity,
        'amount': total,
        'total_with_discount': total_with_discount,
        'discount': discount,
        'channel': weighted_choice(CHANNELS, CHANNEL_WEIGHTS),
        'city': random.choice(CITIES),
        'user_type': user_type,
        'promo': weighted_choice(PROMO_TYPES, PROMO_WEIGHTS),
        'experiment_group': generate_experiment_group(),
        'is_returned': generate_returned(),
        'is_weekend': is_weekend(timestamp),
        'has_card': loyalty['has_card'],
        'card_discount': loyalty['card_discount'],
        'bonus_earned': loyalty['bonus_earned']
    }

# ==================== SIGNAL HANDLING ====================
def signal_handler(sig, frame):
    global running
    print("\nShutting down producer...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ==================== KAFKA WAIT ====================
def wait_for_kafka(retries=20, delay=3):
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
    return False

# ==================== MAIN ====================
def main():
    if not wait_for_kafka():
        sys.exit(1)

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    print(f"Producer started (topic: {TOPIC})")
    print(f"Generating realistic sports retail orders every {SLEEP_INTERVAL}s")
    print(f"Max messages: {'unlimited' if MAX_MESSAGES == 0 else MAX_MESSAGES}")

    count = 0
    while running:
        order = generate_order()
        try:
            producer.send(TOPIC, value=order)
            producer.flush()
            print(f"Sent: {order}")
            count += 1
            if MAX_MESSAGES > 0 and count >= MAX_MESSAGES:
                print(f"Reached max messages: {MAX_MESSAGES}. Stopping.")
                break
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(SLEEP_INTERVAL)

    producer.flush()
    producer.close()
    print("Producer stopped.")

if __name__ == "__main__":
    main()