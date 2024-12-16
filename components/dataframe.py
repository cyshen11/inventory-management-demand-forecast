import streamlit as st
import pandas as pd

def dataframe_orders_not_filled(conn):
    df = pd.read_sql(
        """
            SELECT SalesOrderID, OrderDate FROM OrderFillRate
            WHERE 
                strftime('%Y', OrderDate) = ?
                AND CAST(strftime('%W', OrderDate) AS INT) = ?
                AND IsOrderFilled = 0
            ORDER BY SalesOrderID
        """
        , conn, params=(
            st.session_state["year"],
            st.session_state["week_number"],
        )
    )

    col1, col2 = st.columns(2)

    with col1:
        event = st.dataframe(
                df, 
                on_select="rerun",
                selection_mode=["single-row"],
                hide_index=True,
            column_config={
                "SalesOrderID": st.column_config.TextColumn("SalesOrderID")
            }
        )

    if event.selection.rows:
        sales_order_id = df.iloc[event.selection.rows[0]]["SalesOrderID"]
        order_date = df.iloc[event.selection.rows[0]]["OrderDate"]
        with col2:
            dataframe_products_not_filled(conn, sales_order_id, order_date)

def dataframe_products_not_filled(conn, sales_order_id, order_date):
    df = pd.read_sql(
        """
            WITH OrderDetails AS (
                SELECT 
                    SalesOrderID,
                    ProductID,
                    OrderQty AS Demand
                FROM "SalesOrderDetail"
                WHERE SalesOrderID = ?
            )

            SELECT 
                p.ProductID,
                p.ProductNumber,
                od.Demand AS Demand,
                COALESCE(di.CalculatedInventory, 0) AS CalculatedInventory
            FROM OrderDetails od
            LEFT JOIN DailyInventoryLevels di
                ON od.ProductID = di.ProductID
                AND di.TransactionDate = ?
            LEFT JOIN Product p
                ON od.ProductID = p.ProductID
            ORDER BY CalculatedInventory, p.ProductNumber
            -- WHERE od.Demand > COALESCE(di.CalculatedInventory, 0)
        """
        , conn, params=(int(sales_order_id), order_date)
    )

    event_product = st.dataframe(
                        df[["ProductNumber", "Demand", "CalculatedInventory"]], 
                        on_select="rerun",
                        selection_mode=["single-row"],
                        hide_index=True,
                    )
    
    if event_product.selection.rows:
        st.session_state['product_id'] = df.iloc[event_product.selection.rows[0]]["ProductID"]
        st.session_state['product_number'] = df.iloc[event_product.selection.rows[0]]["ProductNumber"]