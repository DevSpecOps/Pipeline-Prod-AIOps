def test_producer_send(kafka_producer):
    future = kafka_producer.send('test-topic', value={'test': 1})
    result = future.get(timeout=5)
    assert result.topic == 'test-topic'