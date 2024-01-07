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
        return (self.subject, self.predicate, self.obj)
    
    def __str__(self):
        return self.summary()

    def __repr__(self):
        return self.summary()
    
    def __lt__(self, other):
        return self.node_id < other.node_id

    def __eq__(self, other):
        return self.node_id == other.node_id
    
    def __le__(self, other):
        return self.node_id <= other.node_id