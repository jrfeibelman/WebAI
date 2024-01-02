from numpy import uint16
from datetime import date, timedelta, datetime, time

from rtai.utils.timer_manager import TimerManager
# from rtai.utils.datetime import datetime

class WorldClock:
    """
    Class to represent the simulation world's date/time 
    
    Maybe using an entire datetime object ....
    """

    world_clock: uint16
    day_counter: uint16
    world_date: date
    world_date_str: str

    def __init__(self, start_date: date=date.today()):
        # Start world clock at 5 am
        self.world_clock = uint16(300)
        self.day_counter = uint16(0)
        self.world_date = start_date
        self.world_date_str = self.world_date.strftime("%A %B %d, %Y")

    @TimerManager.timer_callback
    def tick(self) -> None:
        """
        Increments the world clock by one minute
        """
        self.world_clock += 1
        if self.world_clock >= 1440:
            self.world_clock = 0
            self.day_counter += 1
            self.world_date += timedelta(days=1)
            self.world_date_str = self.world_date.strftime("%A %B %d, %Y")

    def get_time_str(self) -> str:
        """
        Returns the time as a string object
        """
        return  "%02d:%02d %s" % (self.get_hour() % 12, self.get_minute(), self.get_meridiem())
    
    def get_date_str(self) -> str:
        """
        Returns the date as a string object
        """
        return self.world_date_str
    
    def get_datetime_str(self) -> str:
        """
        Returns the date and time as a string object
        """
        return f'{self.get_date_str()} {self.get_time_str()}'
    
    def get_date_with_time_str(self, time_str: str) -> str:
        """
        Returns the date and provided time as a string object
        """
        return f'{self.get_date_str()} {time_str}'

    def __str__(self) -> str:
        return self.get_datetime_str()
    
    def get_time_raw(self) -> uint16:
        """
        Returns the time as a integer counter representing the number of minutes that occurred since midnight
        """
        return time(self.get_hour(), self.get_minute())
    
    def get_date_raw(self) -> date:
        """
        Returns the date as a date object
        """
        return self.world_date
    
    def get_datetime_raw(self) -> datetime:
        """
        TODO : Returns the date and time as a datetime
        """ 
        return datetime.combine(self.get_date_raw(), self.get_time_raw())

    def get_hour(self) -> uint16:
        """
        Returns the hour of the time in 24-hour format
        """
        return self.world_clock // 60
    
    def get_minute(self) -> uint16:
        """
        Return the minute of the time
        """
        return self.world_clock % 60
    
    def get_meridiem(self) -> str:
        """
        Return the meridiem of the time
        """
        return "AM" if self.get_hour() < 12 else "PM"
    
    def get_day_count(self) -> uint16:
        """
        Return the number of days that have passed since the world clock started
        """
        return self.day_counter