from queue import Queue
from numpy import uint16, uint64                                                                                            
from typing import List



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
from rtai.engine.engine import Engine

NARRATOR_CONFIG = 'Narrator'
NARRATION_TIMER_CONFIG = 'NarrationTimerSec'
NARRATION_TIMER_DEFAULT = 120 # Sec
NARRATION_THREAD_NAME = 'NarrationThread'


USE_GUI_CONFIG = 'UseGui'

MAX_DAYS = 'StopAfterDays'

class StoryEngine(Engine):
    def __init__(self, cfg: Config, debug_mode: bool=False, test_mode: bool=False, static_init: bool=False):
        super().__init__(cfg=cfg, debug_mode=debug_mode, test_mode=test_mode, static_init=static_init)

        self.shutdown_triggered: bool = False
        self.use_gui: bool = self.cfg.get_value(USE_GUI_CONFIG, "False") == "True"

        self.max_days: uint16 = uint16(self.cfg.get_value(MAX_DAYS, "0"))

        self.public_mem: List[Event] = []

        self.narrator: Narrator = Narrator(self.agent_mgr, self.worker_queue, cfg.expand(NARRATOR_CONFIG), client=self.llm_client)
        if not self.agent_mgr.register(self.narrator):
            error("Unable to register narrator with agent manager. Exiting.")
            exit(1)


    def initialize(self) -> bool:
        """ _summary_ Initializes the engine
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """

        super().initialize()

        self.timer_mgr.add_timer(NARRATION_THREAD_NAME, uint16(self.cfg.get_value(NARRATION_TIMER_CONFIG, NARRATION_TIMER_DEFAULT)), self.narrator.generate_narration_callback)
                
        # Generate first narration
        narration: Event = self.narrator.generate_narration()
        print("OK %s" % narration)
        self.dispatch_narration(narration)

        return True


    def start(self):
        """ _summary_ Starts the engine"""
        super().start()
        self.poll_input()

    def stop(self, status: int=0):
        """ _summary_ Stops the engine"""
        self.shutdown_triggered = True
        super().stop(status)

    def process_event(self, event: Event) -> bool:
        """ _summary_ Processes an event from the event worker_queue
        
        Args:
            event (Event): Event to process

        Returns:
            bool: True if event was processed, False otherwise
        """
        if event.get_event_type() == EventType.OracleEvent:
            self.dispatch_narration(event)
        elif event.get_event_type() == EventType.ChatEvent:
            self.agent_mgr.dispatch_chat_event(event)
        else:
            return super().process_event(event)

        return True

    @TimerManager.timer_callback
    def poll_event_queue(self) -> None:
        """ _summary_ Polls the event worker_queue for new events"""
        super().poll_event_queue()

        if self.max_days > 0 and clock.get_day_count() >= self.max_days:
            info("Stopping after %d days" % clock.get_day_count())
            self.stop()

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
        event = Event.create_oracle_event(self.narrator, text)
        print(event)
        self.dispatch_narration(event, True)

    def enter_interrogation_mode(self, agent_name: str) -> None:
        agent = self.agent_mgr.agents[agent_name]
        with agent.enter_interrogation() as interrogation_chat:
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
                    response = agent.interrogate(chat=interrogation_chat, question=x)

                    info("Agent [%s] response: %s" % (agent_name, response))

    def poll_input(self) -> None:
        """ _summary_ Polls console for user input"""
        while not self.shutdown_triggered:
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

                self.enter_interrogation_mode(agent_name)
                info("Finished interrogating Agent [%s]" % agent_name)

            elif x == "h" or x == "help":
                print("Commands:\n \
                    help - print this help message\n \
                    narrate <str> - manually narrate\n \
                    exit - exit the program")
            else:
                print("Unknown command")

    @TimerManager.timer_callback
    def debug_timer(self) -> None:
        """ _summary_ Prints out debug information to see state of simulation on a timer"""
        super().debug_timer()
        self.narrator.debug_timer()



