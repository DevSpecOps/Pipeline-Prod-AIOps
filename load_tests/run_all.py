import subprocess
import sys
import os

def run_script(script_name):
    print(f"\n=== Running {script_name} ===\n")
    result = subprocess.run([sys.executable, script_name], cwd=os.path.dirname(__file__))
    if result.returncode != 0:
        print(f"Error running {script_name}")
    return result.returncode

if __name__ == "__main__":
    scripts = ['test_api_load.py', 'test_clickhouse_fill.py', 'test_consumer_lag.py']
    for script in scripts:
        run_script(script)