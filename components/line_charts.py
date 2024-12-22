import streamlit as st
import numpy as np

def product_daily_inventory_levels_chart(df):

    df = df[df["Product_Code"] == st.session_state['product_code']]
    df = df[df["Date"].dt.year == st.session_state["year"]]
    
    df = df.sort_values(by="Date")
    df = df[["Date", "Order_Demand"]]

    st.line_chart(df, x="Date", y=["Order_Demand"], y_label="Order Demand")
    st.session_state["demand_per_year"] = df["Order_Demand"].sum()