from typing import List

from tests.mock.utils.datetime_mock import mock_datetime

def test_datetime(mock_datetime):
    # mock_datetime = 2023-12-11 10:09 PM
    assert mock_datetime.get_time_str() == "22:09:00"
    assert mock_datetime.get_date_str() == "12/11/2023"
    assert mock_datetime.get_datetime_str() == "12/11/2023 10:09 PM"
    assert mock_datetime.get_date_with_time_str("12:00 AM") == "12/11/2023 12:00 AM"
    assert mock_datetime.get_date_with_time_str("14:00") == "12/11/2023 2:00 PM"
    assert str(mock_datetime) == "12/11/2023 10:09 PM"
    
    mock_datetime.increment_minute()
    
    assert mock_datetime.get_time_str() == "22:10:00"
    assert mock_datetime.get_date_str() == "12/11/2023"
    assert mock_datetime.get_datetime_str() == "12/11/2023 10:10 PM"
    assert str(mock_datetime) == "12/11/2023 10:10 PM"    