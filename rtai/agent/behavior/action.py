from rtai.utils.datetime import datetime, timedelta
from rtai.agent.behavior.abstract_behavior import AbstractBehavior

class Action(AbstractBehavior):

    def __init__(self, description: str, address: str, start_time: datetime, duration: timedelta, end_time: datetime=None):
        self.end_time: datetime = self._calc_end_time(start_time=start_time, duration=duration) if start_time and not end_time else end_time
        self.address: str = address
        self.start_time: datetime = start_time
        self.plan_duration: timedelta = duration
        self.description: str = description

        self.completion_time: datetime = None
        self.action_duration: timedelta = None

    def __str__(self):
        return f"Action [{self.description}] start [{self.start_time}] - end [{self.end_time}] --> dur [{self.plan_duration}]"

    def __repr__(self):
        return f"Action [{self.description}]"

    def _calc_end_time(self, start_time: datetime, duration: timedelta) -> datetime:
        if start_time._data.second != 0:
            start_time.replace_time(seconds=0)
        return (start_time + duration)
    
    def mark_completed(self):
        self.completion_time = datetime.now()
        self.action_duration = self.completion_time.calc_timedelta_diff(self.start_time)