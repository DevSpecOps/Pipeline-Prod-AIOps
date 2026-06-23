import time
import sys
import os
sys.path.append(os.path.dirname(__file__))
from utils import setup_logger, get_clickhouse_disk_usage, get_clickhouse_row_count, get_docker_client
import subprocess
import threading
import signal
import docker

logger = setup_logger('clickhouse_fill', 'clickhouse_fill.log')

running = True

def signal_handler(sig, frame):
    global running
    logger.info("Interrupt received, stopping test...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

def test_disk_fill(target_gb=5, max_seconds=3600):
    logger.info(f"Starting ClickHouse disk fill test, target {target_gb} GB or max {max_seconds}s")
    start_time = time.time()

    client = get_docker_client()
    container = client.containers.get('pipeline-prod-aiops-producer-1')

    logger.info("Starting producer in fast mode (sleep 0.01s)")

    cmd = [
        'docker-compose', 'run', '-d',
        '-e', 'PRODUCER_SLEEP=0.01',
        '--name', 'producer_fast',
        'producer'
    ]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5)

    data_points = []
    try:
        while running:
            used_gb = get_clickhouse_disk_usage()
            rows = get_clickhouse_row_count()
            elapsed = time.time() - start_time
            data_points.append((elapsed, used_gb, rows))
            logger.info(f"Time: {elapsed:.0f}s, Disk: {used_gb:.2f} GB, Rows: {rows}")
            if used_gb >= target_gb:
                logger.info(f"Target disk usage {target_gb} GB reached")
                break
            if elapsed >= max_seconds:
                logger.info(f"Max time {max_seconds}s reached")
                break
            time.sleep(10)
    finally:

        subprocess.call(['docker-compose', 'stop', 'producer_fast'])
        subprocess.call(['docker-compose', 'rm', '-f', 'producer_fast'])
        logger.info("Producer stopped")

    import pandas as pd
    import plotly.graph_objects as go
    df = pd.DataFrame(data_points, columns=['time', 'disk_gb', 'rows'])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['time'], y=df['disk_gb'], name='Disk Usage (GB)'))
    fig.add_trace(go.Scatter(x=df['time'], y=df['rows'], name='Rows', yaxis='y2'))
    fig.update_layout(
        title='ClickHouse Disk Usage over Time',
        xaxis_title='Time (seconds)',
        yaxis_title='Disk (GB)',
        yaxis2=dict(title='Rows', overlaying='y', side='right'),
        template='plotly_white'
    )
    fig.write_html('clickhouse_fill_results.html')
    logger.info("Results saved to clickhouse_fill_results.html")

if __name__ == "__main__":
    test_disk_fill()
