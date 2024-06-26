from numpy import uint32
from typing import Dict, List, TypeAlias

from rtai.world.world_map.arena import Arena
from rtai.world.world_map.surroundings import Surrounding

Sector: TypeAlias = uint32
World: TypeAlias = uint32

Arenas: TypeAlias = List[Arena]
Sectors: TypeAlias = Dict[Sector, Arenas]
Worlds: TypeAlias = Dict[World, Sectors]

class WorldMap:
    """
        Class to represent the map of the world
        Hierarchical structure:
            - World
                - Sector
                    - Arena
                        - Surroundings
                            - Agent / Game Object
    """
    def __init__(self):
        self.worlds: Worlds = dict()

    def add_world(self, world: World):
        self.worlds[world] = dict()

    def add_sector(self, world: World, sector: Sector):
        if world not in self.worlds:
            self.add_world(world)
        self.worlds[world][sector] = []

    def add_arena(self, world: World, sector: Sector, arena: Arena):
        if world not in self.worlds:
            self.add_world(world)
        if sector not in self.worlds[world]:
            self.add_sector(world, sector)
        self.worlds[world][sector].append(arena)
    