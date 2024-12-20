import streamlit as st
import sqlitecloud
from components.filters import *
from components.metrics import *
from components.bar_charts import *
from components.dataframe import *
from components.line_charts import *
import warnings

st.title("Inventory Management")

if 'product_id' not in st.session_state:
    st.session_state['product_id'] = None
if 'product_number' not in st.session_state:
    st.session_state['product_number'] = None

with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    selectbox_year()
    # dynamic_filters_product(conn)
    ytd_order_fill_rate()
    order_fill_weekly_chart()

    # st.subheader("Orders not filled")
    # selectbox_week()
    # dataframe_orders_not_filled(conn)

    # if st.session_state['product_number']:
    #     st.subheader(st.session_state['product_number'] + " Daily Inventory Levels")
    #     selectbox_product(conn)
    #     product_daily_inventory_levels_chart(conn)

    # product_ytd_fill_rate(conn)