import streamlit as st
from components.line_charts import inventory_chart

def eoq():
  col1, col2 = st.columns(2)
  col3, col4 = st.columns(2)
  D = col1.number_input("Demand per year (D)", value=st.session_state["demand_per_year"])
  K = col2.number_input("Order Cost per purchase order (K)", value=20)
  H = col3.number_input("Holding cost per unit per year (H)", value=0.2)
  lot_size = col4.number_input("Lot size", value=100)
  st.session_state["lot_size"] = lot_size

  Q = (2*(D*K)/H)**(1/2)
  Q_rounded = round(Q/lot_size)*lot_size
  st.session_state["EOQ"] = Q_rounded

  st.info(f"EOQ = sqrt(2(DK)/H) = sqrt(2({D} x {K})/{H}) = **{Q_rounded}**")

def rop():
  col1, col2, col3 = st.columns(3)
  avg_daily_sales = col1.number_input("Average daily sales (AS)", value=st.session_state["avg_demand"])
  st.session_state['avg_daily_sales'] = avg_daily_sales
  
  delivery_lead_time = col2.number_input("Lead Time (days)", value=20)
  st.session_state['delivery_lead_time'] = delivery_lead_time

  nb_safety_days = col3.number_input("Number of safety days", value=5)

  safety_stock = round(avg_daily_sales * nb_safety_days)
  st.session_state["safety_stock"] = safety_stock

  ROP = avg_daily_sales * delivery_lead_time + safety_stock
  st.session_state["ROP"] = ROP

  st.info(f"""
    Safety Stock (SS)
          = AS x Number of safety days
          = {avg_daily_sales} x {nb_safety_days} 
          = **{safety_stock}**
  """)

  st.info(f"""
    Reorder Point
          = AS x Lead Time 
          = {avg_daily_sales} x {delivery_lead_time} + {safety_stock} 
          = **{ROP}**
  """)

@st.fragment
def ss_basic():
    rop()
    # inventory_chart(year)