
from abc import ABC, abstractmethod

from rtai.utils.datetime import datetime, timedelta

class AbstractBehavior(ABC):
    """_summary_ Abstract base class to represent an agent behavior."""
    def __init__(self):
        pass