import streamlit as st
import sqlitecloud
from components.filters import *
from components.metrics import *
from components.bar_charts import *
from components.dataframe import *
from components.line_charts import *
from components.inputs import *
from components.dataset import *
from components.eoq import eoq
from components.rop import rop
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

    tab1, tab2 = st.tabs(["Basic", "Average - Max Formula"])

    with tab1:
        @st.fragment
        def ss_basic():
            eoq()
            rop()
            inventory_chart(year)
        
        ss_basic()
        
