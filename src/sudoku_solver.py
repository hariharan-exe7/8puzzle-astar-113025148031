"""
Sudoku CSP Solvers
------------------
Implements four CSP solving variants for 4x4 and 9x9 Sudoku:

1. Plain Backtracking:
   - Fixed row-major variable selection.
   - Ascending value ordering (1..N).
   - Direct row, column, and subgrid constraint checking.
   - Baseline algorithm (no MRV, forward checking, or AC-3).

2. Backtracking + MRV (Minimum Remaining Values):
   - Chooses unassigned cell with the fewest legal candidate values.
   - "Fail-first" heuristic: shrinks branching factor and triggers failure
     early before deep exploration.
   - Deterministic tie-breaking (row-major).
   - No forward checking or AC-3.

3. Backtracking + MRV + Forward Checking:
   - MRV variable selection.
   - Immediately prunes assigned values from domains of unassigned peers.
   - Early detection of domain wipeouts (empty domain -> immediate backtrack).
   - Accurate, undo-based domain restoration on backtracking.

4. Backtracking + MRV + Forward Checking + AC-3:
   - Initial constraint propagation using AC-3 before search begins.
   - AC-3 preprocessing time included in total runtime.
   - Maintaining Arc Consistency (MAC) during search after assignments.
   - Rigorous REVISE(Xi, Xj) and arc queue propagation.
"""

from collections import deque
import copy
import time

try:
    from sudoku_csp import (
        SudokuCSP,
        compute_peers,
        format_sudoku_board,
        get_subgrid_dimensions,
        is_board_solved,
        is_valid_assignment,
        validate_board,
    )
except ImportError:
    from src.sudoku_csp import (
        SudokuCSP,
        compute_peers,
        format_sudoku_board,
        get_subgrid_dimensions,
        is_board_solved,
        is_valid_assignment,
        validate_board,
    )


class SudokuResult:
    """Standardized result container for Sudoku solver executions."""

    def __init__(self, method_name, is_solved, solved_board, assignments, backtracks, runtime_ms, size):
        self.method_name = method_name
        self.is_solved = is_solved
        self.solved_board = solved_board
        self.assignments = assignments
        self.backtracks = backtracks
        self.runtime_ms = runtime_ms
        self.size = size

    def __repr__(self):
        return (
            f"<SudokuResult method='{self.method_name}' solved={self.is_solved} "
            f"assignments={self.assignments} backtracks={self.backtracks} "
            f"runtime={self.runtime_ms:.3f}ms>"
        )


# ===========================================================================
# Variant 1: Plain Backtracking
# ===========================================================================

def solve_plain_backtracking(initial_board):
    """
    Solve Sudoku using baseline recursive backtracking:
    - Fixed row-major variable selection.
    - Ascending value trial (1..N).
    - Direct constraint verification.
    """
    size = len(initial_board)
    validate_board(initial_board, size)
    board = [list(row) for row in initial_board]

    assignments = 0
    backtracks = 0

    def find_empty_cell():
        for r in range(size):
            for c in range(size):
                if board[r][c] == 0:
                    return r, c
        return None

    def backtrack():
        nonlocal assignments, backtracks
        empty_pos = find_empty_cell()
        if empty_pos is None:
            return True  # All variables assigned

        r, c = empty_pos
        for val in range(1, size + 1):
            if is_valid_assignment(board, r, c, val, size):
                board[r][c] = val
                assignments += 1

                if backtrack():
                    return True

                board[r][c] = 0
                backtracks += 1

        return False

    start_time = time.perf_counter()
    solved = backtrack()
    runtime_ms = (time.perf_counter() - start_time) * 1000.0

    return SudokuResult(
        method_name="Plain Backtracking",
        is_solved=solved and is_board_solved(board, size),
        solved_board=board if solved else None,
        assignments=assignments,
        backtracks=backtracks,
        runtime_ms=runtime_ms,
        size=size,
    )


# ===========================================================================
# Variant 2: Backtracking + MRV
# ===========================================================================

