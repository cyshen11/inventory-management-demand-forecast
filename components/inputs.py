import streamlit as st

def input_service_level():
    st.number_input("Specify Service Level", value=0.95, step=0.05)