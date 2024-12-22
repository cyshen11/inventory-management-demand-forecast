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

def calculate_sd(df):
  df_grouped = group_data_by_time_unit(df)
  sd = round(df_grouped['Order_Demand'].std(), 1)
  return sd