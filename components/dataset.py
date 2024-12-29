"""Dataset component for handling demand and lead time data processing"""
import pandas as pd
import streamlit as st


class Dataset:
    """
    A class to handle demand dataset operations.
    
    This class manages the loading and preparation of demand data,
    supporting both uploaded and sample datasets.
    
    Attributes:
        data (pd.DataFrame): Processed demand dataset
    """
    def __init__(self):
        """
        Initialize Dataset instance.
        
        Loads either uploaded or sample demand data based on the session state.
        The data is then prepared using the prepare_data method.
        """
        data_option = st.session_state["data_option"]
        if data_option == "Upload data":
            filename = "demand_upload"
        else:
            filename = "demand_sample"

        df = pd.read_csv(f"data/csv/{filename}.csv")
        self.data = self.prepare_data(df)

    def prepare_data(self, df):
        """
        Prepare and clean the demand dataset.
        
        Parameters:
            df (pd.DataFrame): Raw demand data DataFrame
        
        Returns:
            pd.DataFrame: Cleaned and processed demand data
        
        Processing steps:
            1. Converts Date column to datetime
            2. Filters valid dates
            3. Converts bracketed numbers to negative values
            4. Ensures Order_Demand is integer type
        """
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.loc[df["Date"] == df["Date"]]
        # Convert bracketed numbers to negatives using regex
        df["Order_Demand"] = df["Order_Demand"].replace("\((\d+)\)", "-\\1", regex=True)
        df["Order_Demand"] = df["Order_Demand"].astype(int)
        return df


class DatasetLeadTime:
    """
    A class to handle lead time dataset operations.
    
    This class manages the loading and preparation of lead time data,
    supporting both uploaded and sample datasets with filtering capabilities.
    
    Attributes:
        data (pd.DataFrame): Processed lead time dataset
    """
    def __init__(self, filters):
        """
        Initialize DatasetLeadTime instance.
        
        Parameters:
            filters (dict): Dictionary containing filtering criteria
                          Expected keys: 'Product_Code', 'Year'
        
        Loads either uploaded or sample lead time data based on the session state
        and applies the specified filters.
        """
        data_option = st.session_state["data_option"]
        if data_option == "Upload data":
            filename = "lead_time_upload"
        else:
            filename = "lead_time_sample"

        df = pd.read_csv(f"data/csv/{filename}.csv")
        self.data = self.prepare_data(df, filters)

    def prepare_data(self, df, filters):
        """
        Prepare and filter the lead time dataset.
        
        Parameters:
            df (pd.DataFrame): Raw lead time data DataFrame
            filters (dict): Filtering criteria for Product_Code and Year
        
        Returns:
            pd.DataFrame: Cleaned and filtered lead time data
        
        Processing steps:
            1. Converts date columns to datetime
            2. Filters data for specific product code
            3. Filters data for specific year
        """
        df["Ordered_Date"] = pd.to_datetime(df["Ordered_Date"])
        df["Received_Date"] = pd.to_datetime(df["Received_Date"])
        df = df.loc[df["Ordered_Date"] == df["Ordered_Date"]]
        df = df.loc[df["Received_Date"] == df["Received_Date"]]

        product_code = filters["Product_Code"][0]
        year = filters["Year"][0]

        df = df.loc[df["Product_Code"] == product_code]
        df = df.loc[df["Received_Date"].dt.year == year]

        return df
