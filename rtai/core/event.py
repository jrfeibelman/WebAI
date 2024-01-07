from enum import Enum
from numpy import uint16

from rtai.utils.datetime import datetime
from rtai.agent.abstract_agent import AbstractAgent
from rtai.utils.datetime import datetime

class EventType(Enum):
    """ _summary_ Enum to represent event types"""
    InvalidEvent=uint16(0)
    ThoughtEvent=uint16(1)
    ReverieEvent=uint16(2)
    ActionEvent=uint16(3)
    ChatEvent=uint16(4)
    NarrationEvent=uint16(5)
    EventTypeLength=uint16(6)

class Event:
    """ _summary_ Class to represent an event

    TODO make this an abstract class, and subtype Event for each EventType implementing abstract methods dispatch(), releaseMeToPool()
    """

    __slots__ = ['timestamp', 'event_type', 'sender', 'msg', 'receiver']

    def __init__(self):
        raise RuntimeError('Use Factory Methods Instead')
    
    @classmethod
    def _create_event(cls, event_type: EventType, sender: AbstractAgent, msg: str, receiver: str='') -> 'Event':
        """ _summary_ Factory method to create an event
        
        Args:
            event_type (EventType): Event type
            sender (AbstractAgent): Sender of event
            msg (str): Message of event
            receiver (str, optional): Receiver of event. Defaults to ''.
        
        Returns:
            Event: Event object
        """
        e =  cls.__new__(cls)
        e.timestamp: datetime = datetime.now()
        e.event_type: EventType = event_type
        e.sender: AbstractAgent = sender.get_name()
        e.msg: str = msg
        # Receiver should only be used for chats, and should contain the agent name to send the chat request to
        e.receiver: str = receiver
        return e
    
    @classmethod
    def create_thought_event(cls, sender: AbstractAgent, msg: str) -> 'Event':
        """ _summary_ Factory method to create a thought event
        
        Args:
            sender (AbstractAgent): Sender of event
            msg (str): Message of event
            
        Returns:
            Event: Event object
        """
        return cls._create_event(EventType.ThoughtEvent, sender, msg)
    
    @classmethod
    def create_reverie_event(cls, sender: AbstractAgent, msg: str) -> 'Event':
        """ _summary_ Factory method to create a reverie event
        
        Args:
            sender (AbstractAgent): Sender of event
            msg (str): Message of event
            
        Returns:
            Event: Event object
        """
        return cls._create_event(EventType.ReverieEvent, sender, msg)
    
    @classmethod
    def create_action_event(cls, sender: AbstractAgent, msg: str) -> 'Event':
        """ _summary_ Factory method to create a action event
        
        Args:
            sender (AbstractAgent): Sender of event
            msg (str): Message of event
            
        Returns:
            Event: Event object
        """
        return cls._create_event(EventType.ActionEvent, sender, msg)
    
    @classmethod
    def create_chat_event(cls, sender: AbstractAgent, msg: str, receiver: str) -> 'Event':
        """ _summary_ Factory method to create a chat event
        
        Args:
            sender (AbstractAgent): Sender of event
            msg (str): Message of event
            
        Returns:
            Event: Event object
        """
        return cls._create_event(EventType.ChatEvent, sender, msg, receiver)
    
    @classmethod
    def create_narration_event(cls, sender: AbstractAgent, msg: str) -> 'Event':
        """ _summary_ Factory method to create a narration event
        
        Args:
            sender (AbstractAgent): Sender of event
            msg (str): Message of event
            
        Returns:
            Event: Event object
        """
        return cls._create_event(EventType.NarrationEvent, sender, msg)
    
    @classmethod
    def create_empty_event(cls) -> 'Event':
        """ _summary_ Factory method to create an empty event
        
        Returns:
            Event: Event object
        """
        e =  cls.__new__(cls)
        e.timestamp = None
        e.event_type = EventType.InvalidEvent
        e.sender = ""
        e.msg = ""
        return e

    # TODO Make Event an abstract class and make this method virtual
    def clear(self) -> None:
        """ _summary_ Method to clear an event"""
        self.timestamp = ""
        self.event_type = EventType.InvalidEvent
        self.sender = None
        self.msg = ""

    def get_message(self) -> str:
        """ _summary_ Method to get the event's message
        
        Returns:
            str: Event message"""
        return self.msg

    def get_event_type(self) -> EventType:
        """ _summary_ Method to get the event's type
        
        Returns:
            EventType: Event type
        """
        return self.event_type
    
    def get_timestamp(self) -> datetime:
        """ _summary_ Method to get the event's timestamp
        
        Returns:
            datetime: Event timestamp
        """
        return self.timestamp
    
    def get_sender(self) -> AbstractAgent:
        """ _summary_ Method to get the event's sender
        
        Returns:
            AbstractAgent: Event sender
        """
        return self.sender

    def get_receiver(self) -> str:
        """ _summary_ Method to get the event's receiver
        
        Returns:
            str: Event receiver
        """
        return self.receiver

    def __str__(self) -> str:
        return "[%s] [%s] (%s) %s" % (self.timestamp, self.event_type, self.sender, self.msg)
    
    def __repr__(self) -> str:
        return "%s: %s" % (self.sender, self.msg)