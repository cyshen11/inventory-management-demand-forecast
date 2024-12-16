import streamlit as st
import pandas as pd

def order_fill_weekly_chart(conn):
    df = pd.read_sql(
        """
            SELECT 
                CAST(strftime('%W', OrderDate) AS INT) AS WeekNumber, 
                ROUND(CAST(SUM(IsOrderFilled) AS FLOAT) / COUNT(*), 2) * 100 AS OrderFillRate
            FROM OrderFillRate
            WHERE strftime('%Y', OrderDate) = ?
            GROUP BY WeekNumber
            HAVING SUM(IsOrderFilled) > 0
            ORDER BY WeekNumber
        """
        , conn, params=(st.session_state["year"],)
    )
    st.text("Weekly Order Fill Rate")
    st.bar_chart(
        df, 
        x="WeekNumber", 
        y="OrderFillRate", 
        x_label="Week Number", 
        y_label="Order Fill Rate (%)"
    )