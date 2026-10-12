"""
Sudoku Constraint Satisfaction Problem (CSP) Formulation
---------------------------------------------------------
This module models 4x4 and 9x9 Sudoku puzzles as Constraint Satisfaction
Problems (CSPs) defined by:

1. Variables:
   Each cell (r, c) on an N x N grid is a variable X_{r, c}.
   - For 4x4: 16 variables, organized in 2x2 subgrids.
   - For 9x9: 81 variables, organized in 3x3 subgrids.

2. Domains:
   For an unassigned cell (0), the domain is D_{r, c} = {1, 2, ..., N}.
   For a pre-filled clue d in {1, ..., N}, D_{r, c} = {d}.

3. Constraints:
   All-Different constraints across:
   - Rows:    X_{r, c1} != X_{r, c2} for all c1 != c2
   - Columns: X_{r1, c} != X_{r2, c} for all r1 != r2
   - Subgrids: Cells within the same box must all be distinct.
   Represented as a set of binary inequality constraints between peers.

4. AC-3 (Arc Consistency Algorithm 3):
   Enforces arc consistency across directed arcs (Xi, Xj) in the constraint
   graph where Xj is a peer of Xi.
"""

from collections import deque
import copy


def get_subgrid_dimensions(size):
    """Return (box_rows, box_cols) for a given board size (4 or 9)."""
    if size == 4:
        return 2, 2
    elif size == 9:
        return 3, 3
    else:
        raise ValueError(f"Unsupported Sudoku size: {size}. Only 4 and 9 are supported.")


