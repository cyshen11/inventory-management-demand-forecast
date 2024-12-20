import pandas as pd
import random
import datetime

df_orders_items = pd.read_csv('data/csv/order_items.csv')

df_orders_items['is_fulfilled'] = df_orders_items['quantity_fulfilled'] == df_orders_items['quantity_ordered']

df_orders = df_orders_items.groupby('order_id').agg({
    'is_fulfilled': 'max',
}).reset_index()

df_orders.index.name = 'id'

df_orders['customer_id'] = [random.randint(1, 1000) for _ in range(len(df_orders))]

df_orders['order_date'] = [datetime.date.today() - datetime.timedelta(days=random.randint(0, 365)) for _ in range(len(df_orders))]

df_orders.to_csv('data/csv/orders.csv')