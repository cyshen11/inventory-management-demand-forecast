"""Line charts components for visualizing inventory and demand data"""

import streamlit as st
import pandas as pd


def product_daily_inventory_levels_chart(df):
    """
    Creates a line chart showing daily order demand and updates session state with demand metrics.

    Args:
        df (pd.DataFrame): DataFrame containing Date and Order_Demand columns

    Updates session state with:
        - demand_per_year: Total annual demand
        - avg_demand: Average daily demand
        - max_demand: Maximum daily demand
    """
    # Sort and aggregate daily demand data
    df = df.sort_values(by="Date")
    df = df[["Date", "Order_Demand"]]
    df = df.groupby("Date").sum().reset_index()
    df.columns = ["Date", "Order_Demand"]

    # Display line chart of daily order demand
    st.line_chart(df, x="Date", y=["Order_Demand"], y_label="Order Demand", height=250)

    # Update session state with demand metrics
    st.session_state["demand_per_year"] = df["Order_Demand"].sum()
    st.session_state["avg_demand"] = round(df["Order_Demand"].sum() / 365)
    st.session_state["max_demand"] = (
        df["Order_Demand"].max()
        if not df.empty
        and "Order_Demand" in df.columns
        and not df["Order_Demand"].isna().all()
        else 0
    )


def simulation_chart(df_demand, year_sim, ss, rop, q, L):
    """
    Simulates and visualizes inventory levels over time based on demand data and inventory parameters.

    Args:
        df_demand (pd.DataFrame): DataFrame with demand data
        year_sim (int): Year to simulate
        ss (float): Safety stock level
        rop (float): Reorder point
        q (float): Order quantity
        L (int): Lead time in days

    Returns:
        pd.DataFrame: DataFrame containing simulated inventory levels
    """
    # Filter and prepare demand data for specified year
    df_demand = df_demand.loc[df_demand["Date"].dt.year == year_sim]
    df_demand = df_demand.sort_values(by="Date")
    df_demand = df_demand[["Date", "Order_Demand"]]
    df_demand = df_demand.groupby("Date").sum().reset_index()
    df_demand.columns = ["Date", "Order_Demand"]

    # Create complete date range for the year
    start_date = pd.to_datetime(f"{year_sim}-01-01")
    end_date = pd.to_datetime(f"{year_sim}-12-31")
    dates = pd.date_range(start=start_date, end=end_date, freq="D")

    # Merge demand data with complete date range
    df = pd.DataFrame({"Date": dates})
    df = pd.merge(df, df_demand, on="Date", how="left")
    df = df.fillna(0)

    # Initialize inventory simulation parameters
    initial_inventory = q + ss
    inventory_levels = []
    current_inventory = initial_inventory
    day_since_trigger_rop = 0

    # Simulate daily inventory changes
    for index, row in df.iterrows():
        demand = row["Order_Demand"]

        # Check reorder point and handle lead time
        if current_inventory <= rop:
            if day_since_trigger_rop == L:
                current_inventory += q
                day_since_trigger_rop = 0
            else:
                day_since_trigger_rop += 1

        # Update inventory levels based on demand
        inventory_levels.append(current_inventory)
        current_inventory -= demand
        current_inventory = max(current_inventory, 0)

    df["Inventory_Quantity"] = inventory_levels

    # Display chart showing demand and inventory levels
    st.line_chart(
        df, x="Date", y=["Order_Demand", "Inventory_Quantity"], y_label="Quantity"
    )

    return df


def product_fill_rate_chart(df):
    """
    Creates a line chart showing daily fill rates.

    Args:
        df (pd.DataFrame): DataFrame containing Order_Demand and Inventory_Quantity columns
    """
    # Calculate fill rates for periods with demand
    df = df.loc[df["Order_Demand"] > 0]
    df["Fill_Rate"] = round(df["Inventory_Quantity"] / df["Order_Demand"], 2)
    df["Fill_Rate"] = df["Fill_Rate"].apply(lambda x: min(x, 1.0))

    # Display fill rate chart
    st.line_chart(df, x="Date", y=["Fill_Rate"], y_label="Fill Rate", height=250)
