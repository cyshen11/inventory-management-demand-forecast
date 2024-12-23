from components.filters import *
from components.inputs import *
from components.utils import *
import scipy.stats as stats

@st.fragment
def ss_norm(filtered_data, lead_time_data):
  col1, col2, col3 = st.columns(3)
  selectbox_uncertainty_type(col1)
  selectbox_time_units(col2)
  
  uncertainty_type = st.session_state["uncertainty_type"]

  if uncertainty_type == "Uncertain demand":
    uncertain_demand(filtered_data, lead_time_data)
  elif uncertainty_type == "Uncertain lead time":
    uncertain_lead_time(filtered_data, lead_time_data)

def uncertain_demand(filtered_data, lead_time_data):
  col1, col2, col3 = st.columns(3)
  input_product_fill_rate(col1)
  input_demand_sd(col2, filtered_data)
  input_avg_lead_time(col3, lead_time_data)

  product_fill_rate = st.session_state["product_fill_rate"]
  Z = round(stats.norm.ppf(product_fill_rate), 2)
  sd = st.session_state["demand_sd"]
  L = st.session_state["avg_lead_time"]
  ss = round(Z * sd * (L ** 0.5))

  st.info(f"""
    SS: 
      \n = Z x Demand Standard Deviation x sqrt(Average Lead Time)
      \n = {Z} x {sd:.2f} x sqrt({L})
      \n = **{ss}**
  """)

  col1, col2, col3 = st.columns(3)
  input_avg_sales(col1, filtered_data)
  avg_sales = st.session_state["avg_sales"]
  rop = round(ss + L * avg_sales)

  st.info(f"""
    Reorder Point (ROP)
          \n = SS + Average Lead Time x Average Sales
          \n = {ss} + {L} x {avg_sales}
          \n = **{rop}**
  """)

def uncertain_lead_time(filtered_data, lead_time_data):
  col1, col2, col3 = st.columns(3)
  input_product_fill_rate(col1)
  input_avg_sales(col2, filtered_data)
  input_sd_lead_time(col3, lead_time_data)

  product_fill_rate = st.session_state["product_fill_rate"]
  avg_sales = st.session_state["avg_sales"]
  sd_lead_time = st.session_state["sd_lead_time"]

  Z = round(stats.norm.ppf(product_fill_rate), 2)
  ss = round(Z * sd_lead_time * avg_sales)

  st.info(f"""
    SS: 
      \n = Z x Lead Time Standard Deviation x Average Sales
      \n = {Z} x {sd_lead_time:.2f} x {avg_sales}
      \n = **{ss}**
  """)

  col1, col2, col3 = st.columns(3)
  input_avg_lead_time(col1, lead_time_data)
  L = st.session_state["avg_lead_time"]
  rop = round(ss + L * avg_sales)

  st.info(f"""
    Reorder Point (ROP)
          \n = SS + Average Lead Time x Average Sales
          \n = {ss} + {L} x {avg_sales}
          \n = **{rop}**
  """)

