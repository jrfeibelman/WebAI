from datetime import datetime as pydatetime, timedelta as pytimedelta
from typing import TypeAlias

timedelta: TypeAlias = pytimedelta

def now_str():
    return pydatetime.utcnow().strftime("%m%d%Y_%H:%M:%S")

class datetime():
    _data: pydatetime

    @classmethod
    def now(cls):
        o = cls.__new__(cls)
        o._data = pydatetime.utcnow()
        return o
    
    @classmethod
    def strptime(cls, datetime_str: str, format: str='%Y-%m-%d %I:%M:%S %p'):
        o = cls.__new__(cls)
        o._data = pydatetime.strptime(datetime_str, format)
        return o
    
    def copy(self) -> 'datetime':
        return datetime(self)

    def __init__(self, other: 'datetime'):
        self._data = other._data

    def get_time_str(self) -> str:
        return self._data.strftime("%I:%M:%S %p")

    def get_date_str(self) -> str:
        return self._data.strftime("%Y-%m-%d")

    def get_datetime_str(self, show_seconds: bool=True) -> str:
        return self._data.strftime("%Y-%m-%d %I:%M:%S %p") if show_seconds else self._data.strftime("%Y-%m-%d %I:%M %p")

    def get_date_with_time_str(self, time_str: str) -> str:
        return f"{self.get_date_str()} {time_str}"
    
    def increment_by(self, seconds: int) -> None:
        self._data += timedelta(seconds=seconds)
        # self._data += timedelta64(1, 's')

    def increment_minute(self) -> None:
        self._data += timedelta(minutes=1)
        # self._data += timedelta64(1, 'm')

    def increment_time(self, hours: int=0, minutes: int=0) -> None:
        self._data += timedelta(hours=hours, minutes=minutes)
        # self._data += timedelta64(hours, 'h') + timedelta64(minutes, 'm')

    def get_timedelta_from_time_str(self, time_str: str) -> timedelta:
        return pydatetime.strptime(time_str, "%I:%M %p").replace(month=self._data.month, day=self._data.day, year=self._data.year) - self._data

    def get_datetime_raw(self) -> 'datetime':
        return self._data
    
    def replace_time(self, seconds: int=None, minutes: int=None, hours: int=None) -> None:
        if seconds:
            self._data = self._data.replace(second=seconds)
        if minutes:
            self._data = self._data.replace(minute=minutes)
        if hours:
            self._data = self._data.replace(hour=hours)

    def calc_timedelta_diff(self, other: 'datetime') -> timedelta:
        return self._data - other._data

    def __eq__(self, other: 'datetime') -> bool:
        return self._data == other._data

    def __lt__(self, other: 'datetime') -> bool:
        return self._data < other._data
    
    def __le__(self, other: 'datetime') -> bool:
        return self == other or self < other

    def __str__(self) -> str:
        return self.get_datetime_str()
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __add__(self, other: timedelta) -> 'datetime':
        o = datetime(self)
        o._data += other
        return o
    
#     _data: datetime64

#     @classmethod
#     def now(cls):
#         o = cls.__new__(cls)
#         o._data = datetime64(dt.utcnow())
#         return o

#     def __init__(self, datetime_str: str):
#         self._data = datetime64(datetime_str)

#     def get_time_str(self) -> str:
#         return dt.utcfromtimestamp(self._data.astype('datetime64[m]')/1e9).strftime("%H:%M:%S")

#     def get_date_str(self) -> str:
#         return dt.utcfromtimestamp(self._data.astype('datetime64[0]')/1e9).strftime("%Y-%m-%d")

#     def get_datetime_str(self) -> str:
#         return dt.utcfromtimestamp(self._data.astype('datetime64[0]')/1e9).strftime("%Y-%m-%d %H:%M:%S")

#     def get_date_with_time_str(self, time_str: str) -> str:
#         date_str = self.get_date_str()
#         return f"{date_str} {time_str}"

#     def __str__(self) -> str:
#         return self.get_datetime_str()

#     def increment_minute(self) -> None:
#         self._data += timedelta64(1, 'm')

#     def increment_by(self, hours: int, minutes: int) -> None:
#         self._data += timedelta64(hours, 'h') + timedelta64(minutes, 'm')

#     def get_time_raw(self):
#         return self._data.astype('M8[m]')

#     def get_date_raw(self):
#         return self._data.astype('M8[D]')

#     def get_datetime_raw(self) -> datetime64:
#         return self._data

#     def __eq__(self, other):
#         return self._data == other._data

#     def __lt__(self, other):
#         return self._data < other._data
