from tkinter import Tk, Label, Text, Scrollbar, Entry, Button, Frame
from tkinter import END, TOP
from queue import Queue
from threading import Thread
from typing import List
from sys import exit
from numpy import uint16

from rtai.utils.config import Config
from rtai.story.narrator import Narrator
from rtai.story.agent_manager import AgentManager
from rtai.core.event import Event, EventType
from rtai.utils.timer_manager import TimerManager
from rtai.utils.logging import info, debug, error, warn

"""
TODO:
- Memory Profile
- In debugging print out narration change
- Agent Personalities
- Hooking up to LLM

ToThink:
- Thought -> Action -> Reverie -> Reflection ?
"""
AGENTS_CONFIG = 'Agents'
USE_GUI_CONFIG = 'UseGui'
STORY_CONFIG = 'StoryEngine'
NARRATOR_CONFIG = 'Narrator'

WORKER_THREAD_TIMER_CONFIG = 'WorkerThreadTimerMs'
AGENT_THOUGHT_TIMER_CONFIG = 'AgentThoughtTimerSec'
AGENT_ACTION_TIMER_CONFIG = 'AgentActionTimerSec'
NARRATION_TIMER_CONFIG = 'NarrationTimerSec'
DEBUG_TIMER_CONFIG = 'DebugTimerSec'

WORKER_TIMER_DEFAULT = 100 # MilliSec
AGENT_THOUGHT_TIMER_DEFAULT = 5 # Sec
AGENT_ACTION_TIMER_DEFAULT = 15 # Sec
NARRATION_TIMER_DEFAULT = 120 # Sec
DEBUG_TIMER_CONFIG_DEFAULT = 0 # Sec

WORKER_THREAD_NAME = 'WorkerThread'
AGENT_THOUGHT_THREAD_NAME = 'AgentThoughtThread'
AGENT_ACTION_THREAD_NAME = 'AgentActionThread'
NARRATION_THREAD_NAME = 'NarrationThread'
DEBUG_THREAD_NAME = 'DebugThread'

