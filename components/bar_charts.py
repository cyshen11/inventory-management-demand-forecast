import streamlit as st
import pandas as pd

def order_fill_weekly_chart():
    df_input = pd.read_csv("data/csv/orders.csv")
    df_input['order_date'] = pd.to_datetime(df_input['order_date'])
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

def product_ytd_fill_rate(conn):
    df = pd.read_sql(
        """
            SELECT 
                strftime('%Y', OrderDate) AS Year, 
                ProductID,
                ROUND(CAST(SUM(Demand) AS FLOAT) / SUM(CalculatedInventory), 2) * 100 AS ProductFillRate
            FROM ProductFillRate
            WHERE 
                strftime('%Y', OrderDate) = ?
            GROUP BY Year, ProductID
            HAVING ProductFillRate <= 100
            ORDER BY ProductFillRate DESC
            LIMIT 10
        """
        , conn, params=(st.session_state['year'],))
    st.text("Product YTD Fill Rate")
    st.bar_chart(
        df, 
        x="ProductID", 
        y="ProductFillRate", 
        horizontal=True
    )