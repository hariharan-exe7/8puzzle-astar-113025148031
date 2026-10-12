"""
Unit tests for the Sudoku CSP Solver and AC-3.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sudoku_csp import (
    SudokuCSP,
    ac3,
    compute_peers,
    format_sudoku_board,
    is_board_solved,
    is_valid_assignment,
    revise,
    validate_board,
)
from sudoku_solver import (
    solve_ac3,
    solve_forward_checking,
    solve_mrv,
    solve_plain_backtracking,
    solve_sudoku,
)


class TestSudokuCSP(unittest.TestCase):

    def setUp(self):
        self.board_4x4 = [
            [1, 0, 0, 4],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [3, 0, 0, 2],
        ]
        self.board_9x9 = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]

    def test_validation_valid_4x4(self):
        self.assertTrue(validate_board(self.board_4x4, 4))

    def test_validation_valid_9x9(self):
        self.assertTrue(validate_board(self.board_9x9, 9))

    def test_validation_rejects_wrong_dimensions(self):
        invalid = [[1, 2], [3, 4]]
        with self.assertRaises(ValueError):
            validate_board(invalid)

    def test_validation_rejects_duplicate_clues_row(self):
        bad_board = [
            [1, 1, 0, 4],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [3, 0, 0, 2],
        ]
        with self.assertRaises(ValueError):
            validate_board(bad_board, 4)

    def test_validation_rejects_duplicate_clues_column(self):
        bad_board = [
            [1, 0, 0, 4],
            [1, 0, 0, 0],
            [0, 0, 0, 0],
            [3, 0, 0, 2],
        ]
        with self.assertRaises(ValueError):
            validate_board(bad_board, 4)

    def test_validation_rejects_duplicate_clues_subgrid(self):
        bad_board = [
            [1, 0, 0, 4],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
            [3, 0, 0, 2],
        ]
        with self.assertRaises(ValueError):
            validate_board(bad_board, 4)

    def test_validation_rejects_out_of_range_number(self):
        bad_board = [
            [1, 5, 0, 4],  # 5 is illegal on 4x4
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [3, 0, 0, 2],
        ]
        with self.assertRaises(ValueError):
            validate_board(bad_board, 4)

    def test_peers_count(self):
        peers_4x4 = compute_peers(4)
        for var, p_set in peers_4x4.items():
            self.assertEqual(len(p_set), 7)

        peers_9x9 = compute_peers(9)
        for var, p_set in peers_9x9.items():
            self.assertEqual(len(p_set), 20)

    def test_plain_backtracking_solves_4x4(self):
        res = solve_plain_backtracking(self.board_4x4)
        self.assertTrue(res.is_solved)
        self.assertTrue(is_board_solved(res.solved_board, 4))
        # Ensure original clues preserved
        self.assertEqual(res.solved_board[0][0], 1)
        self.assertEqual(res.solved_board[0][3], 4)

    def test_mrv_solves_4x4(self):
        res = solve_mrv(self.board_4x4)
        self.assertTrue(res.is_solved)
        self.assertTrue(is_board_solved(res.solved_board, 4))

    def test_forward_checking_solves_4x4(self):
        res = solve_forward_checking(self.board_4x4)
        self.assertTrue(res.is_solved)
        self.assertTrue(is_board_solved(res.solved_board, 4))

    def test_ac3_solves_4x4(self):
        res = solve_ac3(self.board_4x4)
        self.assertTrue(res.is_solved)
        self.assertTrue(is_board_solved(res.solved_board, 4))

    def test_all_variants_solve_9x9_and_preserve_clues(self):
        res_plain = solve_plain_backtracking(self.board_9x9)
        res_mrv = solve_mrv(self.board_9x9)
        res_fc = solve_forward_checking(self.board_9x9)
        res_ac3 = solve_ac3(self.board_9x9)

        for res in [res_plain, res_mrv, res_fc, res_ac3]:
            self.assertTrue(res.is_solved)
            self.assertTrue(is_board_solved(res.solved_board, 9))
            # Clues preserved
            self.assertEqual(res.solved_board[0][0], 5)
            self.assertEqual(res.solved_board[0][1], 3)
            self.assertEqual(res.solved_board[0][4], 7)
            # Metrics measured honestly
            self.assertGreaterEqual(res.assignments, 0)
            self.assertGreaterEqual(res.backtracks, 0)
            self.assertGreater(res.runtime_ms, 0.0)

        # Plain, MRV, and FC perform non-zero search assignments on 9x9
        self.assertGreater(res_plain.assignments, 0)
        self.assertGreater(res_mrv.assignments, 0)
        self.assertGreater(res_fc.assignments, 0)

    def test_unsolvable_puzzle_handled(self):
        # A 4x4 board with no duplicates initially, but logically unsolvable:
        # Box (0,0) has 1, 2, 3, so cell (1,1) requires 4.
        # But Row 1 already has 4 at (1,3), making it impossible to satisfy both box and row.
        unsolvable = [
            [1, 2, 0, 0],
            [3, 0, 0, 4],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        res_plain = solve_plain_backtracking(unsolvable)
        res_fc = solve_forward_checking(unsolvable)
        res_ac3 = solve_ac3(unsolvable)
        self.assertFalse(res_plain.is_solved)
        self.assertFalse(res_fc.is_solved)
        self.assertFalse(res_ac3.is_solved)


if __name__ == "__main__":
    unittest.main()
