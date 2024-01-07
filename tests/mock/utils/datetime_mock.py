from pytest import fixture

from rtai.utils.datetime import datetime

@fixture(scope="session")
def mock_datetime():
    dt = datetime("2023-12-11 22:09")
    return dt
