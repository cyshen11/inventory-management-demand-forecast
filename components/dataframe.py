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

    col1, col2 = st.columns([1, 2])

    with col1:
        event = st.dataframe(
                df, 
                on_select="rerun",
                selection_mode=["single-row"],
                hide_index=True,
            column_config={
                "Order ID": st.column_config.TextColumn("Order ID")
            }
        )

    if event.selection.rows:
        order_id = df.iloc[event.selection.rows[0]]["Order ID"]
        with col2:
            dataframe_products_not_filled(order_id)

def dataframe_products_not_filled(order_id):
    order_items_df = pd.read_csv("data/csv/order_items.csv")
    order_items_df = order_items_df.loc[order_items_df['order_id'] == order_id]

    order_items_df['pct_fulfilled'] = order_items_df['pct_fulfilled'] * 100
    
    product_df = pd.read_csv("data/csv/products.csv")
    df = pd.merge(order_items_df, product_df, on='product_id', how='left')
    
    df = df[["order_id", "product_number", "quantity_ordered", "quantity_fulfilled", "pct_fulfilled"]]
    
    df = df.sort_values(by=["pct_fulfilled", "product_number"])

    df.columns = ["Order ID", "Product Number", "Quantity Ordered", "Quantity Fulfilled", "% Fulfilled"]

    df_display = df[["Product Number", "Quantity Ordered", "Quantity Fulfilled", "% Fulfilled"]]

    def color_coding(row):
        return ['background-color:rgba(255, 75, 75, 0.1)'] * len(
            row) if row["% Fulfilled"] < 100 else ['background-color:white'] * len(row)

    event_product = st.dataframe(
                        df_display.style.apply(color_coding, axis=1), 
                        on_select="rerun",
                        selection_mode=["single-row"],
                        hide_index=True,
                        column_config={
                            "% Fulfilled": st.column_config.NumberColumn(
                                "% Fulfilled",
                                help="Percentage fulfilled",
                                min_value=0,
                                max_value=100,
                                format="%.0f%%",  # Shows one decimal place with % symbol
                                width="small"
                            )
                        }
                    )
    
    if event_product.selection.rows:
        st.session_state['product_id'] = df.iloc[event_product.selection.rows[0]]["ProductID"]
        st.session_state['product_number'] = df.iloc[event_product.selection.rows[0]]["ProductNumber"]