'''
        [ NOMINAL SYSTEMS ]
This file contains helper functions for printing
lines to the console. By default, any calls made
to these functions will not print any data. If
the verbosity is enabled, then data will be printed
to the console. Additioanlly, data can be printed
in a text file if set.
'''

# Defines ANSI escape sequences for colors
__RESET =     '\033[0m'
__RED =       '\033[31m'
__GREEN =     '\033[32m'
__YELLOW =    '\033[33m'
__BLUE =      '\033[34m'
__PURPLE =    '\033[35m'
__CYAN =      '\033[36m'
__WHITE =     '\033[37m'
__GREY =      '\033[90m' 

# Defines the colors for the specific verbose types
__LOG     = __GREY
__WARNING = __YELLOW
__ERROR   = __RED
__SUCCESS = __GREEN

# Defines the available verbose levels
LOG_VERBOSITY: str      = "log"
WARNING_VERBOSITY: str  = "warning"
ERROR_VERBOSITY: str    = "error"

__verbose: bool = False
__verbose_level: str = ""

def set_verbosity (level: str) -> None:
    
    global __verbose, __verbose_level
    if level.lower() in [LOG_VERBOSITY, WARNING_VERBOSITY, ERROR_VERBOSITY]:
        __verbose_level = level.lower()
        __verbose = True
    else:
        __verbose_level = ""
        __verbose = False

def output(data: str, color: str = "") -> None:
    if __verbose:
        print(color + data + __RESET)

def log (data: str) -> None:
    if __verbose_level == LOG_VERBOSITY:
        output(data, __LOG)

def warning (data: str) -> None:
    if __verbose_level in [LOG_VERBOSITY, WARNING_VERBOSITY]:
        output(data, __WARNING)

def error (data: str) -> None:
    if __verbose_level in [LOG_VERBOSITY, WARNING_VERBOSITY, ERROR_VERBOSITY]:
        output(data, __ERROR)

def success (data: str) -> None:
    if __verbose_level == LOG_VERBOSITY:
        output(data, __SUCCESS)