# def odd_even(n: int | float) -> str:

import unittest
from implementation import odd_even


class TestOddEven(unittest.TestCase):
    def test_odd(self):
        assert odd_even(3) == "odd"

    def test_even(self):
        assert odd_even(4) == "even"

    def test_negative(self):
        assert odd_even(-1) == "odd"

    def test_zero(self):
        assert odd_even(0) == "even"

    def test_float(self):
        assert odd_even(1.5) == "odd"
