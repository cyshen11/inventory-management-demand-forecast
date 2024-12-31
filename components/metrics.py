def ytd_product_fill_rate(df, col):
    """
    Calculate and display the year-to-date fill rate for products.

    The fill rate is calculated as the ratio of total inventory quantity filled
    to total order demand, capped at 100%. Only considers rows with positive
    order demand.

    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing inventory and order information.
        Must have columns 'Order_Demand' and 'Inventory_Quantity'.

    col : streamlit.column
        Streamlit column object to display the metric.

    Returns:
    --------
    None
        Displays the fill rate metric in the specified Streamlit column.

    Notes:
    ------
    - Fill rate is calculated as: min(total_filled / total_demand, 1.0)
    - Returns 0.0 for empty DataFrames or when no positive demand exists
    - Fill rate is rounded to one decimal place for display
    """
    # Handle empty DataFrame case
    if df.empty:
        col.metric("Fill Rate", "0.0")
        return

    # Filter out rows where there is no demand
    # Only consider positive demand for fill rate calculation
    df = df[df["Order_Demand"] > 0]

    # Check if any rows remain after filtering
    if df.empty:
        col.metric("Fill Rate", "0.0")
        return

    # Calculate total demand and filled quantities
    total_demand = df["Order_Demand"].sum()
    total_filled = df["Inventory_Quantity"].sum()

    # Calculate fill rate, capped at 100%
    # If total_demand is 0, return 0.0 to avoid division by zero
    fill_rate = min(total_filled / total_demand, 1.0) if total_demand > 0 else 0.0

    # Display the fill rate metric with one decimal place
    col.metric("Fill Rate", f"{fill_rate:.1f}")
