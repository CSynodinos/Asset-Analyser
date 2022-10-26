#!/usr/bin/env python3
from __future__ import annotations

from sklearn.preprocessing import MinMaxScaler
from dataclasses import dataclass
from lib.model_methods import models, test_preprocessing, plot_data, next_day_prediction, plot_volatility
import yfinance as yf
import datetime as dt
import pandas as pd
import numpy as np
from lib.utils import dunders
from itertools import cycle
from threading import Thread
from time import sleep
import sys

class financial_assets(dunders):
    """Financial asset class for price predictions.
    """

    def __init__(self, pred_days: int, asset_type: str, plot: bool) -> None:
        self.pred_days = pred_days
        self.asset_type = asset_type
        self.plot = plot
        super().__init__()

    @staticmethod
    def df_act_pred(real:np.ndarray, pred:np.ndarray, d:list) -> pd.DataFrame:
        """Convert multiple Numpy arrays into 1 Dataframe.

        Args:
            * `real` (np.ndarray): Array with actual closing values of financial asset.
            * `pred` (np.ndarray): Array with predicted closing values of financial asset.
            * `d` (list): List of dates.

        Returns:
            `pd.DataFrame`: The 3 column DataFrame.
        """

        real = np.ndarray.tolist(real)
        pred = np.ndarray.tolist(pred)
        pred = [val for vals in pred for val in vals]   # Flatten pred list of lists.
        cols = ['Dates', 'Real_Values', 'Predicted_Values']
        return pd.DataFrame({cols[0]: d, cols[1]: real, cols[2]: pred})

    def predictor(self, model: str, x: list, x_train: np.ndarray, y_train: np.ndarray,
                asset_scaler: MinMaxScaler, tick: str, query_asset: pd.DataFrame, 
                asset_currency_symbol: str, drop: float, optimizer: str,
                loss: str, epoch: int, batch: int, dimensionality: int, 
                closing: int, any_p: bool = False,
                volat_p: bool = False) -> tuple[pd.DataFrame, float, str]:

        """Financial asset predictor.

        Args:
            * `x` (list): List of values for the x-axis.
            * `x_train` (np.ndarray): Numpy array with x axis training set.
            * `y_train` (np.ndarray): Numpy array with y axis training set.
            * `asset_scaler` (MinMaxScaler): Feature scaler array containing numbers scaled to dataset range.
            * `tick` (str): Asset name to download data for.
            * `query_asset` (pd.DataFrame): Asset pandas dataframe.
            * `asset_currency_symbol` (str): Currency symbol of asset.
            * `volat_p` (bool, default = False): Plot the volatility log graph.
            * `drop` (int | float): Model Dropout. Default is 0.2.

        Returns:
        `tuple[pd.DataFrame, float, str]`: All data output DataFrame, the prediction for the 
        next day, the mean percentage volatility as a string.
        """

        training_complete = False

        def _training_tracking(message: str) -> None:
            """Track model training progress and print a progress 
            animation to the terminal.

            Args:
                * `message` (str): Training tracking message.
            """

            for c in cycle(['|', '/', '-', '\\']):
                if training_complete:
                    break
                sys.stdout.write(f'\r{message} ' + c + " ")
                sys.stdout.flush()
                sleep(0.1)

            LINE_UP = '\033[1A'
            LINE_CLEAR = '\x1b[2K'
            print(LINE_CLEAR)
            print(LINE_UP, end = LINE_CLEAR)
            sys.stdout.write('\rTraining Complete!     ')

        # Training starts.
        training_message = 'Training the LSTM-RNN model'
        training_track_thread = Thread(target = _training_tracking, kwargs = {'message':training_message})
        training_track_thread.start()

        models_instance = models(dropout = drop, loss_function = loss, epoch = epoch, batch = batch)

        if model == 'RNN':
            asset_model = models_instance.LSTM_RNN(x = x_train, y = y_train, units = dimensionality, closing_value = closing,
                                    optimize = optimizer)

        sleep(0.1)
        training_complete = True

        # Test data.
        test_start = dt.datetime(2019, 11, 1)
        test_end = dt.datetime.now().date().isoformat()   # Today.
        test_data: pd.DataFrame = yf.download(tickers = tick, start = test_start,
                                            end = test_end) # Get test data from Yahoo.

        actual_prices = test_data['Close'].values   # Get closing prices.
        asset_dataset = pd.concat((query_asset['Close'], test_data['Close']), axis = 0)
        model_inputs = asset_dataset[len(asset_dataset) - len(test_data) - self.pred_days:].values
        model_inputs = model_inputs.reshape(-1, 1)
        model_inputs: np.ndarray = asset_scaler.transform(model_inputs) # Data scaled according to the scaler.

        # Make predictions on test data.
        x_test = test_preprocessing(self.pred_days, model_inputs)
        pred_prices: np.ndarray = asset_model.predict(x_test, verbose = 0)
        pred_prices: np.ndarray = asset_scaler.inverse_transform(pred_prices)
        dates = plot_data(x_values = x, name = tick, dtype = self.asset_type, 
                                actual = actual_prices, predicted = pred_prices, 
                                colour_actual = "blue", colour_predicted = "red", plot = self.plot)

        all_data = self.df_act_pred(real = actual_prices, pred = pred_prices, d = dates)

        # Predict next day
        next_day = next_day_prediction(input = model_inputs, name = tick, 
                                        type = self.asset_type, prediction_days = self.pred_days,
                                        currency = asset_currency_symbol, model = asset_model, 
                                        scaler = asset_scaler)

        # Volatility
        asset_copy = query_asset.copy()   # Copy of dataframe to add a new column for volatility.

        # Creates a column called 'Log returns' with the daily log return of the Close price.
        asset_copy['Log returns'] = np.log(query_asset['Close']/query_asset['Close'].shift())
        volatility: int | float = asset_copy['Log returns'].std() * 252 **.5   # 255 is the trading days per annum. **.5 is square root.
        percentage_vol: int | float = lambda x : round(x, 4) * 100 
        volat = str(percentage_vol(volatility))
        if volat_p:
            plot_volatility(asset_copy['Log returns'], name = tick)
        print(f'{tick} {self.asset_type} Volatility = {volat}%')

        return all_data, next_day[0][0], volat

