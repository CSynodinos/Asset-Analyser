#!/usr/bin/env python3
from __future__ import annotations

"""Wrapper script for all modules and functionalities of the market analysis software.
"""

import os, shutil, re
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import argparse
from lib.data import data
from lib.exceptions import AssetTypeError, PredictionDaysError, BadPortError, NoParameterError, DateError
from lib.model_methods import preprocessing
from lib.fin_asset import financial_assets, prediction_assessment
from lib.db_utils import SQLite_Query
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
parse = yml_parser(f = 'setup.yml')
HELP_MESSAGE: Final[str] = parse['help_messages']['LAUNCHER_HELP_MESSAGE']

parse_constants = parse['constants']    # get constants.
PORT: Final[int] = parse_constants['PORT']
PLT: Final[bool] = parse_constants['PLT']
PREDICTION_DAYS: Final[int] = parse_constants['PREDICTION_DAYS']
DEFAULT_ASSET: Final[str] = parse_constants['DEFAULT_ASSET']
DEFAULT_ASSET_TYPE: Final[str] = parse_constants['DEFAULT_ASSET_TYPE']

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
    parser.add_argument("-d", help = "Optional argument: Start date for data calls. Format. Defaults: 2019-11-1.")
    parser.add_argument("-tdy", help = "Optional argument: End date for data calls is current date. If False, add custom date with -y -m -d parameters. Defaults: True.")
    parser.add_argument("-p", help = "Optional argument: Port for localhost containing the dashboard. Defaults to 8050.")
    parser.add_argument("-plt", help = "Optional argument: Display seaborn plots. Useful for jupyter notebooks. Defaults to False.")
    parser.add_argument("-test", help = f"Optional argument: Runs a test profile. Uses {DEFAULT_ASSET} as an example.")
    parser.add_argument("-end_y", help = "Optional argument: Year of end date for data calls. Only use when -tdy is set to False.")
    parser.add_argument("-end_m", help = "Optional argument: Month of end date for data calls. Only use when -tdy is set to False.")
    parser.add_argument("-end_d", help = "Optional argument: Day of end date for data calls. Only use when -tdy is set to False.")
    return parser.parse_args()

def bool_parser(var: Any) -> bool:
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
        elif var in _false:     # Includes None checks.
            return False
        else:
            raise TypeError(f"{var} must be true, True, 1, False, false, 0 or None.")

