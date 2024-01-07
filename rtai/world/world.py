
from rtai.world.world_map.world_map import WorldMap
from rtai.utils.config import Config

LOAD_FROM_FILES = "LoadFromFiles"

class World:
    """
    Class for managing the world state. There should only ever be one instance
    - Enforce singleton?
    - Own WorldClock()? Would make sense if singleton enforced
    """
    def __init__(self, cfg: Config):
        self.cfg = cfg

        dir_path: str = cfg.get_value(LOAD_FROM_FILES, "")
        if len(dir_path) > 0:
            self.load_from_files(dir_path)

        self.world_map: WorldMap = WorldMap()

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
