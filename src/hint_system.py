"""
Rule-Based Hint System for the 8-Puzzle
---------------------------------------
Provides intelligent move recommendations using:
1. Rule-Based Heuristic Policy:
   - Evaluates all legal moves of the blank tile.
   - Computes immediate change in Manhattan distance (delta_h = h_curr - h_next).
   - Prefers moves that reduce total Manhattan distance.
   - Uses deterministic tie-breaking.
   - Accurately explains whether the move reduces, preserves, or increases distance.
   - Honestly distinguishes between local greedy moves and global optimal paths.

2. Guaranteed Optimal A* Hint:
   - Runs A* with Manhattan distance to compute the optimal path.
   - Extracts the first move on the true shortest path to the goal.
"""

try:
    from puzzle_solver import (
        GOAL_STATE,
        a_star_search,
        get_neighbors,
        is_solvable,
        manhattan_distance,
        state_to_grid_string,
    )
except ImportError:
    from src.puzzle_solver import (
        GOAL_STATE,
        a_star_search,
        get_neighbors,
        is_solvable,
        manhattan_distance,
        state_to_grid_string,
    )


def get_moving_tile(current_state, next_state):
    """
    Identify which numbered tile moved into the blank position.
    In next_state, the blank (0) is at some new index; the tile that was
    at that index in current_state is the tile that moved.
    """
    blank_idx_in_next = next_state.index(0)
    return current_state[blank_idx_in_next]


def get_rule_based_hint(state):
    """
    Generate a transparent, rule-based recommendation for the next move.

    Policy:
    1. Reject unsolvable states.
    2. Check if already solved.
    3. Generate all legal moves (Up, Down, Left, Right).
    4. For each move, calculate:
       - Resulting state
       - Moving tile
       - New Manhattan distance
       - Delta Manhattan distance (improvement = current_h - new_h)
    5. Rank candidate moves by:
       - Highest Manhattan improvement (delta_h)
       - Deterministic tie-breaker: fixed move order (Up, Down, Left, Right)
    6. Generate an honest, transparent rationale.
    """
    if not is_solvable(state):
        return {
            "solvable": False,
            "solved": False,
            "current_state": state,
            "message": "Puzzle is UNSOLVABLE due to odd inversion parity. No legal moves can reach the goal.",
            "recommended_move": None,
        }

    if state == GOAL_STATE:
        return {
            "solvable": True,
            "solved": True,
            "current_state": state,
            "message": "The puzzle is ALREADY SOLVED! Goal state reached.",
            "recommended_move": None,
        }

    current_h = manhattan_distance(state)
    legal_neighbors = get_neighbors(state)

    # Preferred tie-breaking order for directions
    direction_priority = {"Up": 0, "Down": 1, "Left": 2, "Right": 3}

    candidates = []
    for next_state, move_name in legal_neighbors:
        next_h = manhattan_distance(next_state)
        delta_h = current_h - next_h  # Positive means distance decreased
        moving_tile = get_moving_tile(state, next_state)

        candidates.append({
            "next_state": next_state,
            "move_name": move_name,
            "moving_tile": moving_tile,
            "next_h": next_h,
            "delta_h": delta_h,
            "priority": direction_priority.get(move_name, 99),
        })

    # Sort: highest delta_h first, then lowest priority index for tie-break
    candidates.sort(key=lambda c: (-c["delta_h"], c["priority"]))

    best_candidate = candidates[0]
    move_name = best_candidate["move_name"]
    moving_tile = best_candidate["moving_tile"]
    next_h = best_candidate["next_h"]
    delta_h = best_candidate["delta_h"]

    # Generate transparent explanation
    if delta_h > 0:
        if next_h == 0:
            reason = f"Moving blank {move_name} slides tile {moving_tile} into its final goal position, solving the puzzle!"
        else:
            reason = (
                f"Moving blank {move_name} slides tile {moving_tile} closer to its goal position, "
                f"reducing total Manhattan distance from {current_h} to {next_h}."
            )
    elif delta_h == 0:
        reason = (
            f"No legal move immediately reduces Manhattan distance. Moving blank {move_name} "
            f"(sliding tile {moving_tile}) is neutral, maintaining Manhattan distance at {current_h}. "
            "This rearranges tiles to enable future progress."
        )
    else:
        reason = (
            f"Local minimum encountered: every legal move temporarily increases Manhattan distance. "
            f"The least disruptive legal move is moving blank {move_name} (sliding tile {moving_tile}), "
            f"increasing Manhattan distance from {current_h} to {next_h}. "
            "Note: Greedy heuristics cannot see beyond immediate moves; use A* search for guaranteed progress."
        )

    return {
        "solvable": True,
        "solved": False,
        "current_state": state,
        "recommended_move": move_name,
        "moving_tile": moving_tile,
        "current_manhattan": current_h,
        "new_manhattan": next_h,
        "delta_h": delta_h,
        "reason": reason,
        "candidates": candidates,
        "is_greedy": True,
    }


def get_optimal_a_star_hint(state):
    """
    Compute the guaranteed optimal next move using full A* search
    with the Manhattan Distance heuristic.
    """
    if not is_solvable(state):
        return {
            "solvable": False,
            "solved": False,
            "message": "Puzzle is UNSOLVABLE. A* search cannot be executed.",
        }

    if state == GOAL_STATE:
        return {
            "solvable": True,
            "solved": True,
            "message": "Puzzle is ALREADY SOLVED! Cost = 0.",
        }

    result = a_star_search(state, manhattan_distance)
    if not result or len(result["path"]) < 2:
        return None

    first_step_state, move_name = result["path"][1]
    moving_tile = get_moving_tile(state, first_step_state)
    current_h = manhattan_distance(state)
    next_h = manhattan_distance(first_step_state)

    return {
        "solvable": True,
        "solved": False,
        "recommended_move": move_name,
        "moving_tile": moving_tile,
        "current_manhattan": current_h,
        "new_manhattan": next_h,
        "total_optimal_cost": result["cost"],
        "reason": (
            f"Moving blank {move_name} (sliding tile {moving_tile}) is step 1 of "
            f"the mathematically guaranteed shortest {result['cost']}-move A* solution path."
        ),
        "is_optimal": True,
    }


def format_hint_display(hint_data):
    """Format hint information into a clean, human-readable terminal output."""
    if not hint_data.get("solvable", True):
        return f"\n[!] HINT REJECTED: {hint_data['message']}\n"

    if hint_data.get("solved", False):
        return f"\n[*] {hint_data['message']}\n"

    lines = [
        "\n==================================================",
        "             8-PUZZLE MOVE RECOMMENDATION         ",
        "==================================================",
        "CURRENT STATE:",
        state_to_grid_string(hint_data["current_state"]),
        "",
        f"RECOMMENDED MOVE (BLANK):  {hint_data['recommended_move']}",
        f"MOVING TILE:               {hint_data['moving_tile']}",
        f"CURRENT MANHATTAN DISTANCE: {hint_data['current_manhattan']}",
        f"NEW MANHATTAN DISTANCE:     {hint_data['new_manhattan']}",
        "",
        "EXPLANATION / RATIONALE:",
        f"  {hint_data['reason']}",
        "==================================================",
    ]
    return "\n".join(lines)
