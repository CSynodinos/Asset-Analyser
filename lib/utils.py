#!/usr/bin/env python3
from __future__ import annotations

import yaml

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