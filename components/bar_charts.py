import streamlit as st
import pandas as pd

def order_fill_weekly_chart():
    df_input = pd.read_csv("data/csv/orders.csv")
    
    df_input['order_date'] = pd.to_datetime(df_input['order_date'])
    df_input['year'] = df_input['order_date'].dt.year
    df_input = df_input.loc[df_input['year'] == st.session_state['year']]

    df_output = df_input.groupby(df_input['order_date'].dt.isocalendar().week).agg({'is_fulfilled': 'sum', 'order_id': 'count'}).reset_index()
    df_output.columns = ['week', 'orders_fulfilled', 'total_orders']
    df_output['order_fill_rate'] = round(df_output['orders_fulfilled'] / df_output['total_orders'] * 100, 2)
    
    st.text("Weekly Order Fill Rate")
    st.bar_chart(
        df_output, 
        x="week", 
        y="order_fill_rate", 
        x_label="Week Number", 
        y_label="Order Fill Rate (%)"
    )

def lead_time_chart(df):
    df = df.sort_values(by="Received_Date")
    df = df[["Received_Date", "Lead_Time_Days"]]

    st.bar_chart(
        df, 
        x="Received_Date", 
        y=["Lead_Time_Days"], 
        x_label="Received Date",
        y_label="Lead Time (Days)",
        height=200
    )

def cycle_service_level_chart(df):
    time_unit = st.session_state["time_unit"]

    if time_unit == "Days":
        df['Date'] = df['Date'].dt.date
    elif time_unit == "Weeks":
        df['Date'] = df['Date'].dt.isocalendar().week
    elif time_unit == "Months":
        df['Date'] = df['Date'].dt.strftime('%Y-%m')

    df = df.groupby("Date").agg({
        "Order_Demand": "sum",
        "Inventory_Quantity": "sum"
    }).reset_index()

    df["Cycle Service Rate"] = round(df["Inventory_Quantity"] / df["Order_Demand"], 2)
    df["Cycle Service Rate"] = df["Cycle Service Rate"].apply(lambda x: min(x, 1.0))

    st.bar_chart(df, x="Date", y=["Cycle Service Rate"], height=250)