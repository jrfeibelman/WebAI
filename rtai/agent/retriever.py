import datetime
import faiss


class Retriever:
    def __init__(self, embedding_model, index, storage):
        self.index = index
        self.embedding_model = embedding_model
        self.storage = storage
    
    def _text_to_vector(self, text):
        query_embedding = self.embeddings_model.encode(text)
        faiss.normalize_L2(query_embedding)
        return query_embedding
    
    def _top_k_similiary_search(self, index, query: str, k=3):
        '''
        Searches the faiss index for the k nearest neighbors to the query
        '''
        query_embedding = self._text_to_vector(query)
        distances, indices = index.search(query_embedding, k)
        return distances, indices

    def _retrieve_concepts_from_indices(self, indices):
        '''
        Gets the a list of concepts from a list of indices
        '''
        return [self.storage[index] for index in indices]

    def recency_score(self, concepts):  # TODO: check that this works
        '''
        Scores the concepts on how recent it is
        '''
        current_time = datetime.datetime.now()
        return [current_time - concept._last_accessed for concept in concepts]
    
    def importance_score(self, concepts):
        '''
        Scores the concepts on how frequently it is used
        '''
        return [concept.importance for concept in concepts]
    
    def _min_max_normalize_scores(self, scores):
        '''
        Normalizes scores to be between 0 and 1
        '''
        min_score = min(scores)
        max_score = max(scores)
        return [(score - min_score) / (max_score - min_score) for score in scores]

    def retrieve(self, query, k=1):
        '''
        retrieves the content of top k concept nodes based off recency + importance + relevance
        '''
        distances, indices = self._top_k_similiary_search(self.index, query)
        concepts = self._retrieve_concepts_from_indices(indices)
        
        recency_scores = self.recency_score(concepts)
        importance_scores = self.importance_score(concepts)
        relevance_scores = [1 - distance for distance in distances]  # 1 - distance because we want higher distance to be lower score

        raw_score = [sum(score) for score in zip(recency_scores, importance_scores, relevance_scores)]
        normalized_score = self._min_max_normalize_scores(raw_score) # map scores to [0, 1]
        sorted_scores = sorted(zip(indices, normalized_score), key=lambda x: x[1], reverse=True)

        return sorted_scores[:k]