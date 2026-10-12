"""
Unit tests for the Knowledge-Based Solvability Rules and Inversion Parity.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from puzzle_solver import (
    GOAL_STATE,
    count_inversions,
    explain_solvability,
    is_solvable,
    parse_state_input,
)


class TestSolvabilityRules(unittest.TestCase):

    def test_goal_state_has_zero_inversions(self):
        self.assertEqual(count_inversions(GOAL_STATE), 0)
        self.assertTrue(is_solvable(GOAL_STATE))

    def test_single_transposition_produces_odd_inversions(self):
        # Swap 7 and 8 in goal state:
        # 1 2 3 4 5 6 8 7 0
        # Inversion count must be 1 (odd)
        state = (1, 2, 3, 4, 5, 6, 8, 7, 0)
        self.assertEqual(count_inversions(state), 1)
        self.assertFalse(is_solvable(state))

    def test_solvable_state_even_inversions(self):
        # 1 3 6 5 0 2 4 7 8
        # Non-blank sequence: [1, 3, 6, 5, 2, 4, 7, 8]
        # Inversions: (3,2), (6,5), (6,2), (6,4), (5,2), (5,4) -> count = 6 (even)
        state = (1, 3, 6, 5, 0, 2, 4, 7, 8)
        self.assertEqual(count_inversions(state), 6)
        self.assertTrue(is_solvable(state))

    def test_explain_solvability_structure(self):
        solvable_state = (1, 3, 6, 5, 0, 2, 4, 7, 8)
        expl_solvable = explain_solvability(solvable_state)

        self.assertEqual(expl_solvable["parity"], "EVEN")
        self.assertTrue(expl_solvable["is_solvable"])
        self.assertIn("SOLVABLE", expl_solvable["verdict"])
        self.assertEqual(expl_solvable["inversion_count"], 6)

        unsolvable_state = (1, 2, 3, 4, 5, 6, 8, 7, 0)
        expl_unsolvable = explain_solvability(unsolvable_state)

        self.assertEqual(expl_unsolvable["parity"], "ODD")
        self.assertFalse(expl_unsolvable["is_solvable"])
        self.assertIn("UNSOLVABLE", expl_unsolvable["verdict"])
        self.assertEqual(expl_unsolvable["inversion_count"], 1)

    def test_input_validation_catches_invalid_cases(self):
        with self.assertRaises(ValueError):
            parse_state_input("1 2 3 4 5 6 7 8")  # Only 8 numbers

        with self.assertRaises(ValueError):
            parse_state_input("1 2 3 4 5 6 7 8 8")  # Duplicate 8, missing 0

        with self.assertRaises(ValueError):
            parse_state_input("1 2 3 4 5 6 7 8 9")  # 9 is out of range (0-8)

        with self.assertRaises(ValueError):
            parse_state_input("1 2 3 4 5 6 7 8 a")  # Non-integer


if __name__ == "__main__":
    unittest.main()
