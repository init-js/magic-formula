from datetime import datetime


def show_date(d: datetime):
    return d.isoformat("T", "milliseconds")


class ApplicationError(Exception):
    pass

class ScraperError(ApplicationError):
    def __init__(self, url, *args):
        super(ScraperError, self).__init__(*args)
        self.url = url


class NoExchangeData(ApplicationError):
    def __init__(self, exchange, *args):
        super(NoExchangeData, self).__init__(" ".join(["no data for this exchange: %s" % exchange] + args))
        self.exchange = exchange


class NoSuchSymbol(ApplicationError):
    def __init__(self, symbol, *args):
        super(NoSuchSymbol, self).__init__(*args)
        self.symbol = symbol

    def __str__(self):
        return "NoSuchSymbol(%s)" % (self.symbol,)