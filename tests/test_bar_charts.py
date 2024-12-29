import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""Test cases for bar chart components"""
import pandas as pd
import pytest
import streamlit as st
from components.bar_charts import lead_time_chart

@pytest.fixture
def sample_lead_time_data():
    """
    Fixture providing sample lead time data for testing
    
    Returns:
        pd.DataFrame: Sample DataFrame with Received_Date and Lead_Time_Days
    """
    return pd.DataFrame({
        'Received_Date': pd.date_range(start='2023-01-01', periods=5),
        'Lead_Time_Days': [5, 7, 3, 6, 4],
        'Product_Code': ['A001'] * 5
    })

@pytest.fixture
def mock_streamlit(monkeypatch):
    """
    Fixture to mock Streamlit's bar_chart function
    
    Returns:
        MagicMock: Mock object for st.bar_chart
    """
    from unittest.mock import MagicMock
    mock_bar_chart = MagicMock()
    monkeypatch.setattr(st, "bar_chart", mock_bar_chart)
    return mock_bar_chart

class TestLeadTimeChart:
  """Test cases for lead_time_chart function"""

  def test_data_sorting(self, sample_lead_time_data, mock_streamlit):
      """Test if data is correctly sorted by Received_Date"""
      # Create unsorted data
      unsorted_data = sample_lead_time_data.sample(frac=1)  # Shuffle the data
      
      # Call the function
      lead_time_chart(unsorted_data)
      
      # Get the data passed to st.bar_chart
      called_data = mock_streamlit.call_args[0][0]
      
      # Verify data is sorted
      assert all(called_data['Received_Date'].diff()[1:] >= pd.Timedelta(0))

  def test_column_selection(self, sample_lead_time_data, mock_streamlit):
      """Test if only required columns are selected"""
      # Add extra column
      data_with_extra = sample_lead_time_data.copy()
      data_with_extra['Extra_Column'] = 'test'
      
      # Call the function
      lead_time_chart(data_with_extra)
      
      # Get the data passed to st.bar_chart
      called_data = mock_streamlit.call_args[0][0]
      
      # Verify only required columns are present
      assert list(called_data.columns) == ['Received_Date', 'Lead_Time_Days']

  def test_chart_parameters(self, sample_lead_time_data, mock_streamlit):
      """Test if chart parameters are correctly set"""
      # Call the function
      lead_time_chart(sample_lead_time_data)
      
      # Verify chart parameters
      call_kwargs = mock_streamlit.call_args[1]
      assert call_kwargs['x'] == 'Received_Date'
      assert call_kwargs['y'] == ['Lead_Time_Days']
      assert call_kwargs['height'] == 200
      assert call_kwargs['x_label'] == 'Received Date'
      assert call_kwargs['y_label'] == 'Lead Time (Days)'

  def test_empty_dataframe(self, mock_streamlit):
      """Test handling of empty DataFrame"""
      empty_df = pd.DataFrame(columns=['Received_Date', 'Lead_Time_Days'])
      
      # Call the function
      lead_time_chart(empty_df)
      
      # Verify function handles empty DataFrame
      called_data = mock_streamlit.call_args[0][0]
      assert len(called_data) == 0

  def test_missing_columns(self):
      """Test handling of DataFrame with missing required columns"""
      invalid_df = pd.DataFrame({
          'Wrong_Date': pd.date_range(start='2023-01-01', periods=3),
          'Wrong_Lead_Time': [5, 7, 3]
      })
      
      # Verify function raises KeyError for missing columns
      with pytest.raises(KeyError):
          lead_time_chart(invalid_df)

  def test_data_types(self, sample_lead_time_data, mock_streamlit):
      """Test if data types are handled correctly"""
      # Convert lead time to float
      data_with_float = sample_lead_time_data.copy()
      data_with_float['Lead_Time_Days'] = data_with_float['Lead_Time_Days'].astype(float)
      
      # Call the function
      lead_time_chart(data_with_float)
      
      # Verify function handles float data type
      assert mock_streamlit.called

  def test_date_format(self, sample_lead_time_data, mock_streamlit):
      """Test if different date formats are handled correctly"""
      # Convert dates to string format
      data_with_str_dates = sample_lead_time_data.copy()
      data_with_str_dates['Received_Date'] = data_with_str_dates['Received_Date'].dt.strftime('%Y-%m-%d')
      
      # Call the function
      lead_time_chart(data_with_str_dates)
      
      # Verify function processes string dates
      assert mock_streamlit.called

def test_negative_lead_times(mock_streamlit):
    """Test handling of negative lead times"""
    negative_data = pd.DataFrame({
        'Received_Date': pd.date_range(start='2023-01-01', periods=3),
        'Lead_Time_Days': [-1, 0, 1]
    })
    
    # Call the function
    lead_time_chart(negative_data)
    
    # Verify function handles negative values
    assert mock_streamlit.called

def test_large_dataset(mock_streamlit):
    """Test performance with large dataset"""
    large_data = pd.DataFrame({
        'Received_Date': pd.date_range(start='2023-01-01', periods=1000),
        'Lead_Time_Days': range(1000)
    })
    
    # Call the function
    lead_time_chart(large_data)
    
    # Verify function handles large dataset
    assert mock_streamlit.called
