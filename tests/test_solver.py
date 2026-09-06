import unittest

from src.puzzle_solver import (
    GOAL,
    misplaced_tiles,
    manhattan_distance,
    get_neighbors,
    is_solvable,
    a_star
)


class TestHeuristics(unittest.TestCase):

    def test_misplaced_goal(self):
        self.assertEqual(
            misplaced_tiles(GOAL),
            0
        )

    def test_manhattan_goal(self):
        self.assertEqual(
            manhattan_distance(GOAL),
            0
        )

    def test_misplaced_tiles(self):
        state = (
            1, 2, 3,
            4, 5, 6,
            8, 7, 0
        )

        self.assertEqual(
            misplaced_tiles(state),
            2
        )

    def test_manhattan_distance(self):
        state = (
            1, 2, 3,
            4, 5, 6,
            8, 7, 0
        )

        self.assertEqual(
            manhattan_distance(state),
            2
        )


class TestPuzzle(unittest.TestCase):

    def test_solvable_puzzle(self):
        state = (
            1, 2, 3,
            4, 5, 6,
            7, 0, 8
        )

        self.assertTrue(
            is_solvable(state)
        )

    def test_unsolvable_puzzle(self):
        state = (
            1, 2, 3,
            4, 5, 6,
            8, 7, 0
        )

        self.assertFalse(
            is_solvable(state)
        )

    def test_goal_state(self):
        self.assertTrue(
            is_solvable(GOAL)
        )


class TestNeighbors(unittest.TestCase):

    def test_corner_has_two_neighbors(self):

        state = (
            1, 2, 3,
            4, 5, 6,
            7, 8, 0
        )

        neighbors = get_neighbors(state)

        self.assertEqual(
            len(neighbors),
            2
        )

    def test_center_has_four_neighbors(self):

        state = (
            1, 2, 3,
            4, 0, 5,
            6, 7, 8
        )

        neighbors = get_neighbors(state)

        self.assertEqual(
            len(neighbors),
            4
        )


class TestAStar(unittest.TestCase):

    def test_a_star_misplaced(self):

        start = (
            1, 2, 3,
            4, 5, 6,
            7, 0, 8
        )

        path, expanded = a_star(
            start,
            misplaced_tiles
        )

        self.assertIsNotNone(path)

        self.assertEqual(
            path[0],
            start
        )

        self.assertEqual(
            path[-1],
            GOAL
        )

        self.assertEqual(
            len(path) - 1,
            1
        )

        self.assertGreater(
            expanded,
            0
        )

    def test_a_star_manhattan(self):

        start = (
            1, 2, 3,
            4, 5, 6,
            7, 0, 8
        )

        path, expanded = a_star(
            start,
            manhattan_distance
        )

        self.assertIsNotNone(path)

        self.assertEqual(
            path[0],
            start
        )

        self.assertEqual(
            path[-1],
            GOAL
        )

        self.assertEqual(
            len(path) - 1,
            1
        )

        self.assertGreater(
            expanded,
            0
        )


if __name__ == "__main__":
    unittest.main()