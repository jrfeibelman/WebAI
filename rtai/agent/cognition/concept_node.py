from typing import Any, Set, Tuple
from numpy import uint64, uint8
from rtai.core.event import EventType

from rtai.utils.datetime import datetime, timedelta
from rtai.world.clock import clock

class ConceptNode:
    node_id: int
    content: str
    event_type: EventType # TODO: should probably be a string
    importance: int # Importance
    _last_accessed: datetime
    expiration: datetime
    created: datetime

    def __init__(self, node_id: str, event_type: EventType, content: str, importance: uint8, expiration: timedelta=None):
        """_summary_ Constructor for an agent concept.
        TODO: update this docstring
        Args:
            node_id (str): ID of the agent concept node.
            event_type (EventType): type of event the agent concept represents
            content (str): content of the agent concept
            importance (uint8): importance of the agent concept
            expiration (timedelta): expiration time of the agent concept
        """
        self.node_id: str = node_id
        self.content = content
        self.event_type = event_type

        self.created: datetime = clock.snapshot()
        self.expiration: datetime = self.created + expiration if expiration else None
        self._last_accessed = self.created

        self.content = content
        self.importance = importance

    def summary(self) -> str:
        """_summary_ Get a summary of the agent concept.
        """
        return self.content
    
    @property
    def last_accessed(self):
        return self._last_accessed
    
    # @property
    # def content(self):
    #     return self.content
    
    def __getattribute__(self, name: str) -> Any:
        # Check if the attribute being accessed is 'last_accessed'
        if name == 'last_accessed':
            return object.__getattribute__(self, '_last_accessed')
        
        # Update _last_accessed when any attribute (except last_accessed) is accessed
        object.__setattr__(self, '_last_accessed', datetime.now())
        return object.__getattribute__(self, name)
    
    def __str__(self) -> None:
        return self.content # todo print out a nice string rep?

    def __repr__(self) -> None:
        return str(self)
    
    def __lt__(self, other) -> bool:
        return self.node_id < other.node_id

    def __eq__(self, other) -> bool:
        return self.node_id == other.node_id
    
    def __le__(self, other) -> bool:
        return self.node_id <= other.node_id