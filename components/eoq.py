import streamlit as st

@st.fragment
def eoq():
  col1, col2, col3 = st.columns(3)
  D = col1.number_input("Demand per year (D)", value=st.session_state["demand_per_year"])
  K = col2.number_input("Order Cost per purchase order (K)", value=20)
  H = col3.number_input("Holding cost per unit per year (H)", value=0.05)

  Q = (2*(D*K)/H)**(1/2)

  st.info(f"EOQ = sqrt(2(DK)/H) = sqrt(2({D} x {K})/{H}) = **{round(Q)}**")