import streamlit as st
from components.utils import *

def input_product_fill_rate(col):
    st.session_state["product_fill_rate"] = col.number_input(
       label="Specify Targeted Product Fill Rate", 
       min_value = 0.00,
       max_value = 1.00,
       value=0.90, 
       step=0.01)

def input_demand_sd(col, df):
    sd = calculate_sd(df)
    st.session_state["demand_sd"] = col.number_input("Specify Demand Standard Deviation", value=sd, step=0.1)

def input_avg_lead_time(col):
    time_unit = st.session_state["time_unit"]

    st.session_state["avg_lead_time"] = col.number_input(f"Specify Average Lead Time ({time_unit})", value=1.00)