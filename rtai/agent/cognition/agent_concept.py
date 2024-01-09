from typing import Set, Tuple
from numpy import uint64, uint8
from rtai.core.event import EventType

from rtai.utils.datetime import datetime, timedelta
from rtai.world.clock import clock

class AgentConcept:
    node_id: str
    node_count: uint64
    type_count: uint64
    event_type: EventType # TODO should probably be a string

    created: datetime
    expiration: datetime # If importance falls below thrshold
    last_accessed: datetime # Might want to make this datetime

    embedding_key: str

    content: str
    importance: uint8 # Importance

    def __init__(self, node_id: str, event_type: EventType, content: str, importance: uint8, expiration: timedelta=None):
        """_summary_ Constructor for an agent concept.

        Args:
            node_id (str): ID of the agent concept node.
            event_type (EventType): type of event the agent concept represents
            content (str): content of the agent concept
            importance (uint8): importance of the agent concept
            expiration (timedelta): expiration time of the agent concept
        """
        
        self.node_id = node_id
        self.event_type = event_type

        self.created = clock.snapshot()
        self.expiration = self.created + expiration if expiration else None
        self.last_accessed = self.created

        self.content = content
        self.importance = importance

    def summary(self) -> str:
        """_summary_ Get a summary of the agent concept.
        """
        return self.content
    
    def __str__(self) -> None:
        return self.summary()

    def __repr__(self) -> None:
        return str(self)
    
    def __lt__(self, other) -> bool:
        return self.node_id < other.node_id

    def __eq__(self, other) -> bool:
        return self.node_id == other.node_id
    
    def __le__(self, other) -> bool:
        return self.node_id <= other.node_id