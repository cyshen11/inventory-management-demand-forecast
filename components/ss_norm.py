from components.filters import *
from components.inputs import *

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