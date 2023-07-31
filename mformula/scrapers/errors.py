
class ScraperError(Exception):
    def __init__(self, url, *args):
        super(ScraperError, self).__init__(*args)
        self.url = url
