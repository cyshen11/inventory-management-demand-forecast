import streamlit as st

pg = st.navigation([
    st.Page("./pages/inventory_management.py", title="Inventory Management"), 
    st.Page("./pages/demand_forecast.py", title="Demand Forecast"),
    st.Page("./pages/about.py", title="About")
])
pg.run()