def solve_mrv(initial_board):
    """
    Solve Sudoku using Backtracking with Minimum Remaining Values (MRV):
    - Among unassigned cells, select the cell with the fewest legal values.
    - Deterministic tie-breaker: row-major order.
    - Legal values evaluated on-demand without forward checking or AC-3.
    """
    size = len(initial_board)
    validate_board(initial_board, size)
    board = [list(row) for row in initial_board]

    assignments = 0
    backtracks = 0

    def get_legal_values(r, c):
        return [val for val in range(1, size + 1) if is_valid_assignment(board, r, c, val, size)]

    def select_mrv_variable():
        best_pos = None
        min_domain_len = float("inf")
        best_legal = None

        for r in range(size):
            for c in range(size):
                if board[r][c] == 0:
                    legal = get_legal_values(r, c)
                    legal_count = len(legal)
                    if legal_count < min_domain_len:
                        min_domain_len = legal_count
                        best_pos = (r, c)
                        best_legal = legal
                        if min_domain_len == 0:
                            # Immediate dead-end detected (fail-first)
                            return best_pos, best_legal

        return best_pos, best_legal

    def backtrack():
        nonlocal assignments, backtracks
        var, legal_values = select_mrv_variable()
        if var is None:
            return True  # Solved

        if len(legal_values) == 0:
            return False  # Dead-end, backtrack immediately

        r, c = var
        for val in legal_values:
            board[r][c] = val
            assignments += 1

            if backtrack():
                return True

            board[r][c] = 0
            backtracks += 1

        return False

    start_time = time.perf_counter()
    solved = backtrack()
    runtime_ms = (time.perf_counter() - start_time) * 1000.0

    return SudokuResult(
        method_name="Backtracking + MRV",
        is_solved=solved and is_board_solved(board, size),
        solved_board=board if solved else None,
        assignments=assignments,
        backtracks=backtracks,
        runtime_ms=runtime_ms,
        size=size,
    )


# ===========================================================================
# Variant 3: Backtracking + MRV + Forward Checking
# ===========================================================================

def solve_forward_checking(initial_board):
    """
    Solve Sudoku using Backtracking + MRV + Forward Checking:
    - Maintains explicit domain sets for all cells.
    - Prunes assigned values from unassigned peers immediately.
    - Fails instantly upon any domain wipeout.
    - Restores pruned domains accurately using an undo list on backtrack.
    """
    size = len(initial_board)
    validate_board(initial_board, size)
    try:
        csp = SudokuCSP(initial_board)
    except ValueError:
        return SudokuResult(
            method_name="Backtracking + MRV + FC",
            is_solved=False,
            solved_board=None,
            assignments=0,
            backtracks=0,
            runtime_ms=0.0,
            size=size,
        )

    board = [list(row) for row in initial_board]
    domains = {var: set(csp.domains[var]) for var in csp.variables}
    peers = csp.peers

    assignments = 0
    backtracks = 0

    def select_mrv_unassigned():
        best_var = None
        min_domain_size = float("inf")

        for r in range(size):
            for c in range(size):
                if board[r][c] == 0:
                    d_size = len(domains[(r, c)])
                    if d_size < min_domain_size:
                        min_domain_size = d_size
                        best_var = (r, c)
                        if min_domain_size == 0:
                            return best_var

        return best_var

    def backtrack():
        nonlocal assignments, backtracks
        var = select_mrv_unassigned()
        if var is None:
            return True

        r, c = var
        if len(domains[var]) == 0:
            return False

        # Try values in sorted ascending order
        for val in sorted(domains[var]):
            board[r][c] = val
            assignments += 1

            # Prune value from unassigned peers (Forward Checking)
            pruned = []
            wipeout = False

            for peer in peers[var]:
                pr, pc = peer
                if board[pr][pc] == 0 and val in domains[peer]:
                    domains[peer].remove(val)
                    pruned.append((peer, val))
                    if len(domains[peer]) == 0:
                        wipeout = True
                        break

            if not wipeout:
                if backtrack():
                    return True

            # Undo forward checking pruning
            for peer, p_val in pruned:
                domains[peer].add(p_val)

            board[r][c] = 0
            backtracks += 1

        return False

    start_time = time.perf_counter()
    solved = backtrack()
    runtime_ms = (time.perf_counter() - start_time) * 1000.0

    return SudokuResult(
        method_name="Backtracking + MRV + FC",
        is_solved=solved and is_board_solved(board, size),
        solved_board=board if solved else None,
        assignments=assignments,
        backtracks=backtracks,
        runtime_ms=runtime_ms,
        size=size,
    )


# ===========================================================================
# Variant 4: Backtracking + MRV + Forward Checking + AC-3
# ===========================================================================

