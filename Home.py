import streamlit as st
from components.filters import *
from components.metrics import *
from components.bar_charts import *
from components.dataframe import *
from components.line_charts import *
from components.inputs import *
from components.dataset import *
from components.ss_basic import *
from components.ss_average_max import ss_average_max
from components.ss_norm import *
from components.simulation import *
import warnings
warnings.filterwarnings("ignore")

def main():
    st.title("Inventory Management")
    st.subheader("Demand Trend")

    data = Dataset().data
    dynamic_filters = dynamic_filters_product(data)
    filtered_data = dynamic_filters.filter_df()
    filters = st.session_state[dynamic_filters.filters_name]

    if len(filters['Product_Code']) > 0 and len(filters['Year']) > 0:
        st.session_state['year'] = filters['Year'][0]
        st.session_state['product_code'] = filters['Product_Code'][0]

        product_daily_inventory_levels_chart(filtered_data)

        lead_time_data = DatasetLeadTime(filters).data
        lead_time_chart(lead_time_data)

        with st.expander("Calculate EOQ"):
            eoq()

        with st.expander("Calculate Safety Stock and Reorder Point"):
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "Basic", 
                "Average - Max", 
                "Cycle Service Rate", 
                "Fill Rate",
                "Holding / Stockout cost"
            ])

            with tab1:
                ss_basic()

            with tab2:
                ss_average_max()

            with tab3:
                ss_cycle_service_rate(filtered_data, lead_time_data)

            with tab4:
                ss_fill_rate(filtered_data, lead_time_data)
            
            with tab5:
                ss_holding_stockout(filtered_data, lead_time_data)
        
        with st.expander("Simulation"):
            simulation(lead_time_data)

if __name__ == "__main__":
    main()

