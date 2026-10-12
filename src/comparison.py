"""
Performance Comparison and Search vs. CSP Study
------------------------------------------------
Provides comparative benchmarking tools and educational analysis:

1. Sudoku CSP Performance Comparison:
   - Evaluates Plain Backtracking, MRV, MRV+FC, and MRV+FC+AC-3 on the same puzzle.
   - Tracks actual assignments, backtracks, and runtime (ms) using time.perf_counter().
   - Formats clean comparison tables.

2. 8-Puzzle Heuristics Comparison:
   - Compares Misplaced Tiles vs Manhattan Distance.
   - Analyzes optimality, node expansions, and search pruning efficiency.

3. Search vs. CSP Academic Study:
   - Comprehensive comparison between state-space pathfinding (A*) and
     constraint satisfaction problems (Sudoku CSP).
"""

import time
try:
    from sudoku_csp import format_sudoku_board, is_board_solved
    from sudoku_solver import (
        solve_ac3,
        solve_forward_checking,
        solve_mrv,
        solve_plain_backtracking,
    )
    from puzzle_solver import (
        a_star_search,
        manhattan_distance,
        misplaced_tiles,
        print_comparison,
    )
except ImportError:
    from src.sudoku_csp import format_sudoku_board, is_board_solved
    from src.sudoku_solver import (
        solve_ac3,
        solve_forward_checking,
        solve_mrv,
        solve_plain_backtracking,
    )
    from src.puzzle_solver import (
        a_star_search,
        manhattan_distance,
        misplaced_tiles,
        print_comparison,
    )


def run_sudoku_comparison(board, label="Sudoku"):
    """
    Run all four CSP variants on the exact same board and return
    a formatted comparison table and analysis.
    """
    size = len(board)

    # 1. Plain Backtracking
    res_plain = solve_plain_backtracking(board)

    # 2. Backtracking + MRV
    res_mrv = solve_mrv(board)

    # 3. Backtracking + MRV + FC
    res_fc = solve_forward_checking(board)

    # 4. Backtracking + MRV + FC + AC-3
    res_ac3 = solve_ac3(board)

    results = [res_plain, res_mrv, res_fc, res_ac3]

    # Verify all solved boards
    for r in results:
        if r.is_solved:
            assert is_board_solved(r.solved_board, size), f"{r.method_name} produced invalid board!"

    lines = [
        "================================================================================",
        f"        SUDOKU CSP PERFORMANCE COMPARISON — {size}x{size} ({label})",
        "================================================================================",
        f"{'Algorithm':<32}{'Assignments':<16}{'Backtracks':<16}{'Runtime(ms)':<16}",
        "-" * 80,
    ]

    for r in results:
        status_text = f"{r.runtime_ms:10.3f}" if r.is_solved else "FAILED"
        lines.append(
            f"{r.method_name:<32}{r.assignments:<16}{r.backtracks:<16}{status_text:<16}"
        )

    lines.extend([
        "=" * 80,
        "\nANALYSIS & DISCUSSION:",
        "1. Search Space Pruning: Notice how intelligent variable ordering (MRV) and constraint",
        "   propagation (Forward Checking & AC-3) impact the number of assignments and backtracks.",
        "2. Computational Overhead Trade-Off: Stronger constraint propagation algorithms (like AC-3)",
        "   perform additional per-step arc consistency checks. On simple or moderately constrained",
        "   boards, the overhead of maintaining arc queues may result in higher wall-clock time even",
        "   when backtracks are drastically reduced. On harder boards with large search spaces,",
        "   propagation prevents exponential thrashing and scales far better.",
        "================================================================================",
    ])

    return "\n".join(lines), results


def compare_8puzzle_heuristics(start_state):
    """
    Run A* with Misplaced Tiles and Manhattan Distance heuristics on start_state
    and print the comparison.
    """
    misplaced_res = a_star_search(start_state, misplaced_tiles)
    manhattan_res = a_star_search(start_state, manhattan_distance)
    print_comparison(misplaced_res, manhattan_res)
    return misplaced_res, manhattan_res


