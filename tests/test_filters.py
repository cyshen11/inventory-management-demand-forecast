"""Test cases for filters components"""

import pytest
import pandas as pd
import streamlit as st
from components.filters import *

@pytest.fixture
def sample_df():
    dates = pd.date_range(start='2020-01-01', end='2022-12-31', freq='D')
    data = {
        'Date': dates,
        'Product_Code': ['P001', 'P002'] * (len(dates) // 2),
        'Value': range(len(dates))
    }
    return pd.DataFrame(data)

@pytest.fixture
def mock_streamlit_col():
    class MockCol:
        def selectbox(self, label, options, key=None, index=None):
            # Simulate streamlit selectbox behavior
            return options[0] if options else None
    return MockCol()

def test_selectbox_simulation_year(sample_df, mock_streamlit_col):
    result = selectbox_simulation_year(mock_streamlit_col, sample_df)
    assert result == 2020
    
def test_selectbox_uncertainty_type(mock_streamlit_col):
    selectbox_uncertainty_type(mock_streamlit_col)
    assert 'uncertainty_type' in st.session_state
    assert st.session_state['uncertainty_type'] == 'Uncertain demand'

def test_selectbox_time_units(mock_streamlit_col):
    selectbox_time_units(mock_streamlit_col, key='test')
    assert 'time_unit' in st.session_state
    assert st.session_state['time_unit'] == 'Days'

def test_selectbox_forecast_model(mock_streamlit_col):
    # Set required session state
    st.session_state['forecast_horizon'] = 'Week'
    
    selectbox_forecast_model(mock_streamlit_col, key='test')
    assert 'forecast_model' in st.session_state
    assert st.session_state['forecast_model'] == 'Naive Drift'

def test_selectbox_forecast_horizon(mock_streamlit_col):
    selectbox_forecast_horizon(mock_streamlit_col, key='test')
    assert 'forecast_horizon' in st.session_state
    assert st.session_state['forecast_horizon'] == 'Day'

@pytest.fixture(autouse=True)
def clear_session_state():
    # Clear session state before each test
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    yield

def test_dynamic_filters_product(sample_df):
    # This test might be more complex due to DynamicFilters dependency
    # Basic test to ensure it initializes models_result
    dynamic_filters = dynamic_filters_product(sample_df)
    assert 'models_result' in st.session_state
    assert isinstance(st.session_state['models_result'], dict)
