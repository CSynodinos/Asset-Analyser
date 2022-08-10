#!/usr/bin/env python3
from __future__ import annotations

import os, subprocess, argparse
import urllib.request
from typing import Literal

from sys import platform
if platform == "linux" or platform == "linux2" or platform == "darwin":
    python_dist = 'python3'
elif platform == "win32":
    python_dist = 'python'
else:
    raise RuntimeError(f'Platform {platform} is not supported.')

def internet_connect(host = 'http://google.com') -> Literal[True]:
    """Check internet connection.

    Args:
        * `host` (str, optional): http link. Defaults to 'http://google.com'.

    Raises:
        ConnectionError: No Internet.

    Returns:
        Literal[True]: True for established internet connection.
    """
    try:
        urllib.request.urlopen(host)
        return True
    except:
        try:    # try bing in case google is down.
            urllib.request.urlopen('http://bing.com')
        except:
            raise ConnectionError('No Internet connection!')

def args_p(msg) -> argparse.Namespace:
    """Custom argument parser.
    Args:
        * `msg` (str): Description help message.
        * `-env` (str): Select python environment.
    Returns:
        `argparse.Namespace`: Namespace of input arguments.
    """

    parser = argparse.ArgumentParser(description = msg, formatter_class = argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-env", help = "Python environment.")
    return parser.parse_args()

def requirements() -> str | None:
    """Check if requirements file exists.

    Returns:
        str | None: string if file is found.
    """
    reqfile = 'requirements.txt'
    if os.path.isfile(reqfile):
        return str(reqfile)
    else:
        return None

class installer_class:
    """Installer class holding all package manager core subprocesses.
    """

    def __init__(self, package: str, f: bool) -> None:
        self.package = package
        self.f = f

    def pip_install(self) -> int:
        """Install package via pip.

        Returns:
            `int`: Returns 0 on success from subprocess.call()
        """
        if self.f:
            return subprocess.call([f'{python_dist} -m pip install -r {self.package}'], shell = True)
        else:
            return subprocess.call([f'{python_dist} -m pip install {self.package}'], shell = True)

    def conda_install(self) -> int:
        """Install package via conda.

        Returns:
            `int`: Returns 0 on success from subprocess.call()
        """
        subprocess.call(['conda install pip -y'], shell = True)
        return int(self.pip_install())

def pip_caller(pack: str | list) -> int:
    """pip package manager caller.

    Args:
        * `pack` (str | list): Package.

    Returns:
        `int`: 0 from subprocess.call()
    """
    if isinstance(pack, str):
        return installer_class(package = pack, f = True).pip_install()
    elif isinstance(pack, list):
        for i in pack:
            installer_class(package = i, f = False).pip_install()
        return 0

def conda_caller(pack: str | list) -> int:
    """conda package manager caller.

    Args:
        * `pack` (str | list): Package.

    Returns:
        `int`: 0 from subprocess.call()
    """
    if isinstance(pack, str):
        return installer_class(package = pack, f = True).conda_install()
    elif isinstance(pack, list):
        for i in pack:
            installer_class(package = i, f = False).conda_install()
        return 0

def main() -> None:
    internet_connect()
    print('Internet connection established!\n')

    message = ("Installer")
    args = args_p(msg = message)
    arguments = vars(args)
    env = arguments.get('env')
    reqs = requirements()

    if reqs is not None:
        dep = requirements()
    else:
        dep = ['dash', 'keras', 'matplotlib', 'numpy', 'pandas', 
            'scikit_learn', 'seaborn', 'yfinance', 'tensorflow']

    print('Installing dependencies...\n')
    if env:
        if env == 'venv':   # do pip install here.
            pip_caller(pack = dep)

        elif env == 'conda':    # do conda install here.
            conda_caller(pack = dep)

    elif env == None:   # default installer is pip if -env is not specified.
        pip_caller(pack = dep)

    return print('\nInstallation complete!!!')

if __name__ == '__main__':
    main()