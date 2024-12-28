import numpy as np
import streamlit as st
import pandas as pd
from darts import TimeSeries
from darts.models import NaiveDrift, NaiveMovingAverage, Croston, LinearRegressionModel
from darts.models import StatsForecastAutoARIMA, StatsForecastAutoETS, RandomForest
from darts.models import StatsForecastAutoTheta, KalmanForecaster, RNNModel
from darts.metrics import mae, mape
from functools import reduce
from darts.metrics import mae, mape
from sklearn.model_selection import ParameterGrid

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
    elif model == "RNN":
      return RNNModel(
        input_chunk_length=290, # 80% of 365 days
        training_length=290,  # 80% of 365 days
        output_chunk_length=7,
        n_epochs=20,
        model_name="RNN",
      )

  def define_param_grid(self):
    model = st.session_state["forecast_model"]
    if model == "Linear Regression":
      return {
        'lags': [[-1], [-1,-2], [-1,-2,-3], [-1,-2,-3,-4,-5,-6,-7]],  # Different lag values to test
        'output_chunk_length': [1, 7, 30],  # Different forecast horizons
        'n_jobs': [-1],  # Use all available cores
      }
    elif model == "Random Forest":
        return {
            'n_estimators': [50, 100],  # Reduced number of options for tree count
            'max_depth': [10, 20],  # Reduced depth options
            'lags': [[-1], [-1,-2,-3], [-1,-2,-3,-4,-5,-6,-7]],  # Key lag values
            'output_chunk_length': [1, 7],  # Reduced forecast horizons
            'n_jobs': [-1]  # Use all available cores
        }
    elif model == "Gradient Boosting":
        return {
            'lags': [[-1], [-1,-2,-3], [-1,-2,-3,-4,-5,-6,-7]],
            'output_chunk_length': [1, 7],  # Forecast horizon
            'n_jobs': [-1],  # Use all cores
            'num_leaves': [31, 63],  # Control model complexity
            'learning_rate': [0.05, 0.1],  # Learning rate
            'n_estimators': [100, 200],  # Number of boosting iterations
            'max_depth': [-1],  # Unlimited depth
            'min_data_in_leaf': [20, 50],  # Minimum number of records in leaf
            'feature_fraction': [0.8, 1.0],  # Feature subsampling for each tree
            'bagging_fraction': [0.8, 1.0],  # Row subsampling
            'bagging_freq': [5],  # Bagging frequency
            'objective': ['regression'],  # For time series regression
            'metric': ['mae'],  # Evaluation metric
            'boosting_type': ['gbdt'],  # Traditional Gradient Boosting
            'verbose': [-1]  # Suppress logging
        }
    

  def optimize_model(self, param_grid):
    start_date = pd.to_datetime(f'{st.session_state["year"]}-01-01')
    end_date = pd.to_datetime(f'{st.session_state["year"]}-12-31')
    timeseries_cy = self.timeseries.slice(start_date, end_date)

    # Split data for validation
    train_cutoff = int(len(timeseries_cy) * 0.8)
    train_series = timeseries_cy[:train_cutoff]
    val_series = timeseries_cy[train_cutoff:]

    best_mae = float('inf')
    best_model = None
    best_params = None

    forecast_model = st.session_state["forecast_model"]

    # Grid search through parameters
    for params in ParameterGrid(param_grid):
        if forecast_model == "Linear Regression":
          model = LinearRegressionModel(**params)
        elif forecast_model == "Random Forest":
          model = RandomForest(**params)
        
        # try:
        # Train model
        model.fit(train_series)
        
        # Make predictions
        predictions = model.predict(len(val_series))
        
        # Calculate metrics
        current_mae = mae(val_series, predictions)
        
        # Update best model if current one is better
        if current_mae < best_mae:
            best_mae = current_mae
            best_model = model
            best_params = params
                
        # except Exception as e:
        #     continue

    with st.popover("Best parameters"):
      st.write(best_params)
        
    return best_model

  def generate_historical_forecasts(self):
    historical_forecast = self.model.historical_forecasts(
      self.timeseries,
      forecast_horizon=self.get_forecast_horizon_days(),
      start=365
    )
    year = st.session_state["year"] + 1
    split_point = pd.to_datetime(f'{year}-01-01')
    self.predicted_series = historical_forecast
    self.actual_series = self.timeseries.drop_before(split_point)

  def plot(self):
    actual_df = self.actual_series.pd_dataframe()
    predicted_df = self.predicted_series.pd_dataframe()

    combined_df = actual_df.rename(columns={"Value": "Actual"})
    combined_df["Predicted"] = None
    combined_df.loc[predicted_df.index, "Predicted"] = round(predicted_df["Value"])
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

    # bias = round(np.mean(predicted_values - actual_values))
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
    self.train_and_forecast()
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
    
  def train_and_forecast(self):
    
    train_window = 365  # Days to use for training
    forecast_horizon = self.get_forecast_horizon_days()  # Days to predict
    series = self.timeseries
    model = self.model

    # Split the series into initial training and the rest for incremental predictions
    initial_train_series = series[:train_window]
    test_series = series[train_window:]

    # Fit the model on the initial training set
    model.fit(initial_train_series)

    # Store predictions and ground truth for evaluation
    predictions = []
    ground_truth = []

    # Incremental training and prediction
    forecast_cycles = int((len(test_series) - forecast_horizon)/forecast_horizon)
    for i in range(forecast_cycles):
        i_mul_forecast_horizon = i * forecast_horizon

        # Get the current prediction window
        current_train_series = series[: train_window + i_mul_forecast_horizon]
        future_series = series[train_window + i_mul_forecast_horizon : train_window + i_mul_forecast_horizon + forecast_horizon]

        # Update the model (re-fit on the extended series if necessary)
        model.fit(current_train_series)

        # Predict the next `forecast_horizon` steps
        prediction = model.predict(forecast_horizon)
        predictions.append(prediction)
        ground_truth.append(future_series)

    # Concatenate predictions into a single TimeSeries
    self.predicted_series = reduce(lambda x, y: x.concatenate(y, ignore_time_axis=True), predictions)
    self.actual_series = reduce(lambda x, y: x.concatenate(y, ignore_time_axis=True), ground_truth)

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