import logging
import subprocess
import time
import docker
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from clickhouse_driver import Client

# Настройка логирования
def setup_logger(name, log_file=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger

# Работа с Docker
def get_docker_client():
    return docker.from_env()

def stop_container(container_name):
    client = get_docker_client()
    try:
        container = client.containers.get(container_name)
        container.stop()
        logging.info(f"Container {container_name} stopped")
        return True
    except Exception as e:
        logging.error(f"Failed to stop {container_name}: {e}")
        return False

def start_container(container_name):
    client = get_docker_client()
    try:
        container = client.containers.get(container_name)
        container.start()
        logging.info(f"Container {container_name} started")
        return True
    except Exception as e:
        logging.error(f"Failed to start {container_name}: {e}")
        return False

# ClickHouse
def get_clickhouse_client():
    return Client(host='localhost', user='default', password='')

def get_clickhouse_disk_usage():
    client = get_clickhouse_client()
    result = client.execute("SELECT sum(bytes) FROM system.parts WHERE active")
    if result and result[0][0]:
        return result[0][0] / (1024**3)  # в GB
    return 0

def get_clickhouse_row_count():
    client = get_clickhouse_client()
    result = client.execute("SELECT count(*) FROM orders")
    return result[0][0] if result else 0

# Kafka lag (требуется kafka-python)
from kafka import KafkaAdminClient, KafkaConsumer
from kafka.admin import ConsumerGroupDescription

def get_consumer_lag(consumer_group='my-consumer-group', bootstrap_servers='localhost:9092'):
    admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
    try:
        group_description = admin.describe_consumer_groups([consumer_group])
        # Для простоты используем consumer для получения offset
        consumer = KafkaConsumer(
            bootstrap_servers=bootstrap_servers,
            group_id=consumer_group,
            auto_offset_reset='earliest'
        )
        # Получаем партиции и оффсеты
        partitions = consumer.assignment()
        if not partitions:
            return 0
        end_offsets = consumer.end_offsets(partitions)
        # Получаем текущую позицию (lag)
        lag = 0
        for tp in partitions:
            pos = consumer.position(tp)
            end = end_offsets[tp]
            lag += end - pos
        consumer.close()
        return lag
    except Exception as e:
        logging.error(f"Error getting lag: {e}")
        return -1

# Построение графика
def plot_latency_rps(results, output_file='latency_rps.html'):
    df = pd.DataFrame(results)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df['users'], y=df['rps'], name='RPS', mode='lines+markers'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['users'], y=df['p95'], name='p95 latency (ms)', mode='lines+markers'), secondary_y=True)
    fig.update_layout(title='API Performance: RPS vs Latency', xaxis_title='Users', template='plotly_white')
    fig.update_yaxes(title_text='RPS', secondary_y=False)
    fig.update_yaxes(title_text='Latency (ms)', secondary_y=True)
    fig.write_html(output_file)