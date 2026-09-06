import heapq
import itertools


# ==========================================
# GOAL STATE
# ==========================================

GOAL = (
    1, 2, 3,
    4, 5, 6,
    7, 8, 0
)


# ==========================================
# HEURISTIC 1: MISPLACED TILES
# ==========================================

def misplaced_tiles(state):
    count = 0

    for i in range(9):
        # Ignore blank tile
        if state[i] != 0 and state[i] != GOAL[i]:
            count += 1

    return count


# ==========================================
# HEURISTIC 2: MANHATTAN DISTANCE
# ==========================================

def manhattan_distance(state):
    distance = 0

    for i in range(9):

        tile = state[i]

        # Ignore blank tile
        if tile != 0:

            current_row, current_col = divmod(i, 3)

            goal_index = GOAL.index(tile)
            goal_row, goal_col = divmod(goal_index, 3)

            distance += abs(current_row - goal_row)
            distance += abs(current_col - goal_col)

    return distance


# ==========================================
# GENERATE NEIGHBORING STATES
# ==========================================

def get_neighbors(state):

    neighbors = []

    # Find blank tile
    zero_index = state.index(0)

    row, col = divmod(zero_index, 3)

    # Possible movements:
    # Up, Down, Left, Right
    moves = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    for dr, dc in moves:

        new_row = row + dr
        new_col = col + dc

        # Check valid position
        if 0 <= new_row < 3 and 0 <= new_col < 3:

            new_index = new_row * 3 + new_col

            # Convert tuple to list
            new_state = list(state)

            # Swap blank and tile
            new_state[zero_index], new_state[new_index] = \
                new_state[new_index], new_state[zero_index]

            # Convert back to tuple
            neighbors.append(tuple(new_state))

    return neighbors


# ==========================================
# CHECK PUZZLE SOLVABILITY
# ==========================================

def is_solvable(state):

    # Remove blank
    values = [
        x for x in state
        if x != 0
    ]

    inversions = 0

    # Count inversions
    for i in range(len(values)):

        for j in range(i + 1, len(values)):

            if values[i] > values[j]:
                inversions += 1

    # For a 3x3 puzzle:
    # Even number of inversions = solvable
    return inversions % 2 == 0


# ==========================================
# A* SEARCH
# ==========================================

def a_star(start, heuristic):

    # Counter is used to break priority ties
    counter = itertools.count()

    # Calculate initial heuristic
    h = heuristic(start)

    # Priority queue
    # (f, g, counter, state)
    priority_queue = [
        (h, 0, next(counter), start)
    ]

    # Best cost to reach each state
    g_cost = {
        start: 0
    }

    # Parent of each state
    parent = {
        start: None
    }

    # Number of expanded nodes
    expanded = 0

    while priority_queue:

        # Get state with smallest f value
        f, g, _, current = heapq.heappop(
            priority_queue
        )

        # Ignore outdated entry
        if g != g_cost.get(current):
            continue

        # Count expanded node
        expanded += 1

        # Goal reached
        if current == GOAL:

            path = []

            state = current

            # Reconstruct solution path
            while state is not None:

                path.append(state)

                state = parent[state]

            # Reverse path
            path.reverse()

            return path, expanded

        # Generate neighbors
        for neighbor in get_neighbors(current):

            # Each move has cost 1
            new_g = g + 1

            # If a better path is found
            if new_g < g_cost.get(
                neighbor,
                float('inf')
            ):

                # Store new cost
                g_cost[neighbor] = new_g

                # Store parent
                parent[neighbor] = current

                # Calculate heuristic
                h = heuristic(neighbor)

                # f(n) = g(n) + h(n)
                f = new_g + h

                # Add to priority queue
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


# ==========================================
# PRINT PUZZLE
# ==========================================

def print_state(state):

    for i in range(0, 9, 3):

        print(
            state[i],
            state[i + 1],
            state[i + 2]
        )

    print()


# ==========================================
# MAIN PROGRAM
# ==========================================

