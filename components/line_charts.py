import streamlit as st
import pandas as pd

def product_daily_inventory_levels_chart(conn):
    df = pd.read_sql(
        """
            WITH ProductDailyInventory AS (
                SELECT 
                    TransactionDate, 
                    ProductID,
                    COALESCE(di.CalculatedInventory, 0) AS CalculatedInventory
                FROM DailyInventoryLevels di
                WHERE 
                    ProductID = ?
                    AND strftime('%Y', TransactionDate) = ?
            )
            SELECT 
                strftime('%d-%m-%Y', TransactionDate) AS Day, 
                COALESCE(Demand, 0) AS Demand, 
                pdi.CalculatedInventory
            FROM ProductDailyInventory pdi
            LEFT JOIN ProductFillRate pfr
                ON 
                    pdi.TransactionDate = pfr.OrderDate
                    AND pdi.ProductID = pfr.ProductID
            ORDER BY Day
        """
        , conn, params=(int(st.session_state['product_id']), st.session_state['year']))
    st.line_chart(df, x="Day", y=["Demand", "CalculatedInventory"])