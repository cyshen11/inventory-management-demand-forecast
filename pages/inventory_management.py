import streamlit as st
import sqlitecloud
from components.selectbox import *

st.title("Inventory Management")

conn = sqlitecloud.connect(st.secrets["CONNECTION_STRING"])
conn.execute("USE DATABASE adventure_works")

with st.popover("Filters"):
    selectbox_product_category(conn)
