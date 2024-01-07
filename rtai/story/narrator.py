from time import perf_counter
from typing import List
from queue import Queue

from rtai.agent.abstract_agent import AbstractAgent
from rtai.utils.config import Config
from rtai.core.event import Event
from rtai.utils.timer_manager import TimerManager
from rtai.utils.logging import info, debug, log_transcript
from rtai.llm.llm_client import LLMClient
from rtai.world.clock import WorldClock

class Narrator(AbstractAgent):
    """ _summary_ Class to represent Narrator Agent"""

    def __init__(self, event_queue: Queue, cfg: Config, client: LLMClient, world_clock: WorldClock):
        """ _summary_ Constructor to create a new narrator agent
        
        Args:
            event_queue (Queue): Queue to put events on
            cfg (Config): Config to use for narrator
            client (LLMClient): LLM Client to use for narrator
            world_clock (WorldClock): World Clock to use for narrator
        """
        super().__init__()
        self.queue: Queue = event_queue
        self.llm_client: LLMClient = client
        self.cfg: Config = cfg
        self.narration: List[Event] = []
        self.world_clock: WorldClock = world_clock
        self._counter: int = 0 # TODO eventually delete ? add termination to config
        info("Initialized narrator")

    @TimerManager.timer_callback
    def generate_narration(self) -> Event:
        """ _summary_ Method to generate narration from LLM

        Returns:
            Event: Narration event
        """

        debug("Generating Naration")
        start_time = perf_counter()

        # TODO - call LLM to generate narration
        prompt = "Joker"
        completion = self.llm_client.generate_from_prompt(system_prompt="You are a narrator", user_prompt=prompt)

        log_transcript('Narrator', self.world_clock.get_time_str(), 'Auto', completion)

        elapsed_time = perf_counter() - start_time

        event = Event.create_narration_event(self, completion)

        info("Narrator [%s] took [%s] ms for generate_narration()" % (self.get_name(), elapsed_time * 1000))
        
        self.queue.put(event)
        self.narration.append(event)

        self._counter += 1
        return event

    def manual_narration(self, narration: str) -> Event:
        """ _summary_ Method to manually trigger narration

        Args:
            narration (str): Narration to use

        Returns:
            Event: Narration event

        TODO : If manual narration triggered, restart generate_narration timer thread
        """
        event = Event.create_narration_event(self, narration)
        self.queue.put(event)
        self.narration.append(event)
        
        self._counter += 1
        return event
    
    def debug_timer(self) -> None:
        """ _summary_ Method to print out narrator state on debug timer callback"""
        debug("[DEBUG_TIMER - %s] Narration(len=%s):\n%s" % (self.get_name(), len(self.generate_narration()), self.get_narration()))

    def get_narration(self) -> List[Event]:
        """ _summary_ Method to get the narration
        
        Returns:
            List[Event]: List of narration events
        """
        return self.narration
    
    def get_last_narration(self, num: int = 1) -> List[Event]:
        """ _summary_ Method to get the last narration

        Args:
            num (int, optional): Number of last narration events to get. Defaults to 1.

        Returns:
            List[Event]: List of narration events
        """
        return self.narration[-num:]
    
    def __str__(self) -> str:
        return "Narrator"
    
    def get_name(self) -> str:
        """ _summary_ Get the narrator's name
        
        Returns:
            str: Agent's name
        """
        return self.__str__()
    
    def save_to_file(self, file_path: str) -> None:
        """ _summary_ Save the narrator's state to a file
        
        Args:
            file_path (str): File path to save to
        """
        pass
    
    def load_from_file(self, file_path: str) -> bool:
        """ _summary_ Load the narrator's state from a file
        
        Args:
            file_path (str): File path to load from
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        pass