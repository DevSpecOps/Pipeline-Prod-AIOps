import pytest
from testcontainers.kafka import KafkaContainer
from testcontainers.clickhouse import ClickHouseContainer
from kafka import KafkaProducer
import json

@pytest.fixture(scope="session")
def kafka_container():
    with KafkaContainer() as kafka:
        yield kafka

@pytest.fixture(scope="session")
def clickhouse_container():
    with ClickHouseContainer() as ch:
        yield ch

@pytest.fixture
def kafka_producer(kafka_container):
    producer = KafkaProducer(
        bootstrap_servers=kafka_container.get_bootstrap_server(),
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    yield producer
    producer.close()