def _defaults(var: Any, default: object) -> object | Any:
    """Checks for None on variable var.

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

class analyzer_launcher:
    """Launcher class wrapping all program utilities and running the analysis.

    Args:
        * `asset_type` (str): Type of asset e.g. Cryptocurrency or Stock.
        * `asset` (str): Asset codename.
        * `big_db` (str | None): Main database name.
        * `date` (None | dt.datetime): Start date.
        * `today` (bool): If True, today becomes the end date.
        * `pred_days` (int): Days used for training the model.
        * `port` (int): Local host port for the dashboard.
        * `plt` (bool): If True, show the matplotlib plots.

    Raises:
        * `AssetTypeError`: Invalid asset type.
        * `PredictionDaysError`: Invalid prediction days specified.
        * `BadPortError`: Invalid network port specified.
    """

    cwd: str = os.getcwd()

    def __init__(self, asset_type: str, asset: str, big_db: str | None,
                date: None | dt.datetime, today: bool, year: str | None, 
                month: str | None, day: str | None, pred_days: int,
                port: int, plt: bool) -> None:

        self.date = date
        # will always be datetime if interpreter reaches this point because self.date input will be checked by _dt_format().
        self.date = _defaults(var = date, default = dt.datetime(2019, 11, 1))

        self.asset_type = asset_type
        asset_types_tup = ('Cryptocurrency', 'cryptocurrency', 'crypto',
                        'Crypto', 'stock', 'Stock')
        if self.asset_type in asset_types_tup:
            DEFAULT_DB: Final[str] = asset_type + "_data.db"
            self.big_db = big_db
            self.big_db = _defaults(var = self.big_db, default = DEFAULT_DB)
        else:
            raise AssetTypeError(f"Asset type: {self.asset_type} is not valid. Some valid asset types are: "
                                "Cryptocurrency, crypto, stock.")

        self.asset = asset
        valid_curr = ('USD', 'EUR', 'JPY', 'GBP')
        if not any(curr in self.asset for curr in valid_curr):
            self.asset = self.asset + "-USD"

        self.today = today
        self.today = _defaults(var = self.today, default = True)
        self.year = year
        self.month = month
        self.day = day

        self.pred_days = pred_days
        if not isinstance(self.pred_days, int):
            try:
                self.pred_days = int(_defaults(var = pred_days, default = PREDICTION_DAYS))
            except:
                raise PredictionDaysError('Prediction days (-pd) used are not an integer.')
        else:
            self.pred_days = int(self.pred_days)

        self.port = port
        self.port = _defaults(var = port, default = PORT)
        if not isinstance(port, int):
            try:
                self.port = int(self.port)
            except:
                raise BadPortError(f"Local host port: {port} is not an integer.")

        self.plt = plt
        self.plt = bool_parser(var = self.plt)
        self.plt = _defaults(var = self.plt, default = PLT)

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
        db_output_fl = os.path.join(db_subdir, self.big_db)

        if os.path.isfile(db_output_fl):
            fin_asset.asset_data(database = db_output_fl, asset_type = self.asset_type, asset_list = asset_l,
                today = self.today, year = self.year, month = self.month, day = self.day)

        else:
            fin_asset.asset_data(database = self.big_db, asset_type = self.asset_type, asset_list = asset_l,
                    today = self.today)

            # Move database output to Databases subdirectory.
            db_output = os.path.join(self.cwd, self.big_db)
            shutil.move(db_output, db_output_fl)

        asset_l_q = asset_l[0].replace("-", "_")
        asset_df, asset_dates = SQLite_Query(db_output_fl, asset_l_q)
        asset_x_train, asset_y_train, asset_scaler = preprocessing(asset_df, self.pred_days)
        asset_class = financial_assets(pred_days = self.pred_days, asset_type = self.asset_type, plot = self.plt)
        asset_all_data, asset_next, asset_volatility = asset_class.predictor(x = asset_dates, x_train = asset_x_train, 
                                                                            y_train = asset_y_train, asset_scaler = asset_scaler,
                                                                            tick = asset_l[0], query_asset = asset_df)

        prediction_db = f"Prediction_Assessment_{self.asset}.db"
        prediction_assessment(df = asset_all_data, db = prediction_db, asset = asset_l[0])
        db_pred_new_fl = os.path.join(db_subdir, prediction_db)

        # Move prediction database output to Databases subdirectory.
        shutil.move(prediction_db, db_pred_new_fl)

        # Import dashboard_launch and launch app.
        from dashboard.app import dashboard_launch
        dashboard_launch(db = db_pred_new_fl, table = asset_l_q, fin_asset = self.asset,
                        asset_type = self.asset_type, nxt_day = asset_next,
                        volatility = asset_volatility, port = self.port)

        return True

def _dt_format(date: str | None):
    """Checks for date format with regex. Format is YYYY-MM-DD.

    Args:
        * `date` (str | None): Input date.

    Raises:
        * `DateError`: If format is not YYYY-MM-DD.
        * `DateError`: If input date is not a date.
    """

    r = re.compile('.*-.*-.*')
    if not date == None and not date == "None" and not isinstance(date, (int, float)):
        try:
            pattern = r.match(date)
        except:
            raise TypeError(f"Date: {date} cannot be compiled as a regex expression. Ensure that it's either True, False or YYYY-MM-DD.")

        if pattern is not None:
            try:
                str(dt.datetime.strptime(date, '%Y-%m-%d').date())
            except ValueError:
                raise DateError('Date format should be YYYY-MM-DD.')
        else:
            raise DateError('Input for argument -d is not a date.')

    else:
        if isinstance(date, (int, float)):
            return bool_parser(date)
        else:
            return None

def main():
    args = args_parser(msg = HELP_MESSAGE)
    arguments = vars(args)
    test_profile: bool = bool_parser(arguments.get('test'))

    if test_profile:     # Launch default profile.
        analyzer_launcher(asset_type = DEFAULT_ASSET_TYPE, asset = DEFAULT_ASSET, big_db = None, date = None, 
                        today = True, year = None, month = None, day = None, pred_days = 60,
                        port = None, plt = False).analyze()

    else:
        ast = arguments.get('ast')
        ast_n: str = [k for k, v in locals().items() if v == ast][0] # gets var name.
        tp: str = arguments.get('tp')
        tp_n: str = [k for k, v in locals().items() if v == tp][0]
        pd: str = arguments.get('pd')
        db: str | None = arguments.get('db')
        tdy: bool | None = arguments.get('tdy')
        p: str = str(arguments.get('p'))
        d: str | None = arguments.get('d')
        plt: bool = bool_parser(arguments.get('plt'))
        end_year: str | None = arguments.get('y')
        end_month: str | None = arguments.get('m')
        end_day: str | None = arguments.get('d')

        if not tdy:
            if not isinstance(end_year, int):
                raise DateError('-tdy is set to False, but -end_y is not an integer. Please use an eligible number e.g. 2015')
            if not isinstance(end_month, int):
                raise DateError('-tdy is set to False, but -end_m is not an integer. Please use an eligible number e.g. 12')
            if not isinstance(end_day, int):
                raise DateError('-tdy is set to False, but -end_d is not an integer. Please use an eligible number e.g. 30')
        elif tdy:
            from warnings import warn
            if not end_year == None:
                warn('-tdy has been set but end_year is not None. end_year has been set to None.')
            if not end_month == None:
                warn('-tdy has been set but end_month is not None. end_month has been set to None.')
            if not end_day == None:
                warn('-tdy has been set but end_day is not None. end_day has been set to None.')
            end_year = None
            end_month = None
            end_day = None

        def _var_n(var_n, var: Any) -> tuple:
            if var == None:
                var = 'None'
            _str = var_n + ", " + var
            return tuple(map(str, _str.split(', ')))

        ast_nv = _var_n(var_n = ast_n, var = ast)
        tp_nv = _var_n(var_n = tp_n, var = tp)  # Add to this for new essential args.
        lst_vars = [ast_nv, tp_nv]
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

        analyzer_launcher(asset_type = tp, asset = ast, big_db = db, date = d,
                        today = tdy, year = end_year, month = end_month, day = end_day,
                        pred_days = pd, port = p, plt = plt).analyze()

if __name__ == "__main__":
    main()