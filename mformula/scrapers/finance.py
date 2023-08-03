from pandas import DataFrame, Series
import yfinance as yf
from requests.exceptions import HTTPError
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter

from mformula.errors import NoSuchSymbol
from mformula.version import __version__


class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass


def get_yfinance_session():
    """use this to ratelimit calls to yahoo finance"""
    if get_yfinance_session.singleton is None:
        session = CachedLimiterSession(
            limiter=Limiter(RequestRate(2, Duration.SECOND*5)),  # max 2 requests per 5 seconds
            bucket_class=MemoryQueueBucket,
            expire_after=60,  # seconds
            backend=SQLiteCache("yfinance.cache"),
        )
        session.headers['User-Agent'] = 'mformula ' + __version__
        get_yfinance_session.singleton = session
    return get_yfinance_session.singleton


get_yfinance_session.singleton = None


def get_quarterly_balance_sheet(symbol):
    ticker = yf.Ticker(symbol, session=get_yfinance_session())
    try:
        bal_sheet: DataFrame
        bal_sheet = ticker.quarterly_balance_sheet
    except HTTPError as he:
        if he.response.status_code == 404:
            raise NoSuchSymbol(symbol)
        raise
    return bal_sheet


def get_quarterly_income_statement(symbol):
    """gets the quarterly income statement for a given symbol"""
    ticker = yf.Ticker(symbol, session=get_yfinance_session())
    try:
        df: DataFrame
        df = ticker.quarterly_income_stmt
    except HTTPError as he:
        if he.response.status_code == 404:
            raise NoSuchSymbol(symbol)
        raise
    return df


def get_ttm_income_statement(symbol):
    """gets the trailing twelve months (ttm) income statements.
       yahoo finance returns calculations for the two most recent statements.
       column 0 is the latest.
    """
    ticker = yf.Ticker(symbol, session=get_yfinance_session())
    try:
        df: DataFrame
        df = ticker.ttm_income_stmt
    except HTTPError as he:
        if he.response.status_code == 404:
            raise NoSuchSymbol(symbol)
        raise
    return df


def get_company_info(symbol):
    """get basic company info in json"""
    ticker = yf.Ticker(symbol, session=get_yfinance_session())

    try:
        return (ticker.info, ticker.get_major_holders)
    except HTTPError as he:
        if he.response.status_code == 404:
            raise NoSuchSymbol(symbol)
        raise


def get_ticker_history(symbol, period='1mo'):
    """get open and close prices over the past period"""
    ticker = yf.Ticker(symbol, session=get_yfinance_session())

    try:
        return ticker.history(period=period)
    except HTTPError as he:
        if he.response.status_code == 404:
            raise NoSuchSymbol(symbol)
        raise


def cmd_show_income_statement(symbol):
    income_stmt: DataFrame
    income_stmt = get_quarterly_income_statement(symbol)
    ttm: DataFrame
    ttm = get_ttm_income_statement()

    # column names are timestamps --- strip the time portion.
    ttm.columns = Series(ttm.columns.format())
    income_stmt.columns = Series(income_stmt.columns.format())

    # one of the columns in the TTM information has the same timestamp as the
    # latest quarterly report. insert that one to merge the summaries.
    income_stmt.insert(0, income_stmt.columns[0] + " (TTM)", ttm[income_stmt.columns[0]])
    print(income_stmt)


def cmd_show_bal_sheet(symbol):
    bal_sheet = get_quarterly_balance_sheet(symbol)
    print(bal_sheet.to_string())


def cmd_show_ticker_info(symbol):
    info = get_company_info(symbol)

    print(info)

    history = get_ticker_history(symbol)

    print()
    print(history)
