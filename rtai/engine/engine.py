from queue import Queue
from typing import List
from sys import exit
from numpy import uint16, uint64

from rtai.utils.config import Config
from mythos.agent.oracle.narrator import Narrator
from rtai.agent.agent_manager import AgentManager
from rtai.core.event import Event, EventType
from rtai.utils.timer_manager import TimerManager
from rtai.utils.logging import info, debug, error, warn
from rtai.llm.llm_client import LLMClient
from rtai.core.clock import clock
from rtai.environment.world import World

from tests.mock.llm.llm_client_mock import LLMTestClient
from rtai.llm.llm_client import LLMClient

"""
TODO:
- Memory Profile
- In debugging print out narration change
- Agent Personalities
- Hooking up to LLM
- Limit iterations to max steps

ToThink:
- Thought -> Action -> Reverie -> Reflection ?
"""
AGENTS_CONFIG = 'Agents'
ENGINE_CONFIG = 'Engine'
WORLD_CONFIG = 'World'
CLOCK_CONFIG = 'Clock'
LLM_CLIENT_CONFIG = 'LLMClient'

WORKER_THREAD_TIMER_CONFIG = 'WorkerThreadTimerMs'
AGENT_TIMER_CONFIG = 'AgentTimerMillis'
DEBUG_TIMER_CONFIG = 'DebugTimerSec'
WORLD_CLOCK_TIMER_CONFIG = 'ClockTimerMillis'

WORKER_TIMER_DEFAULT = 100 # MilliSec
AGENT_TIMER_DEFAULT = 5 # Sec
DEBUG_TIMER_CONFIG_DEFAULT = 0 # Sec
WORLD_CLOCK_TIMER_DEFAULT = 500 # MilliSec

WORKER_THREAD_NAME = 'WorkerThread'
AGENT_THREAD_NAME = 'AgentThread'
DEBUG_THREAD_NAME = 'DebugThread'
WORLD_CLOCK_THREAD_NAME = 'WorldClockThread'

MAX_CYCLES = 'StopAfterCycles'

