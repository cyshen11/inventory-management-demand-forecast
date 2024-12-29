import streamlit as st
from components.dataset import Dataset
from components.filters import *

def sidebar():

  with st.sidebar.expander("## 1. Choose data to use"):
    data_option = st.segmented_control("", options=["Upload data", "Use sample dataset"])

    if data_option == "Upload data":
      with open("data/csv/Historical Product Demand Template.csv", "rb") as file:
        st.download_button(
          label="Download file template for demand",
          data=file,
          file_name='demand.csv',
          mime='text/csv',
        )
      with open("data/csv/Lead Time Template.csv", "rb") as file2:
        st.download_button(
          label="Download file template for lead time",
          data=file2,
          file_name='lead_time.csv',
          mime='text/csv',
        )
      uploaded_file_demand = st.file_uploader("Choose a csv file with historical product demand")
      uploaded_file_lead_time = st.file_uploader("Choose a csv file with historical product lead time")
    else:
      data = Dataset().data
  
    dynamic_filters = dynamic_filters_product(data)
    filtered_data = dynamic_filters.filter_df()

  return dynamic_filters, filtered_data