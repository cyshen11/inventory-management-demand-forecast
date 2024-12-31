import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
from darts import TimeSeries
from components.forecaster import Forecaster, BaselineForecaster, FutureForecaster
import time

# ============= Fixtures ============= #

@pytest.fixture
def sample_patterns():
    """Create sample patterns for testing."""
    def create_patterns(length):
        return {
            'constant': np.ones(length),
            'linear_trend': np.linspace(0, 100, length),
            'random': np.random.randint(1, 100, size=length)
        }
    return create_patterns

@pytest.fixture
def sample_df(sample_patterns):
    """Create sample DataFrame with different patterns for testing."""
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    patterns = sample_patterns(len(dates))
    
    data = {
        'Date': dates,
        'Order_Demand': patterns['random']  # Default pattern
    }
    df = pd.DataFrame(data)
    return df, patterns  # Return both DataFrame and patterns dictionary

@pytest.fixture
def mock_session_state():
    """Initialize mock Streamlit session state with default values."""
    session_state = {
        'year': 2023,
        'forecast_model': "Naive Drift",
        'forecast_horizon': "Day",
        'models_result': {},
        'mae_baseline': 0,
        'mape_baseline': 0
    }
    
    for key, value in session_state.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    return session_state

@pytest.fixture
def forecaster(sample_df, mock_session_state):
    """Create Forecaster instance for testing."""
    df, _ = sample_df  # Only use the DataFrame part
    return Forecaster(df)

# ============= Base Forecaster Tests ============= #

class TestForecasterBase:
    """Base test class for common forecasting functionality."""
    
    def test_initialization(self, forecaster):
      """Test proper initialization of forecaster."""
      assert isinstance(forecaster.timeseries, TimeSeries)
      assert forecaster.model is not None
      assert hasattr(forecaster, 'predicted_series')
    
    def test_timeseries_properties(self, forecaster):
        """Test time series basic properties."""
        assert forecaster.timeseries.freq == 'D'
        assert not forecaster.timeseries.pd_dataframe()['Value'].isnull().any()
        assert len(forecaster.timeseries) == 731  # 2023 + 2024 (including leap year)

    @pytest.mark.parametrize("model_name", [
      "Naive Drift",
      ("3-Days Moving Average", "Day"),
    #   ("3-Weeks Moving Average", "Week"),
    #   ("3-Months Moving Average", "Month"),
    #   "Linear Regression",
    #   "ARIMA",
    #   "Exponential Smoothing",
    #   "Theta",
    #   "Kalman Filter",
    #   "Random Forest"
    ])
    def test_model_preparation(self, sample_df, mock_session_state, model_name):
      """Test model preparation for different model types."""
      df, _ = sample_df  # Only use the DataFrame part
      
      if isinstance(model_name, tuple):
          model, horizon = model_name
          st.session_state["forecast_model"] = model
          st.session_state["forecast_horizon"] = horizon
      else:
          st.session_state["forecast_model"] = model_name
      
      forecaster = Forecaster(df)
      model = forecaster.prepare_model()
      assert model is not None
      
      # Test model-specific properties
      if isinstance(model_name, tuple):
          model_name = model_name[0]
      
      if model_name.endswith("Moving Average"):
          assert hasattr(model, 'input_chunk_length')
          assert model.input_chunk_length == 3
      elif model_name == "Linear Regression":
          assert hasattr(model, 'fit')
          assert hasattr(model, 'predict')
      elif model_name == "Random Forest":
          assert hasattr(model, 'n_estimators')

      # Verify the model can generate forecasts
      try:
          forecaster.generate_historical_forecasts()
          assert forecaster.predicted_series is not None
          assert len(forecaster.predicted_series) > 0
      except Exception as e:
          pytest.fail(f"Failed to generate historical forecasts for {model_name}: {str(e)}")

    @pytest.mark.parametrize("horizon,expected_days", [
        ("Day", 1),
        ("Week", 7),
        ("Month", 30)
    ])
    def test_forecast_horizon(self, forecaster, horizon, expected_days):
        """Test forecast horizon calculations."""
        st.session_state["forecast_horizon"] = horizon
        assert forecaster.get_forecast_horizon_days() == expected_days

# ============= Historical Forecaster Tests ============= #

