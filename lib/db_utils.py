#!/usr/bin/env python3
from __future__ import annotations

import sqlite3
import pandas as pd
from lib.exceptions import EntryNotFoundError

def db_conn(db: str) -> sqlite3.Connection:
    """Connect to SQLite3 database.

    Args:
        * `db` (str): Database name.

    Returns:
        `sqlite3.Connection`: Database connection object.
    """
    return sqlite3.connect(db)   # Read SQLite table into dataframe.

def db_curr(engine: sqlite3.Connection) -> sqlite3.Cursor:
    """Generate SQLite3 cursor object.

    Args:
        * `engine` (sqlite3.Connection): Database connection object.

    Returns:
        `sqlite3.Cursor`: SQLite3 cursor object.
    """
    return engine.cursor()

def db_con_curr(db: str) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    """Generate both a connection and cursor objects.

    Args:
        * `db` (str): Database name.

    Returns:
        `tuple[sqlite3.Connection, sqlite3.Cursor]`: SQLite3 connection and cursor objects.
    """
    return sqlite3.connect(db), sqlite3.connect(db).cursor()

def SQLite_Query(database: str, table: str) -> tuple[pd.DataFrame, list]:
    """Access an SQLite database and query a table. Return the entire table
    and the dates column as a pandas Dataframe and a list, respectively.

    Args:
        * `database` (str): Database name.
        * `table` (str): Table name.

    Returns:
        `tuple[pd.DataFrame, list]`: Pandas Dataframe with the all the queried data
        and the list of all dates.
    """

    con = db_conn(db = database)
    df = pd.read_sql_query("SELECT * from %s" %table, con)
    dates = df.iloc[:, 1].to_list()
    con.close()
    return df, dates

def get_column(db: str, table: str, col_n: str) -> list:
    """Parse specific column from SQLite3 database into a python list.

    Args:
        * `db` (str): Database name.
        * `table` (str): Table name.
        * `col_n` (str): Column name.

    Returns:
        `list`: List with all column values.
    """

    cursor = db_con_curr(db = db)[1]
    cursor.execute("SELECT %s FROM '%s' WHERE %s IS NOT NULL" %(col_n, table, col_n))
    dat_tmp = cursor.fetchall()
    data = []
    for i in dat_tmp:
        if not i == None:
            i = str(i)  # tuple to string.
            i = i.replace('(',"").replace(')',"").replace(',',"").strip()
            data.append(i)
    return data

def table_parser(df: pd.DataFrame, dbname: str, asset_n: str) -> bool:
    """Send data from dataframe to a database.

    Args:
        * `df` (pd.Dataframe): Dataframe with the data.
        * `dbname` (str): Database name (full or relative path).
        * `asset_n` (str): Asset name as it is stored in the database table name.

    Returns:
        `boolean`: True when operation finishes successfully.
    """

    engine = db_conn(db = dbname)
    cursor = db_curr(engine = engine)
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    cursor.execute("SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name='%s'" %asset_n)
    if cursor.fetchone()[0] == 1:
        df.to_sql(asset_n, con = engine, if_exists = 'replace', index = True)
        cursor.close()
    else:
        df.to_sql(asset_n, con = engine, if_exists = 'replace', index = True)
        cursor.close()

    return True

def get_entry(db: str, d: str, table: str) -> tuple:
    """Get row from database, specified by the data column.

    Args:
        * `db` (str): Database name.
        * `d` (str): Date as string.
        * `table` (str): Table name.

    Raises:
        `EntryNotFoundError`: If date entry is not in the database.

    Returns:
        `tuple`: Resulting row from query.
    """

    cursor = db_con_curr(db = db)[1]
    cursor.execute("SELECT * FROM '%s' WHERE Dates='%s'" %(table, d))
    tmp = cursor.fetchall()
    all_data = []
    for i in tmp:
        if None in i:
            continue
        else:
            all_data.append(i)

    if len(all_data) > 1:   # If there is more than one entry of the same date,
                            # get the one with the best percent difference.
        all_percent_diff = []
        for k in all_data:
            percent_diff = k[-1]
            all_percent_diff.append(percent_diff)
        all_percent_diff = [float(x) for x in all_percent_diff] # convert to list of floats.
        smallest_diff = min(all_percent_diff)
        for m in all_data:
            if smallest_diff in m:
                return tuple(m)
            else:
                continue

    elif len(all_data) == 1:
        return tuple(all_data[0])

    else:
        raise EntryNotFoundError(f"Unable to locate entry '{d}' in database: {db}")