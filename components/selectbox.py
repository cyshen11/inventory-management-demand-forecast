import streamlit as st
import pandas as pd

def selectbox_product_category(conn):
    product_categories = pd.read_sql(
    """
        SELECT DISTINCT Name FROM ProductCategory
        ORDER BY Name
    """
    , conn)
    st.selectbox("Product Category", product_categories["Name"])