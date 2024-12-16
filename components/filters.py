import streamlit as st
import pandas as pd
from streamlit_dynamic_filters import DynamicFilters

def selectbox_year(conn):
    df = pd.read_sql(
        """
            SELECT DISTINCT strftime('%Y', OrderDate) AS Year FROM SalesOrderHeader
            ORDER BY Year
        """
        , conn)
    st.session_state["year"] = st.sidebar.selectbox("Year", df["Year"])

def dynamic_filters_product(conn):
    df = pd.read_sql(
        """
            SELECT 
                pc.Name AS Category,
                ps.Name AS Subcategory,
                p.Name AS ProductName,
                p.ProductNumber AS ProductNumber
            FROM ProductCategory pc
            LEFT JOIN ProductSubcategory ps 
                ON pc.ProductCategoryId = ps.ProductCategoryId
            LEFT JOIN Product p 
                ON ps.ProductSubcategoryID = p.ProductSubcategoryID
            ORDER BY Category, Subcategory, ProductName, ProductNumber
        """
        , conn)
    dynamic_filters = DynamicFilters(df, filters=df.columns.tolist())
    dynamic_filters.display_filters(location='sidebar')

def selectbox_week():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.session_state["week_number"] = st.selectbox("Select Week Number", range(1, 53))
    