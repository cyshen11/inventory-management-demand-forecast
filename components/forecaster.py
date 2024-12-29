import numpy as np
import streamlit as st
import pandas as pd
from darts import TimeSeries
from darts.models import NaiveDrift, NaiveMovingAverage, Croston, LinearRegressionModel
from darts.models import StatsForecastAutoARIMA, StatsForecastAutoETS, RandomForest
from darts.models import StatsForecastAutoTheta, KalmanForecaster, NBEATSModel
import darts.metrics

class Forecaster:
  def __init__(self, df):
    self.timeseries = self.prepare_timeseries(df)
    self.model = self.prepare_model()
    self.generate_historical_forecasts()

  def prepare_timeseries(self, df):
    year = st.session_state["year"]
    year_forecast = year + 1

    start_date = f'{year}-01-01'
    end_date = f'{year_forecast}-12-31'

    df_filtered = df.loc[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    df_filtered = df_filtered[['Date', 'Order_Demand']]
    df_filtered = df_filtered.groupby('Date').sum().reset_index()

    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    df_forecast = pd.DataFrame({
      'Date': date_range,
    })
    df_forecast = pd.merge(df_forecast, df_filtered, on='Date', how='left')
    df_forecast.fillna(value=0, inplace=True)
    df_forecast = df_forecast[['Date', 'Order_Demand']]
    df_forecast.columns = ["Date", "Value"]
    series = TimeSeries.from_dataframe(df_forecast, "Date", "Value", freq='D')    
    return series

  def prepare_model(self):
    model = st.session_state["forecast_model"]
    forecast_horizon = st.session_state['forecast_horizon']
    if model == "Naive Drift":
      return NaiveDrift()
    elif model == f"3-{forecast_horizon}s Moving Average":
      return NaiveMovingAverage(input_chunk_length=3)
    elif model == "Croston":
      return Croston()
    elif model == "Linear Regression":
      param_grid = self.define_param_grid()
      return self.optimize_model(param_grid)
    elif model == "ARIMA":
      return StatsForecastAutoARIMA()
    elif model == "Exponential Smoothing":
      return StatsForecastAutoETS()
    elif model =="Theta":
      return StatsForecastAutoTheta()
    elif model =="Kalman Filter":
      return KalmanForecaster()
    elif model == "Random Forest":
      param_grid = self.define_param_grid()
      return self.optimize_model(param_grid)

  def define_param_grid(self):
    model = st.session_state["forecast_model"]
    if model == "Linear Regression":
      return {
        'lags': [[-1], [-1,-2], [-1,-2,-3], [-1,-2,-3,-4,-5,-6,-7]],  # Different lag values to test
        'output_chunk_length': [self.get_forecast_horizon_days()],  # Different forecast horizons
        'n_jobs': [-1],  # Use all available cores
      }
    elif model == "Random Forest":
        return {
            'n_estimators': [50, 100],  # Reduced number of options for tree count
            'max_depth': [10, 20],  # Reduced depth options
            'lags': [[-1], [-1,-2,-3], [-1,-2,-3,-4,-5,-6,-7]],  # Key lag values
            'output_chunk_length': [self.get_forecast_horizon_days()],  # Reduced forecast horizons
            'n_jobs': [-1]  # Use all available cores
        }
    

  def optimize_model(self, param_grid):
    
    year = st.session_state["year"]
    split_point = pd.to_datetime(f'{year}-11-01')
    series = self.timeseries.drop_after(split_point)

    split_point_1 = pd.to_datetime(f'{year}-10-31')
    split_point_2 = pd.to_datetime(f'{year + 1}-01-01')
    val_series = self.timeseries.drop_before(split_point_1).drop_after(split_point_2)

    args = {
      "parameters": param_grid,
      "series": series,
      "val_series": val_series,
      "n_jobs": -1,
      "metric": darts.metrics.mae,
      "show_warnings": False  
    }

    forecast_model = st.session_state["forecast_model"]
    if forecast_model == "Linear Regression":
      gridsearch = LinearRegressionModel.gridsearch(**args)
    elif forecast_model == "Random Forest":
      gridsearch = RandomForest.gridsearch(**args)
      
    best_model = gridsearch[0]
    best_params = gridsearch[1]

    with st.popover("Best parameters"):
      st.write(best_params)
        
    return best_model

  def generate_historical_forecasts(self):
    forecast_horizon=self.get_forecast_horizon_days()
    historical_forecast = self.model.historical_forecasts(
      self.timeseries,
      forecast_horizon=forecast_horizon,
      start=365 - forecast_horizon + 1,
      verbose=False
    )
    year = st.session_state["year"]
    split_point = pd.to_datetime(f'{year}-12-31')
    self.predicted_series = historical_forecast
    self.actual_series = self.timeseries.drop_before(split_point)

  def plot(self):
    actual_df = self.actual_series.pd_dataframe()
    predicted_df = self.predicted_series.pd_dataframe()

    combined_df = predicted_df.rename(columns={"Value": "Forecast"})
    combined_df["Actual"] = 0
    combined_df.loc[actual_df.index, "Actual"] = round(actual_df["Value"])
    combined_df.fillna(0, inplace=True)

    st.line_chart(combined_df)

  def get_forecast_horizon_days(self):
    forecast_horizon = st.session_state["forecast_horizon"]
    if forecast_horizon == "Day":
      return 1
    elif forecast_horizon == "Week":
      return 7
    elif forecast_horizon == "Month":
      return 30

  def score(self):
    actual_values = self.actual_series.pd_dataframe()["Value"]
    predicted_values = self.predicted_series.pd_dataframe()["Value"]
    non_zero_indices = np.where(actual_values != 0)[0]

    bias = round(np.mean(predicted_values - actual_values))
    mae = round(np.mean(np.abs(predicted_values - actual_values)))
    mape = round(np.mean(np.abs((predicted_values[non_zero_indices] - actual_values[non_zero_indices]) / actual_values[non_zero_indices])) * 100)

    mae_baseline = st.session_state['mae_baseline']
    mape_baseline = st.session_state['mape_baseline']

    mae_delta = float(mae - mae_baseline) / mae_baseline
    mape_delta = float(mape - mape_baseline) / mape_baseline

    col1, col2= st.columns(2)
    # col1.metric("Bias", f"{bias}", border=True)
    col1.metric(
      "MAE (compared to baseline Naive Drift)", 
      f"{mae}", 
      border=True, 
      delta=f"{round(mae_delta * 100)}%",
      delta_color="inverse"
    )
    col2.metric(
      "MAPE (compared to baseline Naive Drift)", 
      f"{mape}%", 
      border=True, 
      delta=f"{round(mape_delta)}%",
      delta_color="inverse"
    )

    model = st.session_state["forecast_model"]
    st.session_state['models_result'].update({
      model: {
        'MAE': mae, 
        'MAPE': f"{mape}%"
      }
    })

class BaselineForecaster:
  def __init__(self, df):
    self.timeseries = self.prepare_timeseries(df)
    self.model = self.prepare_model()
    self.generate_historical_forecasts()
    self.score()

  def prepare_timeseries(self, df):
    year = st.session_state["year"]
    year_forecast = year + 1

    start_date = f'{year}-01-01'
    end_date = f'{year_forecast}-12-31'

    df_filtered = df.loc[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    df_filtered = df_filtered[['Date', 'Order_Demand']]
    df_filtered = df_filtered.groupby('Date').sum().reset_index()

    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    df_forecast = pd.DataFrame({
      'Date': date_range,
    })
    df_forecast = pd.merge(df_forecast, df_filtered, on='Date', how='left')
    df_forecast.fillna(value=0, inplace=True)
    df_forecast = df_forecast[['Date', 'Order_Demand']]
    df_forecast.columns = ["Date", "Value"]
    series = TimeSeries.from_dataframe(df_forecast, "Date", "Value", freq='D')    
    return series

  def prepare_model(self):
    return NaiveDrift()
    
  def generate_historical_forecasts(self):
    historical_forecast = self.model.historical_forecasts(
      self.timeseries,
      forecast_horizon=self.get_forecast_horizon_days(),
      start=365 - self.get_forecast_horizon_days() + 2
    )
    year = st.session_state["year"] + 1
    split_point = pd.to_datetime(f'{year}-01-01')
    self.predicted_series = historical_forecast
    self.actual_series = self.timeseries.drop_before(split_point)

  def get_forecast_horizon_days(self):
    forecast_horizon = st.session_state["forecast_horizon"]
    if forecast_horizon == "Day":
      return 1
    elif forecast_horizon == "Week":
      return 7
    elif forecast_horizon == "Month":
      return 30

  def score(self):
    actual_values = self.actual_series.pd_dataframe()["Value"]
    predicted_values = self.predicted_series.pd_dataframe()["Value"]
    non_zero_indices = np.where(actual_values != 0)[0]

    # bias = round(np.mean(predicted_values - actual_values))
    mae = round(np.mean(np.abs(predicted_values - actual_values)))
    mape = round(np.mean(np.abs((predicted_values[non_zero_indices] - actual_values[non_zero_indices]) / actual_values[non_zero_indices])) * 100)

    st.session_state['mae_baseline'] = mae
    st.session_state['mape_baseline'] = mape

    model = "Naive Drift"
    st.session_state['models_result'].update({
      model: {
        'MAE': mae, 
        'MAPE': f"{mape}%"
      }
    })

class FutureForecaster():
  def __init__(self, df):
    self.timeseries = self.prepare_timeseries(df)
    self.model = self.prepare_model()
    self.predict()

  def prepare_timeseries(self, df):
    year = st.session_state["year"]
    start_date = f'{year}-01-01'
    end_date = f'{year}-12-31'

    df_filtered = df.loc[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    df_filtered = df_filtered[['Date', 'Order_Demand']]
    df_filtered = df_filtered.groupby('Date').sum().reset_index()

    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    df_forecast = pd.DataFrame({
      'Date': date_range,
    })
    df_forecast = pd.merge(df_forecast, df_filtered, on='Date', how='left')
    df_forecast.fillna(value=0, inplace=True)
    df_forecast = df_forecast[['Date', 'Order_Demand']]
    df_forecast.columns = ["Date", "Value"]
    series = TimeSeries.from_dataframe(df_forecast, "Date", "Value", freq='D')    
    return series
  
  def prepare_model(self):
    model = st.session_state["forecast_model"]
    forecast_horizon = st.session_state['forecast_horizon']
    if model == "Naive Drift":
      return NaiveDrift()
    elif model == f"3-{forecast_horizon}s Moving Average":
      return NaiveMovingAverage(input_chunk_length=3)
    elif model == "Croston":
      return Croston()
    elif model == "Linear Regression":
      param_grid = self.define_param_grid()
      return self.optimize_model(param_grid)
    elif model == "ARIMA":
      return StatsForecastAutoARIMA()
    elif model == "Exponential Smoothing":
      return StatsForecastAutoETS()
    elif model =="Theta":
      return StatsForecastAutoTheta()
    elif model =="Kalman Filter":
      return KalmanForecaster()
    elif model == "Random Forest":
      param_grid = self.define_param_grid()
      return self.optimize_model(param_grid)
    
  def predict(self):
    self.model.fit(self.timeseries)
    self.predicted_series = self.model.predict(self.get_forecast_horizon_days())

  def get_forecast_horizon_days(self):
    forecast_horizon = st.session_state["forecast_horizon"]
    if forecast_horizon == "Day":
      return 1
    elif forecast_horizon == "Week":
      return 7
    elif forecast_horizon == "Month":
      return 30
    
  def define_param_grid(self):
    model = st.session_state["forecast_model"]
    if model == "Linear Regression":
      return {
        'lags': [[-1], [-1,-2], [-1,-2,-3], [-1,-2,-3,-4,-5,-6,-7]],  # Different lag values to test
        'output_chunk_length': [self.get_forecast_horizon_days()],  # Different forecast horizons
        'n_jobs': [-1],  # Use all available cores
      }
    elif model == "Random Forest":
        return {
            'n_estimators': [50, 100],  # Reduced number of options for tree count
            'max_depth': [10, 20],  # Reduced depth options
            'lags': [[-1], [-1,-2,-3], [-1,-2,-3,-4,-5,-6,-7]],  # Key lag values
            'output_chunk_length': [self.get_forecast_horizon_days()],  # Reduced forecast horizons
            'n_jobs': [-1]  # Use all available cores
        }
    
  def optimize_model(self, param_grid):
    year = st.session_state["year"]
    split_point = pd.to_datetime(f'{year}-11-01')
    series = self.timeseries.drop_after(split_point)

    split_point = pd.to_datetime(f'{year}-10-31')
    val_series = self.timeseries.drop_before(split_point)

    args = {
      "parameters": param_grid,
      "series": series,
      "val_series": val_series,
      "n_jobs": -1,
      "metric": darts.metrics.mae,
      "show_warnings": False  
    }

    forecast_model = st.session_state["forecast_model"]
    if forecast_model == "Linear Regression":
      gridsearch = LinearRegressionModel.gridsearch(**args)
    elif forecast_model == "Random Forest":
      gridsearch = RandomForest.gridsearch(**args)
      
    best_model = gridsearch[0]
    best_params = gridsearch[1]

    with st.popover("Best parameters"):
      st.write(best_params)
        
    return best_model
  
  def plot(self):
    predicted_df = self.predicted_series.pd_dataframe()
    predicted_df = predicted_df.rename(columns={"Value": "Predicted"})
    predicted_df.fillna(0, inplace=True)
    st.line_chart(predicted_df)