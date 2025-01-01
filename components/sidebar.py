import streamlit as st
from components.dataset import Dataset
from components.filters import *
import pandas as pd


def sidebar():
    """
    Creates and manages the sidebar interface for data filtering and selection.

    This function implements a two-step process in the sidebar:
    1. Data source selection (upload or sample dataset)
    2. Product and year filtering options

    Returns:
    --------
    tuple
        (dynamic_filters, filtered_data) where:
        - dynamic_filters: Filter object containing selected filter parameters
        - filtered_data: Pandas DataFrame containing the filtered dataset
    """

    # Step 1: Data Source Selection
    with st.sidebar.expander("📂 1. Choose data to use"):
        # Toggle between upload and sample dataset options
        data_option = st.segmented_control(
            "Data:", options=["Upload data", "Use sample dataset"]
        )
        # Store selection in session state for persistence
        st.session_state["data_option"] = data_option

        if data_option == "Upload data":
            # Provide template downloads for data formatting
            with open("data/csv/demand_template.csv", "rb") as file:
                st.download_button(
                    label="Download file template for demand",
                    data=file,
                    file_name="demand_template.csv",
                    mime="text/csv",
                )
            with open("data/csv/lead_time_template.csv", "rb") as file2:
                st.download_button(
                    label="Download file template for lead time",
                    data=file2,
                    file_name="lead_time_template.csv",
                    mime="text/csv",
                )

            # File upload interface for user data
            uploaded_file_demand = st.file_uploader(
                "Choose a csv file with historical product demand"
            )
            uploaded_file_lead_time = st.file_uploader(
                "Choose a csv file with historical product lead time"
            )

            # Save uploaded files when both are provided
            if uploaded_file_demand is not None and uploaded_file_lead_time is not None:
                # Save demand data
                with open("data/csv/demand_upload.csv", "wb") as f:
                    f.write(uploaded_file_demand.getbuffer())
                # Save lead time data
                with open("data/csv/lead_time_upload.csv", "wb") as f:
                    f.write(uploaded_file_lead_time.getbuffer())
        else:
            pass

        # Step 2: Product and Year Selection
        with st.sidebar.expander("🔍 2. Choose product and year"):
            # Load dataset based on previous selections
            data = Dataset().data
            # Create dynamic filters for product selection
            dynamic_filters = dynamic_filters_product(data)
            # Apply selected filters to the dataset
            filtered_data = dynamic_filters.filter_df()

        # (Optional) Step 3: Delete data
        with st.sidebar.expander("🗑️ (Optional) 3. Delete uploaded data"):
            # Button to delete all data
            if st.button("Delete"):
                delete_uploaded_data()
                st.markdown("✅ Deleted successfully!")

        st.sidebar.markdown("v1.0.3")

    return dynamic_filters, filtered_data

def delete_uploaded_data():
    """
    Resets the uploaded data files to empty DataFrames with predefined column structures.
    This effectively clears any previously uploaded data while maintaining the expected file format.
    """    
    df_demand = pd.DataFrame({
        "Product_Code": [],
        "Warehouse": [],
        "Product_Category": [],
        "Date": [],
        "Order_Demand": []
    })
    df_demand.to_csv("data/csv/demand_upload.csv")
    
    df_lead_time = pd.DataFrame({
        "Product_Code": [],
        "Ordered_Date": [],
        "Received_Date": [],
        "Lead_Time_Days": [],
    })
    df_lead_time.to_csv("data/csv/lead_time_upload.csv")  