#!/usr/bin/env python3
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

import seaborn as sns
import sklearn
sns.set()   # Set seaborn graphs as default.

import logging
logging.getLogger('tensorflow').disabled = True     # Disable Tensorflow warning messages.

from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
import pandas as pd
from keras.layers import Dense, Dropout, LSTM

def preprocessing(data: pd.DataFrame, prediction_days: int) -> tuple[np.ndarray, np.ndarray, MinMaxScaler]:
    """Data preprocessing for training the model.

    Args:
        * `data` (pd.Dataframe): Dataframe containing the data to train on.
        * `prediction_days` (int): Number of days to predict the data for training.

    Returns:
        tuple[np.ndarray, np.ndarray, MinMaxScaler]: x and y axis training data and the scaler.
    """

    scaler = MinMaxScaler(feature_range = (0, 1))
    scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))

    x_train = []
    y_train = []

    for i in range(prediction_days, len(scaled_data)):  # Loop over data according to the prediction days integer.
        x_train.append(scaled_data[i - prediction_days:i, 0])
        y_train.append(scaled_data[i, 0])

    x_train, y_train = np.array(x_train), np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

    return x_train, y_train, scaler

def test_preprocessing(prediction_days, inputs):
    """Preprocess the test data.

    `prediction_days` are the number of days that the prediction will be based on.

    `inputs` is the dataset being tested.

    Returns `x_test`"""

    x_test = []

    for i in range(prediction_days, len(inputs)):
        x_test.append(inputs[i-prediction_days:i, 0])

    x_test = np.array(x_test)
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

    return x_test

def RNN_model(x, y, units, closing_value, optimize, loss_function, epoch, batch):
    """Build and train a Long Short-Term Memory Reccurent Neural Network (LSTM-RNN) using the Keras Sequential API.
    
    `x` and `y` are the training sets respectively.
    
    `units` is the dimensionality of the output space.
    
    `closing_value` is the number of prediction days i.e. if it is equal to 1 then just the next day will be predicted.
    
    `optimize` is the optimization algorithm.
    
    `loss_function` is the loss function of the NN which is used to calculate the prediction error.
    
    `epoch` is the number of epochs that the model will be trained for.
    
    `batch` is the batch_size of the model."""
    
    model = Sequential()
    model.add(LSTM(units = units, return_sequences = True, input_shape = (x.shape[1], 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units = units, return_sequences = True))
    model.add(Dropout(0.2))
    model.add(LSTM(units = units))
    model.add(Dropout(0.2))
    model.add(Dense(units = closing_value)) # Predict a closing value. 1 is the next closing value.
    model.compile(optimizer = optimize, loss = loss_function)
    model.fit(x, y, epochs = epoch, batch_size = batch, verbose = 0)

    return model

def plot_data(x_values: list, name: str, dtype: str, actual:np.ndarray,
            predicted: np.ndarray, colour_actual: str, colour_predicted: str) -> list:

    """Line plot real and predicted financial market data.

    x axis is the dates of each price, y axis is the price of the financial asset.

    Plots 2 lines, one for the real data and one for the predicted data at each date of
    real data.

    Args:
        * `x_values` (list): List of dates.
        * `name` (str): Name of financial asset.
        * `dtype` (str): type of financial asset (Crypto or Stock).
        * `actual` (np.ndarray): Array of real market values.
        * `predicted` (np.ndarray): Array of predicted market values from model training.
        * `colour_actual` (str): Line colour of real market values.
        * `colour_predicted` (str): Line colour of predicted market values.

    Returns:
        `list`: List of dates without times.
    """

    x_values_year = []
    for i in x_values:  # get year, month, day for each x.
        date = dt.datetime.strptime(i, "%Y-%m-%d %H:%M:%S")
        date = str(date).split(' ',1)[0]
        x_values_year.append(date)

    plt.plot(x_values_year, actual, color = colour_actual, label = '%s Actual Price' %name)
    plt.plot(x_values_year, predicted, color = colour_predicted, label = '%s Predicted Price' %name)
    plt.title('%s %s Price' %(name, dtype))
    plt.xlabel('Date')

    x_range = list(range(0, len(x_values_year)))
    plt.xticks(np.arange(0, len(x_range) + 1, 300)) # show an x value every 300 intervals.
    plt.ylabel('%s %s Price' %(name, dtype))
    plt.legend()
    plt.show()

    return x_values_year

def plot_volatility(dataframe: pd.DataFrame, name: str) -> bool:
    """Plot the volatility histogram.

    Args:
        `dataframe` (pd.Dataframe): Dataframe to plot.
        `name` (str): Name of financial asset.

    Returns:
        Boolean: True when operation finishes successfully.
    """

    fig, ax = plt.subplots()    # fig is placeholder, ax is used to set axis on graph.
    dataframe.hist(ax = ax, bins = 50, alpha = 0.6, color = "blue")
    ax.set_xlabel("Log Volatility")
    ax.set_ylabel("Volatility Frequency(%)")
    ax.set_title("%s Volatility Plot" %name)

    return True

def next_day_prediction(input: np.ndarray, name: str, type: str, prediction_days: int, model: Sequential, 
                        scaler: MinMaxScaler, today = True, year = "", month = "", day = "") -> float:
    """Predict the closing value that the array will have on the next day.

    Args:
        * `input` (np.ndarray): Numpy array with all the data to analyse.
        * `name` (str): Name of financial asset.
        * `type` (str): Type of financial asset.
        * `prediction_days` (int): Days to use for prediction.
        * `model` (Sequential): Linear model layer stack.
        * `scaler` (MinMaxScaler): Model scaler.
        * `today` (bool, optional): Today's date. Defaults to True.
        * `year` (str, optional): Year. Defaults to "".
        * `month` (str, optional): Month. Defaults to "".
        * `day` (str, optional): Day. Defaults to "".

    Returns:
        float: Prediction of the price of the financial asset on the next day after the specified date.
    """

    next_day = [input[len(input) + 1 - prediction_days:len(input + 1), 0]]  # Calculate the next day.
    next_day = np.array(next_day, dtype=object) # Hold result in an array.
    next_day = np.reshape(next_day, (next_day.shape[0], next_day.shape[1], 1))  # Reshape array into a single column.
    next_day = np.asarray(next_day).astype(np.float)
    prediction = model.predict(next_day)
    prediction = scaler.inverse_transform(prediction)

    # Print the result and the prediction date.
    tomorrow = dt.date.today() + dt.timedelta(days=1)   # Today.
    if today == True:
        print("%s %s Adj.Close price prediction for %s: $%f" %(name, type, tomorrow, prediction))
    elif today == False and year != "" and month != "" and day != "":
        print("%s %s Adj.Close price prediction (%d/%d/%d): $%f" %(name, type, day, month, year, prediction))
    elif today == True and year != "" and month != "" and day != "":
        print("%s %s Adj.Close price prediction (%d/%d/%d): $%f" %(name, type, day, month, year, prediction))
    else:
        print("%s %s Adj.Close price prediction: $%f" %(name, type, prediction))

    return prediction
