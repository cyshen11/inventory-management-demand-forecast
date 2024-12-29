import streamlit as st
from streamlit_dynamic_filters import DynamicFilters

def selectbox_simulation_year(col, df):
   years = df['Date'].dt.year.unique().tolist()
   years.sort()
   return col.selectbox("Select Year", years)

def dynamic_filters_product(df):
    df['Year'] = df['Date'].dt.year
    dynamic_filters = DynamicFilters(df, filters=['Product_Code', 'Year'])
    dynamic_filters.display_filters()
    if 'models_result' not in st.session_state:
      st.session_state['models_result'] = {}
    else:
      st.session_state['models_result'] = {}
    return dynamic_filters

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
    forecast_horizon = st.session_state['forecast_horizon']
    models = [
        "Naive Drift",
        f"3-{forecast_horizon}s Moving Average",
        "ARIMA",
        "Exponential Smoothing",
        "Theta",
        "Kalman Filter",
        "Linear Regression",
        "Random Forest"
    ]
    st.session_state["forecast_model"] = col.selectbox("Select Model", models, key=key)

def selectbox_forecast_horizon(col, key):
    window = [
        "Day",
        "Week",
        "Month"
    ]
    st.session_state["forecast_horizon"] = col.selectbox(
        "Select Forecasting Horizon", 
        window, 
        key=key,
        index=1
    )