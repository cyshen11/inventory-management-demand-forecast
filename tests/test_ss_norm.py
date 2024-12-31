import pytest
import numpy as np
from components.ss_norm import *
from components.utils import *
import streamlit as st
import pandas as pd
from scipy import stats

@pytest.fixture
def mock_session_state():
    session_state = {
        "cycle_service_rate": 0.95,
        "uncertainty_type": "Uncertain demand",
        "avg_sales": 100,
        "avg_lead_time": 2,
        "demand_sd": 20,
        "sd_lead_time": 0.5,
        "fill_rate": 0.98,
        "holding_cost": 10,
        "stockout_cost": 50,
        "time_unit": "Days"
    }
    return session_state

@pytest.fixture
def mock_data():
    # Create sample dates
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    
    # Create sample filtered data and lead time data
    filtered_data = pd.DataFrame({
        'Date': dates,
        'Order_Demand': np.random.normal(100, 20, 100)
    })
    
    lead_time_data = pd.DataFrame({
        'Date': dates,
        'Lead_Time_Days': np.random.normal(2, 0.5, 100)
    })
    
    return filtered_data, lead_time_data

class MockColumn:
    def number_input(self, label, value=None, min_value=None, max_value=None, key=None, step=None, format=None, help=None):
        return value

    def write(self, *args, **kwargs):
        pass

def test_uncertain_demand(monkeypatch, mock_session_state, mock_data):
    monkeypatch.setattr(st, 'session_state', mock_session_state)
    filtered_data, lead_time_data = mock_data
    
    mock_cols = [MockColumn(), MockColumn(), MockColumn()]
    monkeypatch.setattr(st, 'columns', lambda x: mock_cols)
    monkeypatch.setattr(st, 'info', lambda x: None)
    monkeypatch.setattr(st, 'write', lambda *args, **kwargs: None)
    
    uncertain_demand(filtered_data, lead_time_data)
    
    Z = stats.norm.ppf(0.95)
    expected_ss = round(Z * 20 * (2 ** 0.5))
    expected_avg_sales = calculate_avg_demand(filtered_data)
    expected_avg_lead_time = calculate_avg_lead_time(lead_time_data)
    expected_demand_sd = calculate_sd_demand(filtered_data)
    
    assert st.session_state['avg_sales'] == expected_avg_sales
    assert st.session_state['avg_lead_time'] == expected_avg_lead_time
    assert st.session_state['demand_sd'] == expected_demand_sd

def test_uncertain_lead_time(monkeypatch, mock_session_state, mock_data):
    monkeypatch.setattr(st, 'session_state', mock_session_state)
    filtered_data, lead_time_data = mock_data
    
    mock_cols = [MockColumn(), MockColumn(), MockColumn()]
    monkeypatch.setattr(st, 'columns', lambda x: mock_cols)
    monkeypatch.setattr(st, 'info', lambda x: None)
    monkeypatch.setattr(st, 'write', lambda *args, **kwargs: None)
    
    uncertain_lead_time(filtered_data, lead_time_data)
    
    Z = stats.norm.ppf(0.95)
    expected_avg_sales = calculate_avg_demand(filtered_data)
    expected_sd_lead_time = calculate_sd_lead_time(lead_time_data)
    
    assert st.session_state['avg_sales'] == expected_avg_sales
    assert st.session_state['sd_lead_time'] == expected_sd_lead_time

def test_uncertain_demand_lead_time_ind(monkeypatch, mock_session_state, mock_data):
    monkeypatch.setattr(st, 'session_state', mock_session_state)
    filtered_data, lead_time_data = mock_data
    
    mock_cols = [MockColumn(), MockColumn(), MockColumn()]
    monkeypatch.setattr(st, 'columns', lambda x: mock_cols)
    monkeypatch.setattr(st, 'info', lambda x: None)
    monkeypatch.setattr(st, 'write', lambda *args, **kwargs: None)
    
    uncertain_demand_lead_time_ind(filtered_data, lead_time_data)
    
    expected_avg_sales = calculate_avg_demand(filtered_data)
    exepcted_sd_demand = calculate_sd_demand(filtered_data)
    expected_sd_lead_time = calculate_sd_lead_time(lead_time_data)

    assert st.session_state['avg_sales'] == expected_avg_sales
    assert st.session_state['demand_sd'] == exepcted_sd_demand
    assert st.session_state['sd_lead_time'] == expected_sd_lead_time

def test_ss_fill_rate(monkeypatch, mock_session_state, mock_data):
    monkeypatch.setattr(st, 'session_state', mock_session_state)
    filtered_data, lead_time_data = mock_data
    
    mock_cols = [MockColumn(), MockColumn(), MockColumn()]
    monkeypatch.setattr(st, 'columns', lambda x: mock_cols)
    monkeypatch.setattr(st, 'info', lambda x: None)
    monkeypatch.setattr(st, 'write', lambda *args, **kwargs: None)
    
    ss_fill_rate(filtered_data, lead_time_data)
    
    beta = 0.98
    mu = 100
    sigma = 20
    L = 2
    
    z_std_normal_loss = mu * (1 - beta) / sigma
    z = 4.85 - (z_std_normal_loss ** 1.3) * 0.3924 - (z_std_normal_loss ** 0.135) * 5.359
    
    assert st.session_state['fill_rate'] == 0.98
    assert st.session_state['avg_sales'] == 100
    assert st.session_state['demand_sd'] == 20

def test_ss_holding_stockout(monkeypatch, mock_session_state, mock_data):
    monkeypatch.setattr(st, 'session_state', mock_session_state)
    filtered_data, lead_time_data = mock_data
    
    mock_cols = [MockColumn(), MockColumn(), MockColumn()]
    monkeypatch.setattr(st, 'columns', lambda x: mock_cols)
    monkeypatch.setattr(st, 'info', lambda x: None)
    monkeypatch.setattr(st, 'write', lambda *args, **kwargs: None)
    
    ss_holding_stockout(filtered_data, lead_time_data)
    
    h = 10
    p = 50
    mu = 100
    sigma = 20
    L = 2
    
    expected_ss = round((mu + sigma * stats.norm.cdf(p / (p + h))) * (L ** 0.5))
    
    assert st.session_state['holding_cost'] == 10
    assert st.session_state['stockout_cost'] == 50
    assert st.session_state['avg_sales'] == 100
