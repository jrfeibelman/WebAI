from typing import List
from queue import Queue

from rtai.environment.world_map.world_map import WorldMap
from rtai.utils.config import Config

LOAD_FROM_FILES = "LoadFromFiles"
LOAD_SHARED_MEMORIES = "LoadSharedMemories"

class World:
    """
    Class for managing the world state. There should only ever be one instance
    - Enforce singleton?
    """
    def __init__(self, cfg: Config, queue: Queue):
        self.cfg: Config = cfg
        self.queue: Queue = queue
        self.shared_memories: List[str] = []

        dir_path: str = cfg.get_value(LOAD_FROM_FILES, "")
        if len(dir_path) > 0:
            self.load_from_files(dir_path)

        self.world_map: WorldMap = WorldMap()

        shared_memories_file: str = cfg.get_value(LOAD_SHARED_MEMORIES, "")
        if len(shared_memories_file) > 0:
            self.shared_memories = self.load_shared_memories(shared_memories_file)

    def initialize(self) -> bool:
        self.setup_world()
        return True

    def update(self) -> None:
        # Update internal logic
        pass
            # LoadFromFiles: ${WEBAI_HOME}/configs/samples/world/world1/
    
    def setup_world(self) -> None:
        # TODO
        pass

    def load_from_files(self, dir_path: str) -> None:
        # TODO
        pass

    def load_shared_memories(self, file_path: str) -> List[str]:
        lines = []
        with open(file_path, "r") as f:
            lines = f.readlines()
        lines = [line.strip() for line in lines]
        return lines
    
    def get_shared_memories(self) -> List[str]:
        return self.shared_memories