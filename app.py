"""
Flask Web Application Backend
==============================
8-Puzzle Solver using A* — Search vs. Constraint Satisfaction Study

Connects the web frontend directly to existing Python AI modules:
- 8-Puzzle A* Heuristic Search & Solvability
- Rule-Based Hint System & Explainable AI (XAI)
- 4x4 & 9x9 Sudoku CSP Solvers (Plain, MRV, FC, AC-3)
- Empirical Benchmarks & Comparisons
"""

import os
import sys
import time
from flask import Flask, jsonify, render_template, request

# Add src/ to path so imports work cleanly in all environments
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from puzzle_solver import (
    GOAL_STATE,
    a_star_search,
    count_inversions,
    explain_solvability,
    get_per_tile_manhattan,
    is_solvable,
    manhattan_distance,
    misplaced_tiles,
    parse_state_input,
)
from hint_system import (
    get_optimal_a_star_hint,
    get_rule_based_hint,
)
from explainable_ai import (
    explain_single_step,
    get_per_tile_manhattan_details,
)
from sudoku_csp import (
    format_sudoku_board,
    is_board_solved,
    validate_board,
)
from sudoku_solver import (
    solve_ac3,
    solve_forward_checking,
    solve_mrv,
    solve_plain_backtracking,
    solve_sudoku,
)
from comparison import (
    get_search_vs_csp_study_text,
    run_sudoku_comparison,
)

app = Flask(__name__)


# ===========================================================================
# Validation Helpers
# ===========================================================================

def validate_puzzle_state(raw_state):
    """
    Validate that raw_state is a list of exactly 9 integers,
    containing numbers 0-8 exactly once. Returns a tuple of 9 integers.
    """
    if not isinstance(raw_state, list) or len(raw_state) != 9:
        raise ValueError("8-Puzzle state must be a list of exactly 9 numbers.")

    try:
        numbers = [int(x) for x in raw_state]
    except (ValueError, TypeError):
        raise ValueError("All 9 puzzle values must be integers between 0 and 8.")

    if sorted(numbers) != list(range(9)):
        raise ValueError("Puzzle must contain each number from 0 to 8 exactly once.")

    return tuple(numbers)


def validate_sudoku_grid(raw_board):
    """
    Validate that raw_board is an N x N grid of integers in 0..N (N=4 or 9).
    Returns (board, size).
    """
    if not isinstance(raw_board, list) or len(raw_board) not in (4, 9):
        raise ValueError("Sudoku board must be a 4x4 or 9x9 grid.")

    size = len(raw_board)
    board = []
    for r_idx, row in enumerate(raw_board):
        if not isinstance(row, list) or len(row) != size:
            raise ValueError(f"Row {r_idx + 1} must contain exactly {size} elements.")
        cleaned_row = []
        for c_idx, val in enumerate(row):
            try:
                # Treat empty string or null as 0
                val_int = 0 if val in ("", None) else int(val)
            except (ValueError, TypeError):
                raise ValueError(f"Cell ({r_idx + 1}, {c_idx + 1}) must be an integer between 0 and {size}.")

            if val_int < 0 or val_int > size:
                raise ValueError(f"Cell ({r_idx + 1}, {c_idx + 1}) value '{val_int}' is out of range (0-{size}).")
            cleaned_row.append(val_int)
        board.append(cleaned_row)

    # Verify duplicate clues in row, col, or subgrid
    validate_board(board, size)
    return board, size


# ===========================================================================
# Web Page Routes
# ===========================================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/puzzle")
def puzzle():
    return render_template("puzzle.html")


@app.route("/sudoku")
def sudoku():
    return render_template("sudoku.html")


@app.route("/comparison")
def comparison():
    return render_template("comparison.html")


@app.route("/about")
def about():
    return render_template("about.html")


# ===========================================================================
# 8-Puzzle API Endpoints
# ===========================================================================

