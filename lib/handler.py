#!/usr/bin/env python3
from __future__ import annotations

import os, sys, fnmatch
from inspect import getfullargspec

class directories:
    """Class holds 3 functions:

    >>> OS()

    >>> location(pattern)

    >>> contents(dir, pattern, extension)

    OS() finds the operating system currently running in the machine.

    location() finds a subdirectory according to a given pattern.

    contents() finds a file according to a given pattern.
    """    

    def __init__(self, d):
        self.d = d

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
            list: List of attributes.
        """

        all_att = list(cls.__dict__.keys())
        if not only_added:
            return all_att
        else:
            default_atts = ['__module__', '__doc__', '__dict__', '__weakref__']
            all_att = [x for x in all_att if x not in default_atts]
            return all_att

    def OS(self):   
        """Checks the OS type and returns corresponding slash."""
        
        type = sys.platform

        if type == 'win32':
            sl = str("\\")
        else:
            sl = str("/")
        
        return sl

    def location(self, pattern):
        """Finds a subdirectory according to a pattern and returns it as a string.
        
        `pattern` is a string pattern found in the required subdirectory."""
        
        directory = str(self.d)
        pt = ('%s*' %pattern)   # pattern.
        cont = os.listdir(directory)

        for dir in cont:
            print(dir)
            if dir == "Databases":
                x = str(os.path.join(directory, dir))

        return x

    def contents(self, dir, pattern, extension):
        """Finds a file according to a pattern and returns it as a string.

        `dir` is the directory that will be searched.

        `pattern` is the file name pattern.

        `extension` is the file extension. Add a . in the beginning of the string like: .txt"""

        cont = os.listdir(dir)
        pt = ('%s*' %pattern)   # pattern.

        for file in cont:
            if file.endswith(extension) and fnmatch.fnmatch(file, pt):
                x = str(os.path.join(dir, file))

        return x
