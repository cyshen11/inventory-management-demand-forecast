import streamlit as st

def input_product_fill_rate(col):
    st.session_state["product_fill_rate"] = col.number_input(
       label="Specify Targeted Product Fill Rate", 
       min_value = 0.00,
       max_value = 1.00,
       value=0.90, 
       step=0.01)

def input_demand_sd(col, df):
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
    sd = round(df['Order_Demand'].std(), 1)
    
    st.session_state["demand_sd"] = col.number_input("Specify Demand Standard Deviation", value=sd, step=0.1)

def input_avg_lead_time(col):
    time_unit = st.session_state["time_unit"]

    st.session_state["avg_lead_time"] = col.number_input(f"Specify Average Lead Time ({time_unit})", value=1.00)