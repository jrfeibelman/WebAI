from datetime import datetime as dt
from numpy import datetime64, timedelta64

class datetime():
    _data: dt # datetime64

    @classmethod
    def now(cls):
        o = cls.__new__(cls)
        # o._data = datetime64(dt.utcnow())
        o._data = dt.utcnow()
        return o

    def __init__(self, datetime_str: str):
        self._data = datetime64(datetime_str)

    def get_time_str(self):
        pass

    def get_date_str(self):
        pass

    def __str__(self) -> str:
        pass

    def increment_minute(self):
        a = timedelta64(1, 'Y')

    def increment_by(self, increment):
        pass

    def __eq__(self, other: datetime):
        self._data == other._data

    def __lt__(self):
        pass