import streamlit as st
import pandas as pd

def ytd_order_fill_rate(conn):
    df = pd.read_sql(
        """
            SELECT ROUND(SUM(IsOrderFilled) / COUNT(*), 4) AS YtdOrderFillRate 
            FROM OrderFillRate
            WHERE strftime('%Y', OrderDate) = ?
        """
        , conn, params=(st.session_state["year"],))
    value = df["YtdOrderFillRate"][0]
    st.metric("YTD Order Fill Rate", f"{value:.1%}")