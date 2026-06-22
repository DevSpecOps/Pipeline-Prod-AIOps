import os
import time
import asyncio
import pandas as pd
from fastapi import FastAPI, Request, BackgroundTasks
from pydantic import BaseModel
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import LabelEncoder
from aiochclient import ChClient
from aiohttp import ClientSession
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from aiocache import cached, Cache
from aiocache.serializers import JsonSerializer

app = FastAPI(title="MLOps Pipeline API (Async)")

# Prometheus metrics
REQUESTS = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
PREDICTION_COUNTER = Counter('predictions_total', 'Total predictions made', ['category'])
CACHE_HITS = Counter('cache_hits_total', 'Cache hits', ['endpoint'])

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    REQUESTS.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.labels(method=request.method, endpoint=request.url.path).observe(duration)
    return response

# Global state
ch_client = None
clf, reg, le_user, le_cat = None, None, None, None
model_ready = False

async def get_ch_client():
    """Get async ClickHouse client."""
    global ch_client
    if ch_client is None:
        session = ClientSession()
        ch_client = ChClient(session, url='http://clickhouse:8123')
    return ch_client

async def train_models_async():
    """Train models using current data from ClickHouse."""
    global clf, reg, le_user, le_cat, model_ready
    try:
        client = await get_ch_client()
        data = await client.execute('SELECT user_id, amount, product_category FROM orders')
        if not data:
            model_ready = False
            return
        df = pd.DataFrame(data, columns=['user_id', 'amount', 'product_category'])
        le_user = LabelEncoder()
        le_cat = LabelEncoder()
        df['user_enc'] = le_user.fit_transform(df['user_id'])
        df['cat_enc'] = le_cat.fit_transform(df['product_category'])
        X = df[['amount', 'user_enc']].values
        y_cat = df['cat_enc'].values
        y_reg = df['amount'].values
        clf = LogisticRegression(multi_class='multinomial', max_iter=1000)
        reg = LinearRegression()
        clf.fit(X, y_cat)
        reg.fit(X, y_reg)
        model_ready = True
        print(f"Models trained on {len(df)} samples")
    except Exception as e:
        print(f"Training error: {e}")
        model_ready = False

async def periodic_training(interval=60):
    """Background task to retrain models periodically."""
    while True:
        await train_models_async()
        await asyncio.sleep(interval)

@app.on_event("startup")
async def startup():
    asyncio.create_task(periodic_training(interval=60))  # every 60 seconds

@app.on_event("shutdown")
async def shutdown():
    if ch_client:
        await ch_client.session.close()

@cached(ttl=60, cache=Cache.MEMORY, serializer=JsonSerializer())
async def get_prediction(user_id: int, amount: float):
    """Cached prediction function."""
    global clf, reg, le_user, le_cat
    if not model_ready or clf is None:
        return None
    try:
        try:
            user_enc = le_user.transform([user_id])[0]
        except ValueError:
            user_enc = le_user.transform([le_user.classes_[0]])[0]
        X_pred = [[amount, user_enc]]
        cat_enc = clf.predict(X_pred)[0]
        category = le_cat.inverse_transform([cat_enc])[0]
        amount_pred = reg.predict(X_pred)[0]
        return category, float(amount_pred)
    except Exception:
        return None

class PredictionResponse(BaseModel):
    user_id: int
    predicted_category: str
    predicted_amount: float
    from_cache: bool = False

@app.get("/predict/{user_id}", response_model=PredictionResponse)
async def predict(user_id: int, amount: float = 0.0):
    """Predict category and amount for a user."""
    from_cache = False
    cached_result = await get_prediction(user_id, amount)
    if cached_result is not None:
        CACHE_HITS.labels(endpoint="/predict").inc()
        from_cache = True
        category, amount_pred = cached_result
    else:
        if not model_ready:
            return PredictionResponse(user_id=user_id, predicted_category="no_data", predicted_amount=0.0, from_cache=False)
        try:
            user_enc = le_user.transform([user_id])[0]
        except ValueError:
            user_enc = le_user.transform([le_user.classes_[0]])[0]
        X_pred = [[amount, user_enc]]
        cat_enc = clf.predict(X_pred)[0]
        category = le_cat.inverse_transform([cat_enc])[0]
        amount_pred = reg.predict(X_pred)[0]
    PREDICTION_COUNTER.labels(category=category).inc()
    return PredictionResponse(
        user_id=user_id,
        predicted_category=category,
        predicted_amount=amount_pred,
        from_cache=from_cache
    )

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        client = await get_ch_client()
        await client.execute('SELECT 1')
        db_ok = True
    except:
        db_ok = False
    return {
        "status": "ok" if db_ok and model_ready else "degraded",
        "db_connected": db_ok,
        "model_ready": model_ready,
        "cache_available": True
    }

@app.post("/retrain")
async def retrain(background_tasks: BackgroundTasks):
    """Manually trigger model retraining."""
    background_tasks.add_task(train_models_async)
    return {"status": "training_started"}