import os
import sys
import fnmatch

class directories():    
    def __init__(self, d):
        """Class holds 3 functions:
    
        >>> OS()
        
        >>> location(pattern)
        
        >>> contents(dir, pattern, extension)
        
        OS( ) finds the operating system currently running in the machine.
        
        location( ) finds a subdirectory according to a given pattern.
        
        contents( ) finds a file according to a given pattern."""
        
        self.d = d
    
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
            if fnmatch.fnmatch(dir, pt):
                x = str(os.path.join(directory, dir))
        
        return x
    
    def contents(self, dir, pattern, extension):
        """Finds a file according to a pattern and returns it as a string.
        
        `dir` is the directory that will be searched.
        
        `pattern` is the file name pattern.
        
        `extension` is the file extension. Add a . in the beggining of the string like: .txt"""
        
        cont = os.listdir(dir)
        pt = ('%s*' %pattern)   # pattern.
                
        for file in cont:
            if file.endswith(extension) and fnmatch.fnmatch(file, pt):
                x = str(os.path.join(dir, file))
                
        return x