
def cmd_scrape_market(exchange=None, **kwargs):
    from . import tsx
    if exchange not in ("tsx",):
        raise ValueError("cannot scrape " + exchange + ". unrecognized")
    tsx.cmd_write_symbols()


def cmd_show_ticker(exchange=None, symbol=None, **kwargs):
    from . import finance
    if exchange == "tsx":
        symbol += ".to"
    finance.cmd_show_ticker_info(symbol)


def cmd_show_balance_sheet(exchange=None, symbol=None, **kwargs):
    from . import finance
    if exchange == "tsx":
        symbol += ".to"
    finance.cmd_show_bal_sheet(symbol)


def cmd_show_income_stmt(exchange=None, symbol=None, **kwargs):
    from . import finance
    if exchange == "tsx":
        symbol += ".to"
    finance.cmd_show_income_statement(symbol)
    

def configure_parsers(main_parsers):
    scrapers_cmd = main_parsers.add_parser("scrape", help="pull data from the web")
    sub_scrapers = scrapers_cmd.add_subparsers(
        help='The type of scraper to invoke', metavar='CMD',
        dest='scraper_command')

    symbols_cmd = sub_scrapers.add_parser("symbols", help="retrieve list of symbols and save to market-data")
    symbols_cmd.set_defaults(func=cmd_scrape_market)

    parser = main_parsers.add_parser("ticker",
                                     help="show ticker data",
                                     description="access live or historical ticker data for a symbol")
    parser.add_argument("symbol", metavar="SYMBOL", help="the symbol to look for")
    parser.set_defaults(func=cmd_show_ticker)

    parser = main_parsers.add_parser("balance",
                                     help="show balance sheet info",
                                     description="access live or historical balance sheet" +
                                                 " info for a company (by symbol)")
    parser.add_argument("symbol", metavar="SYMBOL", help="the symbol to look for")
    parser.set_defaults(func=cmd_show_balance_sheet)

    parser = main_parsers.add_parser("income",
                                     help="show company income statement info",
                                     description="access latest income statement" +
                                                 " info for a company (by symbol)")
    parser.add_argument("symbol", metavar="SYMBOL", help="the symbol to look for")
    parser.set_defaults(func=cmd_show_income_stmt)
