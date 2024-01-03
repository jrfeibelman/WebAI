from numpy import uint16
from datetime import timedelta

from rtai.utils.timer_manager import TimerManager
from rtai.utils.datetime import datetime as mydatetime

class WorldClock:
    """
    Class to represent the simulation world's date/time 
    
    Maybe using an entire datetime object ....
    """

    day_counter: uint16
    mins_since_last_update: uint16
    time: uint16
    clock: mydatetime
    # world_date_str: str

    def __init__(self, start_date: mydatetime=mydatetime.now()):

        # Start world clock at 5 am
        start_date._data = start_date._data.replace(second=0, microsecond=0, hour=5, minute=0)
        self.clock = start_date

        # Tracks number of minutes that have passed in a given day
        self.time = uint16(300)

        # Tracks number of days that have passed since clock was created
        self.day_counter = uint16(0)

        # Tracks number of minutes that have passed since lasted updated the clock field
        self.mins_since_last_update = uint16(0)

        # self.world_date_str = self.world_date.strftime("%A %B %d, %Y")

    @TimerManager.timer_callback
    def tick(self) -> None:
        """
        Increments the world clock by one minute
        """
        self.time += 1
        self.mins_since_last_update += 1
        if self.time >= 1440:
            self.time = 0
            self.day_counter += 1
            self.clock.increment_minute()

        self.clock += timedelta(minutes=1) # TODO delete
        self.mins_since_last_update = 0# TODO delete

            # self.world_date_str = self.world_date.strftime("%A %B %d, %Y")
        
    def snapshot(self) -> mydatetime:
        return self.clock.copy()

    def get_time_str(self) -> str:
        """
        Returns the time as a string object
        """
        # return  "%02d:%02d %s" % (self.get_hour() % 12, self.get_minute(), self.get_meridiem())
        return self.clock.get_time_str()
    
    def get_date_str(self) -> str:
        """
        Returns the date as a string object
        """
        return self.clock.get_date_str()
    
    def get_datetime_str(self) -> str:
        """
        Returns the date and time as a string object
        """
        return self.clock.get_datetime_str(show_seconds=False)

    def __str__(self) -> str:
        return self.get_datetime_str()
    
    # def get_time_raw(self) -> uint16:
    #     """
    #     Returns the time as a integer counter representing the number of minutes that occurred since midnight
    #     """
    #     # return time(self.get_hour(), self.get_minute())
    #     return self.clock.get_time_raw()
    
    # def get_date_raw(self) -> mydatetime:
    #     """
    #     Returns the date as a date object
    #     """
    #     return self.clock.get_date_raw()
    
    # def get_datetime_raw(self) -> mydatetime:
    #     """
    #     TODO : Returns the date and time as a datetime
    #     """ 
    #     return self.clock._data

    # def get_hour(self) -> uint16:
    #     """
    #     Returns the hour of the time in 24-hour format
    #     """
    #     return self.world_clock // 60
    
    # def get_minute(self) -> uint16:
    #     """
    #     Return the minute of the time
    #     """
    #     return self.world_clock % 60
    
    # def get_meridiem(self) -> str:
    #     """
    #     Return the meridiem of the time
    #     """
    #     return "AM" if self.get_hour() < 12 else "PM"
    
    def get_day_count(self) -> uint16:
        """
        Return the number of days that have passed since the world clock started
        """
        return self.day_counter