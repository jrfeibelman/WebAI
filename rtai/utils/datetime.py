from datetime import datetime as pydatetime, timedelta as pytimedelta
from typing import TypeAlias

timedelta: TypeAlias = pytimedelta

def now_str() -> str:
    """ _summary_ Get a string representation of the current UTC time 
    
    Returns:
        str: string representation of the current UTC time
    """
    return pydatetime.utcnow().strftime("%m%d%Y_%H:%M:%S")

class datetime:
    """ _summary_ Wrapper class for working with datetime objects """

    @classmethod
    def now(cls) -> 'datetime':
        """ _summary_ Factory method to generate a datetime object with the current UTC time
        
        Returns:
            datetime: datetime object with the current UTC time
        """
        o = cls.__new__(cls)
        o._data: pydatetime = pydatetime.utcnow()
        return o
    
    @classmethod
    def strptime(cls, datetime_str: str, format: str='%Y-%m-%d %I:%M:%S %p') -> 'datetime':
        """ _summary_ Factory method to generate a datetime object from a string
        
        Args:
            datetime_str (str): string representation of the datetime
            format (str, optional): format of the datetime string. Defaults to '%Y-%m-%d %I:%M:%S %p'.
            
        Returns:
            datetime: datetime object from the input string
        """
        o = cls.__new__(cls)
        o._data = pydatetime.strptime(datetime_str, format)
        return o
    
    def copy(self) -> 'datetime':
        """ _summary_ Copy the datetime object
        
        Returns:
            datetime: copy of the datetime object
        """
        return datetime(self)

    def __init__(self, other: 'datetime'):
        """ _summary_ Constructor for the datetime object
        
        Args:
            other (datetime): datetime object to copy
        """
        self._data = other._data

    def get_time_str(self) -> str:
        """ _summary_ Get a string representation of the time

        Returns:
            str: string representation of the time
        """
        return self._data.strftime("%I:%M:%S %p")

    def get_date_str(self) -> str:
        """ _summary_ Get a string representation of the date

        Returns:
            str: string representation of the date
        """
        return self._data.strftime("%Y-%m-%d")

    def get_datetime_str(self, show_seconds: bool=True) -> str:
        """ _summary_ Get a string representation of the datetime
        
        Args:
            show_seconds (bool, optional): whether or not to show the seconds. Defaults to True.
        """
        return self._data.strftime("%Y-%m-%d %I:%M:%S %p") if show_seconds else self._data.strftime("%Y-%m-%d %I:%M %p")

    def get_date_with_time_str(self, time_str: str) -> str:
        """ _summary_ Get a string representation of the datetime with the input time
        
        Args:
            time_str (str): time string to append to the date
        """
        return f"{self.get_date_str()} {time_str}"
    
    def increment_by(self, seconds: int) -> None:
        """ _summary_ Increment the datetime by the input number of seconds
        
        Args:
            seconds (int): number of seconds to increment by
        """
        self._data += timedelta(seconds=seconds)
        # self._data += timedelta64(1, 's')

    def increment_minute(self) -> None:
        """ _summary_ Increment the datetime by 1 minute """
        self._data += timedelta(minutes=1)
        # self._data += timedelta64(1, 'm')

    def increment_time(self, hours: int=0, minutes: int=0) -> None:
        """ _summary_ Increment the datetime by the input number of hours and minutes
        
        Args:
            hours (int, optional): number of hours to increment by. Defaults to 0.
            minutes (int, optional): number of minutes to increment by. Defaults to 0.
        """
        self._data += timedelta(hours=hours, minutes=minutes)
        # self._data += timedelta64(hours, 'h') + timedelta64(minutes, 'm')

    def get_timedelta_from_time_str(self, time_str: str) -> timedelta:
        """ _summary_ Get a timedelta object from the input time string
        
        Args:
            time_str (str): time string to convert to timedelta
            
        Returns:
            timedelta: timedelta object from the input time string
        """
        return pydatetime.strptime(time_str, "%I:%M %p").replace(month=self._data.month, day=self._data.day, year=self._data.year) - self._data

    def get_datetime_raw(self) -> pydatetime:
        """ _summary_ Get the raw datetime object
        
        Returns:
            datetime: raw datetime object"""
        return self._data
    
    def replace_time(self, seconds: int=None, minutes: int=None, hours: int=None) -> None:
        """ _summary_ Replace the time of the datetime with the input values
        
        Args:
            seconds (int, optional): seconds to replace the time with. Defaults to None.
            minutes (int, optional): minutes to replace the time with. Defaults to None.
            hours (int, optional): hours to replace the time with. Defaults to None.
        """
        if seconds:
            self._data = self._data.replace(second=seconds)
        if minutes:
            self._data = self._data.replace(minute=minutes)
        if hours:
            self._data = self._data.replace(hour=hours)

    def calc_timedelta_diff(self, other: 'datetime') -> timedelta:
        """ _summary_ Calculate the timedelta difference between the input datetime and the current datetime
        
        Args:
            other (datetime): datetime to calculate the timedelta difference with
            
        Returns:
            timedelta: timedelta difference between the input datetime and the current datetime
        """
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
