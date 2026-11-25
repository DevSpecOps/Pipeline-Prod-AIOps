# Pipeline-Prod-AIOps

[![CI/CD](https://github.com/DevSpecOps/Pipeline-Prod-AIOps/actions/workflows/ci.yml/badge.svg)](https://github.com/DevSpecOps/Pipeline-Prod-AIOps/actions)
[![GitHub release](https://img.shields.io/github/release/DevSpecOps/Pipeline-Prod-AIOps.svg)](https://github.com/DevSpecOps/Pipeline-Prod-AIOps/releases)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Docker](https://img.shields.io/badge/docker-compose-blue.svg)

**Production-ready MLOps pipeline** with Kafka, ClickHouse, FastAPI, Streamlit, Prometheus, Grafana, and CI/CD.

---

## What It Does

- **Streaming data ingestion** via Apache Kafka
- **Storage** in ClickHouse (columnar DB for analytics)
- **ML Models** — Logistic Regression (classification) + Linear Regression (regression)
- **Asynchronous API** — FastAPI with in-memory caching and background model retraining
- **Interactive Dashboard** with Streamlit for real-time monitoring and manual inference
- **Monitoring** with Prometheus + Grafana
- **CI/CD** with GitHub Actions (auto-tests, build, push)
- **Containerization** with Docker Compose
- **Business analytics** — realistic sports retail data, A/B testing, loyalty cards, discounts

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Streaming | Apache Kafka |
| Storage | ClickHouse |
| Backend API | FastAPI (Python) |
| Frontend Dashboard | Streamlit |
| ML Models | scikit-learn (LogisticRegression, LinearRegression) |
| Monitoring | Prometheus + Grafana |
| CI/CD | GitHub Actions |
| Containerization | Docker Compose |

---

## Quick Start

### Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/DevSpecOps/Pipeline-Prod-AIOps.git
cd Pipeline-Prod-AIOps
```

2. Build and run all services:
```bash
docker-compose up -d --build
```

3. Verify services:

   | Service | URL | Credentials |
   |---------|-----|-------------|
   | API Docs | http://localhost:8000/docs | — |
   | Dashboard | http://localhost:8501 | — |
   | Prometheus | http://localhost:9090 | — |
   | Grafana | http://localhost:3001 | admin / admin |

4. Check data flow:
   Producer (simulates events) -> Kafka -> Consumer (writes to ClickHouse) -> API (serves predictions)

---

## Development & Testing

### Prerequisites
- Docker and Docker Compose installed.
- Python 3.10+ (for running local tests and load tests).

### Run Locally (without Docker)

1. Install production dependencies:
```bash
pip install -r requirements.txt
```

2. Install development dependencies (tests, load tests):
```bash
pip install -r requirements-dev.txt
```

3. Run each component in a separate terminal:
```bash
python producer.py
python consumer.py
uvicorn fastapi_app:app --reload --port 8000
streamlit run streamlit_app.py
```

### Run Tests

```bash
pytest tests/
```

### Run Load Tests

```bash
python load_tests/test_api_load.py
python load_tests/test_clickhouse_fill.py
python load_tests/test_consumer_lag.py
```

### Monitoring

- Prometheus scrapes metrics from the `/metrics` endpoint (HTTP request duration, count, predictions).
- Grafana is pre-provisioned and can be accessed via port 3001.

---

## Dependencies

| File | Purpose |
|------|---------|
| `requirements.txt` | Production runtime dependencies |
| `requirements-dev.txt` | Development, testing, and load testing dependencies |

---

## Project Structure

```text
Pipeline-Prod-AIOps/
├── .github/                   # CI/CD workflows
├── grafana/                   # Grafana dashboards and provisioning
├── k8s/                       # Kubernetes manifests (planned/optional)
├── load_tests/                # Load testing suite (Locust scripts)
├── monitoring/                # Prometheus configuration (prometheus.yml)
├── tests/                     # Pytest unit tests
├── docker-compose.yml         # Main orchestration file
├── Dockerfile.api             # API Dockerfile
├── Dockerfile.consumer        # Consumer Dockerfile
├── Dockerfile.dashboard       # Dashboard Dockerfile
├── Dockerfile.producer        # Producer Dockerfile
├── fastapi_app.py             # FastAPI backend logic
├── producer.py                # Kafka event generator
├── consumer.py                # Kafka -> ClickHouse consumer
├── streamlit_app.py           # Streamlit dashboard
├── model_stub.py              # Classification model script
├── linear_regression.py       # Regression model script
├── users.xml                  # ClickHouse user configuration
├── test_all.ps1 / test_all.sh # Scripts to run all tests
├── requirements.txt           # Production dependencies
└── requirements-dev.txt       # Development dependencies
```

---

## CI/CD

GitHub Actions is configured to:
- Run unit tests on every push and pull request
- Build Docker images

---

## Roadmap

### Version 4.0.0 (Planned)
- **Kubernetes deployment** (minikube) — full orchestration
- **Dead Letter Queue** (DLQ) for Kafka
- **MLflow** for experiment tracking and model registry
- **Data drift monitoring** with Evidently AI

---

## Releases

Check the [Releases](https://github.com/DevSpecOps/Pipeline-Prod-AIOps/releases) page for versioned artifacts, changelogs, and stable builds.

- **Latest stable version**: [v3.1.0](https://github.com/DevSpecOps/Pipeline-Prod-AIOps/releases/tag/v3.1.0)

---

## License

**MIT** — free for personal and commercial use.

---

## Contact

- **Author**: devspecops
- **Email**: devspecops@gmail.com
- **GitHub**: [@DevSpecOps](https://github.com/DevSpecOps)
- **Telegram**: @DevSpecOps