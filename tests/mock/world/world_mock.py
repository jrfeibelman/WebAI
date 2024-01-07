from pytest import fixture
from typing import List, Tuple

from rtai.utils.config import Config
from rtai.world.world import World
from rtai.world.world_map.arena import Arena

@fixture(scope="session")
def mock_world(mock_config_base: Config):
    return World(mock_config_base)

class TestWorld(World):
    def __init__(self, cfg: Config):
        super().__init__(cfg)

    def load_from_files(self, dir_path: str) -> None:
        self.world_map.add_world(world=0)
        self.world_map.add_sector(world=0, sector=0)
        self.world_map.add_arena(world=0, sector=0, arena=Arena())
        self.world_map.add_arena(world=0, sector=0, arena=Arena())
        self.world_map.add_arena(world=0, sector=0, arena=Arena())