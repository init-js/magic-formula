import os.path
import glob
import logging
import pandas as pd

from datetime import datetime

from . import utils
from . import errors

log = logging.getLogger(__package__)


def with_exchange_suffix(exchange, symbol):
    """appends exchange-specific suffix to a stock"""
    if exchange.lower() == "tsx":
        suffix = ".TO"
    else:
        suffix = ""

    symbol = symbol.upper()
    return symbol if symbol.endswith(suffix) else symbol + suffix


def parse_symbols(symbols_file):
    log.debug("loading symbols file: %s", symbols_file)
    df: pd.DataFrame = pd.read_json(symbols_file)
    return df


def symbol_data(exchange: str, as_of: datetime) -> pd.DataFrame:
    mdata_dir = utils.get_market_data_dir()
    xdir = os.path.join(mdata_dir, exchange)
    timepoints = glob.glob(xdir + "/*/symbols.json")
    
    if not timepoints:
        raise errors.NoExchangeData(exchange)
    
    symbols_listing = utils.select_most_recent(timepoints, utils.FILE_TIME_RE, as_of, utils.FILE_TIME_FMT)

    if not symbols_listing:
        raise errors.NoExchangeData(exchange, "(as of: %s)" % errors.show_date(as_of))

    return parse_symbols(symbols_listing)

def cmd_show_symbols(exchange=None, **kwargs):
    print(symbol_data(exchange, datetime.utcnow()))


def configure_parsers(main_parsers):
    symbols_cmd = main_parsers.add_parser("symbols", help="generate list of symbols")
    symbols_cmd.set_defaults(func=cmd_show_symbols)
