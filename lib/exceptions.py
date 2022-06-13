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
            return 'DateError has been raised'
