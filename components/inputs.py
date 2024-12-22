import streamlit as st

def input_product_fill_rate(col):
    col.number_input("Specify Targeted Product Fill Rate", value=0.90, step=0.01)