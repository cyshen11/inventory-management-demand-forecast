from streamlit.testing.v1 import AppTest
import pandas as pd
import pytest
from unittest.mock import patch
import time
import streamlit as st

@pytest.fixture
def mock_data():
    filtered_data = pd.DataFrame({
        'date': ['2023-01-01', '2023-01-02'],
        'demand': [100, 150],
        'inventory': [500, 450]
    })
    
    lead_time_data = pd.DataFrame({
        'lead_time': [5, 6],
        'frequency': [10, 15]
    })
    return filtered_data, lead_time_data

@pytest.fixture
def mock_dataset():
    with patch('components.dataset.DatasetLeadTime') as mock_dataset:
        mock_dataset.return_value.data = pd.DataFrame({
            'lead_time': [5, 6],
            'frequency': [10, 15]
        })
        yield mock_dataset

def test_home_page_initial_load():
    at = AppTest.from_file("Home.py")
    
    # Initialize required session state variables
    at.session_state["dynamic_filters"] = {
        'Product_Code': [],
        'Year': []
    }
    
    at.run(timeout=10)
    
    # Test that the title is present
    assert "Inventory Optimization & Demand Forecast" in at.title[0].value

def test_side_bar():
    at = AppTest.from_file("Home.py")
    at.run(timeout=20)
    
    # Check if expanders exist (without accessing specific content)
    expanders = at.expander
    assert len(expanders) > 0
    assert expanders[0].label == "📂 1. Choose data to use"
    assert expanders[0].children[0] # Check if segmented control exist

    assert expanders[1].label == "🔍 2. Choose product and year"
    assert expanders[1].children[0].label == "Select Product_Code"
    assert expanders[1].children[1].label == "Select Year"

    assert expanders[2].label == "🗑️ (Optional) 3. Delete uploaded data"
    assert expanders[2].children[0].label == "Delete" # Check if button exist

def test_home_page_with_filters(mock_dataset):
    at = AppTest.from_file("Home.py")
    
    # Initialize required session state variables
    at.session_state["dynamic_filters"] = {
        'Product_Code': ['P001'],
        'Year': [2023]
    }
    at.session_state["year"] = 2023
    at.session_state["product_code"] = 'P001'
    
    at.run(timeout=10)

    # Check if expanders exist (without accessing specific content)
    expanders = at.expander
    print(expanders)
    assert len(expanders) > 0
    assert expanders[3].label == "Calculate Economic Order Quantity (EOQ)"
    assert expanders[4].label == "Calculate Safety Stock and Reorder Point"
    assert expanders[5].label == "Simulation"

def test_safety_stock_tabs():
    at = AppTest.from_file("Home.py")
    
    # Initialize required session state variables
    at.session_state["dynamic_filters"] = {
        'Product_Code': ['P001'],
        'Year': [2023]
    }
    at.session_state["year"] = 2023
    at.session_state["product_code"] = 'P001'
    
    at.run(timeout=10)
    
    # Verify that expanders exist
    expanders = at.expander
    assert len(expanders) > 0

def test_session_state_updates():
    at = AppTest.from_file("Home.py")
    
    # Initialize session state
    at.session_state["dynamic_filters"] = {
        'Product_Code': ['P001'],
        'Year': [2023]
    }
    at.session_state["year"] = 2023
    at.session_state["product_code"] = 'P001'
    
    at.run(timeout=10)
    
    # Verify session state
    assert at.session_state["year"] == 2023
    assert at.session_state["product_code"] == 'P001'

def test_no_filters_selected():
    at = AppTest.from_file("Home.py")
    
    # Initialize with empty filters
    at.session_state["dynamic_filters"] = {
        'Product_Code': [],
        'Year': []
    }
    
    at.run(timeout=10)
    
    # Verify basic page structure
    assert "Inventory Optimization & Demand Forecast" in at.title[0].value

@pytest.mark.asyncio
async def test_interactive_behavior():
    at = AppTest.from_file("Home.py")
    
    # Initialize required session state
    at.session_state["dynamic_filters"] = {
        'Product_Code': ['P001'],
        'Year': [2023]
    }
    at.session_state["year"] = 2023
    at.session_state["product_code"] = 'P001'
    
    at.run(timeout=10)
    
    # Verify that expanders exist
    expanders = at.expander
    assert len(expanders) > 0

def test_error_handling():
    at = AppTest.from_file("Home.py")
    
    # Initialize with invalid filters
    at.session_state["dynamic_filters"] = {
        'Product_Code': ['INVALID'],
        'Year': [9999]
    }
    at.session_state["year"] = 9999
    at.session_state["product_code"] = 'INVALID'
    
    at.run(timeout=10)
    
    # Verify basic page structure remains intact
    assert "Inventory Optimization & Demand Forecast" in at.title[0].value
