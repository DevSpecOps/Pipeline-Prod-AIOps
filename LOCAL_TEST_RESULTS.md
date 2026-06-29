# Local Test Results

**Date:** 2026-06-29
**Project:** Pipeline-Prod-AIOps v3.0.1
**Environment:** Docker Compose (local)

## Tested Services

| Service | Status | URL | Notes |
|---------|--------|-----|-------|
| Zookeeper | ✅ Healthy | - | |
| Kafka | ✅ Healthy | localhost:9092 | advertised listener fixed |
| ClickHouse | ✅ Healthy | localhost:8123 | Tables created |
| Producer | ✅ Running | - | Sending events |
| Consumer | ✅ Running | - | Inserting data |
| API | ✅ Healthy | http://localhost:8000 | Models trained |
| Dashboard | ✅ Healthy | http://localhost:8501 | Data visible, explicit query |
| Prometheus | ✅ Healthy | http://localhost:9090 | Targets UP |
| Grafana | ✅ Healthy | http://localhost:3001 | admin/admin |

## API Tests

### Health Check
```bash
curl http://localhost:8000/health
```
**Result:** `{"status":"ok","db_connected":true,"model_ready":true,"cache_available":true}`

### Prediction
```bash
curl "http://localhost:8000/predict/13?amount=200"
```
**Result:** `{"user_id":13,"predicted_category":"Electronics","predicted_amount":200.0,"from_cache":true}`

### Retrain
```bash
curl -X POST http://localhost:8000/retrain
```
**Result:** `{"status":"training_started"}`

## Metrics Collected

- `http_requests_total`: 200+
- `predictions_total`: 50+
- `cache_hits_total`: 20+
- `http_request_duration_seconds`: p95 ~ 50ms

## Conclusion

All services are operational. The pipeline handles streaming data, model training, and inference as expected. Monitoring stack (Prometheus/Grafana) is configured and collecting metrics.

**Ready for production deployment (v3.0.1).**