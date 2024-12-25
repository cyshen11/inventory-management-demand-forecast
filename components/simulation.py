import streamlit as st
from components.inputs import *
from components.line_charts import *
from components.bar_charts import *
from components.dataset import *
from components.metrics import *
from components.filters import *
from components.forecaster import Forecaster

@st.fragment
def simulation(lead_time_data):

  df = Dataset().data
  df = df.loc[df['Product_Code'] == st.session_state["product_code"]]
  df = df.sort_values(by=['Date'])

  tab1, tab2 = st.tabs(["Actual Data", "Forecast"])
  with tab1:
    simulation_actual_data(df, lead_time_data)

  with tab2:
    simulation_forecast(df, lead_time_data)

@st.fragment
def simulation_actual_data(df, lead_time_data):
  col1, col2, col3 = st.columns(3)
  col4, col5, col6 = st.columns(3)
  year_sim = selectbox_simulation_year(col1, df)
  ss = input_ss(col2)
  rop = input_rop(col3)
  q = input_oq(col4)
  input_avg_lead_time(col5, lead_time_data, 20001)
  L = round(st.session_state["avg_lead_time"])

  if ss > 0 and rop > 0 and q > 0:
    df_calculation = simulation_chart(df, year_sim, ss, rop, q, L)
    col1, col2, col3 = st.columns(3)
    ytd_product_fill_rate(df_calculation, col1)
    product_fill_rate_chart(df_calculation)

@st.fragment
def simulation_forecast(df, lead_time_data):
  forecast_year = st.session_state["year"] + 1
  st.subheader(f"Forecast for {forecast_year}")

  col1, col2, col3 = st.columns(3)
  col4, col5, col6 = st.columns(3)
  col7, col8, col9 = st.columns(3)

  selectbox_forecast_window(col1, 20002)
  selectbox_forecast_model(col2, 20003)
  ss = input_ss(col4, 20004)
  rop = input_rop(col5, 20005)
  q = input_oq(col6, 20006)
  input_avg_lead_time(col7, lead_time_data, 20007)
  L = round(st.session_state["avg_lead_time"])

  forecaster = Forecaster(df)
  forecaster.score()
  forecaster.plot()
  