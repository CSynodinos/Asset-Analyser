#!/usr/bin/env python3
from __future__ import annotations

"""Wrapper script for all modules and functionalities of the market analysis project.
"""

import os, shutil
from lib.data import data
from lib.exceptions import AssetTypeError, PredictionDaysError, BadPortError
from lib.model_methods import preprocessing
from lib.fin_asset import financial_assets, prediction_comparison, prediction_assessment
from lib.db_utils import SQLite_Query
from dashboard.app import dashboard_launch
import datetime as dt
from inspect import getfullargspec

class analyze_asset:

    cwd = os.getcwd()

    def __init__(self, asset_type: str, asset: str, big_db = "",
                date = dt.datetime(2019, 11, 1), today = True,
                pred_days = 60, port = 8050) -> None:

        self.date = date
        self.asset_type = asset_type
        asset_types_tup = ('Cryptocurrency', 'cryptocurrency', 'crypto',
                        'Crypto', 'stock', 'Stock')
        if self.asset_type in asset_types_tup:
            self.big_db = big_db
            if self.big_db == "":
                self.big_db = asset_type + "_data.db"
        else:
            raise AssetTypeError(f"Asset type: {self.asset_type} is not valid. Some valid asset types are: "
                                "Cryptocurrency, crypto, stock.")
        self.asset = asset
        valid_curr = ('USD', 'EUR', 'JPY', 'GBP')
        if not any(curr in self.asset for curr in valid_curr):
            self.asset = self.asset + "-USD"
        self.today = today
        self.pred_days = pred_days
        if not isinstance(self.pred_days, int):
            raise PredictionDaysError('Prediction days used are not an integer.')
        self.port = port
        if not isinstance(port, int):
            raise BadPortError(f"Local host port: {port} is not an integer.")

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
            `list`: List of attributes.
        """

        all_att = list(cls.__dict__.keys())
        if not only_added:
            return all_att
        else:
            default_atts = ['__module__', '__doc__', '__dict__', '__weakref__']
            all_att = [x for x in all_att if x not in default_atts]
            return all_att

    @classmethod
    def __db_subdir(cls):
        """Class method for database subdirectory.

        Returns:
            `str`: Path to database subdirectory.
        """
        return os.path.join(cls.cwd, "Databases")

    def analyze(self) -> bool:
        """Run through all the analysis of the asset. Produces the dash dashboard on localhost.

        Returns:
            `boolean`: True when operation finishes successfully.
        """

        db_subdir = self.__db_subdir()
        fin_asset = data(start = self.date)
        asset_l = self.asset.split()
        fin_asset.asset_data(database = self.big_db, asset_type = self.asset_type, asset_list = asset_l,
                today = self.today)
        db_output = os.path.join(self.cwd, self.big_db)
        db_output_fl = os.path.join(db_subdir, self.big_db)
        shutil.move(db_output, db_output_fl)    # Move database output to Databases subdirectory.

        asset_l_q = asset_l[0].replace("-", "_")
        asset_df, asset_dates = SQLite_Query(db_output_fl, asset_l_q)
        asset_x_train, asset_y_train, asset_scaler = preprocessing(asset_df, self.pred_days)
        asset_class = financial_assets(pred_days = self.pred_days, asset_type = self.asset_type)
        asset_all_data, asset_next, asset_volatility = asset_class.predictor(x = asset_dates, 
                                                                            x_train = asset_x_train, 
                                                                            y_train = asset_y_train,
                                                                            asset_scaler = asset_scaler,
                                                                            tick = asset_l[0], 
                                                                            query_asset = asset_df)
        prediction_db = f"Prediction_Assessment_{self.asset}.db"
        prediction_assessment(df = asset_all_data, db = prediction_db, asset = asset_l[0])
        db_pred_new_fl = os.path.join(db_subdir, prediction_db)

        # Move prediction database output to Databases subdirectory.
        shutil.move(prediction_db, db_pred_new_fl)
        dashboard_launch(db = db_pred_new_fl, table = asset_l_q, fin_asset = self.asset,
                        asset_type = self.asset_type, nxt_day = asset_next,
                        volatility = asset_volatility, port = self.port)
        return True

def main():
    analyze_asset(asset_type = 'Cryptocurrency', asset = 'XRP', pred_days = 60).analyze()

if __name__ == "__main__":
    main()