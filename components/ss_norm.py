from components.filters import *
from components.inputs import *
from components.utils import *
import scipy.stats as stats

@st.fragment
def ss_norm(filtered_data):
  col1, col2, col3 = st.columns(3)
  selectbox_uncertainty_type(col1)
  selectbox_time_units(col2)
  
  uncertainty_type = st.session_state["uncertainty_type"]

  if uncertainty_type == "Uncertain demand":
    uncertain_demand(filtered_data)

def uncertain_demand(filtered_data):
  col1, col2, col3 = st.columns(3)
  input_product_fill_rate(col1)
  input_demand_sd(col2, filtered_data)
  input_avg_lead_time(col3)

  product_fill_rate = st.session_state["product_fill_rate"]
  Z = round(stats.norm.ppf(product_fill_rate), 2)
  sd = st.session_state["demand_sd"]
  L = st.session_state["avg_lead_time"]
  ss = round(Z * sd * (L ** 0.5))

  st.info(f"""
    SS: 
      \n = Z x Demand Standard Deviation x sqrt(Average Lead Time)
      \n = {Z} x {sd:.1f} x sqrt({L})
      \n = **{ss}**
  """)

  avg_sales = calculate_avg_demand(filtered_data)
  rop = ss + L * avg_sales

  st.info(f"""
    Reorder Point (ROP)
          \n = SS + Average Lead Time x Average Sales per day
          \n = {ss} + {L} x {avg_sales}
          \n = **{rop}**
  """)