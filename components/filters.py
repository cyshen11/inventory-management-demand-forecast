"""Filters components"""

import streamlit as st
from streamlit_dynamic_filters import DynamicFilters


def selectbox_simulation_year(col, df):
    """
    Creates a selectbox for choosing a simulation year from the available years in the dataset.

    Args:
        col: Streamlit column object where the selectbox will be rendered
        df: DataFrame containing a 'Date' column

    Returns:
        int: Selected year from the selectbox
    """
    years = df["Date"].dt.year.unique().tolist()
    years.sort()
    return col.selectbox("Select Year", years)


def dynamic_filters_product(df):
    """
    Creates dynamic filters for Product Code and Year selection.
    Initializes or resets the models_result in session state.

    Args:
        df: DataFrame containing 'Date' and 'Product_Code' columns

    Returns:
        DynamicFilters: Object containing the filtered dataset
    """
    df["Year"] = df["Date"].dt.year
    dynamic_filters = DynamicFilters(df, filters=["Product_Code", "Year"])
    dynamic_filters.display_filters()

    # Initialize or reset models_result in session state
    if "models_result" not in st.session_state:
        st.session_state["models_result"] = {}
    else:
        st.session_state["models_result"] = {}
    return dynamic_filters


def selectbox_uncertainty_type(col):
    """
    Creates a selectbox for selecting the type of uncertainty in the simulation.
    Stores selection in session state under 'uncertainty_type'.

    Args:
        col: Streamlit column object where the selectbox will be rendered
    """
    uncertainties = [
        "Uncertain demand",
        "Uncertain lead time",
        "Uncertain demand and lead time (independent)",
        "Uncertain demand and lead time (dependent)",
    ]
    st.session_state["uncertainty_type"] = col.selectbox(
        "Select Uncertainty Type", uncertainties
    )


def selectbox_time_units(col, key):
    """
    Creates a selectbox for selecting time units (Days/Weeks/Months).
    Stores selection in session state under 'time_unit'.

    Args:
        col: Streamlit column object where the selectbox will be rendered
        key: Unique key for the selectbox component
    """
    time_units = ["Days", "Weeks", "Months"]
    st.session_state["time_unit"] = col.selectbox(
        "Select Time Units", time_units, key=key
    )


def selectbox_forecast_model(col, key):
    """
    Creates a selectbox for selecting the forecasting model.
    Uses forecast_horizon from session state to customize Moving Average option.
    Stores selection in session state under 'forecast_model'.

    Args:
        col: Streamlit column object where the selectbox will be rendered
        key: Unique key for the selectbox component
    """
    forecast_horizon = st.session_state["forecast_horizon"]
    models = [
        "Naive Drift",
        f"3-{forecast_horizon}s Moving Average",
        "ARIMA",
        "Exponential Smoothing",
        "Theta",
        "Kalman Filter",
        "Linear Regression",
        "Random Forest",
    ]
    st.session_state["forecast_model"] = col.selectbox("Select Model", models, key=key)


def selectbox_forecast_horizon(col, key):
    """
    Creates a selectbox for selecting the forecasting horizon (Day/Week/Month).
    Stores selection in session state under 'forecast_horizon'.
    Default selection is set to 'Week'.

    Args:
        col: Streamlit column object where the selectbox will be rendered
        key: Unique key for the selectbox component
    """
    window = ["Day", "Week", "Month"]
    st.session_state["forecast_horizon"] = col.selectbox(
        "Select Forecasting Horizon",
        window,
        key=key,
        index=1,  # Default selection is 'Week'
    )