def get_search_vs_csp_study_text():
    """
    Return comprehensive educational comparison text contrasting
    State-Space Search (8-Puzzle) with Constraint Satisfaction Problems (Sudoku).
    """
    return """
================================================================================
       SEARCH VS. CONSTRAINT SATISFACTION PROBLEM (CSP) STUDY
================================================================================

1. PROBLEM FORMULATION
-----------------------
* 8-PUZZLE (State-Space Search):
  - Formulated as a state-space graph: G = (V, E)
  - States: Discrete arrangements of 8 tiles and 1 blank on a 3x3 grid (9!/2 reachable states).
  - Transitions / Actions: Sliding the blank Up, Down, Left, or Right.
  - Path Cost: Cumulative sum of action step costs (each move = 1).
  - Objective: Find an OPTIMAL PATH (sequence of actions) from an initial state
    to a predefined goal state.

* SUDOKU (Constraint Satisfaction Problem):
  - Formulated as a CSP triple: <X, D, C>
  - Variables (X): 16 (for 4x4) or 81 (for 9x9) cell coordinates X_{r, c}.
  - Domains (D): Allowed values {1..N} for unassigned cells, or fixed clues {d}.
  - Constraints (C): All-Different relations across each row, column, and subgrid,
    represented as binary inequality constraints (Xi != Xj) for all peers.
  - Path Cost: IRRELEVANT. The sequence of assignments does not matter; only the
    final state's consistency is evaluated.
  - Objective: Find ANY VALID COMPLETE ASSIGNMENT satisfying all constraints.

2. SEARCH STRATEGY & HEURISTICS
--------------------------------
* 8-PUZZLE:
  - Algorithm: A* Best-First Search with Priority Queue (heapq).
  - Evaluation Function: f(n) = g(n) + h(n)
    - g(n): Known exact cost from start state to n.
    - h(n): Admissible estimate of remaining cost to goal (Manhattan Distance).
  - Search Direction: Forward exploration from start state toward goal state.
  - Optimality: Guaranteed optimal shortest path when h(n) is admissible.

* SUDOKU CSP:
  - Algorithm: Depth-First Backtracking Search with Constraint Propagation.
  - Heuristics:
    - Variable Ordering: Minimum Remaining Values (MRV / "Fail-First") selects
      the most constrained variable to prune the branching factor early.
    - Constraint Propagation: Forward Checking (1-step peer pruning) and
      AC-3 (Arc Consistency Algorithm 3) to propagate binary inequality arcs.
  - Optimality: Optimality is not applicable; the focus is feasibility.

3. WHEN HEURISTIC SEARCH IS PREFERABLE
---------------------------------------
Heuristic state-space search (like A*) is superior when:
- The problem is inherently about SEQUENTIAL PLANNING, ACTIONS, and ROUTING.
- Intermediate paths carry cost, and the goal is to find the minimum-cost route
  (e.g., GPS navigation, robotic arm trajectory planning, video game pathfinding).
- The solution is the ACTION SEQUENCE, not just the final board configuration.

4. WHEN CSP IS PREFERABLE
--------------------------
Constraint satisfaction formulations are superior when:
- The problem is inherently about ASSIGNMENT, CONFIGURATION, or RESOURCE ALLOCATION.
- The order in which variables receive values has no physical meaning or cost
  (e.g., timetable scheduling, circuit layout, Sudoku, graph coloring, frequency assignment).
- Rich constraint structures can be exploited using domain reduction (AC-3, forward
  checking) to detect dead ends before search even reaches them.

5. SUMMARY COMPARISON TABLE
----------------------------
Dimension            State-Space Search (8-Puzzle)    CSP (Sudoku)
--------------------------------------------------------------------------------
Primary Focus        Optimal Path of Actions          Feasible Assignment
State Representation Atomic State Tuple (1..8, 0)     Variables & Domains
Constraint Type      Implicit in legal move rules     Explicit binary/n-ary constraints
Evaluation Metric    f(n) = g(n) + h(n)               Domain size / Constraint consistency
Heuristic Type       Distance to Goal (Manhattan)     Variable choice (MRV), Value choice (LCV)
Memory Requirement   High (Frontier + Visited table)  Low (O(N) recursion stack with undo)
Optimality           Guaranteed optimal if admissible Feasibility (any valid solution)
================================================================================
"""
