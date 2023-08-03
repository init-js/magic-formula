import logging
import pytz
import tempfile
import re
from datetime import datetime
import requests
import pandas as pd
import os.path

from ..errors import ScraperError
from ..utils import create_data_point_dir

"""
Pulls data from tsx.com
"""

# TSX & TSXV Listed Companies
MARKET_STATS_URL = "https://www.tsx.com/resource/en/571"

TSX_SHEET_NAME_RE = re.compile(r"^(TSXV?) Issuers ([^\s]+) (\d\d\d\d)$")

TORONTO_TZ = pytz.timezone('America/Toronto')

# Remove "NA" from the default NaN values, and anything else that could be
# a stock symbol. "NA" is National Bank!
NA_VALUES = ("#N/A", "#N/A N/A", "#NA", "-1.#IND", "-1.#QNAN",
             "-NaN", "-nan", "1.#IND", "1.#QNAN", "<NA>",
             "N/A", "NaN", "None", "n/a", "nan", "null",
             # "NA", "NULL"
             )

log = logging.getLogger(__package__)


def toronto_date(date_stamp):
    """parses a date of the form 30-June-2023 (assumed to be in toronto) into UTC"""
    day_s, month_s, year_s = date_stamp.split("-")
    day = int(day_s, 10)
    year = int(year_s, 10)
    month = {
        'january': 1,
        'febuary': 2,
        'march': 3,
        'april': 4,
        'may': 5,
        'june': 6,
        'july': 7,
        'august': 8,
        'september': 9,
        'october': 10,
        'november': 11,
        'december': 12
    }[month_s.lower()]
    # market closes at 16:00, toronto time
    closing_datetime = TORONTO_TZ.localize(datetime(year, month, day, 16, 0, 0))
    return closing_datetime.astimezone(pytz.utc)


def cmd_write_symbols():
    """fills market-data directory with list of tsx/tsxv symbols"""
    log.info("downloading %s", MARKET_STATS_URL)
    r = requests.get(MARKET_STATS_URL)

    for hdr, val in r.headers.items():
        log.debug("resp %s: %s", hdr, val)

    content_disp = r.headers['Content-Disposition']
    match = re.search(r'filename="(.*)"$', content_disp)

    if not match:
        raise ScraperError(MARKET_STATS_URL, "site has changed, expected to find filename in the Content-Disposition")
    fname = match.group(1)
    log.info("file is called: %s", fname)

    # Clean up a NamedTemporaryFile on your own
    # delete=True means the file will be deleted on close
    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        tmp.write(r.content)
        tmp.flush()
        xl = pd.ExcelFile(tmp)
        for sheet_name in xl.sheet_names:
            log.debug("xls sheets: %s", sheet_name)
            if sheet_name.startswith("_"):
                # hidden sheets. don't care
                continue
            match = TSX_SHEET_NAME_RE.match(sheet_name)
            if not match:
                raise ScraperError(MARKET_STATS_URL, "unexpected sheet name syntax: " + sheet_name)
            exchange_name = match.group(1).lower()
            month = match.group(2)
            year = match.group(3)
            log.debug("exchange %s %s %s", exchange_name, year, month)

            df: pd.DataFrame
            df = xl.parse(sheet_name, header=9, index_col="Root\nTicker", na_values=NA_VALUES, keep_default_na=False)
            df.sort_index(inplace=True)
            # The market cap column holds the timestamp
            mcap = [c for c in df.columns if c.startswith("Market Cap (C$)")]
            if not mcap:
                raise ScraperError(MARKET_STATS_URL, "columns have changed")
            date_stamp = mcap[0].split()[-1]
            log.debug("excel spreadsheet date stamp: %s", date_stamp)
            dt = toronto_date(date_stamp)

            # rename columns
            def rename_col(col: str):
                col = (col
                       .replace(date_stamp, "")
                       .replace("\n", " ")
                       .replace("-", "_")
                       .replace("(C$)", "")
                       .replace("/", "")  # "O/S Shares" is outstanding shares
                       .strip())
                col = re.sub(r"\s+", "_", col)
                col = re.sub(r"_+", "_", col)
                return col

            new_cols = [rename_col(col) for col in df.columns]
            df.columns = new_cols

            outdir = create_data_point_dir(exchange_name, dt)
            final_out = os.path.join(outdir, "symbols.json")
            tmp_out = os.path.join(outdir, "symbols.json") + ".tmp"
            with open(tmp_out, "w") as out_fd:
                df.to_json(out_fd, date_format='iso', indent=2)
            log.info("Writing symbols file: " + final_out)
            os.rename(tmp_out, final_out)
