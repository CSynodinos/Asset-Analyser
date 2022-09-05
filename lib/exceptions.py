#!/usr/bin/env python3
from __future__ import annotations

## Custom Exceptions

class DateError(Exception):
    """Custom exception class raised when the date is not selected."""

    __module__ = 'builtins'

    def __init__(self, *args) -> None:
        if args:
            self.errmessage = args[0]
        else:
            self.errmessage = None

    def __repr__(self) -> str:
        if self.errmessage:
            return '{0} '.format(self.errmessage)
        else:
            return f'{self.__class__.__name__} has been raised.'

class EntryNotFoundError(Exception):
    """Custom exception class raised when a database entry is not found."""

    __module__ = 'builtins'

    def __init__(self, *args) -> None:
        if args:
            self.errmessage = args[0]
        else:
            self.errmessage = None

    def __repr__(self) -> str:
        if self.errmessage:
            return '{0} '.format(self.errmessage)
        else:
            return f'{self.__class__.__name__} has been raised.'

class BadPortError(Exception):
    """Custom exception class raised when local host port is invalid."""

    __module__ = 'builtins'

    def __init__(self, *args) -> None:
        if args:
            self.errmessage = args[0]
        else:
            self.errmessage = None

    def __repr__(self) -> str:
        if self.errmessage:
            return '{0} '.format(self.errmessage)
        else:
            return f'{self.__class__.__name__} has been raised.'

class AssetTypeError(Exception):
    """Custom exception class raised when asset type is invalid."""

    __module__ = 'builtins'

    def __init__(self, *args) -> None:
        if args:
            self.errmessage = args[0]
        else:
            self.errmessage = None

    def __repr__(self) -> str:
        if self.errmessage:
            return '{0} '.format(self.errmessage)
        else:
            return f'{self.__class__.__name__} has been raised.'

class PredictionDaysError(Exception):
    """Custom exception class raised when prediction days are invalid."""

    __module__ = 'builtins'

    def __init__(self, *args) -> None:
        if args:
            self.errmessage = args[0]
        else:
            self.errmessage = None

    def __repr__(self) -> str:
        if self.errmessage:
            return '{0} '.format(self.errmessage)
        else:
            return f'{self.__class__.__name__} has been raised.'

class NoParameterError(Exception):
    """Custom exception class raised when no command line input is set."""

    __module__ = 'builtins'

    def __init__(self, *args) -> None:
        if args:
            self.errmessage = args[0]
        else:
            self.errmessage = None

    def __repr__(self) -> str:
        if self.errmessage:
            return '{0} '.format(self.errmessage)
        else:
            return f'{self.__class__.__name__} has been raised.'