<h1 align="center"; style='font-size:200%'>
<ins><strong>Asset Analyser</strong><ins>
</h1>

*A Python application for the analysis and prediction of market assets, including Cryptocurrencies and Stocks.*

## Developers
[CSynodinos](https://github.com/CSynodinos)

## Description
This application is able to analyse any asset data and make predictions on the price of such asset for the next day from the specified date. Predictions are made through the use of ML. Currently, the application supports only 1 model, the Long Short-Term Memory Recurrent Neural Network (LSTM-RNN). Future expansions will include more ML model options. The resulting analysis can either be displayed in a dashboard or in a jupyter notebook using matplotlib. The default behaviour is displaying the dashboard in a localhost instance, which is created using the Dash and Flask frameworks. All the data is stored in sqlite3 databases in the Databases subdirectory.

## Installation
Download the repository in your system and run installer.py
```bash
>>> curl https://raw.githubusercontent.com/CSynodinos/Asset-Analyser

For Windows:
>>> python .\lib\installer.py -env [venv or conda] # Default is venv.

For Linux/Mac:
>>> python lib/installer.py -env [venv or conda] # Default is venv
```

This version of the application supports both tensorflow and tensorflow-gpu. The installer can install tensorflow-gpu by using the -gpu flag. However, you will need to follow Nvidia's instructions for the CUDA toolkit and CUDA Deep Neural Network library installations for Windows/Linux. Otherwise, tensorflow-gpu will not work!

*Note*: To see all the options available in the application:

```bash
For Windows:
>>> python .\lib\installer.py -h

For Linux/Mac:
>>> python3 lib/installer.py -h
```

## Example
```bash
>>> asset_analysis.py -test
                                    Asset Analyser

    Connecting to Yahoo Finance...

    Fetching BTC-USD Cryptocurrency data...

    [*********************100%***********************]  1 of 1 completed
    Adding BTC-USD data to YOUR/PATH/TO/*.db database...

    BTC-USD Cryptocurrency data saved!

    Cryptocurrency Database has been successfully updated!

    Training the model...

    [*********************100%***********************]  1 of 1 completed
    1/1 [==============================] - 1s 910ms/step
    BTC-USD Cryptocurrency Adj.Close price prediction for 2022-08-23: $23380.16
    BTC-USD Cryptocurrency Volatility = 62.31%
    Dash is running on http://127.0.0.1:8050/

    WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
    * Serving Flask app 'dashboard.app'
    * Debug mode: off
    * Running on http://127.0.0.1:8050 (Press CTRL+C to quit)
    127.0.0.1 - - [22/Aug/2022 11:31:09] "GET / HTTP/1.1" 200 -
    127.0.0.1 - - [22/Aug/2022 11:31:09] "GET /assets/style.css?m=1660504342.4959888 HTTP/1.1" 200 -
    127.0.0.1 - - [22/Aug/2022 11:31:09] "GET /_dash-component-suites/dash/deps/react-dom@16.v2_5_0m1659572569.14.0.min.js HTTP/1.1" 200 -
    127.0.0.1 - - [22/Aug/2022 11:31:09] "GET /_dash-component-suites/dash/deps/prop-types@15.v2_5_0m1659572569.8.1.min.js HTTP/1.1" 200 -
    127.0.0.1 - - [22/Aug/2022 11:31:09] "GET /_dash-component-suites/dash/deps/react@16.v2_5_0m1659572569.14.0.min.js HTTP/1.1" 200 -
    127.0.0.1 - - [22/Aug/2022 11:31:09] "GET /_dash-component-suites/dash/dash-renderer/build/dash_renderer.v2_5_0m1659572568.min.js HTTP/1.1" 200 -
    127.0.0.1 - - [22/Aug/2022 11:31:09] "GET /_dash-layout HTTP/1.1" 200 -
    127.0.0.1 - - [22/Aug/2022 11:31:10] "GET /_dash-dependencies HTTP/1.1" 200 -
    127.0.0.1 - - [22/Aug/2022 11:31:10] "GET /assets/favicon.ico?m=1660494775.9404457 HTTP/1.1" 200 -
    127.0.0.1 - - [22/Aug/2022 11:31:10] "GET / HTTP/1.1" 200 -
    127.0.0.1 - - [22/Aug/2022 11:31:10] "GET /_dash-component-suites/dash/dcc/async-graph.js HTTP/1.1" 304 -
    127.0.0.1 - - [22/Aug/2022 11:31:10] "GET /assets/style.css?m=1660504342.4959888 HTTP/1.1" 304 -
    127.0.0.1 - - [22/Aug/2022 11:31:10] "GET /_dash-component-suites/dash/dcc/async-plotlyjs.js HTTP/1.1" 304 -
    127.0.0.1 - - [22/Aug/2022 11:31:10] "GET /_dash-layout HTTP/1.1" 200 -
    127.0.0.1 - - [22/Aug/2022 11:31:11] "GET /_dash-dependencies HTTP/1.1" 200 -
    127.0.0.1 - - [22/Aug/2022 11:31:11] "GET /_dash-component-suites/dash/dcc/async-markdown.js HTTP/1.1" 304 -
    127.0.0.1 - - [22/Aug/2022 11:31:11] "GET /_dash-component-suites/dash/dcc/async-graph.js HTTP/1.1" 304 -
    127.0.0.1 - - [22/Aug/2022 11:31:11] "GET /_dash-component-suites/dash/dcc/async-plotlyjs.js HTTP/1.1" 304 -
    127.0.0.1 - - [22/Aug/2022 11:31:11] "GET /_dash-component-suites/dash/dcc/async-markdown.js HTTP/1.1" 304 -
    127.0.0.1 - - [22/Aug/2022 11:31:11] "GET /_dash-component-suites/dash/dcc/async-highlight.js HTTP/1.1" 304 -
    127.0.0.1 - - [22/Aug/2022 11:31:11] "GET /_dash-component-suites/dash/dcc/async-highlight.js HTTP/1.1" 304 -
```

*Note*: To see all the options available in the application:

```bash
>>> asset_analysis.py -h
```

The resulting dashboard localhost page from running the test profile:

![My Image](assets/full_dash_test.png)

The graph itself:

![My Image](assets/test_plot.png)

## Application Features

:heavy_check_mark: Download data from **YahooFinance**.

:heavy_check_mark: **SQLite3** database integration.

:heavy_check_mark: **ML/AI** integration, only **LSTM-RNN** supported currently.

:heavy_check_mark: **Matplotlib (seaborn)** support.

:heavy_check_mark: **Dashboard** support using **Dash** and **Flask**.

## CLI options
##### *Essential*:
    1. -ast: Market Asset. Needs to be written as: Asset_initials-currency

    2. -tp: Asset Type, etc. Cryptocurrency or Stock.

    3. -pd: Prediction days used for training. Must be a positive integer.

##### *Optional*:
    1. -db: SQLite3 Database name. Defaults: asset_name_data.db

    2. -d: Start date for data calls. Format: YYYY-MM-DD. Defaults: 2019-11-1.

    3. -tdy: End date for data calls is current date. 
        If False, add custom date with -y -m -d parameters. Defaults: True.

    4. -p: Port for localhost containing the dashboard. Defaults to 8050.

    5. -plt: Display seaborn plots. Useful for jupyter notebooks. Defaults to False.

    6. -test: Runs a test profile.

    7. -end_y: Year of end date for data calls. Only use when -tdy is set to False.

    8. -end_m: Month of end date for data calls. Only use when -tdy is set to False.

    9. -end_d: Day of end date for data calls. Only use when -tdy is set to False.

# Work-In-Progress Features

:small_red_triangle: Addition of more AI/ML options. Currently working on adding a **Convoluted NN** as an option.

:small_red_triangle: Postgres4 integration.

