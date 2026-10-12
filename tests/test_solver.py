"""
Unit tests for the 8-Puzzle A* Solver.

Run from the project root with:
    python -m unittest discover -s tests

These tests use only the Python standard library (unittest), so no extra
packages need to be installed.
"""

import os
import sys
import unittest

# Make sure "src" is on the import path when running this test file
# directly from the project root or from inside the tests/ folder.
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "src")
)

from puzzle_solver import (
    GOAL_STATE,
    misplaced_tiles,
    manhattan_distance,
    is_solvable,
    a_star_search,
    parse_state_input,
)


class TestHeuristics(unittest.TestCase):

    def test_goal_state_misplaced_tiles_is_zero(self):
        self.assertEqual(misplaced_tiles(GOAL_STATE), 0)

    def test_goal_state_manhattan_distance_is_zero(self):
        self.assertEqual(manhattan_distance(GOAL_STATE), 0)

    def test_misplaced_tiles_ignores_blank(self):
        # Blank in the wrong position, but every numbered tile correct
        # relative to itself should still not count the blank.
        state = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        # Tile 8 is misplaced (it should be at index 7, but is at index 8)
        # Blank (0) must not be counted, even though it is "misplaced".
        self.assertEqual(misplaced_tiles(state), 1)

    def test_manhattan_distance_known_value(self):
        # Only tile 8 is displaced by one swap with the blank.
        # Goal index of 8 is 7 (row2,col1). In this state 8 is at index 8
        # (row2,col2): distance = |2-2| + |2-1| = 1
        state = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        self.assertEqual(manhattan_distance(state), 1)


class TestSolvability(unittest.TestCase):

    def test_known_solvable_state(self):
        state = (1, 3, 6, 5, 0, 2, 4, 7, 8)
        self.assertTrue(is_solvable(state))

    def test_known_unsolvable_state(self):
        state = (1, 2, 3, 4, 5, 6, 8, 7, 0)
        self.assertFalse(is_solvable(state))

    def test_goal_state_is_solvable(self):
        self.assertTrue(is_solvable(GOAL_STATE))


class TestAStarSearch(unittest.TestCase):

    def test_a_star_returns_goal_state(self):
        state = (1, 3, 6, 5, 0, 2, 4, 7, 8)
        result = a_star_search(state, manhattan_distance)
        final_state = result["path"][-1][0]
        self.assertEqual(final_state, GOAL_STATE)

    def test_a_star_already_solved_has_zero_cost(self):
        result = a_star_search(GOAL_STATE, manhattan_distance)
        self.assertEqual(result["cost"], 0)

    def test_a_star_optimal_cost_matches_known_small_puzzle(self):
        # One move away from goal: swapping 0 and 8.
        # 1 2 3
        # 4 5 6
        # 7 0 8   -> one Right move of blank solves it? Let's verify goal.
        # Goal:
        # 1 2 3
        # 4 5 6
        # 7 8 0
        # This state has 8 and 0 swapped relative to goal -> exactly 1 move.
        state = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        result = a_star_search(state, manhattan_distance)
        self.assertEqual(result["cost"], 1)

    def test_both_heuristics_agree_on_optimal_cost(self):
        state = (1, 3, 6, 5, 0, 2, 4, 7, 8)
        result_misplaced = a_star_search(state, misplaced_tiles)
        result_manhattan = a_star_search(state, manhattan_distance)
        self.assertEqual(result_misplaced["cost"], result_manhattan["cost"])


class TestInputParsing(unittest.TestCase):

    def test_parse_valid_input(self):
        parsed = parse_state_input("1 3 6 5 0 2 4 7 8")
        self.assertEqual(parsed, (1, 3, 6, 5, 0, 2, 4, 7, 8))

    def test_parse_rejects_wrong_count(self):
        with self.assertRaises(ValueError):
            parse_state_input("1 2 3 4 5")

    def test_parse_rejects_duplicate_numbers(self):
        with self.assertRaises(ValueError):
            parse_state_input("1 1 2 3 4 5 6 7 8")

    def test_parse_rejects_non_integers(self):
        with self.assertRaises(ValueError):
            parse_state_input("1 2 3 4 5 6 7 8 x")


if __name__ == "__main__":
    unittest.main()
