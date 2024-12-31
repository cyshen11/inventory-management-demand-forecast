"""Generate lead time data for product demand simulation"""

import pandas as pd
from datetime import datetime, timedelta
import random


def main():
    # Read the historical product demand data
    df_demand = pd.read_csv("data/csv/Historical Product Demand.csv")

    # Sample 20% of the demand data to create lead time dataset
    df_lead_time = df_demand.sample(frac=0.2, random_state=42)

    # Generate random order dates for each sampled record
    df_lead_time["Ordered_Date"] = [
        random_datetime_simple() for _ in range(len(df_lead_time))
    ]

    # Get unique products for lead time assignment
    products = df_lead_time["Product_Code"].unique()

    # Create a dictionary to store min and max lead times for each product
    products_min_max_lead_time = {}
    for product in products:
        # Assign random min lead time between 3 to 90 days
        min_lead_time = random.randint(3, 90)
        # Add random additional days (1-15) to create max lead time
        max_lead_time = min_lead_time + random.randint(1, 15)
        products_min_max_lead_time[product] = {
            "min_lead_time": min_lead_time,
            "max_lead_time": max_lead_time,
        }

    # Generate received dates based on order dates and product-specific lead times
    df_lead_time["Received_Date"] = df_lead_time.apply(
        lambda row: generate_received_date(row, products_min_max_lead_time), axis=1
    )

    # Calculate actual lead time in days
    df_lead_time["Lead_Time_Days"] = (
        df_lead_time["Received_Date"] - df_lead_time["Ordered_Date"]
    ).dt.days

    # Select relevant columns for final output
    df_lead_time = df_lead_time[
        ["Product_Code", "Ordered_Date", "Received_Date", "Lead_Time_Days"]
    ]

    # Save the generated lead time data to CSV
    df_lead_time.to_csv("data/csv/Lead Time.csv", index=False)


def random_datetime_simple():
    """
    Generate a random date between 2012-01-01 and 2016-12-31.

    Returns:
        datetime: A random date within the specified range
    """
    start = datetime(2012, 1, 1)
    end = datetime(2016, 12, 31)

    # Calculate the difference in days between start and end dates
    time_between = end - start
    days_between = time_between.days

    # Generate a random number of days to add to start date
    random_days = random.randint(0, days_between)

    return start + timedelta(days=random_days)


def generate_received_date(row, products_min_max_lead_time):
    """
    Generate received date for an order based on product-specific lead time ranges.

    Args:
        row (pandas.Series): Row containing order information
        products_min_max_lead_time (dict): Dictionary containing lead time ranges for each product

    Returns:
        datetime: Generated received date
    """
    product_code = row["Product_Code"]
    min_lead_time = products_min_max_lead_time[product_code]["min_lead_time"]
    max_lead_time = products_min_max_lead_time[product_code]["max_lead_time"]

    # Add random lead time between min and max to order date
    received_date = row["Ordered_Date"] + timedelta(
        days=random.randint(min_lead_time, max_lead_time)
    )

    return received_date


if __name__ == "__main__":
    main()
