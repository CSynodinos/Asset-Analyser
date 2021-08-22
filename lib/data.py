import sqlite3
import pandas as pd
import os
import datetime
import time
import yfinance as yf

class data:
    start: int
        
    def __init__(self, start):
        """Access data through the Yahoo API and store them in an SQLite local database.
        Example:
        >>> import lib.data as data
        >>> stocks = data.stock_data(start = a_start_date)
        >>> stocks.stocks(database = 'a_database.db', stck = list_of_stocks, today = True)"""
        
        self.start = start 
    
    def stocks(self, database, stck, today = True, year = "", month = "", day = ""):
        """Get stock data from Yahoo and add them into an SQLite database.
                
        `database` is the SQLite database that the data will be saved at.
        
        `stck` can either be a list or a string of cryptocurrencies.
        
        If `today = True`, the stocks data will start from the given date taken from the initialization of the class, and end in today's date.
        
        Otherwise, an exact date will need to be given through the `year`, `month` and `day` parameters"""""  
        
        if today == True:
            end_time = datetime.datetime.now().date().isoformat()   # today
        elif today == False and year != "" and month != "" and day != "":
            end_time = datetime.datetime(year, month, day)   # Choose end date
        elif today == True and year != "" and month != "" and day != "":
            end_time = datetime.datetime(year, month, day)   # Choose end date
        else:
            print("Error: Please insert a specific date or today = True if you want today's date")
            exit()
        
        if os.path.isfile(database):
                db = True
        else:
                db = False
        
        data_fetch(db = database, type = 'stock', currency = stck, begin = self.start, stop = end_time) # get stock data
        
        if db == True:
            result = print('Stocks Database has been successfully updated!')
        elif db == False:
            result = print('Stocks Database has been successfully generated!')
        
        return result
    
    def crypto(self, database, crypt, today = True, year = "", month = "", day = ""):
        """Get cryptocurrency data from Yahoo and add them into an SQLite database.
        
        `database` is the SQLite database that the data will be saved at.
        
        `crypt` can either be a list or a string of cryptocurrencies.
        
        If `today = True`, the cryptocurrency data will start from the given date taken from the initialization of the class, and end in today's date.
        
        Otherwise, an exact date will need to be given through the `year`, `month` and `day` parameters""""" 
        
        if today == True:
            final = datetime.datetime.now().date().isoformat()   # today
        elif today == False and year != "" and month != "" and day != "":
            final = datetime.datetime(year, month, day)   # Choose end date
        elif today == True and year != "" and month != "" and day != "":
            final = datetime.datetime(year, month, day)
        else:
            print("Error: Please insert a specific date or today = True if you want today's date")
            exit()
        
        data_fetch(db = database, type = 'cryptocurrency', currency = crypt, begin = self.start, stop = final) # get crypto data
        
        if os.path.isfile(database):
                db = True
        else:
                db = False

        if db == True:
            result = print('Cryptocurrency Database has been successfully updated!')
        elif db == False:
            result = print('Cryptocurrency Database has been successfully generated!')
        
        return result    

def SQLite_Query(database, table):
    """Function to access an SQLite database and read an entire table. Returns the table into a pandas dataframe."""
    
    con = sqlite3.connect(database)   # Read SQLite table into dataframe.
    df = pd.read_sql_query("SELECT * from %s" %table, con)
    con.close()
    
    return df

def data_fetch(db, type, currency, begin, stop):
    """Method that gets data from Yahoo.
    
    `db` is the name of the database that the data will be added.
    
    `type` is the type of data e.g. stock.
    
    `currency` can either be a list or string of the data for download from Yahoo e.g. AAPL
    
    `begin` is the start date for the data and `stop` is the end date."""
    
    engine = sqlite3.connect(db)
    cur = engine.cursor()
        
    print('Connecting to Yahoo Finance...')
    
    for i in currency:
            connected = False
            while not connected:    # Check connection to Yahoo finance.
                try:
                    print('Fetching %s %s data...' %(i, type))
                    df = yf.download(tickers = i, start = begin, end = stop)
                    connected = True
                except Exception as e:
                    print("type error: " + str(e))
                    time.sleep(30)
                    pass    
            
            print('Adding %s data to %s database...' %(i, db))                
             
            df.rename(columns = {"Adj Close": "Adj_Close"}, inplace = True) # Replace white space with _ in column names.
   
            df = df.reset_index()   # Numerical integer index instead of date index.
            tables = ('%s' %i)
            df.to_sql(tables, con = engine, if_exists='replace', index = True)
            print('%s %s data saved!\n' %(i, type))

    # close db session.
    cur.close()
    engine.close()