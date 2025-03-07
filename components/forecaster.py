"""Forecaster components"""

import numpy as np
import streamlit as st
import pandas as pd
from darts import TimeSeries
from darts.models import NaiveDrift, NaiveMovingAverage, LinearRegressionModel
from darts.models import StatsForecastAutoARIMA, StatsForecastAutoETS, RandomForest
from darts.models import StatsForecastAutoTheta, KalmanForecaster
import darts.metrics


class Forecaster:
    """
    A class for time series forecasting using various models.

    This class handles the preparation of time series data, model selection,
    training, and evaluation of forecasts for inventory demand data.

    Attributes:
        timeseries (TimeSeries): Processed time series data
        model: Selected forecasting model instance
        predicted_series (TimeSeries): Generated forecast values
        actual_series (TimeSeries): Actual values for comparison
    """

    def __init__(self, df):
        """
        1. Initialize the Forecaster with input data
        2. Prepare forecasting model
        3. Generate historical forecast

        Args:
            df (pandas.DataFrame): Input DataFrame containing Date and Order_Demand columns
        """
        self.timeseries = self.prepare_timeseries(df)
        self.model = self.prepare_model()
        self.generate_historical_forecasts()

    def prepare_timeseries(self, df):
        """
        Prepare time series data for forecasting.

        Processes the input DataFrame to create a continuous daily time series,
        handling missing values and formatting for the Darts TimeSeries object.

        Args:
            df (pandas.DataFrame): Input DataFrame with Date and Order_Demand columns

        Returns:
            TimeSeries: Darts TimeSeries object ready for forecasting
        """
        year = st.session_state["year"]
        year_forecast = year + 1

        start_date = f"{year}-01-01"
        end_date = f"{year_forecast}-12-31"

        # Filter data for selected time range
        df_filtered = df.loc[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
        df_filtered = df_filtered[["Date", "Order_Demand"]]
        df_filtered = df_filtered.groupby("Date").sum().reset_index()

        # Create continuous date range and merge with filtered data
        date_range = pd.date_range(start=start_date, end=end_date, freq="D")
        df_forecast = pd.DataFrame(
            {
                "Date": date_range,
            }
        )
        df_forecast = pd.merge(df_forecast, df_filtered, on="Date", how="left")

        # Handle missing values
        df_forecast.fillna(value=0, inplace=True)

        # Filter positive values
        df_forecast["Order_Demand"] = df_forecast["Order_Demand"].clip(lower=0)

        df_forecast = df_forecast[["Date", "Order_Demand"]]
        df_forecast.columns = ["Date", "Value"]
        series = TimeSeries.from_dataframe(df_forecast, "Date", "Value", freq="D")

        return series

    def prepare_model(self):
        """
        Initialize the selected forecasting model.

        Creates and returns an instance of the forecasting model selected in the
        Streamlit session state.

        Returns:
            object: Instance of the selected forecasting model
        """
        model = st.session_state["forecast_model"]

        # Handle moving average models
        if "Moving Average" in model:
            input_chunk_length = 3  # Default to 3 periods
            return NaiveMovingAverage(input_chunk_length=input_chunk_length)

        # Other models
        if model == "Naive Drift":
            return NaiveDrift()
        elif model == "Linear Regression":
            param_grid = self.define_param_grid()
            return self.optimize_model(param_grid)
        elif model == "ARIMA":
            return StatsForecastAutoARIMA()
        elif model == "Exponential Smoothing":
            return StatsForecastAutoETS()
        elif model == "Theta":
            return StatsForecastAutoTheta()
        elif model == "Kalman Filter":
            return KalmanForecaster()
        elif model == "Random Forest":
            param_grid = self.define_param_grid()
            return self.optimize_model(param_grid)

    def define_param_grid(self):
        """
        Define parameter grid for model optimization.

        Creates a dictionary of parameters to test during model optimization
        based on the selected model type.

        Returns:
            dict: Parameter grid for model optimization
        """
        model = st.session_state["forecast_model"]
        if model == "Linear Regression":
            return {
                "lags": [
                    [-1],
                    [-1, -2],
                    [-1, -2, -3],
                    [-1, -2, -3, -4, -5, -6, -7],
                ],  # Different lag values to test
                "output_chunk_length": [
                    self.get_forecast_horizon_days()
                ],  # Different forecast horizons
                "n_jobs": [-1],  # Use all available cores
            }
        elif model == "Random Forest":
            return {
                "n_estimators": [50, 100],  # Reduced number of options for tree count
                "max_depth": [10, 20],  # Reduced depth options
                "lags": [
                    [-1],
                    [-1, -2, -3],
                    [-1, -2, -3, -4, -5, -6, -7],
                ],  # Key lag values
                "output_chunk_length": [
                    self.get_forecast_horizon_days()
                ],  # Reduced forecast horizons
                "n_jobs": [-1],  # Use all available cores
            }

    def optimize_model(self, param_grid):
        """
        Perform grid search to optimize model parameters.

        Uses cross-validation to find the best parameters for the selected model.

        Args:
            param_grid (dict): Parameter grid to search

        Returns:
            object: Optimized model instance with best parameters
        """
        year = st.session_state["year"]
        split_point = pd.to_datetime(f"{year}-11-01")
        series = self.timeseries.drop_after(split_point)

        split_point_1 = pd.to_datetime(f"{year}-10-31")
        split_point_2 = pd.to_datetime(f"{year + 1}-01-01")
        val_series = self.timeseries.drop_before(split_point_1).drop_after(
            split_point_2
        )

        # Configure grid search parameters
        args = {
            "parameters": param_grid,
            "series": series,
            "val_series": val_series,
            "n_jobs": -1,
            "metric": darts.metrics.mae,
            "show_warnings": False,
        }

        # Perform grid search for selected model
        forecast_model = st.session_state["forecast_model"]
        if forecast_model == "Linear Regression":
            gridsearch = LinearRegressionModel.gridsearch(**args)
        elif forecast_model == "Random Forest":
            gridsearch = RandomForest.gridsearch(**args)

        best_model = gridsearch[0]
        best_params = gridsearch[1]

        with st.popover("Best parameters"):
            st.write(best_params)

        return best_model

    def generate_historical_forecasts(self):
        """
        Generate historical forecasts for model evaluation.

        Creates forecasts for historical data to evaluate model performance
        and stores both predicted and actual values.
        """
        forecast_horizon = self.get_forecast_horizon_days()
        historical_forecast = self.model.historical_forecasts(
            self.timeseries,
            forecast_horizon=forecast_horizon,
            start=365 - forecast_horizon + 1,
            verbose=False,
        )
        year = st.session_state["year"]
        split_point = pd.to_datetime(f"{year}-12-31")
        self.predicted_series = historical_forecast
        self.actual_series = self.timeseries.drop_before(split_point)

    def plot(self):
        """
        Create a line chart comparing actual vs predicted values.

        Displays a Streamlit line chart showing both the actual and
        forecasted values for visual comparison.
        """
        actual_df = self.actual_series.pd_dataframe()
        predicted_df = self.predicted_series.pd_dataframe()

        combined_df = predicted_df.rename(columns={"Value": "Forecast"})
        combined_df["Actual"] = 0
        combined_df.loc[actual_df.index, "Actual"] = round(actual_df["Value"])
        combined_df.fillna(0, inplace=True)

        st.line_chart(combined_df)

    def get_forecast_horizon_days(self):
        """
        Convert forecast horizon setting to number of days.

        Returns:
            int: Number of days in the forecast horizon
        """
        forecast_horizon = st.session_state["forecast_horizon"]
        if forecast_horizon == "Day":
            return 1
        elif forecast_horizon == "Week":
            return 7
        elif forecast_horizon == "Month":
            return 30

    def score(self):
        """
        Calculate and display forecast performance metrics.

        Computes MAE and MAPE metrics, comparing them against the baseline model,
        and displays results using Streamlit metrics.
        """
        actual_values = self.actual_series.pd_dataframe()["Value"]
        predicted_values = self.predicted_series.pd_dataframe()["Value"]
        non_zero_indices = np.where(actual_values != 0)[0]

        # Calculate performance metrics
        bias = round(np.mean(predicted_values - actual_values))
        mae = round(np.mean(np.abs(predicted_values - actual_values)))
        mape = round(
            np.mean(
                np.abs(
                    (
                        predicted_values[non_zero_indices]
                        - actual_values[non_zero_indices]
                    )
                    / actual_values[non_zero_indices]
                )
            )
            * 100
        )

        # Compare with baseline
        mae_baseline = st.session_state["mae_baseline"]
        mape_baseline = st.session_state["mape_baseline"]

        mae_delta = float(mae - mae_baseline) / mae_baseline
        mape_delta = float(mape - mape_baseline) / mape_baseline

        # Display metrics
        col1, col2 = st.columns(2)
        col1.metric(
            "MAE (compared to baseline Naive Drift)",
            f"{mae}",
            border=True,
            delta=f"{round(mae_delta * 100)}%",
            delta_color="inverse",
        )
        col2.metric(
            "MAPE (compared to baseline Naive Drift)",
            f"{mape}%",
            border=True,
            delta=f"{round(mape_delta * 100)}%",
            delta_color="inverse",
        )

        # Store results
        model = st.session_state["forecast_model"]
        st.session_state["models_result"].update(
            {model: {"MAE": mae, "MAPE": f"{mape}%"}}
        )


class BaselineForecaster:
    """
    A class for generating baseline forecasts using the Naive Drift model.

    This class serves as a benchmark for comparing other forecasting models.
    It implements the same interface as the main Forecaster class but uses
    only the Naive Drift model.
    """

    def __init__(self, df):
        """
        Initialize the BaselineForecaster with input data.

        Args:
            df (pandas.DataFrame): Input DataFrame containing Date and Order_Demand columns
        """
        self.timeseries = self.prepare_timeseries(df)
        self.model = self.prepare_model()
        self.generate_historical_forecasts()
        self.score()

    def prepare_timeseries(self, df):
        """
        Prepare time series data for forecasting.

        Processes the input DataFrame to create a continuous daily time series,
        handling missing values and formatting for the Darts TimeSeries object.

        Args:
            df (pandas.DataFrame): Input DataFrame with Date and Order_Demand columns

        Returns:
            TimeSeries: Darts TimeSeries object ready for forecasting
        """
        year = st.session_state["year"]
        year_forecast = year + 1

        start_date = f"{year}-01-01"
        end_date = f"{year_forecast}-12-31"

        df_filtered = df.loc[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
        df_filtered = df_filtered[["Date", "Order_Demand"]]
        df_filtered = df_filtered.groupby("Date").sum().reset_index()

        date_range = pd.date_range(start=start_date, end=end_date, freq="D")
        df_forecast = pd.DataFrame(
            {
                "Date": date_range,
            }
        )
        df_forecast = pd.merge(df_forecast, df_filtered, on="Date", how="left")
        df_forecast.fillna(value=0, inplace=True)
        df_forecast["Order_Demand"] = df_forecast["Order_Demand"].clip(lower=0)
        df_forecast = df_forecast[["Date", "Order_Demand"]]
        df_forecast.columns = ["Date", "Value"]
        series = TimeSeries.from_dataframe(df_forecast, "Date", "Value", freq="D")
        return series

    def prepare_model(self):
        """
        Creates and returns an instance of the Naive Drift forecasting model.

        Returns:
            object: Instance of the Naive Drift forecasting model
        """
        return NaiveDrift()

    def generate_historical_forecasts(self):
        """
        Generate historical forecasts for model evaluation.

        Creates forecasts for historical data to evaluate model performance
        and stores both predicted and actual values.
        """
        historical_forecast = self.model.historical_forecasts(
            self.timeseries,
            forecast_horizon=self.get_forecast_horizon_days(),
            start=365 - self.get_forecast_horizon_days() + 2,
        )
        year = st.session_state["year"] + 1
        split_point = pd.to_datetime(f"{year}-01-01")
        self.predicted_series = historical_forecast
        self.actual_series = self.timeseries.drop_before(split_point)

    def get_forecast_horizon_days(self):
        """
        Convert forecast horizon setting to number of days.

        Returns:
            int: Number of days in the forecast horizon
        """
        forecast_horizon = st.session_state["forecast_horizon"]
        if forecast_horizon == "Day":
            return 1
        elif forecast_horizon == "Week":
            return 7
        elif forecast_horizon == "Month":
            return 30

    def score(self):
        """
        Calculate forecast performance metrics.

        Computes MAE and MAPE baseline metrics and store in Streamlit session.
        """
        actual_values = self.actual_series.pd_dataframe()["Value"]
        predicted_values = self.predicted_series.pd_dataframe()["Value"]
        non_zero_indices = np.where(actual_values != 0)[0]

        # bias = round(np.mean(predicted_values - actual_values))
        mae = round(np.mean(np.abs(predicted_values - actual_values)))
        mape = round(
            np.mean(
                np.abs(
                    (
                        predicted_values[non_zero_indices]
                        - actual_values[non_zero_indices]
                    )
                    / actual_values[non_zero_indices]
                )
            )
            * 100
        )

        st.session_state["mae_baseline"] = mae
        st.session_state["mape_baseline"] = mape

        model = "Naive Drift"
        st.session_state["models_result"].update(
            {model: {"MAE": mae, "MAPE": f"{mape}%"}}
        )


class FutureForecaster:
    """
    A class for generating future forecasts using various time series models.

    This class handles the preparation of time series data and generation of
    future predictions using different forecasting models. Unlike the main
    Forecaster class, this focuses on future predictions rather than
    historical validation.

    Attributes:
        timeseries (TimeSeries): Processed time series data
        model: Selected forecasting model instance
        predicted_series (TimeSeries): Generated forecast values for future periods
    """

    def __init__(self, df):
        """
        Initialize the FutureForecaster with input data.

        Args:
            df (pandas.DataFrame): Input DataFrame containing Date and Order_Demand columns
        """
        self.timeseries = self.prepare_timeseries(df)
        self.model = self.prepare_model()
        self.predict()

    def prepare_timeseries(self, df):
        """
        Prepare time series data for forecasting.

        Processes the input DataFrame to create a continuous daily time series
        for the selected year, handling missing values and formatting for the
        Darts TimeSeries object.

        Args:
            df (pandas.DataFrame): Input DataFrame with Date and Order_Demand columns

        Returns:
            TimeSeries: Darts TimeSeries object ready for forecasting
        """
        # Get the selected year from session state
        year = st.session_state["year"]
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

        # Filter data for selected time range
        df_filtered = df.loc[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
        df_filtered = df_filtered[["Date", "Order_Demand"]]
        df_filtered = df_filtered.groupby("Date").sum().reset_index()

        # Create continuous date range and merge with filtered data
        date_range = pd.date_range(start=start_date, end=end_date, freq="D")
        df_forecast = pd.DataFrame(
            {
                "Date": date_range,
            }
        )
        df_forecast = pd.merge(df_forecast, df_filtered, on="Date", how="left")
        df_forecast.fillna(value=0, inplace=True)
        df_forecast["Order_Demand"] = df_forecast["Order_Demand"].clip(lower=0)
        df_forecast = df_forecast[["Date", "Order_Demand"]]
        df_forecast.columns = ["Date", "Value"]
        series = TimeSeries.from_dataframe(df_forecast, "Date", "Value", freq="D")

        return series

    def prepare_model(self):
        """
        Initialize the selected forecasting model.

        Creates and returns an instance of the forecasting model selected in the
        Streamlit session state. Supports multiple model types including naive
        methods, statistical models, and machine learning approaches.

        Returns:
            object: Instance of the selected forecasting model
        """
        model = st.session_state["forecast_model"]

        # Handle moving average models
        if "Moving Average" in model:
            input_chunk_length = 3  # Default to 3 periods
            return NaiveMovingAverage(input_chunk_length=input_chunk_length)

        # Other models
        if model == "Naive Drift":
            return NaiveDrift()
        elif model == "Linear Regression":
            param_grid = self.define_param_grid()
            return self.optimize_model(param_grid)
        elif model == "ARIMA":
            return StatsForecastAutoARIMA()
        elif model == "Exponential Smoothing":
            return StatsForecastAutoETS()
        elif model == "Theta":
            return StatsForecastAutoTheta()
        elif model == "Kalman Filter":
            return KalmanForecaster()
        elif model == "Random Forest":
            param_grid = self.define_param_grid()
            return self.optimize_model(param_grid)

    def predict(self):
        """
        Generate future forecasts using the selected model.

        Fits the model to the prepared time series data and generates
        predictions for the specified forecast horizon.
        """
        self.model.fit(self.timeseries)
        self.predicted_series = self.model.predict(self.get_forecast_horizon_days())

    def get_forecast_horizon_days(self):
        """
        Convert forecast horizon setting to number of days.

        Translates the forecast horizon setting from the session state
        into the corresponding number of days.

        Returns:
            int: Number of days in the forecast horizon
        """
        forecast_horizon = st.session_state["forecast_horizon"]
        if forecast_horizon == "Day":
            return 1
        elif forecast_horizon == "Week":
            return 7
        elif forecast_horizon == "Month":
            return 30

    def define_param_grid(self):
        """
        Define parameter grid for model optimization.

        Creates a dictionary of parameters to test during model optimization
        based on the selected model type. Supports different parameter sets
        for Linear Regression and Random Forest models.

        Returns:
            dict: Parameter grid for model optimization
        """
        model = st.session_state["forecast_model"]
        if model == "Linear Regression":
            return {
                "lags": [
                    [-1],
                    [-1, -2],
                    [-1, -2, -3],
                    [-1, -2, -3, -4, -5, -6, -7],
                ],  # Different lag values to test
                "output_chunk_length": [
                    self.get_forecast_horizon_days()
                ],  # Different forecast horizons
                "n_jobs": [-1],  # Use all available cores
            }
        elif model == "Random Forest":
            return {
                "n_estimators": [50, 100],  # Reduced number of options for tree count
                "max_depth": [10, 20],  # Reduced depth options
                "lags": [
                    [-1],
                    [-1, -2, -3],
                    [-1, -2, -3, -4, -5, -6, -7],
                ],  # Key lag values
                "output_chunk_length": [
                    self.get_forecast_horizon_days()
                ],  # Reduced forecast horizons
                "n_jobs": [-1],  # Use all available cores
            }

    def optimize_model(self, param_grid):
        """
        Perform grid search to optimize model parameters.

        Uses cross-validation to find the best parameters for the selected model.
        Splits the data into training and validation sets, performs grid search,
        and displays the best parameters found.

        Args:
            param_grid (dict): Parameter grid to search

        Returns:
            object: Optimized model instance with best parameters
        """
        # Define training period
        year = st.session_state["year"]
        split_point = pd.to_datetime(f"{year}-11-01")
        series = self.timeseries.drop_after(split_point)

        # Define validation period
        split_point = pd.to_datetime(f"{year}-10-31")
        val_series = self.timeseries.drop_before(split_point)

        # Configure grid search parameters
        args = {
            "parameters": param_grid,
            "series": series,
            "val_series": val_series,
            "n_jobs": -1,
            "metric": darts.metrics.mae,
            "show_warnings": False,
        }

        # Perform grid search for selected model
        forecast_model = st.session_state["forecast_model"]
        if forecast_model == "Linear Regression":
            gridsearch = LinearRegressionModel.gridsearch(**args)
        elif forecast_model == "Random Forest":
            gridsearch = RandomForest.gridsearch(**args)

        best_model = gridsearch[0]
        best_params = gridsearch[1]

        # Display best parameters in Streamlit UI
        with st.popover("Best parameters"):
            st.write(best_params)

        return best_model

    def plot(self):
        """
        Create a line chart of the forecasted values.

        Displays a Streamlit line chart showing the predicted future values.
        Handles any missing values by filling them with zeros.
        """
        predicted_df = self.predicted_series.pd_dataframe()
        predicted_df = predicted_df.rename(columns={"Value": "Predicted"})
        predicted_df.fillna(0, inplace=True)
        st.line_chart(predicted_df)
