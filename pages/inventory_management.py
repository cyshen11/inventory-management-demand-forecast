import streamlit as st
import sqlitecloud
from components.filters import *
from components.metrics import *
from components.bar_charts import *
from components.dataframe import *
import warnings

st.title("Inventory Management")

conn = sqlitecloud.connect(st.secrets["CONNECTION_STRING"])
conn.execute("USE DATABASE adventure_works")

with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    selectbox_year(conn)
    dynamic_filters_product(conn)
    ytd_order_fill_rate(conn)
    order_fill_weekly_chart(conn)

    st.subheader("Orders not filled")
    selectbox_week()
    dataframe_orders_not_filled(conn)