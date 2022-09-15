#!/usr/bin/env python3
from __future__ import annotations

import os
from inspect import getfullargspec

def yml_parser(f: str) -> dict:
    """Parser for a .yml file.

    Args:
        * `f` (str): .yml file.

    Returns:
        `dict`: Contents of yml.
    """

    import yaml
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

class dunders:
    """Custom dunder methods.
    """

    @classmethod
    def __repr__(cls) -> str:
        params = getfullargspec(__class__).args
        try:
            params.remove("self")
        except:     # Only when class __init__ has self and no other parameters.
            return ['self']
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