from datetime import datetime
import logging
from .. import symbols
from . import finance

log = logging.getLogger(__package__)

def refresh_company(symbol, progress=(0, 0)):
    log.debug("processing symbol %s (%d of %d)", symbol, progress[0], progress[1])

    history = finance.get_ticker_history(symbol, period='1mo')
    last_row = history.iloc[-1]

    sample_date = last_row.name.to_pydatetime()
    print(sample_date)

    info = finance.get_company_info(symbol)
    print(info)

def refresh_all_companies(exchange, symbol_range=("", "")):
    scrape_date = datetime.utcnow()
    clist = symbols.symbol_data(exchange, scrape_date)

    if clist.empty:
        log.error("No companies found for exchange: %s", exchange)
        return
    
    filtered = [name for name in clist.index
                if (name >= symbol_range[0]) and ((symbol_range[1] >= name) if symbol_range[1] else True)]

    for (iname, name) in enumerate(filtered):
        yahoo_symbol = symbols.with_exchange_suffix(exchange, name)
        refresh_company(yahoo_symbol, progress=(iname, len(filtered)))
