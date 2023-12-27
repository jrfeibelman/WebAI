from time import perf_counter
from typing import List
from queue import Queue

from rtai.story.abstract_agent import AbstractAgent
from rtai.utils.config import Config
from rtai.core.event import Event
from rtai.utils.timer_manager import TimerManager
from rtai.utils.logging import info, debug

class Narrator(AbstractAgent):
    def __init__(self, event_queue: Queue, cfg: Config):
        super().__init__()
        self.queue: Queue = event_queue
        self.cfg: Config = cfg
        self.narration: List[Event] = []
        self._counter: int = 0 # TODO eventually delete ?

        info("Initialized narrator")

    @TimerManager.timer_callback
    def generate_narration(self, t="") -> Event:
        debug("Generating Naration")
        start_time = perf_counter()

        # TODO - call LLM to generate narration
        new_narration = "Narration %s" % self._counter

        elapsed_time = perf_counter() - start_time

        event = Event.create_narration_event(self, new_narration)

        info("Narrator [%s] took [%s] ms for generate_narration()" % (self.get_name(), elapsed_time * 1000))
        
        self.queue.put(event)
        self.narration.append(event)

        self._counter += 1
        return event

    def manual_narration(self, narration: str) -> Event:
        event = Event.create_narration_event(self, narration)
        self.queue.put(event)
        self.narration.append(event)
        
        self._counter += 1
        return event
    
    def debug_timer(self):
        debug("[DEBUG_TIMER - %s] Narration(len=%s):\n%s" % (self.get_name(), len(self.generate_narration()), self.get_narration()))

    def get_narration(self) -> List[Event]:
        return self.narration
    
    def get_last_narration(self, num: int = 1) -> List[Event]:
        return self.narration[-num:]
    
    def __str__(self) -> str:
        return "Narrator"
    
    def get_name(self) -> str:
        return self.__str__()