def main():

    print("======================================")
    print("          8-PUZZLE A* SOLVER")
    print("======================================")

    print()
    print("Enter 9 numbers separated by spaces.")
    print("Use 0 for the blank space.")
    print()

    # ======================================
    # GET USER INPUT
    # ======================================

    user_input = input("Enter initial state: ")

    try:

        start = tuple(
            map(int, user_input.split())
        )

    except ValueError:

        print("\nInvalid input!")
        print("Please enter numbers only.")
        return

    # ======================================
    # VALIDATE NUMBER OF VALUES
    # ======================================

    if len(start) != 9:

        print("\nInvalid puzzle!")
        print("Please enter exactly 9 numbers.")
        return

    # ======================================
    # VALIDATE NUMBERS
    # ======================================

    if set(start) != set(range(9)):

        print("\nInvalid puzzle!")

        print(
            "Use every number from 0 to 8 exactly once."
        )

        return

    # ======================================
    # CHECK SOLVABILITY
    # ======================================

    if not is_solvable(start):

        print("\n======================================")
        print("         PUZZLE NOT SOLVABLE")
        print("======================================")

        return

    # ======================================
    # DISPLAY INITIAL STATE
    # ======================================

    print("\n======================================")
    print("           INITIAL STATE")
    print("======================================")

    print_state(start)

    # ======================================
    # RUN A* WITH MISPLACED TILES
    # ======================================

    print("Running A* with Misplaced Tiles...")

    path1, expanded1 = a_star(
        start,
        misplaced_tiles
    )

    # ======================================
    # RUN A* WITH MANHATTAN DISTANCE
    # ======================================

    print("Running A* with Manhattan Distance...")

    path2, expanded2 = a_star(
        start,
        manhattan_distance
    )

    # ======================================
    # MISPLACED TILES RESULT
    # ======================================

    print("\n======================================")
    print("       MISPLACED TILES HEURISTIC")
    print("======================================")

    print(
        "Solution Cost:",
        len(path1) - 1
    )

    print(
        "Nodes Expanded:",
        expanded1
    )

    print("\nSolution Path:")

    for i, state in enumerate(path1):

        print("Step", i)

        print_state(state)

    # ======================================
    # MANHATTAN DISTANCE RESULT
    # ======================================

    print("======================================")
    print("      MANHATTAN DISTANCE HEURISTIC")
    print("======================================")

    print(
        "Solution Cost:",
        len(path2) - 1
    )

    print(
        "Nodes Expanded:",
        expanded2
    )

    print("\nSolution Path:")

    for i, state in enumerate(path2):

        print("Step", i)

        print_state(state)

    # ======================================
    # HEURISTIC COMPARISON
    # ======================================

    print("======================================")
    print("          HEURISTIC COMPARISON")
    print("======================================")

    print()

    print(
        "Misplaced Tiles :",
        expanded1,
        "nodes expanded"
    )

    print(
        "Manhattan       :",
        expanded2,
        "nodes expanded"
    )

    # ======================================
    # COMPARE NODES
    # ======================================

    print()

    if expanded2 < expanded1:

        reduction = (
            (expanded1 - expanded2)
            / expanded1
        ) * 100

        print(
            "Manhattan Distance expanded fewer nodes."
        )

        print(
            "Node reduction: {:.2f}%".format(
                reduction
            )
        )

    elif expanded1 < expanded2:

        reduction = (
            (expanded2 - expanded1)
            / expanded2
        ) * 100

        print(
            "Misplaced Tiles expanded fewer nodes."
        )

        print(
            "Node reduction: {:.2f}%".format(
                reduction
            )
        )

    else:

        print(
            "Both heuristics expanded the same number of nodes."
        )

    # ======================================
    # FINAL CONCLUSION
    # ======================================

    print()
    print("======================================")
    print("             CONCLUSION")
    print("======================================")

    print(
        "Both heuristics are admissible."
    )

    print(
        "Both produce an optimal solution."
    )

    print(
        "Manhattan Distance is more informed"
    )

    print(
        "because it considers the distance"
    )

    print(
        "of each tile from its goal position."
    )


# ==========================================
# START PROGRAM
# ==========================================

if __name__ == "__main__":
    main()