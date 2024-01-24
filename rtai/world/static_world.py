
from typing import List, Tuple
import faiss
from sentence_transformers import SentenceTransformer
from rtai.agent.retriever import Retriever

from rtai.world.world import World

class StaticWorld(World):
    def __init__(self, cfg, queue):
        super().__init__(cfg, queue)
    
        static_world_file: str = cfg.get_value("StaticWorldFile", "")
        self.static_world = []
        if len(static_world_file) > 0:
            self.static_world = self.load_static_world(static_world_file)

        self.embeddings_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        embeddings_dim = 768
        self.index = faiss.IndexFlatL2(embeddings_dim)
        self.retriever = Retriever(self.embeddings_model, self.index, self.static_world)

        self.create_embeddings()

    def load_static_world(self, file_path: str) -> List[str]:
        lines = []
        with open(file_path, "r") as f:
            lines = f.readlines()
        lines = [line.strip() for line in lines]
        return lines
 
    def search_embeddings(self, query: str, k: int) -> Tuple[List[int], List[float]]:
        '''
        searches the embeddings for the query and returns the distances and indices of the top k results
        '''
        query_embedding = self.embeddings_model.encode([query]) # query needs to be a list as it is converted to a vector
        faiss.normalize_L2(query_embedding)
        distances, indices = self.index.search(query_embedding, k) # get the top k serarch embeddings
        return distances, indices  # we probably want the raw content?

    def create_embeddings(self):
        '''
        Creates embeddings of all the content in long term memory and adds the index
        '''
        # grab the content from storage
        embeddings = self.embeddings_model.encode(self.static_world)

        # faiss set index
        faiss.normalize_L2(embeddings) # generate embeddings on the entire storage
        # self.index = None

        # create a new index
        index = faiss.IndexFlatL2(768)
        index.add(embeddings)
        self.index = index