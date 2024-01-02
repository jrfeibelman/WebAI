from numpy import uint8, uint16, float32
from numpy.random import normal
from datetime import datetime, timedelta
from typing import Dict, List
from random import choice

from rtai.utils.logging import log_transcript, log_debug
from rtai.agent.persona import Persona
from rtai.llm.llm_client import LLMClient
from rtai.agent.agent_event.action import Action
from rtai.agent.agent_event.chat import Chat
from rtai.world.clock import WorldClock

class ShortTermMemory:
    # Factor to determine temporal order of events so agents don't perceive same events at each timestep
    retention: uint16
    # Persona - core identity of agent
    persona: Persona
    # LLM interfacing client
    llm_client: LLMClient

    world_clock: WorldClock

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
                "6:30 AM: Wake up and get washed up",
                "7:00 AM: Cook and eat breakfast",
                "7:30 AM: Attend work",
                "9:00 AM: Attend work",
                "10:00 AM: Attend work",
                "11:00 AM: Attend work",
                "12:00 PM: Get lunch at work",
                "01:00 PM: Attend work",
                "02:00 PM: Attend work",
                "03:00 PM: Attend work",
                "04:00 PM: Attend work",
                "05:00 PM: Pick up daughter from school",
                "05:30 PM: Get more groceries
                "06:00 PM: Go home and cook dinner",
                "07:00 PM: Have dinner with Dolores",
                "08:00 PM: Patrol the streets of New York City for crime",
                "09:00 PM: Patrol the streets of New York City for crime",
                "10:00 PM: Patrol the streets of New York City for crime",
                "11:00 PM: Patrol the streets of New York City for crime",
                "12:00 AM: Go home and to bed",
            ]
    TODO:
        - should some DSL be leveraged if we are going to map text based plans to actions in immersive sim (ie Wake Up, Wash Up, Cook Breakfast, etc)
            - There is a lot of common tasks that might be done across different agents, create interface for hooks/callbacks from different actions
            over maybe some channel over API, then hook up front end to it?
    """
    daily_schedule: List[str]
    daily_completed: List[str]

    # Current action or chatting fields
    current_action: Action
    chatting_with: str # TODO fix type
    current_chat: Chat

    def __init__(self, persona: Persona, llm_client: LLMClient, world_clock: WorldClock):
        self.retention = 5
        self.persona = persona
        self.llm_client = llm_client
        self.world_clock = world_clock

        self.concept_forget = 100
        self.daily_reflection_time = 60 * 3
        self.daily_reflection_size = 5
        self.thought_count = 5

        self.daily_plan = ''
        self.daily_req = []
        self.daily_schedule = []
        self.daily_schedule_idx = 0
        self.daily_completed = []

        self.current_action = Action.new_empty_action()
        self.chatting_with = None # TODO
        self.current_chat = Action.new_empty_action() # TODO

    def add_new_action(self, 
                        action_address: str, 
                        action_start_time: datetime,
                        action_duration : timedelta,
                        action_description: str,
                        action_event: str): 
        self.act_description = action_description
        self.act_event = action_event
        self.act_start_time = self.world_clock.get_time_raw()
        self.current_action.reset_with(address=action_address, start_time=action_start_time, duration=action_duration)


    def get_act_time_str(self) -> str: 
        return self.act_start_time.strftime("%H:%M %p")

    def has_action_completed(self) -> bool: 
        """ TODO
        Checks whether the self.Action instance has finished.  

        INPUT
        curr_datetime: Current time. If current time is later than the action's
                        start time + its duration, then the action has finished. 
        OUTPUT 
        Boolean [True]: Action has finished.
        Boolean [False]: Action has not finished and is still ongoing.
        """
        if not self.current_action.address:
            return True
        
        end_time = self.current_chat.end_time if self.chatting_with else self.current_action.end_time

        if end_time.strftime('%H:%M:%S %p') == self.world_clock.get_time_str(): 
            return True
        return False
    
    def generate_daily_plan(self) -> None:
        self.daily_plan = self.llm_client.generate_daily_plan()
        log_debug("Agent [%s] generated daily plan: [%s]" % (self.persona.name, self.daily_plan))
    
    def generate_first_daily_plan(self, wake_up_hour) -> None:
        self.daily_plan = self.llm_client.generate_first_daily_plan(wake_up_hour)
        log_debug("Agent [%s] generated first daily plan: [%s]" % (self.persona.name, self.daily_plan))

    def generate_daily_req(self) -> None:
        self.daily_req = self.llm_client.generate_daily_req()
        log_debug("Agent [%s] generated daily requirements: [%s]" % (self.persona.name, self.daily_req))

    def generate_hourly_schedule(self, wake_up_hour) -> None:
        self.daily_schedule = self.llm_client.generate_daily_schedule(wake_up_hour)
        log_debug("Agent [%s] generated hourly schedule: [%s]" % (self.persona.name, self.daily_schedule))

    def generate_wake_up_hour(self) -> str:
        """
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
        """
        Summarize the current action as a dictionary. 
        """
        exp = dict()
        exp["persona"] = self.name
        exp["address"] = self.current_action.address
        exp["start_datetime"] = self.current_action.start_time
        exp["duration"] = self.current_action.duration
        exp["description"] = self.current_action.description
        return exp
    
    def get_action_summary_str(self) -> str:
        """
        Summarize the current action as a string.
        """
        start_datetime_str = self.current_action.start_time.strftime("%A %B %d -- %H:%M %p")
        ret = f"[{start_datetime_str}]\n"
        ret += f"Activity: {self.name} is {self.current_action.description}\n"
        ret += f"Address: {self.current_action.address}\n"
        ret += f"Duration in minutes (e.g., x min): {str(self.current_action.duration)} min\n"
        return ret

    def save_to_file(self, file_name: str):
        pass

    def load_from_file(self, file_name: str):
        pass