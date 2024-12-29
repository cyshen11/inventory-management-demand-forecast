import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""Test cases for dataset components"""

import pytest
import pandas as pd
import numpy as np
import streamlit as st
from unittest.mock import patch, MagicMock
from components.dataset import Dataset, DatasetLeadTime
import os

@pytest.fixture
def mock_demand_data():
    """Fixture for sample demand data"""
    return pd.DataFrame({
        'Date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'Order_Demand': ['10', '(15)', '20'],
        'Product_Code': ['A001', 'A001', 'A001']
    })

@pytest.fixture
def mock_lead_time_data():
    """Fixture for sample lead time data"""
    return pd.DataFrame({
        'Product_Code': ['A001', 'A001', 'B002'],
        'Ordered_Date': ['2023-01-01', '2023-02-01', '2023-03-01'],
        'Received_Date': ['2023-01-10', '2023-02-10', '2023-03-10'],
        'Lead_Time': [9, 9, 9]
    })

@pytest.fixture
def mock_st():
    """Fixture for mocking all required Streamlit components"""
    session_state = MagicMock()
    session_state.__getitem__.return_value = "Upload data"
    session_state.get.return_value = "Upload data"
    
    st_mock = MagicMock()
    st_mock.session_state = session_state
    return st_mock

@pytest.fixture
def mock_csv_path(tmp_path):
    """Create a mock CSV file structure"""
    csv_dir = tmp_path / "data" / "csv"
    csv_dir.mkdir(parents=True)
    
    # Create demand upload file
    demand_data = pd.DataFrame({
        'Date': ['2023-01-01', '2023-01-02'],
        'Order_Demand': ['10', '20'],
        'Product_Code': ['A001', 'A001']
    })
    demand_file = csv_dir / "demand_upload.csv"
    demand_data.to_csv(demand_file, index=False)
    
    # Create lead time upload file
    lead_time_data = pd.DataFrame({
        'Product_Code': ['A001', 'A001'],
        'Ordered_Date': ['2023-01-01', '2023-02-01'],
        'Received_Date': ['2023-01-10', '2023-02-10'],
        'Lead_Time': [9, 9]
    })
    lead_time_file = csv_dir / "lead_time_upload.csv"
    lead_time_data.to_csv(lead_time_file, index=False)
    
    return tmp_path

class TestDataset:
    def test_prepare_data(self, mock_demand_data, mock_st, monkeypatch):
        """Test the prepare_data method of Dataset class"""
        monkeypatch.setattr(st, "session_state", mock_st.session_state)
        
        dataset = Dataset()
        processed_df = dataset.prepare_data(mock_demand_data)

        assert isinstance(processed_df['Date'].iloc[0], pd.Timestamp)
        assert processed_df['Order_Demand'].iloc[1] == -15
        assert processed_df['Order_Demand'].dtype == 'int64'

    def test_dataset_initialization(self, mock_demand_data, mock_st, monkeypatch):
        """Test Dataset initialization with mock data"""
        monkeypatch.setattr(st, "session_state", mock_st.session_state)
        monkeypatch.setattr(pd, "read_csv", lambda x: mock_demand_data)
        
        dataset = Dataset()
        assert isinstance(dataset.data, pd.DataFrame)
        assert len(dataset.data) == 3
        assert 'Date' in dataset.data.columns
        assert 'Order_Demand' in dataset.data.columns

    def test_file_loading(self, mock_csv_path, mock_st, monkeypatch):
        """Test loading data from CSV file"""
        monkeypatch.setattr(st, "session_state", mock_st.session_state)
        
        # Create a wrapper for pd.read_csv that uses the mock path
        original_read_csv = pd.read_csv
        def mock_read_csv(file_path, *args, **kwargs):
            modified_path = str(mock_csv_path / file_path.lstrip('/'))
            return original_read_csv(modified_path, *args, **kwargs)
        
        # Apply the mock
        monkeypatch.setattr(pd, "read_csv", mock_read_csv)
        
        # Initialize dataset
        with patch('os.path.exists', return_value=True):
            dataset = Dataset()
            
        assert isinstance(dataset.data, pd.DataFrame)
        assert len(dataset.data) == 2
        assert all(isinstance(x, pd.Timestamp) for x in dataset.data['Date'])

    def test_invalid_date_handling(self, mock_st, monkeypatch):
        """Test handling of invalid dates"""
        monkeypatch.setattr(st, "session_state", mock_st.session_state)
        
        invalid_data = pd.DataFrame({
            'Date': ['2023-01-01', np.nan, '2023-01-03'],
            'Order_Demand': ['10', '15', '20'],
            'Product_Code': ['A001', 'A001', 'A001']
        })
        
        dataset = Dataset()
        processed_df = dataset.prepare_data(invalid_data)
        
        assert len(processed_df) == 2
        assert all(isinstance(d, pd.Timestamp) for d in processed_df['Date'])

class TestDatasetLeadTime:
    def test_prepare_data(self, mock_lead_time_data, mock_st, monkeypatch):
        """Test the prepare_data method of DatasetLeadTime class"""
        monkeypatch.setattr(st, "session_state", mock_st.session_state)
        
        filters = {
            "Product_Code": ["A001"],
            "Year": [2023]
        }
        
        dataset = DatasetLeadTime(filters)
        processed_df = dataset.prepare_data(mock_lead_time_data, filters)
        
        assert isinstance(processed_df['Ordered_Date'].iloc[0], pd.Timestamp)
        assert isinstance(processed_df['Received_Date'].iloc[0], pd.Timestamp)
        assert all(processed_df['Product_Code'] == 'A001')
        assert all(processed_df['Received_Date'].dt.year == 2023)

    def test_empty_data_handling(self, mock_st, monkeypatch):
        """Test handling of empty dataset"""
        monkeypatch.setattr(st, "session_state", mock_st.session_state)
        
        empty_data = pd.DataFrame(columns=['Product_Code', 'Ordered_Date', 'Received_Date'])
        
        filters = {
            "Product_Code": ["A001"],
            "Year": [2023]
        }
        
        dataset = DatasetLeadTime(filters)
        processed_df = dataset.prepare_data(empty_data, filters)
        
        assert len(processed_df) == 0
        assert list(processed_df.columns) == ['Product_Code', 'Ordered_Date', 'Received_Date']

    def test_invalid_dates_lead_time(self, mock_lead_time_data, mock_st, monkeypatch):
        """Test handling of invalid dates in lead time data"""
        monkeypatch.setattr(st, "session_state", mock_st.session_state)
        
        invalid_data = pd.DataFrame({
            'Product_Code': ['A001', 'A001'],
            'Ordered_Date': ['2023-01-01', np.nan],
            'Received_Date': ['2023-01-10', '2023-01-15']
        })
        
        filters = {
            "Product_Code": ["A001"],
            "Year": [2023]
        }
        
        dataset = DatasetLeadTime(filters)
        processed_df = dataset.prepare_data(invalid_data, filters)
        
        assert len(processed_df) == 1

def test_dataset_file_not_found(mock_st, monkeypatch):
    """Test handling of missing file"""
    monkeypatch.setattr(st, "session_state", mock_st.session_state)
    
    # Mock pd.read_csv to raise FileNotFoundError
    def mock_read_csv_error(file_path, *args, **kwargs):
        raise FileNotFoundError(f"File {file_path} not found")
    
    monkeypatch.setattr(pd, "read_csv", mock_read_csv_error)
    
    with pytest.raises(FileNotFoundError):
        dataset = Dataset()





