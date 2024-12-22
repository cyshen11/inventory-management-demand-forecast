from components.filters import *

@st.fragment
def ss_norm():
  col1, col2 = st.columns(2)
  selectbox_uncertainty_type(col1)
  selectbox_time_units(col2)