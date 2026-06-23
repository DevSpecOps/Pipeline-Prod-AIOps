# Pipeline-Prod-AIOps

[![CI/CD](https://github.com/DevSpecOps/Pipeline-Prod-AIOps/actions/workflows/ci.yml/badge.svg)](https://github.com/DevSpecOps/Pipeline-Prod-AIOps/actions)
[![GitHub release](https://img.shields.io/github/release/DevSpecOps/Pipeline-Prod-AIOps.svg)](https://github.com/DevSpecOps/Pipeline-Prod-AIOps/releases)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Docker](https://img.shields.io/badge/docker-compose-blue.svg)

**Production‑ready MLOps pipeline** with Kafka, ClickHouse, FastAPI, Streamlit, Prometheus, Grafana, and CI/CD.

---

## 🧠 What It Does

- **Streaming data ingestion** via Apache Kafka
- **Storage** in ClickHouse (columnar DB for analytics)
- **ML Models** — Logistic Regression (classification) + Linear Regression (regression)
- **REST API** built with FastAPI (async, cached predictions)
- **Interactive Dashboard** with Streamlit
- **Monitoring** with Prometheus + Grafana
- **CI/CD** with GitHub Actions (auto-tests, build, push)
- **Containerization** with Docker Compose
- **Orchestration** with Kubernetes (minikube) — see `k8s/`

---

## 📊 Tech Stack

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
| Orchestration | Kubernetes (minikube) |

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended for development)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/DevSpecOps/Pipeline-Prod-AIOps.git
   cd Pipeline-Prod-AIOps
   ```

2. **Build and run all services**:
   ```bash
   docker-compose up -d --build
   ```

3. **Verify services**:

   | Service | URL | Credentials |
   |---------|-----|-------------|
   | API Docs | http://localhost:8000/docs | — |
   | Dashboard | http://localhost:8501 | — |
   | Prometheus | http://localhost:9090 | — |
   | Grafana | http://localhost:3001 | admin / admin |

4. **Check data flow**:
   ```
   Producer (simulates events) → Kafka → Consumer (writes to ClickHouse) → API (serves predictions)
   ```

### Option 2: Kubernetes (minikube)

1. **Start minikube**:
   ```bash
   minikube start --driver=docker --cpus=4 --memory=8192
   ```

2. **Build images inside minikube**:
   ```bash
   eval $(minikube docker-env)
   docker build -t pipeline-prod-aiops-api:latest -f Dockerfile.api .
   docker build -t pipeline-prod-aiops-consumer:latest -f Dockerfile.consumer .
   docker build -t pipeline-prod-aiops-producer:latest -f Dockerfile.producer .
   docker build -t pipeline-prod-aiops-dashboard:latest -f Dockerfile.dashboard .
   ```

3. **Apply manifests**:
   ```bash
   kubectl apply -f k8s/
   ```

4. **Port-forward services**:
   ```bash
   kubectl port-forward -n mlops svc/api 8000:8000
   kubectl port-forward -n mlops svc/dashboard 8501:8501
   kubectl port-forward -n mlops svc/grafana 3001:3000
   kubectl port-forward -n mlops svc/prometheus 9090:9090
   ```

5. **Clean up**:
   ```bash
   kubectl delete -f k8s/
   minikube stop
   ```

---

## 🛠️ Development

### Run Locally (without Docker)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run each component in a separate terminal
python producer.py      # generates events
python consumer.py      # consumes and stores
uvicorn fastapi_app:app --reload --port 8000
streamlit run streamlit_app.py
```

### Run Tests

```bash
pytest tests/
```

### Monitoring

- Prometheus scrapes metrics from the `/metrics` endpoint.
- Import a Grafana dashboard (e.g., ID `1860` for Prometheus stats).

---

## 🧪 Local Testing

After starting the services, run the health check script:

**Windows**:
```powershell
./test_all.ps1
```

**Linux/Mac**:
```bash
./test_all.sh
```

**Expected output**:
- `API Health: ok`
- `Prediction: Home` (or any category)

See [LOCAL_TEST_RESULTS.md](LOCAL_TEST_RESULTS.md) for detailed test results.

---

## 🔄 CI/CD

GitHub Actions is configured to:

- Run unit tests on every `push` and `pull_request`
- Build Docker images
- (Optional) Push to GitHub Container Registry

---

## 📁 Project Structure

```
Pipeline-Prod-AIOps/
├── .github/workflows/ci.yml   # CI/CD pipeline
├── k8s/                       # Kubernetes manifests (v2.0.0)
│   ├── namespace.yaml
│   ├── zookeeper.yaml
│   ├── kafka.yaml
│   ├── clickhouse.yaml
│   ├── api.yaml
│   ├── consumer.yaml
│   ├── producer.yaml
│   ├── dashboard.yaml
│   ├── prometheus.yaml
│   └── grafana.yaml
├── monitoring/
│   └── prometheus.yml         # Prometheus config
├── tests/                     # Unit tests (pytest)
├── docker-compose.yml         # Full stack orchestration
├── Dockerfile.*               # Per-service Dockerfiles
├── requirements.txt           # Python dependencies
├── producer.py                # Kafka event generator (realistic data)
├── consumer.py                # Kafka → ClickHouse consumer
├── fastapi_app.py             # Async REST API with caching
├── streamlit_app.py           # Dashboard
├── model_stub.py              # Classification model
├── linear_regression.py       # Regression model
├── test_all.ps1               # Health check script (Windows)
├── test_all.sh                # Health check script (Linux/Mac)
├── LOCAL_TEST_RESULTS.md      # Local test results
└── users.xml                  # ClickHouse user config
```

---

## 📦 Releases

Check the [Releases](https://github.com/DevSpecOps/Pipeline-Prod-AIOps/releases) page for versioned artifacts, changelogs, and stable builds.

- **Latest stable version**: [v2.0.0](https://github.com/DevSpecOps/Pipeline-Prod-AIOps/releases/tag/v2.0.0)

---

## 📄 License

**MIT** — free for personal and commercial use.

---

## 🤝 Contributing

PRs and issues are welcome! Feel free to improve the project.

---

## 📬 Contact

- **Author**: devspecops
- **Email**: devspecops@gmail.com
- **GitHub**: [@DevSpecOps](https://github.com/DevSpecOps)
- **Telegram**: @DevSpecOps