import streamlit as st
import pandas as pd

def product_daily_inventory_levels_chart():
    inventory_df = pd.read_csv("data/csv/inventory_daily_snapshot.csv")
    inventory_df = inventory_df[inventory_df["product_id"] == st.session_state['product_id']]
    inventory_df["Day"] = pd.to_datetime(inventory_df["snapshot_date"])
    inventory_df = inventory_df.sort_values(by="Day")
    inventory_df = inventory_df[["Day", "quantity_start_of_day"]]

    demand_df = pd.read_csv("data/csv/demand.csv")
    demand_df = demand_df[demand_df["product_id"] == st.session_state['product_id']]
    demand_df["Day"] = pd.to_datetime(demand_df["order_date"])
    demand_df = demand_df.sort_values(by="Day")
    demand_df = demand_df[["Day", "quantity_ordered", "quantity_fulfilled"]]

    df = pd.merge(demand_df, inventory_df, on="Day")

    st.line_chart(df, x="Day", y=["quantity_start_of_day", "quantity_ordered", "quantity_fulfilled"])