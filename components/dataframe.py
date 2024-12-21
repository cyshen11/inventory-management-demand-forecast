import streamlit as st
import pandas as pd

def dataframe_orders_not_filled():
    df = pd.read_csv("data/csv/orders.csv")
    
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['year'] = df['order_date'].dt.year
    df['week_number'] = df['order_date'].dt.isocalendar().week

    df = df.loc[df['year'] == st.session_state['year']]
    df = df.loc[df['week_number'] == st.session_state['week_number']]
    df = df.loc[df['is_fulfilled'] == 0]

    df = df[["order_id", "order_date"]]
    df = df.sort_values(by=["order_id"])

    df.columns = ["Order ID", "Order Date"]

    col1, col2 = st.columns([1, 1.5])

    with col1:
        event = st.dataframe(
                df, 
                on_select="rerun",
                selection_mode=["single-row"],
                hide_index=True,
            column_config={
                "order_id": st.column_config.TextColumn("Order ID")
            }
        )

    if event.selection.rows:
        order_id = df.iloc[event.selection.rows[0]]["Order ID"]
        with col2:
            dataframe_products_not_filled(order_id)

def dataframe_products_not_filled(order_id):
    order_items_df = pd.read_csv("data/csv/order_items.csv")
    order_items_df = order_items_df.loc[order_items_df['order_id'] == order_id]
    order_items_df['is_fulfilled'] = order_items_df['quantity_ordered'] == order_items_df['quantity_fulfilled']
    
    product_df = pd.read_csv("data/csv/products.csv")
    df = pd.merge(order_items_df, product_df, on='product_id', how='left')
    
    df = df[["order_id", "product_id", "product_name", "quantity_ordered", "quantity_fulfilled", "is_fulfilled"]]
    
    df = df.sort_values(by=["is_fulfilled", "product_name"])

    df.columns = ["Order ID", "Product ID", "Product Name", "Quantity Ordered", "Quantity Fulfilled", "Is Fulfilled"]

    event_product = st.dataframe(
                        df[["Product Name", "Quantity Ordered", "Quantity Fulfilled"]], 
                        on_select="rerun",
                        selection_mode=["single-row"],
                        hide_index=True,
                    )
    
    if event_product.selection.rows:
        st.session_state['product_id'] = df.iloc[event_product.selection.rows[0]]["ProductID"]
        st.session_state['product_number'] = df.iloc[event_product.selection.rows[0]]["ProductNumber"]