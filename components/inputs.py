import streamlit as st
from components.utils import *

def input_cycle_service_rate(col):
    st.session_state["cycle_service_rate"] = col.number_input(
       label="Specify Targeted Cycle Service Rate", 
       min_value = 0.00,
       max_value = 1.00,
       value=0.90, 
       step=0.01)

def input_demand_sd(col, df):
    sd = calculate_sd_demand(df)
    st.session_state["demand_sd"] = col.number_input("Specify Demand Standard Deviation", value=sd, step=0.1)

def input_avg_lead_time(col, df):
    time_unit = st.session_state["time_unit"]
    value = calculate_avg_lead_time(df)
    st.session_state["avg_lead_time"] = col.number_input(f"Specify Average Lead Time ({time_unit})", value=value)

def input_sd_lead_time(col, df):
    time_unit = st.session_state["time_unit"]
    value = calculate_sd_lead_time(df)

    st.session_state["sd_lead_time"] = col.number_input(f"Specify Lead Time Std Dev ({time_unit})", value=value)

def input_avg_sales(col, df):
    time_unit = st.session_state["time_unit"]
    avg_sales = calculate_avg_demand(df)

    if time_unit == "Days":
      label = "Specify Average Demand per day"
    elif time_unit == "Weeks":
      label = "Specify Average Demand per week"
    elif time_unit == "Months":
      label = "Specify Average Demand per month"

    st.session_state["avg_sales"] = col.number_input(label, value=avg_sales)

