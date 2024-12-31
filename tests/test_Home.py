from streamlit.testing.v1 import AppTest
import pandas as pd
import pytest
from unittest.mock import patch

timeout = 30

def test_side_bar():
    at = AppTest.from_file("Home.py")
    at.run(timeout=timeout)
    
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

def test_home_page_initial_load():
    at = AppTest.from_file("Home.py")
    
    # Initialize required session state variables
    at.session_state["dynamic_filters"] = {
        'Product_Code': [],
        'Year': []
    }
    
    at.run(timeout=timeout)
    
    # Test that the title is present
    assert "Inventory Optimization & Demand Forecast" in at.title[0].value

    # Check that subheader is not present
    assert len(at.subheader) == 0, "Subheader should not be visible when filters are empty"

def test_home_page():
    at = AppTest.from_file("Home.py")

    at.session_state["filters"] = {
        'Product_Code': ['Product_0001'], 
        'Year': [2015]
    }
    at.run(timeout=timeout)

    # Check that subheader is present and has correct text
    assert len(at.subheader) > 0, "Subheader should be visible when filters are set"
    assert at.subheader[0].value == "Demand Trend"
