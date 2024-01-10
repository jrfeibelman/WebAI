from typing import List

from rtai.agent.agent import Agent

from tests.mock.agent.agent_manager_mock import mock_agent_manager
from tests.mock.configs.config_mock import mock_config_base
from tests.mock.llm.llm_client_mock import mock_llm_client
from tests.mock.story.engine_mock import mock_worker_queue

def test_agent_manager_base(mock_agent_manager):
    agents: List[Agent] = mock_agent_manager.agents
    for a in agents:
        assert len(a.s_mem.daily_plan) == 0
        assert len(a.s_mem.daily_req) == 0

    mock_agent_manager.update()

    for a in agents:
        assert len(a.s_mem.daily_plan) > 0
        assert len(a.s_mem.daily_req) > 0