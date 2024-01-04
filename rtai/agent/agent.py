from __future__ import annotations
from time import perf_counter
from datetime import timedelta
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from rtai.agent.agent_manager import AgentManager

from rtai.agent.abstract_agent import AbstractAgent

from rtai.core.event import Event
from rtai.utils.logging import info, debug, log_transcript
from rtai.agent.persona import Persona
from rtai.agent.memory.short_memory import ShortTermMemory
from rtai.agent.memory.long_memory import LongTermMemory
from rtai.utils.datetime import datetime
from rtai.llm.llm_client import LLMClient
from rtai.agent.cognition.agent_concept import AgentConcept
from rtai.agent.cognition.action import Action
from rtai.agent.cognition.cognition import Cognition

class Agent(AbstractAgent):
    """
    Class to represent AI Agent with thoughts and actions generated by LLMs

    TODO:
        Questions:
            - What should AI Agents do? Thoughts --> Actions (within context of environment (environment = narration + other AI agents))
            - Is this too simplistic? Should reveries = thoughts or should reveries be multiple thoughts / skills / plans that lead to a given action?

        Implementation
            - add retriever to trigger generating reverie
    
    
    """
    counter: int = 0
    id: int
    agent_mgr: AbstractAgent
    s_mem: ShortTermMemory
    l_mem : LongTermMemory
    conversations: List[Event]
    persona: Persona
    cognition: Cognition
    # String representation of persona for LLM calls
    common_set: str


    def __init__(self, agent_mgr: AgentManager, client: LLMClient, file_path: str=""):
        """
        Constructor to create a new agent
        INPUT
            agent_mgr: an Agent Manager reference
            file_path: (optional) file to load personality from
        """
        super().__init__()

        self.agent_mgr: AgentManager = agent_mgr
        self.llm_client = client

        self.conversations: List[Event] = []

        Agent.counter += 1
        self.id = Agent.counter
        if len(file_path) == 0:
            self.persona = Persona.generate_from_file('tests/examples/personas/persona%s.txt' % self.id) # TODO use file_path, use LLM to generate personality???
        else:
            self.persona = Persona.generate_from_file(file_path)

        self.s_mem = ShortTermMemory(self.persona, self.llm_client, self.agent_mgr.world_clock)
        self.l_mem = LongTermMemory()
        self.cognition = Cognition(self)

        info("Created Agent [%s]" % self.get_name())

    # def generate_reverie(self) -> Event:
    #     """
    #     Function to leverage LLMs to generate a given thought based on their environment, which influences the actions they take
    #     """
    #     start_time = perf_counter()

    #     # TODO - call LLM to generate reverie
    #     msg = "Test Reverie (%s)" % self.get_name()

    #     elapsed_time = perf_counter() - start_time
    #     info("Agent [%s] took [%s] ms for generate_reverie()" % (self.get_name(), elapsed_time * 1000))

    #     event = Event.create_reverie_event(self, msg)
    #     self.queue.put(event)
    #     # self.memory.append(event)
    #     return event

    # def generate_action(self) -> Event:
    #     """
    #     Function to leverage LLMs to generate a given action based on their environment and reveries
    #     """
    #     start_time = perf_counter()
    #     # TODO - add logic to determine if action or chat, annd chatting functionality
    #     # TODO - call LLM to generate action
    #     msg = "Test Action (%s)" % self.get_name()

    #     elapsed_time = perf_counter() - start_time
    #     info("Agent [%s] took [%s] ms for generate_action()" % (self.get_name(), elapsed_time * 1000))

    #     event = Event.create_action_event(self, msg)
    #     self.queue.put(event)
    #     # self.memory.append(event)
    #     return event
    
    def update(self) -> None:
        self.retrieve(self.perceive())
        debug("Agent [%s] finished update()" % (self.get_name()))

    def perceive(self) -> List:
        """ 
        Create Thoughts (SKIP FOR NOW)
            - Analyze surroundings: perceives events around the persona and saves events to the memory ?
        """
        return [] # TODO

    def retrieve(self, perceived: List) -> None:
        """
        2) Retreive
            From simularca:
                This function takes the events that are perceived by the persona as input
                and returns a set of related events and thoughts that the persona would 
                need to consider as context when planning. 

                INPUT: 
                    perceived: a list of event <ConceptNode>s that represent any of the events
                    `         that are happening around the persona. What is included in here
                            are controlled by the att_bandwidth and retention 
                            hyper-parameters.
                OUTPUT: 
                    retrieved: a dictionary of dictionary. The first layer specifies an event, 
                            while the latter layer specifies the "curr_event", "events", 
                            and "thoughts" that are relevant.
        """
        
        pass # TODO

    def act(self, new_day: bool, first_day: bool=False) -> None:
        """
        Plan --> Create actions????????? or thoughts that lead to actions
            1) If start of day, perform daily agenda creation
            2) If current action expired, create new plan 
            3) If you perceived an event that needs to be responded to, generate action or chat (TODO later)
            4) 
        """
        start_time = perf_counter()

        if new_day or first_day:
            self._create_day_plan(first_day, new_day) # Creates Planning Thought

        # if action expired, create new agenda/plan
        print("[%s] Checking action completion" % self.agent_mgr.world_clock.get_time_str())
        if self.s_mem.has_action_completed():
            print("[%s] Completed action" % self.agent_mgr.world_clock.get_time_str())
            debug("Action [%s] completed at [%s]" % (self.s_mem.current_action.description, self.agent_mgr.world_clock.get_time_str()))
            self._determine_action() # TODO this function needs to generate a new ACTION

        # TODO later - if perceived event that needs to be responded to (such as chat), generate action or chat
            
        # TODO NEIL - call LLM to generate reverie
        # move error handling to the LLM Client? or LLMServer
        # prompt = reverie_prompt(self.persona)
        # response = self.llm_client.generate_from_prompt(system_prompt="You are a story teller.", user_prompt=prompt)

        # log_transcript(self.get_name(), self.agent_mgr.world_clock.get_time_str(), 'Action', response)

        elapsed_time = perf_counter() - start_time
        debug("Agent [%s] took [%s] ms for act()" % (self.get_name(), elapsed_time * 1000))

    def reflect(self) -> None:
        """
        Reflect --> Create Reveries
        """
        start_time = perf_counter()

        # TODO

        elapsed_time = perf_counter() - start_time
        debug("Agent [%s] took [%s] ms for reflect()" % (self.get_name(), elapsed_time * 1000))

    def _determine_action(self) -> Event:
        """ Generate next action sequence here for agent --> call add_new_action
        
        TODO - As a part of this, persona may need to decompose hourly schedule into smaller tasks for long duration events   
        TODO - There might be core events, such as meals and bed time, which are tasks that must be accomplished on a given day
        TODO - There might be fixed events such as work and events shared with other agents, which are tasked that have non-negotiable start times

        Example Hourly Sched:
            ("6:30 AM", "0.5", "Wake up and get washed up"),
            ("7:00 AM", "0.5", "Cook and eat breakfast"),
            ("7:30 AM", "8.5", "Attend work"),
            ("04:00 PM", "0.5", "Pick up daughter from school"),
            ("04:30 PM", "0.5", "Get more groceries"),
            ("05:00 PM", "1.0", "Go home and cook dinner"),
            ("06:00 PM", "1.0", "Have dinner with Dolores"),
            ("07:00 PM", "4.5", "Patrol the streets of New York City for crime"),
            ("11:30 PM", "0.5", "Have conversation with Batman about Joker's latest crime"),
            ("12:00 AM", "0.0", "Go home and go to sleep"),
        """
        action_start: datetime = self.agent_mgr.world_clock.snapshot()

        # Get current index into daily schedule
        if self.s_mem.daily_schedule_idx == 0:
            # Schedule sleep --> Wakeup event
            action_desc = "Sleep"
            wake_up_hour_str = self.s_mem.daily_schedule[0][0] # TODO wakeup hour by LLM or by other func?
            action_dur = action_start.get_timedelta_from_time_str(wake_up_hour_str)
        elif self.s_mem.daily_schedule_idx >= len(self.s_mem.daily_schedule):
            # TODO end of schedule, do nothing
            return
        else:
            _, tmp_dur, action_desc = self.s_mem.daily_schedule[self.s_mem.daily_schedule_idx] # TODO use action_start
            action_dur = timedelta(minutes=int(float(tmp_dur) * 60))

        action_address = 'Test Address' # TODO add locations of actions
        action_start_str = action_start.get_time_str()
        completed_action = self.s_mem.current_action
        new_action: Action = self.s_mem.add_new_action(action_address=action_address,
                                  action_start_time=action_start,
                                  action_duration=action_dur,
                                  action_description=action_desc)
        # TODO should we only add action to long memory once it completes or add it here?
        # self.l_mem.add_action(new_action) # TODO
        

        log_transcript(self.get_name(), action_start_str, 'Action', action_desc)
        
        # Increment index to next action
        self.s_mem.daily_schedule_idx += 1
        e = Event.create_action_event(self, new_action)

        # Dispatch event to worker queue
        self.agent_mgr.dispatch_to_queue(e)

        return e


    def _create_day_plan(self, new_day: bool, first_day: bool) -> None:
        """
        Function to create a plan for the day
        """
        wake_up_hour = self.s_mem.generate_wake_up_hour()

        if first_day:
            # Generate the very first daily plan
            self.s_mem.generate_first_daily_plan(wake_up_hour)

        elif new_day:
            # Update the agent's identity based on events that occurred and reveries its developed
            self.update_identity() # Do Later...

            # Create new daily plan
            self.s_mem.generate_daily_plan()

        log_transcript(self.get_name(), self.agent_mgr.world_clock.get_time_str(), 'Thought(Plan)', 'Daily Plan: %s' % self.s_mem.daily_plan)

        # Generate list of daily requirements for the day
        self.s_mem.generate_daily_req()

        log_transcript(self.get_name(), self.agent_mgr.world_clock.get_time_str(), 'Thought(Plan)', 'Daily Requirements: %s' % self.s_mem.daily_req)

        # Create hourly schedule for the persona - list of todo items where each has a duration that adds up to a full day
        self.s_mem.generate_hourly_schedule(self.persona, wake_up_hour)

        log_transcript(self.get_name(), self.agent_mgr.world_clock.get_time_str(), 'Thought(Plan)', 'Daily Schedule: %s' % self.s_mem.daily_schedule)

        # Save daily requirements to long term memory
        date_str = self.agent_mgr.world_clock.get_date_str()
        thought = f"This is {self.persona.name}'s plan for {date_str}:"
        for i in self.s_mem.daily_plan:
            thought += f" {i},"
        thought = thought[:-1] + "."
        created = self.agent_mgr.world_clock.snapshot()
        expiration = created + timedelta(days=30)

        s, p, o = (self.persona.name, "plan", date_str)
        keywords = set(["plan"])

        node: AgentConcept = self.l_mem.add_thought(created, expiration, s, p, o, thought, keywords)
        log_transcript(self.get_name(), self.agent_mgr.world_clock.get_time_str(), 'Thought(Plan)', f"{node.summary()} --> {node.description}")

    def update_identity(self) -> None:
        """ * Uses LLM
        TODO
        Implement function to update an agent's identity based on new events that occurred and reveries its developed
        Will be called at start of every day
        Try and moving to a memory class
        """
        pass

    def narration_event_trigger(self, event: Event) -> None:
        """
        Function to receive narration change events from the Narrator
        """
        # self.memory.append(event)
        pass

    def agent_event_trigger(self, event: Event) -> None:
        """
        Function to receive agent events for other agents such as chat requests from agent manager
        """
        pass

    def debug_timer(self):
        debug("[DEBUG_TIMER - %s] Private Memory(len=%s):\n%s" % (self.get_name(), len(self.memory), self.memory))

    def __str__(self) -> str:
        return self.get_name()
    
    def get_name(self) -> str:
        return self.persona.get_name()
    
    def save_to_file(self) -> str:
        # TODO - should be 2 saves : 1 for state and other for base persona ??
        pass
    
    def load_from_file(self) -> bool:
        pass

    def get_common_set_str(self):
        # TODO just store this as a string
        commonset = ""
        commonset += f"Name: {self.persona.name}\n"
        commonset += f"Age: {self.persona.age}\n"
        commonset += f"Backstory: {self.persona.backstory}\n"
        commonset += f"Occupation: {self.persona.occupation}\n"
        commonset += f"Innate traits: {self.persona.traits}\n"
        commonset += f"Motivations: {self.persona.motivations}\n"
        commonset += f"Relationships: {self.persona.relationships}\n"
        commonset += f"Daily plan requirement: {self.s_mem.daily_plan}\n"
        # commonset += f"Current Date: {self.curr_time.strftime('%A %B %d')}\n"
        return commonset