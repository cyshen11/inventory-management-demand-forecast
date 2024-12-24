import streamlit as st
from components.inputs import *
from components.line_charts import *
from components.dataset import *

@st.fragment
def simulation():
  st.subheader("Simulation")

  df = Dataset().data
  df = df.loc[df['Product_Code'] == st.session_state["product_code"]]

  col1, col2, col3, col4 = st.columns(4)
  year_sim = input_year(col1, df)
  ss = input_ss(col2)
  rop = input_rop(col3)
  q = input_oq(col4)

  if ss > 0 and rop > 0 and q > 0:
    simulation_chart(df, year_sim, ss, rop, q)