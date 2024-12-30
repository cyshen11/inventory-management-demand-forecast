"""Inputs components"""

import streamlit as st
from components.utils import *

# Function to create input field for cycle service rate (probability of not stocking out)
def input_cycle_service_rate(col):
    st.session_state["cycle_service_rate"] = col.number_input(
       label="Specify Targeted Cycle Service Rate", 
       min_value = 0.00,
       max_value = 1.00,
       value=0.90, 
       step=0.01)

# Function to create input field for fill rate (fraction of demand met from stock)
def input_fill_rate(col):
    st.session_state["fill_rate"] = col.number_input(
       label="Specify Targeted Fill Rate", 
       min_value = 0.00,
       max_value = 0.99,
       value=0.90, 
       step=0.01)

# Function to create input field for demand standard deviation
# Calculates and sets default value based on historical data
def input_demand_sd(col, df, key):
    sd = calculate_sd_demand(df)
    st.session_state["demand_sd"] = col.number_input("Specify Demand Standard Deviation", value=sd, step=0.1, key=key)

# Function to create input field for average lead time
# Uses time unit from session state and calculates default from historical data
def input_avg_lead_time(col, df, key):
    time_unit = st.session_state["time_unit"]
    value = calculate_avg_lead_time(df)
    st.session_state["avg_lead_time"] = col.number_input(f"Specify Average Lead Time ({time_unit})", value=value, key=key)

# Function to create input field for lead time standard deviation
# Calculates default value from historical data
def input_sd_lead_time(col, df):
    time_unit = st.session_state["time_unit"]
    value = calculate_sd_lead_time(df)

    st.session_state["sd_lead_time"] = col.number_input(f"Specify Lead Time Std Dev ({time_unit})", value=value)

# Function to create input field for average sales/demand
# Adapts label based on time unit and calculates default from historical data
def input_avg_sales(col, df, key):
    time_unit = st.session_state["time_unit"]
    avg_sales = calculate_avg_demand(df)

    if time_unit == "Days":
      label = "Specify Average Demand per day"
    elif time_unit == "Weeks":
      label = "Specify Average Demand per week"
    elif time_unit == "Months":
      label = "Specify Average Demand per month"

    st.session_state["avg_sales"] = col.number_input(label, value=avg_sales, key=key)

# Function to create input field for holding cost per unit per year
def input_holding_cost(col, key):
   st.session_state["holding_cost"] = col.number_input("Specify Holding cost / unit / year (H)", value=0.20, key=key)

# Function to create input field for stockout cost per unit
def input_stockout_cost(col, key):
   st.session_state["stockout_cost"] = col.number_input("Specify Stockout cost per unit (p)", value=0.20, key=key)

# Function to create input field for safety stock level
def input_ss(col, key=None):
   return col.number_input("Specify Safety Stock (SS)", value=0, key=key)

# Function to create input field for reorder point
def input_rop(col, key=None):
   return col.number_input("Specify Reorder Point (ROP)", value=0, key=key)

# Function to create input field for order quantity
def input_oq(col, key=None):
   return col.number_input("Specify Order Quantity (Q)", value=0, key=key)