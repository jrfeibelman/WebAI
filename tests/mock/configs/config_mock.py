from pytest import fixture
from logging import DEBUG

from rtai.utils.logging import setup_logging, info
from rtai.utils.config import Config, YamlLoader

@fixture(scope="session")
def mock_config_base() -> Config:

    BASE_CONFIG = """
        StoryEngine:
            UseGui: False
            WorkerThreadTimerMs: 1000
            AgentTimerSec: 5
            NarrationTimerSec: 12
            # DebugTimerSec: 30
            # StopAfterCycles: 5 # Exits the program after X cycles
            # StopAfterDays: 1 # Exits the program after X days
            WorldClockScaleMs: 500 # Minutes to milliseconds
        Narrator:
        Agents:
            NumAgents: 4
        LLMClient:
            model_name: "test_llm"
            base_url: "0.0.0.0:0000"
            api_key: "not-needed"
    """

    config = YamlLoader.load_from_string(BASE_CONFIG)
    setup_logging(log_dir='logs', log_name='test', log_level=DEBUG, use_callee_stack=True, log_stdout_pipe=True)
    info("Starting tests")
    yield config
    info("Test Completed")