import sqlite3
import pandas as pd
import os
import datetime
import time
import pandas_datareader.data as web

class stock_data:    
    def __init__(self, database, stck, start):
        """Access stock data through the Yahoo API and store them in an SQLite local database.
        Example:
        >>> import lib.data as data
        >>> stocks = data.stock_data(database = 'a_database.db', stck = list_of_stocks, start = a_start_date)
        >>> stocks.stocks(today = True)"""
        
        self.database = database
        self.stck = stck
        self.start = start 
    
    def stocks(self, today = True, year = "", month = "", day = ""):
        """Get stock data from Yahoo and add them into an SQLite database.
        
        If `today = True`, the stocks data will start from the given date taken from the initialization of the class and end in today's date.
        
        Otherwise, an exact date will need to be given through the `year`, `month` and `day` parameters"""""  
        
        if today == True:
            end_time = datetime.datetime.now().date().isoformat()   # today
        elif today == False and year != "" and month != "" and day != "":
            end_time = datetime.datetime(year, month, day)   # Choose end date
        else:
            print("Error: Please insert a specific date or today = True if you want today's date")
            exit()
        
        if os.path.isfile(self.database):
                db = True
        else:
                db = False
        
        engine = sqlite3.connect(self.database)
        cur = engine.cursor()
        
        print('Connecting to Yahoo Finance...')

        for i in self.stck:
            connected = False
            while not connected:    # Check connection to Yahoo finance.
                try:
                    df = web.get_data_yahoo(i, start = self.start, end = end_time)
                    connected = True
                    print('Fetching %s stock data...' %i)
                except Exception as e:
                    print("type error: " + str(e))
                    time.sleep(5)
                    pass    
            
            print('Adding %s data to %s database...' %(i, self.database))                
             
            df.rename(columns = {"Adj Close": "Adj_Close"}, inplace = True) # Replace white space with _ in column names.
   
            df = df.reset_index()   # Numerical integer index instead of date index.
            #print(df)
            tables = ('%s' %i)
            df.to_sql(tables, con = engine, if_exists='replace', index = True)
            print('%s stock data saved!' %i)

        # close db session.
        cur.close()
        engine.close()
        
        if db == True:
            result = print('Stocks Database has been successfully updated!')
        elif db == False:
            result = print('Stocks Database has been successfully generated!')
        
        return result
     
#todo: add class/function for crypto.

def SQLite_Query(db, table):
    """Function to access an SQLite database and read an entire table. Returns the table into a pandas dataframe."""
    con = sqlite3.connect(db)   # Read SQLite table into dataframe.
    df = pd.read_sql_query("SELECT * from %s" %table, con)
    con.close()
    
    return df