#!/usr/bin/env python3
from __future__ import annotations
from asyncio import constants

"""Wrapper script for all modules and functionalities of the market analysis software.
"""

import os, shutil, re
import argparse
from lib.data import data
from lib.exceptions import AssetTypeError, PredictionDaysError, BadPortError, NoParameterError, DateError
from lib.model_methods import preprocessing
from lib.fin_asset import financial_assets, prediction_assessment
from lib.db_utils import SQLite_Query
from dashboard.app import dashboard_launch
import datetime as dt
from inspect import getfullargspec
from typing import Any, Final

def yml_parser(f: str) -> dict:
    """Parser for a .yml file.

    Args:
        * `f` (str): .yml file.

    Returns:
        dict: Contents of yml.
    """

    import yaml
    with open(f, 'r') as fl_stream:
        try:
            return dict(yaml.safe_load(fl_stream))
        except yaml.YAMLError as exc:
            print(exc)

# constants
parse = yml_parser(f = 'setup.yml')['constants']    # get constants.
HELP_MESSAGE: Final[str] = parse['HELP_MESSAGE']
PORT: Final[int] = parse['PORT']
PLT: Final[bool] = parse['PLT']
PREDICTION_DAYS: Final[int] = parse['PREDICTION_DAYS']

def args_parser(msg) -> argparse.Namespace:
    """Custom argument parser.
    Args:
        * `msg` (str): Description help message.
    Returns:
        `argparse.Namespace`: Namespace of input arguments.
    """

    parser = argparse.ArgumentParser(description = msg, formatter_class = argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-ast", help = "Market Asset. Needs to be written as: Asset_initials-currency")
    parser.add_argument("-tp", help = "Asset Type, etc. Cryptocurrency or Stock.")
    parser.add_argument("-pd", help = "Prediction days used for training. Must be a positive integer.")
    parser.add_argument("-db", help = "Optional argument: SQLite3 Database name. Defaults: asset_name_data.db")
    parser.add_argument("-d", help = "Optional argument: Start date for data calls. Format. Defaults: 2019-11-1")
    parser.add_argument("-tdy", help = "Optional argument: End date for data calls is current date. If False, add custom date with format: YYYY-MM-DD. Defaults: True")
    parser.add_argument("-p", help = "Optional argument: Port for localhost containing the dashboard. Defaults to 8050")
    parser.add_argument("-plt", help = "Optional argument: Display seaborn plots. Useful for jupyter notebooks. Defaults to False")
    return parser.parse_args()

def bool_parser(var: any) -> bool:
    """Check if parameter is boolean, if not, convert it to boolean.
    Args:
        * `var` (Any): variable to check for boolean.
    Raises:
        TypeError: Unable to convert to boolean.
    Returns:
        boolean: True if var is boolean, False if not.
    """

    _true = ["true", "True", "1"]
    _false = ["false", "False", "0", None]
    if type(var) == bool:
        return var
    else:
        if var in _true:
            return True
        elif var in _false:
            return False
        else:
            raise TypeError(f"{var} must be true, True, 1, False, false, 0 or None.")

def _defaults(var: Any, default: object) -> object | Any:
    """Checks for None for variable var.

    Args:
        * `var` (Any): The variable.
        * `var_type` (Any): Specify var type.
        * `default` (object): The default value of the object.

    Returns:
        `object | Any`: The default value specified (object) or the original value (Any).
    """
    if var in [None, 'None']:
        return default
    else:
        return var

class analyzer_launcher:    #TODO: docstrings for class
    """Analyzer class wrapping all program utilities.

    Raises:
        * AssetTypeError: Invalid asset type.
        * `PredictionDaysError`: Invalid prediction days specified.
        * `BadPortError`: Invalid network port specified.
    """

    cwd: str = os.getcwd()

    def __init__(self, asset_type: str, asset: str, big_db: str | None,
                date: None | dt.datetime, today: bool,
                pred_days: int, port: int, plt: bool) -> None:

        self.date = _defaults(var = self.date, default = dt.datetime(2019, 11, 1))

        self.asset_type = asset_type
        asset_types_tup = ('Cryptocurrency', 'cryptocurrency', 'crypto',
                        'Crypto', 'stock', 'Stock')
        if self.asset_type in asset_types_tup:
            DEFAULT_DB: Final[str] = asset_type + "_data.db"
            self.big_db = _defaults(var = self.big_db, default = DEFAULT_DB)
        else:
            raise AssetTypeError(f"Asset type: {self.asset_type} is not valid. Some valid asset types are: "
                                "Cryptocurrency, crypto, stock.")

        self.asset = asset
        valid_curr = ('USD', 'EUR', 'JPY', 'GBP')
        if not any(curr in self.asset for curr in valid_curr):
            self.asset = self.asset + "-USD"

        self.today = _defaults(var = today, default = True)

        self.pred_days = _defaults(val = pred_days, default = PREDICTION_DAYS)
        if not isinstance(self.pred_days, int):
            raise PredictionDaysError('Prediction days used are not an integer.')
        else:
            self.pred_days = int(self.pred_days)

        self.port = _defaults(var = port, default = PORT)
        if not isinstance(port, int):
            raise BadPortError(f"Local host port: {port} is not an integer.")
        else:
            self.port = int(self.port)

        self.plt = _defaults(val = self.plt, default = PLT)

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
        asset_class = financial_assets(pred_days = self.pred_days, asset_type = self.asset_type, plot = self.plt)
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

def _dt_format(date: str | None):
    """Checks for data format with regex. Format is YYYY-MM-DD.

    Args:
        * `date` (str | None): Input date.

    Raises:
        * `DateError`: If format is not YYYY-MM-DD.
        * `DateError`: If input date is not a date.
    """

    r = re.compile('.*-.*-.*')
    if date is not None:
        if r.match(date) is not None:
            try:
                str(dt.datetime.strptime(date, '%Y-%m-%d').date())
            except ValueError:
                raise DateError('Date format should be YYYY-MM-DD.')
        else:
            raise DateError('Input for argument -d is not a date.')

def main():
    args = args_parser(msg = HELP_MESSAGE)
    arguments = vars(args)
    ast = arguments.get('ast')
    ast_n: str = [k for k, v in locals().items() if v == ast][0] # gets var name.
    tp: str = arguments.get('tp')
    tp_n: str = [k for k, v in locals().items() if v == tp][0]
    pd: str = arguments.get('pd')
    pd_n: str = [k for k, v in locals().items() if v == pd][0]
    db: str | None = arguments.get('db')
    tdy: bool | None= bool_parser(arguments.get('tdy'))
    p: str = str(arguments.get('p'))
    d: str | None = arguments.get('d')
    plt: bool = bool_parser(arguments.get('plt'))

    def _var_n(var_n, var: Any) -> tuple:
        if var == None:
            var = 'None'
        _str = var_n + ", " + var
        return tuple(map(str, _str.split(', ')))

    ast_nv = _var_n(var_n = ast_n, var = ast)
    tp_nv = _var_n(var_n = tp_n, var = tp)
    pd_nv = _var_n(var_n = pd_n, var = pd)
    lst_vars = [ast_nv, tp_nv, pd_nv]  # Add to this for new essential args.
    essential_args = {}     # Contains all essential argument values.
    for i in lst_vars:
        key = i[0]
        value = i[1]
        essential_args[key] = value
    for key, value in essential_args.items():
        if essential_args[key] == 'None':
            raise NoParameterError(f'Argument: "-{key}" is not set.')
        else:
            continue

    # Date checks
    _dt_format(date = d)
    _dt_format(date = tdy)

    analyzer_launcher(asset_type = 'Cryptocurrency', asset = 'XRP', big_db = db, date = d, pred_days = pd, port = p).analyze()

if __name__ == "__main__":
    print(HELP_MESSAGE)
    #main()