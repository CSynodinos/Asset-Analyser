import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM

def preprocessing(data, prediction_days):
    """Preprocess the training data.
    
    `data` is the dataframe holding the data.
    
    `prediction_days` are the number of days that the prediction will be based on."""
    
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
    
    `inputs` is the dataset being tested."""
    
    x_test = []
    
    for i in range(prediction_days, len(inputs)):
        x_test.append(inputs[i-prediction_days:i, 0])
    
    x_test = np.array(x_test)
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
    
    return x_test

def CNN_model(x, y, units, closing_value, optimize, loss_function, epoch, batch):
    """Build and train a Convolutional Neural Network (CNN) using the Keras Sequential API.
    
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

def plot_data(name, type, actual, predicted, colour_actual, colour_predicted,):
    """Plot two arrays. `actual` and `predicted` are the two arrays being plotted.
    
    `name` and `type` are the name of the data and type of data, respectively.
    
    `colour_actual` and `colour_predicted` are the colours for `actual` and `predicted` lines in the plot, respectively."""
    
    plt.plot(actual, color = colour_actual, label = '%s Actual Price' %name)
    plt.plot(predicted, color = colour_predicted, label = '%s Predicted Price' %name)
    plt.title('%s %s Price' %(name, type))
    plt.xlabel('Time')
    plt.ylabel('%s %s Price' %(name, type))
    plt.legend()
    plt.show()

def plot_volatility(dataframe, str_vol, name):
    """Plot the volatility histogram.
    
    `dataframe` is the dataframe to be plotted.
    
    `str_vol` is the string of the volatility result.
    
    `name` is the name of the stock/cryptocurrency."""
    
    fig, ax = plt.subplots()    # fig is placeholder, ax is used to set axis on graph.
    dataframe.hist(ax=ax, bins=50, alpha=0.6, color="blue")
    ax.set_xlabel("Log Volatility")
    ax.set_ylabel("Volatility Frequency(%)")
    ax.set_title("%s Volatility Plot" %name)
    

def next_day_prediction(input, name, type, prediction_days, model, scaler, today = True, year = "", month = "", day = ""):
    """Predict the closing value that the array will have on the next day.
    
    `input` is the input array. `prediction_days` are the number of days used for the prediction.
    
    `name` and `type` are the name of the data and type of data, respectively.
    
    `model` is the model used for the prediction.
    
    `scaler` is the scaler for the array.
    
    `today` = True by default. If today = True and `year`, `month`, `day` are empty, the next day will be the day after today,
    otherwise, it will be the day specified by the `year`, `month` and `day` parameters."""
    
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