#!/usr/bin/env python3
from __future__ import annotations

import sqlite3, os, datetime, time
import yfinance as yf
import pandas as pd
from lib.exceptions import DateError
from inspect import getfullargspec

class data:
    """Access data through the Yahoo API and store them in an SQLite local database.
    """

    def __init__(self, start: datetime) -> None:
        self.start = start 

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
    def __data_fetch(db: str, type: str, currency: list, begin: str, stop: str) -> bool:
        """Get data from Yahoo.

        Args:
            * `db` (str): Database name used for storage.
            * `type` (str): Asset type e.g. stock.
            * `currency` (list): List of assets.
            * `begin` (str): Start date for data fetching.
            * `stop` (str): End date for data fetching.

        Returns:
            `boolean`: True when operation finishes successfully.
        """

        engine = sqlite3.connect(db)
        cur = engine.cursor()
        print('Connecting to Yahoo Finance...\n')
        for i in currency:
            connected = False
            while not connected:    # Check connection to Yahoo finance.
                try:
                    print(f'Fetching {i} {type} data...\n')
                    df: pd.DataFrame = yf.download(tickers = i, start = begin, end = stop)
                    connected = True
                except Exception as e:
                    print("type error: " + str(e))
                    time.sleep(30)

                print(f'Adding {i} data to {db} database...\n')                

                df.rename(columns = {"Adj Close": "Adj_Close"}, inplace = True) # Replace white space with _ in column names.

                df = df.reset_index()   # Numerical integer index instead of date index.

                str_to_replace = "-"
                str_check = any(tables in str_to_replace for tables in i)

                if str_check == True:  # Checks if the "-" character exists. If yes, then it gets replaced with "_".
                    crypto_table = i.replace("-", "_")
                    df.to_sql(crypto_table, con = engine, if_exists = 'replace', index = True)
                else:
                    df.to_sql(i, con = engine, if_exists = 'replace', index = True)
                print(f'{i} {type} data saved!\n')

        cur.close()
        engine.close()

        return True

    def asset_data(self, database: str, asset_type: str, asset_list: list, today = True, 
                year = None, month = None, day = None) -> bool:
        """Get asset data and append them into an SQLite database.

        Args:
            * `database` (str): SQLite database that the data will be saved at.
            * `asset_type` (str): Asset type e.g. stock.
            * `asset_list` (list): List of assets.
            * `today` (bool): Select today's date.

        Raises:
            `DateError`: When data is incorrectly selected.

        Returns:
            `boolean`: True when operation finishes successfully.
        """

        if today == True:
            end_time = datetime.datetime.now().date().isoformat()   # today
        elif today == False and (year, month, day) != None:
            end_time = datetime.datetime(year, month, day)   # Choose end date
        elif today == True and (year, month, day) != None:
            raise DateError("today = True and year, month, day are set. Please set one of the two types of dates.")
        else:
            raise DateError("Please insert a specific date or today = True if you want today's date")

        if os.path.isfile(database):
            db = True
        else:
            db = False

        self.__data_fetch(db = database, type = asset_type, currency = asset_list,
                        begin = self.start, stop = end_time) # get stock data

        if db == True:
            print(f'{asset_type} Database has been successfully updated!\n')
        elif db == False:
            print(f'{asset_type} Database has been successfully generated!\n')

        return True
