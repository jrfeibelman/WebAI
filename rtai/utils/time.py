from datetime import datetime
from time import perf_counter

def now():
    return datetime.utcnow()

def now_str():
    return datetime.utcnow().strftime("%m%d%Y_%H%M%S")