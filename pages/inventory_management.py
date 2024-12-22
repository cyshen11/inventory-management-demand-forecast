import streamlit as st
import sqlitecloud
from components.filters import *
from components.metrics import *
from components.bar_charts import *
from components.dataframe import *
from components.line_charts import *
from components.inputs import *
from components.dataset import *
import warnings

st.title("Inventory Management")

if 'product_id' not in st.session_state:
    st.session_state['product_id'] = None
if 'product_number' not in st.session_state:
    st.session_state['product_number'] = None
if 'dataset' not in st.session_state:
    st.session_state['dataset'] = Dataset()

    # selectbox_year()
    # # dynamic_filters_product(conn)
    # ytd_order_fill_rate()
    # order_fill_weekly_chart()

    # st.subheader("Orders not filled")
    # selectbox_week()
    # dataframe_orders_not_filled()

st.subheader("Demand Trend")
col1, col2, col3 = st.columns(3)
selectbox_product(col1)
selectbox_year(col2)


product_daily_inventory_levels_chart()

tab1, tab2, tab3 = st.tabs(["EOQ", "Reorder Point", "Safety Stock"])

with tab1:
    col1, col2, col3 = st.columns(3)
    D = col1.number_input("Demand per year (D)", value=st.session_state["demand_per_year"])
    K = col1.number_input("Order Cost per purchase order (K)", value=0)
    H = col2.number_input("Holding cost per unit per year (H)", value=0)
