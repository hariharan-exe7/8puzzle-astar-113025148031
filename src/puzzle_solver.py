"""
8-Puzzle Solver using A* Search
--------------------------------
This program solves the classic 8-Puzzle using the A* search algorithm.
It supports two heuristics:
    1. Misplaced Tiles
    2. Manhattan Distance

It solves the same puzzle with both heuristics and compares:
    - Solution cost (number of moves)
    - Number of nodes expanded

A puzzle state is represented as a tuple of 9 integers (0-8), read
left-to-right, top-to-bottom. The number 0 represents the blank tile.

Example state (1 3 6 5 0 2 4 7 8) means the board looks like:
    1 3 6
    5 0 2
    4 7 8

Author: [YOUR NAME]
"""

import heapq
import itertools

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 0)
BOARD_SIZE = 3  # 3x3 board

# Pre-compute the goal position (row, col) of every tile number for speed.
# GOAL_POSITIONS[tile] = (row, col)
GOAL_POSITIONS = {}
for index, tile in enumerate(GOAL_STATE):
    GOAL_POSITIONS[tile] = (index // BOARD_SIZE, index % BOARD_SIZE)


# ---------------------------------------------------------------------------
# Basic state helpers
# ---------------------------------------------------------------------------

def state_to_grid_string(state):
    """Convert a flat 9-tuple state into a readable 3x3 string for printing."""
    rows = []
    for r in range(BOARD_SIZE):
        row_tiles = state[r * BOARD_SIZE:(r + 1) * BOARD_SIZE]
        row_str = " ".join(str(t) if t != 0 else "_" for t in row_tiles)
        rows.append(row_str)
    return "\n".join(rows)


def get_neighbors(state):
    """
    Given a state, return a list of (new_state, move_description) tuples
    representing all legal moves of the blank tile (0).

    The blank tile can move Up, Down, Left, or Right, as long as it does
    not move outside the 3x3 grid.
    """
    neighbors = []
    blank_index = state.index(0)
    row, col = blank_index // BOARD_SIZE, blank_index % BOARD_SIZE

    # (row_change, col_change, move_name)
    possible_moves = [
        (-1, 0, "Up"),
        (1, 0, "Down"),
        (0, -1, "Left"),
        (0, 1, "Right"),
    ]

    for d_row, d_col, move_name in possible_moves:
        new_row, new_col = row + d_row, col + d_col
        if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
            new_index = new_row * BOARD_SIZE + new_col
            new_state = list(state)
            # Swap blank with the target tile
            new_state[blank_index], new_state[new_index] = (
                new_state[new_index],
                new_state[blank_index],
            )
            neighbors.append((tuple(new_state), move_name))

    return neighbors


# ---------------------------------------------------------------------------
# Solvability check
# ---------------------------------------------------------------------------

def count_inversions(state):
    """
    Count the number of inversions in the puzzle (ignoring the blank tile).

    An inversion is a pair of tiles (a, b) where a appears before b in the
    flattened list, but a's value is greater than b's value.
    """
    tiles = [t for t in state if t != 0]
    inversions = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversions += 1
    return inversions


def is_solvable(state):
    """
    For a 3x3 (odd width) 8-puzzle, a state is solvable if and only if the
    number of inversions is EVEN. The position of the blank does not matter
    for an odd-width board.
    """
    return count_inversions(state) % 2 == 0


# ---------------------------------------------------------------------------
# Heuristic functions
# ---------------------------------------------------------------------------

def misplaced_tiles(state):
    """
    Heuristic 1: Misplaced Tiles.

    Counts how many tiles are NOT in their goal position.
    The blank tile (0) is never counted.
    """
    count = 0
    for index, tile in enumerate(state):
        if tile == 0:
            continue  # blank tile is ignored
        goal_index = tile - 1  # since GOAL_STATE lists 1..8 then 0
        if index != goal_index:
            count += 1
    return count


def manhattan_distance(state):
    """
    Heuristic 2: Manhattan Distance.

    For every non-blank tile, add the distance
        |current_row - goal_row| + |current_col - goal_col|
    The blank tile (0) is never counted.
    """
    total_distance = 0
    for index, tile in enumerate(state):
        if tile == 0:
            continue  # blank tile is ignored
        current_row, current_col = index // BOARD_SIZE, index % BOARD_SIZE
        goal_row, goal_col = GOAL_POSITIONS[tile]
        total_distance += abs(current_row - goal_row) + abs(current_col - goal_col)
    return total_distance


HEURISTICS = {
    "misplaced": misplaced_tiles,
    "manhattan": manhattan_distance,
}


# ---------------------------------------------------------------------------
# A* Search
# ---------------------------------------------------------------------------

def reconstruct_path(came_from, current_state):
    """
    Walk backwards through the came_from dictionary to build the list of
    moves from the start state to the goal state.

    Returns a list of (state, move_description) pairs in order from
    start to goal. The starting state has move_description = "Start".
    """
    path = []
    while current_state in came_from:
        previous_state, move_name = came_from[current_state]
        path.append((current_state, move_name))
        current_state = previous_state
    path.append((current_state, "Start"))
    path.reverse()
    return path


def get_per_tile_manhattan(state):
    """
    Calculate the Manhattan distance contribution for each tile (1-8).
    Returns a dictionary mapping tile number -> distance.
    The blank tile (0) is omitted (distance = 0).
    The sum of these values strictly equals manhattan_distance(state).
    """
    contributions = {}
    for index, tile in enumerate(state):
        if tile == 0:
            continue
        current_row, current_col = index // BOARD_SIZE, index % BOARD_SIZE
        goal_row, goal_col = GOAL_POSITIONS[tile]
        contributions[tile] = abs(current_row - goal_row) + abs(current_col - goal_col)
    return contributions


def explain_solvability(state):
    """
    Provide a logical step-by-step reasoning for why an 8-puzzle state
    is solvable or unsolvable based on the inversion parity rule.
    """
    tiles = [t for t in state if t != 0]
    inversion_pairs = []
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversion_pairs.append((tiles[i], tiles[j]))

    inv_count = len(inversion_pairs)
    is_even = (inv_count % 2 == 0)

    return {
        "state": state,
        "tiles_sequence": tiles,
        "inversion_count": inv_count,
        "inversion_pairs": inversion_pairs,
        "parity": "EVEN" if is_even else "ODD",
        "is_solvable": is_even,
        "rule": (
            "For a 3x3 8-puzzle with odd grid width (N=3), sliding the blank tile horizontally "
            "does not change the relative order of tiles, while sliding the blank vertically shifts "
            "one tile past two other tiles, changing the inversion count by +2, -2, or 0. "
            "In all cases, the parity (evenness/oddness) of the inversion count is an invariant! "
            "Because the standard goal state has 0 inversions (EVEN), only initial states with "
            "an EVEN inversion count can reach the goal state."
        ),
        "verdict": "SOLVABLE" if is_even else "UNSOLVABLE - A* search rejected before execution",
    }


def a_star_search(start_state, heuristic_function, record_trace=False):
    """
    Run A* search from start_state to GOAL_STATE using the given heuristic
    function.

    Returns a dictionary with:
        "path"           : list of (state, move) from start to goal
        "cost"           : number of moves in the optimal solution
        "nodes_expanded" : how many states were popped from the frontier
                            and actually processed (expanded)
        "search_trace"   : (optional) list of decision events if record_trace=True

    Implementation notes for the viva:
    - We use heapq as a priority queue. Each entry is
          (f_score, tie_breaker, state)
      The tie_breaker is a strictly increasing counter. This keeps the
      heap comparisons deterministic and avoids ever trying to compare
      two tuples directly (which would fail because states are tuples
      of ints and there is nothing to compare when f_scores tie).
    - g_score keeps the best known cost from start to each state.
    - When we pop a state from the heap, if we already reached it with a
      strictly better (lower) g_score before, we skip it. This avoids
      expanding outdated / stale queue entries.
    """
    counter = itertools.count()  # unique increasing id, used to break ties

    start_g = 0
    start_h = heuristic_function(start_state)
    start_f = start_g + start_h

    frontier = []
    heapq.heappush(frontier, (start_f, next(counter), start_state))

    g_score = {start_state: 0}
    came_from = {}
    visited = set()  # states that have been expanded (finalized)

    nodes_expanded = 0
    search_trace = [] if record_trace else None

    while frontier:
        current_f, tie_breaker, current_state = heapq.heappop(frontier)

        # Skip if this state was already expanded with an equal or better
        # cost. This handles "stale" entries left in the heap.
        if current_state in visited:
            continue

        visited.add(current_state)
        nodes_expanded += 1

        if record_trace:
            # Capture actual search decision data at expansion time
            # Peek at other states in the frontier (up to 3 alternatives)
            alternatives = []
            for item in sorted(frontier)[:3]:
                alternatives.append({
                    "f": item[0],
                    "state": item[2],
                    "tie_breaker": item[1]
                })
            search_trace.append({
                "expansion_index": nodes_expanded,
                "state": current_state,
                "f": current_f,
                "g": g_score[current_state],
                "h": heuristic_function(current_state),
                "tie_breaker": tie_breaker,
                "frontier_size": len(frontier) + 1,
                "alternatives": alternatives,
                "is_goal": (current_state == GOAL_STATE)
            })

        if current_state == GOAL_STATE:
            path = reconstruct_path(came_from, current_state)
            result = {
                "path": path,
                "cost": g_score[current_state],
                "nodes_expanded": nodes_expanded,
            }
            if record_trace:
                result["search_trace"] = search_trace
            return result

        for neighbor_state, move_name in get_neighbors(current_state):
            tentative_g = g_score[current_state] + 1  # every move costs 1

            if neighbor_state in visited:
                continue

            if tentative_g < g_score.get(neighbor_state, float("inf")):
                g_score[neighbor_state] = tentative_g
                came_from[neighbor_state] = (current_state, move_name)
                f_score = tentative_g + heuristic_function(neighbor_state)
                heapq.heappush(frontier, (f_score, next(counter), neighbor_state))

    # If the frontier empties without reaching the goal, no solution exists.
    # (This should not happen for a puzzle that already passed is_solvable.)
    return None


# ---------------------------------------------------------------------------
# Input handling
# ---------------------------------------------------------------------------

def parse_state_input(raw_input_text):
    """
    Convert a raw user input string like "1 3 6 5 0 2 4 7 8" into a tuple
    of 9 integers, after validating that it contains exactly the numbers
    0 through 8, each appearing once.

    Raises ValueError with a clear message if the input is invalid.
    """
    parts = raw_input_text.split()

    if len(parts) != 9:
        raise ValueError(
            f"Expected exactly 9 numbers, but got {len(parts)}. "
            "Please enter the puzzle as 9 numbers separated by spaces."
        )

    try:
        numbers = [int(p) for p in parts]
    except ValueError:
        raise ValueError("All 9 values must be integers between 0 and 8.")

    if sorted(numbers) != list(range(9)):
        raise ValueError(
            "Input must contain each of the numbers 0-8 exactly once."
        )

    return tuple(numbers)


def get_puzzle_input_from_user():
    """
    Prompt the user for a starting puzzle state and keep asking until a
    valid one is provided.
    """
    print("Enter the initial 8-puzzle state as 9 numbers (0-8), separated")
    print("by spaces, reading left-to-right, top-to-bottom. Use 0 for the")
    print("blank tile. Example: 1 3 6 5 0 2 4 7 8")

    while True:
        raw_text = input("Enter puzzle state: ")
        try:
            return parse_state_input(raw_text)
        except ValueError as error:
            print(f"Invalid input: {error}")
            print("Please try again.\n")


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_solution_path(path):
    """Print every state in the solution path, from start to goal."""
    for step_number, (state, move_name) in enumerate(path):
        print(f"\nStep {step_number} ({move_name}):")
        print(state_to_grid_string(state))


def print_heuristic_result(name, result):
    """Print a short summary for a single heuristic's A* result."""
    print(f"\n--- Results using {name} heuristic ---")
    print(f"Solution cost (moves): {result['cost']}")
    print(f"Nodes expanded:        {result['nodes_expanded']}")


def print_comparison(misplaced_result, manhattan_result):
    """
    Print a comparison table between the two heuristics, and a conclusion
    based on the ACTUAL numbers produced in this run (never hard-coded).
    """
    print("\n=========================================")
    print(" HEURISTIC COMPARISON")
    print("=========================================")
    print(f"{'Heuristic':<20}{'Solution Cost':<16}{'Nodes Expanded':<16}")
    print(f"{'Misplaced Tiles':<20}{misplaced_result['cost']:<16}"
          f"{misplaced_result['nodes_expanded']:<16}")
    print(f"{'Manhattan Distance':<20}{manhattan_result['cost']:<16}"
          f"{manhattan_result['nodes_expanded']:<16}")

    same_cost = misplaced_result["cost"] == manhattan_result["cost"]
    print(f"\nBoth heuristics found the same optimal cost: {same_cost}")

    m_nodes = misplaced_result["nodes_expanded"]
    d_nodes = manhattan_result["nodes_expanded"]

    print("\nConclusion:")
    if same_cost:
        print("Both heuristics are admissible, so both correctly found the")
        print("optimal (lowest-cost) solution, as expected from A*.")
    else:
        print("WARNING: the two heuristics produced different costs. This")
        print("would indicate a bug, since both heuristics are admissible")
        print("and A* is guaranteed to return an optimal solution with an")
        print("admissible heuristic.")

    if m_nodes > 0:
        reduction_percent = ((m_nodes - d_nodes) / m_nodes) * 100
    else:
        reduction_percent = 0.0

    if d_nodes < m_nodes:
        print(f"Manhattan Distance expanded fewer nodes than Misplaced Tiles")
        print(f"in this run ({d_nodes} vs {m_nodes}), a reduction of "
              f"{reduction_percent:.2f}%.")
        print("This is expected because Manhattan Distance is a more")
        print("informed heuristic (its estimates are closer to the true")
        print("remaining cost), so A* can discard more unpromising paths")
        print("earlier in the search.")
    elif d_nodes == m_nodes:
        print("Both heuristics expanded the same number of nodes in this")
        print("particular run. This can happen for small/simple puzzles,")
        print("even though Manhattan Distance is, in general, at least as")
        print("informed as Misplaced Tiles.")
    else:
        print("In this particular run, Misplaced Tiles expanded fewer or")
        print("equal nodes compared to Manhattan Distance. This is unusual")
        print("but not mathematically impossible depending on tie-breaking")
        print("and implementation details; it does not violate optimality,")
        print("since both heuristics are admissible.")


# ---------------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------------

def main():
    print("=========================================")
    print(" 8-PUZZLE SOLVER USING A* SEARCH")
    print("=========================================\n")

    start_state = get_puzzle_input_from_user()

    print("\nInitial state:")
    print(state_to_grid_string(start_state))

    if not is_solvable(start_state):
        print("\nResult: This puzzle is NOT solvable.")
        print("(The number of inversions is odd, so no sequence of moves")
        print("can reach the goal state.)")
        return

    print("\nResult: This puzzle IS solvable. Running A* search...")

    if start_state == GOAL_STATE:
        print("\nThe puzzle is already solved! Solution cost = 0.")

    # Run A* with Misplaced Tiles heuristic
    misplaced_result = a_star_search(start_state, misplaced_tiles)

    # Run A* with Manhattan Distance heuristic
    manhattan_result = a_star_search(start_state, manhattan_distance)

    print_heuristic_result("Misplaced Tiles", misplaced_result)
    print_heuristic_result("Manhattan Distance", manhattan_result)

    print("\nSolution path (using Manhattan Distance heuristic):")
    print_solution_path(manhattan_result["path"])

    print_comparison(misplaced_result, manhattan_result)


if __name__ == "__main__":
    main()
