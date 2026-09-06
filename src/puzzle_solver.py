import heapq
import itertools


# ============================================================
# 8-PUZZLE SOLVER USING A* SEARCH
# ============================================================
#
# Goal State:
#
#     1 2 3
#     4 5 6
#     7 8 0
#
# 0 represents the blank space.
#
# A* formula:
#
#     f(n) = g(n) + h(n)
#
# g(n) = cost from start state to current state
# h(n) = estimated cost from current state to goal
# f(n) = total estimated cost
#
# Two heuristics are implemented:
# 1. Misplaced Tiles
# 2. Manhattan Distance
# ============================================================


# ============================================================
# GOAL STATE
# ============================================================

GOAL = (
    1, 2, 3,
    4, 5, 6,
    7, 8, 0
)


# ============================================================
# HEURISTIC 1: MISPLACED TILES
# ============================================================

def misplaced_tiles(state):
    """
    Count the number of tiles that are not in their
    correct goal positions.

    The blank tile (0) is ignored.

    Example:
        Current:
        1 3 2
        4 5 6
        7 8 0

        Only 2 and 3 are misplaced.

        h(n) = 2
    """

    count = 0

    for i in range(9):

        # Ignore blank tile
        if state[i] != 0 and state[i] != GOAL[i]:
            count += 1

    return count


# ============================================================
# HEURISTIC 2: MANHATTAN DISTANCE
# ============================================================

def manhattan_distance(state):
    """
    Calculate the Manhattan Distance.

    For each tile:

        |current_row - goal_row|
        +
        |current_column - goal_column|

    The blank tile (0) is ignored.
    """

    distance = 0

    for current_index in range(9):

        tile = state[current_index]

        # Ignore blank tile
        if tile == 0:
            continue

        # Current row and column
        current_row, current_col = divmod(
            current_index, 3
        )

        # Goal position of this tile
        goal_index = GOAL.index(tile)

        goal_row, goal_col = divmod(
            goal_index, 3
        )

        # Add horizontal and vertical distance
        distance += abs(
            current_row - goal_row
        )

        distance += abs(
            current_col - goal_col
        )

    return distance


# ============================================================
# GENERATE NEIGHBORING STATES
# ============================================================

def get_neighbors(state):
    """
    Generate all possible states by moving the blank tile.

    The blank can move:
        Up
        Down
        Left
        Right

    depending on its current position.
    """

    neighbors = []

    # Find blank position
    blank_index = state.index(0)

    row, col = divmod(
        blank_index, 3
    )

    # Possible movements
    moves = [
        (-1, 0),     # Up
        (1, 0),      # Down
        (0, -1),     # Left
        (0, 1)       # Right
    ]

    for row_change, col_change in moves:

        new_row = row + row_change
        new_col = col + col_change

        # Check whether the new position is valid
        if 0 <= new_row < 3 and 0 <= new_col < 3:

            new_index = new_row * 3 + new_col

            # Convert tuple to list so we can swap values
            new_state = list(state)

            # Move blank tile
            new_state[blank_index], new_state[new_index] = (
                new_state[new_index],
                new_state[blank_index]
            )

            # Convert back to tuple
            neighbors.append(
                tuple(new_state)
            )

    return neighbors


# ============================================================
# CHECK WHETHER PUZZLE IS SOLVABLE
# ============================================================

def is_solvable(state):
    """
    Check whether an 8-puzzle is solvable.

    For a 3x3 puzzle:
        Even number of inversions = solvable
        Odd number of inversions  = unsolvable

    An inversion occurs when a larger tile appears
    before a smaller tile.
    """

    # Remove blank tile
    values = [
        tile for tile in state
        if tile != 0
    ]

    inversions = 0

    # Count inversions
    for i in range(len(values)):

        for j in range(i + 1, len(values)):

            if values[i] > values[j]:
                inversions += 1

    return inversions % 2 == 0


# ============================================================
# A* SEARCH ALGORITHM
# ============================================================

