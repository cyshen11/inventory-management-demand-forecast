"""Bar charts components"""

import streamlit as st

def lead_time_chart(df):
    """
    Creates a bar chart visualization of lead times over received dates.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame containing at least two columns:
        - Received_Date: Date when items were received
        - Lead_Time_Days: Number of days for delivery
    
    Returns:
    --------
    None
        Displays a Streamlit bar chart directly in the app
    """
    df = df.sort_values(by="Received_Date")
    df = df[["Received_Date", "Lead_Time_Days"]]

    st.bar_chart(
        df,
        x="Received_Date",
        y=["Lead_Time_Days"],
        x_label="Received Date",
        y_label="Lead Time (Days)",
        height=200,
    )
