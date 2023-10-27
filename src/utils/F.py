import time
from datetime import datetime, timezone, timedelta
import pandas as pd

def get_midnight_timestamp(t):
    """
    Convert a timestamp to the midnight timestamp of the same day (UTC+8).
    Args:
    - t (float): The original timestamp.
    Returns:
    - float: The midnight timestamp (UTC+8) of the same day.
    """
    # Convert the timestamp to UTC+8 local time
    local_time = datetime.fromtimestamp(t, tz=timezone(timedelta(hours=8)))
    # Get the midnight time of the same day
    midnight_local = local_time.replace(hour=0, minute=0, second=0, microsecond=0)
    # Convert the local time back to a timestamp
    return int(midnight_local.timestamp())

def time_now():
    t = time.time()
    return datetime.fromtimestamp(t, tz=timezone(timedelta(hours=8)))
    