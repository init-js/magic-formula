import mformula.scrapers.tsx as tsx


def test_can_parse_toronto_date_summer():
    fmt = '%Y-%m-%d %H:%M:%S %Z (%z)'
    dt = tsx.toronto_date("30-June-2023")
    assert dt.strftime(fmt) == "2023-06-30 20:00:00 UTC (+0000)"


def test_can_parse_toronto_date_winter():
    fmt = '%Y-%m-%d %H:%M:%S %Z (%z)'
    dt = tsx.toronto_date("5-January-2022")
    assert dt.strftime(fmt) == "2022-01-05 21:00:00 UTC (+0000)"