@app.route("/api/puzzle/solve", methods=["POST"])
def api_puzzle_solve():
    data = request.get_json() or {}
    try:
        state = validate_puzzle_state(data.get("state"))
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    # Solvability check before executing search
    if not is_solvable(state):
        inversions = count_inversions(state)
        return jsonify({
            "success": False,
            "error": (
                f"Puzzle is UNSOLVABLE (inversion count: {inversions}, ODD parity). "
                "A* search was not executed to prevent wasted computation."
            ),
            "is_solvable": False,
            "inversion_count": inversions,
        }), 400

    heuristic_type = data.get("heuristic", "manhattan").lower()
    if heuristic_type == "misplaced":
        heuristic_fn = misplaced_tiles
        h_name = "Misplaced Tiles"
    else:
        heuristic_fn = manhattan_distance
        h_name = "Manhattan Distance"

    start_time = time.perf_counter()
    result = a_star_search(state, heuristic_fn, record_trace=True)
    runtime_ms = (time.perf_counter() - start_time) * 1000.0

    if not result:
        return jsonify({"success": False, "error": "No solution path found."}), 500

    # Build detailed step explanation for trajectory viewing
    steps = []
    prev_state = None
    for step_num, (st, move_name) in enumerate(result["path"]):
        g_val = step_num
        step_explanation = explain_single_step(step_num, prev_state, st, move_name, g_val)

        # Convert state tuple to 2D list for frontend rendering
        grid_2d = [
            list(st[0:3]),
            list(st[3:6]),
            list(st[6:9])
        ]

        steps.append({
            "step_number": step_num,
            "move_name": move_name,
            "state_flat": list(st),
            "state_grid": grid_2d,
            "g": step_explanation["g"],
            "h": step_explanation["h"],
            "f": step_explanation["f"],
            "moved_tile": step_explanation["moved_tile"],
            "action_desc": step_explanation["action_desc"],
            "per_tile": step_explanation["details"],
            "total_manhattan": step_explanation["total_manhattan"],
        })
        prev_state = st

    # Sample top search decision events from trace
    trace = result.get("search_trace", [])
    trace_samples = []
    sample_indices = [0]
    if len(trace) > 2:
        sample_indices.append(1)
    if len(trace) > 1:
        sample_indices.append(len(trace) - 1)
    for idx in sorted(set(sample_indices)):
        if idx < len(trace):
            t = trace[idx]
            trace_samples.append({
                "expansion_index": t["expansion_index"],
                "f": t["f"],
                "g": t["g"],
                "h": t["h"],
                "tie_breaker": t["tie_breaker"],
                "frontier_size": t["frontier_size"],
                "is_goal": t["is_goal"],
                "alternatives": t.get("alternatives", []),
            })

    return jsonify({
        "success": True,
        "cost": result["cost"],
        "nodes_expanded": result["nodes_expanded"],
        "runtime_ms": round(runtime_ms, 3),
        "heuristic": h_name,
        "steps": steps,
        "search_trace": trace_samples,
    })


@app.route("/api/puzzle/solvability", methods=["POST"])
def api_puzzle_solvability():
    data = request.get_json() or {}
    try:
        state = validate_puzzle_state(data.get("state"))
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    explanation = explain_solvability(state)
    return jsonify({
        "success": True,
        "is_solvable": explanation["is_solvable"],
        "inversion_count": explanation["inversion_count"],
        "parity": explanation["parity"],
        "tiles_sequence": explanation["tiles_sequence"],
        "inversion_pairs": explanation["inversion_pairs"],
        "rule": explanation["rule"],
        "verdict": explanation["verdict"],
    })


@app.route("/api/puzzle/hint", methods=["POST"])
def api_puzzle_hint():
    data = request.get_json() or {}
    try:
        state = validate_puzzle_state(data.get("state"))
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    greedy_hint = get_rule_based_hint(state)
    optimal_hint = None
    if greedy_hint.get("solvable") and not greedy_hint.get("solved"):
        optimal_hint = get_optimal_a_star_hint(state)

    return jsonify({
        "success": True,
        "greedy_hint": greedy_hint,
        "optimal_hint": optimal_hint,
    })


