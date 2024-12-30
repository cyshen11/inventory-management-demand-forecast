import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
from darts import TimeSeries
from components.forecaster import Forecaster, BaselineForecaster

@pytest.fixture
def sample_df():
    # Create sample data for testing
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    data = {
        'Date': dates,
        'Order_Demand': np.random.randint(0, 100, size=len(dates))
    }
    return pd.DataFrame(data)

@pytest.fixture
def mock_session_state():
    # Mock Streamlit session state
    if 'year' not in st.session_state:
        st.session_state['year'] = 2023
    if 'forecast_model' not in st.session_state:
        st.session_state['forecast_model'] = "Naive Drift"
    if 'forecast_horizon' not in st.session_state:
        st.session_state['forecast_horizon'] = "Day"
    if 'models_result' not in st.session_state:
        st.session_state['models_result'] = {}
    if 'mae_baseline' not in st.session_state:
        st.session_state['mae_baseline'] = 0
    if 'mape_baseline' not in st.session_state:
        st.session_state['mape_baseline'] = 0

def test_forecaster_initialization(sample_df, mock_session_state):
    forecaster = Forecaster(sample_df)
    assert isinstance(forecaster.timeseries, TimeSeries)
    assert forecaster.model is not None

def test_prepare_timeseries(sample_df, mock_session_state):
    forecaster = Forecaster(sample_df)
    series = forecaster.prepare_timeseries(sample_df)
    
    assert isinstance(series, TimeSeries)
    assert len(series) == 731  # 2023 + 2024 (including leap year)
    assert series.freq == 'D'

@pytest.mark.parametrize("model_name", [
    "Naive Drift",
    "3-Days Moving Average",
    "Linear Regression",
    "ARIMA",
    "Exponential Smoothing",
    "Theta",
    "Kalman Filter",
    "Random Forest"
])
def test_prepare_model(sample_df, mock_session_state, model_name):
    st.session_state["forecast_model"] = model_name
    forecaster = Forecaster(sample_df)
    model = forecaster.prepare_model()
    assert model is not None

@pytest.mark.parametrize("horizon,expected_days", [
    ("Day", 1),
    ("Week", 7),
    ("Month", 30)
])
def test_get_forecast_horizon_days(sample_df, mock_session_state, horizon, expected_days):
    st.session_state["forecast_horizon"] = horizon
    forecaster = Forecaster(sample_df)
    assert forecaster.get_forecast_horizon_days() == expected_days

def test_generate_historical_forecasts(sample_df, mock_session_state):
    forecaster = Forecaster(sample_df)
    assert forecaster.predicted_series is not None
    assert forecaster.actual_series is not None

def test_baseline_forecaster(sample_df, mock_session_state):
    baseline = BaselineForecaster(sample_df)
    assert isinstance(baseline.timeseries, TimeSeries)
    assert baseline.model is not None
    assert 'mae_baseline' in st.session_state
    assert 'mape_baseline' in st.session_state

def test_score_calculation(sample_df, mock_session_state):
    forecaster = Forecaster(sample_df)
    # First run baseline to set baseline metrics
    baseline = BaselineForecaster(sample_df)
    
    # Test if metrics are calculated and stored
    forecaster.score()
    assert st.session_state['models_result'][st.session_state["forecast_model"]] is not None
    assert 'MAE' in st.session_state['models_result'][st.session_state["forecast_model"]]
    assert 'MAPE' in st.session_state['models_result'][st.session_state["forecast_model"]]

def test_define_param_grid(sample_df, mock_session_state):
    forecaster = Forecaster(sample_df)
    
    # Test Linear Regression param grid
    st.session_state["forecast_model"] = "Linear Regression"
    param_grid = forecaster.define_param_grid()
    assert 'lags' in param_grid
    assert 'output_chunk_length' in param_grid
    assert 'n_jobs' in param_grid
    
    # Test Random Forest param grid
    st.session_state["forecast_model"] = "Random Forest"
    param_grid = forecaster.define_param_grid()
    assert 'n_estimators' in param_grid
    assert 'max_depth' in param_grid
    assert 'lags' in param_grid
