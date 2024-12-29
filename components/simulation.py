import streamlit as st
from components.inputs import *
from components.line_charts import *
from components.bar_charts import *
from components.dataset import *
from components.metrics import *
from components.filters import *
from components.forecaster import *
from components.dataframe import dataframe_models_result

@st.fragment
def simulation(lead_time_data):

  df = Dataset().data
  df = df.loc[df['Product_Code'] == st.session_state["product_code"]]
  df = df.sort_values(by=['Date'])

  tab1, tab2 = st.tabs(["Actual Data", "Forecast"])
  with tab1:
    simulation_actual_data(df, lead_time_data, 3000)

  with tab2:
    simulation_forecast(df, lead_time_data)

@st.fragment
def simulation_actual_data(df, lead_time_data, key):
  col1, col2, col3 = st.columns(3)
  col4, col5, col6 = st.columns(3)
  year_sim = selectbox_simulation_year(col1, df)
  ss = input_ss(col2, key + 1)
  rop = input_rop(col3, key + 2)
  q = input_oq(col4, key + 3)
  input_avg_lead_time(col5, lead_time_data, key + 4)
  L = round(st.session_state["avg_lead_time"])

  if ss > 0 and rop > 0 and q > 0:
    df_calculation = simulation_chart(df, year_sim, ss, rop, q, L)
    col1, col2, col3 = st.columns(3)
    ytd_product_fill_rate(df_calculation, col1)
    product_fill_rate_chart(df_calculation)

@st.fragment
def simulation_forecast(df, lead_time_data):
  year = st.session_state["year"]
  forecast_year = year + 1
  st.subheader(f"Forecast for {forecast_year} using {year} data")

  # Initialization
  
  if 'models_result' not in st.session_state:
      st.session_state['models_result'] = {}
  if 'forecast_horizon' not in st.session_state:
      st.session_state['forecast_horizon'] = None

  if 'previous_horizon' not in st.session_state:
    st.session_state['previous_horizon'] = st.session_state.get('forecast_horizon')
  # Check if forecast horizon changed
  if st.session_state['previous_horizon'] != st.session_state['forecast_horizon']:
    # Reset the models_result dictionary
    st.session_state['models_result'] = {}
  # Update the previous horizon
  st.session_state['previous_horizon'] = st.session_state['forecast_horizon']
  
  col1, col2, col3 = st.columns(3)

  selectbox_forecast_horizon(col1, 20002)
  selectbox_forecast_model(col2, 20003)

  if forecast_year not in df['Date'].dt.year.unique():
    forecaster = FutureForecaster(df)
    forecaster.plot()
  else:
    BaselineForecaster(df)
    forecaster = Forecaster(df)
    forecaster.score()
    forecaster.plot()
    dataframe_models_result()

  st.subheader("Inventory Management using Forecast Data")
  df = forecaster.predicted_series.pd_dataframe()
  df = df.reset_index()
  df = df.rename(columns={"time": "Date", "Value": "Order_Demand"})
  simulation_actual_data(df, lead_time_data, 4000)