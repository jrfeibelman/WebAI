from rtai.utils.datetime import datetime, timedelta
from rtai.agent.behavior.abstract_behavior import AbstractBehavior

class Action(AbstractBehavior):
    """_summary_ Class to represent an action to be executed by an agent."""

    def __init__(self, description: str, address: str, start_time: datetime, duration: timedelta, end_time: datetime=None):
        """_summary_ Constructor for an action.
        
        Args:
            description (str): Description of the action.
            address (str): Address of the action.
            start_time (datetime): Start time of the action.
            duration (timedelta): Planned duration of the action.
            end_time (datetime, optional): End time of the action. Defaults to None. If None, it is calculated from start_time and duration.
        Returns:
            Action: An action object.
        """
        self.end_time: datetime = self._calc_end_time(start_time=start_time, duration=duration) if start_time and not end_time else end_time
        self.address: str = address
        self.start_time: datetime = start_time
        self.plan_duration: timedelta = duration
        self.description: str = description

        self.completion_time: datetime = None
        self.action_duration: timedelta = None

    def __str__(self) -> str:
        return f"Action [{self.description}]"

    def __repr__(self) -> str:
        return f"Action [{self.description}] start [{self.start_time}] - end [{self.end_time}] --> dur [{self.plan_duration}]"

    def _calc_end_time(self, start_time: datetime, duration: timedelta) -> datetime:
        """_summary_ Calculate the end time of an action.

        Args:
            start_time (datetime): Start time of the action.
            duration (timedelta): Planned duration of the action.
        Returns:
            datetime: End time of the action.
        """
        if start_time._data.second != 0:
            start_time.replace_time(seconds=0)
        return (start_time + duration)
    
    def mark_completed(self) -> None:
        """_summary_ Mark the action as completed and calculate the action duration."""
        self.completion_time = datetime.now()
        self.action_duration = self.completion_time.calc_timedelta_diff(self.start_time)