def compute_peers(size):
    """
    Precompute the set of peers (row, column, and subgrid neighbors)
    for every cell (r, c) on an N x N board.
    Returns a dictionary mapping (r, c) -> set of (r', c') peers.
    """
    box_r, box_c = get_subgrid_dimensions(size)
    peers = {}

    for r in range(size):
        for c in range(size):
            p_set = set()
            # Row peers
            for other_c in range(size):
                if other_c != c:
                    p_set.add((r, other_c))
            # Column peers
            for other_r in range(size):
                if other_r != r:
                    p_set.add((other_r, c))
            # Subgrid peers
            start_r = (r // box_r) * box_r
            start_c = (c // box_c) * box_c
            for br in range(start_r, start_r + box_r):
                for bc in range(start_c, start_c + box_c):
                    if (br, bc) != (r, c):
                        p_set.add((br, bc))
            peers[(r, c)] = p_set

    return peers


class SudokuCSP:
    """
    Represents a Sudoku puzzle as a Constraint Satisfaction Problem.
    """

    def __init__(self, initial_board):
        """
        Initialize the CSP with an N x N initial board (list of lists of ints).
        0 represents an unassigned cell.
        """
        self.size = len(initial_board)
        if self.size not in (4, 9):
            raise ValueError(f"Invalid Sudoku size: {self.size}. Expected 4 or 9.")

        self.box_rows, self.box_cols = get_subgrid_dimensions(self.size)
        self.variables = [(r, c) for r in range(self.size) for c in range(self.size)]
        self.peers = compute_peers(self.size)

        # Validate board structure and initial clue constraints
        validate_board(initial_board, self.size)

        # Deep copy initial board to preserve clues
        self.initial_board = [list(row) for row in initial_board]

        # Initialize domains
        self.domains = {}
        for r, c in self.variables:
            val = initial_board[r][c]
            if val != 0:
                self.domains[(r, c)] = {val}
            else:
                self.domains[(r, c)] = set(range(1, self.size + 1))

        # Initial domain pruning from fixed clues
        self.prune_initial_clues()

    def prune_initial_clues(self):
        """
        Remove assigned clue values from the domains of their peers.
        """
        for (r, c), domain in list(self.domains.items()):
            if len(domain) == 1:
                val = next(iter(domain))
                for peer in self.peers[(r, c)]:
                    if val in self.domains[peer] and len(self.domains[peer]) > 1:
                        self.domains[peer].remove(val)
                    elif val in self.domains[peer] and len(self.domains[peer]) == 1 and peer != (r, c):
                        # Duplicate clue contradiction
                        raise ValueError(f"Contradictory clues detected between ({r},{c}) and {peer} with value {val}.")


def validate_board(board, expected_size=None):
    """
    Validate board structure, dimension, number ranges, and ensure no
    pre-existing duplicate clues exist in any row, column, or subgrid.
    """
    if not isinstance(board, list) or len(board) == 0:
        raise ValueError("Sudoku board must be a non-empty list of lists.")

    size = len(board)
    if expected_size is not None and size != expected_size:
        raise ValueError(f"Expected board size {expected_size}x{expected_size}, got {size}x{size}.")

    if size not in (4, 9):
        raise ValueError(f"Unsupported Sudoku size: {size}. Only 4 and 9 are supported.")

    box_r, box_c = get_subgrid_dimensions(size)

    for r_idx, row in enumerate(board):
        if not isinstance(row, list) or len(row) != size:
            raise ValueError(f"Row {r_idx} must have exactly {size} elements.")
        for c_idx, val in enumerate(row):
            if not isinstance(val, int) or val < 0 or val > size:
                raise ValueError(
                    f"Cell ({r_idx}, {c_idx}) has invalid value '{val}'. "
                    f"Values must be integers between 0 and {size}."
                )

    # Check for duplicate clues in rows
    for r in range(size):
        seen = set()
        for c in range(size):
            val = board[r][c]
            if val != 0:
                if val in seen:
                    raise ValueError(f"Duplicate clue {val} in row {r + 1}.")
                seen.add(val)

    # Check for duplicate clues in columns
    for c in range(size):
        seen = set()
        for r in range(size):
            val = board[r][c]
            if val != 0:
                if val in seen:
                    raise ValueError(f"Duplicate clue {val} in column {c + 1}.")
                seen.add(val)

    # Check for duplicate clues in subgrids
    for br in range(0, size, box_r):
        for bc in range(0, size, box_c):
            seen = set()
            for r in range(br, br + box_r):
                for c in range(bc, bc + box_c):
                    val = board[r][c]
                    if val != 0:
                        if val in seen:
                            raise ValueError(f"Duplicate clue {val} in subgrid starting at ({br+1}, {bc+1}).")
                        seen.add(val)

    return True


def is_valid_assignment(board, r, c, val, size=None):
    """
    Check if assigning 'val' at board[r][c] satisfies row, column,
    and subgrid constraints.
    """
    if size is None:
        size = len(board)
    box_r, box_c = get_subgrid_dimensions(size)

    # Check row
    for other_c in range(size):
        if other_c != c and board[r][other_c] == val:
            return False

    # Check column
    for other_r in range(size):
        if other_r != r and board[other_r][c] == val:
            return False

    # Check subgrid
    start_r = (r // box_r) * box_r
    start_c = (c // box_c) * box_c
    for br in range(start_r, start_r + box_r):
        for bc in range(start_c, start_c + box_c):
            if (br, bc) != (r, c) and board[br][bc] == val:
                return False

    return True


def is_board_solved(board, size=None):
    """
    Verify that the entire board is filled (no 0s) and strictly satisfies
    all row, column, and subgrid constraints.
    """
    if size is None:
        size = len(board)

    # Validate structure first
    try:
        validate_board(board, size)
    except ValueError:
        return False

    digits = set(range(1, size + 1))
    box_r, box_c = get_subgrid_dimensions(size)

    # Check all rows
    for r in range(size):
        if set(board[r]) != digits:
            return False

    # Check all columns
    for c in range(size):
        col_vals = {board[r][c] for r in range(size)}
        if col_vals != digits:
            return False

    # Check all subgrids
    for br in range(0, size, box_r):
        for bc in range(0, size, box_c):
            subgrid_vals = {
                board[r][c]
                for r in range(br, br + box_r)
                for c in range(bc, bc + box_c)
            }
            if subgrid_vals != digits:
                return False

    return True


def format_sudoku_board(board):
    """
    Return an aesthetically formatted string representation of a 4x4 or 9x9 board
    with visual subgrid separators.
    """
    size = len(board)
    box_r, box_c = get_subgrid_dimensions(size)
    lines = []

    h_border = "+" + "+".join(["-" * (box_c * 2 + 1)] * (size // box_c)) + "+"

    for r in range(size):
        if r % box_r == 0:
            lines.append(h_border)
        row_str = "| "
        for c in range(size):
            val = board[r][c]
            char = str(val) if val != 0 else "."
            row_str += char + " "
            if (c + 1) % box_c == 0:
                row_str += "| "
        lines.append(row_str)
    lines.append(h_border)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# AC-3 (Arc Consistency Algorithm 3)
# ---------------------------------------------------------------------------

def revise(domains, xi, xj):
    """
    REVISE(Xi, Xj) for binary inequality constraint (Xi != Xj):
    Removes any value x in Domain(Xi) for which there is no value y in Domain(Xj)
    such that x != y.
    In binary inequality, this condition occurs if and only if Domain(Xj) == {x}.
    Returns (revised, pruned_values).
    """
    revised = False
    pruned = []

    # If Xj has a single allowed value {y}, Xi cannot take value y.
    if len(domains[xj]) == 1:
        single_val = next(iter(domains[xj]))
        if single_val in domains[xi]:
            domains[xi].remove(single_val)
            pruned.append((xi, single_val))
            revised = True

    return revised, pruned


def ac3(domains, peers, initial_queue=None):
    """
    Run AC-3 on the given domains.
    If initial_queue is None, queue is initialized with all arcs (Xi, Xj)
    where Xj is in peers[Xi].

    Returns (is_consistent, total_pruned_list)
    - is_consistent: False if any domain is wiped out (empty), True otherwise.
    - total_pruned_list: List of (variable, removed_value) for undo/tracking.
    """
    if initial_queue is None:
        queue = deque()
        for xi in domains:
            for xj in peers[xi]:
                queue.append((xi, xj))
    else:
        queue = deque(initial_queue)

    total_pruned = []

    while queue:
        xi, xj = queue.popleft()
        revised, pruned = revise(domains, xi, xj)
        if revised:
            total_pruned.extend(pruned)
            if len(domains[xi]) == 0:
                # Domain wipeout detected
                return False, total_pruned

            # Re-add all arcs (Xk, Xi) for peers Xk of Xi (where Xk != Xj)
            for xk in peers[xi]:
                if xk != xj:
                    queue.append((xk, xi))

    return True, total_pruned
