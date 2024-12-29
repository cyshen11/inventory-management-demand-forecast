"""Dataframe component"""

import streamlit as st
import pandas as pd


def dataframe_models_result():
    """
    Combines results from multiple forecasting models into a consolidated DataFrame.

    Parameters:
    -----------
    None

    Returns:
    --------
    None
        Displays a Streamlit dataframe directly in the app
    """
    st.subheader("Models Result")
    st.markdown("Sorted by MAE in increasing order")

    models_result = st.session_state["models_result"]
    
    df = pd.DataFrame.from_dict(models_result)
    df = df.T
    df = df.reset_index()
    df.columns = ["Model", "MAE", "MAPE"]
    df.sort_values(by="MAE", inplace=True)
    
    st.dataframe(
        df,
        hide_index=True,
        column_config={"Model": st.column_config.TextColumn("Model", width="medium")},
    )
