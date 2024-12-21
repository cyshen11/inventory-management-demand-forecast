import streamlit as st
import pandas as pd
from streamlit_dynamic_filters import DynamicFilters

def selectbox_year():
    # Read the orders CSV file
    df = pd.read_csv('data/csv/orders.csv')
    
    # Convert order_date to datetime
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    # Extract year and get unique values
    unique_years = df['order_date'].dt.year.unique()
    
    # Sort years in ascending order
    unique_years.sort()

    st.session_state["year"] = st.sidebar.selectbox("Year", unique_years)

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

def selectbox_product():
    df = pd.read_csv("data/csv/products.csv")
    col1, col2, col3, col4 = st.columns(4)
    st.session_state["product_number"] = col1.selectbox("Select Product Number", df["product_number"])
    