import pytest
from clickhouse_driver import Client

def test_clickhouse_connection():
    """Verify that ClickHouse is reachable and responds to a simple query."""
    client = Client(host='localhost', user='default', password='')
    result = client.execute('SELECT 1')
    assert result == [(1,)]