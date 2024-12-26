import streamlit as st
import pandas as pd
from streamlit_dynamic_filters import DynamicFilters

def selectbox_year(df, col):
    # Extract year and get unique values
    unique_years = df['Date'].dt.year.unique().astype(int)
    
    # Exclude invalid years
    unique_years = unique_years[unique_years > 0]

    # Sort years in ascending order
    unique_years.sort()

    st.session_state["year"] = col.selectbox("Year", unique_years)

def selectbox_simulation_year(col, df):
   years = df['Date'].dt.year.unique().tolist()
   years.sort()
   return col.selectbox("Select Year", years)

def dynamic_filters_product(df):
    df['Year'] = df['Date'].dt.year
    dynamic_filters = DynamicFilters(df, filters=['Product_Code', 'Year'])
    dynamic_filters.display_filters(location='sidebar')
    return dynamic_filters

def selectbox_week():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.session_state["week_number"] = st.selectbox("Select Week Number", range(1, 53))

def selectbox_product(df, col):
    products = df["Product_Code"].unique()
    products.sort()
    product_code = col.selectbox("Select Product", products)
    st.session_state["product_code"] = product_code

def selectbox_service_level():
    service_level_type = st.selectbox("Select Service Level Type", ["Cycle Service Level", "Fill Rate"])
    st.session_state["service_level_type"] = service_level_type

def selectbox_uncertainty_type(col):
    uncertainties = [
        "Uncertain demand",
        "Uncertain lead time",
        "Uncertain demand and lead time (independent)",
        "Uncertain demand and lead time (dependent)",
    ]
    st.session_state["uncertainty_type"] = col.selectbox("Select Uncertainty Type", uncertainties)

def selectbox_time_units(col, key):
    time_units = [
        "Days",
        "Weeks",
        "Months"
    ]
    st.session_state["time_unit"] = col.selectbox("Select Time Units", time_units, key=key)

def selectbox_forecast_model(col, key):
    models = [
        "Naive Drift",
        "Croston"
    ]
    st.session_state["forecast_model"] = col.selectbox("Select Models", models, key=key)

def selectbox_forecast_horizon(col, key):
    window = [
        "Day",
        "Week",
        "Month"
    ]
    st.session_state["forecast_horizon"] = col.selectbox("Select Forecasting Horizon", window, key=key)