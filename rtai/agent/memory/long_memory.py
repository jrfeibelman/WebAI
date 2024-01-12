from typing import Tuple, Set, Dict, List, OrderedDict
from numpy import uint64, float32

from rtai.utils.datetime import datetime, timedelta
from rtai.core.event import EventType, Event
from rtai.agent.cognition.concept_node import ConceptNode
from rtai.agent.behavior.action import Action
from rtai.agent.behavior.chat import Chat
from rtai.agent.persona import Persona
from rtai.world.clock import clock
from collections import OrderedDict
from rtai.agent.retriever import Retriever
import faiss
from sentence_transformers import SentenceTransformer

# storage class to manage concept insertion
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

    def __init__(self, persona: Persona):
        """_summary_ Constructor for an agent's long term memory.

        Args:
            persona (Persona): persona of the agent
        """
        self.persona = persona

        self.id_to_node: OrderedDict[int, ConceptNode] = {} # Do we need ordered dict?
        
        self.seq_action: List[ConceptNode] = []
        self.seq_thought: List[ConceptNode] = []
        self.seq_chat: List[ConceptNode] = []

        self.current_narration: str = "" # should this be here?

        '''
        Embeddings
        '''
        self.embeddings_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        embeddings_dim = 768
        self.index = faiss.IndexFlatL2(embeddings_dim)

        self.retriever = Retriever(self.embeddings_model, self.index, self.id_to_node)

    def create_embeddings(self):
        '''
        Creates embeddings of all the content in long term memory and adds the index
        '''
        # grab the content from storage
        sentences = [concept.content for concept in self.id_to_node.values()]
        embeddings = self.embeddings_model.encode(sentences)

        # faiss set index
        faiss.normalize_L2(embeddings) # generate embeddings on the entire storage
        # self.index = None

        # create a new index
        index = faiss.IndexFlatL2(768)
        index.add(embeddings)
        self.index = index
        self.retriever.update_index(self.index)
     
    def search_embeddings(self, query: str, k: int) -> Tuple[List[int], List[float]]:
        '''
        searches the embeddings for the query and returns the distances and indices of the top k results
        '''
        query_embedding = self.embeddings_model.encode([query]) # query needs to be a list
        faiss.normalize_L2(query_embedding)
        distances, indices = self.index.search(query_embedding, k) # get the top k serarch embeddings
        return distances, indices  # we probably want the raw content?

    def add_concept(self, content: str, event_type: EventType = None, expiration: timedelta = None) -> ConceptNode:
        # print(content)
        node_id = len(self.id_to_node.keys())

        if event_type == EventType.ChatEvent:
            # TODO if chat event, summarize the chat and add to long term memory
            pass

        # TODO calculate importance using LLM
        importance: float32 = 1.0
        
        expiration = timedelta(days=15) # expiration function of importance

        node = ConceptNode(node_id=node_id, content=content, event_type=event_type, importance=importance, expiration=expiration)  # TODO: do the call

        # TODO: decide when to update embeddings - convert agent concept to embedding and store
        
        # Fast Access dictionary caches
        self.id_to_node[node_id] = node
        if event_type == EventType.ThoughtEvent:
            self.seq_thought.append(node)
        elif event_type == EventType.ActionEvent:
            self.seq_action.append(node)
        elif event_type == EventType.ChatEvent:
            self.seq_chat.append(node)

        # recalculate the embeddings everytime a new concept node is added
        self.create_embeddings()
        return node
    
    def process_narration(self, narration: str) -> ConceptNode:
        """ TODO : implement function to add a new narration change to long term memory long term memory
                - Convert Action to ConceptNode
        """

        """_summary_ TODO function to add a new narration change to long term memory

        Args:
            narration (str): narration change to store in memory

        Returns:
            ConceptNode: created ConceptNode from the input action
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