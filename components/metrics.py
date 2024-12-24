import streamlit as st
import pandas as pd

def ytd_order_fill_rate():
    # Read the OrderFillRate data
    df = pd.read_csv('data/csv/orders.csv')
    
    # Convert OrderDate to datetime if it's not already
    df['OrderDate'] = pd.to_datetime(df['order_date'])
    
    # Convert to year
    df['Year'] = df['OrderDate'].dt.year

    # Filter for the selected year
    df_ytd = df[df['Year'] == st.session_state["year"]]
    
    # Calculate YTD fill rate
    total_orders = len(df_ytd)
    total_filled = len(df_ytd.loc[df_ytd['is_fulfilled'] == True])
    ytd_fill_rate = round(total_filled / total_orders, 2)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("YTD Order Fill Rate", f"{ytd_fill_rate:.1%}")
    with col2:
        st.metric("YTD Total Orders", total_orders)
    with col3:
        st.metric("YTD Total Filled", total_filled)

def ytd_product_fill_rate(df, col):
    df = df.loc[df["Order_Demand"] > 0]
    product_fill_rate = round(df["Inventory_Quantity"].sum() / df["Order_Demand"].sum(), 2)
    product_fill_rate = min(product_fill_rate, 1)
    col.metric("YTD Product Fill Rate:", f"{product_fill_rate:.1f}")