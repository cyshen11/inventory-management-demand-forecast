"""Generate lead time data"""

import pandas as pd
from datetime import datetime, timedelta
import random

def main():
  df_demand = pd.read_csv("data/csv/Historical Product Demand.csv")

  df_lead_time = df_demand.sample(frac=0.2, random_state=42)

  df_lead_time['Ordered_Date'] = [random_datetime_simple() for _ in range(len(df_lead_time))]

  products = df_lead_time['Product_Code'].unique()

  products_min_max_lead_time = {}
  for product in products:
    min_lead_time = random.randint(3, 90)
    max_lead_time = min_lead_time + random.randint(1, 15)
    products_min_max_lead_time[product] = {
        'min_lead_time': min_lead_time,
        'max_lead_time': max_lead_time
    }

  df_lead_time['Received_Date'] = df_lead_time.apply(lambda row: generate_received_date(row, products_min_max_lead_time), axis=1)
  df_lead_time['Lead_Time_Days'] = (df_lead_time['Received_Date'] - df_lead_time['Ordered_Date']).dt.days

  df_lead_time = df_lead_time[['Product_Code', 'Ordered_Date', 'Received_Date', 'Lead_Time_Days']]

  df_lead_time.to_csv("data/csv/Lead Time.csv", index=False)


# Method 1: Simple and straightforward
def random_datetime_simple():
    start = datetime(2012, 1, 1)
    end = datetime(2016, 12, 31)
    
    # Calculate the difference in days
    time_between = end - start
    days_between = time_between.days
    
    # Generate a random number of days to add
    random_days = random.randint(0, days_between)
    
    # Return the random date
    return start + timedelta(days=random_days)

def generate_received_date(row, products_min_max_lead_time):
   product_code = row['Product_Code']
   min_lead_time = products_min_max_lead_time[product_code]['min_lead_time']
   max_lead_time = products_min_max_lead_time[product_code]['max_lead_time']
   received_date = row['Ordered_Date'] + timedelta(days=random.randint(min_lead_time, max_lead_time))

   return received_date

if __name__ == "__main__":
  main()