def a_star(start, heuristic):
    """
    Solve the puzzle using A* Search.

    Parameters:
        start     : initial puzzle state
        heuristic : heuristic function

    Returns:
        path     : list of states from start to goal
        expanded : number of nodes expanded
    """

    # Counter provides deterministic tie-breaking
    counter = itertools.count()

    # Calculate initial heuristic
    h = heuristic(start)

    # Priority queue
    #
    # Each item:
    # (f_cost, g_cost, counter, state)
    #
    # f(n) = g(n) + h(n)

    priority_queue = [
        (
            h,
            0,
            next(counter),
            start
        )
    ]

    # Best known cost from start to each state
    g_cost = {
        start: 0
    }

    # Parent of each state
    parent = {
        start: None
    }

    # Number of nodes expanded
    expanded = 0

    # Continue until queue is empty
    while priority_queue:

        # Remove state with lowest f value
        f, g, _, current = heapq.heappop(
            priority_queue
        )

        # Ignore outdated queue entries
        if g != g_cost.get(current):
            continue

        # Count this node as expanded
        expanded += 1

        # ----------------------------------------------------
        # GOAL CHECK
        # ----------------------------------------------------

        if current == GOAL:

            path = []

            state = current

            # Reconstruct path by following parents
            while state is not None:

                path.append(state)

                state = parent[state]

            # Reverse path to get:
            # start -> goal
            path.reverse()

            return path, expanded

        # ----------------------------------------------------
        # GENERATE SUCCESSORS
        # ----------------------------------------------------

        for neighbor in get_neighbors(current):

            # Every move costs 1
            new_g = g + 1

            # If this is a better path to the neighbor
            if new_g < g_cost.get(
                neighbor,
                float("inf")
            ):

                # Save the better cost
                g_cost[neighbor] = new_g

                # Save parent
                parent[neighbor] = current

                # Calculate heuristic
                h = heuristic(neighbor)

                # Calculate f(n)
                f = new_g + h

                # Add neighbor to priority queue
                heapq.heappush(
                    priority_queue,
                    (
                        f,
                        new_g,
                        next(counter),
                        neighbor
                    )
                )

    # No solution found
    return None, expanded


# ============================================================
# PRINT PUZZLE STATE
# ============================================================

def print_state(state):
    """
    Display a puzzle state as a 3x3 grid.
    """

    for i in range(0, 9, 3):

        print(
            state[i],
            state[i + 1],
            state[i + 2]
        )

    print()


# ============================================================
# PRINT SOLUTION PATH
# ============================================================

def print_solution(path):
    """
    Print every state in the solution path.
    """

    if path is None:
        print("No solution found.")
        return

    for step, state in enumerate(path):

        print("Step", step)
        print_state(state)


# ============================================================
# VALIDATE USER INPUT
# ============================================================

def get_user_input():
    """
    Read and validate the initial puzzle state.

    The user must enter:
        9 numbers
        containing every number from 0 to 8 exactly once.
    """

    print("Enter 9 numbers separated by spaces.")
    print("Use 0 for the blank space.")
    print()

    user_input = input(
        "Enter initial state: "
    )

    try:

        state = tuple(
            map(int, user_input.split())
        )

    except ValueError:

        print()
        print("ERROR: Please enter numbers only.")
        return None

    # Check number of values
    if len(state) != 9:

        print()
        print("ERROR: Please enter exactly 9 numbers.")
        return None

    # Check that numbers 0-8 are used exactly once
    if set(state) != set(range(9)):

        print()
        print(
            "ERROR: Use every number from 0 to 8 exactly once."
        )

        return None

    return state


# ============================================================
# DISPLAY HEURISTIC VALUES
# ============================================================

def display_heuristic_values(state):
    """
    Display the initial heuristic values.
    """

    misplaced = misplaced_tiles(state)

    manhattan = manhattan_distance(state)

    print()
    print("Initial Heuristic Values")
    print("------------------------")

    print(
        "Misplaced Tiles :",
        misplaced
    )

    print(
        "Manhattan       :",
        manhattan
    )


# ============================================================
# DISPLAY COMPARISON
# ============================================================

def display_comparison(
    path1,
    expanded1,
    path2,
    expanded2
):
    """
    Compare both heuristics based on:
    - Solution cost
    - Nodes expanded
    """

    cost1 = len(path1) - 1
    cost2 = len(path2) - 1

    print()
    print("=" * 55)
    print("                 HEURISTIC COMPARISON")
    print("=" * 55)

    print()

    print(
        "{:<25} {:<15} {:<15}".format(
            "Heuristic",
            "Solution Cost",
            "Nodes Expanded"
        )
    )

    print("-" * 55)

    print(
        "{:<25} {:<15} {:<15}".format(
            "Misplaced Tiles",
            cost1,
            expanded1
        )
    )

    print(
        "{:<25} {:<15} {:<15}".format(
            "Manhattan Distance",
            cost2,
            expanded2
        )
    )

    print()

    # --------------------------------------------------------
    # Compare nodes
    # --------------------------------------------------------

    if expanded2 < expanded1:

        reduction = (
            (expanded1 - expanded2)
            / expanded1
        ) * 100

        print(
            "Result: Manhattan Distance expanded fewer nodes."
        )

        print(
            "Nodes reduced by: {:.2f}%".format(
                reduction
            )
        )

    elif expanded1 < expanded2:

        reduction = (
            (expanded2 - expanded1)
            / expanded2
        ) * 100

        print(
            "Result: Misplaced Tiles expanded fewer nodes."
        )

        print(
            "Nodes reduced by: {:.2f}%".format(
                reduction
            )
        )

    else:

        print(
            "Result: Both heuristics expanded the same number of nodes."
        )

    # --------------------------------------------------------
    # Compare solution costs
    # --------------------------------------------------------

    print()

    if cost1 == cost2:

        print(
            "Both heuristics found solutions with the same cost."
        )

        print(
            "Therefore, both produced an optimal solution for this puzzle."
        )

    else:

        print(
            "The solution costs are different."
        )


