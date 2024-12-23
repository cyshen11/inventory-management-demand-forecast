import streamlit as st
import numpy as np
import pandas as pd

def product_daily_inventory_levels_chart(df):
    
    df = df.sort_values(by="Date")
    df = df[["Date", "Order_Demand"]]
    df = df.groupby("Date").sum().reset_index()
    df.columns = ["Date", "Order_Demand"]

    st.line_chart(df, x="Date", y=["Order_Demand"], y_label="Order Demand", height=250)
    
    st.session_state["demand_per_year"] = df["Order_Demand"].sum()
    st.session_state["avg_demand"] = round(df["Order_Demand"].sum() / 365)
    st.session_state["max_demand"] = df["Order_Demand"].max()

def inventory_chart(year):
    year = str(year)
    
    # Create date range for one year
    dates = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31', freq='D')
    
    eoq = st.session_state["EOQ"]
    rop = st.session_state["ROP"]
    safety_stock = st.session_state["safety_stock"]
    avg_daily_demand = st.session_state["avg_daily_sales"]
    lead_time_days = st.session_state["delivery_lead_time"]

    # Initialize inventory levels
    initial_inventory = eoq
    inventory_levels = []
    current_inventory = initial_inventory
    
    # Simulate inventory changes over the year
    for _ in dates:
        # If inventory drops to ROP, order more (add EOQ after lead time)
        if current_inventory <= rop:
            # Schedule delivery after lead time
            if len(inventory_levels) + lead_time_days < len(dates):
                for _ in range(lead_time_days - 1):
                    inventory_levels.append(current_inventory - avg_daily_demand)
                    current_inventory -= avg_daily_demand
                current_inventory = current_inventory + eoq
        
        # Subtract daily demand
        current_inventory = max(current_inventory - avg_daily_demand, safety_stock)
        inventory_levels.append(current_inventory)
    
    # Trim to exactly one year
    inventory_levels = inventory_levels[:365]
    
    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates[:365],
        'Inventory Level': inventory_levels,
        'EOQ': [eoq] * 365,
        'ROP': [rop] * 365,
        'Safety Stock': [safety_stock] * 365
    })
    
    # Create Streamlit line chart
    st.line_chart(
        df.set_index('Date')[['Inventory Level', 'EOQ', 'ROP', 'Safety Stock']]
    )