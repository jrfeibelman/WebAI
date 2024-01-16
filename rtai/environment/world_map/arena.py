from typing import List
from numpy import zeros

from rtai.environment.world_map.surroundings import Surrounding

class Arena:
    def __init__(self, surroundings: List[Surrounding]):
        self.surroundings: List[Surrounding] = surroundings
        size = len(self.surroundings)

        # Initialize a size x size adjancency matrix with zeros
        self.arena_graph = zeros((size, size))

    def add_graph_edge(self, u, v):
        # Add an edge by setting the corresponding matrix elements to 1
        self.arena_graph[u][v] = 1
        self.arena_graph[v][u] = 1  # Since the graph is undirected

    def remove_graph_edge(self, u, v):
        # Remove an edge by setting the corresponding matrix elements to 0
        self.arena_graph[u][v] = 0
        self.arena_graph[v][u] = 0

    def has_graph_edge(self, u, v):
        # Returns True if there's an edge between u and v
        return self.arena_graph[u][v] == 1

    def __str__(self):
        return str(self.arena_graph)