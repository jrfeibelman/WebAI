from numpy import uint32

from rtai.world.world_map.arena import Arena
from rtai.world.world_map.surroundings import Surrounding

class Location:
    """
        Class to represent a location for any agent or game object in the world
        Hierarchical structure:
            - World
                - Sector
                    - Arena
                        - Surroundings
                            - Agent / Game Object

    """
    def __init__(self):
        self.world_num: uint32 = uint32(0)
        self.sector: uint32 = uint32(0)
        self.arena: Arena = None
        self.surroundings: Surrounding = None
        self.obj_desc: str = ''
        self.is_agent: bool = False