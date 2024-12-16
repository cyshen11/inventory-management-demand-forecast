import streamlit as st
import pandas as pd

def ytd_order_fill_rate(conn):
    df = pd.read_sql(
        """
            SELECT 
                SUM(IsOrderFilled) AS TotalFilled,
                COUNT(*) AS TotalOrders,
                ROUND(CAST(SUM(IsOrderFilled) AS FLOAT) / COUNT(*), 4) AS YtdOrderFillRate 
            FROM OrderFillRate
            WHERE strftime('%Y', OrderDate) = ?
        """
        , conn, params=(st.session_state["year"],))
    value = df["YtdOrderFillRate"][0]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("YTD Order Fill Rate", f"{value:.1%}")
    with col2:
        st.metric("YTD Total Orders", df["TotalOrders"])
    with col3:
        st.metric("YTD Total Filled", df["TotalFilled"])