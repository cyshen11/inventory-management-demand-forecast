import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""Test cases for dataframe components"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from components.dataframe import dataframe_models_result  

@pytest.fixture
def sample_models_result():
    """Fixture providing sample model results data"""
    return {
        'ARIMA': {'MAE': 10.5, 'MAPE': 5.2},
        'Prophet': {'MAE': 8.3, 'MAPE': 4.1},
        'SARIMA': {'MAE': 12.7, 'MAPE': 6.3}
    }

@pytest.fixture
def expected_dataframe():
    """Fixture providing the expected transformed DataFrame"""
    data = {
        'Model': ['Prophet', 'ARIMA', 'SARIMA'],
        'MAE': [8.3, 10.5, 12.7],
        'MAPE': [4.1, 5.2, 6.3]
    }
    return pd.DataFrame(data).sort_values(by='MAE')

@pytest.fixture
def expected_empty_df():
    """Fixture providing an empty DataFrame with correct columns"""
    return pd.DataFrame(columns=['Model', 'MAE', 'MAPE'])

@pytest.fixture
def mock_st():
    """Fixture for mocking all required Streamlit components"""
    with patch('streamlit.subheader') as mock_subheader, \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.dataframe') as mock_dataframe:
        
        # Create a MagicMock for session_state that behaves like a dict
        session_state = MagicMock()
        session_state.get = MagicMock()
        
        # Create a MagicMock for streamlit with all required components
        st = MagicMock()
        st.session_state = session_state
        st.subheader = mock_subheader
        st.markdown = mock_markdown
        st.dataframe = mock_dataframe
        
        yield st

def test_dataframe_models_result_transformation(mock_st, sample_models_result, expected_dataframe):
    """Test the data transformation logic and DataFrame structure"""
    # Setup mock session state
    mock_st.session_state.get.return_value = sample_models_result
    
    with patch('streamlit.session_state', mock_st.session_state), \
         patch('streamlit.subheader', mock_st.subheader), \
         patch('streamlit.markdown', mock_st.markdown), \
         patch('streamlit.dataframe', mock_st.dataframe):
        
        dataframe_models_result()
    
    actual_df = mock_st.dataframe.call_args[0][0]
    
    pd.testing.assert_frame_equal(
        actual_df.reset_index(drop=True),
        expected_dataframe.reset_index(drop=True),
        check_dtype=True
    )

def test_empty_models_result(mock_st, expected_empty_df):
    """Test handling of empty models result"""
    mock_st.session_state.get.return_value = {}
    
    with patch('streamlit.session_state', mock_st.session_state), \
         patch('streamlit.subheader', mock_st.subheader), \
         patch('streamlit.markdown', mock_st.markdown), \
         patch('streamlit.dataframe', mock_st.dataframe):
        
        dataframe_models_result()
    
    actual_df = mock_st.dataframe.call_args[0][0]
    
    pd.testing.assert_frame_equal(
        actual_df,
        expected_empty_df,
        check_dtype=True
    )

@pytest.mark.parametrize("invalid_data", [
    None,
    "not a dict",
    [1, 2, 3],
    {'invalid': 'format'},
    {'a': 1, 'b': 2},  # Dict without proper structure
])
def test_invalid_models_result(mock_st, invalid_data, expected_empty_df):
    """Test handling of invalid models result data"""
    mock_st.session_state.get.return_value = invalid_data
    
    with patch('streamlit.session_state', mock_st.session_state), \
         patch('streamlit.subheader', mock_st.subheader), \
         patch('streamlit.markdown', mock_st.markdown), \
         patch('streamlit.dataframe', mock_st.dataframe):
        
        dataframe_models_result()
    
    actual_df = mock_st.dataframe.call_args[0][0]
    
    pd.testing.assert_frame_equal(
        actual_df,
        expected_empty_df,
        check_dtype=True
    )