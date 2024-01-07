from typing import Set, Tuple
from numpy import uint64
from rtai.core.event import EventType

from rtai.utils.datetime import datetime

class AgentConcept:
    node_id: str
    node_count: uint64
    type_count: uint64
    event_type: EventType # TODO should probably be a string

    created: datetime
    expiration: datetime
    last_accessed: datetime # Might want to make this datetime

    subject: str
    predicate: str
    obj: str

    description: str

    def __init__(self, node_id: str, node_count: uint64, type_count: uint64, event_type: EventType, created: datetime, 
                 expiration: datetime, subject: str, predicate: str, obj: str, description: str):
        """_summary_ Constructor for an agent concept.

        Args:
            node_id (str): ID of the agent concept node.
            node_count (uint64): _description_
            type_count (uint64): _description_
            event_type (EventType): type of event the agent concept represents
            created (datetime): creation time of the agent concept
            expiration (datetime): expiration time of the agent concept
            subject (str): subject of the agent concept, which is the noun performing the event
            predicate (str): predicate of the agent concept, which is the verb describing the event
            obj (str): object of the agent concept, which is the noun receiving the event
            description (str): description of the agent concept
        """
        
        self.node_id = node_id
        self.node_count = node_count
        self.type_count = type_count
        self.event_type = event_type

        self.created = created
        self.expiration = expiration
        self.last_accessed = self.created

        self.subject = subject
        self.predicate = predicate
        self.obj = obj

        self.description = description

    def summary(self) -> Tuple[str, str, str]:
        """_summary_ Get a summary of the agent concept.
        
        Returns:
            Tuple[str, str, str]: A tuple of the subject, predicate, and object of the agent concept.
        """
        return (self.subject, self.predicate, self.obj)
    
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