#!/usr/bin/env python3
from __future__ import annotations

import os, argparse
import urllib.request
from subprocess import run
from typing import Literal, Final

from sys import platform
from lib.utils import yml_parser, terminal_str_formatter


if platform == "linux" or platform == "linux2" or platform == "darwin":
    PYTHON_DIST: str = 'python3'
elif platform == "win32":
    PYTHON_DIST: str = 'python'
else:
    raise RuntimeError(f'Platform {platform} is not supported.')

# constants
ENV = os.environ
REQFILE: Final[str] = 'requirements.txt'
HELP: Final[str] = yml_parser(f = 'setup.yml')['help_messages']['INSTALLER_HELP_MESSAGE']

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

    Returns:
        `argparse.Namespace`: Namespace of input arguments.
    """

    parser = argparse.ArgumentParser(description = msg, formatter_class = argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-env", help = "Python environment. Supports venv and conda.")
    return parser.parse_args()

def requirements() -> bool:
    """Check if requirements file exists.

    Returns:
        `bool`: True if file is found, False if not.
    """
    if os.path.isfile(REQFILE):
        return True
    else:
        return False

class installer_launcher:
    """Installer class holding all package manager core subprocesses.

    Args:
        * `package` (str): Package to install. Can either be a requirements file or the name of the package.
        * `f` (bool): True if package file exists, False if not. Checking occurs by requirements() outside of the class.
    """

    def __init__(self, package: str, f: bool) -> None:
        self.package = package
        self.f = f

    def pip_install(self) -> int:
        """Install package via pip.

        Returns:
            `int`: Returns 0 on success from subprocess.run()
        """

        if self.f:
            return run(['pip', 'install', '-r', f'{self.package}'], shell = True, env = ENV)
        else:
            return run(['pip', 'install', f'{self.package}'], shell = True, env = ENV)

    def conda_install(self, state: int) -> int:
        """Install package for conda using pip.

        Args:
            * `state` (int): State of package installation. First package gets 0, 
            the rest get a value > 0 to avoid retrying installation of pip.

        Returns:
            `int`: Returns 0 on success from subprocess.run()
        """
        if state == 0:
            run(['conda', 'install', 'pip', '-y'], shell = True, env = ENV)
        return int(self.pip_install())

class callers:
    """Class for pip and conda callers.

    Args:
        * `req` (bool): requirements.txt boolean argument. Get passed after requirements() has been called. 
    """

    def __init__(self, req: bool) -> None:
        self.req = req

    def pip_caller(self, pack: str | list) -> int:
        """pip package manager caller.

        Args:
            * `pack` (str | list): Package.

        Returns:
            `int`: 0 from subprocess.run()
        """

        if self.req:
            return installer_launcher(package = pack, f = True).pip_install()
        else:
            if isinstance(pack, list):
                for i in pack:
                    installer_launcher(package = i, f = False).pip_install()
            else:
                raise TypeError("If requirements.txt doesn't exist, use a list with each dependancy as a string.")

            return 0

    def conda_caller(self, pack: str | list) -> int:
        """conda package manager caller.

        Args:
            * `pack` (str | list): Package.

        Returns:
            `int`: 0 from subprocess.run()
        """
        if self.req:
            return installer_launcher(package = pack, f = True).conda_install()
        else:
            if isinstance(pack, list):
                for i in pack:
                    installer_launcher(package = i, f = False).conda_install()
            else:
                raise TypeError("If requirements.txt doesn't exist, use a list with each dependancy as a string.")

            return 0

def main():
    # Get terminal width, center and bold the title.
    print('\n')
    print(terminal_str_formatter(_str_ = 'Market Analysis Dependancy Installer'))
    print('\n')

    args = args_p(msg = HELP)
    internet_connect()
    print('Internet connection established!\n')

    arguments = vars(args)
    env = arguments.get('env')
    reqs = requirements()

    if reqs:
        dep = REQFILE
    else:
        dep = ['dash', 'keras', 'matplotlib', 'numpy', 'pandas', 
            'scikit_learn', 'seaborn', 'yfinance', 'tensorflow']

    print('Installing dependencies...\n')
    call = callers(req = reqs)
    if env:
        if env == 'venv':   # do pip install here.
            call.pip_caller(pack = dep)

        elif env == 'conda':    # do conda install here.
            call.conda_caller(pack = dep)

    elif env == None:   # default installer is pip if -env is not specified.
        call.pip_caller(pack = dep)

    return print('\nInstallation complete!!!')

if __name__ == '__main__':
    main()