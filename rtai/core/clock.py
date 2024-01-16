from numpy import uint16

from rtai.utils.timer_manager import TimerManager
from rtai.utils.datetime import datetime as mydatetime
from rtai.utils.logging import info
from rtai.utils.config import Config

SEC_PER_HALF_DAY = 43200

class clock:
    """
    Class to represent the simulation world's date/time 
    
    Maybe using an entire datetime object ....
    """

    # Tracks number of days that have passed since clock was created
    day_counter: uint16 = uint16(0)

    clock: mydatetime

    def __new__(cls, config: Config) -> 'clock':
        """ _summary_ Singleton constructor for the world clock"""
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

            # Start world clock at 5 am
            cls.clock = mydatetime.strptime('%s %s' % (config['StartDate'], config['StartTime'])) # static datetime object
            cls._instance.clock_increment = int(config['ClockIncrementSec'])

            # Tracks number of seconds that have passed in a given day
            cls._instance.time = uint16(60*60*5)
            cls._instance.is_am = True

        return cls._instance

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
        
    @classmethod
    def snapshot(cls) -> mydatetime:
        return clock.clock.copy()
    
    @classmethod
    def peek(cls) -> mydatetime:
        return clock.clock

    @classmethod
    def get_time_str(cls) -> str:
        """
        Returns the time as a string object
        """
        # return  "%02d:%02d %s" % (self.get_hour() % 12, self.get_minute(), self.get_meridiem())
        return clock.clock.get_time_str()
    
    @classmethod
    def get_date_str(cls) -> str:
        """
        Returns the date as a string object
        """
        return clock.clock.get_date_str()
    
    @classmethod
    def get_datetime_str(cls) -> str:
        """
        Returns the date and time as a string object
        """
        return clock.clock.get_datetime_str(show_seconds=False)

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
    #     return self.sim_clock // 60
    
    # def get_minute(self) -> uint16:
    #     """
    #     Return the minute of the time
    #     """
    #     return self.sim_clock % 60
    
    # def get_meridiem(self) -> str:
    #     """
    #     Return the meridiem of the time
    #     """
    #     return "AM" if self.get_hour() < 12 else "PM"
    
    @classmethod
    def get_day_count(cls) -> uint16:
        """
        Return the number of days that have passed since the world clock started
        """
        return clock.day_counter