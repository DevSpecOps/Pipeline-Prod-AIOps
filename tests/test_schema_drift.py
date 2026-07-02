import re
import pytest

def test_schema_consistency():
    """
    Ensure that the columns defined in consumer.py's CREATE TABLE
    match the keys produced by producer.py's generate_order().
    """
    with open('consumer.py', 'r') as f:
        consumer_content = f.read()
    match = re.search(r'CREATE TABLE IF NOT EXISTS orders \(([^)]+)\)', consumer_content, re.DOTALL)
    assert match, "CREATE TABLE not found in consumer.py"
    columns = re.findall(r'(\w+)\s+', match.group(1))
    keywords = {'ENGINE', 'MergeTree', 'ORDER', 'BY', 'timestamp', 'IF', 'NOT', 'EXISTS'}
    consumer_cols = [c for c in columns if c not in keywords and not c.isdigit() and c != 'TABLE']

    with open('producer.py', 'r') as f:
        producer_content = f.read()
    match = re.search(r'return\s*\{([^}]+)\}', producer_content, re.DOTALL)
    assert match, "Return dict not found in producer.py"
    keys = re.findall(r"'(\w+)':", match.group(1))
    producer_keys = set(keys)

    consumer_set = set(consumer_cols)
    missing = consumer_set - producer_keys
    assert not missing, f"Producer missing columns: {missing}"
    extra = producer_keys - consumer_set
    if extra:
        print(f"Producer has extra columns (not in consumer): {extra}")

    print("Schema consistency check passed.")