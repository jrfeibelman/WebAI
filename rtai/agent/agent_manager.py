from typing import List, Set, Dict
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from numpy import uint64

from rtai.utils.config import Config
from rtai.agent.agent import Agent
from rtai.agent.abstract_agent import AbstractAgent
from rtai.core.event import Event
from rtai.utils.timer_manager import TimerManager
from rtai.utils.logging import info, debug, error
from rtai.llm.llm_client import LLMClient
from rtai.world.world import World
from rtai.agent.behavior.chat import Chat
from rtai.agent.behavior.chat_message import ChatMessage
from rtai.agent.chat_manager import ChatManager

DEFAULT_NUM_AGENTS = 4
NUM_AGENTS_CONFIG = "NumAgents"
AGENT_STATIC_FILES = "LoadFiles"

class AgentManager:
    """ _summary_ Class to manage all the different agents, facilitating communication between them, and provide shared memory between them.

    Class to manage all the different AI agents. This class should
        - receive events (thoughts/reveries + actions) from the various AI agents and dispatch them
        - dispatch narration to AI agents

    TODO:
        - remove chat from registry
    
    """

    def __init__(self, event_queue: Queue, cfg: Config, client: LLMClient, world: World):
        """_summary_ Constructor for the Agent Manager.

        Args:
            event_queue (Queue): Event queue for the Agent Manager to receive events from.
            cfg (Config): Config object for the Agent Manager.
            client (LLMClient): LLM Client for the Agent Manager.
            world (World): World object for the Agent Manager.
        """
        self.queue: Queue = event_queue
        self.cfg: Config = cfg
        self.agents: Dict[str, Agent] = dict()
        self.registry: Set[str] = set()
        self.last_narration: Event = Event.create_empty_event()
        self.tp: ThreadPoolExecutor = None
        self.client: LLMClient = client
        self.cycle_count: uint64 = uint64(0)
        self.world: World = world
        self.chat_mgr: ChatManager = ChatManager()

    def initialize(self) -> bool:
        """_summary_ Initialize the Agent Manager.

        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        num_agents = int(self.cfg.get_value(NUM_AGENTS_CONFIG, DEFAULT_NUM_AGENTS))

        static_persona_files = self.cfg.get_value(AGENT_STATIC_FILES, [])
        if len(static_persona_files) > 0:
            static_persona_files = static_persona_files[1:-1]
            static_persona_files = [f.strip().replace("'", "") for f in static_persona_files.split(',')]
            static_persona_files = [static_persona_files[i] if i < len(static_persona_files) else '' for i in range(num_agents)]

        for i in range(num_agents):
            a = Agent(self, self.client, file_path=static_persona_files[i])
            if self.register(a): # can prob delete register
                self.agents[a.get_name()] = a
        
        if len(self.agents) != num_agents:
            error("There was an error initializing some agents.")

        info("Initialized Agent Manager with [%d] agents" % len(self.agents))
        self.tp = ThreadPoolExecutor(len(self.agents))
        return True
    
    def start(self) -> None:
        """_summary_ Start each agent individually in parallel with a process
        TODO: rearchitect AgentManager - Agent relationship
        """
        pass
    
    def dispatch_chat_event(self, event: Event) -> None:
        """ _summary_ Dispatch a chat event to the appropriate agent
        
        Args:
            event (Event): Chat event to dispatch
        """
        if event.get_receiver() in self.agents:
            self.chat_mgr.create_chat(event.get_message())
            self.dispatch_to_agent(event)

    def dispatch_action_event(self, event: Event) -> None:
        """ _summary_ Dispatch an action event to the appropriate agent

        Args:
            event (Event): Action event to dispatch
        """
        pass
        # if self.dispatch_to_agent(event):
        #     pass

    def dispatch_to_agent(self, event) -> bool:
        """ _summary_ Dispatch an event to an agent

        Args:
            event (Event): Event to dispatch
        Returns:
            bool: True if event was dispatched successfully, False otherwise
        """
            
        recipient = event.get_receiver()
        try:
            self.agents[recipient].agent_queue.put(event)
        except KeyError:
            error("Agent [%s] not registered with Agent Manager" % recipient)
            return False
        return True

    def dispatch_to_queue(self, event: Event) -> None:
        """ _summary_ Dispatch an event to the Agent Manager's queue

        Args:
            event (Event): Event to dispatch
        """
        self.queue.put(event)
        # TODO: how to dispatch event from one agent to another, or to public story engine memory?
        # TODO how to route event to specific agents
        pass

    def dispatch_narration(self, event: Event) -> None:
        """ _summary_ Dispatch a narration event to all agents

        Args:
            event (Event): Narration event to dispatch
        """
        self.last_narration = event
        [a.narration_event_trigger(event) for a in self.agents.values()]

    def register(self, agent: AbstractAgent) -> bool:
        """ _summary_ Register an agent with the Agent Manager

        Args:
            agent (AbstractAgent): Agent to register
        Returns:
            bool: True if agent was registered successfully, False otherwise
        
        Is having an agent register even necessary?
        """
        name = agent.get_name()

        if name in self.registry:
            error("Unable to register agent [%s] with Agent Manager. Name likely already taken" % name)
            return False
        
        self.registry.add(name)
        info("Registered agent [%s] with Agent Manager" % name)
        return True
    
    @TimerManager.timer_callback
    def update(self, first_day: bool=False, new_day: bool=False) -> None:
        """ _summary_ Update all the agents in Agent Manager
        
        Args:
            first_day (bool, optional): Whether or not it is the first day. Defaults to False.
            new_day (bool, optional): Whether or not it is a new day. Defaults to False.
        """
        # debug("Updating Agents")
        agents = self.agents.values()

        # First update the state of all the agents    
        wait([self.tp.submit(a.update) for a in agents])

        # TODO - have agents communicate with one another and actions inform other agents action in a reactive manner 
        #Then generate actions (Thoughts, Actions, Chats) sequentially for all the agents
        # I guess this can be in parallel if all agents have perceived/updated already
        [a.act(first_day, new_day) for a in agents]
            
        # Then generate reflections / reveries for all the agents
        wait([self.tp.submit(a.reflect) for a in agents])

        self.cycle_count += 1
    
    def get_last_narration(self) -> Event:
        """ _summary_ Get the last narration event

        Returns:
            Event: Last narration event
        """
        return self.last_narration
    
    def debug_timer(self):
        """ _summary_ Calls debug timer for all agents
        """
        [a.debug_timer() for a in self.agents.values()]

    def get_cycle_count(self) -> uint64:
        """ _summary_ Get the cycle count

        Returns:
            uint64: Cycle count
        """
        return self.cycle_count