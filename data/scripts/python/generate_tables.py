import tablefaker

tables = [
    "orders"
]

for t in tables:
    tablefaker.to_csv(f"data/scripts/yaml/{t}.yaml", f"data/csv/{t}.csv")