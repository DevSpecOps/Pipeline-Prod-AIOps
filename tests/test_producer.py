import pytest
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

def test_producer_connection():
    """Verify that Kafka is reachable and a producer can be created."""
    try:
        producer = KafkaProducer(bootstrap_servers='localhost:9092')
        producer.close()
    except NoBrokersAvailable:
        pytest.skip("Kafka is not available")
    except Exception as e:
        pytest.fail(f"Failed to connect to Kafka: {e}")