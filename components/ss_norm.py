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

  elif uncertainty_type == "Uncertain demand and lead time (independent)":
    uncertain_demand_lead_time_ind(filtered_data, lead_time_data)

  elif uncertainty_type == "Uncertain demand and lead time (dependent)":
    uncertain_demand_lead_time_dep(filtered_data, lead_time_data)

def uncertain_demand(filtered_data, lead_time_data):
  col1, col2, col3 = st.columns(3)
  input_cycle_service_rate(col1)
  input_demand_sd(col2, filtered_data)
  input_avg_lead_time(col3, lead_time_data)

  cycle_service_rate = st.session_state["cycle_service_rate"]
  Z = round(stats.norm.ppf(cycle_service_rate), 2)
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
  input_cycle_service_rate(col1)
  input_avg_sales(col2, filtered_data)
  input_sd_lead_time(col3, lead_time_data)

  cycle_service_rate = st.session_state["cycle_service_rate"]
  avg_sales = st.session_state["avg_sales"]
  sd_lead_time = st.session_state["sd_lead_time"]

  Z = round(stats.norm.ppf(cycle_service_rate), 2)
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

def uncertain_demand_lead_time_ind(filtered_data, lead_time_data):
  col1, col2, col3 = st.columns(3)
  col4, col5, col6 = st.columns(3)

  input_cycle_service_rate(col1)
  input_avg_lead_time(col2, lead_time_data)
  input_demand_sd(col3, filtered_data)
  input_avg_sales(col4, filtered_data)
  input_sd_lead_time(col5, lead_time_data)

  cycle_service_rate = st.session_state["cycle_service_rate"]
  avg_lead_time = st.session_state["avg_lead_time"]
  sd_demand = st.session_state["demand_sd"]
  avg_sales = st.session_state["avg_sales"]
  sd_lead_time = st.session_state["sd_lead_time"]

  Z = round(stats.norm.ppf(cycle_service_rate), 2)
  temp_1 = avg_lead_time * (sd_demand ** 2)
  temp_2 = (avg_lead_time ** 2) * (sd_lead_time ** 2)
  ss = round(Z * ((temp_1 + temp_2) ** 0.5))
  rop = round(ss + avg_lead_time * avg_sales)

  st.info(f"""
    SS: 
      \n = Z x sqrt(Average Lead Time x Demand Standard Deviation^2 + Average Lead Time^2 x Lead Time Standard Deviation^2)
      \n = {Z} x sqrt({avg_lead_time} x {sd_demand}^2 + {avg_lead_time}^2 x {sd_lead_time}^2)
      \n = **{ss}**
  """)

  st.info(f"""
    Reorder Point (ROP)
          \n = SS + Average Lead Time x Average Sales
          \n = {ss} + {avg_lead_time} x {avg_sales}
          \n = **{rop}**
  """)

def uncertain_demand_lead_time_dep(filtered_data, lead_time_data):
  col1, col2, col3 = st.columns(3)
  col4, col5, col6 = st.columns(3)

  input_cycle_service_rate(col1)
  input_avg_lead_time(col2, lead_time_data)
  input_demand_sd(col3, filtered_data)
  input_avg_sales(col4, filtered_data)
  input_sd_lead_time(col5, lead_time_data)

  cycle_service_rate = st.session_state["cycle_service_rate"]
  avg_lead_time = st.session_state["avg_lead_time"]
  sd_demand = st.session_state["demand_sd"]
  avg_sales = st.session_state["avg_sales"]
  sd_lead_time = st.session_state["sd_lead_time"]

  Z = round(stats.norm.ppf(cycle_service_rate), 2)
  temp_1 = Z * sd_demand * (avg_lead_time ** 0.5)
  temp_2 = Z * avg_sales * sd_lead_time
  ss = round(temp_1 + temp_2)
  rop = round(ss + avg_lead_time * avg_sales)

  st.info(f"""
    SS: 
      \n = Z x Demand Standard Deviation x sqrt(Average Lead Time) + Z x Average Sales x Lead Time Standard Deviation
      \n = {Z} x {sd_demand} x sqrt({avg_lead_time}) + {Z} x {avg_sales} x {sd_lead_time}
      \n = **{ss}**
  """)

  st.info(f"""
    Reorder Point (ROP)
          \n = SS + Average Lead Time x Average Sales
          \n = {ss} + {avg_lead_time} x {avg_sales}
          \n = **{rop}**
  """)

