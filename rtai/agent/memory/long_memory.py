from typing import Tuple, Set, Dict, List
from numpy import uint64

from rtai.utils.datetime import datetime, timedelta
from rtai.core.event import EventType, Event
from rtai.agent.cognition.agent_concept import AgentConcept
from rtai.agent.behavior.action import Action
from rtai.agent.behavior.chat import Chat
from rtai.agent.persona import Persona
from rtai.world.clock import WorldClock

class LongTermMemory:
    """_summary_ Class to represent the long term memory of an agent.


    """
    def __init__(self, persona: Persona, world_clock: WorldClock):
        self.persona = persona
        self.world_clock = world_clock

        self.id_to_node: Dict[str, AgentConcept] = dict()
        self.seq_action: List[AgentConcept] = []
        self.seq_thought: List[AgentConcept] = []
        self.seq_chat: List[AgentConcept] = []

        self.current_narration: str = ""

    def add_plan(self, expiration : datetime, subject: str, predicate: str, 
                    obj: str, thought: str) -> AgentConcept:
        """_summary_ Add a new plan to long term memory

        Args:
            created (datetime): time that plan was created
            expiration (datetime): time to expire the plan from long term memory
            subject (str): subject of the plan
            predicate (str): predicate of the plan
            obj (str): object of the plan
            thought (str): string representation of the plan description

        Returns:
            AgentConcept: created AgentConcept from the input parameters
        """
        # Setting up the node ID and counts
        node_count = len(self.id_to_node.keys()) + 1
        type_count = len(self.seq_thought) + 1
        event_type = EventType.ThoughtEvent
        node_id = f"node_{str(node_count)}"

        # TODO incorporate embeddings somehow

        # Create the ConceptNode object
        created = self.world_clock.snapshot()
        node = AgentConcept(node_id, node_count, type_count, event_type, created, expiration, subject, predicate, obj, thought)
        
        # Fast Access dictionary caches
        self.seq_thought.append(node)
        self.id_to_node[node_id] = node

        return node
    
    def add_thought(self) -> AgentConcept:
        pass

    def add_reverie(self) -> AgentConcept:
        pass

    def add_action(self, action: Action) -> AgentConcept:
        """_summary_ TODO function to add a new completed action to long term memory by converting an Action to an AgentConcept

        Args:
            action (Action): action to store in memory

        Returns:
            AgentConcept: created AgentConcept from the input action
        """

        # Setting up the node ID and counts
        node_count = len(self.id_to_node.keys()) + 1
        type_count = len(self.seq_thought) + 1
        event_type = EventType.ActionEvent
        node_id = f"node_{str(node_count)}"

        # TODO incorporate embeddings somehow

        # Create the ConceptNode object to store into memory
        created = self.world_clock.snapshot()
        s, p, o = (self.persona.name, "act", action.description) # TODO
        node = AgentConcept(node_id, node_count, type_count, event_type, created, action.completion_time + timedelta(days=30), s, p, o, action.description)
        
        # Fast Access dictionary caches
        self.seq_action.append(node)
        self.id_to_node[node_id] = node

        return node
    
    def add_chat(self, chat: Chat) -> AgentConcept:
        """_summary_ TODO function to add a new completed chat to long term memory by converting a Chat to an AgentConcept

        Args:
            action (Action): action to store in memory

        Returns:
            AgentConcept: created AgentConcept from the input action
        """

        # Setting up the node ID and counts
        node_count = len(self.id_to_node.keys()) + 1
        type_count = len(self.seq_thought) + 1
        event_type = EventType.ActionEvent
        node_id = f"node_{str(node_count)}"

        # TODO incorporate embeddings somehow

        # Create the ConceptNode object to store into memory
        s, p, o = (self.persona.name, "chat", chat.description) # TODO
        node = AgentConcept(node_id, node_count, type_count, event_type, chat.created, chat.completion_time + timedelta(days=30), s, p, o, chat.description)
        
        # Fast Access dictionary caches
        self.seq_chat.append(node)
        self.id_to_node[node_id] = node

        return node
    
    def process_narration(self, narration: str) -> AgentConcept:
        """ TODO : implement function to add a new narration change to long term memory long term memory
                - Convert Action to AgentConcept
        """

        """_summary_ TODO function to add a new narration change to long term memory

        Args:
            narration (str): narration change to store in memory

        Returns:
            AgentConcept: created AgentConcept from the input action
        """
        self.current_narration = narration

    def get_summarized_latest_events(self, retention) -> str:
        """_summary_ Get the latest events in the long term memory given agent specific retention

        Args:
            retention (_type_): agent specific retention factor for retrieving long term memory
        Returns:
            str: string summary of latest events in long term memory
        """
        pass

    def save_to_file(self, file_path: str):
        """_summary_ save the current state of long term memory to a file

        Args:
            file_path (str): path to save the file to
        """
        pass