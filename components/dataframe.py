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

    models_result = st.session_state.get("models_result", {})
    
    # Create empty DataFrame with correct columns
    empty_df = pd.DataFrame(columns=["Model", "MAE", "MAPE"])
    
    # Handle invalid or empty data
    if not isinstance(models_result, dict) or not models_result:
        df = empty_df
    else:
        try:
            df = pd.DataFrame.from_dict(models_result)
            df = df.T
            df = df.reset_index()
            df.columns = ["Model", "MAE", "MAPE"]
            df.sort_values(by="MAE", inplace=True)
        except (ValueError, AttributeError, TypeError):
            df = empty_df
    
    st.dataframe(
        df,
        hide_index=True,
        column_config={"Model": st.column_config.TextColumn("Model", width="medium")},
    )