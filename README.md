# Pipeline-Prod-AIOps

**Production‑ready MLOps pipeline** with Kafka, ClickHouse, FastAPI, Streamlit, Prometheus, Grafana, and CI/CD.

## Tech Stack
- **Streaming**: Apache Kafka
- **Storage**: ClickHouse (columnar DB)
- **Backend API**: FastAPI (Python)
- **Dashboard**: Streamlit
- **ML Models**: Logistic Regression (classification), Linear Regression (regression)
- **Monitoring**: Prometheus + Grafana
- **CI/CD**: GitHub Actions
- **Containerization**: Docker Compose

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/DevSpecOps/Pipeline-Prod-AIOps.git
   cd Pipeline-Prod-AIOps
Build and run all services:

bash
docker-compose up -d --build
Verify services:

API docs: http://localhost:8000/docs

Dashboard: http://localhost:8501

Prometheus: http://localhost:9090

Grafana: http://localhost:3001 (login: admin / admin)

Check data flow: Producer sends events → Consumer inserts into ClickHouse → API serves predictions.

Development
Run locally without Docker
bash
pip install -r requirements.txt
python producer.py   # in one terminal
python consumer.py   # in another
uvicorn fastapi_app:app --reload --port 8000
streamlit run streamlit_app.py
Run tests
bash
pytest tests/
Monitoring
Prometheus scrapes metrics from /metrics endpoint.

Import a Grafana dashboard (e.g., ID 1860 for Prometheus stats).

CI/CD
GitHub Actions runs tests and builds Docker images on every push to main.

License
MIT