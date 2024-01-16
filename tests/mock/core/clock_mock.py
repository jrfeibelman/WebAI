from pytest import fixture

from rtai.utils.config import Config
from rtai.core.clock import clock
from rtai.engine.engine import CLOCK_CONFIG
from tests.mock.configs.config_mock import mock_config_base

@fixture(scope="session")
def mock_clock(mock_config_base: Config) -> clock:
    return clock(mock_config_base.expand(CLOCK_CONFIG))