@app.route("/api/puzzle/compare", methods=["POST"])
def api_puzzle_compare():
    data = request.get_json() or {}
    try:
        state = validate_puzzle_state(data.get("state"))
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    if not is_solvable(state):
        return jsonify({
            "success": False,
            "error": "Puzzle is unsolvable. Heuristic comparison requires a solvable configuration.",
        }), 400

    # Misplaced Tiles
    t0 = time.perf_counter()
    res_m = a_star_search(state, misplaced_tiles)
    m_time = (time.perf_counter() - t0) * 1000.0

    # Manhattan Distance
    t1 = time.perf_counter()
    res_d = a_star_search(state, manhattan_distance)
    d_time = (time.perf_counter() - t1) * 1000.0

    m_nodes = res_m["nodes_expanded"]
    d_nodes = res_d["nodes_expanded"]
    reduction = ((m_nodes - d_nodes) / m_nodes * 100.0) if m_nodes > 0 else 0.0

    return jsonify({
        "success": True,
        "misplaced": {
            "name": "Misplaced Tiles",
            "cost": res_m["cost"],
            "nodes_expanded": m_nodes,
            "runtime_ms": round(m_time, 3),
        },
        "manhattan": {
            "name": "Manhattan Distance",
            "cost": res_d["cost"],
            "nodes_expanded": d_nodes,
            "runtime_ms": round(d_time, 3),
        },
        "same_cost": res_m["cost"] == res_d["cost"],
        "reduction_percent": round(reduction, 2),
    })


# ===========================================================================
# Sudoku API Endpoints
# ===========================================================================

@app.route("/api/sudoku/solve", methods=["POST"])
def api_sudoku_solve():
    data = request.get_json() or {}
    try:
        board, size = validate_sudoku_grid(data.get("board"))
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    algo = data.get("algorithm", "ac3").lower()
    algo_map = {
        "plain": solve_plain_backtracking,
        "mrv": solve_mrv,
        "fc": solve_forward_checking,
        "ac3": solve_ac3,
    }
    solver_fn = algo_map.get(algo, solve_ac3)

    result = solver_fn(board)

    # Record clue positions to allow frontend to highlight initial clues
    clues = []
    for r in range(size):
        for c in range(size):
            if board[r][c] != 0:
                clues.append([r, c])

    if not result.is_solved:
        return jsonify({
            "success": False,
            "error": "This Sudoku puzzle is unsatisfiable or has contradictory constraints.",
            "method_name": result.method_name,
            "assignments": result.assignments,
            "backtracks": result.backtracks,
            "runtime_ms": round(result.runtime_ms, 3),
            "size": size,
            "clues": clues,
        }), 200

    return jsonify({
        "success": True,
        "method_name": result.method_name,
        "solved_board": result.solved_board,
        "assignments": result.assignments,
        "backtracks": result.backtracks,
        "runtime_ms": round(result.runtime_ms, 3),
        "size": size,
        "clues": clues,
    })


@app.route("/api/sudoku/compare", methods=["POST"])
def api_sudoku_compare():
    data = request.get_json() or {}
    try:
        board, size = validate_sudoku_grid(data.get("board"))
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    table_text, results = run_sudoku_comparison(board, label=f"{size}x{size} Board")

    results_data = []
    for r in results:
        results_data.append({
            "method_name": r.method_name,
            "assignments": r.assignments,
            "backtracks": r.backtracks,
            "runtime_ms": round(r.runtime_ms, 3),
            "is_solved": r.is_solved,
        })

    return jsonify({
        "success": True,
        "size": size,
        "results": results_data,
        "table_text": table_text,
    })


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  AI Search & CSP Solver — Web Interface Running")
    print("  Open your browser at: http://127.0.0.1:5000")
    print("=" * 60 + "\n")
    app.run(debug=True, host="127.0.0.1", port=5000)
