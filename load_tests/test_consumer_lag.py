import time
import sys
import os
import signal
sys.path.append(os.path.dirname(__file__))
from utils import setup_logger, get_consumer_lag, stop_container, start_container

logger = setup_logger('consumer_lag', 'consumer_lag.log')

running = True

def signal_handler(sig, frame):
    global running
    logger.info("Interrupt received, stopping test...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def test_consumer_lag(stop_time=60, recovery_time=120, bootstrap_servers='localhost:9092'):
    logger.info(f"Starting consumer lag test: stop for {stop_time}s, recover for {recovery_time}s")
    logger.info("Stopping consumer container...")
    if not stop_container('pipeline-prod-aiops-consumer-1'):
        logger.error("Failed to stop consumer")
        return

    logger.info(f"Waiting {stop_time}s for lag to accumulate...")
    time.sleep(stop_time)

    logger.info("Starting consumer container...")
    if not start_container('pipeline-prod-aiops-consumer-1'):
        logger.error("Failed to start consumer")
        return

    logger.info("Monitoring consumer lag...")
    start_recovery = time.time()
    lag_history = []
    while running and (time.time() - start_recovery) < recovery_time:
        lag = get_consumer_lag(bootstrap_servers=bootstrap_servers)
        lag_history.append((time.time() - start_recovery, lag))
        logger.info(f"Recovery time: {time.time() - start_recovery:.0f}s, Lag: {lag}")
        if lag == 0:
            logger.info("Lag cleared!")
            break
        time.sleep(5)

    # Save results even if interrupted
    if lag_history:
        import pandas as pd
        import plotly.graph_objects as go
        df = pd.DataFrame(lag_history, columns=['time', 'lag'])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['time'], y=df['lag'], name='Lag'))
        fig.update_layout(
            title='Consumer Lag Recovery',
            xaxis_title='Recovery Time (s)',
            yaxis_title='Lag',
            template='plotly_white'
        )
        fig.write_html('consumer_lag_results.html')
        logger.info("Results saved to consumer_lag_results.html")
    else:
        logger.warning("No data collected")

if __name__ == "__main__":
    test_consumer_lag()