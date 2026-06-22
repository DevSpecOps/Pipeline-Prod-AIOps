from clickhouse_driver import Client
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import pandas as pd

client = Client(host='clickhouse', user='default', password='')

data = client.execute('SELECT user_id, amount, product_category FROM orders')
if not data:
    print("No data")
    exit()

df = pd.DataFrame(data, columns=['user_id', 'amount', 'product_category'])
le_user = LabelEncoder()
le_cat = LabelEncoder()
df['user_enc'] = le_user.fit_transform(df['user_id'])
df['cat_enc'] = le_cat.fit_transform(df['product_category'])

X = df[['amount', 'user_enc']].values
y = df['cat_enc'].values
model = LogisticRegression(multi_class='multinomial', max_iter=1000)
model.fit(X, y)

agg = df.groupby('user_id').agg(avg_amount=('amount','mean')).reset_index()
agg['user_enc'] = le_user.transform(agg['user_id'])
X_pred = agg[['avg_amount','user_enc']].values
preds = model.predict(X_pred)
categories = le_cat.inverse_transform(preds)

for idx, row in agg.iterrows():
    print(f"User {row['user_id']} avg {row['avg_amount']:.2f} → predicts {categories[idx]}")