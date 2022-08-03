#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import subprocess
import urllib.request
from lib.args import bool_parser

def connect(host = 'http://google.com'):
    try:
        urllib.request.urlopen(host)
        return True
    except:
        raise ConnectionError('No Internet connection!')

def args_parser(msg) -> argparse.Namespace:
    """Custom argument parser.
    Args:
        * `msg` (str): Description help message.
    Returns:
        `argparse.Namespace`: Namespace of input arguments.
    """

    parser = argparse.ArgumentParser(description = msg, formatter_class = argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-env", help = "Input.")
    return parser.parse_args()

class installer:
    def __init__(self, package: str) -> None:
        self.package = package

    def pip_install(self) -> int:
        """Install package via pip.

        Returns:
            int: Returns 0 on success
        """
        return subprocess.check_call([sys.executable, "-m", "pip", "install", self.package])

    def conda_install(self):
        import conda.cli
        return conda.cli.main('conda', 'install',  '-y', self.package)

def main():
    connect()
    print('Internet connection established!\n')

    message = ("Installer")
    args = args_parser(msg = message)
    arguments = vars(args)
    env = bool_parser(arguments.get('env'))
    if env:
        if env == 'venv':   # do pip install here.
            pass
    else:   # do pip install here.
        pass
    print('Installing dependencies...')

if __name__ == '__main__':
    main()