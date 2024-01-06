import pytest
from implementation import find_minimal_plan, NoSolutionError, is_goal, check_state

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

     The exchange() function does NOT modify the original 
     state - it returns a new state with the exchange 
     applied, if possible. 
 
 Aim: 
 
     Obtain a  configuration where  all A's are placed to 
     the left of all B's, no matter where the empty boxes 
     are. 
 
     Given  an  initial  state, find  at  least  one 
     exchanging plan,  which reaches the aim (if there is 
     such  a plan).  A plan  includes  the  initial state 
     and the intermediate states for each step. 
 
 
"""


@pytest.mark.timeout(10)
def test_minimal_plan_jury_1():
    initial_state = [None, None, "A", "B", "A", "B", "A", "B", "A", "B"]
    plan = find_minimal_plan(initial_state)
    assert plan[0] == initial_state
    last_state = plan[-1]
    assert is_goal(last_state)
    # assert len(plan) == 4 + 1
    # E.g:
    # A B _ _ A B A B A B
    # A B B A A _ _ B A B
    # A B B A A A B B _ _
    # A _ _ A A A B B B B   # All A's are to the left of B's.


@pytest.mark.timeout(10)
def test_minimal_plan_jury_2():
    initial_state = ["A", "B", "B", "A", None, None, "A", "B", "A", "B"]
    plan = find_minimal_plan(initial_state)
    assert plan[0] == initial_state
    last_state = plan[-1]
    assert is_goal(last_state)
    # assert len(plan) == 3 + 1  # 3 exchanges + initial state
    # E.g:
    # A B B A _ _ A B A B
    # A B B A B A A _ _ B
    # A _ _ A B A A B B B
    # A A A A B _ _ B B B   # All A's are to the left of B's.


@pytest.mark.timeout(10)
def test_minimal_plan_jury_3():
    initial_state = [None, None, "A", "B", "A", "B"]
    with pytest.raises(NoSolutionError):
        find_minimal_plan(initial_state)


@pytest.mark.timeout(10)
def test_minimal_plan_jury_4():
    initial_state = [None, "A", "B", "A", None, "B", "A", "B"]
    with pytest.raises(ValueError, match="Invalid state"):
        find_minimal_plan(initial_state)


def test_minimal_plan_n1():
    initial_state = [None, None]
    plan = find_minimal_plan(initial_state)
    assert len(plan) == 1
    assert plan[0] == initial_state


def test_minimal_plan_n2_1():
    initial_state = [None, None, "A", "B"]
    plan = find_minimal_plan(initial_state)
    assert len(plan) == 1
    assert plan[0] == initial_state


def test_minimal_plan_n2_2():
    initial_state = ["A", "B", None, None]
    plan = find_minimal_plan(initial_state)
    assert len(plan) == 1
    assert plan[0] == initial_state


def test_minimal_plan_n2_3():
    initial_state = ["A", None, None, "B"]
    plan = find_minimal_plan(initial_state)
    assert len(plan) == 1
    assert plan[0] == initial_state


def test_plan_n2_no_solution_1():
    initial_state = ["B", None, None, "A"]
    with pytest.raises(NoSolutionError):
        find_minimal_plan(initial_state)


def _generate_random_state(N: int) -> list:
    from random import shuffle

    state = [None, None]
    state += ["A"] * (N - 1)
    state += ["B"] * (N - 1)
    shuffle(state)
    # Make sure the None boxes are next to each other
    pos_n1 = state.index(None)
    if state[pos_n1 + 1] is not None:
        pos_n2 = state.index(None, pos_n1 + 1)
        tmp_box = state[pos_n1 + 1]
        state[pos_n1 + 1] = state[pos_n2]
        state[pos_n2] = tmp_box
    return state


@pytest.mark.timeout(10)
@pytest.mark.parametrize("N", [2, 3, 4, 5, 6, 7, 8, 9])
def test_minimal_plan_random(N: int):
    initial_state = _generate_random_state(N)
    assert check_state(initial_state) is None

    print(f"Testing random state: {initial_state}")

    # Try to find a solution and assert that it either raises NoSolutionError or returns a plan, whose last state is a goal state
    try:
        plan = find_minimal_plan(initial_state)
        assert plan[0] == initial_state
        last_state = plan[-1]
        assert is_goal(last_state)
        print(f"Found a solution: {last_state}")
    except NoSolutionError:
        print("No solution found")
