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
            `list`: List of attributes.
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

    def predictor(self, x: list, x_train: np.ndarray, y_train: np.ndarray, asset_scaler: MinMaxScaler,
                tick: str, query_asset: pd.DataFrame, any_p: bool = False,
                volat_p: bool = False, drop = 0.2) -> tuple[pd.DataFrame, float, str]:

        """Financial asset predictor.

        Args:
            * `x` (list): List of values for the x-axis.
            * `x_train` (np.ndarray): Numpy array with x axis training set.
            * `y_train` (np.ndarray): Numpy array with y axis training set.
            * `asset_scaler` (MinMaxScaler): Feature scaler array containing numbers scaled to dataset range.
            * `tick` (str): Asset name to download data for.
            * `query_asset` (pd.DataFrame): Asset pandas dataframe.
            * `volat_p` (bool, default = False): Plot the volatility log graph.
            * `drop` (int | float): Model Dropout. Default is 0.2.

        Returns:
        `tuple[pd.DataFrame, float, str]`: All data output DataFrame, the prediction for the 
        next day and the mean percentage volatility as a string.
        """

        # Training starts.
        print('Training the model...\n')
        asset_model = RNN_model(x = x_train, y = y_train, units = 50, closing_value = 1,
                                optimize = 'adam', dropout = drop, loss_function = 'mean_squared_error', 
                                epoch = 25, batch = 32)

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
        volatility: int | float = asset_copy['Log returns'].std() * 252 **.5   # 255 is the trading days per annum. **.5 is square root.
        percentage_vol: int | float = lambda x : round(x, 4) * 100 
        volat = str(percentage_vol(volatility))
        if volat_p:
            plot_volatility(asset_copy['Log returns'], name = tick)
        print(f'{tick} {self.asset_type} Volatility = {volat}%')

        return all_data, next_day[0][0], volat

def prediction_assessment(df: pd.DataFrame, db: str, asset: str) -> bool:
    """Wrapper for table_parser().

    Args:
        * `df` (pd.DataFrame): Dataframe input for df_analyses class.
        * `db` (str): Database for table_parser().
        * `asset` (str): Asset name.

    Returns:
        bool: True when operation finishes successfully.
    """
    from lib.df_utils import df_analyses
    from lib.db_utils import table_parser

    all_data_df = df_analyses(df = df).assessment_df_parser()
    return table_parser(df = all_data_df, dbname = db, asset_n = asset)

## Will be used in the comparison script for new AI/ML models.
@dataclass
class prediction_comparison:
    """Dataclass to compare next day prediction with actual closing value of
    the asset on that day.

    Returns:
        __eq__() returns the resulting difference as float.
    """

    value: float | int

    def __post_init__(self):
        # get type of class variable as string.
        val_type = str(list(__class__.__annotations__.values())[0])
        val_type = val_type.replace("<class","").replace(">","").replace("'","").strip()
        if not (val_type == 'float' or val_type == 'int'):
            raise TypeError("Class variable can only be of type float and int.")

        # Ensure the input value is always of the same type as the specified class variable type.
        if isinstance(self.value, float) and val_type == "int":
            self.value = int(self.value)
        if isinstance(self.value, int) and val_type == "float":
            self.value = float(self.value)

    def __eq__(self, __o: object) -> float:
        if isinstance(__o, __class__):
            if not self.value == __o.value:
                return float(self.value - __o.value)   # get the difference between the unequal objects.