import requests
import pytest

def test_api_health():
    try:
        response = requests.get("http://localhost:8000/docs")
        assert response.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.skip("API is not running, skipping test.")