import streamlit as st
import pandas as pd
import requests
from clickhouse_driver import Client

st.set_page_config(page_title="MLOps Dashboard", layout="wide")
st.title("📊 Real‑time Order Monitoring & ML Predictions")

try:
    client = Client(host='clickhouse', user='default', password='')
    # Explicit column selection instead of SELECT * to avoid ordering issues
    df = pd.DataFrame(
        client.execute(
            'SELECT order_id, user_id, amount, product_category, timestamp FROM orders'
        ),
        columns=['order_id', 'user_id', 'amount', 'product_category', 'timestamp']
    )
except Exception as e:
    st.error(f"Cannot connect to ClickHouse: {e}")
    st.stop()

if df.empty:
    st.warning("No data yet. Run producer and consumer.")
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", len(df))
    col2.metric("Unique Users", df['user_id'].nunique())
    col3.metric("Avg Amount", f"{df['amount'].mean():.2f}")

    st.subheader("Orders by Category")
    st.bar_chart(df['product_category'].value_counts())

    st.subheader("Latest Orders")
    st.dataframe(df.tail(10))

    st.subheader("Predict for a User")
    user_id = st.number_input("User ID", min_value=1, value=13, step=1)
    amount = st.number_input("Order amount (optional)", value=0.0, step=10.0)
    if st.button("Predict"):
        try:
            resp = requests.get(f"http://api:8000/predict/{user_id}?amount={amount}")
            data = resp.json()
            st.success(f"Predicted category: **{data['predicted_category']}**")
            st.success(f"Predicted amount: **{data['predicted_amount']:.2f}**")
            if data.get('from_cache'):
                st.info("Result from cache")
        except Exception as e:
            st.error(f"API error: {e}")