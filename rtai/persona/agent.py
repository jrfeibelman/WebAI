from time import perf_counter
from queue import Queue
from typing import List

from rtai.story.abstract_agent import AbstractAgent
from rtai.core.event import Event
from rtai.utils.logging import info, debug
from rtai.persona.persona import Persona
from rtai.llm.llm_client import LLMClient
from rtai.llm.prompt import reverie_prompt

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
    counter = 0

    def __init__(self, agent_mgr: AbstractAgent, event_queue: Queue, client: LLMClient):
        super().__init__()
        self.agent_mgr: AbstractAgent = agent_mgr
        self.queue: Queue = event_queue
        self.llm_client = client
        self.memory: List[Event] = []
        self.conversations: List[Event] = []

        Agent.counter += 1
        self.id = Agent.counter
        self.persona = Persona.generate_from_file('tests/personas/persona%s.txt' % self.id) # TODO: use llm to generate persona?
        # print(self.persona)
        info("Created Agent [%s]" % self.get_name())

    def generate_reverie(self) -> Event:
        """
        Function to leverage LLMs to generate a given thought based on their environment, which influences the actions they take
        """
        start_time = perf_counter()
        # TODO - call LLM to generate reverie
        # move error handling to the LLM Client? or LLMServer
        prompt = reverie_prompt(self.persona)
        response = self.llm_client.generate_from_prompt(system_prompt="You are a story teller.", user_prompt=prompt)
        msg = "Test Reverie (%s)" % self.get_name()

        try:
            msg += "\n" + response
        except:
            msg += "\n" + "Failed to generate reverie for some reason"

        elapsed_time = perf_counter() - start_time
        info("Agent [%s] took [%s] ms for generate_reverie()" % (self.get_name(), elapsed_time * 1000))

        event = Event.create_reverie_event(self, msg)
        self.queue.put(event)
        self.memory.append(event)
        return event

    def generate_action(self) -> Event:
        """
        Function to leverage LLMs to generate a given action based on their environment and reveries
        """
        start_time = perf_counter()

        # TODO - call LLM to generate action
        msg = "Test Action (%s)" % self.get_name()

        elapsed_time = perf_counter() - start_time
        info("Agent [%s] took [%s] ms for generate_action()" % (self.get_name(), elapsed_time * 1000))

        event = Event.create_action_event(self, msg)
        self.queue.put(event)
        self.memory.append(event)
        return event

    def dispatch_narration(self, event: Event) -> None:
        """
        Function to receive narration change events from the Narrator
        """
        self.memory.append(event)

    def debug_timer(self):
        debug("[DEBUG_TIMER - %s] Private Memory(len=%s):\n%s" % (self.get_name(), len(self.memory), self.memory))

    def __str__(self) -> str:
        return self.persona.get_name()
    
    def get_name(self) -> str:
        return self.__str__()
    
    def save_to_file(self) -> str:
        # TODO - should be 2 saves : 1 for state and other for base persona ??
        pass
    
    def load_from_file(self) -> bool:
        pass