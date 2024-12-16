import streamlit as st
import pandas as pd

def product_daily_inventory_levels_chart(conn):
    df = pd.read_sql(
        """
            SELECT 
                strftime('%d-%m-%Y', TransactionDate) AS Day, 
                CalculatedInventory
            FROM DailyInventoryLevels
            WHERE 
                ProductID = ?
                AND strftime('%Y', TransactionDate) = ?
            ORDER BY Day
        """
        , conn, params=(int(st.session_state['product_id']), st.session_state['year']))
    st.line_chart(df, x="Day", y="CalculatedInventory")