import streamlit as st
from components.filters import *
from components.metrics import *
from components.bar_charts import *
from components.dataframe import *
from components.line_charts import *
from components.inputs import *
from components.dataset import *
from components.ss_basic import ss_basic
from components.ss_average_max import ss_average_max
from components.ss_norm import ss_norm
import warnings
warnings.filterwarnings("ignore")

st.title("Inventory Management")
st.subheader("Demand Trend")

dynamic_filters = dynamic_filters_product(Dataset().data)
filtered_data = dynamic_filters.filter_df()
filters = st.session_state[dynamic_filters.filters_name]
year = filtered_data['Date'].dt.year.unique().astype(int)[0]

if len(filters['Product_Code']) > 0 and len(filters['Year']) > 0:
    product_daily_inventory_levels_chart(filtered_data)

    st.subheader("Calculate Safety Stock")
    tab1, tab2, tab3 = st.tabs(["Basic", "Average - Max", "Normal Distribution"])

    with tab1:
        ss_basic(year)

    with tab2:
        ss_average_max()

    with tab3:
        ss_norm()
        
        
