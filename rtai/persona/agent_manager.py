from typing import List, Set
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

from rtai.utils.config import Config
from rtai.persona.agent import Agent
from rtai.persona.abstract_agent import AbstractAgent
from rtai.core.event import Event
from rtai.utils.timer_manager import TimerManager
from rtai.utils.logging import info, debug, error

DEFAULT_NUM_AGENTS = 4
NUM_AGENTS_CONFIG = "NumAgents"

class AgentManager:
    """
    Class to manage all the different AI agents. This class should
        - receive events (thoughts/reveries + actions) from the various AI agents and dispatch them
        - dispatch narration to AI agents
    
    """
    queue: Queue
    cfg: Config
    agents: List[Agent]
    registry: Set[str]
    last_narration: Event
    thread_pool: ThreadPoolExecutor

    def __init__(self, event_queue: Queue, cfg: Config):
        self.queue = event_queue
        self.cfg: Config = cfg
        self.agents: List[Agent] = []
        self.registry: Set[str] = set()
        self.last_narration: Event = Event.create_empty_event()
        self.tp: ThreadPoolExecutor = None

    def initialize(self) -> bool:
        num_agents = int(self.cfg.get_value(NUM_AGENTS_CONFIG, DEFAULT_NUM_AGENTS))
        self.agents = [Agent(self, self.queue) for _ in range(num_agents)]

        info("Initialized Agent Manager with [%d] agents" % len(self.agents))
        self.tp = ThreadPoolExecutor(len(self.agents))
        return True

    def dispatch(self, event: Event) -> None:
        # TODO: how to dispatch event from one agent to another, or to public story engine memory?
        # TODO how to route event to specific agents
        pass

    def dispatch_narration(self, event: Event) -> None:
        self.last_narration = event
        [a.dispatch_narration(event) for a in self.agents]

    def register(self, agent: AbstractAgent) -> bool:
        name = agent.get_name()

        if name in self.registry:
            error("Unable to register agent [%s] with Agent Manager. Name likely already taken" % name)
            return False
        
        self.registry.add(name)
        info("Registered agent [%s] with Agent Manager" % name)
        return True
    
    @TimerManager.timer_callback
    def update(self, first_day: bool=False, new_day: bool=False) -> None:
        debug("Updating Agents")
        # First update the state of all the agents
        wait([self.tp.submit(a.update) for a in self.agents])

        # Then generate actions (Thoughts, Actions, Chats) sequentially for all the agents
        # I guess this can be in parallel if all agents have perceived/updated already
        [a.act(first_day, new_day) for a in self.agents]
            
        # Then generate reflections / reveries for all the agents
        wait([self.tp.submit(a.reflect) for a in self.agents])

    
    def get_last_narration(self) -> Event:
        return self.last_narration
    
    def debug_timer(self):
        [a.debug_timer() for a in self.agents]