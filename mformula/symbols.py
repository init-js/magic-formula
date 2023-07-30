
def cmd_show_symbols(exchange=None, **kwargs):
    print(exchange, "foo")


def configure_parsers(main_parsers):    
    symbols_cmd = main_parsers.add_parser("symbols", help="generate list of symbols")
    symbols_cmd.set_defaults(func=cmd_show_symbols)
