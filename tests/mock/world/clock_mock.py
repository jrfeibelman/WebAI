from pytest import fixture

from rtai.utils.config import Config
from rtai.world.clock import clock
from tests.mock.configs.config_mock import mock_config_base

@fixture(scope="session")
def mock_clock(mock_config_base: Config) -> clock:
    return clock(mock_config_base.expand("World").expand("Clock"))