import streamlit as st
from components.inputs import *
from components.line_charts import *
from components.bar_charts import *
from components.dataset import *
from components.metrics import *
from components.filters import *

@st.fragment
def simulation(lead_time_data):

  df = Dataset().data
  df = df.loc[df['Product_Code'] == st.session_state["product_code"]]

  tab1, tab2 = st.tabs(["Actual Data", "Forecast"])
  with tab1:
    simulation_actual_data(df, lead_time_data)

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