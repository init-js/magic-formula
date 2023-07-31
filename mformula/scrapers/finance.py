from pandas import DataFrame
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


def cmd_show_income_statement(symbol):
    ticker = yf.Ticker(symbol, session=get_yfinance_session())

    try:
        income_stmt: DataFrame
        income_stmt = ticker.quarterly_income_stmt
    except HTTPError as he:
        if he.response.status_code == 404:
            raise NoSuchSymbol(symbol)
        raise
    income_stmt.insert(0, "TTM", income_stmt.sum(axis=1))
    print(income_stmt)

def cmd_show_bal_sheet(symbol):
    ticker = yf.Ticker(symbol, session=get_yfinance_session())

    try:
        bal_sheet: DataFrame
        bal_sheet = ticker.balance_sheet
    except HTTPError as he:
        if he.response.status_code == 404:
            raise NoSuchSymbol(symbol)
        raise
    print(bal_sheet)


def cmd_show_ticker_info(symbol):
    ticker = yf.Ticker(symbol, session=get_yfinance_session())

    try:
        print(ticker.info)
    except HTTPError as he:
        if he.response.status_code == 404:
            raise NoSuchSymbol(symbol)
        raise

    print()
    print(ticker.history(period='1mo'))
