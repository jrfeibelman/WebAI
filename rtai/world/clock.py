from numpy import uint16

from rtai.utils.timer_manager import TimerManager
from rtai.utils.datetime import datetime as mydatetime
from rtai.utils.logging import info
from rtai.utils.config import Config

SEC_PER_HALF_DAY = 43200

class WorldClock:
    """
    Class to represent the simulation world's date/time 
    
    Maybe using an entire datetime object ....
    """

    day_counter: uint16
    # mins_since_last_update: uint16
    time: uint16
    clock: mydatetime
    is_am: bool
    # world_date_str: str


    # StartDate: '2024-01-01'
    # StartTime: '05:00 AM'
    # ClockIncrementSec: 20 # Amount that clock is incremented by each cycle
    # ClockTimerMillis: 1000 # Amount of time between clock increments

    def __init__(self, config: Config):

        # Start world clock at 5 am
        self.clock = mydatetime.strptime('%s %s' % (config['StartDate'], config['StartTime']))
        self.clock_increment = int(config['ClockIncrementSec'])

        # Tracks number of seconds that have passed in a given day
        self.time = uint16(60*60*5)
        self.is_am = True

        # Tracks number of days that have passed since clock was created
        self.day_counter = uint16(0)

        # Tracks number of minutes that have passed since lasted updated the clock field
        # self.mins_since_last_update = uint16(0)

        # self.world_date_str = self.world_date.strftime("%A %B %d, %Y")

    @TimerManager.timer_callback
    def tick(self) -> None:
        """
        Increments the world clock by one minute
        """
        self.time += self.clock_increment
        
        # self.mins_since_last_update += 1
        self.clock.increment_by(self.clock_increment)
        info("TIME : %s " % self.clock.get_datetime_str())
        if self.time >= 43200:
            if self.is_am:
                # AM -> PM
                self.is_am = False
            else:
                # NEW DAY
                self.is_am = True
                self.day_counter += 1
                info("New Day: %s" % self.clock.get_datetime_str())
            
            self.time = 0



        # self.mins_since_last_update = 0# TODO delete

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