from pytest import fixture

from rtai.world.clock import WorldClock

@fixture(scope="session")
def mock_world_clock() -> WorldClock:
    return WorldClock()