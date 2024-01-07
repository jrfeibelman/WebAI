from queue import Queue
from pytest import fixture

@fixture(scope="session")
def mock_worker_queue() -> Queue:
    return Queue()