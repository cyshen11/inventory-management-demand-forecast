import numpy as np
import streamlit as st
import pandas as pd
from darts import TimeSeries
from darts.models import NaiveDrift
from functools import reduce

class Forecaster:
  def __init__(self, df):
    self.timeseries = self.prepare_timeseries(df)
    self.model = self.prepare_model()
    self.train_and_forecast()

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
    if model == "Naive Drift":
      return NaiveDrift()
    
  def train_and_forecast(self):
    train_window = 365  # Days to use for training
    forecast_horizon = 1  # Days to predict
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
    for i in range(len(test_series) - forecast_horizon):
        # Get the current prediction window
        current_train_series = series[: train_window + i]
        future_series = series[train_window + i : train_window + i + forecast_horizon]

        # Update the model (re-fit on the extended series if necessary)
        model.fit(current_train_series)

        # Predict the next `forecast_horizon` steps
        prediction = model.predict(forecast_horizon)
        predictions.append(prediction)
        ground_truth.append(future_series)

    # Concatenate predictions into a single TimeSeries
    self.predicted_series = reduce(lambda x, y: x.concatenate(y), predictions)
    self.actual_series = reduce(lambda x, y: x.concatenate(y), ground_truth)

  def plot(self):
    actual_df = self.actual_series.pd_dataframe()
    predicted_df = self.predicted_series.pd_dataframe()

    combined_df = actual_df.rename(columns={"Value": "Actual"})
    combined_df["Predicted"] = None
    combined_df.loc[predicted_df.index, "Predicted"] = round(predicted_df["Value"])

    st.line_chart(combined_df)

  def score(self):
    actual_values = self.actual_series.pd_dataframe()["Value"]
    predicted_values = self.predicted_series.pd_dataframe()["Value"]
    non_zero_indices = np.where(actual_values != 0)[0]

    bias = round(np.mean(predicted_values - actual_values))
    mae = round(np.mean(np.abs(predicted_values - actual_values)))
    mape = round(np.mean(np.abs((predicted_values[non_zero_indices] - actual_values[non_zero_indices]) / actual_values[non_zero_indices])) * 100)

    col1, col2, col3 = st.columns(3)
    col1.metric("Bias", f"{bias}", border=True)
    col2.metric("MAE", f"{mae}", border=True)
    col3.metric("MAPE", f"{mape}%", border=True)