def prediction_assessment(df_all: pd.DataFrame, df_pred_real: pd.DataFrame, db: str, asset: str, model_name: str) -> pd.DataFrame:
    """Wrapper for table_parser().

    Args:
        * `df_all` (pd.DataFrame): Dataframe input with all data.
        * `df_pred_real` (pd.DataFrame): Dataframe with real and predicted values.
        * `db` (str): Database for table_parser().
        * `asset` (str): Asset name.

    Returns:
        `pd.DataFrame`: Queries the updated table in the database and get all values as a pandas DataFrame.
    """

    from lib.df_utils import df_analyses
    from lib.db_utils import table_utils, SQLite_Query

    all_data_df = df_analyses(df = df_pred_real).assessment_df_parser()
    all_data_df = all_data_df.drop(all_data_df.columns[[0, 1]], axis = 1)
    merged_df = df_all.join(all_data_df)    # Combines original df with prediction operations df.

    if "-" in asset:
        asset = asset.replace('-', "_")
    if " " in asset:
        asset = asset.replace(' ', "")

    new_table_name = f'{asset}_{model_name}'
    table_instance = table_utils(dbname = db, asset_n = new_table_name)
    table_instance.table_parser(df = merged_df)
    return SQLite_Query(database = db, table = new_table_name)[0]

@dataclass
class prediction_comparison:
    """Dataclass to compare next day prediction with actual closing value of
    the asset on that day.

    Returns:
        __eq__() internal returns the resulting difference as float.
    """

    value: float | int

    def __post_init__(self):
        # get type of class variable as string.
        val_type = str(list(__class__.__annotations__.values())[0]).replace(" ", "")
        if not (val_type == 'float' or val_type == 'int' or val_type == 'float|int'):
            raise TypeError("Class variable can only be of type float and int.")

        # Ensure the input value is always of the same type as the specified class variable type.
        if isinstance(self.value, float) and val_type == "int":
            self.value = int(self.value)
        elif isinstance(self.value, int) and val_type == "float":
            self.value = float(self.value)
        elif isinstance(self.value, int) and val_type == 'float|int':
            self.value = float(self.value)

    def __eq__(self, __o: object) -> float:
        if isinstance(__o, __class__):
            if not self.value == __o.value:
                return float(self.value - __o.value)   # get the difference between the unequal objects.