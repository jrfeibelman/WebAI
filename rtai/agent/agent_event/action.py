from datetime import timedelta, time, datetime

from rtai.agent.agent_event.agent_event import AgentEvent


class Action(AgentEvent):
    address: str
    description: str
    start_time: datetime
    end_time: datetime
    duration: timedelta

    @classmethod
    def new_empty_action(cls):
        o = cls.__new__(cls)
        o.address = None
        o.start_time = None
        o.end_time = None
        o.duration = None
        o.description = None
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
        x = start_time
        if x.second != 0: 
            x = x.replace(second=0)
            x = (x + timedelta(minutes=1))
        return (x + duration)

    def reset(self) -> None:
        self.address = None
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.description = None

    def reset_with(self, address: str, start_time: datetime, duration: timedelta, end_time: datetime=None) -> None:
        self.end_time = self._calc_end_time(start_time=start_time, duration=duration) if end_time is None else end_time
        self.address = address
        self.start_time = start_time
        self.duration = duration