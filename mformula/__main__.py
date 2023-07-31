import logging

from . import setup_logging
from . import symbols
from . import scrapers
import argparse

"""
Analyzes stock data on different markets and provides company rankings according
to the magic formula from Joel Greenblatt.
"""
log = logging.getLogger(__package__)


def main():
    setup_logging(logging.DEBUG)
    parser = argparse.ArgumentParser(
        "mformula", __doc__,
        "mfomula command line interface")
    
    # global flags
    parser.add_argument("-x", "--exchange", metavar='EXCG', default="tsx", choices=('tsx', 'nyse'), help="the marketplace/exchange acronym")
    parser.set_defaults(func=None)
    commands = parser.add_subparsers(help='The sub-command to invoke', metavar='CMD', dest='command')
 
    symbols.configure_parsers(commands)
    scrapers.configure_parsers(commands)
    args = parser.parse_args()

    if args.command is None:
        sys.stderr.write("No subcommand specified.\n")
        sys.stderr.write(parser.format_usage() + "\n")
        return 1

    if not args.func:
        sys.stderr.write("No command specified.\n")
        sys.stderr.write(parser.format_usage() + "\n")
        return 1

    retcode = args.func(**vars(args))
    return retcode if retcode is not None else 0


if __name__ == "__main__":
    # user ran `python3 -m mformula``
    import sys
    sys.exit(main())

if __name__ == 'mformula.__main__':
    # user ran `mformula` (script helper installed by pip)
    import sys
    sys.exit(main())
