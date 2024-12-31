import pytest
import pandas as pd
import streamlit as st
import datetime as dt
from components.utils import *

@pytest.fixture
def sample_df():
    # Create sample data for testing
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    data = {
        'Date': dates,
        'Order_Demand': [100] * len(dates),
        'Lead_Time_Days': [5] * len(dates)
    }
    return pd.DataFrame(data)

@pytest.fixture
def setup_streamlit_state():
    # Setup streamlit session state
    if 'time_unit' not in st.session_state:
        st.session_state['time_unit'] = 'Days'

def test_group_data_by_time_unit_days(sample_df, setup_streamlit_state):
    st.session_state['time_unit'] = 'Days'
    result = group_data_by_time_unit(sample_df)
    assert len(result) == len(sample_df)
    assert all(result.columns == ['Date', 'Order_Demand'])

def test_group_data_by_time_unit_weeks(sample_df, setup_streamlit_state):
    st.session_state['time_unit'] = 'Weeks'
    result = group_data_by_time_unit(sample_df)
    assert len(result) == 52  # approximately 52 weeks in a year
    assert all(result.columns == ['Date', 'Order_Demand'])

def test_group_data_by_time_unit_months(sample_df, setup_streamlit_state):
    st.session_state['time_unit'] = 'Months'
    result = group_data_by_time_unit(sample_df)
    assert len(result) == 12
    assert all(result.columns == ['Date', 'Order_Demand'])

def test_calculate_sd_demand(sample_df, setup_streamlit_state):
    st.session_state['time_unit'] = 'Days'
    result = calculate_sd_demand(sample_df)
    assert isinstance(result, float)
    assert result >= 0

def test_calculate_avg_demand_days(sample_df, setup_streamlit_state):
    st.session_state['time_unit'] = 'Days'
    result = calculate_avg_demand(sample_df)
    expected = round(sample_df['Order_Demand'].sum() / 365)
    assert result == expected

def test_calculate_avg_demand_weeks(sample_df, setup_streamlit_state):
    st.session_state['time_unit'] = 'Weeks'
    result = calculate_avg_demand(sample_df)
    expected = round(sample_df['Order_Demand'].sum() / 52)
    assert result == expected

def test_calculate_avg_demand_months(sample_df, setup_streamlit_state):
    st.session_state['time_unit'] = 'Months'
    result = calculate_avg_demand(sample_df)
    expected = round(sample_df['Order_Demand'].sum() / 12)
    assert result == expected

def test_calculate_sd_lead_time(sample_df, setup_streamlit_state):
    st.session_state['time_unit'] = 'Days'
    result = calculate_sd_lead_time(sample_df)
    assert isinstance(result, float)
    assert result >= 0

def test_calculate_avg_lead_time(sample_df, setup_streamlit_state):
    st.session_state['time_unit'] = 'Days'
    result = calculate_avg_lead_time(sample_df)
    assert isinstance(result, float)
    assert result >= 0

def test_remove_outliers_iqr():
    # Create a DataFrame with known outliers
    data = {
        'Order_Demand': [1, 2, 3, 100, 2, 3, 1, 200, 2, 3]
    }
    df = pd.DataFrame(data)
    
    result = remove_outliers_iqr(df, 'Order_Demand')
    assert len(result) < len(df)  # Should have removed outliers
    assert 200 not in result['Order_Demand'].values  # Extreme value should be removed
