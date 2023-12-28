import pytest
from implementation import exchange

"""
We are given 2*N boxes in line  side  by  side.  Two 
adjacent boxes are empty, and the other boxes contain N-1 
symbols "A" and N-1 symbols "B". 
 
Example for N=5: 
 
        | A | B | B | A |   |   | A | B | A | B | 
 
Exchanging rule: 
 
     The content  of any two adjacent non-empty boxes can 
     be moved  into the  two empty ones, preserving their 
     order. 

     Each exchange is input by the number (from  0 to  N-2) 
     of the first of the two neighboring boxes which are to 
     be exchanged with the empty  ones. 

     The exchange() function should NOT modify the original 
     state - it should instead return a new state with the 
     exchange applied, if possible. 
 
"""


def test_exchange_operation():
    initial_state = ["A", "B", "B", "A", None, None, "A", "B", "A", "B"]

    new_state = exchange(initial_state, 0)
    assert new_state == [None, None, "B", "A", "A", "B", "A", "B", "A", "B"]

    new_state = exchange(initial_state, 1)
    assert new_state == ["A", None, None, "A", "B", "B", "A", "B", "A", "B"]

    new_state = exchange(initial_state, 2)
    assert new_state == ["A", "B", None, None, "B", "A", "A", "B", "A", "B"]

    new_state = exchange(initial_state, 6)
    assert new_state == ["A", "B", "B", "A", "A", "B", None, None, "A", "B"]

    new_state = exchange(initial_state, 7)
    assert new_state == ["A", "B", "B", "A", "B", "A", "A", None, None, "B"]

    new_state = exchange(initial_state, 8)
    assert new_state == ["A", "B", "B", "A", "A", "B", "A", "B", None, None]


def test_boundary_conditions():
    initial_state = ["A", "B", "B", "A", None, None, "A", "B", "A", "B"]
    with pytest.raises(IndexError):
        exchange(initial_state, 9)
    with pytest.raises(IndexError):
        exchange(initial_state, 10)


def test_invalid_exchanges():
    initial_state = ["A", "B", "B", "A", None, None, "A", "B", "A", "B"]
    with pytest.raises(ValueError, match="Invalid exchange"):
        exchange(initial_state, 3)
    with pytest.raises(ValueError, match="Invalid exchange"):
        exchange(initial_state, 4)
    with pytest.raises(ValueError, match="Invalid exchange"):
        exchange(initial_state, 5)


def test_multiple_exchanges():
    initial_state = ["A", "B", "A", "B", "A", "B", None, None]
    new_state = exchange(initial_state, 3)
    assert new_state == ["A", "B", "A", None, None, "B", "B", "A"]
    final_state = exchange(new_state, 0)
    assert final_state == [None, None, "A", "A", "B", "B", "B", "A"]


def test_n1():
    initial_state = [None, None]
    with pytest.raises(ValueError, match="Invalid exchange"):
        exchange(initial_state, 0)
    with pytest.raises(IndexError):
        exchange(initial_state, 1)


def test_n2():
    initial_state = ["B", "A", None, None]
    new_state = exchange(initial_state, 0)
    assert new_state == [None, None, "B", "A"]


def test_n3():
    initial_state = ["B", None, None, "A", "B", "A"]
    new_state = exchange(initial_state, 3)
    assert new_state == ["B", "A", "B", None, None, "A"]
    new_state = exchange(initial_state, 4)
    assert new_state == ["B", "B", "A", "A", None, None]