class Engine:
    """ _summary_ Class to represent the story engine"""

    def __init__(self, cfg: Config, debug_mode: bool=False, test_mode: bool=False, static_init: bool=False):
        """ _summary_ Constructor for the story engine
        
        Args:
            cfg (Config): Config object
            debug_mode (bool, optional): Debug mode flag. Defaults to False.
            test_mode (bool, optional): Test mode flag to use all static fiels instead of LLM calls. Defaults to False.
            static_init(bool, optional): Static initialization mode flag that bootstraps from static files then uses LLM during program. Defaults to False.
        """

        self.cfg: Config = cfg.expand(ENGINE_CONFIG)

        self.debug_mode: bool = debug_mode

        self.worker_queue = Queue()

        self.max_cycles: uint64 = uint64(self.cfg.get_value(MAX_CYCLES, "0"))

        self.test_mode: bool = test_mode
        self.static_init: bool = static_init

        # Setup World Clock
        clock_config = cfg.expand(CLOCK_CONFIG)
        sim_clock: clock = clock(clock_config)
        
        # Setup LLM Client
        if test_mode:
            self.llm_client: LLMClient = LLMTestClient()
            warn("Test mode enabled. LLMClient will leverage test data for responses")
        else:
            self.llm_client: LLMClient = LLMClient()
            warn("Test mode disabled. LLMClient will leverage Local LLM for responses")

        if not self.llm_client.initialize(cfg.expand(LLM_CLIENT_CONFIG)):
            error("Unable to initialize LLMClient. Exiting.")
            exit(1)

        if static_init:
            self.static_client: LLMTestClient = LLMTestClient()
            print(type(self.static_client))
            warn("Static Initialization mode enabled. LLMClient will leverage test data for initialization")
        
        # Setup World
        self.environment: World = World(cfg.expand(WORLD_CONFIG), self.worker_queue)
        initial_shared_memories: List[str] = self.environment.get_shared_memories() # TODO: feed the intial shred memories into the LLMClient

        if not self.environment.initialize():
            error("Unable to initialize world. Exiting.")
            exit(1)

        # Set up Agents
        self.agent_mgr: AgentManager = AgentManager(self.worker_queue, cfg.expand(AGENTS_CONFIG), client=self.llm_client, world=self.environment)
        # self.narrator: Narrator = Narrator(self.agent_mgr, self.worker_queue, cfg.expand(NARRATOR_CONFIG), client=self.llm_client)
        # if not self.agent_mgr.register(self.narrator):
        #     error("Unable to register narrator with agent manager. Exiting.")
        #     exit(1)

        if not self.agent_mgr.initialize():
            error("Unable to initialize agent manager. Exiting.")
            exit(1)

        self.agent_mgr.load_initial_memories(initial_shared_memories)

        # Set up threaded timers (i.e. create a thought every x seconds)
        self.timer_mgr: TimerManager = TimerManager()
        self.timer_mgr.add_timer(AGENT_THREAD_NAME, uint16(self.cfg.get_value(AGENT_TIMER_CONFIG, AGENT_TIMER_DEFAULT)), self.agent_mgr.update, milliseconds=True)
        self.timer_mgr.add_timer(WORKER_THREAD_NAME, uint16(self.cfg.get_value(WORKER_THREAD_TIMER_CONFIG, WORKER_TIMER_DEFAULT)), self.poll_event_queue, milliseconds=True)
        self.timer_mgr.add_timer(WORLD_CLOCK_THREAD_NAME, uint16(clock_config.get_value(WORLD_CLOCK_TIMER_CONFIG, WORLD_CLOCK_TIMER_DEFAULT)), sim_clock.tick, milliseconds=True)
        
        # Debug printing
        debug_timer_sec = uint16(self.cfg.get_value(DEBUG_TIMER_CONFIG, DEBUG_TIMER_CONFIG_DEFAULT))
        if self.debug_mode and debug_timer_sec > 0:
            debug("Debug mode enabled. Adding debug timer")
            self.timer_mgr.add_timer(DEBUG_THREAD_NAME, debug_timer_sec, self.debug_timer)



    def initialize(self) -> bool:
        """ _summary_ Initializes the engine
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """

        # Set initial state of agents
        self.agent_mgr.update(first_day=True) # TODO Fix static init, test_llm_client=self.static_client if static_init else None)

        info("Initialized Story Engine")

    def start(self) -> None:
        """ _summary_ Starts the engine"""
        self.timer_mgr.start_timers()
        self.agent_mgr.start()

        info("Started engine")

    def stop(self, status: int=0) -> None:
        """ _summary_ Stops the engine"""
        self.timer_mgr.stop_timers()
        info("Engine shutdown complete")
        exit(status)

    @TimerManager.timer_callback
    def poll_event_queue(self) -> None:
        """ _summary_ Polls the event worker_queue for new events"""
        # debug("Polling Event Queue")
        event: Event = None
        while not self.worker_queue.empty():
            event = self.worker_queue.get(block=False)
                
            debug("Received event:\n\t%s" % event)
            self.process_event(event)

        # Is this the right place to do this?
        if self.max_cycles > 0 and self.agent_mgr.get_cycle_count() >= self.max_cycles:
            info("Stopping after %d cycles" % self.agent_mgr.get_cycle_count())
            self.stop()
        if self.max_days > 0 and clock.get_day_count() >= self.max_days:
            info("Stopping after %d days" % clock.get_day_count())
            self.stop()

    def process_event(self, event: Event) -> bool:
        """ _summary_ Processes an event from the event worker_queue
        
        Args:
            event (Event): Event to process

        Returns:
            bool: True if event was processed, False otherwise
        """
        if event.get_event_type() == EventType.TaskEvent:
            self.agent_mgr.dispatch_action_event(event)
        else:
            warn("Unknown event type: %s. Ignoring" % event.get_event_type())
            return False
        
        return True

    @TimerManager.timer_callback
    def debug_timer(self) -> None:
        """ _summary_ Prints out debug information to see state of simulation on a timer"""
        debug("[DEBUG_TIMER - Engine] Public Memory:\n%s" % self.narrator.get_narration())
        self.agent_mgr.debug_timer()