from components.filters import *
from components.inputs import *
from components.utils import *
import scipy.stats as stats


@st.fragment
def ss_cycle_service_rate(filtered_data, lead_time_data):
    """
    Main function to calculate safety stock based on cycle service rate.
    Provides different calculation methods based on uncertainty type.

    Args:
        filtered_data (pd.DataFrame): Historical demand data
        lead_time_data (pd.DataFrame): Historical lead time data
    """
    col1, col2, col3 = st.columns(3)
    input_cycle_service_rate(col1)
    selectbox_uncertainty_type(col2)
    selectbox_time_units(col3, 17)

    uncertainty_type = st.session_state["uncertainty_type"]

    # Route to appropriate calculation method based on uncertainty type
    if uncertainty_type == "Uncertain demand":
        uncertain_demand(filtered_data, lead_time_data)
    elif uncertainty_type == "Uncertain lead time":
        uncertain_lead_time(filtered_data, lead_time_data)
    elif uncertainty_type == "Uncertain demand and lead time (independent)":
        uncertain_demand_lead_time_ind(filtered_data, lead_time_data)
    elif uncertainty_type == "Uncertain demand and lead time (dependent)":
        uncertain_demand_lead_time_dep(filtered_data, lead_time_data)


def uncertain_demand(filtered_data, lead_time_data):
    """
    Calculate safety stock when only demand is uncertain.
    Uses formula: SS = Z × σd × √L
    where:
        Z = safety factor based on cycle service rate
        σd = standard deviation of demand
        L = lead time

    Args:
        filtered_data (pd.DataFrame): Historical demand data
        lead_time_data (pd.DataFrame): Historical lead time data
    """
    col1, col2, col3 = st.columns(3)
    input_avg_sales(col1, filtered_data, 1001)
    input_avg_lead_time(col2, lead_time_data, 1002)
    input_demand_sd(col3, filtered_data, 1003)

    cycle_service_rate = st.session_state["cycle_service_rate"]
    Z = round(stats.norm.ppf(cycle_service_rate), 2)
    sd = st.session_state["demand_sd"]
    L = st.session_state["avg_lead_time"]
    ss = round(Z * sd * (L**0.5))

    # Display safety stock calculation
    st.info(
        f"""
    SS: 
      \n = Z x Demand Standard Deviation x sqrt(Average Lead Time)
      \n = {Z} x {sd:.2f} x sqrt({L})
      \n = **{ss}**
  """
    )

    # Calculate and display reorder point
    avg_sales = st.session_state["avg_sales"]
    rop = round(ss + L * avg_sales)
    st.info(
        f"""
    Reorder Point (ROP)
          \n = SS + Average Lead Time x Average Sales
          \n = {ss} + {L} x {avg_sales}
          \n = **{rop}**
  """
    )


def uncertain_lead_time(filtered_data, lead_time_data):
    """
    Calculate safety stock when only lead time is uncertain.
    Uses formula: SS = Z × σL × D
    where:
        Z = safety factor based on cycle service rate
        σL = standard deviation of lead time
        D = average demand

    Args:
        filtered_data (pd.DataFrame): Historical demand data
        lead_time_data (pd.DataFrame): Historical lead time data
    """
    col1, col2, col3 = st.columns(3)
    input_avg_sales(col1, filtered_data, 1006)
    input_avg_lead_time(col2, lead_time_data, 1007)
    input_sd_lead_time(col3, lead_time_data)

    cycle_service_rate = st.session_state["cycle_service_rate"]
    avg_sales = st.session_state["avg_sales"]
    sd_lead_time = st.session_state["sd_lead_time"]

    Z = round(stats.norm.ppf(cycle_service_rate), 2)
    ss = round(Z * sd_lead_time * avg_sales)

    st.info(
        f"""
    SS: 
      \n = Z x Lead Time Standard Deviation x Average Sales
      \n = {Z} x {sd_lead_time:.2f} x {avg_sales}
      \n = **{ss}**
  """
    )

    L = st.session_state["avg_lead_time"]
    rop = round(ss + L * avg_sales)

    st.info(
        f"""
    Reorder Point (ROP)
          \n = SS + Average Lead Time x Average Sales
          \n = {ss} + {L} x {avg_sales}
          \n = **{rop}**
  """
    )


def uncertain_demand_lead_time_ind(filtered_data, lead_time_data):
    """
    Calculate safety stock when both demand and lead time are uncertain and independent.
    Uses formula: SS = Z × √(L × σd² + (D x σd)²)
    where:
        Z = safety factor based on cycle service rate
        L = average lead time
        σd = standard deviation of demand
        D = average demand
        σL = standard deviation of lead time

    Args:
        filtered_data (pd.DataFrame): Historical demand data
        lead_time_data (pd.DataFrame): Historical lead time data
    """
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    input_avg_lead_time(col2, lead_time_data, 1008)
    input_sd_lead_time(col3, lead_time_data)
    input_avg_sales(col5, filtered_data, 1009)
    input_demand_sd(col6, filtered_data, 10010)

    cycle_service_rate = st.session_state["cycle_service_rate"]
    avg_lead_time = st.session_state["avg_lead_time"]
    sd_demand = st.session_state["demand_sd"]
    avg_sales = st.session_state["avg_sales"]
    sd_lead_time = st.session_state["sd_lead_time"]

    Z = round(stats.norm.ppf(cycle_service_rate), 2)
    temp_1 = avg_lead_time * (sd_demand**2)
    temp_2 = (avg_lead_time * sd_lead_time) ** 2
    ss = round(Z * ((temp_1 + temp_2) ** 0.5))
    rop = round(ss + avg_lead_time * avg_sales)

    st.info(
        f"""
    SS: 
      \n = Z x sqrt(Average Lead Time x Demand Standard Deviation^2 + (Average Sales x Lead Time Standard Deviation)^2)
      \n = {Z} x sqrt({avg_lead_time} x {sd_demand}^2 + ({avg_sales} x {sd_lead_time})^2)
      \n = **{ss}**
  """
    )

    st.info(
        f"""
    Reorder Point (ROP)
          \n = SS + Average Lead Time x Average Sales
          \n = {ss} + {avg_lead_time} x {avg_sales}
          \n = **{rop}**
  """
    )


