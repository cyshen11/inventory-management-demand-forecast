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
  