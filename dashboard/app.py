from __future__ import annotations

from typing import Any, Final
from lib.fin_asset import prediction_comparison
import dash
from dash import dcc, html
import pandas as pd
import webbrowser
from threading import Timer
from dashboard.plots.lines import line_plotter

##http://localhost:8050

TREND_DESCRIPTIONS: Final[dict] = { 'upward': 'an upwards trend',
                                    'downward': 'a downwards trend',
                                    'none': 'no change'}

def get_first_key_value(dictionary: dict) -> tuple[str, str]:
    """Get the first key value pair in a dictionary.

    Args:
        * `dictionary` (dict): Input dictionary.

    Raises:
        `IndexError`: When dictionary is empty or corrupt.

    Returns:
        `tuple[str, str]`: Key, Value pair.
    """
    for key, value in dictionary.items():
        return key, value
    raise IndexError('Dictionary is empty. Check database for the absence of the specified last date entry.')

def __compare_prices(df: pd.DataFrame, value_pre: str, next_day_price: str):
    """Compare two asset prices to find the trend.

    Args:
        * `df` (pd.DataFrame): Dataframe to pull the data from.
        * `value_pre` (str): Actual price of asset on a specific day.
        * `next_day_price` (str): Predicted price of the asset for the next day.

    Returns:
        `str`: Description of results as text.
    """

    # Convert the strings to floats for comparison.
    df_value_pre = float(df.loc[df['Date'] == value_pre, 'Predicted_Values'].iloc[0])   # Predicted_Values will need to change on a db merge.
    next_day_price = float(next_day_price)
    previous_date = prediction_comparison(value = df_value_pre) 
    next_day = prediction_comparison(value = next_day_price)
    percent_diff = str((abs(next_day_price - df_value_pre) / df_value_pre) * 100.0)
    difference: float | int = previous_date == next_day
    if difference > 0:
        return {TREND_DESCRIPTIONS["downward"]: percent_diff}, df_value_pre
    elif difference < 0:
        return {TREND_DESCRIPTIONS["downward"]: percent_diff}, df_value_pre
    elif difference == 0:
        return {TREND_DESCRIPTIONS["none"]: percent_diff}, df_value_pre

y_dict = {'Adj_Close': 'Actual_Values',
        'Predicted_Values': 'Predicted_Values'}

def __dashboard_create(df: pd.DataFrame, asset: str, asset_type: str, next_day: int | float,
                    volatility: str, currency: str, model_name: str) -> dash.Dash:

    """Create a one graph dashboard using dash.

    Args:
        * `df` (pd.DataFrame): DataFrame with the dashboard data.
        * `asset` (str): Asset name.
        * `asset_type` (str): Type of asset.
        * `next_day` (int | float): Next day prediction value.
        * `volatility` (str): Volatility percentage value.

    Returns:
        Dash: Instance of the dash web application.
    """

    specified_date = df['Date'].iloc[-1]
    COMPARISON_INSTANCE = __compare_prices(df = df, value_pre = specified_date, next_day_price = next_day)
    trend_diff = get_first_key_value(COMPARISON_INSTANCE[0])
    TREND, diff = trend_diff[0], trend_diff[1]
    diff = abs(float(diff))
    if TREND == TREND_DESCRIPTIONS["upward"]:
        DIFFERENCE = f'+{diff}'
    elif TREND == TREND_DESCRIPTIONS["downward"]:
        DIFFERENCE = f'-{diff}'
    elif TREND == TREND_DESCRIPTIONS["none"]:
        DIFFERENCE = '0'
    TODAYS_VAL = COMPARISON_INSTANCE[1]
    external_stylesheets = [
        {
            "href": "https://fonts.googleapis.com/css2?"
                    "family=Lato:wght@400;700&display=swap",
            "rel": "stylesheet",
        },
    ]
    app = dash.Dash(__name__, external_stylesheets = external_stylesheets)
    app.title = "Market Analysis using ML!!!"
    app.layout = html.Div(
        children = [
            html.Div(
                children = [
                    html.P(children = "📈", className = "header-emoji"),
                    html.H1(
                        children = f"{asset} Analytics", className = "header-title"
                    ),
                    html.Span(children = dcc.Markdown(f"Analyze {asset_type} prices using a **{model_name}**. "
                            f"Predict the price of the {asset_type} for the next day from the specified date ({specified_date}).",
                            className = "header-description")
                    ),
                    html.P(
                        children = f"Made by Christos Synodinos",
                        className = "header-author",
                    ),
                ],
                className = "header",
            ),
            html.Div(
                children = [
                    html.Div(
                        children = dcc.Graph(
                            id = "price-chart",
                            config = {'displayModeBar': True,
                                    'scrollZoom': True,
                                    'modeBarButtonsToAdd':['drawline',
                                        'drawopenpath',
                                        'drawclosedpath',
                                        'drawcircle',
                                        'drawrect',
                                        'eraseshape']
                                    },
                            figure = {
                                "data": line_plotter(df = df, x_name = 'Date', all_y = y_dict).plot_generator(),
                                "layout": {
                                    "title": {
                                        "text": f"{asset} {asset_type} Price Prediction",
                                        "x": 0.35,
                                        "xanchor": "left",
                                    },
                                    "xaxis": {"fixedrange": True},
                                    "yaxis": {
                                        "tickprefix": "$",
                                        "fixedrange": True,
                                    },
                                    'plot_bgcolor': '#111111',
                                    'paper_bgcolor': '#111111',
                                    'font': {
                                        'color': '#FFFFFF'}
                                },
                            },
                        ),
                        className = "card",
                    ),
                ],
                className="wrapper",
            ),
        html.Div(
        children = [
            html.Div(
                children = [
                    html.Span(
                        children = dcc.Markdown("_**Description**_: The prediction for the price of the " 
                                            f"asset on the next day (Previous date: {specified_date} with Adj Close of {currency}{TODAYS_VAL}) "
                                            f"is: **{currency}{next_day}**. The mean volatility of "
                                            f"the asset is **{str(round(float(volatility), 3))}**%. Comparing the price prediction with the value of the asset "
                                            f"on the previous day, **{TREND}** " 
                                            f"can be observed between the two days, with a percent difference of **{DIFFERENCE}%**.",
                                            className = "legend-title")
                    ),
                    html.Span(
                        className = "legend-description",
                    ),
                ],
                className = "Legend",
                ),
            ])
        ]
    )

    return app

def dashboard_launch(df: pd.DataFrame, fin_asset: str, asset_type: str, 
                nxt_day: float | int, volatility: str, asset_currency: str,
                port: int, model: str) -> Any:

    """Launch a dash dashboard.

    Args:
        * `df` (pd.Dataframe): Dataframe with all data.
        * `fin_asset` (str): Name of asset.
        * `asset_type` (str): Type of asset e.g. crypto, stock.
        * `nxt_day` (float | int): Next day price prediction.
        * `volatility` (str): Volatility of asset.
        * `port` (int, optional): Port for server.

    Returns:
        Launches an instance of the app.
    """

    app = __dashboard_create(df = df, asset = fin_asset, asset_type = asset_type, next_day = nxt_day,
                        volatility = volatility, currency = asset_currency, model_name = model)
    Timer(1, webbrowser.open_new, args = (f"http://localhost:{port}",)).start()
    return app.run(port = port, debug = False)