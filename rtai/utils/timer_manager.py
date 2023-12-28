from threading import Timer as Thread_Timer
from numpy import uint16
from dataclasses import dataclass
from typing import Callable, Dict

from rtai.utils.logging import info

@dataclass
class TimerWrapper:
    thread_id: str
    seconds: uint16
    callback: Callable
    timer: Thread_Timer

    def __init__(self, thread_id: str, seconds: uint16, callback: Callable, timer: Thread_Timer):
        self.thread_id = thread_id
        self.seconds = seconds
        self.callback = callback
        self.timer = timer
        self.timer.name = thread_id

    def start(self):
        self.timer.start()

    def cancel(self):
        self.timer.cancel()

    def reset(self):
        self.timer = Thread_Timer(self.seconds, self.callback, [self.thread_id])
        self.timer.name = self.thread_id
        self.timer.start()

class TimerManager:
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
            cls._instance.timers: Dict[uint16, TimerWrapper] = dict()
            cls._instance.terminated: bool = False
        return cls._instance

    def start_timers(self) -> None:
        [t.start() for t in self.timers.values()]
        info("All Timers Started")

    def stop_timers(self) -> None:
        self.terminated = True
        info("Joining Timers.........")
        [t.cancel() for t in self.timers.values()]
        info("All Timers Joined.........")

    def add_timer(self, thread_id: str, seconds: uint16, callback_func: Callable, milliseconds: bool=False) -> None:
        seconds = uint16(seconds/1000) if milliseconds else uint16(seconds)
        self.timers[thread_id] = TimerWrapper(thread_id, seconds, callback_func, Thread_Timer(seconds, callback_func, [thread_id]))
    
    def reset_timer(self, thread_id: str) -> bool:
        if not self.terminated and thread_id in self.timers:
            self.timers[thread_id].reset()
            return True
        return False

    def timer_callback(func):
        """
        A decorator for callback functions from timers 
        """
        def wrapper(self, thread_id: str):
            func(self)
            if len(thread_id) > 0:
                TimerManager().reset_timer(thread_id)
        return wrapper