#!/usr/bin/env python3
from __future__ import annotations

import argparse

#TODO Temporary.
def args_parser(msg) -> argparse.Namespace:
    """Custom argument parser.
    Args:
        * `msg` (str): Description help message.
    Returns:
        `argparse.Namespace`: Namespace of input arguments.
    """

    parser = argparse.ArgumentParser(description = msg, formatter_class = argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-f", help = "Input.")
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