import os.path
import pytz
from datetime import datetime


def create_data_point_dir(exchange: str, date: datetime) -> str:
    """creates (if necessary) the directory that will contain exchange data for the given point in time"""
    mdir = get_market_data_dir()    
    mdir = os.path.join(mdir, exchange.lower())
    dir_fmt = "%y-%m-%dT%H.%M.%S"
    utc_date = date.astimezone(pytz.utc)
    mdir = os.path.join(mdir, utc_date.strftime(dir_fmt))
    os.makedirs(mdir, exist_ok=True)
    return os.path.abspath(mdir)


def get_market_data_dir() -> str:
    """gets the root of the market data directory (abspath)"""
    here = os.path.dirname(__file__)
    mdir = os.path.join(here, "..", "market-data")
    if not os.path.isdir(mdir):
        raise Exception("directory " + mdir + " does not exist")
    return os.path.abspath(mdir)
