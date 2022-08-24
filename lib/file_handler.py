#!/usr/bin/env python3
from __future__ import annotations

import os, fnmatch
from lib.utils import dunders

#TODO: Might get deprecated!!!!
class directories(dunders):
    """Class holds 2 functions:

    >>> location(pattern)

    >>> contents(dir, pattern, extension)

    location() finds a subdirectory according to a given pattern.

    contents() finds a file according to a given pattern.
    """    

    def __init__(self, d):
        self.d = d
        super().__init__()

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
