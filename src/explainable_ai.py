"""
Explainable AI (XAI) Module for 8-Puzzle A* Search
--------------------------------------------------
Provides transparent, interpretable, and mathematically rigorous explanations
of A* search decisions and solution trajectories:

1. Per-Tile Manhattan Distance Decomposition:
   - Decomposes total heuristic h(n) into individual contributions of tiles 1-8.
   - Shows current (r, c) vs goal (gr, gc) coordinates.
   - Guarantees sum(contributions) == manhattan_distance(state).

2. Trajectory Explanation:
   - Step-by-step audit of the optimal solution path.
   - Displays g(n), h(n), f(n) = g(n) + h(n).
   - Identifies which tile moved and the physical effect of the transition.

3. Authentic Search Decision Auditing:
   - Uses real search events recorded during A* execution.
   - Explains why a state was popped from the priority queue:
     min f(n) on frontier, deterministic tie-breaking, and competing candidates.
   - Rigorously distinguishes between:
     (A) Why A* expanded a state during search exploration.
     (B) Why a state belongs to the reconstructed optimal solution path.
"""

try:
    from puzzle_solver import (
        BOARD_SIZE,
        GOAL_POSITIONS,
        GOAL_STATE,
        a_star_search,
        get_per_tile_manhattan,
        manhattan_distance,
        state_to_grid_string,
    )
except ImportError:
    from src.puzzle_solver import (
        BOARD_SIZE,
        GOAL_POSITIONS,
        GOAL_STATE,
        a_star_search,
        get_per_tile_manhattan,
        manhattan_distance,
        state_to_grid_string,
    )


