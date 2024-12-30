def ytd_product_fill_rate(df, col):
    if df.empty:
        col.metric("Fill Rate", "0.0")
        return
        
    # Filter out zero demand rows
    df = df[df['Order_Demand'] > 0]
    
    if df.empty:  # Check again after filtering
        col.metric("Fill Rate", "0.0")
        return
        
    total_demand = df['Order_Demand'].sum()
    total_filled = df['Inventory_Quantity'].sum()
    
    fill_rate = min(total_filled / total_demand, 1.0) if total_demand > 0 else 0.0
    col.metric("Fill Rate", f"{fill_rate:.1f}")
