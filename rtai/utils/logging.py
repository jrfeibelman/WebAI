
from os import path, makedirs
from sys import stdout
from inspect import stack

from logging import info as log_info, debug as log_debug, error as log_error, warn as log_warn
from logging import basicConfig, getLogger, StreamHandler, Formatter

from rtai.utils.time import now_str

# TODO wrap in a class and setup instance in __init__.py, then reroute all logging calls to use instance
USE_CALLEE_STACK = False

def setup_logging(log_dir: str, log_name: str, log_level: int, use_callee_stack: bool=False, log_stdout_pipe: bool=False) -> None:

    if not path.exists(log_dir):
        makedirs(log_dir)

    log_fmt = '[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s'
    basicConfig(filename='logs/%s_%s.log' % (log_name, now_str()), filemode='w', format=log_fmt, 
                        level=log_level)
    
    if use_callee_stack:
        global USE_CALLEE_STACK 
        USE_CALLEE_STACK = True
    
    if log_stdout_pipe:
        root = getLogger()
        root.setLevel(log_level)
        handler = StreamHandler(stdout)
        handler.setLevel(log_level)
        formatter = Formatter(log_fmt)
        handler.setFormatter(formatter)
        root.addHandler(handler)

def get_caller_details() -> str:
    call_stack = stack()
    try:
        calling_class = call_stack[2][0].f_locals["self"].__class__.__name__
    except KeyError:
        calling_class = call_stack[2][1].split('/')[-1]
        
    calling_method = call_stack[2][0].f_code.co_name
    line_number = call_stack[2][2]
    return "%s::%s::%s" % (calling_class, calling_method, line_number)

def info(msg, *args, **kwargs):
    log_info(msg if not USE_CALLEE_STACK else "[%s] %s" % (get_caller_details(), msg), *args, **kwargs)

def debug(msg, *args, **kwargs):
    # log_debug(msg, *args, **kwargs)
    log_debug(msg if not USE_CALLEE_STACK else "[%s] %s" % (get_caller_details(), msg), *args, **kwargs)

def warn(msg, *args, **kwargs):
    # log_warn(msg, *args, **kwargs)
    log_warn(msg if not USE_CALLEE_STACK else "[%s] %s" % (get_caller_details(), msg), *args, **kwargs)

def error(msg, *args, **kwargs):
    # log_error(msg, *args, **kwargs)
    log_error(msg if not USE_CALLEE_STACK else "[%s] %s" % (get_caller_details(), msg), *args, **kwargs)
