from datetime import timedelta

from rtai.utils.datetime import datetime
from rtai.agent.agent_event.agent_event import AgentEvent
from rtai.utils.logging import log_debug

class Action(AgentEvent):
    address: str
    description: str
    start_time: datetime
    end_time: datetime
    duration: timedelta

    @classmethod
    def new_empty_action(cls):
        o = cls.__new__(cls)
        o.reset()
        return o
    
    def __init__(self, address: str, start_time: datetime, duration: timedelta, end_time: datetime=None):
        super.__init__()

        self.end_time = self._calc_end_time(start_time=start_time, duration=duration) if end_time is None else end_time
        self.address = address
        self.start_time = start_time
        self.duration = duration

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def __lt__(self, other):
        pass

    def __eq__(self, other):
        pass

    def _calc_end_time(self, start_time: datetime, duration: timedelta) -> datetime:
        if start_time._data.second != 0:
            start_time.replace_time(seconds=0)
            start_time = (start_time + timedelta(minutes=1))
        return (start_time + duration)

    def reset(self) -> None:
        self.address = None
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.description = None

    def reset_with(self, address: str, start_time: datetime, duration: timedelta, description: str, end_time: datetime=None) -> None:
        self.end_time = self._calc_end_time(start_time=start_time, duration=duration) if end_time is None else end_time
        self.address = address
        self.start_time = start_time
        self.duration = duration
        self.description = description
        log_debug(f"Reseating action to [{self.description}], start [{self.start_time}], end [{self.end_time}], duration [{self.duration}]")
