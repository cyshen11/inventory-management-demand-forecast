import streamlit as st

@st.fragment
def ss_average_max():
  col1, col2 = st.columns(2)
  col3, col4 = st.columns(2)

  max_lead_time = col1.number_input("Max Lead Time (days)", value=20)
  average_lead_time = col2.number_input("Average Lead Time (days)", value=10)
  max_sales = col3.number_input("Max Sales per day", value=st.session_state["max_demand"])
  avg_sales = col4.number_input("Average Sales per day", value=st.session_state["avg_demand"])

  ss = round((max_lead_time * max_sales) - (average_lead_time * avg_sales))
  rop = round(ss + (average_lead_time * avg_sales))

  st.info(f"""
    Safety Stock (SS)
          \n = (Max Lead Time x Max Sales per day) - (Average Lead Time x Average Sales per day)
          \n = ({max_lead_time} x {max_sales}) - ({average_lead_time} x {avg_sales})
          \n = **{ss}**
  """)

  st.info(f"""
    Reorder Point (ROP)
          \n = SS + Average Lead Time x Average Sales per day
          \n = {ss} + {average_lead_time} x {avg_sales}
          \n = **{rop}**
  """)