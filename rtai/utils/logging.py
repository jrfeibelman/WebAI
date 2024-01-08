
from os import path, makedirs
from sys import stdout
from inspect import stack

from logging import info as log_info, debug as log_debug, error as log_error, warning as log_warn
from logging import basicConfig, getLogger, StreamHandler, Formatter, FileHandler, Formatter, INFO

from rtai.utils.datetime import now_str

# TODO wrap in a class and setup instance in __init__.py, then reroute all logging calls to use instance
USE_CALLEE_STACK = False
t_logger = None

# class LogFormatter(Formatter):
#     def format(self, record):
#         custom_name = getattr(record, 'custom_name', 'DefaultName')
#         custom_time = getattr(record, 'custom_time', 'DefaultTime')
#         custom_description = getattr(record, 'custom_description', 'DefaultDescription')

#         # Format the message with different colors
#         formatted_message = f"{Fore.RED}[{custom_name}]{Fore.GREEN} [{custom_time}]{Fore.BLUE} [{custom_description}] {Fore.YELLOW}{record.getMessage()}{Style.RESET_ALL}"
#         return formatted_message
    
class TranscriptFormatter(Formatter):
    """ _summary_ Custom formatter for the transcript log using color coding - TODO NOT YET IMPLEMENTED"""
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    cyan = "\x1b[36;20m"
    green = "\x1b[32;20m"
    magenta = "\x1b[35;20m"
    red = "\x1b[31;20m"
    blue = '\x1b[38;5;39m'
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def format(self, record):
        """ _summary_ Format the log message """
        custom_name = getattr(record, 'custom_name', '')
        custom_time = getattr(record, 'custom_time', '')
        custom_type = getattr(record, 'custom_type', '')

        # COLOR CODING ONLY WORKS FOR CONSOLE OUTPUT
        # formatted_message = f"{self.green}[{custom_time}]{self.magenta} [{custom_name}]{self.cyan} [{custom_type}] {self.reset}{record.getMessage()}"
        formatted_message = f"[{custom_time}] [{custom_name}] [{custom_type}] {record.getMessage()}"
        return formatted_message

def setup_logging(log_dir: str, log_name: str, log_level: int, transcript_log_name: str='', use_callee_stack: bool=False, log_stdout_pipe: bool=False) -> None:
    """ _summary_ Setup the logging for the agent

    Args:
        log_dir (str): directory to store the log files
        log_name (str): name of the log file
        log_level (int): logging level
        transcript_log_name (str, optional): name of the transcript log file. Defaults to ''.
        use_callee_stack (bool, optional): whether or not to use the callee stack to get the calling class and method. Defaults to False.
        log_stdout_pipe (bool, optional): whether or not to pipe the log to stdout. Defaults to False.
    """
    if not path.exists(log_dir):
        makedirs(log_dir)

    log_fmt = '[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s'
    basicConfig(filename='%s/%s_%s.log' % (log_dir, log_name, now_str()), filemode='w', format=log_fmt, 
                        level=log_level)
    
    if use_callee_stack:
        global USE_CALLEE_STACK 
        USE_CALLEE_STACK = True
    
    if log_stdout_pipe:
        logger = getLogger()
        logger.setLevel(log_level)
        handler = StreamHandler(stdout)
        handler.setLevel(log_level)
        formatter = Formatter(log_fmt)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if len(transcript_log_name) > 0:
        global t_logger
        handler = FileHandler(filename='%s/%s_%s.log' % (log_dir, transcript_log_name, now_str()))   
        handler.setLevel(INFO)
        formatter = TranscriptFormatter()
        handler.setFormatter(formatter)

        t_logger = getLogger('transcript')
        t_logger.setLevel(INFO)
        t_logger.addHandler(handler)
        # COLOR CODING ONLY WORKS FOR CONSOLE OUTPUT
        # ch = StreamHandler()
        # ch.setLevel(INFO)
        # ch.setFormatter(formatter)
        # t_logger.addHandler(ch)

def get_caller_details() -> str:
    """ _summary_ Get the details of the calling class and method
    
    Returns:
        str: string representation of the calling class and method
    """
    call_stack = stack()
    try:
        calling_class = call_stack[2][0].f_locals["self"].__class__.__name__
    except KeyError:
        calling_class = call_stack[2][1].split('/')[-1]
        
    calling_method = call_stack[2][0].f_code.co_name
    line_number = call_stack[2][2]
    return "%s::%s::%s" % (calling_class, calling_method, line_number)

def info(msg, *args, **kwargs):
    """ _summary_ Log an info message
    
    Args:
        msg (any): object to log
        args (list): arguments for the message
        kwargs (dict): keyword arguments for the message
    """
    log_info(msg if not USE_CALLEE_STACK else "[%s] %s" % (get_caller_details(), msg), *args, **kwargs)

def debug(msg, *args, **kwargs):
    """ _summary_ Log a debug message
    
    Args:
        msg (any): object to log
        args (list): arguments for the message
        kwargs (dict): keyword arguments for the message
    """
    log_debug(msg if not USE_CALLEE_STACK else "[%s] %s" % (get_caller_details(), msg), *args, **kwargs)

def warn(msg, *args, **kwargs):
    """ _summary_ Log a warning message
    
    Args:
        msg (any): object to log
        args (list): arguments for the message
        kwargs (dict): keyword arguments for the message
    """
    log_warn(msg if not USE_CALLEE_STACK else "[%s] %s" % (get_caller_details(), msg), *args, **kwargs)

def error(msg, *args, **kwargs):
    """ _summary_ Log an error message
    
    Args:
        msg (any): object to log
        args (list): arguments for the message
        kwargs (dict): keyword arguments for the message
    """
    log_error(msg if not USE_CALLEE_STACK else "[%s] %s" % (get_caller_details(), msg), *args, **kwargs)

def log_transcript(sender, time, event, msg):
    """ _summary_ Log a transcript message
    
    Args:
        sender (str): name of the sender
        time (str): time of the message
        event (str): event of the message
        msg (str): message to log
    """
    if t_logger:
        t_logger.info(msg, extra={'custom_name': sender, 'custom_time': time, 'custom_type': event})