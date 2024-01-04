from typing import Tuple, Set, Dict, List
from numpy import uint64

from rtai.utils.datetime import datetime
from rtai.core.event import EventType
from rtai.agent.cognition.agent_concept import AgentConcept
from rtai.agent.cognition.action import Action

class LongTermMemory:
    """
    Class to represent the long term memory of an agent. This class should maintain a ??? of ConceptNodes

    TODO architect underlying data structure
    """
    id_to_node: Dict[str, AgentConcept]
    seq_action: List[AgentConcept]
    seq_thought: List[AgentConcept]
    kw_to_event: Dict[str, List[AgentConcept]]
    kw_to_thought: Dict[str, List[AgentConcept]]
    kw_to_chat: Dict[str, List[AgentConcept]]

    def __init__(self):
        self.id_to_node = dict()
        self.seq_action = []
        self.seq_thought = []
        self.kw_to_event = dict()
        self.kw_to_thought = dict()
        self.kw_to_chat = dict()

    def add_thought(self, created: datetime, expiration : datetime, subject: str, predicate: str, 
                    obj: str, thought: str, keywords: Set[str]) -> AgentConcept:
        # Setting up the node ID and counts
        node_count = len(self.id_to_node.keys()) + 1
        type_count = len(self.seq_thought) + 1
        event_type = EventType.ThoughtEvent
        node_id = f"node_{str(node_count)}"

        # TODO incorporate embeddings somehow

        # Create the ConceptNode object
        node = AgentConcept(node_id, node_count, type_count, event_type, created, expiration, subject, predicate, obj, thought, keywords)
        
        # Fast Access dictionary caches
        self.seq_thought[0:0] = [node]
        keywords = [i.lower() for i in keywords] # This should probably be removed????
        for kw in keywords: 
            if kw in self.kw_to_thought: 
                self.kw_to_thought[kw][0:0] = [node]
            else: 
                self.kw_to_thought[kw] = [node]
        self.id_to_node[node_id] = node

        return node

    def add_reverie(self):
        pass

    def add_action(self, created: datetime, expiration : datetime, subject: str, predicate: str, 
                    obj: str, thought: str, keywords: Set[str]) -> AgentConcept:
        pass

    def add_chat(self): 
        pass

    def get_summarized_latest_events(self, retention): 
        pass

    def save_to_file(self, file_path: str):
        pass