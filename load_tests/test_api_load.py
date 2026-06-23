import subprocess
import time
import json
import requests
import sys
import os
sys.path.append(os.path.dirname(__file__))
from utils import setup_logger, plot_latency_rps

logger = setup_logger('api_load', 'api_load.log')

def run_locust(users, spawn_rate=10, host='http://localhost:8000', run_time='60s'):
    cmd = [
        'locust', '-f', 'locustfile.py',
        '--host', host,
        '--users', str(users),
        '--spawn-rate', str(spawn_rate),
        '--run-time', run_time,
        '--headless',
        '--only-summary',
        '--json'
    ]
    # Implementation depends on parsing JSON output from locust
    return {}

def test_api_load():
    logger.info("Starting API load test")
    results = []
    user_counts = [1, 5, 10, 20, 50, 100, 200]
    for users in user_counts:
        logger.info(f"Testing with {users} users")
        cmd = [
            'locust', '-f', 'locustfile.py',
            '--host', 'http://localhost:8000',
            '--users', str(users),
            '--spawn-rate', str(users//2 + 1),
            '--run-time', '30s',
            '--headless',
            '--only-summary',
            '--json'
        ]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
            lines = output.splitlines()
            json_line = None
            for line in lines:
                if line.startswith('{'):
                    json_line = line
                    break
            if json_line:
                data = json.loads(json_line)
                rps = data.get('total_rps', 0)
                p95 = data.get('p95_response_time', 0)
                results.append({'users': users, 'rps': rps, 'p95': p95})
                logger.info(f"Users: {users}, RPS: {rps}, p95: {p95}ms")
            else:
                logger.error(f"No JSON output for {users} users")
        except subprocess.CalledProcessError as e:
            logger.error(f"Locust failed for {users} users: {e.output}")
        time.sleep(2)
    if results:
        plot_latency_rps(results, 'api_load_results.html')
        logger.info("API load test completed, results saved to api_load_results.html")
    else:
        logger.error("No results collected")

if __name__ == "__main__":
    test_api_load()