#!/usr/bin/env python3
from __future__ import annotations

import yaml, os

def yml_parser(f: str) -> dict:
    """Parser for a .yml file.

    Args:
        * `f` (str): .yml file.

    Returns:
        dict: Contents of yml.
    """

    with open(f, 'r') as fl_stream:
        try:
            return dict(yaml.safe_load(fl_stream))
        except yaml.YAMLError as exc:
            print(exc)

def terminal_str_formatter(_str_: str) -> str:
    """Bold and centre a string for the terminal. 

    Args:
        * `_str_` (str): Input str.

    Returns:
        `str`: Formatted str.
    """
    terminal_width = os.get_terminal_size().columns
    return f'\033[1m{_str_}\033[0m'.center(terminal_width)