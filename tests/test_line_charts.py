import pytest
import pandas as pd
import numpy as np
import streamlit as st
from components.line_charts import *

@pytest.fixture
def sample_demand_df():
    """Fixture to create sample demand DataFrame for testing."""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    data = {
        'Date': dates,
        'Order_Demand': np.random.randint(10, 100, size=len(dates))
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_inventory_df():
    """Fixture to create sample inventory DataFrame for testing."""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    data = {
        'Date': dates,
        'Order_Demand': np.random.randint(10, 100, size=len(dates)),
        'Inventory_Quantity': np.random.randint(100, 500, size=len(dates))
    }
    return pd.DataFrame(data)

@pytest.fixture
def mock_session_state():
    """Fixture to mock Streamlit session state."""
    if 'demand_per_year' not in st.session_state:
        st.session_state['demand_per_year'] = 0
    if 'avg_demand' not in st.session_state:
        st.session_state['avg_demand'] = 0
    if 'max_demand' not in st.session_state:
        st.session_state['max_demand'] = 0
    if 'EOQ' not in st.session_state:
        st.session_state['EOQ'] = 100
    if 'ROP' not in st.session_state:
        st.session_state['ROP'] = 50
    if 'safety_stock' not in st.session_state:
        st.session_state['safety_stock'] = 20
    if 'avg_daily_sales' not in st.session_state:
        st.session_state['avg_daily_sales'] = 30
    if 'delivery_lead_time' not in st.session_state:
        st.session_state['delivery_lead_time'] = 5

def test_product_daily_inventory_levels_chart(sample_demand_df, mock_session_state):
    """Test product_daily_inventory_levels_chart updates session state correctly."""
    product_daily_inventory_levels_chart(sample_demand_df)
    
    assert 'demand_per_year' in st.session_state
    assert 'avg_demand' in st.session_state
    assert 'max_demand' in st.session_state
    assert isinstance(st.session_state['demand_per_year'], np.int64)
    assert isinstance(st.session_state['avg_demand'], (int, float))
    assert isinstance(st.session_state['max_demand'], np.int64)

def test_simulation_chart(sample_demand_df):
    """Test simulation_chart returns correct DataFrame structure."""
    year_sim = 2023
    ss = 100
    rop = 150
    q = 300
    L = 5
    
    result_df = simulation_chart(sample_demand_df, year_sim, ss, rop, q, L)
    
    assert isinstance(result_df, pd.DataFrame)
    assert all(col in result_df.columns for col in ['Date', 'Order_Demand', 'Inventory_Quantity'])
    assert len(result_df) == 365  # Full year of daily data
    assert result_df['Date'].dt.year.unique() == [year_sim]
    assert (result_df['Inventory_Quantity'] >= 0).all()  # No negative inventory

def test_product_fill_rate_chart(sample_inventory_df):
    """Test product_fill_rate_chart handles fill rate calculations correctly."""
    product_fill_rate_chart(sample_inventory_df)
    
    # Calculate fill rate manually for verification
    df_test = sample_inventory_df.loc[sample_inventory_df['Order_Demand'] > 0].copy()
    df_test['Fill_Rate'] = round(df_test['Inventory_Quantity'] / df_test['Order_Demand'], 2)
    df_test['Fill_Rate'] = df_test['Fill_Rate'].apply(lambda x: min(x, 1.0))
    
    assert (df_test['Fill_Rate'] <= 1.0).all()
    assert (df_test['Fill_Rate'] >= 0.0).all()

def test_inventory_chart(mock_session_state):
    """Test inventory_chart generates correct data structure."""
    year = 2023
    inventory_chart(year)
    
    # Verify session state variables are used
    assert 'EOQ' in st.session_state
    assert 'ROP' in st.session_state
    assert 'safety_stock' in st.session_state
    assert 'avg_daily_sales' in st.session_state
    assert 'delivery_lead_time' in st.session_state

@pytest.mark.parametrize("invalid_year", [2020.5, "invalid", -2023])
def test_inventory_chart_invalid_year(invalid_year, mock_session_state):
    """Test inventory_chart handles invalid year inputs."""
    with pytest.raises(Exception):
        inventory_chart(invalid_year)

def test_simulation_chart_edge_cases(sample_demand_df):
    """Test simulation_chart with edge cases."""
    year_sim = 2023
    test_cases = [
        (0, 0, 0, 0),  # All zeros
        (100, 100, 100, 1),  # Equal values
        (1000, 2000, 3000, 10),  # Large values
    ]
    
    for ss, rop, q, L in test_cases:
        result_df = simulation_chart(sample_demand_df, year_sim, ss, rop, q, L)
        assert isinstance(result_df, pd.DataFrame)
        assert (result_df['Inventory_Quantity'] >= 0).all()

def test_product_daily_inventory_levels_empty_df():
    """Test product_daily_inventory_levels_chart with empty DataFrame."""
    empty_df = pd.DataFrame(columns=['Date', 'Order_Demand'])
    product_daily_inventory_levels_chart(empty_df)
    
    assert st.session_state['demand_per_year'] == 0
    assert st.session_state['avg_demand'] == 0
    assert st.session_state['max_demand'] == 0

def test_simulation_chart_data_consistency(sample_demand_df):
    """Test simulation_chart maintains data consistency."""
    year_sim = 2023
    ss = 100
    rop = 150
    q = 300
    L = 5
    
    result_df = simulation_chart(sample_demand_df, year_sim, ss, rop, q, L)
    
    # Verify initial inventory level
    assert result_df['Inventory_Quantity'].iloc[0] == q + ss
    
    # Verify inventory never exceeds maximum possible level
    assert (result_df['Inventory_Quantity'] <= (q + ss)).all()
