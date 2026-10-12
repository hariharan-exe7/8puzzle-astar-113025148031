"""
Unit tests for the 8-Puzzle Rule-Based Hint System and Optimal A* Hints.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from puzzle_solver import (
    GOAL_STATE,
    get_neighbors,
    manhattan_distance,
)
from hint_system import (
    format_hint_display,
    get_moving_tile,
    get_optimal_a_star_hint,
    get_rule_based_hint,
)


class TestHintSystem(unittest.TestCase):

    def test_hint_on_solved_puzzle(self):
        hint = get_rule_based_hint(GOAL_STATE)
        self.assertTrue(hint["solvable"])
        self.assertTrue(hint["solved"])
        self.assertIn("ALREADY SOLVED", hint["message"])

    def test_hint_on_unsolvable_puzzle_rejected(self):
        unsolvable = (1, 2, 3, 4, 5, 6, 8, 7, 0)
        hint = get_rule_based_hint(unsolvable)
        self.assertFalse(hint["solvable"])
        self.assertIn("UNSOLVABLE", hint["message"])

    def test_hint_on_one_move_away(self):
        # 1 2 3
        # 4 5 6
        # 7 0 8  -> blank moving Right slides tile 8 into goal
        state = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        hint = get_rule_based_hint(state)

        self.assertTrue(hint["solvable"])
        self.assertFalse(hint["solved"])
        self.assertEqual(hint["recommended_move"], "Right")
        self.assertEqual(hint["moving_tile"], 8)
        self.assertEqual(hint["current_manhattan"], 1)
        self.assertEqual(hint["new_manhattan"], 0)
        self.assertEqual(hint["delta_h"], 1)
        self.assertIn("tile 8 into its final goal position", hint["reason"])

    def test_moving_tile_identification(self):
        curr = (1, 2, 3, 4, 0, 6, 7, 5, 8)
        # Blank is at index 4 (center).
        # If blank moves Down, it swaps with index 7 (tile 5).
        neighbors = dict(get_neighbors(curr))
        # Find next state for Down
        down_state = None
        for next_s, move_name in get_neighbors(curr):
            if move_name == "Down":
                down_state = next_s
                break

        self.assertIsNotNone(down_state)
        moving_tile = get_moving_tile(curr, down_state)
        self.assertEqual(moving_tile, 5)

    def test_optimal_a_star_hint(self):
        # 1 move away
        state = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        opt_hint = get_optimal_a_star_hint(state)

        self.assertTrue(opt_hint["solvable"])
        self.assertEqual(opt_hint["recommended_move"], "Right")
        self.assertEqual(opt_hint["moving_tile"], 8)
        self.assertEqual(opt_hint["total_optimal_cost"], 1)
        self.assertTrue(opt_hint["is_optimal"])

    def test_optimal_hint_unsolvable_rejected(self):
        unsolvable = (1, 2, 3, 4, 5, 6, 8, 7, 0)
        opt_hint = get_optimal_a_star_hint(unsolvable)
        self.assertFalse(opt_hint["solvable"])

    def test_hint_display_formatting(self):
        state = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        hint = get_rule_based_hint(state)
        formatted = format_hint_display(hint)
        self.assertIn("RECOMMENDED MOVE", formatted)
        self.assertIn("Right", formatted)
        self.assertIn("MOVING TILE:", formatted)
        self.assertIn("8", formatted)


if __name__ == "__main__":
    unittest.main()