def solve_ac3(initial_board):
    """
    Solve Sudoku using Backtracking + MRV + Forward Checking + AC-3:
    - Preprocessing with AC-3 across the entire initial constraint graph.
    - Preprocessing time included in total runtime measurement.
    - Maintaining Arc Consistency (MAC) during search.
    - Rigorous arc queue revision and domain undo restoration.
    """
    size = len(initial_board)
    validate_board(initial_board, size)

    start_time = time.perf_counter()

    try:
        csp = SudokuCSP(initial_board)
    except ValueError:
        runtime_ms = (time.perf_counter() - start_time) * 1000.0
        return SudokuResult(
            method_name="Backtracking + MRV + FC + AC-3",
            is_solved=False,
            solved_board=None,
            assignments=0,
            backtracks=0,
            runtime_ms=runtime_ms,
            size=size,
        )

    board = [list(row) for row in initial_board]
    domains = {var: set(csp.domains[var]) for var in csp.variables}
    peers = csp.peers

    assignments = 0
    backtracks = 0

    # AC-3 Preprocessing step
    arc_queue = deque()
    for xi in csp.variables:
        for xj in peers[xi]:
            arc_queue.append((xi, xj))

    preprocessing_ok = True
    while arc_queue:
        xi, xj = arc_queue.popleft()
        if len(domains[xj]) == 1:
            val = next(iter(domains[xj]))
            if val in domains[xi]:
                domains[xi].remove(val)
                if len(domains[xi]) == 0:
                    preprocessing_ok = False
                    break
                for xk in peers[xi]:
                    if xk != xj:
                        arc_queue.append((xk, xi))

    if not preprocessing_ok:
        runtime_ms = (time.perf_counter() - start_time) * 1000.0
        return SudokuResult(
            method_name="Backtracking + MRV + FC + AC-3",
            is_solved=False,
            solved_board=None,
            assignments=0,
            backtracks=0,
            runtime_ms=runtime_ms,
            size=size,
        )

    # Fill any cells that were solved purely by initial AC-3 preprocessing
    for r in range(size):
        for c in range(size):
            if board[r][c] == 0 and len(domains[(r, c)]) == 1:
                # Value uniquely determined by arc consistency
                val = next(iter(domains[(r, c)]))
                if is_valid_assignment(board, r, c, val, size):
                    board[r][c] = val

    if is_board_solved(board, size):
        runtime_ms = (time.perf_counter() - start_time) * 1000.0
        return SudokuResult(
            method_name="Backtracking + MRV + FC + AC-3",
            is_solved=True,
            solved_board=board,
            assignments=assignments,
            backtracks=backtracks,
            runtime_ms=runtime_ms,
            size=size,
        )

    def select_mrv_unassigned():
        best_var = None
        min_domain_size = float("inf")

        for r in range(size):
            for c in range(size):
                if board[r][c] == 0:
                    d_size = len(domains[(r, c)])
                    if d_size < min_domain_size:
                        min_domain_size = d_size
                        best_var = (r, c)
                        if min_domain_size == 0:
                            return best_var

        return best_var

    def maintain_arc_consistency(assigned_var, assigned_val):
        """
        Propagate arc consistency starting from the peers of assigned_var.
        Returns (is_consistent, pruned_list).
        """
        pruned = []
        q = deque()

        # Initial arcs from unassigned peers to assigned_var
        for peer in peers[assigned_var]:
            pr, pc = peer
            if board[pr][pc] == 0 and assigned_val in domains[peer]:
                domains[peer].remove(assigned_val)
                pruned.append((peer, assigned_val))
                if len(domains[peer]) == 0:
                    return False, pruned
                # If peer domain shrank to 1, propagate forward
                if len(domains[peer]) == 1:
                    for neighbor in peers[peer]:
                        nr, nc = neighbor
                        if board[nr][nc] == 0 and neighbor != assigned_var:
                            q.append((neighbor, peer))

        while q:
            xi, xj = q.popleft()
            if len(domains[xj]) == 1:
                y = next(iter(domains[xj]))
                if y in domains[xi]:
                    domains[xi].remove(y)
                    pruned.append((xi, y))
                    if len(domains[xi]) == 0:
                        return False, pruned
                    if len(domains[xi]) == 1:
                        for xk in peers[xi]:
                            kr, kc = xk
                            if board[kr][kc] == 0 and xk != xj:
                                q.append((xk, xi))

        return True, pruned

    def backtrack():
        nonlocal assignments, backtracks
        var = select_mrv_unassigned()
        if var is None:
            return True

        r, c = var
        if len(domains[var]) == 0:
            return False

        for val in sorted(domains[var]):
            board[r][c] = val
            assignments += 1

            consistent, pruned = maintain_arc_consistency(var, val)

            if consistent:
                if backtrack():
                    return True

            # Undo all prunings performed by MAC
            for cell, p_val in reversed(pruned):
                domains[cell].add(p_val)

            board[r][c] = 0
            backtracks += 1

        return False

    solved = backtrack()
    runtime_ms = (time.perf_counter() - start_time) * 1000.0

    return SudokuResult(
        method_name="Backtracking + MRV + FC + AC-3",
        is_solved=solved and is_board_solved(board, size),
        solved_board=board if solved else None,
        assignments=assignments,
        backtracks=backtracks,
        runtime_ms=runtime_ms,
        size=size,
    )


# ===========================================================================
# Unified Solver Dispatcher
# ===========================================================================

SUDOKU_SOLVERS = {
    "plain": solve_plain_backtracking,
    "mrv": solve_mrv,
    "fc": solve_forward_checking,
    "ac3": solve_ac3,
}


def solve_sudoku(board, method="ac3"):
    """
    Unified entry point to solve a Sudoku board using one of the 4 methods:
    'plain', 'mrv', 'fc', 'ac3'.
    """
    if method not in SUDOKU_SOLVERS:
        raise ValueError(f"Unknown method '{method}'. Supported: {list(SUDOKU_SOLVERS.keys())}")
    return SUDOKU_SOLVERS[method](board)
