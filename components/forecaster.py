import numpy as np
import streamlit as st
import pandas as pd
from darts import TimeSeries
from darts.models import NaiveMean

class Forecaster:
  def __init__(self, df, model):
    self.timeseries = self.prepare_timeseries(df)
    # self.model = model
    # self.forecast_window = st.session_state["forecast_window"]

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

  def forecast(self):
    if self.model == 'Naive':
      self.df_forecast = self.forecast_naive()

  def forecast_naive(self):
    df_forecast = self.prepare_forecast_df()

    if len(self.df_fy) == 0:
      df_forecast['Order_Demand'] = np.full(365, self.df_cy['Order_Demand'][-1])
    else:
      if self.forecast_window == 'Day':
        df_forecast['Forecast'] = df_forecast['Order_Demand'].ffill().values
        df_forecast = df_forecast[['Date', 'Year', 'Forecast']]
        df_forecast.columns = ['Date', 'Year', 'Order_Demand']

    return df_forecast