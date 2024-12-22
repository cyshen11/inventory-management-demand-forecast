"""Dataset"""
import pandas as pd

class Dataset:
  def __init__(self):
    df = pd.read_csv("data/csv/Historical Product Demand.csv")
    self.data = self.prepare_data(df)

  def prepare_data(self, df):
    df['Date'] = pd.to_datetime(df['Date'])
    return df
  