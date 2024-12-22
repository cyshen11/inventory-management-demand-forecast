import streamlit as st

@st.fragment
def rop():
  col1, col2, col3 = st.columns(3)
  avg_daily_sales = col1.number_input("Average daily sales (AS)", value=st.session_state["avg_demand"])
  delivery_lead_time = col2.number_input("Lead Time (days)", value=20)
  nb_safety_days = col3.number_input("Number of safety days", value=5)

  safety_stock = round(avg_daily_sales * nb_safety_days)
  ROP = avg_daily_sales * delivery_lead_time + safety_stock

  st.info(f"""
    Safety Stock 
          = {avg_daily_sales} x {nb_safety_days} 
          = **{safety_stock}**
  """)

  st.info(f"""
    Reorder Point
          = {avg_daily_sales} x {delivery_lead_time} + {safety_stock} 
          = **{ROP}**
  """)