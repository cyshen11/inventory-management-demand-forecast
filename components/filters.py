import streamlit as st
import pandas as pd
from streamlit_dynamic_filters import DynamicFilters

def selectbox_year(col):
    # Read data
    df = st.session_state["dataset"].data
    
    # Extract year and get unique values
    unique_years = df['Date'].dt.year.unique().astype(int)
    
    # Exclude invalid years
    unique_years = unique_years[unique_years > 0]

    # Sort years in ascending order
    unique_years.sort()

    st.session_state["year"] = col.selectbox("Year", unique_years)

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

def selectbox_product(col):
    df = pd.read_csv("data/csv/products.csv")
    product_number = col.selectbox("Select Product Number", df["product_number"])
    st.session_state["product_number"] = product_number
    st.session_state["product_id"] = df[df["product_number"] == product_number]["product_id"].values[0]

def selectbox_service_level():
    service_level_type = st.selectbox("Select Service Level Type", ["Cycle Service Level", "Fill Rate"])
    st.session_state["service_level_type"] = service_level_type
