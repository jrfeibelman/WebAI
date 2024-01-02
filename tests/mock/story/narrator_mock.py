from pytest import fixture
from queue import Queue

from rtai.story.narrator import Narrator
from rtai.utils.config import Config
from rtai.llm.llm_client import LLMClient
from rtai.world.clock import WorldClock
from rtai.story.engine import NARRATOR_CONFIG

from tests.mock.configs.config_mock import mock_config_base
from tests.mock.world.world_clock_mock import mock_world_clock
from tests.mock.llm.llm_client_mock import mock_llm_client
from tests.mock.story.engine_mock import mock_worker_queue

@fixture(scope="session")
def mock_narrator(mock_config_base: Config, mock_world_clock: WorldClock, mock_llm_client: LLMClient, mock_worker_queue: Queue) -> Narrator:
    return Narrator(mock_worker_queue, mock_config_base.expand(NARRATOR_CONFIG), client=mock_llm_client, world_clock=mock_world_clock)