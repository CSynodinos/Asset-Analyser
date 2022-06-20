#!/usr/bin/env python3
from __future__ import annotations

from sklearn.preprocessing import MinMaxScaler
from dataclasses import dataclass
from lib.model_methods import RNN_model, test_preprocessing, plot_data, next_day_prediction, plot_volatility
from inspect import getfullargspec
import yfinance as yf
import datetime as dt
import pandas as pd
import numpy as np

class financial_assets:
    """Financial asset class for price predictions.
    """

    def __init__(self, pred_days: int, asset_type: str) -> None:
        self.pred_days = pred_days
        self.asset_type = asset_type

    @classmethod
    def __repr__(cls) -> str:
        params = getfullargspec(__class__).args
        params.remove("self")
        return params

    @classmethod
    def __dir__(cls, only_added = False) -> list:
        """Display function attributes.
        Args:
            * `only_added` (bool, optional): Choose whether to display only the specified attributes. Defaults to False.
        Returns:
            list: List of attributes.
        """

        all_att = list(cls.__dict__.keys())
        if not only_added:
            return all_att
        else:
            default_atts = ['__module__', '__doc__', '__dict__', '__weakref__']
            all_att = [x for x in all_att if x not in default_atts]
            return all_att

    @staticmethod
    def df_act_pred(real:np.ndarray, pred:np.ndarray, d:list) -> pd.DataFrame:
        real = np.ndarray.tolist(real)
        pred = np.ndarray.tolist(pred)
        pred = [val for vals in pred for val in vals]   # Flatten pred list of lists.
        cols = ['Dates', 'Real_Values', 'Predicted_Values']
        return pd.DataFrame({cols[0]: d, cols[1]: real, cols[2]: pred})

    def predictor(self, x, x_train: np.ndarray, y_train: np.ndarray, asset_scaler: MinMaxScaler,
                tick: str, query_asset: pd.DataFrame) -> tuple[float, str]:

        """Financial asset predictor.

        Args:
            * `x_train` (np.ndarray): Numpy array with x axis training set.
            * `y_train` (np.ndarray): Numpy array with y axis training set.
            * `asset_scaler` (MinMaxScaler): Feature scaler array containing numbers scaled to dataset range.
            * `tick` (str): Asset name to download data for.
            * `query_asset` (pd.DataFrame): Asset pandas dataframe.

        Returns:
            
        """

        # Training starts.
        print('Training the model...')
        asset_model = RNN_model(x_train, y_train, 50, 1, 'adam', 'mean_squared_error', 25, 32)

        # Test data.
        test_start = dt.datetime(2019, 11, 1)
        test_end = dt.datetime.now().date().isoformat()   # Today.
        test_data = yf.download(tickers = tick, start = test_start, end = test_end) # Get test data from Yahoo.
        actual_prices = test_data['Close'].values   # Get closing prices.

        asset_dataset = pd.concat((query_asset['Close'], test_data['Close']), axis = 0)
        model_inputs = asset_dataset[len(asset_dataset) - len(test_data) - self.pred_days:].values
        model_inputs = model_inputs.reshape(-1, 1)
        model_inputs = asset_scaler.transform(model_inputs) # Data scaled according to the scaler.

        # Make predictions on test data.
        x_test = test_preprocessing(self.pred_days, model_inputs)
        pred_prices = asset_model.predict(x_test, verbose = 0)
        pred_prices = asset_scaler.inverse_transform(pred_prices)

        # Plot Results
        dates = plot_data(x_values = x, name = tick, dtype = self.asset_type, 
                                actual = actual_prices, predicted = pred_prices, 
                                colour_actual = "blue", colour_predicted = "red")

        all_data = self.df_act_pred(real = actual_prices, pred = pred_prices, d = dates)

        # Predict next day
        next_day = next_day_prediction(input = model_inputs, name = tick, 
                                        type = self.asset_type, prediction_days = self.pred_days, 
                                        model = asset_model, scaler = asset_scaler)

        # Volatility
        asset_copy = query_asset.copy()   # Copy of dataframe to add a new column for volatility.

        # Creates a column called 'Log returns' with the daily log return of the Close price.
        asset_copy['Log returns'] = np.log(query_asset['Close']/query_asset['Close'].shift())
        volatility = asset_copy['Log returns'].std() * 252 **.5   # 255 is the trading days per annum. **.5 is square root.
        percentage_vol = lambda x : round(x, 4) * 100 
        volat = str(percentage_vol(volatility))
        plot_volatility(asset_copy['Log returns'], name = tick)
        print(f'{tick} {self.asset_type} Volatility = {volat}%%')

        return all_data, next_day[0][0], volat

## Idea: Create or append a database with two columns: date and next day price pred. 
## Then, make another method that will get the current price and match it to a database date.
## Then make another table in the database that will have: predicted price column, actual price
## column. Extract that as a dataframe and make a line graph with x = date, y = price, and each line
## with actual vs predicted. From that also get the average percent difference between each value in 
## the columns.

@dataclass
class prediction_comparison:
    df: pd.DataFrame

    def prediction_tracking(self):
        pass