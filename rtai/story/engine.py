from queue import Queue
from typing import List
from sys import exit
from numpy import uint16, uint64

from rtai.utils.config import Config
from rtai.story.narrator import Narrator
from rtai.agent.agent_manager import AgentManager
from rtai.core.event import Event, EventType
from rtai.utils.timer_manager import TimerManager
from rtai.utils.logging import info, debug, error, warn
from rtai.llm.llm_client import LLMClient
from rtai.world.clock import clock
from rtai.world.world import World

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
USE_GUI_CONFIG = 'UseGui'
STORY_CONFIG = 'StoryEngine'
NARRATOR_CONFIG = 'Narrator'
WORLD_CONFIG = 'World'
CLOCK_CONFIG = 'Clock'
LLM_CLIENT_CONFIG = 'LLMClient'

WORKER_THREAD_TIMER_CONFIG = 'WorkerThreadTimerMs'
AGENT_TIMER_CONFIG = 'AgentTimerMillis'
NARRATION_TIMER_CONFIG = 'NarrationTimerSec'
DEBUG_TIMER_CONFIG = 'DebugTimerSec'
WORLD_CLOCK_TIMER_CONFIG = 'ClockTimerMillis'

WORKER_TIMER_DEFAULT = 100 # MilliSec
AGENT_TIMER_DEFAULT = 5 # Sec
NARRATION_TIMER_DEFAULT = 120 # Sec
DEBUG_TIMER_CONFIG_DEFAULT = 0 # Sec
WORLD_CLOCK_TIMER_DEFAULT = 500 # MilliSec

WORKER_THREAD_NAME = 'WorkerThread'
AGENT_THREAD_NAME = 'AgentThread'
NARRATION_THREAD_NAME = 'NarrationThread'
DEBUG_THREAD_NAME = 'DebugThread'
WORLD_CLOCK_THREAD_NAME = 'WorldClockThread'

MAX_CYCLES = 'StopAfterCycles'
MAX_DAYS = 'StopAfterDays'