class TestHistoricalForecaster(TestForecasterBase):
    """Test class for historical forecasting functionality."""
    
    def test_historical_forecasts(self, forecaster):
        """Test historical forecast generation."""
        assert forecaster.predicted_series is not None
        assert forecaster.actual_series is not None
        assert len(forecaster.predicted_series) > 0
        assert len(forecaster.actual_series) > 0
    
    def test_score_calculation(self, sample_df, mock_session_state):
      """Test scoring metrics calculation."""
      df, _ = sample_df  # Only use the DataFrame part
      forecaster = Forecaster(df)
      baseline = BaselineForecaster(df)
      
      forecaster.score()
      model = st.session_state["forecast_model"]
      results = st.session_state['models_result'][model]
      
      assert 'MAE' in results
      assert 'MAPE' in results
      assert isinstance(results['MAE'], (int, float))
      assert isinstance(results['MAPE'], str)
      assert results['MAPE'].endswith('%')

    @pytest.mark.parametrize("pattern", ['constant', 'linear_trend', 'random'])
    def test_different_patterns(self, sample_df, mock_session_state, pattern):
        """Test forecaster with different data patterns."""
        df, patterns = sample_df  # Unpack the tuple from sample_df fixture
        df_copy = df.copy()
        df_copy['Order_Demand'] = patterns[pattern]
        forecaster = Forecaster(df_copy)
        
        assert forecaster.predicted_series is not None
        assert len(forecaster.predicted_series) > 0

        # Add pattern-specific assertions
        pred_values = forecaster.predicted_series.pd_dataframe()['Value'].values
        if pattern == 'constant':
            # For constant pattern, predictions should have low variance
            assert np.std(pred_values) < 10
        elif pattern == 'linear_trend':
            # For linear trend, check if predictions follow the trend
            assert np.all(np.diff(pred_values) >= -100)
        elif pattern == 'random':
            # For random pattern, check if predictions are within reasonable bounds
            assert np.all((pred_values >= 0) & (pred_values <= 100))

# ============= Parameter Grid Tests ============= #

class TestParameterGrid:
    """Test class for parameter grid optimization."""
    
    def test_linear_regression_grid(self, forecaster):
        """Test Linear Regression parameter grid."""
        st.session_state["forecast_model"] = "Linear Regression"
        param_grid = forecaster.define_param_grid()
        
        assert 'lags' in param_grid
        assert 'output_chunk_length' in param_grid
        assert 'n_jobs' in param_grid
        assert isinstance(param_grid['lags'], list)
        assert param_grid['n_jobs'] == [-1]
    
    def test_random_forest_grid(self, forecaster):
        """Test Random Forest parameter grid."""
        st.session_state["forecast_model"] = "Random Forest"
        param_grid = forecaster.define_param_grid()
        
        assert 'n_estimators' in param_grid
        assert 'max_depth' in param_grid
        assert 'lags' in param_grid
        assert isinstance(param_grid['n_estimators'], list)
        assert isinstance(param_grid['max_depth'], list)

# ============= Error Handling Tests ============= #

class TestErrorHandling:
    """Test class for error handling scenarios."""
    
    def test_missing_data(self, sample_df):
        """Test handling of missing data."""
        df, _ = sample_df
        df_copy = df.copy()
        df_copy.loc[df_copy.index[10:20], 'Order_Demand'] = np.nan
        
        forecaster = Forecaster(df_copy)
        # Check if missing values are handled
        assert not forecaster.timeseries.pd_dataframe()['Value'].isnull().any()
    
    def test_negative_values(self, sample_df):
        """Test handling of negative values."""
        df, _ = sample_df
        df_copy = df.copy()
        
        # Create some negative values
        df_copy.loc[df_copy.index[10:20], 'Order_Demand'] = -1
        
        # Initialize forecaster with negative values
        forecaster = Forecaster(df_copy)
        
        # Check if negative values are handled (should be converted to 0 or absolute values)
        timeseries_values = forecaster.timeseries.pd_dataframe()['Value']
        
        # Print debug information
        print("\nDebug information:")
        print(f"Min value: {timeseries_values.min()}")
        print(f"Negative values count: {(timeseries_values < 0).sum()}")
        
        # Assert no negative values
        assert (timeseries_values >= 0).all(), \
            f"Found negative values: {timeseries_values[timeseries_values < 0]}"


# ============= Integration Tests ============= #

@pytest.mark.integration
class TestIntegration:
    """Integration test class."""
    
    @pytest.mark.parametrize("model", [
        "Naive Drift",
    ])
    @pytest.mark.parametrize("horizon", ["Day", "Week", "Month"])
    def test_end_to_end(self, sample_df, mock_session_state, model, horizon):
        """Test end-to-end forecasting process."""
        st.session_state["forecast_model"] = model
        st.session_state["forecast_horizon"] = horizon
        
        df, _ = sample_df  # Only use the DataFrame part= 

        forecaster = Forecaster(df)
        assert forecaster.predicted_series is not None
        
        # Test forecast length matches horizon
        expected_days = {
            "Day": 1,
            "Week": 7,
            "Month": 30
        }[horizon]
        
        assert len(forecaster.predicted_series) >= expected_days

# ============= Performance Tests ============= #

@pytest.mark.performance
class TestPerformance:
    """Performance test class."""
    
    def test_large_dataset(self):
        """Test performance with large dataset."""
        dates = pd.date_range('2020-01-01', '2023-12-31')
        df = pd.DataFrame({
            'Date': dates,
            'Order_Demand': np.random.randint(0, 100, len(dates))
        })
        
        import time
        start_time = time.time()
        
        forecaster = Forecaster(df)
        assert forecaster is not None
        
        execution_time = time.time() - start_time
        assert execution_time < 600  # Should complete within 600 seconds

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
