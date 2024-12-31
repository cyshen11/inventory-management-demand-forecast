import streamlit as st


def eoq():
    """
    Calculate the Economic Order Quantity (EOQ) using the Wilson formula.

    EOQ is the optimal order quantity that minimizes total inventory holding and ordering costs.
    The formula used is: EOQ = sqrt(2DK/H), where:
    - D: Annual demand quantity
    - K: Fixed cost per order
    - H: Annual holding cost per unit

    The function also rounds the EOQ to the nearest lot size for practical implementation.
    """
    # Create two columns for input parameters
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    # Get input parameters from user
    D = col1.number_input(
        "Specify Demand per year (D)", value=st.session_state["demand_per_year"]
    )
    K = col2.number_input("Specify Order Cost per purchase order (K)", value=20)
    H = col3.number_input("Specify Holding cost per unit per year (H)", value=0.2)
    lot_size = col4.number_input("Specify Lot size", value=100)

    # Store lot size in session state for future reference
    st.session_state["lot_size"] = lot_size

    # Calculate EOQ using Wilson formula
    Q = (2 * (D * K) / H) ** (1 / 2)
    Q_rounded = round(Q / lot_size) * lot_size
    st.session_state["EOQ"] = Q_rounded

    # Display the calculation and result
    st.info(f"EOQ = sqrt(2(DK)/H) = sqrt(2({D} x {K})/{H}) = **{Q_rounded}**")


def rop():
    """
    Calculate the Reorder Point (ROP) and Safety Stock.

    ROP determines when to place a new order and is calculated as:
    ROP = (Average Daily Sales × Lead Time) + Safety Stock

    Safety Stock is calculated as:
    Safety Stock = Average Daily Sales × Number of Safety Days

    This helps maintain a buffer against stockouts during lead time and demand variability.
    """
    # Create three columns for input parameters
    col1, col2, col3 = st.columns(3)

    # Get input parameters from user
    avg_daily_sales = col1.number_input(
        "Specify Average Daily Sales (AS)", value=st.session_state["avg_demand"]
    )
    delivery_lead_time = col2.number_input("Specify Lead Time (days)", value=20)
    nb_safety_days = col3.number_input("Specify Number of Safety Days", value=5)

    # Store values in session state
    st.session_state["avg_daily_sales"] = avg_daily_sales
    st.session_state["delivery_lead_time"] = delivery_lead_time

    # Calculate Safety Stock
    safety_stock = round(avg_daily_sales * nb_safety_days)
    st.session_state["safety_stock"] = safety_stock

    # Calculate Reorder Point
    ROP = avg_daily_sales * delivery_lead_time + safety_stock
    st.session_state["ROP"] = ROP

    # Display Safety Stock calculation
    st.info(
        f"""
    Safety Stock (SS)
          = AS x Number of safety days
          = {avg_daily_sales} x {nb_safety_days} 
          = **{safety_stock}**
  """
    )

    # Display Reorder Point calculation
    st.info(
        f"""
    Reorder Point
          = AS x Lead Time 
          = {avg_daily_sales} x {delivery_lead_time} + {safety_stock} 
          = **{ROP}**
  """
    )


@st.fragment
def ss_basic():
    """
    Main function to calculate and display basic Safety Stock metrics.
    This function serves as an entry point and currently implements:
    - Reorder Point (ROP) calculation
    """
    rop()
