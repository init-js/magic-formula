import os.path
import pytz
from datetime import datetime
import re

FILE_TIME_FMT = "%Y-%m-%dT%H.%M.%S"
FILE_TIME_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}T\d{2}.\d{2}.\d{2}\b")


def format_datetime_for_files(instant: datetime):
    """formats a datetime to the way we embed them in filenames """
    utc_date = instant.astimezone(pytz.utc)
    return utc_date.strftime(FILE_TIME_FMT)


def create_data_point_dir(exchange: str, date: datetime) -> str:
    """creates (if necessary) the directory that will contain exchange data for the given point in time"""
    mdir = get_market_data_dir()
    mdir = os.path.join(mdir, exchange.lower())
    mdir = os.path.join(mdir, format_datetime_for_files(date))
    os.makedirs(mdir, exist_ok=True)
    return os.path.abspath(mdir)


def get_market_data_dir() -> str:
    """gets the root of the market data directory (abspath)"""
    here = os.path.dirname(__file__)
    mdir = os.path.join(here, "..", "market-data")
    if not os.path.isdir(mdir):
        raise Exception("directory " + mdir + " does not exist")
    return os.path.abspath(mdir)


def index_of_closest_le(arr, needle, key:callable = None):
    """finds the index of the closest value lesser or equal to needle.
       arr is assumed to be sorted.

       if no entry is lesser or equal to needle, -1 is returned.
    """
    def _id(x): return x

    def _cmp(a, b):
        return bool(a > b) - bool(a < b)

    if len(arr) == 0:
        return -1

    key = _id if key is None else key
    low = 0
    high = len(arr) - 1\

    # index of the most recently visited item smaller than needle. (or -1).
    last = -1
    while low <= high:
        mid = (low + high) // 2
        test = key(arr[mid])
        c = _cmp(needle, test)
        print(test, c, "mid=", mid, "low=", low, "hi=", high)
        if c == 0:
            return mid
        if c > 0:
            last = mid
            low = mid + 1
        else:
            high = mid - 1

    return last


def select_most_recent(iter: list[str], date_re: re.Pattern, as_of: datetime, format: str):
    """from the provided entries, which each contain some date string representation which matches
       date_re, pick the entry that is the most recent (in the past) as of date `as_of`.

       Only pass utc datetimes, preferably naive.
    """
    matches = []

    for ent in iter:
        match = date_re.search(ent)
        if not match:
            continue
        start_i, end_i = match.span()
        date_part = ent[start_i:end_i]
        item_date = datetime.strptime(date_part, format)
        matches.append((item_date, ent))

    matches.sort()
    idx = index_of_closest_le(matches, as_of, key=lambda x: x[0])
    return None if idx == -1 else matches[idx][1]
