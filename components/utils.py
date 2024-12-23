import streamlit as st

def group_data_by_time_unit(df):
  time_unit = st.session_state["time_unit"]
  df = df[["Date", "Order_Demand"]]

  if time_unit == "Days":
      df = df.groupby("Date").sum().reset_index()
    
  elif time_unit == "Weeks":
    df["Week"] = df["Date"].dt.isocalendar().week
    df = df[["Week", "Order_Demand"]]
    df = df.groupby("Week").sum().reset_index()

  elif time_unit == "Months":
    df["Month"] = df["Date"].dt.month
    df = df[["Month", "Order_Demand"]]
    df = df.groupby("Month").sum().reset_index()

  df.columns = ["Date", "Order_Demand"]
  return df

def calculate_sd_demand(df):
  df_grouped = group_data_by_time_unit(df)
  sd = round(df_grouped['Order_Demand'].std(), 1)
  return sd

def calculate_avg_demand(df):
  time_unit = st.session_state["time_unit"]
  total_demand = df['Order_Demand'].sum()

  if time_unit == "Days":
    avg_demand = total_demand / 365

  elif time_unit == "Weeks":
    avg_demand = total_demand / 52

  elif time_unit == "Months":
    avg_demand = total_demand / 12

  avg_demand = round(avg_demand, 1)

  return avg_demand