"""
Unit tests for the Explainable AI (XAI) features of the 8-Puzzle A* solver.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from puzzle_solver import (
    GOAL_STATE,
    a_star_search,
    get_per_tile_manhattan,
    manhattan_distance,
)
from explainable_ai import (
    explain_single_step,
    get_per_tile_manhattan_details,
    run_full_xai_demonstration,
)


class TestExplainableAI(unittest.TestCase):

    def test_per_tile_distances_sum_equals_manhattan_distance(self):
        # Arbitrary scrambled state
        state = (1, 3, 6, 5, 0, 2, 4, 7, 8)
        total_h = manhattan_distance(state)

        contributions = get_per_tile_manhattan(state)
        self.assertEqual(sum(contributions.values()), total_h)

        details, sum_details = get_per_tile_manhattan_details(state)
        self.assertEqual(sum_details, total_h)
        self.assertEqual(len(details), 8)  # tiles 1 through 8

    def test_goal_state_all_per_tile_distances_zero(self):
        details, total_h = get_per_tile_manhattan_details(GOAL_STATE)
        self.assertEqual(total_h, 0)
        for d in details:
            self.assertEqual(d["distance"], 0)
            self.assertTrue(d["is_home"])

    def test_single_step_explanation_costs(self):
        start = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        step_info = explain_single_step(0, None, start, "Start", 0)

        self.assertEqual(step_info["g"], 0)
        self.assertEqual(step_info["h"], 1)
        self.assertEqual(step_info["f"], 1)
        self.assertEqual(step_info["total_manhattan"], 1)

    def test_search_trace_reflects_actual_expansion_decisions(self):
        start = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        result = a_star_search(start, manhattan_distance, record_trace=True)

        self.assertIn("search_trace", result)
        trace = result["search_trace"]
        self.assertGreater(len(trace), 0)

        # Check first expansion event
        first_event = trace[0]
        self.assertEqual(first_event["expansion_index"], 1)
        self.assertEqual(first_event["state"], start)
        self.assertEqual(first_event["g"], 0)
        self.assertEqual(first_event["h"], 1)
        self.assertEqual(first_event["f"], 1)
        self.assertIn("frontier_size", first_event)
        self.assertIn("tie_breaker", first_event)

    def test_full_xai_demonstration_runs_cleanly(self):
        start = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        output = run_full_xai_demonstration(start)
        self.assertIn("EXPLAINABLE AI", output)
        self.assertIn("PER-TILE MANHATTAN CONTRIBUTIONS", output)
        self.assertIn("REAL SEARCH DECISION SAMPLES", output)


if __name__ == "__main__":
    unittest.main()
