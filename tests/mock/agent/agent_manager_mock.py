from pytest import fixture
from queue import Queue

from rtai.agent.agent_manager import AgentManager
from rtai.utils.config import Config
from rtai.llm.llm_client import LLMClient
from rtai.world.clock import WorldClock
from rtai.utils.logging import error
from rtai.utils.config import Config

from tests.mock.configs.config_mock import mock_config_base
from tests.mock.world.world_clock_mock import mock_world_clock
from tests.mock.llm.llm_client_mock import mock_llm_client
from tests.mock.story.engine_mock import mock_worker_queue

@fixture(scope="session")
def mock_agent_manager(mock_config_base: Config, mock_world_clock: WorldClock, mock_llm_client: LLMClient, mock_worker_queue: Queue):
    agent_mgr = AgentManager(mock_worker_queue, mock_config_base, mock_llm_client, mock_world_clock)
    assert agent_mgr.initialize()
    return agent_mgr
