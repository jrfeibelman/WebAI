from threading import Timer as Thread_Timer
from numpy import uint16
from dataclasses import dataclass
from typing import Callable, Dict
from time import time

from rtai.utils.logging import info, warn

@dataclass
class TimerWrapper:
    """ _summary_ Wrapper class for a timer object"""

    def __init__(self, thread_id: str, seconds: float, callback: Callable):
        """ _summary_ Constructor for the TimerWrapper
        
        Args:
            thread_id (str): ID of the thread
            seconds (float): number of seconds for the timer
            callback (Callable): callback function to call when the timer expires
            timer (Thread_Timer): timer object
        """
        self.thread_id: str = thread_id
        self.seconds: float = seconds
        self.callback: Callable = callback
        self.timer: Thread_Timer = None
        self.remaining: float = seconds
        self.start_time: time = None
        self.is_paused: bool = False

    def pause(self):
        if self.timer:
            self.timer.cancel()
            self.remaining -= time() - self.start_time
            self.timer = None
            self.is_paused = True
        else:
            warn("Failed to pause timer %s - not yet running." % self.thread_id)

    def resume(self):
        if not self.timer:
            self.is_paused = False
            self.start()
        else:
            warn("Failed to resume timer %s - already running." % self.thread_id)

    def start(self):
        self.timer = Thread_Timer(self.remaining, self.callback, [self.thread_id])
        self.timer.name = self.thread_id
        self.remaining = self.seconds
        self.start_time = time()
        self.timer.start()

    def cancel(self):
        if self.timer:
            self.timer.cancel()

class TimerManager:
    """ _summary_ Singleton class to manage timers"""

    def __new__(cls):
        """ _summary_ Singleton constructor for the TimerManager"""
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
            cls._instance.timers: Dict[str, TimerWrapper] = dict()
            cls._instance.terminated: bool = False
            cls._instance.is_paused: bool = False
        return cls._instance

    def start_timers(self) -> None:
        """ _summary_ Start all timers """
        [t.start() for t in self.timers.values()]
        info("All Timers Started")

    def pause_timers(self) -> None:
        [t.pause() for t in self.timers.values()]
        self.is_paused = True
        info("All Timers Paused")

    def resume_timers(self) -> None:
        [t.resume() for t in self.timers.values()]
        self.is_paused = False
        info("All Timers Resumed")

    def stop_timers(self) -> None:
        """ _summary_ Stop all timers """
        self.terminated = True
        info("Joining Timers.........")
        [t.cancel() for t in self.timers.values()]
        info("All Timers Joined.........")

    def add_timer(self, thread_id: str, seconds: uint16, callback_func: Callable, milliseconds: bool=False) -> None:
        """ _summary_ Add a timer to the timer manager
        
        Args:
            thread_id (str): ID of the thread
            seconds (uint16): number of seconds for the timer
            callback_func (Callable): callback function to call when the timer expires
            milliseconds (bool, optional): whether or not the seconds are in milliseconds. Defaults to False.
        """

        seconds = float(seconds/1000.0) if milliseconds else float(seconds)
        print("Adding Timer %s every %s seconds." % (thread_id, seconds))
        self.timers[thread_id] = TimerWrapper(thread_id, seconds, callback_func)
    
    def reset_timer(self, thread_id: str) -> bool:
        """ _summary_ Reset a timer
        
        Args:
            thread_id (str): ID of the thread
            
        Returns:
            bool: whether or not the timer was reset
        """
        if not self.terminated and thread_id in self.timers:
            self.timers[thread_id].start()
            return True
        return False

    def timer_callback(func) -> Callable:
        """ _summary_ A decorator for callback functions from timers 
        
        Args:
            func (Callable): callback function to call when the timer expires
            
        Returns:
            Callable: wrapper function for the callback function
        """
        def wrapper(self, thread_id: str="", *args, **kwargs) -> None:
            """ _summary_ Wrapper for callback functions from timers 
            
            Args:
                thread_id (str, optional): ID of the thread. Defaults to "".
                args (list, optional): arguments for the callback function. Defaults to [].
                kwargs (dict, optional): keyword arguments for the callback function. Defaults to {}.
            """
            func(self, *args, **kwargs)
            if len(thread_id) > 0:
                TimerManager().reset_timer(thread_id)
        return wrapper