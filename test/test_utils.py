import pytest
import re
from datetime import datetime

from mformula import utils


@pytest.mark.parametrize("array, needle, expected_result", [
    ([1, 5, 6, 10], 5, 1),
    ([-5, 10, 100, 1000], 15, 1),
    (["bob", "carl", "david"], "elisabeth", 2),
    (["bob", "carl", "david", "eli", "frank"], "alice", -1),
    (["bob", "carl", "david", "eli", "frank"], "bob", 0),
    (["bob", "bob", "carl", "david", "eli", "frank"], "cab", 1),
    (["bob", "carl", "david", "eli", "frank"], "joe", 4),
])
def test_bin_search(array, needle, expected_result):
    assert utils.index_of_closest_le(array, needle) == expected_result


@pytest.mark.parametrize("filenames, date_s, format, expected", [
    (["foo/2005-01-20.symbols", "foo/2005-01-10.symbols", "foo/2006-02-12.symbols"], "2005-01-11", "%Y-%m-%d", "foo/2005-01-10.symbols"),
    (["foo/2005-01-20.symbols", "foo/2005-01-10.symbols", "foo/2006-02-12.symbols"], "2003-01-11", "%Y-%m-%d", None),  # too early
    (["foo/2005-01-20.symbols", "foo/2005-01-10.symbols", "foo/2006-02-12.symbols"], "3003-01-11", "%Y-%m-%d", "foo/2006-02-12.symbols"),
    
])
def test_date_select(filenames, date_s, format, expected):
    as_of = datetime.strptime(date_s, format)
    assert utils.select_most_recent(filenames, re.compile(r"\b[-\d]+"), as_of, format) == expected


def file_time_re_can_understand_file_time_format():
    t = datetime(2023, 4, 4, 22, 0, 5)
    formatted = t.strftime(utils.FILE_TIME_FMT)
    match = utils.FILE_TIME_RE.search(formatted)
    assert match is not None
    stuff = match.group(0)
    back = datetime.strptime(stuff, utils.FILE_TIME_FMT)

    # we haven't lost any info in the conversion
    assert back == t
