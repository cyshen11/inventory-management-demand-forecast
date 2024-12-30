import pytest
import pandas as pd
from components.metrics import ytd_product_fill_rate

class MockColumn:
    def metric(self, label, value):
        self.label = label
        self.value = value

@pytest.fixture
def mock_col():
    return MockColumn()

def test_normal_fill_rate(mock_col):
    # Test case where some orders are fully filled and some are partially filled
    data = {
        'Order_Demand': [100, 50, 75],
        'Inventory_Quantity': [80, 50, 60]
    }
    df = pd.DataFrame(data)
    
    ytd_product_fill_rate(df, mock_col)
    
    # Expected: (80 + 50 + 60) / (100 + 50 + 75) = 0.8444... ≈ 0.8
    assert mock_col.value == "0.8"

def test_perfect_fill_rate(mock_col):
    # Test case where all orders can be completely filled
    data = {
        'Order_Demand': [100, 50, 75],
        'Inventory_Quantity': [100, 50, 75]
    }
    df = pd.DataFrame(data)
    
    ytd_product_fill_rate(df, mock_col)
    
    assert mock_col.value == "1.0"

def test_zero_inventory(mock_col):
    # Test case where there's no inventory
    data = {
        'Order_Demand': [100, 50, 75],
        'Inventory_Quantity': [0, 0, 0]
    }
    df = pd.DataFrame(data)
    
    ytd_product_fill_rate(df, mock_col)
    
    assert mock_col.value == "0.0"

def test_excess_inventory(mock_col):
    # Test case where inventory exceeds demand
    data = {
        'Order_Demand': [100, 50, 75],
        'Inventory_Quantity': [150, 100, 200]
    }
    df = pd.DataFrame(data)
    
    ytd_product_fill_rate(df, mock_col)
    
    assert mock_col.value == "1.0"

def test_empty_dataframe(mock_col):
    # Test case with empty dataframe
    df = pd.DataFrame({'Order_Demand': [], 'Inventory_Quantity': []})
    
    ytd_product_fill_rate(df, mock_col)
    
    assert mock_col.value == "0.0"

def test_zero_demand_filtered(mock_col):
    # Test case where some rows have zero demand (should be filtered out)
    data = {
        'Order_Demand': [100, 0, 75],
        'Inventory_Quantity': [80, 50, 60]
    }
    df = pd.DataFrame(data)
    
    ytd_product_fill_rate(df, mock_col)
    
    # Expected: (80 + 60) / (100 + 75) = 0.8
    assert mock_col.value == "0.8"
