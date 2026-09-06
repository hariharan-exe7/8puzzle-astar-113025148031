import sys

sys.path.append("src")

from puzzle_solver import (
    misplaced_tiles,
    manhattan_distance,
    is_solvable
)


def test_goal_misplaced():

    state = (
        1, 2, 3,
        4, 5, 6,
        7, 8, 0
    )

    assert misplaced_tiles(state) == 0


def test_goal_manhattan():

    state = (
        1, 2, 3,
        4, 5, 6,
        7, 8, 0
    )

    assert manhattan_distance(state) == 0


def test_solvable():

    state = (
        1, 3, 6,
        5, 0, 2,
        4, 7, 8
    )

    assert is_solvable(state)


def test_unsolvable():

    state = (
        1, 2, 3,
        4, 5, 6,
        8, 7, 0
    )

    assert not is_solvable(state)