def uncertain_demand_lead_time_dep(filtered_data, lead_time_data):
    """
    Calculate safety stock when both demand and lead time are uncertain and dependent.
    Uses formula: SS = Z × σd × √L + Z × D × σL
    where:
        Z = safety factor based on cycle service rate
        σd = standard deviation of demand
        L = average lead time
        D = average demand
        σL = standard deviation of lead time

    Args:
        filtered_data (pd.DataFrame): Historical demand data
        lead_time_data (pd.DataFrame): Historical lead time data
    """
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    input_avg_lead_time(col2, lead_time_data, 10011)
    input_sd_lead_time(col3, lead_time_data)
    input_avg_sales(col5, filtered_data, 10012)
    input_demand_sd(col6, filtered_data, 10013)

    cycle_service_rate = st.session_state["cycle_service_rate"]
    avg_lead_time = st.session_state["avg_lead_time"]
    sd_demand = st.session_state["demand_sd"]
    avg_sales = st.session_state["avg_sales"]
    sd_lead_time = st.session_state["sd_lead_time"]

    Z = round(stats.norm.ppf(cycle_service_rate), 2)
    temp_1 = Z * sd_demand * (avg_lead_time**0.5)
    temp_2 = Z * avg_sales * sd_lead_time
    ss = round(temp_1 + temp_2)
    rop = round(ss + avg_lead_time * avg_sales)

    st.info(
        f"""
    SS: 
      \n = Z x Demand Standard Deviation x sqrt(Average Lead Time) + Z x Average Sales x Lead Time Standard Deviation
      \n = {Z} x {sd_demand} x sqrt({avg_lead_time}) + {Z} x {avg_sales} x {sd_lead_time}
      \n = **{ss}**
  """
    )

    st.info(
        f"""
    Reorder Point (ROP)
          \n = SS + Average Lead Time x Average Sales
          \n = {ss} + {avg_lead_time} x {avg_sales}
          \n = **{rop}**
  """
    )


@st.fragment
def ss_fill_rate(filtered_data, lead_time_data):
    """
    Calculate safety stock based on fill rate criterion.
    Uses an approximation function to determine safety factor.

    Args:
        filtered_data (pd.DataFrame): Historical demand data
        lead_time_data (pd.DataFrame): Historical lead time data
    """
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    input_fill_rate(col1)
    selectbox_time_units(col2, 2)
    input_avg_sales(col4, filtered_data, 10014)
    input_demand_sd(col5, filtered_data, 10015)
    input_avg_lead_time(col6, lead_time_data, 10016)

    beta = st.session_state["fill_rate"]
    mu = st.session_state["avg_sales"]
    sigma = st.session_state["demand_sd"]
    L = st.session_state["avg_lead_time"]

    z_std_normal_loss = mu * (1 - beta) / sigma
    z = 4.85 - (z_std_normal_loss**1.3) * 0.3924 - (z_std_normal_loss**0.135) * 5.359
    ss = round(z * sigma * (L**0.5))
    rop = ss + L * mu

    st.info(
        f"""
    Safety Stock (SS): **{ss}**
    \n[Formula reference](https://or.stackexchange.com/questions/5589/safety-stock-with-fill-rate-criterion) 
    (using approximation function)
  """
    )
    st.info(
        f"""
    Reorder Point (ROP)
          \n = SS + Average Lead Time x Average Sales
          \n = {ss} + {L} x {mu}
          \n = **{rop:.0f}**
  """
    )


@st.fragment
def ss_holding_stockout(filtered_data, lead_time_data):
    """
    Calculate safety stock based on holding cost and stockout cost optimization.
    Uses formula that balances the cost of holding inventory against stockout costs.

    Args:
        filtered_data (pd.DataFrame): Historical demand data
        lead_time_data (pd.DataFrame): Historical lead time data
    """
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    input_holding_cost(col=col1, key=10017)
    input_stockout_cost(col=col2, key=10018)
    selectbox_time_units(col=col3, key=10019)
    input_avg_sales(col=col4, df=filtered_data, key=10020)
    input_demand_sd(col=col5, df=filtered_data, key=10021)
    input_avg_lead_time(col=col6, df=lead_time_data, key=10022)

    h = st.session_state["holding_cost"]
    p = st.session_state["stockout_cost"]
    mu = st.session_state["avg_sales"]
    sigma = st.session_state["demand_sd"]
    L = st.session_state["avg_lead_time"]

    # Calculate optimal safety stock based on costs
    ss = round((mu + sigma * stats.norm.cdf(p / (p + h))) * (L**0.5))
    rop = ss + L * mu

    st.info(
        f"""
    Safety Stock (SS): **{ss}**
    \n[Formula reference](https://or.stackexchange.com/questions/5589/safety-stock-with-fill-rate-criterion) 
  """
    )
    st.info(
        f"""
    Reorder Point (ROP)
          \n = SS + Average Lead Time x Average Sales
          \n = {ss} + {L} x {mu}
          \n = **{rop:.0f}**
  """
    )
