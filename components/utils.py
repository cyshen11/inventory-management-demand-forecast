import streamlit as st
import datetime as dt


def group_data_by_time_unit(df):
    """
    Groups the data by specified time unit (Days, Weeks, or Months) and calculates sum of Order_Demand.

    Args:
        df (pandas.DataFrame): Input DataFrame containing 'Date' and 'Order_Demand' columns

    Returns:
        pandas.DataFrame: Grouped DataFrame with date/time unit and aggregated Order_Demand
    """
    time_unit = st.session_state["time_unit"]
    df = df[["Date", "Order_Demand"]]

    if time_unit == "Days":
        df = df.groupby("Date").sum().reset_index()

    elif time_unit == "Weeks":
        df["Week"] = df["Date"].dt.isocalendar().week
        df = df[["Week", "Order_Demand"]]
        df = df.groupby("Week").sum().reset_index()

    elif time_unit == "Months":
        df["Month"] = df["Date"].dt.month
        df = df[["Month", "Order_Demand"]]
        df = df.groupby("Month").sum().reset_index()

    df.columns = ["Date", "Order_Demand"]
    return df


def calculate_sd_demand(df):
    """
    Calculates standard deviation of demand after removing outliers.

    Args:
        df (pandas.DataFrame): Input DataFrame with 'Order_Demand' column

    Returns:
        float: Standard deviation of demand rounded to 1 decimal place
    """
    df = remove_outliers_iqr(df, "Order_Demand")
    df_grouped = group_data_by_time_unit(df)
    sd = round(df_grouped["Order_Demand"].std(), 1)
    return sd


def calculate_avg_demand(df):
    """
    Calculates average demand per time unit (daily, weekly, or monthly).

    Args:
        df (pandas.DataFrame): Input DataFrame with 'Order_Demand' column

    Returns:
        int: Rounded average demand for the specified time unit
    """
    time_unit = st.session_state["time_unit"]
    total_demand = df["Order_Demand"].sum()

    if time_unit == "Days":
        avg_demand = total_demand / 365

    elif time_unit == "Weeks":
        avg_demand = total_demand / 52

    elif time_unit == "Months":
        avg_demand = total_demand / 12

    avg_demand = round(avg_demand)

    return avg_demand


def calculate_sd_lead_time(df):
    """
    Calculates standard deviation of lead time, converting days to specified time unit.

    Args:
        df (pandas.DataFrame): Input DataFrame with 'Lead_Time_Days' column

    Returns:
        float: Standard deviation of lead time rounded to 2 decimal places
    """
    time_unit = st.session_state["time_unit"]

    # Convert lead time days to appropriate time unit
    if time_unit == "Days":
        denom = 1
    elif time_unit == "Weeks":
        denom = 7
    elif time_unit == "Months":
        denom = 30

    df["Lead_Time"] = df["Lead_Time_Days"] / denom
    sd = round(df["Lead_Time"].std(), 2)

    return sd


def calculate_avg_lead_time(df):
    """
    Calculates average lead time, converting days to specified time unit.

    Args:
        df (pandas.DataFrame): Input DataFrame with 'Lead_Time_Days' column

    Returns:
        float: Average lead time rounded to 2 decimal places
    """
    time_unit = st.session_state["time_unit"]
    if time_unit == "Days":
        denom = 1
    elif time_unit == "Weeks":
        denom = 7
    elif time_unit == "Months":
        denom = 30

    df["Lead_Time"] = df["Lead_Time_Days"] / denom
    value = round(df["Lead_Time"].mean(), 2)

    return value


def remove_outliers_iqr(df, column):
    """
    Removes outliers from specified column using the Interquartile Range (IQR) method.
    Values outside 1.5 * IQR below Q1 or above Q3 are considered outliers.

    Args:
        df (pandas.DataFrame): Input DataFrame
        column (str): Name of the column to remove outliers from

    Returns:
        pandas.DataFrame: DataFrame with outliers removed
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
