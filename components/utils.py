import streamlit as st
import datetime as dt

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
  df = remove_outliers_iqr(df, "Order_Demand")
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

def calculate_sd_lead_time(df):
  time_unit = st.session_state["time_unit"]

  if time_unit == "Days":
    denom = 1
  elif time_unit == "Weeks":
    denom = 7
  elif time_unit == "Months":
    denom = 30

  df["Lead_Time"] = df["Lead_Time_Days"] / denom
  sd = round(df["Lead_Time"].std(), 2)

  return sd

def calculate_avg_lead_time(df):
  time_unit = st.session_state["time_unit"]
  if time_unit == "Days":
      denom = 1
  elif time_unit == "Weeks":
    denom = 7
  elif time_unit == "Months":
    denom = 30

  df["Lead_Time"] = df["Lead_Time_Days"] / denom
  value = round(df["Lead_Time"].mean(), 2)

  return value

def remove_outliers_iqr(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
