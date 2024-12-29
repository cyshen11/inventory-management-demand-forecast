import streamlit as st
from components.dataset import Dataset
from components.filters import *
import pandas as pd

def sidebar():

  with st.sidebar.expander("# 1. Choose data to use"):
    data_option = st.segmented_control("", options=["Upload data", "Use sample dataset"])
    st.session_state["data_option"] = data_option

    if data_option == "Upload data":
      with open("data/csv/demand_template.csv", "rb") as file:
        st.download_button(
          label="Download file template for demand",
          data=file,
          file_name='demand_template.csv',
          mime='text/csv',
        )
      with open("data/csv/lead_time_template.csv", "rb") as file2:
        st.download_button(
          label="Download file template for lead time",
          data=file2,
          file_name='lead_time_template.csv',
          mime='text/csv',
        )
      uploaded_file_demand = st.file_uploader("Choose a csv file with historical product demand")
      uploaded_file_lead_time = st.file_uploader("Choose a csv file with historical product lead time")

      if uploaded_file_demand is not None and uploaded_file_lead_time is not None:
        with open("data/csv/demand_upload.csv", "wb") as f:
          f.write(uploaded_file_demand.getbuffer())
        with open("data/csv/lead_time_upload.csv", "wb") as f:
          f.write(uploaded_file_lead_time.getbuffer())

      
    with st.sidebar.expander("# 2. Choose product and year"):
      data = Dataset().data
      dynamic_filters = dynamic_filters_product(data)
      filtered_data = dynamic_filters.filter_df()

  return dynamic_filters, filtered_data