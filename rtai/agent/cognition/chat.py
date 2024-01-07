from datetime import timedelta
from rtai.utils.datetime import datetime

class Chat:
    address: str
    description: str
    start_time: datetime
    end_time: datetime
    duration: timedelta

    def __init__(self, address: str, start_time: datetime, duration: timedelta, end_time: datetime=None):
        self.end_time = self._calc_end_time(start_time=start_time, duration=duration) if start_time and not end_time else end_time
        self.address = address
        self.start_time = start_time
        self.duration = duration

    def __str__(self):
        return f"Chat [{self.description}]"

    def __repr__(self):
        return f"Chat [{self.description}]"

    def _calc_end_time(self, start_time: datetime, duration: timedelta) -> datetime:
        if start_time._data.second != 0:
            start_time.replace_time(seconds=0)
            start_time = (start_time + timedelta(minutes=1))
        return (start_time + duration)