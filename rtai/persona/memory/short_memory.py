from numpy import uint8, uint16, float32
from numpy.random import normal
from datetime import datetime
from typing import Dict, List
from random import choice

from rtai.persona.persona import Persona

class ShortTermMemory:
    # Factor to determine temporal order of events so agents don't perceive same events at each timestep
    retention: uint16
    # Perceived world time
    curr_time: datetime
    # Perceived world daily requirement. 
    daily_plan: str
    # Persona - core identity of agent
    persona: Persona

    # REFLECTION VARIABLES
    concept_forget: uint16
    daily_reflection_time: uint16
    daily_reflection_size: uint8
    overlap_reflect_th: uint8
    kw_strg_event_reflect_th: uint8
    kw_strg_thought_reflect_th: uint8
    recency_w: float32
    relevance_w: float32
    importance_w: float32
    recency_decay: float32
    importance_trigger_max: uint16
    importance_trigger_curr: uint16
    importance_ele_n: uint16
    thought_count: uint16

    # # PERSONA PLANNING
    # # <daily_req> is a list of various goals the persona is aiming to achieve
    # # today. 
    # # e.g., ['Work on her paintings for her upcoming show', 
    # #        'Take a break to watch some TV', 
    # #        'Make lunch for herself', 
    # #        'Work on her paintings some more', 
    # #        'Go to bed early']
    # # They have to be renewed at the end of the day, which is why we are
    # # keeping track of when they were first generated. 
    # daily_req = []
    # # <f_daily_schedule> denotes a form of long term planning. This lays out 
    # # the persona's daily plan. 
    # # Note that we take the long term planning and short term decomposition 
    # # appoach, which is to say that we first layout hourly schedules and 
    # # gradually decompose as we go. 
    # # Three things to note in the example below: 
    # # 1) See how "sleeping" was not decomposed -- some of the common events 
    # #    really, just mainly sleeping, are hard coded to be not decomposable.
    # # 2) Some of the elements are starting to be decomposed... More of the 
    # #    things will be decomposed as the day goes on (when they are 
    # #    decomposed, they leave behind the original hourly action description
    # #    in tact).
    # # 3) The latter elements are not decomposed. When an event occurs, the
    # #    non-decomposed elements go out the window.  
    # # e.g., [['sleeping', 360], 
    # #         ['wakes up and ... (wakes up and stretches ...)', 5], 
    # #         ['wakes up and starts her morning routine (out of bed )', 10],
    # #         ...
    # #         ['having lunch', 60], 
    # #         ['working on her painting', 180], ...]
    # f_daily_schedule = []
    # # <f_daily_schedule_hourly_org> is a replica of f_daily_schedule
    # # initially, but retains the original non-decomposed version of the hourly
    # # schedule. 
    # # e.g., [['sleeping', 360], 
    # #        ['wakes up and starts her morning routine', 120],
    # #        ['working on her painting', 240], ... ['going to bed', 60]]
    # f_daily_schedule_hourly_org = []

    # # CURR ACTION 
    # # <address> is literally the string address of where the action is taking 
    # # place.  It comes in the form of 
    # # "{world}:{sector}:{arena}:{game_objects}". It is important that you 
    # # access this without doing negative indexing (e.g., [-1]) because the 
    # # latter address elements may not be present in some cases. 
    # # e.g., "dolores double studio:double studio:bedroom 1:bed"
    # act_address = None
    # # <start_time> is a python datetime instance that indicates when the 
    # # action has started. 
    # act_start_time: datetime
    # # <duration> is the integer value that indicates the number of minutes an
    # # action is meant to last. 
    # act_duration = None
    # # <description> is a string description of the action. 
    # act_description = None
    # # <pronunciatio> is the descriptive expression of the description. 
    # # Currently, it is implemented as emojis. 
    # act_pronunciatio = None
    # # <event_form> represents the event triple that the persona is currently 
    # # engaged in. 
    # act_event = (persona.name, None, None)

    # # <obj_description> is a string description of the object action. 
    # act_obj_description = None
    # # <obj_pronunciatio> is the descriptive expression of the object action. 
    # # Currently, it is implemented as emojis. 
    # act_obj_pronunciatio = None
    # # <obj_event_form> represents the event triple that the action object is  
    # # currently engaged in. 
    # act_obj_event = (persona.name, None, None)

    # # <chatting_with> is the string name of the persona that the current 
    # # persona is chatting with. None if it does not exist. 
    # chatting_with = None
    # # <chat> is a list of list that saves a conversation between two personas.
    # # It comes in the form of: [["Dolores Murphy", "Hi"], 
    # #                           ["Maeve Jenson", "Hi"] ...]
    # chat = None
    # # <chatting_with_buffer>  
    # # e.g., ["Dolores Murphy"] = vision_r
    # chatting_with_buffer: dict
    # chatting_end_time: datetime

    def __init__(self, persona: Persona):
        self.retention = 5
        self.curr_time = None
        self.daily_plan = None
        self.persona = persona

        self.concept_forget = 100
        self.daily_reflection_time = 60 * 3
        self.daily_reflection_size = 5
        self.overlap_reflect_th = 2
        self.kw_strg_event_reflect_th = 4
        self.kw_strg_thought_reflect_th = 4
        self.recency_w = 1
        self.relevance_w = 1
        self.importance_w = 1
        self.recency_decay = 0.99
        self.importance_trigger_max = 150
        self.importance_trigger_curr = self.importance_trigger_max
        self.importance_ele_n = 0 
        self.thought_count = 5

        self.daily_req = []
        self.f_daily_schedule = []
        self.f_daily_schedule_hourly_org = []

        self.act_address = None
        self.act_start_time = None
        self.act_duration = None
        self.act_description = None
        self.act_pronunciatio = None
        self.act_event = (self.persona.name, None, None)
        self.act_obj_description = None
        self.act_obj_pronunciatio = None
        self.act_obj_event = (self.persona.name, None, None)
        self.chatting_with = None
        self.chat = None
        self.chatting_with_buffer = dict()
        self.chatting_end_time = None

    def get_str_iss(self): 
        """
        Taken from reverie simularca:

        ISS stands for "identity stable set." This describes the commonset summary
        of this persona -- basically, the bare minimum description of the persona
        that gets used in almost all prompts that need to call on the persona. 

        INPUT
        None
        OUTPUT
        the identity stable set summary of the persona in a string form.
        EXAMPLE STR OUTPUT
        "Name: Dolores Heitmiller
        Age: 28
        Innate traits: hard-edged, independent, loyal
        Learned traits: Dolores is a painter who wants live quietly and paint 
            while enjoying her everyday life.
        Currently: Dolores is preparing for her first solo show. She mostly 
            works from home.
        Lifestyle: Dolores goes to bed around 11pm, sleeps for 7 hours, eats 
            dinner around 6pm.
        Daily plan requirement: Dolores is planning to stay at home all day and 
            never go out."
        """
        commonset = ""
        commonset += f"Name: {self.name}\n"
        commonset += f"Age: {self.age}\n"
        commonset += f"Innate traits: {self.innate}\n"
        commonset += f"Learned traits: {self.learned}\n"
        commonset += f"Currently: {self.currently}\n"
        commonset += f"Lifestyle: {self.lifestyle}\n"
        commonset += f"Daily plan requirement: {self.daily_plan}\n"
        commonset += f"Current Date: {self.curr_time.strftime('%A %B %d')}\n"
        return commonset

    def add_new_action(self, 
                        action_address, 
                        action_duration,
                        action_description,
                        action_pronunciatio, 
                        action_event,
                        chatting_with, 
                        chat, 
                        chatting_with_buffer,
                        chatting_end_time,
                        act_obj_description, 
                        act_obj_pronunciatio, 
                        act_obj_event, 
                        act_start_time=None): 
        self.act_address = action_address
        self.act_duration = action_duration
        self.act_description = action_description
        self.act_pronunciatio = action_pronunciatio
        self.act_event = action_event

        self.chatting_with = chatting_with
        self.chat = chat 
        if chatting_with_buffer: 
            self.chatting_with_buffer.update(chatting_with_buffer)
        self.chatting_end_time = chatting_end_time

        self.act_obj_description = act_obj_description
        self.act_obj_pronunciatio = act_obj_pronunciatio
        self.act_obj_event = act_obj_event
        
        self.act_start_time = self.curr_time # KEEP
        
        self.act_path_set = False

    def get_act_time_str(self) -> str: 
        return self.act_start_time.strftime("%H:%M %p")

    def has_action_completed(self) -> bool: 
        """
        Checks whether the self.Action instance has finished.  

        INPUT
        curr_datetime: Current time. If current time is later than the action's
                        start time + its duration, then the action has finished. 
        OUTPUT 
        Boolean [True]: Action has finished.
        Boolean [False]: Action has not finished and is still ongoing.
        """
        if not self.act_address:
            return True
        
        if self.chatting_with: 
            end_time = self.chatting_end_time
        else: 
            x = self.act_start_time
            if x.second != 0: 
                x = x.replace(second=0)
                x = (x + datetime.timedelta(minutes=1))
            end_time = (x + datetime.timedelta(minutes=self.act_duration))

        if end_time.strftime("%H:%M:%S") == self.curr_time.strftime("%H:%M:%S"): 
            return True
        return False
    
    def generate_daily_plan(self):
        pass

    def generate_first_daily_plan(self, wake_up_hour):
        """ * Uses LLM
        TODO Generate daily plan fir the first day
        """
        pass

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
        exp["address"] = self.act_address
        exp["start_datetime"] = self.act_start_time
        exp["duration"] = self.act_duration
        exp["description"] = self.act_description
        exp["pronunciatio"] = self.act_pronunciatio
        return exp
    
    def get_action_summary_str(self) -> str:
        """
        Summarize the current action as a string.
        """
        start_datetime_str = self.act_start_time.strftime("%A %B %d -- %H:%M %p")
        ret = f"[{start_datetime_str}]\n"
        ret += f"Activity: {self.name} is {self.act_description}\n"
        ret += f"Address: {self.act_address}\n"
        ret += f"Duration in minutes (e.g., x min): {str(self.act_duration)} min\n"
        return ret

    def save_to_file(self, file_name: str):
        pass

    def load_from_file(self, file_name: str):
        pass