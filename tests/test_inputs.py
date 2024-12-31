import pytest
from unittest.mock import MagicMock, patch
import streamlit as st
import pandas as pd
from components.inputs import *

@pytest.fixture
def mock_streamlit():
    # Mock streamlit session state with common variables
    with patch('streamlit.session_state', {
        "time_unit": "Days",
        # Add other common session state variables here
    }) as mock_state:
        # Mock a streamlit column
        mock_col = MagicMock()
        mock_col.number_input.return_value = 0.9
        yield mock_col, mock_state


@pytest.fixture
def sample_df():
    # Create a sample DataFrame for testing with all required columns
    return pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', periods=5),  # Add date range
        'Order_Demand': [10, 20, 30, 40, 50],
        'Lead_Time_Days': [2, 3, 2, 4, 3]
    })


def test_input_cycle_service_rate(mock_streamlit):
    mock_col, mock_state = mock_streamlit
    input_cycle_service_rate(mock_col)
    
    mock_col.number_input.assert_called_with(
        label="Specify Targeted Cycle Service Rate",
        min_value=0.00,
        max_value=1.00,
        value=0.90,
        step=0.01
    )
    assert mock_state["cycle_service_rate"] == 0.9

def test_input_fill_rate(mock_streamlit):
    mock_col, mock_state = mock_streamlit
    input_fill_rate(mock_col)
    
    mock_col.number_input.assert_called_with(
        label="Specify Targeted Fill Rate",
        min_value=0.00,
        max_value=0.99,
        value=0.90,
        step=0.01
    )
    assert mock_state["fill_rate"] == 0.9

def test_input_demand_sd(mock_streamlit, sample_df):
    mock_col, mock_state = mock_streamlit
    mock_state["time_unit"] = "Days"
    
    # Set a default return value for the mock
    default_value = 15.8  
    mock_col.number_input.return_value = default_value
    
    input_demand_sd(mock_col, sample_df, key="test_key")
    
    # Use assert_called_once_with to ensure exact match
    mock_col.number_input.assert_called_once_with(
        "Specify Demand Standard Deviation",
        value=default_value,  # Use the default value we set
        step=0.1,
        key="test_key"
    )

def test_input_avg_lead_time(mock_streamlit, sample_df):
    mock_col, mock_state = mock_streamlit
    mock_state["time_unit"] = "Days"
    input_avg_lead_time(mock_col, sample_df, key="test_key")
    
    # Set a default return value for the mock
    default_value = 2.8 
    mock_col.number_input.return_value = default_value

    mock_col.number_input.assert_called_with(
        "Specify Average Lead Time (Days)",
        value=default_value,
        key="test_key"
    )

def test_input_avg_sales(mock_streamlit, sample_df):
    mock_col, mock_state = mock_streamlit
    mock_state["time_unit"] = "Days"
    input_avg_sales(mock_col, sample_df, key="test_key")
    
    # Set a default return value for the mock
    default_value = 0
    mock_col.number_input.return_value = default_value

    mock_col.number_input.assert_called_with(
        "Specify Average Demand per day",
        value=default_value,
        key="test_key"
    )

def test_input_holding_cost(mock_streamlit):
    mock_col, mock_state = mock_streamlit
    input_holding_cost(mock_col, key="test_key")
    
    mock_col.number_input.assert_called_with(
        "Specify Holding cost / unit / year (H)",
        value=0.20,
        key="test_key"
    )

def test_input_stockout_cost(mock_streamlit):
    mock_col, mock_state = mock_streamlit
    input_stockout_cost(mock_col, key="test_key")
    
    mock_col.number_input.assert_called_with(
        "Specify Stockout cost per unit (p)",
        value=0.20,
        key="test_key"
    )

def test_input_ss(mock_streamlit):
    mock_col, _ = mock_streamlit
    result = input_ss(mock_col, key="test_key")
    
    mock_col.number_input.assert_called_with(
        "Specify Safety Stock (SS)",
        value=0,
        key="test_key"
    )
    assert result == mock_col.number_input.return_value

def test_input_rop(mock_streamlit):
    mock_col, _ = mock_streamlit
    result = input_rop(mock_col, key="test_key")
    
    mock_col.number_input.assert_called_with(
        "Specify Reorder Point (ROP)",
        value=0,
        key="test_key"
    )
    assert result == mock_col.number_input.return_value

def test_input_oq(mock_streamlit):
    mock_col, _ = mock_streamlit
    result = input_oq(mock_col, key="test_key")
    
    mock_col.number_input.assert_called_with(
        "Specify Order Quantity (Q)",
        value=0,
        key="test_key"
    )
    assert result == mock_col.number_input.return_value
