import streamlit as st


@st.fragment
def ss_average_max():
    """
    Calculate Safety Stock and Reorder Point using the Average-Max method.

    This function creates a Streamlit interface that:
    1. Collects lead time and sales data inputs
    2. Calculates Safety Stock using the formula: (Max Lead Time × Max Sales) - (Avg Lead Time × Avg Sales)
    3. Calculates Reorder Point using the formula: Safety Stock + (Avg Lead Time × Avg Sales)
    4. Displays the calculations and results

    Session State Requirements:
        - max_demand: Maximum daily demand/sales
        - avg_demand: Average daily demand/sales
    """
    # Create two rows of columns for input fields
    col1, col2 = st.columns(2)  # First row for lead time inputs
    col3, col4 = st.columns(2)  # Second row for sales inputs

    # Input fields for lead time data
    max_lead_time = col1.number_input("Specify Max Lead Time (days)", value=20)
    average_lead_time = col2.number_input("Specify Average Lead Time (days)", value=10)

    # Input fields for sales data, using session state values as defaults
    max_sales = col3.number_input(
        "Specify Max Sales per day", value=st.session_state["max_demand"]
    )
    avg_sales = col4.number_input(
        "Specify Average Sales per day", value=st.session_state["avg_demand"]
    )

    # Calculate Safety Stock (SS)
    # Formula: (Max Lead Time × Max Sales) - (Average Lead Time × Average Sales)
    ss = round((max_lead_time * max_sales) - (average_lead_time * avg_sales))

    # Calculate Reorder Point (ROP)
    # Formula: Safety Stock + (Average Lead Time × Average Sales)
    rop = round(ss + (average_lead_time * avg_sales))

    # Display Safety Stock calculation and result
    st.info(
        f"""
    Safety Stock (SS)
          \n = (Max Lead Time x Max Sales per day) - (Average Lead Time x Average Sales per day)
          \n = ({max_lead_time} x {max_sales}) - ({average_lead_time} x {avg_sales})
          \n = **{ss}**
  """
    )

    # Display Reorder Point calculation and result
    st.info(
        f"""
    Reorder Point (ROP)
          \n = SS + Average Lead Time x Average Sales per day
          \n = {ss} + {average_lead_time} x {avg_sales}
          \n = **{rop}**
  """
    )
