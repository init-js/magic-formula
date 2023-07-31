
class ApplicationError(Exception):
    pass


class ScraperError(ApplicationError):
    def __init__(self, url, *args):
        super(ScraperError, self).__init__(*args)
        self.url = url


class NoSuchSymbol(ApplicationError):
    def __init__(self, symbol, *args):
        super(NoSuchSymbol, self).__init__(*args)
        self.symbol = symbol

    def __str__(self):
        return "NoSuchSymbol(%s)" % (self.symbol,)