def get_tile_coordinates(state):
    """
    Return a mapping of tile number -> (current_row, current_col).
    Blank tile (0) is included.
    """
    coords = {}
    for idx, tile in enumerate(state):
        coords[tile] = (idx // BOARD_SIZE, idx % BOARD_SIZE)
    return coords


def get_per_tile_manhattan_details(state):
    """
    Compute detailed breakdown of Manhattan distance for every tile 1-8.
    Returns a list of dicts:
      [{"tile": t, "current_pos": (r, c), "goal_pos": (gr, gc), "distance": d}, ...]
    and the total distance.
    """
    details = []
    total = 0
    coords = get_tile_coordinates(state)

    for tile in range(1, 9):
        curr_r, curr_c = coords[tile]
        goal_r, goal_c = GOAL_POSITIONS[tile]
        dist = abs(curr_r - goal_r) + abs(curr_c - goal_c)
        total += dist
        details.append({
            "tile": tile,
            "current_pos": (curr_r, curr_c),
            "goal_pos": (goal_r, goal_c),
            "distance": dist,
            "is_home": (dist == 0),
        })

    return details, total


def explain_single_step(step_number, prev_state, current_state, move_name, g_val):
    """
    Generate an explainable summary for a single step on the solution path.
    """
    h_val = manhattan_distance(current_state)
    f_val = g_val + h_val
    details, total_h = get_per_tile_manhattan_details(current_state)

    if prev_state is None:
        action_desc = "Initial puzzle configuration."
        moved_tile = None
    else:
        # Tile that moved into the previous blank spot
        prev_blank_idx = prev_state.index(0)
        moved_tile = current_state[prev_blank_idx]
        prev_coords = get_tile_coordinates(prev_state)[moved_tile]
        curr_coords = get_tile_coordinates(current_state)[moved_tile]
        goal_coords = GOAL_POSITIONS[moved_tile]

        prev_tile_dist = abs(prev_coords[0] - goal_coords[0]) + abs(prev_coords[1] - goal_coords[1])
        curr_tile_dist = abs(curr_coords[0] - goal_coords[0]) + abs(curr_coords[1] - goal_coords[1])

        if curr_tile_dist == 0:
            action_desc = f"Blank moved {move_name}, sliding tile {moved_tile} into its final goal position."
        elif curr_tile_dist < prev_tile_dist:
            action_desc = f"Blank moved {move_name}, bringing tile {moved_tile} 1 step closer to its goal."
        elif curr_tile_dist > prev_tile_dist:
            action_desc = (
                f"Blank moved {move_name}, shifting tile {moved_tile} temporarily away from its goal "
                f"to clear the way for adjacent tiles."
            )
        else:
            action_desc = f"Blank moved {move_name}, sliding tile {moved_tile} laterally."

    return {
        "step_number": step_number,
        "move_name": move_name,
        "state": current_state,
        "g": g_val,
        "h": h_val,
        "f": f_val,
        "moved_tile": moved_tile,
        "action_desc": action_desc,
        "details": details,
        "total_manhattan": total_h,
    }


def format_step_explanation(step_info):
    """Format step XAI data into clean human-readable output."""
    lines = [
        f"\n==================================================",
        f" STEP {step_info['step_number']} — A* EXPLANATION ({step_info['move_name']})",
        f"==================================================",
        "Puzzle State:",
        state_to_grid_string(step_info["state"]),
        "",
        f"Cost Metrics: g(n) = {step_info['g']} (path cost) | h(n) = {step_info['h']} (heuristic) | f(n) = {step_info['f']}",
        "",
        "PER-TILE MANHATTAN CONTRIBUTIONS:",
    ]

    for d in step_info["details"]:
        home_tag = " [GOAL]" if d["is_home"] else ""
        lines.append(
            f"  Tile {d['tile']}: dist = {d['distance']} "
            f"(curr={d['current_pos']} -> goal={d['goal_pos']}){home_tag}"
        )

    lines.extend([
        f"Total Manhattan Distance: {step_info['total_manhattan']}",
        "",
        "ACTION EXPLANATION:",
        f"  {step_info['action_desc']}",
        "==================================================",
    ])
    return "\n".join(lines)


def format_search_decision_explanation(trace_event):
    """
    Explain why A* expanded a specific node during actual search.
    """
    lines = [
        f"\n--- Node Expansion #{trace_event['expansion_index']} ---",
        f"Selected State f(n) = {trace_event['f']} [g={trace_event['g']}, h={trace_event['h']}]",
        f"Tie-breaker insertion order: #{trace_event['tie_breaker']}",
        f"Frontier size prior to pop: {trace_event['frontier_size']}",
        "Reason for expansion:",
        (
            f"  This node had the absolute minimum f(n) = {trace_event['f']} in the priority queue. "
            f"A* guarantees expanding nodes in non-decreasing order of f(n)."
        ),
    ]

    if trace_event["alternatives"]:
        lines.append("Competing frontier candidates that were NOT chosen:")
        for idx, alt in enumerate(trace_event["alternatives"], 1):
            lines.append(
                f"  Candidate {idx}: f={alt['f']} (tie-breaker #{alt['tie_breaker']})"
            )

    return "\n".join(lines)


def run_full_xai_demonstration(start_state):
    """
    Run an end-to-end A* search with full trace recording and explain
    both the trajectory and actual search expansion decisions.
    """
    result = a_star_search(start_state, manhattan_distance, record_trace=True)
    if not result:
        return "No solution found."

    output_lines = [
        "=================================================================",
        "        EXPLAINABLE AI (XAI): 8-PUZZLE A* SEARCH AUDIT           ",
        "=================================================================",
        f"Start State:",
        state_to_grid_string(start_state),
        f"\nOptimal Solution Length: {result['cost']} moves",
        f"Total Nodes Expanded:    {result['nodes_expanded']}",
        "\nCONCEPTUAL DISTINCTION:",
        "- Why A* EXPANDED a state: At that moment, it had the lowest estimated total",
        "  cost f(n) = g(n) + h(n) on the active search frontier.",
        "- Why a state is on the SOLUTION PATH: After reaching the goal, backwards pointer",
        "  chaining traced the strictly optimal ancestral sequence back to the start.",
    ]

    path = result["path"]
    prev_state = None
    for step_num, (state, move_name) in enumerate(path):
        g_val = step_num
        step_info = explain_single_step(step_num, prev_state, state, move_name, g_val)
        output_lines.append(format_step_explanation(step_info))
        prev_state = state

    output_lines.extend([
        "\n=================================================================",
        " REAL SEARCH DECISION SAMPLES (Actual Expansion Trace)",
        "=================================================================",
    ])

    trace = result.get("search_trace", [])
    # Display first 2 expansions and final expansion
    sample_indices = [0]
    if len(trace) > 2:
        sample_indices.append(1)
    if len(trace) > 1:
        sample_indices.append(len(trace) - 1)

    for idx in sorted(set(sample_indices)):
        if idx < len(trace):
            output_lines.append(format_search_decision_explanation(trace[idx]))

    return "\n".join(output_lines)
