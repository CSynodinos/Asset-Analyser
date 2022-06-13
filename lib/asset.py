from __future__ import annotations

from sklearn.preprocessing import MinMaxScaler

from lib.model_methods import RNN_model, test_preprocessing, plot_data, next_day_prediction, plot_volatility
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

    def predictor(self, x_train: np.ndarray, y_train: np.ndarray, asset_scaler: MinMaxScaler,
                tick: str, query_asset: pd.DataFrame) -> bool:

        """Financial asset predictor.

        Args:
            * `x_train` (np.ndarray): Numpy array with x axis training set.
            * `y_train` (np.ndarray): Numpy array with y axis training set.
            * `asset_scaler` (MinMaxScaler): Feature scaler array containing numbers scaled to dataset range.
            * `tick` (str): Asset name to download data for.
            * `query_asset` (pd.DataFrame): Asset pandas dataframe.

        Returns:
            Boolean: True when operation finishes successfully.
        """

        # Training starts.
        print('Training the model...')
        asset_model = RNN_model(x_train, y_train, 50, 1, 'adam', 'mean_squared_error', 25, 32)

        # Test data.
        test_start = dt.datetime(2019, 1, 1)
        test_end = dt.datetime.now().date().isoformat()   # Today.
        test_data = yf.download(tickers = tick, start = test_start, end = test_end) # Get test data from Yahoo.
        actual_prices = test_data['Close'].values   # Get closing cryptocurrency prices.

        asset_dataset = pd.concat((query_asset['Close'], test_data['Close']), axis = 0)
        model_inputs = asset_dataset[len(asset_dataset) - len(test_data) - self.pred_days:].values
        model_inputs = model_inputs.reshape(-1, 1)
        model_inputs = asset_scaler.transform(model_inputs) # Data scaled according to the scaler.

        # Make predictions on test data.
        x_test = test_preprocessing(self.pred_days, model_inputs)
        pred_prices = asset_model.predict(x_test, verbose = 0)
        pred_prices = asset_scaler.inverse_transform(pred_prices)

        # Plot Results
        plot_data(name = tick, type = self.asset_type, 
                                actual = actual_prices, predicted = pred_prices, 
                                colour_actual = "blue", colour_predicted = "red")

        # Predict next day
        next_day_prediction(input = model_inputs, name = tick, 
                                        type = self.asset_type, prediction_days = self.pred_days, 
                                        model = asset_model, scaler = asset_scaler)

        # Volatility
        asset_copy = query_asset.copy()   # Copy of dataframe to add a new column for volatility.
        asset_copy['Log returns'] = np.log(query_asset['Close']/query_asset['Close'].shift())   # Creates a column called 'Log returns' with the daily log return of the Close price.
        returns = asset_copy['Log returns']
        volatility = returns.std() * 252 **.5   # 255 is the trading days per annum. **.5 is square root.
        percentage_vol = lambda x : round(x, 4) * 100 # Calculate volatility.  
        volat = str(percentage_vol(volatility))
        plot_volatility(asset_copy['Log returns'], name = tick)
        print(f'{tick} {self.asset_type} Volatility = {volat}')

        return True