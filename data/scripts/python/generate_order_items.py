import datetime
import pandas as pd
import random

random.seed(43)

row_count = 30000

df = pd.DataFrame(
    {
        "order_item_id": range(row_count),
        "order_id": [random.randint(1, 10000) for _ in range(row_count)],
        "product_id": [random.randint(1, 100) for _ in range(row_count)],
        "quantity_ordered": [random.randint(1, 50) for _ in range(row_count)],
    }
)
df["quantity_fulfilled"] = df['quantity_ordered'].apply(lambda x: x if random.random() < 0.9 else random.randint(0, x))
df = df[["order_item_id", "order_id", "product_id", "quantity_ordered", "quantity_fulfilled"]]
df.to_csv("data/csv/order_items.csv", index=False)
