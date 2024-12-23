"""Dataset"""
import pandas as pd

class Dataset:
  def __init__(self):
    df = pd.read_csv("data/csv/Historical Product Demand.csv")
    self.data = self.prepare_data(df)

  def prepare_data(self, df):
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.loc[df['Date'] == df['Date']]
    # Convert bracketed numbers to negatives using regex
    df['Order_Demand'] = df['Order_Demand'].replace('\((\d+)\)', '-\\1', regex=True)
    df['Order_Demand'] = df['Order_Demand'].astype(int)
    return df
  
class DatasetLeadTime:
  def __init__(self, filters):
    df = pd.read_csv("data/csv/Lead Time.csv")
    self.data = self.prepare_data(df, filters)

  def prepare_data(self, df, filters):
    df['Ordered_Date'] = pd.to_datetime(df['Ordered_Date'])
    df['Received_Date'] = pd.to_datetime(df['Received_Date'])

    product_code = filters['Product_Code'][0]
    year = filters['Year'][0]

    df = df.loc[df['Product_Code'] == product_code]
    df = df.loc[df['Received_Date'].dt.year == year]

    return df
  