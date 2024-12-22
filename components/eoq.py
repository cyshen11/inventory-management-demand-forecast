import streamlit as st

def eoq():
  col1, col2 = st.columns(2)
  col3, col4 = st.columns(2)
  D = col1.number_input("Demand per year (D)", value=st.session_state["demand_per_year"])
  K = col2.number_input("Order Cost per purchase order (K)", value=20)
  H = col3.number_input("Holding cost per unit per year (H)", value=0.05)
  lot_size = col4.number_input("Lot size", value=100)
  st.session_state["lot_size"] = lot_size

  Q = (2*(D*K)/H)**(1/2)
  Q_rounded = round(Q/lot_size)*lot_size
  st.session_state["EOQ"] = Q_rounded

  st.info(f"EOQ = sqrt(2(DK)/H) = sqrt(2({D} x {K})/{H}) = **{Q_rounded}**")