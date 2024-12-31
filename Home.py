import streamlit as st
from components import (
    bar_charts,
    line_charts,
    dataset,
    ss_basic,
    ss_norm,
    simulation,
    ss_average_max,
    sidebar,
    dataset
)
import warnings
warnings.filterwarnings("ignore")

def main():
    st.title("Inventory Optimization & Demand Forecast")

    dynamic_filters, filtered_data = sidebar.sidebar()
    filters = st.session_state[dynamic_filters.filters_name]
    print(filters)

    if len(filters['Product_Code']) > 0 and len(filters['Year']) > 0:
        st.subheader("Demand Trend")
        st.session_state['year'] = filters['Year'][0]
        st.session_state['product_code'] = filters['Product_Code'][0]

        line_charts.product_daily_inventory_levels_chart(filtered_data)

        lead_time_data = dataset.DatasetLeadTime(filters).data
        bar_charts.lead_time_chart(lead_time_data)

        with st.expander("Calculate Economic Order Quantity (EOQ)"):
            ss_basic.eoq()

        with st.expander("Calculate Safety Stock and Reorder Point"):
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "Basic", 
                "Average - Max", 
                "Cycle Service Rate", 
                "Fill Rate",
                "Holding / Stockout cost"
            ])

            with tab1:
                ss_basic.ss_basic()

            with tab2:
                ss_average_max.ss_average_max()

            with tab3:
                ss_norm.ss_cycle_service_rate(filtered_data, lead_time_data)

            with tab4:
                ss_norm.ss_fill_rate(filtered_data, lead_time_data)
            
            with tab5:
                ss_norm.ss_holding_stockout(filtered_data, lead_time_data)
        
        with st.expander("Simulation"):
            simulation.simulation(lead_time_data)

if __name__ == "__main__":
    main()

