from typing import Any, Set, Tuple
from numpy import uint64, uint8
from rtai.core.event import EventType

from rtai.utils.datetime import datetime

class AgentConcept:
    node_id: int
    content: str
    event_type: EventType # TODO: should probably be a string
    importance: int # Importance

    created: datetime # when the AgentConcept was created
    expiration: datetime # If importance falls below thrshold
    _last_accessed: datetime

    def __init__(self, node_id: int, content: str, event_type: EventType, created: datetime, expiration: datetime, importance: uint8):
        """_summary_ Constructor for an agent concept.
        TODO: update this docstring
        Args:
            node_id (str): ID of the agent concept node.
            event_type (EventType): type of event the agent concept represents
            created (datetime): creation time of the agent concept
            expiration (datetime): expiration time of the agent concept
            content (str): content of the agent concept
            importance (uint8): importance of the agent concept
        """
        self.node_id = node_id
        self.content = content
        self.event_type = event_type
        self.expiration = expiration
        self._last_accessed = created # initially set _last_accessed to created when an attribute is accessed

        self.content = content
        self.importance = importance

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