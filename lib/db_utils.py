import sqlite3
import pandas as pd

def SQLite_Query(database: str, table: str):
        """Access an SQLite database and query a table. Get the entire table
        and the dates column as two separate pandas Dataframes.

        Args:
            * `database` (str): Database name.
            * `table` (str): Table name.

        Returns:
            `pd.DataFrame`: Pandas Dataframe with the queried data.
        """

        con = sqlite3.connect(database)   # Read SQLite table into dataframe.
        df = pd.read_sql_query("SELECT * from %s" %table, con)
        dates = df.iloc[:, 1].to_list()
        con.close()
        return df, dates

def table_parser(df: pd.DataFrame, dbname: str, asset_n: str) -> bool:
    """Send data from dataframe to a database.

    Args:
        df (pd.Dataframe): Dataframe.

    Returns:
        bool: _description_
    """

    engine = sqlite3.connect(dbname)
    if "-" in asset_n:
        asset_n = asset_n.replace('-', "_")
    if " " in asset_n:
        asset_n = asset_n.replace(' ', "")

    cursor = engine.cursor()
    cursor.execute("SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name='%s'" %asset_n)
    if cursor.fetchone()[0] == 1:
        cursor.execute("SELECT * FROM '%s'" %asset_n)
        table_cols = list(map(lambda x: x[0], cursor.description))
        df_cols = list(df.columns)
        col_diff = list(set(df_cols) - set(table_cols))
        if len(col_diff) != 0:
            for i in col_diff:
                cursor.execute("ALTER TABLE '%s' ADD COLUMN '%s'" %(asset_n, i))
        else:
            pass
        df.to_sql(asset_n, con = engine, if_exists = 'append', index = True)
    else:
        df.to_sql(asset_n, con = engine, if_exists = 'append', index = True)

    return True