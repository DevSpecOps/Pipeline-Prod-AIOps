# Local Test Results

**Date:** 2026-06-23
**Project:** Pipeline-Prod-AIOps v1.0.0
**Environment:** Docker Compose (local)

## Tested Services

| Service | Status | URL | Notes |
|---------|--------|-----|-------|
| Zookeeper | ✅ Healthy | - | |
| Kafka | ✅ Healthy | localhost:9092 | |
| ClickHouse | ✅ Healthy | localhost:8123 | Tables created |
| Producer | ✅ Running | - | Sending events |
| Consumer | ✅ Running | - | Inserting data |
| API | ✅ Healthy | http://localhost:8000 | Models trained |
| Dashboard | ✅ Healthy | http://localhost:8501 | Data visible |
| Prometheus | ✅ Healthy | http://localhost:9090 | Targets UP |
| Grafana | ✅ Healthy | http://localhost:3001 | admin/admin |

## API Tests

### Health Check
```bash
curl http://localhost:8000/health