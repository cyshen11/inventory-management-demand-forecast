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
    dataset,
)
import warnings

warnings.filterwarnings("ignore")


def main():
    """
    Main function that sets up the Streamlit web application for inventory optimization
    and demand forecasting.
    """
    st.title("Inventory Optimization & Demand Forecast")
    st.markdown("Click the top left corner arrow icon to get started.")

    # Initialize sidebar filters and get filtered dataset
    dynamic_filters, filtered_data = sidebar.sidebar()
    filters = st.session_state[dynamic_filters.filters_name]

    # Only display content if both Product Code and Year filters are selected
    if len(filters["Product_Code"]) > 0 and len(filters["Year"]) > 0:
        st.subheader("Demand Trend")
        # Store selected year and product code in session state for later use
        st.session_state["year"] = filters["Year"][0]
        st.session_state["product_code"] = filters["Product_Code"][0]

        # Display daily inventory levels chart
        line_charts.product_daily_inventory_levels_chart(filtered_data)

        # Get and display lead time data
        lead_time_data = dataset.DatasetLeadTime(filters).data
        bar_charts.lead_time_chart(lead_time_data)

        # Economic Order Quantity (EOQ) calculator section
        with st.expander("Calculate Economic Order Quantity (EOQ)"):
            ss_basic.eoq()

        # Safety Stock and Reorder Point calculator section
        with st.expander("Calculate Safety Stock and Reorder Point"):
            # Create tabs for different calculation methods
            tab1, tab2, tab3, tab4, tab5 = st.tabs(
                [
                    "Basic",
                    "Average - Max",
                    "Cycle Service Rate",
                    "Fill Rate",
                    "Holding / Stockout cost",
                ]
            )

            # Basic safety stock calculation
            with tab1:
                ss_basic.ss_basic()

            # Average-Max method calculation
            with tab2:
                ss_average_max.ss_average_max()

            # Cycle service rate based calculation
            with tab3:
                ss_norm.ss_cycle_service_rate(filtered_data, lead_time_data)

            # Fill rate based calculation
            with tab4:
                ss_norm.ss_fill_rate(filtered_data, lead_time_data)

            # Holding/Stockout cost based calculation
            with tab5:
                ss_norm.ss_holding_stockout(filtered_data, lead_time_data)

        with st.expander("Simulation"):
            simulation.simulation(lead_time_data)


if __name__ == "__main__":
    main()
