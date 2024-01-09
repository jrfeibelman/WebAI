from typing import Tuple, Set, Dict, List, OrderedDict
from numpy import uint64

from rtai.utils.datetime import datetime, timedelta
from rtai.core.event import EventType, Event
from rtai.agent.cognition.agent_concept import AgentConcept
from rtai.agent.behavior.action import Action
from rtai.agent.behavior.chat import Chat
from rtai.agent.persona import Persona
from rtai.world.clock import WorldClock
from collections import OrderedDict
import faiss
from sentence_transformers import SentenceTransformer

# class ConceptStorage(dict):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.id_counter = 0

#     def insert_object(self, other_field):
#         self.id_counter += 1
#         new_object = YourObject(other_field=other_field)
#         new_object.id = self.id_counter
#         self[self.id_counter] = new_object

class LongTermMemory:
    """_summary_ Class to represent the long term memory of an agent."""

    def __init__(self, persona: Persona, world_clock: WorldClock):
        """_summary_ Constructor for an agent's long term memory.

        Args:
            persona (Persona): persona of the agent
            world_clock (WorldClock): world clock of the agent
        """
        self.persona = persona
        self.world_clock = world_clock

        self.storage: OrderedDict[int, AgentConcept] = {}
        
        self.seq_action: List[AgentConcept] = []
        self.seq_thought: List[AgentConcept] = []
        self.seq_chat: List[AgentConcept] = []

        self.current_narration: str = "" # should this be here?

        # variables for RAG pipeline
        self.embeddings_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2') # <- one

        # self.vectorstore = None
        embeddings_dim = 768 # TODO: add as a config value
        self.index = faiss.IndexFlatL2(embeddings_dim) # n agent, n indexes

    def create_embeddings(self):
        '''
        Creates embeddings of all the content in long term memory and adds the index
        '''
        # grab the content from storage
        sentences = [concept.content for concept in self.storage.values()]
        embeddings = self.embeddings_model.encode(sentences)

        # faiss set index
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
     
    def search_embeddings(self, query: str, k: int) -> Tuple[List[int], List[float]]:
        '''
        searches the embeddings for the query and returns the top k results
        '''
        query_embedding = self.embeddings_model.encode([query]) # query needs to be a list
        faiss.normalize_L2(query_embedding)
        distances, indices = self.index.search(query_embedding, k) # get the top k serarch embeddings
        return distances, indices  # we probably want the raw content?

    def add_concept(self, content: str, event_type: EventType, expiration: timedelta = None):
        node_id = len(self.storage) + 1
        
        created = datetime.now() # should move this logic into agent_concept? TODO: change this back to using the world clock
        expiration_date = timedelta(days=15) # expiration function of importance
        expiration = created + expiration_date

        concept = AgentConcept(node_id=node_id, content=content, event_type=event_type, created=created, expiration=expiration, importance=10)  # TODO: do the call
        self.storage[node_id] = concept

        # TODO: decide when to update embeddings
        
        return concept # may not return concept later
    
    # TODO: collapse add_plan, add_action, add_chat into add_concept
    def add_plan(self, expiration : datetime, subject: str, predicate: str, 
                    obj: str, content: str) -> AgentConcept:
        """_summary_ Add a new plan to long term memory

        Args:

            thought (str): string representation of the plan description

        Returns:
            AgentConcept: created AgentConcept from the input parameters
        """
        # Setting up the node ID and counts
        node_count = len(self.id_to_node.keys()) + 1
        event_type = EventType.ThoughtEvent
        node_id = f"node_{str(node_count)}"

        # TODO calculate importance using LLM
        importance = 10

        # Create the ConceptNode object
        created = self.world_clock.snapshot()
        node = AgentConcept(node_id, event_type, created, expiration, content, importance)

        # TODO convert agent concept to embedding and store
        
        # Fast Access dictionary caches
        self.seq_thought.append(node)
        self.id_to_node[node_id] = node

        return node

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

        # TODO calculate importance using LLM
        importance = 10

        # Create the ConceptNode object to store into memory
        created = self.world_clock.snapshot()
        s, p, o = (self.persona.name, "act", action.description) # TODO
        node = AgentConcept(node_id, event_type, created, action.completion_time + timedelta(days=30), action.description, importance)
        
        # TODO convert agent concept to embedding and store

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

        # TODO summarize conversation to then store
        conversation_summary = ""

        # TODO calculate importance using LLM
        importance = 10

        # Create the ConceptNode object to store into memory
        s, p, o = (self.persona.name, "chat", chat.description) # TODO
        node = AgentConcept(node_id, event_type, chat.created, chat.completion_time + timedelta(days=30), conversation_summary, importance)
        
        # TODO convert agent concept to embedding and store

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

    def save_to_file(self, file_path: str) -> None:
        """_summary_ Save the long term memory to a file.

        Args:
            file_path (str): path to the file to write long term memory to
        """
        pass

    def load_from_file(self, file_name: str) -> bool:
        """_summary_ Load the long term memory from a file.

        Args:
            file_name (str): name of the file to load long term memory from

        Returns:
            bool: True if the long term memory was loaded successfully, False otherwise
        """
        pass