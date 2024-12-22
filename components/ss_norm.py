from components.filters import *
from components.inputs import *

@st.fragment
def ss_norm():
  col1, col2, col3 = st.columns(3)
  selectbox_uncertainty_type(col1)
  selectbox_time_units(col2)
  input_product_fill_rate(col3)