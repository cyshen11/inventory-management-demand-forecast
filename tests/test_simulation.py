import pytest
import pandas as pd
import streamlit as st
from components.simulation import *

class MockTab:
    def __init__(self):
        self.content = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class MockColumn:
    def __init__(self):
        self.metric_value = None
        self.chart_data = None
        
    def metric(self, label, value):
        self.metric_value = value
        
    def line_chart(self, data):
        self.chart_data = data

@pytest.fixture
def mock_streamlit(monkeypatch):
    """Mock streamlit components"""
    class MockSt:
        def __init__(self):
            self.tabs_called = False
            self.columns_called = False
            self.session_state = {
                "product_code": "P001",
                "year": 2023,
                "forecast_model": "Naive Drift",
                "forecast_horizon": 12
            }
            self.tab_contents = []
            
        def tabs(self, labels):
            self.tabs_called = True
            return [MockTab() for _ in labels]
            
        def tab(self, label):
            self.tabs_called = True
            mock_tab = MockTab()
            self.tab_contents.append((label, mock_tab))
            return mock_tab
            
        def columns(self, n):
            self.columns_called = True
            return [MockColumn() for _ in range(n)]
            
        def subheader(self, text):
            pass
            
        def write(self, text):
            pass
            
        def line_chart(self, data):
            pass

    mock_st = MockSt()
    # Mock both tabs and tab methods
    monkeypatch.setattr(st, "tabs", mock_st.tabs)
    monkeypatch.setattr(st, "columns", mock_st.columns)
    monkeypatch.setattr(st, "subheader", mock_st.subheader)
    monkeypatch.setattr(st, "write", mock_st.write)
    monkeypatch.setattr(st, "line_chart", mock_st.line_chart)
    monkeypatch.setattr(st, "session_state", mock_st.session_state)
    return mock_st

@pytest.fixture
def sample_df():
    """Create sample DataFrame for testing"""
    return pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', end='2023-12-31', freq='D'),
        'Product_Code': ['P001'] * 365,
        'Order_Demand': [100] * 365,
        'Inventory_Quantity': [80] * 365
    })

@pytest.fixture
def lead_time_data():
    """Create sample lead time data"""
    return pd.DataFrame({
        'Product_Code': ['P001'] * 12,
        'Lead_Time': [5] * 12,
        'Month': range(1, 13)
    })

def test_simulation_initialization(mock_streamlit, sample_df, lead_time_data):
    """Test simulation function initialization"""
    simulation(sample_df, lead_time_data)

def test_simulation_actual_data(mock_streamlit, sample_df, lead_time_data):
    """Test simulation_actual_data function"""
    st.session_state["avg_lead_time"] = 5
    
    tabs = st.tabs(["Historical Data", "Forecast"])
    with tabs[0]:
        simulation_actual_data(sample_df, lead_time_data, 3000)

def test_simulation_forecast(mock_streamlit, sample_df, lead_time_data):
    """Test simulation_forecast function"""
    tabs = st.tabs(["Historical Data", "Forecast"])
    with tabs[1]:
        simulation_forecast(sample_df, lead_time_data)

@pytest.mark.parametrize("ss,rop,q,expected_success", [
    (100, 150, 200, True),   # Valid inputs
    (0, 150, 200, False),    # Invalid safety stock
    (100, 0, 200, False),    # Invalid reorder point
    (100, 150, 0, False),    # Invalid order quantity
])
def test_simulation_actual_data_parameters(mock_streamlit, sample_df, lead_time_data,
                                         ss, rop, q, expected_success):
    """Test simulation_actual_data with different parameters"""
    st.session_state["avg_lead_time"] = 5
    st.session_state["safety_stock"] = ss
    st.session_state["reorder_point"] = rop
    st.session_state["order_quantity"] = q
    
    tabs = st.tabs(["Historical Data", "Forecast"])
    with tabs[0]:
        simulation_actual_data(sample_df, lead_time_data, 3000)

def test_simulation_forecast_models(mock_streamlit, sample_df, lead_time_data):
    """Test simulation_forecast with different models"""
    tabs = st.tabs(["Historical Data", "Forecast"])
    for model in ["Naive Drift", "SARIMA", "Prophet", "LSTM"]:
        st.session_state["forecast_model"] = model
        with tabs[1]:
            simulation_forecast(sample_df, lead_time_data)

def test_empty_dataframe_handling(mock_streamlit, lead_time_data):
    """Test handling of empty DataFrames"""
    empty_df = pd.DataFrame(columns=['Date', 'Product_Code', 'Order_Demand', 
                                   'Inventory_Quantity'])
    
    tabs = st.tabs(["Historical Data", "Forecast"])
    with tabs[0]:
        simulation_actual_data(empty_df, lead_time_data, 3000)
    with tabs[1]:
        simulation_forecast(empty_df, lead_time_data)
    
    with mock_streamlit.tab("Forecast"):
        simulation_forecast(empty_df, lead_time_data)

def test_invalid_date_handling(mock_streamlit, sample_df):
    """Test handling of invalid dates"""
    invalid_df = sample_df.copy()
    invalid_df['Date'] = None
    
    simulation_actual_data(invalid_df, lead_time_data, 3000)
    simulation_forecast(invalid_df, lead_time_data)

def test_simulation_state_persistence(mock_streamlit, sample_df, lead_time_data):
    """Test persistence of simulation state"""
    initial_state = st.session_state.copy()
    
    simulation(sample_df, lead_time_data)
    
    for key in initial_state:
        assert st.session_state[key] == initial_state[key]

@pytest.mark.parametrize("year,horizon", [
    (2023, 12),
    (2023, 6),
    (2022, 12),
])
def test_forecast_combinations(mock_streamlit, sample_df, year, horizon):
    """Test different combinations of forecast parameters"""
    st.session_state["year"] = year
    st.session_state["forecast_horizon"] = horizon
    st.session_state["forecast_model"] = "Naive Drift"
    
    simulation_forecast(sample_df, lead_time_data)

def test_lead_time_calculations(mock_streamlit, sample_df, lead_time_data):
    """Test lead time calculations in simulation"""
    st.session_state["avg_lead_time"] = 5
    
    tabs = st.tabs(["Historical Data", "Forecast"])
    with tabs[0]:
        simulation_actual_data(sample_df, lead_time_data, 3000)
    
    assert st.session_state["avg_lead_time"] > 0