class StoryEngine:
    """ _summary_ Class to represent the story engine"""

    def __init__(self, cfg: Config, debug_mode: bool=False, test_mode: bool=False, static_init: bool=False):
        """ _summary_ Constructor for the story engine
        
        Args:
            cfg (Config): Config object
            debug_mode (bool, optional): Debug mode flag. Defaults to False.
            test_mode (bool, optional): Test mode flag. Defaults to False.
        """

        self.cfg: Config = cfg.expand(STORY_CONFIG)
        self.queue = Queue()
        self.public_mem: List[Event] = []
        self.use_gui: bool = self.cfg.get_value(USE_GUI_CONFIG, "False") == "True"
        self.max_cycles: uint64 = uint64(self.cfg.get_value(MAX_CYCLES, "0"))
        self.max_days: uint16 = uint16(self.cfg.get_value(MAX_DAYS, "0"))

        self.debug_mode: bool = debug_mode
        self.test_mode: bool = test_mode
        self.static_init: bool = static_init
        self.force_stop: bool = False

        # Setup World Clock
        clock_config = cfg.expand(CLOCK_CONFIG)
        world_clock: clock = clock(clock_config)
        
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
        self.world: World = World(cfg.expand(WORLD_CONFIG), self.queue)
        initial_shared_memories: List[str] = self.world.get_shared_memories()

        if not self.world.initialize():
            error("Unable to initialize world. Exiting.")
            exit(1)

        # Set up Agents
        self.narrator: Narrator = Narrator(self.queue, cfg.expand(NARRATOR_CONFIG), client=self.llm_client)
        self.agent_mgr: AgentManager = AgentManager(self.queue, cfg.expand(AGENTS_CONFIG), client=self.llm_client, world=self.world)
        if not self.agent_mgr.register(self.narrator):
            error("Unable to register narrator with agent manager. Exiting.")
            exit(1)

        if not self.agent_mgr.initialize():
            error("Unable to initialize agent manager. Exiting.")
            exit(1)

        self.agent_mgr.load_initial_memories(initial_shared_memories)

        # Set up threaded timers (i.e. create a thought every x seconds)
        self.timer_mgr: TimerManager = TimerManager()
        self.timer_mgr.add_timer(AGENT_THREAD_NAME, uint16(self.cfg.get_value(AGENT_TIMER_CONFIG, AGENT_TIMER_DEFAULT)), self.agent_mgr.update, milliseconds=True)
        self.timer_mgr.add_timer(NARRATION_THREAD_NAME, uint16(self.cfg.get_value(NARRATION_TIMER_CONFIG, NARRATION_TIMER_DEFAULT)), self.narrator.generate_narration)
        self.timer_mgr.add_timer(WORKER_THREAD_NAME, uint16(self.cfg.get_value(WORKER_THREAD_TIMER_CONFIG, WORKER_TIMER_DEFAULT)), self.poll_event_queue, milliseconds=True)
        self.timer_mgr.add_timer(WORLD_CLOCK_THREAD_NAME, uint16(clock_config.get_value(WORLD_CLOCK_TIMER_CONFIG, WORLD_CLOCK_TIMER_DEFAULT)), world_clock.tick, milliseconds=True)
        
        # Debug printing
        debug_timer_sec = uint16(self.cfg.get_value(DEBUG_TIMER_CONFIG, DEBUG_TIMER_CONFIG_DEFAULT))
        if self.debug_mode and debug_timer_sec > 0:
            debug("Debug mode enabled. Adding debug timer")
            self.timer_mgr.add_timer(DEBUG_THREAD_NAME, debug_timer_sec, self.debug_timer)

        # Generate first narration
        narration: Event = self.narrator.generate_narration("")
        self.public_mem.append(narration)
        self.agent_mgr.dispatch_narration(narration)

        # Set initial state of agents
        self.agent_mgr.update(first_day=True, test_llm_client=self.static_client if static_init else None)

        info("Initialized Story Engine")

    def start(self) -> None:
        """ _summary_ Starts the story engine"""
        self.timer_mgr.start_timers()
        self.agent_mgr.start()

        info("Started story engine")

        self.poll_input()

    def stop(self, status=0) -> None:
        """ _summary_ Stops the story engine"""
        self.force_stop = True
        self.timer_mgr.stop_timers()
        info("Shutdown complete")
        exit(status)

    def poll_input(self) -> None:
        """ _summary_ Polls console for user input"""
        while not self.force_stop:
            x = input(">>> ")
            if x == "exit":
                self.stop()
                return
            elif "narrate" in x:
                text = x.split("narrate ")[1]
                self.manual_narration_change(text)
            elif "pause" in x:
                self.timer_mgr.pause_timers()
            elif "resume" in x:
                self.timer_mgr.resume_timers()
            elif "interrogate" in x:
                if not self.timer_mgr.is_paused:
                    error("Failed to interrogate agent - timers must be paused first.")
                    continue

                agent_name = x.split("interrogate ")[1]
                if agent_name not in self.agent_mgr.agents:
                    error("Tried to interrogate unknown agent: %s" % a)
                    continue

                self.enter_interrogation(agent_name)
                info("Finished interrogating Agent [%s]" % agent_name)

            elif x == "h" or x == "help":
                print("Commands:\n \
                    help - print this help message\n \
                    narrate <str> - manually narrate\n \
                    exit - exit the program")
            else:
                print("Unknown command")

    def enter_interrogation(self, agent_name: str) -> None:
        agent = self.agent_mgr.agents[agent_name]
        with agent.enter_interrogation():
            info("Agent [%s] is now under interrogation. Type 'end interrogate' to end." % agent_name)
            while True:
                x = input(">>> ")
                if x == "end":
                    return
                elif x == "h" or x == "help":
                    print("Commands:\n \
                        help - print this help message\n \
                        narrate <str> - manually narrate\n \
                        end - end interrogation")
                else:
                    response = agent.interrogate(x)
                    info("Agent [%s] response: %s" % (agent_name, response))

    def dispatch_narration(self, event: Event, manual: bool = False) -> None:
        """ _summary_ Dispatches a narration event

        Args:
            event (Event): Narration event
            manual (bool, optional): Flag to indicate if the event was manually generated. Defaults to False.
        """

        info("%sNarration Change: %s" % ("Manual " if manual else "", event.get_message()))
        self.public_mem.append(event)
        self.agent_mgr.dispatch_narration(event)

    def manual_narration_change(self, text: str) -> None:
        """ _summary_ Manually generates a narration event

        Args:
            text (str, optional): Text to narrate
        """
        event = Event.create_narration_event(self.narrator, text)
        self.dispatch_narration(event, True)

    @TimerManager.timer_callback
    def poll_event_queue(self) -> None:
        """ _summary_ Polls the event queue for new events"""
        # debug("Polling Event Queue")
        event: Event = None
        while not self.queue.empty():
            event = self.queue.get(block=False)
                
            debug("Received event:\n\t%s" % event)
            self.process_event(event)

        # Is this the right place to do this?
        if self.max_cycles > 0 and self.agent_mgr.get_cycle_count() >= self.max_cycles:
            info("Stopping after %d cycles" % self.agent_mgr.get_cycle_count())
            self.stop()
        if self.max_days > 0 and clock.get_day_count() >= self.max_days:
            info("Stopping after %d days" % clock.get_day_count())
            self.stop()

    def process_event(self, event: Event) -> None:
        """ _summary_ Processes an event from the event queue
        
        Args:
            event (Event): Event to process
        """
        if event.get_event_type() == EventType.NarrationEvent:
            self.dispatch_narration(event)
        elif event.get_event_type() == EventType.ActionEvent:
            self.agent_mgr.dispatch_action_event(event)
        elif event.get_event_type() == EventType.ChatEvent:
            self.agent_mgr.dispatch_chat_event(event)
        else:
            warn("Unknown event type: %s. Ignoring" % event.get_event_type())

    @TimerManager.timer_callback
    def debug_timer(self) -> None:
        """ _summary_ Prints out debug information to see state of simulation on a timer"""
        debug("[DEBUG_TIMER - Engine] Public Memory:\n%s" % self.narrator.get_narration())
        self.narrator.debug_timer()
        self.agent_mgr.debug_timer()