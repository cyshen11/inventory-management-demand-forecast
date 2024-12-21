import pandas as pd

df_order_items = pd.read_csv('data/csv/order_items.csv')
df_orders = pd.read_csv('data/csv/orders.csv')

df = pd.merge(df_order_items, df_orders, on='order_id')

df = df.groupby(['product_id', 'order_date']).agg({
    'quantity_ordered': 'sum',
    'quantity_fulfilled': 'sum',
    'is_fulfilled': 'min',
}).reset_index()

df.to_csv('data/csv/demand.csv')