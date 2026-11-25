import subprocess
import time
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(__file__))
from utils import setup_logger, plot_latency_rps

logger = setup_logger('api_load', 'api_load.log')

def test_api_load():
    logger.info("Starting API load test")
    results = []
    user_counts = [1, 5, 10, 20, 50, 100]
    
    locust_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'locustfile.py'))

    for users in user_counts:
        logger.info(f"Testing with {users} users")
        csv_prefix = f"locust_{users}"
        cmd = [
            'locust', '-f', locust_file,
            '--host', 'http://localhost:8000',
            '--users', str(users),
            '--spawn-rate', str(users//2 + 1),
            '--run-time', '15s',
            '--headless',
            '--only-summary',
            '--csv', csv_prefix
        ]
        try:
            subprocess.run(cmd, check=True, text=True, shell=True, stdout=subprocess.DEVNULL)
            
            stats_file = f"{csv_prefix}_stats.csv"
            if os.path.exists(stats_file):
                df = pd.read_csv(stats_file)
                # Берем строку "Aggregated"
                agg = df[df['Name'] == 'Aggregated'].iloc[0]
                rps = float(agg['Requests/s'])
                p95 = float(agg['95%'])
                results.append({'users': users, 'rps': rps, 'p95': p95})
                logger.info(f"Users: {users}, RPS: {rps}, p95: {p95}ms")
                os.remove(stats_file)
            else:
                logger.error(f"No CSV output for {users} users")
        except subprocess.CalledProcessError as e:
            logger.error(f"Locust failed for {users} users")
        time.sleep(2)
        
    if results:
        plot_latency_rps(results, 'api_load_results.html')
        logger.info("API load test completed, results saved to api_load_results.html")
    else:
        logger.error("No results collected")

if __name__ == "__main__":
    test_api_load()