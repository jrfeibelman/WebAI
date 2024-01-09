from __future__ import annotations
from time import perf_counter
from typing import List, TYPE_CHECKING
from queue import Queue
from numpy import uint16

if TYPE_CHECKING:
    from rtai.agent.agent_manager import AgentManager

from rtai.agent.abstract_agent import AbstractAgent

from rtai.core.event import Event, EventType
from rtai.utils.logging import info, debug, warn, log_transcript
from rtai.agent.persona import Persona
from rtai.agent.memory.short_memory import ShortTermMemory
from rtai.agent.memory.long_memory import LongTermMemory
from rtai.utils.datetime import datetime, timedelta
from rtai.llm.llm_client import LLMClient
from rtai.agent.cognition.agent_concept import AgentConcept
from rtai.agent.behavior.action import Action
from rtai.agent.behavior.chat import Chat
from rtai.agent.cognition.cognition import Cognition
from rtai.agent.cognition.conversing import Conversing

class Agent(AbstractAgent):
    """ _summary_ Class to represent AI Agent with behaviors generated by LLMs

    TODO:
        Questions:
            - What should AI Agents do? Thoughts --> Actions (within context of environment (environment = narration + other AI agents))
            - Is this too simplistic? Should reveries = thoughts or should reveries be multiple thoughts / skills / plans that lead to a given action?

        Implementation
            - add retriever to trigger generating reverie
    
    
    """
    id: uint16 = uint16(0)

    def __init__(self, agent_mgr: AgentManager, client: LLMClient, file_path: str=""):
        """ _summary_ Constructor to create a new agent

        Args:
            agent_mgr (AgentManager): Agent Manager for the agent
            client (LLMClient): LLM Client for the agent
            file_path (str, optional): File path to load persona from. Defaults to "".        
        """
        super().__init__()

        self.agent_mgr: AgentManager = agent_mgr
        self.llm_client: LLMClient = client

        self.conversations: List[Event] = []

        self.agent_queue: Queue = Queue()
        self.is_sleeping: bool = False

        Agent.id += 1
        self.id = Agent.id

        if len(file_path) > 0:
            self.persona: Persona = Persona.generate_from_file(file_path)
            info("Generating Agent [%s] from file [%s]" % (self.get_name(), file_path))
        else:
            self.persona: Persona = Persona.generate()
            info("Generating Agent [%s] from LLM" % (self.get_name()))

        self.s_mem: ShortTermMemory = ShortTermMemory(self.id, self.persona, self.llm_client, self.agent_mgr.world_clock)
        self.l_mem: LongTermMemory = LongTermMemory(self.persona, self.agent_mgr.world_clock)
        self.cognition: Cognition = Cognition(self)
        self.conversing: Conversing = Conversing(self)

        # String representation of persona for LLM calls
        self.common_set: str = self.get_common_set_str()

        info("Created Agent [%s]" % self.get_name())
    
    def update(self) -> None:
        """ _summary_ Update the agent's state
        """
        self.cognition.perceive()
        debug("Agent [%s] finished update()" % (self.get_name()))

    def process_queue(self) -> None:
        """ _summary_ Process the events from the agent's event queue"""
        event: Event = None
        while not self.agent_queue.empty():
            event = self.agent_queue.get(block=False)
                
            debug("Agent [%s] Received event:\n\t%s" % (self.get_name(), event))
            self.process_event(event)

    def process_event(self, event: Event) -> None:
        """ _summary_ Process an event received from the agent's queue

        Args:
            event (Event): Event to process
        """

        if event.get_event_type() == EventType.ChatEvent:
            self.conversing.receive_chat_request(event)
        elif event.get_event_type() == EventType.ActionEvent:
            pass
        else:
            warn("Agent [%s] did not process event: %s" % (self.get_name(), event))

    def act(self, new_day: bool, first_day: bool=False) -> None:
        """ _summary_ Logic for updating the agent's behavior

        Args:
            new_day (bool): True if new day, False otherwise
            first_day (bool, optional): True if first day, False otherwise. Defaults to False.

        1) If start of day, perform daily agenda creation
        2) If current action expired, create new plan 
        3) If you perceived an event that needs to be responded to, generate action or chat (TODO later)
        """
        start_time = perf_counter()

        if new_day or first_day:
             # Creates Planning Thought
            self.cognition.plan(False, new_day, first_day)

        # if action expired, create new agenda/plan
        if self.s_mem.has_action_completed():
            debug("Action [%s] completed at [%s]" % (self.s_mem.current_action.description, self.agent_mgr.world_clock.get_time_str()))
            self.cognition.determine_action()
            
        # TODO later - if perceived event that needs to be responded to (such as chat), generate action or chat
        self.process_queue()

        if len(self.s_mem.chatting_with) > 0:
            self.cognition.chat()

        elapsed_time = perf_counter() - start_time
        debug("Agent [%s] took [%s] ms for act()" % (self.get_name(), elapsed_time * 1000))

    def reflect(self) -> None:
        """ _summary_ Logic for updating the agent's memory based on completed events
        Reflect --> Create Reveries
        """
        start_time = perf_counter()

        self.cognition.reflect()

        elapsed_time = perf_counter() - start_time
        debug("Agent [%s] took [%s] ms for reflect()" % (self.get_name(), elapsed_time * 1000))

    def update_identity(self) -> None:
        """ _summary_ Logic for updating the agent's identity based on new events that occurred and reveries its developed
        TODO
        Implement function to update an agent's identity based on new events that occurred and reveries its developed
        Will be called at start of every day
        Try and moving to a memory class
        """
        pass

    def narration_event_trigger(self, event: Event) -> None:
        """ _summary_ Function to receive narration change events from the Narrator

        Args:
            event (Event): Narration change event
        """
        self.l_mem.process_narration(event)

    def go_to_sleep(self) -> None:
        """ _summary_ Function to put agent to sleep

        TODO write function to kick off sleeping logic instead of relying on NewDay event
            - revise identity
            - dream ?
        """
        # Update the agent's identity based on events that occurred and reveries its developed
        self.update_identity()
        # Update the agent's relationships with other agents
        # self.update_relationships()

    def debug_timer(self) -> None:
        """ _summary_ Function to debug the agent's timer
        """
        debug("[DEBUG_TIMER - %s] Private Memory(len=%s):\n%s" % (self.get_name(), len(self.memory), self.memory))

    def __str__(self) -> str:
        return self.get_name()
    
    def get_name(self) -> str:
        """ _summary_ Get the agent's name
        
        Returns:
            str: Agent's name
        """
        return self.persona.get_name()
    
    def get_id(self) -> uint16:
        """ _summary_ Get the agent's id 
        
        Returns:
            uint16: Agent's id
        """
        return self.id
    
    def interrogate(self, question: str) -> str:
        """ _summary_ Interrogate the agent with a question
        
        Args:
            question (str): Question to ask
            
        Returns:
            str: Response to question
        """
        return "Dummy Response"

    def save_to_file(self, file_path: str) -> None:
        """ _summary_ Save the agent's state to a file
        
        Args:
            file_path (str): File path to save to
        """
        # TODO - should be 2 saves : 1 for state and other for base persona ??
        pass
    
    def load_from_file(self, file_path: str) -> bool:
        """ _summary_ Load the agent's state from a file

        Args:
            file_path (str): File path to load from
        
        Returns:
            bool: True if successful, False otherwise
        """
        pass

    def get_common_set_str(self) -> str:
        """ _summary_ Get the agent's common set as a string

        Returns:
            str: Common set as a string
         
        TODO store this as a string and update when changed ??
        """
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