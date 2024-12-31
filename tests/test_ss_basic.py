import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
from components.ss_basic import eoq, rop

@pytest.fixture
def mock_streamlit():
    with patch('streamlit.columns') as mock_columns, \
         patch('streamlit.session_state', {}) as mock_session_state, \
         patch('streamlit.info') as mock_info:
        
        # Create mock columns that return number_input mocks
        column_mock = MagicMock()
        column_mock.number_input.return_value = 0
        mock_columns.return_value = [column_mock, column_mock]
        
        yield {
            'columns': mock_columns,
            'session_state': mock_session_state,
            'info': mock_info
        }

class TestEOQ:
    def test_eoq_calculation(self, mock_streamlit):
        # Setup mock values
        col_mock = MagicMock()
        col_mock.number_input.side_effect = [1000, 20, 0.2, 100]
        mock_streamlit['columns'].return_value = [col_mock, col_mock]
        
        # Initialize session state
        st.session_state["demand_per_year"] = 1000
        
        # Execute function
        eoq()
        
        # Verify calculations
        expected_eoq = 400  # sqrt(2*1000*20/0.2) rounded to nearest 100
        assert st.session_state["EOQ"] == expected_eoq
        assert st.session_state["lot_size"] == 100

class TestROP:
    def test_rop_calculation(self, mock_streamlit):
        # Setup mock values
        col_mock = MagicMock()
        col_mock.number_input.side_effect = [100, 20, 5]
        mock_streamlit['columns'].return_value = [col_mock, col_mock, col_mock]
        
        # Initialize session state
        st.session_state["avg_demand"] = 100
        
        # Execute function
        rop()
        
        # Verify calculations
        expected_safety_stock = 500  # 100 * 5
        expected_rop = 2500  # (100 * 20) + 500
        
        assert st.session_state["safety_stock"] == expected_safety_stock
        assert st.session_state["ROP"] == expected_rop
        assert st.session_state["avg_daily_sales"] == 100
        assert st.session_state["delivery_lead_time"] == 20

    def test_rop_with_different_values(self, mock_streamlit):
        # Setup mock values with different test data
        col_mock = MagicMock()
        col_mock.number_input.side_effect = [50, 10, 3]
        mock_streamlit['columns'].return_value = [col_mock, col_mock, col_mock]
        
        # Initialize session state
        st.session_state["avg_demand"] = 50
        
        # Execute function
        rop()
        
        # Verify calculations
        expected_safety_stock = 150  # 50 * 3
        expected_rop = 650  # (50 * 10) + 150
        
        assert st.session_state["safety_stock"] == expected_safety_stock
        assert st.session_state["ROP"] == expected_rop
