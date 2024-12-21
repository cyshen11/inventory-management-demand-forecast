import streamlit as st
import pandas as pd

def product_daily_inventory_levels_chart():

    demand_df = pd.read_csv("data/csv/demand.csv")
    demand_df = demand_df[demand_df["product_id"] == st.session_state['product_id']]
    demand_df["Day"] = pd.to_datetime(demand_df["order_date"])
    demand_df = demand_df[demand_df["Day"].dt.year == st.session_state["year"]]
    
    demand_df = demand_df.sort_values(by="Day")
    demand_df = demand_df[["Day", "quantity_ordered", "quantity_fulfilled"]]

    st.line_chart(demand_df, x="Day", y=["quantity_ordered"], y_label="Demand")
    st.session_state["demand_per_year"] = demand_df["quantity_ordered"].sum()