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
from components.ss_norm import *
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

    lead_time_data = DatasetLeadTime(filters).data
    lead_time_chart(lead_time_data)

    st.subheader("Calculate Safety Stock and Reorder Point")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Basic", 
        "Average - Max", 
        "Cycle Service Rate", 
        "Fill Rate",
        "Holding / Stockout cost"
    ])

    with tab1:
        ss_basic(year)

    with tab2:
        ss_average_max()

    with tab3:
        ss_cycle_service_rate(filtered_data, lead_time_data)

    with tab4:
        ss_fill_rate(filtered_data, lead_time_data)
    
    with tab5:
        ss_holding_stockout(filtered_data, lead_time_data)
        
