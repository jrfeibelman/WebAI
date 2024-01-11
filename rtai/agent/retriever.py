
import faiss
import numpy as np
from rtai.utils.datetime import datetime
from typing import List
from time import sleep

'''
https://www.pinecone.io/learn/series/faiss/faiss-tutorial/
'''

class Retriever:
    def __init__(self, embeddings_model, index, storage):
        self.index = index
        self.embeddings_model = embeddings_model
        self.storage = storage
        self.max_retrieval = 1000 # the max number of concepts to retrieve
        self.max_context = 5 # the max number of concepts to use to create a context
    
    def _text_to_vector(self, text):
        query_embedding = self.embeddings_model.encode([text])
        faiss.normalize_L2(query_embedding)
        return query_embedding
    
    def _top_k_similiary_search(self, index, query: str):
        '''
        Searches the faiss index for the k nearest neighbors to the query
        '''
        query_embedding = self._text_to_vector(query)
        num_search_results = min(self.max_retrieval, len(self.storage))
        distances, indices = index.search(query_embedding, num_search_results)
        
        # we just want the distances as lists
        distances_list = distances[0].tolist()
        indices_list = indices[0].tolist()
        
        return distances_list, indices_list

    def _retrieve_concepts_from_indices(self, indices_list):
        '''
        Gets the a list of concepts from a list of indices
        '''
        print(f"Storage is here {self.storage.items()}")
        res = []
        for index in indices_list:
            res.append(self.storage[index])
        # return [self.storage[index] for index in indices_list]
        return res

    def _recency_score(self, concepts) -> List[float]:  # TODO: add the rececy
        '''
        Scores the concepts on how recent it is
        '''
        current_time = datetime.now()
        recency_scores = []
        # print("sleeping for 2 seconds")
        # sleep(2)
        for concept in concepts:
            last_accessed = concept._last_accessed
            recency = last_accessed.calc_timedelta_diff(current_time)
            print (f"recency for {concept} is {recency}")
            recency_scores.append(recency.total_seconds())
        print(f"recency scores are {recency_scores}")
        # return [ for concept in concepts]
        return recency_scores
    
    def _importance_score(self, concepts):
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

    def _calculate_combined_score(self, distances, indices, concepts):
        '''
        given retrieved concepts, calculates final normalized score
        '''
        # relevancy + recency + imporance
        relevance_scores = [1 - distance for distance in distances]
        recency_scores = self._recency_score(concepts)
        importance_scores = self._importance_score(concepts)

        # normalize and sort concepts by score
        raw_score = [sum(score) for score in zip(recency_scores, importance_scores, relevance_scores)]
        print(f"raw score for all retrieved is {raw_score}")
        normalized_score = self._min_max_normalize_scores(raw_score) # map scores to [0, 1]
        print(f"normalized score for all retrieved is {normalized_score}")
        
        # sort the indices by score
        sorted_scores = list(sorted(zip(indices, normalized_score), key=lambda x: x[1], reverse=True)) # indices of the top k
        return sorted_scores
    
    def _create_context(self, sorted_scores, k) -> str:
        '''
        creates a context string from the top k concepts
        '''
        context = ""
        print(f"fetching the top {k} results to create a context string")
        for i, a in enumerate(sorted_scores[:k]):
            print(f"The {i}th result is {self.storage[a[0]]} at index {a[0]} and has score: {a[1]}")
            context += self.storage[a[0]].content
        
        return context
    
    def retrieve_context(self, query, k=3):
        '''
        retrieves a context string composed of the top k concept nodes based off query
        
        fetches up to max retrival contents (similarity to query), then weights importance and recency to further filter to k concepts
        '''
        distances, indices = self._top_k_similiary_search(self.index, query)
        print("faiss distances are", distances)
        print("indices are", indices)
        
        concepts = self._retrieve_concepts_from_indices(indices)
        
        # create final score based off of relevancy, recency, and importance
        sorted_scores = self._calculate_combined_score(distances, indices, concepts)
        print("sorted scores are", sorted_scores)

        # take the top k results and create a context string to be inserted into a prompt
        context = self._create_context(sorted_scores, k)
        
        return context