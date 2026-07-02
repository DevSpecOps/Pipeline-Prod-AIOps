import os
import time
import asyncio
import logging
import pandas as pd
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from pydantic import BaseModel
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import LabelEncoder
from clickhouse_driver import Client as SyncClient
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLICKHOUSE_HOST = os.getenv('CLICKHOUSE_HOST', 'clickhouse')

# Global state
clf, reg, le_user, le_cat = None, None, None, None
model_ready = False

# Prometheus metrics
REQUESTS = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
PREDICTION_COUNTER = Counter('predictions_total', 'Total predictions made', ['category'])
CACHE_HITS = Counter('cache_hits_total', 'Cache hits', ['endpoint'])

# Simple in-memory cache
_cache = {}
CACHE_TTL = 60

def get_from_cache(key):
    if key in _cache:
        value, expiry = _cache[key]
        if time.time() < expiry:
            return value
        else:
            del _cache[key]
    return None

def set_to_cache(key, value, ttl=CACHE_TTL):
    _cache[key] = (value, time.time() + ttl)

async def train_models_async():
    global clf, reg, le_user, le_cat, model_ready
    try:
        client = SyncClient(host=CLICKHOUSE_HOST, user='default', password='')
        data = client.execute('SELECT user_id, amount, product_category FROM orders')
        if not data:
            logger.info("No data in ClickHouse, waiting for next cycle")
            return
        df = pd.DataFrame(data, columns=['user_id', 'amount', 'product_category'])
        le_user = LabelEncoder()
        le_cat = LabelEncoder()
        df['user_enc'] = le_user.fit_transform(df['user_id'])
        df['cat_enc'] = le_cat.fit_transform(df['product_category'])
        # For demonstration: using 'amount' as both feature and target (target leakage)
        # This is intentional for this demo; a proper regression would use user stats and time features.
        X = df[['amount', 'user_enc']].values
        y_cat = df['cat_enc'].values
        y_reg = df['amount'].values
        clf = LogisticRegression(multi_class='multinomial', max_iter=1000)
        reg = LinearRegression()
        clf.fit(X, y_cat)
        reg.fit(X, y_reg)
        model_ready = True
        logger.info(f"Models trained on {len(data)} samples (demo: target leakage present)")
    except Exception as e:
        logger.error(f"Training error: {e}")

async def periodic_training(interval=20):
    await asyncio.sleep(30)  # initial delay
    while True:
        try:
            await train_models_async()
        except Exception as e:
            logger.error(f"Periodic training error: {e}")
        await asyncio.sleep(interval)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API...")
    asyncio.create_task(periodic_training(interval=20))
    yield
    logger.info("Shutting down API...")

app = FastAPI(title="MLOps Pipeline API", lifespan=lifespan)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    REQUESTS.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.labels(method=request.method, endpoint=request.url.path).observe(duration)
    return response

async def get_prediction(user_id: int, amount: float):
    global clf, reg, le_user, le_cat
    if not model_ready or clf is None:
        return None, False
    cache_key = f"pred_{user_id}_{amount}"
    cached = get_from_cache(cache_key)
    if cached is not None:
        return cached, True
    try:
        try:
            user_enc = le_user.transform([user_id])[0]
        except ValueError:
            user_enc = le_user.transform([le_user.classes_[0]])[0]
        X_pred = [[amount, user_enc]]
        cat_enc = clf.predict(X_pred)[0]
        category = le_cat.inverse_transform([cat_enc])[0]
        amount_pred = reg.predict(X_pred)[0]
        result = (category, float(amount_pred))
        set_to_cache(cache_key, result)
        return result, False
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return None, False

class PredictionResponse(BaseModel):
    user_id: int
    predicted_category: str
    predicted_amount: float
    from_cache: bool = False

@app.get("/predict/{user_id}", response_model=PredictionResponse)
async def predict(user_id: int, amount: float = 0.0):
    result, from_cache = await get_prediction(user_id, amount)
    if result is None:
        if not model_ready:
            return PredictionResponse(user_id=user_id, predicted_category="no_data", predicted_amount=0.0, from_cache=False)
        else:
            return PredictionResponse(user_id=user_id, predicted_category="error", predicted_amount=0.0, from_cache=False)
    category, amount_pred = result
    if from_cache:
        CACHE_HITS.labels(endpoint="/predict").inc()
    PREDICTION_COUNTER.labels(category=category).inc()
    return PredictionResponse(
        user_id=user_id,
        predicted_category=category,
        predicted_amount=amount_pred,
        from_cache=from_cache
    )

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
async def health():
    try:
        client = SyncClient(host=CLICKHOUSE_HOST, user='default', password='')
        client.execute('SELECT 1')
        db_ok = True
    except Exception as e:
        logger.error(f"Health check DB error: {e}")
        db_ok = False
    return {
        "status": "ok" if db_ok and model_ready else "degraded",
        "db_connected": db_ok,
        "model_ready": model_ready,
        "cache_available": True
    }

@app.post("/retrain")
async def retrain(background_tasks: BackgroundTasks):
    background_tasks.add_task(train_models_async)
    return {"status": "training_started"}