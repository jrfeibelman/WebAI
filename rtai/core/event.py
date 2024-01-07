from enum import Enum
from numpy import uint16

from rtai.utils.time import now
from rtai.agent.abstract_agent import AbstractAgent

class EventType(Enum):
    InvalidEvent=uint16(0)
    ThoughtEvent=uint16(1)
    ReverieEvent=uint16(2)
    ActionEvent=uint16(3)
    ChatEvent=uint16(4)
    NarrationEvent=uint16(5)
    EventTypeLength=uint16(6)

class Event:   
    # TODO make this an abstract class, and subtype Event for each EventType implementing abstract methods dispatch(), releaseMeToPool()
    timestamp: str
    msg: str
    event_type: EventType
    sender: AbstractAgent
    # Receiver should only be used for chats, and should contain the agent name to send the chat request to
    receiver: str

    __slots__ = ['timestamp', 'event_type', 'sender', 'msg']

    def __init__(self):
        raise RuntimeError('Use Factory Methods Instead')
    
    @classmethod
    def _create_event(cls, event_type: EventType, sender: AbstractAgent, msg: str):
        e =  cls.__new__(cls)
        e.timestamp = now()
        e.event_type = event_type
        e.sender = sender.get_name()
        e.msg = msg
        return e
    
    @classmethod
    def create_thought_event(cls, sender: AbstractAgent, msg: str):
        return cls._create_event(EventType.ThoughtEvent, sender, msg)
    
    @classmethod
    def create_reverie_event(cls, sender: AbstractAgent, msg: str):
        return cls._create_event(EventType.ReverieEvent, sender, msg)
    
    @classmethod
    def create_action_event(cls, sender: AbstractAgent, msg: str):
        return cls._create_event(EventType.ActionEvent, sender, msg)
    
    @classmethod
    def create_chat_event(cls, sender: AbstractAgent, msg: str):
        return cls._create_event(EventType.ChatEvent, sender, msg)
    
    @classmethod
    def create_narration_event(cls, sender: AbstractAgent, msg: str):
        return cls._create_event(EventType.NarrationEvent, sender, msg)
    
    @classmethod
    def create_empty_event(cls):
        e =  cls.__new__(cls)
        e.timestamp = now()
        e.event_type = EventType.InvalidEvent
        e.sender = ""
        e.msg = ""
        return e

    # TODO Make Event an abstract class and make this method virtual
    def clear(self):
        self.timestamp = ""
        self.event_type = EventType.InvalidEvent
        self.sender = None
        self.msg = ""

    def get_message(self):
        return self.msg

    def get_event_type(self):
        return self.event_type
    
    def get_timestamp(self):
        return self.timestamp
    
    def get_sender(self):
        return self.sender

    def get_receiver(self):
        return self.receiver

    def __str__(self):
        return "[%s] [%s] (%s) %s" % (self.timestamp, self.event_type, self.sender, self.msg)
    
    def __repr__(self):
        return "%s: %s" % (self.sender, self.msg)