Write-Host "=== Pipeline-Prod-AIOps Health Check ===" -ForegroundColor Cyan
Write-Host ""

try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health"
    Write-Host "API Health: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "API Health: FAILED" -ForegroundColor Red
}

try {
    $pred = Invoke-RestMethod -Uri "http://localhost:8000/predict/13?amount=200"
    Write-Host "Prediction: $($pred.predicted_category)" -ForegroundColor Green
} catch {
    Write-Host "Prediction: FAILED" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Dashboard URLs ===" -ForegroundColor Yellow
Write-Host "API:      http://localhost:8000/docs"
Write-Host "Streamlit: http://localhost:8501"
Write-Host "Prometheus: http://localhost:9090"
Write-Host "Grafana:   http://localhost:3001 (admin/admin)"