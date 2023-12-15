# def mformat(d: date, f: str) -> str:

from datetime import date

from implementation import mformat


def test_for_quarters():
    assert mformat(date(2022, 1, 1), "Q") == "Q1-22"
    assert mformat(date(2023, 1, 30), "Q") == "Q1-23"
    assert mformat(date(2023, 3, 31), "Q") == "Q1-23"
    assert mformat(date(2023, 4, 1), "Q") == "Q2-23"
    assert mformat(date(2023, 6, 30), "Q") == "Q2-23"
    assert mformat(date(2023, 7, 1), "Q") == "Q3-23"
    assert mformat(date(2023, 9, 30), "Q") == "Q3-23"
    assert mformat(date(2023, 12, 15), "Q") == "Q4-23"
    assert mformat(date(2023, 12, 31), "Q") == "Q4-23"


def test_for_months():
    assert mformat(date(2022, 1, 5), "M") == "Jan22"
    assert mformat(date(2023, 2, 1), "M") == "Feb23"
    assert mformat(date(2023, 2, 19), "M") == "Feb23"
    assert mformat(date(2023, 12, 30), "M") == "Dec23"
