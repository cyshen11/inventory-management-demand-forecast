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

def input_avg_lead_time(col, df):
    time_unit = st.session_state["time_unit"]

    if time_unit == "Days":
      denom = 1
    elif time_unit == "Weeks":
      denom = 7
    elif time_unit == "Months":
      denom = 30

    df["Lead_Time"] = df["Lead_Time_Days"] / denom
    value = round(df["Lead_Time"].mean(), 2)

    st.session_state["avg_lead_time"] = col.number_input(f"Specify Average Lead Time ({time_unit})", value=value)

def input_sd_lead_time(col, df):
    time_unit = st.session_state["time_unit"]

    if time_unit == "Days":
      denom = 1
    elif time_unit == "Weeks":
      denom = 7
    elif time_unit == "Months":
      denom = 30

    df["Lead_Time"] = df["Lead_Time_Days"] / denom
    value = round(df["Lead_Time"].std(), 2)

    st.session_state["sd_lead_time"] = col.number_input(f"Specify Lead Time Std Dev ({time_unit})", value=value)

def input_avg_sales(col, df):
    time_unit = st.session_state["time_unit"]
    avg_sales = calculate_avg_demand(df)

    if time_unit == "Days":
      label = "Specify Average Sales per day"
    elif time_unit == "Weeks":
      label = "Specify Average Sales per week"
    elif time_unit == "Months":
      label = "Specify Average Sales per month"

    st.session_state["avg_sales"] = col.number_input(label, value=avg_sales, step=0.1)

