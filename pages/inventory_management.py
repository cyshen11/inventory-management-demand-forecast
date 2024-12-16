import streamlit as st
import sqlitecloud
from components.filters import *

st.title("Inventory Management")

conn = sqlitecloud.connect(st.secrets["CONNECTION_STRING"])
conn.execute("USE DATABASE adventure_works")

dynamic_filters_product(conn)
