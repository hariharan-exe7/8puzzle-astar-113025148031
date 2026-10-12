"""
AI Search & CSP Solver — Main Application
=========================================
8-Puzzle Solver using A* — Search vs. Constraint Satisfaction Study

College Artificial Intelligence and Machine Learning Project
Combines:
- Heuristic State-Space Search (A*, Misplaced Tiles, Manhattan Distance)
- Constraint Satisfaction Problems (Sudoku 4x4 & 9x9, MRV, Forward Checking, AC-3)
- Knowledge Representation & Inversion Parity Solvability
- Rule-Based Hint System
- Explainable AI (XAI) and Authentic Search Decision Tracing
- Search vs. CSP Academic Comparative Study
"""

import sys
import os

# Ensure src/ is on Python module search path
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
    print_comparison,
    print_solution_path,
    state_to_grid_string,
)
from sudoku_csp import (
    SudokuCSP,
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
from hint_system import (
    format_hint_display,
    get_optimal_a_star_hint,
    get_rule_based_hint,
)
from explainable_ai import (
    run_full_xai_demonstration,
)
from comparison import (
    get_search_vs_csp_study_text,
    run_sudoku_comparison,
)


# ===========================================================================
# Built-in Presets
# ===========================================================================

PRESET_PUZZLES_8 = [
    ("Standard 4-Move Solvable", (1, 2, 3, 0, 4, 6, 7, 5, 8)),
    ("Medium Solvable", (1, 3, 6, 5, 0, 2, 4, 7, 8)),
    ("1 Move Away from Goal", (1, 2, 3, 4, 5, 6, 7, 0, 8)),
    ("Unsolvable (Odd Inversions)", (1, 2, 3, 4, 5, 6, 8, 7, 0)),
]

PRESET_SUDOKU_4X4 = [
    ("Classic 4x4", [
        [1, 0, 0, 4],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [3, 0, 0, 2],
    ]),
    ("Moderate 4x4", [
        [0, 2, 4, 0],
        [1, 0, 0, 3],
        [4, 0, 0, 2],
        [0, 1, 3, 0],
    ]),
]

PRESET_SUDOKU_9X9 = [
    ("Classic Easy 9x9", [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]),
    ("Medium 9x9", [
        [0, 0, 0, 2, 6, 0, 7, 0, 1],
        [6, 8, 0, 0, 7, 0, 0, 9, 0],
        [1, 9, 0, 0, 0, 4, 5, 0, 0],
        [8, 2, 0, 1, 0, 0, 0, 4, 0],
        [0, 0, 4, 6, 0, 2, 9, 0, 0],
        [0, 5, 0, 0, 0, 3, 0, 2, 8],
        [0, 0, 9, 3, 0, 0, 0, 7, 4],
        [0, 4, 0, 0, 5, 0, 0, 3, 6],
        [7, 0, 3, 0, 1, 8, 0, 0, 0],
    ]),
]


# ===========================================================================
# Input Helpers
# ===========================================================================

def choose_8puzzle_input():
    """Prompt user to choose a preset 8-puzzle or type a custom state."""
    print("\nSelect 8-Puzzle State Source:")
    for idx, (label, state) in enumerate(PRESET_PUZZLES_8, 1):
        print(f"  {idx}. {label} ({' '.join(map(str, state))})")
    print("  C. Enter custom 9-number state")
    print("  B. Back to main menu")

    while True:
        choice = input("\nEnter choice [1-4, C, B]: ").strip().upper()
        if choice == "B":
            return None
        if choice in ("1", "2", "3", "4"):
            return PRESET_PUZZLES_8[int(choice) - 1][1]
        if choice == "C":
            print("\nEnter 9 integers (0-8) separated by spaces (0 for blank):")
            print("Example: 1 3 6 5 0 2 4 7 8")
            raw_text = input("Puzzle state: ").strip()
            try:
                return parse_state_input(raw_text)
            except ValueError as e:
                print(f"[!] Invalid input: {e}")
                print("Try again or enter B to go back.")
        else:
            print("[!] Invalid option. Enter 1-4, C, or B.")


def choose_sudoku_board(size):
    """Prompt user to choose a preset Sudoku board or enter a custom grid."""
    presets = PRESET_SUDOKU_4X4 if size == 4 else PRESET_SUDOKU_9X9
    print(f"\nSelect {size}x{size} Sudoku Board Source:")
    for idx, (label, _) in enumerate(presets, 1):
        print(f"  {idx}. {label}")
    print("  C. Enter custom board line-by-line")
    print("  B. Back to main menu")

    while True:
        choice = input(f"\nEnter choice [1-{len(presets)}, C, B]: ").strip().upper()
        if choice == "B":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(presets):
            # Return deep copy of selected preset
            return [list(r) for r in presets[int(choice) - 1][1]]
        if choice == "C":
            print(f"\nEnter {size} lines, each containing {size} space-separated integers (0-{size}, 0 for empty):")
            custom_board = []
            try:
                for r in range(size):
                    line = input(f"Row {r + 1}/{size}: ").strip()
                    parts = [int(p) for p in line.split()]
                    if len(parts) != size:
                        raise ValueError(f"Row must contain exactly {size} numbers, got {len(parts)}.")
                    custom_board.append(parts)
                validate_board(custom_board, size)
                return custom_board
            except ValueError as e:
                print(f"[!] Invalid board: {e}")
                print("Returning to selection...")
        else:
            print(f"[!] Invalid option. Enter 1-{len(presets)}, C, or B.")


# ===========================================================================
# Menu Handlers
# ===========================================================================

def handle_solve_8puzzle():
    print("\n------------------------------------------------------------")
    print(" 1. SOLVE 8-PUZZLE USING A* SEARCH")
    print("------------------------------------------------------------")
    state = choose_8puzzle_input()
    if state is None:
        return

    print("\nInitial State:")
    print(state_to_grid_string(state))

    # Knowledge Layer: Solvability check before search
    if not is_solvable(state):
        print("\n[!] REJECTION: This puzzle state is UNSOLVABLE!")
        print(f"    Inversion count: {count_inversions(state)} (ODD parity).")
        print("    A* search was not executed to prevent wasted computation.")
        return

    print("\nChoose Heuristic:")
    print("  1. Manhattan Distance (Recommended — Admissible & Informed)")
    print("  2. Misplaced Tiles (Admissible — Coarser estimate)")
    h_choice = input("Enter choice [1/2, default=1]: ").strip()

    heuristic_func = misplaced_tiles if h_choice == "2" else manhattan_distance
    h_name = "Misplaced Tiles" if h_choice == "2" else "Manhattan Distance"

    print(f"\nRunning A* with {h_name}...")
    result = a_star_search(state, heuristic_func)

    if not result:
        print("[!] No solution found.")
        return

    print(f"\nOptimal Solution Found in {result['cost']} moves!")
    print(f"Total Nodes Expanded: {result['nodes_expanded']}")

    show_path = input("\nDisplay full step-by-step solution path? [Y/n]: ").strip().lower()
    if show_path != "n":
        print_solution_path(result["path"])


def handle_compare_8puzzle_heuristics():
    print("\n------------------------------------------------------------")
    print(" 2. COMPARE 8-PUZZLE HEURISTICS (MISPLACED VS. MANHATTAN)")
    print("------------------------------------------------------------")
    state = choose_8puzzle_input()
    if state is None:
        return

    print("\nInitial State:")
    print(state_to_grid_string(state))

    if not is_solvable(state):
        print("\n[!] REJECTION: This puzzle state is UNSOLVABLE!")
        print(f"    Inversion count: {count_inversions(state)} (ODD parity).")
        print("    A* search rejected.")
        return

    print("\nExecuting A* with both heuristics on the same state...")
    res_misplaced = a_star_search(state, misplaced_tiles)
    res_manhattan = a_star_search(state, manhattan_distance)
    print_comparison(res_misplaced, res_manhattan)


def handle_check_solvability():
    print("\n------------------------------------------------------------")
    print(" 3. KNOWLEDGE-BASED 8-PUZZLE SOLVABILITY CHECK")
    print("------------------------------------------------------------")
    state = choose_8puzzle_input()
    if state is None:
        return

    explanation = explain_solvability(state)
    print("\n==================================================")
    print("             LOGICAL SOLVABILITY AUDIT            ")
    print("==================================================")
    print("Puzzle State:")
    print(state_to_grid_string(state))
    print(f"\nNon-Blank Tile Sequence: {explanation['tiles_sequence']}")
    print(f"Inversion Count:         {explanation['inversion_count']}")
    print(f"Parity:                  {explanation['parity']}")
    print(f"\nInversion Pairs:         {explanation['inversion_pairs']}")
    print(f"\nMathematical Invariant Rule:")
    print(f"  {explanation['rule']}")
    print(f"\nVERDICT: {explanation['verdict']}")
    print("==================================================")


def handle_rule_based_hint():
    print("\n------------------------------------------------------------")
    print(" 4. RULE-BASED 8-PUZZLE HINT SYSTEM")
    print("------------------------------------------------------------")
    state = choose_8puzzle_input()
    if state is None:
        return

    hint = get_rule_based_hint(state)
    print(format_hint_display(hint))

    if hint.get("solvable") and not hint.get("solved"):
        opt = input("\nAlso show guaranteed optimal A* next move? [Y/n]: ").strip().lower()
        if opt != "n":
            opt_hint = get_optimal_a_star_hint(state)
            if opt_hint and opt_hint.get("solvable"):
                print("\n--- GUARANTEED OPTIMAL A* MOVE ---")
                print(f"Move Blank:         {opt_hint['recommended_move']}")
                print(f"Slide Tile:         {opt_hint['moving_tile']}")
                print(f"Total Optimal Cost: {opt_hint['total_optimal_cost']} moves to goal")
                print(f"Rationale:          {opt_hint['reason']}")


def handle_explainable_ai():
    print("\n------------------------------------------------------------")
    print(" 5. EXPLAINABLE AI (XAI) & A* SEARCH AUDIT")
    print("------------------------------------------------------------")
    state = choose_8puzzle_input()
    if state is None:
        return

    if not is_solvable(state):
        print("\n[!] REJECTION: State is unsolvable. A* search cannot be explained.")
        return

    print("\nRunning A* with real search trace recording...")
    output = run_full_xai_demonstration(state)
    print(output)


def handle_solve_sudoku(size):
    print(f"\n------------------------------------------------------------")
    print(f" SOLVE {size}x{size} SUDOKU")
    print(f"------------------------------------------------------------")
    board = choose_sudoku_board(size)
    if board is None:
        return

    print("\nInitial Board:")
    print(format_sudoku_board(board))

    print("\nChoose CSP Algorithm:")
    print("  1. Plain Backtracking (Baseline)")
    print("  2. Backtracking + MRV")
    print("  3. Backtracking + MRV + Forward Checking")
    print("  4. Backtracking + MRV + FC + AC-3 (Full Propagation)")
    algo_choice = input("Enter choice [1-4, default=4]: ").strip()

    solver_map = {
        "1": solve_plain_backtracking,
        "2": solve_mrv,
        "3": solve_forward_checking,
        "4": solve_ac3,
    }
    solver_fn = solver_map.get(algo_choice, solve_ac3)

    print("\nSolving puzzle...")
    result = solver_fn(board)

    if result.is_solved:
        print(f"\n[+] Solution found using {result.method_name}!")
        print(format_sudoku_board(result.solved_board))
        print(f"\nPerformance Metrics:")
        print(f"  Assignments: {result.assignments}")
        print(f"  Backtracks:  {result.backtracks}")
        print(f"  Runtime:     {result.runtime_ms:.3f} ms")
    else:
        print(f"\n[!] Puzzle is UNSATISFIABLE or no valid assignment exists.")
        print(f"  Assignments attempted: {result.assignments}")
        print(f"  Backtracks:            {result.backtracks}")
        print(f"  Runtime:               {result.runtime_ms:.3f} ms")


def handle_compare_sudoku():
    print("\n------------------------------------------------------------")
    print(" 8. COMPARE SUDOKU CSP ALGORITHMS (ALL 4 VARIANTS)")
    print("------------------------------------------------------------")
    print("Select Sudoku Dimension:")
    print("  1. 4x4 Sudoku (Quick comparison)")
    print("  2. 9x9 Sudoku (Full CSP scale comparison)")
    print("  B. Back to main menu")

    size_choice = input("\nEnter choice [1/2, B]: ").strip().upper()
    if size_choice == "B":
        return
    size = 4 if size_choice == "1" else 9

    board = choose_sudoku_board(size)
    if board is None:
        return

    print("\nInitial Board:")
    print(format_sudoku_board(board))

    print("\nExecuting all 4 CSP variants on this exact board...")
    table_text, _ = run_sudoku_comparison(board, label="Selected Board")
    print("\n" + table_text)


def handle_search_vs_csp_study():
    print(get_search_vs_csp_study_text())


# ===========================================================================
# Main Interactive Loop
# ===========================================================================

def print_menu():
    print("\n" + "=" * 60)
    print("          AI SEARCH & CONSTRAINT SATISFACTION STUDY          ")
    print("=" * 60)
    print("  1. Solve 8-Puzzle using A*")
    print("  2. Compare 8-Puzzle Heuristics (Misplaced vs Manhattan)")
    print("  3. Check 8-Puzzle Solvability (Inversion Parity)")
    print("  4. Get Rule-Based 8-Puzzle Hint")
    print("  5. Explain A* Solution (Explainable AI - XAI)")
    print("  6. Solve 4x4 Sudoku")
    print("  7. Solve 9x9 Sudoku")
    print("  8. Compare Sudoku CSP Algorithms (Plain / MRV / FC / AC-3)")
    print("  9. Search vs. CSP Academic Study")
    print("  0. Exit")
    print("=" * 60)


def main():
    print("Welcome to the AI Search & CSP Solver Suite!")
    while True:
        print_menu()
        choice = input("Enter your choice [0-9]: ").strip()

        if choice == "1":
            handle_solve_8puzzle()
        elif choice == "2":
            handle_compare_8puzzle_heuristics()
        elif choice == "3":
            handle_check_solvability()
        elif choice == "4":
            handle_rule_based_hint()
        elif choice == "5":
            handle_explainable_ai()
        elif choice == "6":
            handle_solve_sudoku(4)
        elif choice == "7":
            handle_solve_sudoku(9)
        elif choice == "8":
            handle_compare_sudoku()
        elif choice == "9":
            handle_search_vs_csp_study()
        elif choice == "0":
            print("\nThank you for using the AI Search & CSP Solver Suite. Goodbye!\n")
            break
        else:
            print("\n[!] Invalid selection. Please enter a number between 0 and 9.")


if __name__ == "__main__":
    main()
