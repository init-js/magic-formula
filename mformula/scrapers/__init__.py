
def cmd_scrape_market(exchange=None, **kwargs):
    from . import tsx
    if exchange not in ("tsx",):
        raise ValueError("cannot scrape " + exchange + ". unrecognized")
    tsx.cmd_show_issuers()


def configure_parsers(main_parsers):
    scrapers_cmd = main_parsers.add_parser("scrapers", help="pull data from the web")
    scrapers_cmd.set_defaults(func=cmd_scrape_market)
