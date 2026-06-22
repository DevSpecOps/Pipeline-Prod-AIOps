from clickhouse_driver import Client
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import pandas as pd

client = Client(host='clickhouse', user='default', password='')
data = client.execute('SELECT user_id, amount FROM orders')
df = pd.DataFrame(data, columns=['user_id', 'amount'])
if df.empty:
    print("No data")
    exit()

le = LabelEncoder()
df['user_enc'] = le.fit_transform(df['user_id'])
X = df[['user_enc']].values
y = df['amount'].values
model = LinearRegression()
model.fit(X, y)

users = df.groupby('user_id').first().reset_index()
users['user_enc'] = le.transform(users['user_id'])
preds = model.predict(users[['user_enc']])

for idx, row in users.iterrows():
    print(f"User {row['user_id']} → predicted next amount: {preds[idx]:.2f}")