class StoryEngine:

    def __init__(self, cfg: Config, debug_mode: bool=False):
        self.cfg: Config = cfg.expand(STORY_CONFIG)
        self.queue: Queue = Queue()
        self.public_mem: List[Event] = []
        self.use_gui: bool = self.cfg.get_value(USE_GUI_CONFIG, "False") == "True"
        self.debug_mode: bool = debug_mode
        
        # Set up Agents
        self.narrator: Narrator = Narrator(self.queue, cfg.expand(NARRATOR_CONFIG))
        self.agent_mgr: AgentManager = AgentManager(self.queue, cfg.expand(AGENTS_CONFIG))
        if not self.agent_mgr.register(self.narrator):
            error("Unable to register narrator with agent manager. Exiting.")
            exit(1)

        if not self.agent_mgr.initialize():
            error("Unable to initialize agent manager. Exiting.")
            exit(1) 

        # Set up threaded timers
        self.timer_mgr: TimerManager = TimerManager()
        self.timer_mgr.add_timer(AGENT_THOUGHT_THREAD_NAME, uint16(self.cfg.get_value(AGENT_THOUGHT_TIMER_CONFIG, AGENT_THOUGHT_TIMER_DEFAULT)), self.agent_mgr.generate_reveries)
        self.timer_mgr.add_timer(AGENT_ACTION_THREAD_NAME, uint16(self.cfg.get_value(AGENT_ACTION_TIMER_CONFIG, AGENT_ACTION_TIMER_DEFAULT)), self.agent_mgr.generate_actions)
        self.timer_mgr.add_timer(NARRATION_THREAD_NAME, uint16(self.cfg.get_value(NARRATION_TIMER_CONFIG, NARRATION_TIMER_DEFAULT)), self.narrator.generate_narration)
        self.timer_mgr.add_timer(WORKER_THREAD_NAME, uint16(self.cfg.get_value(WORKER_THREAD_TIMER_CONFIG, WORKER_TIMER_DEFAULT)), self.poll_event_queue, milliseconds=True)
        
        # Debug printing
        debug_timer_sec = uint16(self.cfg.get_value(DEBUG_TIMER_CONFIG, DEBUG_TIMER_CONFIG_DEFAULT))
        if self.debug_mode and debug_timer_sec > 0:
            debug("Debug mode enabled. Adding debug timer")
            self.timer_mgr.add_timer(DEBUG_THREAD_NAME, debug_timer_sec, self.debug_timer)

        # Generate first narration
        narration: Event = self.narrator.generate_narration("")
        self.public_mem.append(narration)
        self.agent_mgr.dispatch_narration(narration)

        info("Initialized Story Engine")

    def init_gui(self):
        info("Initializing GUI")
        self.root = Tk()
        self.root.title("Real Time AI")
        self.root.geometry("1000x750")
        
        BG_GRAY = "#ABB2B9"
        BG_COLOR = "#17202A"
        TEXT_COLOR = "#EAECEE"
        
        FONT = "Helvetica 14"
        FONT_BOLD = "Helvetica 13 bold"

        label1 = Label(self.root, bg=BG_COLOR, fg=TEXT_COLOR, text="RTAI", font=FONT_BOLD)
        label1.pack(pady=10, padx=20, side=TOP)
        
        self.txt = Text(self.root, bg=BG_COLOR, fg=TEXT_COLOR, font=FONT, width=120, height=30)
        self.txt.pack(side=TOP)
        
        scrollbar = Scrollbar(self.txt)
        scrollbar.place(relheight=1, relx=0.974)
        
        self.entry = Entry(self.root, bg="#2C3E50", fg=TEXT_COLOR, font=FONT, width=55)
        self.entry.pack(side=TOP)

        send = Button(self.root, text="Manual Narration", font=FONT_BOLD, bg=BG_GRAY, command=self.manual_narration_change)
        send.pack(side=TOP)

        info("Starting GUI")
        Thread().start()
        self.root.after(100, self.process_event_queue)
        
        self.root.mainloop()

    def start(self):
        self.timer_mgr.start_timers()

        info("Started story engine")

        if self.use_gui:
            self.init_gui()
        else:
            self.poll_input()

    def stop(self):
        self.timer_mgr.stop_timers()

    def poll_input(self):
        while True:
            x = input(">>> ")
            if x == "exit":
                self.stop()
                return
            elif "narrate" in x:
                text = x.split("narrate ")[1]
                self.manual_narration_change(text)
            elif x == "h" or x == "help":
                print("Commands:\n \
                    help - print this help message\n \
                    narrate <str> - manually narrate\n \
                    exit - exit the program")
            else:
                print("Unknown command")

    def dispatch_narration(self, event: Event, manual: bool = False):
        info("%sNarration Change: %s" % ("Manual " if manual else "", event.get_message()))
        self.public_mem.append(event)
        self.agent_mgr.dispatch_narration(event)

    def manual_narration_change(self, text: str = ""):
        event: Event

        if text == "":
            send = "Narration (manual): " + self.entry.get()
            self.txt.insert(END, "\n" + send)
            event = Event.create_narration_event(self.narrator, self.entry.get())
        else:
            event = Event.create_narration_event(self.narrator, text)

        self.dispatch_narration(event, True)

    @TimerManager.timer_callback
    def poll_event_queue(self):
        debug("Polling Event Queue")
        event: Event = None
        while not self.queue.empty():
            event = self.queue.get(block=False)
                
            debug("Received event:\n\t%s" % event)
            self.process_event(event)

            if self.use_gui:
                self.txt.insert(END, "\n" + "%s" % event)
                # self.root.after(100, self.process_event_queue) # TODO this line needed for gui?

    def process_event(self, event: Event):
        if event.get_event_type() == EventType.NarrationEvent:
            self.dispatch_narration(event)
        elif event.get_event_type() == EventType.ReverieEvent or event.get_event_type == EventType.ActionEvent:
            self.agent_mgr.dispatch(event)
        else:
            warn("Unknown event type: %s. Ignoring" % event.get_event_type())

    @TimerManager.timer_callback
    def debug_timer(self):
        debug("[DEBUG_TIMER - Engine] Public Memory:\n%s" % self.narrator.get_narration())
        self.narrator.debug_timer()
        self.agent_mgr.debug_timer()