# ============================================================
# DISPLAY CONCLUSION
# ============================================================

def display_conclusion():
    """
    Display the theoretical conclusion of the comparison.
    """

    print()
    print("=" * 55)
    print("                    CONCLUSION")
    print("=" * 55)

    print()

    print(
        "Misplaced Tiles only checks whether a tile is"
    )

    print(
        "in the correct position or not."
    )

    print()

    print(
        "Manhattan Distance measures how far each tile"
    )

    print(
        "is from its goal position."
    )

    print()

    print(
        "Therefore, Manhattan Distance is generally"
    )

    print(
        "a more informed heuristic."
    )

    print()

    print(
        "Both heuristics are admissible because they"
    )

    print(
        "do not overestimate the actual remaining cost."
    )

    print()

    print(
        "A* can therefore use these heuristics to find"
    )

    print(
        "an optimal solution."
    )

    print()

    print(
        "A more informed heuristic generally allows"
    )

    print(
        "A* to focus the search better and expand"
    )

    print(
        "fewer nodes."
    )


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():

    print("=" * 55)
    print("             8-PUZZLE A* SOLVER")
    print("=" * 55)

    print()
    print("Goal State:")
    print_state(GOAL)

    # --------------------------------------------------------
    # Get initial state
    # --------------------------------------------------------

    start = get_user_input()

    # Invalid input
    if start is None:
        return

    # --------------------------------------------------------
    # Display initial state
    # --------------------------------------------------------

    print()
    print("=" * 55)
    print("                  INITIAL STATE")
    print("=" * 55)

    print_state(start)

    # --------------------------------------------------------
    # Check if already solved
    # --------------------------------------------------------

    if start == GOAL:

        print("The puzzle is already solved.")

        print()
        print("Solution Cost: 0")
        print("Nodes Expanded: 1")

        return

    # --------------------------------------------------------
    # Check solvability
    # --------------------------------------------------------

    if not is_solvable(start):

        print("=" * 55)
        print("               PUZZLE NOT SOLVABLE")
        print("=" * 55)

        print()
        print(
            "This puzzle cannot reach the goal state."
        )

        print(
            "Please enter a different puzzle."
        )

        return

    print("Puzzle is solvable.")

    # --------------------------------------------------------
    # Display heuristic values
    # --------------------------------------------------------

    display_heuristic_values(start)

    # --------------------------------------------------------
    # Run A* with Misplaced Tiles
    # --------------------------------------------------------

    print()
    print("=" * 55)
    print("       RUNNING A* - MISPLACED TILES")
    print("=" * 55)

    path1, expanded1 = a_star(
        start,
        misplaced_tiles
    )

    # --------------------------------------------------------
    # Run A* with Manhattan Distance
    # --------------------------------------------------------

    print()
    print("=" * 55)
    print("       RUNNING A* - MANHATTAN DISTANCE")
    print("=" * 55)

    path2, expanded2 = a_star(
        start,
        manhattan_distance
    )

    # --------------------------------------------------------
    # Check whether solutions were found
    # --------------------------------------------------------

    if path1 is None or path2 is None:

        print()
        print("ERROR: A solution could not be found.")

        return

    # --------------------------------------------------------
    # Display Misplaced Tiles result
    # --------------------------------------------------------

    print()
    print("=" * 55)
    print("             MISPLACED TILES RESULT")
    print("=" * 55)

    print()

    print(
        "Solution Cost:",
        len(path1) - 1
    )

    print(
        "Nodes Expanded:",
        expanded1
    )

    print()

    print("Solution Path:")
    print()

    print_solution(path1)

    # --------------------------------------------------------
    # Display Manhattan Distance result
    # --------------------------------------------------------

    print()
    print("=" * 55)
    print("           MANHATTAN DISTANCE RESULT")
    print("=" * 55)

    print()

    print(
        "Solution Cost:",
        len(path2) - 1
    )

    print(
        "Nodes Expanded:",
        expanded2
    )

    print()

    print("Solution Path:")
    print()

    print_solution(path2)

    # --------------------------------------------------------
    # Compare heuristics
    # --------------------------------------------------------

    display_comparison(
        path1,
        expanded1,
        path2,
        expanded2
    )

    # --------------------------------------------------------
    # Final conclusion
    # --------------------------------------------------------

    display_conclusion()

    print()
    print("=" * 55)
    print("                  PROGRAM COMPLETE")
    print("=" * 55)


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()