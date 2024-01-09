from numpy import uint8, uint16, float32
from numpy.random import normal
from typing import Dict, List, Tuple
from random import choice

from rtai.utils.logging import log_transcript, debug, warn
from rtai.agent.persona import Persona
from rtai.agent.behavior.action import Action
from rtai.agent.behavior.chat import Chat
from rtai.world.clock import clock
from rtai.utils.datetime import datetime, timedelta

from rtai.llm.llm_client import LLMClient

class ShortTermMemory:
    """_summary_ Class to represent the short term memory of an agent."""
    # Factor to determine temporal order of events so agents don't perceive same events at each timestep
    retention: uint16
    # Persona - core identity of agent
    persona: Persona
    # LLM interfacing client
    llm_client: LLMClient

    # Reflection variables
    concept_forget: uint16
    daily_reflection_time: uint16
    daily_reflection_size: uint8
    thought_count: uint16

    """ daily_req: Perceived world daily requirement
            Example:
                'Get more groceries, attend work at Goliath National Bank, have dinner with Dolores, pick up daughter from school, patrol the streets of New York City for crime'
    """
    daily_req: str

    """ daily_plan: High level plan for the day
            Example:
            [
                "Wake up", 
                "Get washed up",
                "Cook and eat breakfast",
                "Attend work",
                "Get lunch at work",
                "Pick up daughter from school",
                "Get more groceries",
                "Go home and cook dinner",
                "Have dinner with Dolores",
                "Patrol the streets of New York City for crime",
                "Go home and to bed",
            ]
    """
    daily_plan: List[str]

    """ daily_schedule: Tentative hourly schedule of activities for the day
        - Is this even necessary? Maybe have heirarchy of event importance, snapping most important events to times and scheduling less important events in between them?
            Example:
            [
                ("6:30 AM", "0.5", "Wake up and get washed up"),
                ("7:00 AM", "0.5", "Cook and eat breakfast"),
                ("7:30 AM", "8.5", "Attend work"),
                ("04:00 PM", "0.5", "Pick up daughter from school"),
                ("04:30 PM", "0.5", "Get more groceries"),
                ("05:00 PM", "1.0", "Go home and cook dinner"),
                ("06:00 PM", "1.0", "Have dinner with Dolores"),
                ("07:00 PM", "5.0", "Patrol the streets of New York City for crime"),
                ("12:00 AM", "0.0", "Go home and to bed"),
            ]
    TODO:
        - should some DSL be leveraged if we are going to map text based plans to actions in immersive sim (ie Wake Up, Wash Up, Cook Breakfast, etc)
            - There is a lot of common tasks that might be done across different agents, create interface for hooks/callbacks from different actions
            over maybe some channel over API, then hook up front end to it?
    """
    daily_schedule: List[Tuple[str]]
    daily_completed: List[str]

    # Current action or chatting fields
    current_action: Action
    chatting_with: str # TODO fix type
    current_chat: Chat

    agent_id: uint16

    def __init__(self, agent_id: uint16, persona: Persona, llm_client: LLMClient):
        """_summary_ Constructor for an agent's short term memory.

        Args:
            persona (Persona): persona of the agent
            llm_client (LLMClient): LLM interfacing client
        """
        self.retention = 5
        self.agent_id = agent_id
        self.persona = persona
        self.llm_client = llm_client

        self.concept_forget = 100
        self.daily_reflection_time = 60 * 3
        self.daily_reflection_size = 5
        self.thought_count = 5

        self.daily_plan = ''
        self.daily_req = []
        self.daily_schedule = []
        self.daily_schedule_idx = 0
        self.daily_completed = []

        # TODO need functionality to pause an action and possibly resume it later
        # Some actions are core actions and others are fixed time actions
        self.current_action = Action(None, None, None, None)
        self.chatting_with = ''
        self.current_chat = Chat(None, None, None, None, None)

    def add_new_chat(self, 
                    action_address: str, 
                    action_start_time: datetime,
                    action_duration : timedelta,
                    action_description: str) -> Chat:
        """_summary_ Function to create a new chat

        Args:
            action_address (str): address of chat
            action_start_time (datetime): start time of chat
            action_duration (timedelta): duration of chat
            action_description (str): description of chat
        Returns:
            Chat: created Chat object
        """
        return Chat(description=action_description, creator_id=self.agent_id, address=action_address, start_time=action_start_time, duration=action_duration)

    def add_new_action(self, 
                        action_address: str, 
                        action_start_time: datetime,
                        action_duration : timedelta,
                        action_description: str) -> Action:
        """_summary_ Function to create a new action

        Args:
            action_address (str): address of action
            action_start_time (datetime): start time of action
            action_duration (timedelta): duration of action
            action_description (str): description of action
        Returns:
            Action: created Action object
        """
        return Action(description=action_description, address=action_address, start_time=action_start_time, duration=action_duration)

    def get_act_time_str(self) -> str:
        """_summary_ Get the start time of the current action as a string.

        Returns:
            str: start time of the current action as a string
        """
        return self.act_start_time.strftime("%H:%M %p")

    def has_action_completed(self) -> bool: 
        """_summary_ Checks whether the current Action instance has finished. 
        
        Returns:
            bool: True if the current action has completed, False otherwise
        """
        if not self.current_action.address:
            return True

        end_time = self.current_chat.end_time if len(self.chatting_with) > 0 else self.current_action.end_time
        if end_time <= clock.peek():
            debug("Action [%s] with end time [%s] completed at world time [%s]" % (self.current_action.description, end_time, clock.peek()))
            return True
        return False
    
    def generate_daily_plan(self) -> None:
        """_summary_ Generate a daily plan for the agent.

        Construct daily schedule according to format List[Tuple[str, str, str]] where each tuple is (task, duration, start_time)
        """
        self.daily_plan = self.llm_client.generate_daily_plan(self.persona)
        # self.daily_schedule_idx = 0
        debug("Agent [%s] generated daily plan: [%s]" % (self.persona.name, self.daily_plan))
    
    def generate_first_daily_plan(self, wake_up_hour: str='') -> None:
        """_summary_ Generate a daily plan for the agent for the first day of the simulation.

        Args:
            wake_up_hour (str): time to wake up for the day
        """
        warn("Generate First Daily Plan called but not yet implemented")
        return self.generate_daily_plan()
        # self.daily_plan = generate_daily_plan(self.persona)
        # # self.daily_plan = self.llm_client.generate_first_daily_plan(wake_up_hour)
        # self.daily_schedule_idx = 0
        # debug("Agent [%s] generated first daily plan: [%s]" % (self.persona.name, self.daily_plan))

    def generate_daily_req(self) -> None:
        """_summary_ Generate the daily requirements for the agent.
        """
        self.daily_req = generate_daily_plan(self.persona)
        # self.daily_req = self.llm_client.generate_daily_req()
        debug("Agent [%s] generated daily requirements: [%s]" % (self.persona.name, self.daily_req))

    def generate_hourly_schedule(self, persona: Persona, wake_up_hour) -> None:
        """_summary_ Generate an hourly schedule for the agent.

        Args:
            persona (Persona): persona of the agent
            wake_up_hour (str): time to wake up for the day
        """
        self.daily_schedule = self.llm_client.generate_daily_schedule(persona=persona)
        debug("Agent [%s] generated hourly schedule: [%s]" % (self.persona.name, self.daily_schedule))

    def generate_wake_up_hour(self) -> str:
        """ _summary_ Generate a time to wake up for the day.

        Returns:
            str: time to wake up for the day

        Generate a time to wake up for the day --> average around 8:00 am
        Hour will be 5-11 and minutes will be 0 or 30
        Chooses time using normal distribution centered around 8 and a random choice to make it half past
        """
        generated_number = normal(8, 1)

        hours = [i for i in range(5,12)]
        hour = min(hours, key=lambda x: abs(x - generated_number))
        half_past_bool = choice([True, False])

        hour_str = "0%s" if hour < 10 else "%s"

        return "%s:%s AM" % (hour_str, "30" if half_past_bool else "00")
    
    def get_action_summary_dict(self) -> Dict[str, str]:
        """ _summary_ Get summary of the current action as a dictionary.

        Returns:
            Dict[str, str]: summary of the current action as a dictionary
        """
        exp = dict()
        exp["persona"] = self.name
        exp["address"] = self.current_action.address
        exp["start_datetime"] = self.current_action.start_time
        exp["duration"] = self.current_action.duration
        exp["description"] = self.current_action.description
        return exp
    
    def get_action_summary_str(self) -> str:
        """ _summary_ Get summary of the current action as a string.

        Returns:
            str: summary of the current action as a string
        """
        start_datetime_str = self.current_action.start_time.strftime("%A %B %d -- %H:%M %p")
        ret = f"[{start_datetime_str}]\n"
        ret += f"Activity: {self.name} is {self.current_action.description}\n"
        ret += f"Address: {self.current_action.address}\n"
        ret += f"Duration in minutes (e.g., x min): {str(self.current_action.duration)} min\n"
        return ret

    def save_to_file(self, file_path: str) -> None:
        """_summary_ Save the short term memory to a file.

        Args:
            file_path (str): path to the file to write short term memory to
        """
        pass

    def load_from_file(self, file_name: str) -> bool:
        """_summary_ Load the short term memory from a file.

        Args:
            file_name (str): name of the file to load short term memory from

        Returns:
            bool: True if the short term memory was loaded successfully, False otherwise
        """
        pass