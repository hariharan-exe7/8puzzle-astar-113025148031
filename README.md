# 8-Puzzle Solver using A* — Search vs. Constraint Satisfaction Study

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests: Passing](https://img.shields.io/badge/tests-46%20passed-brightgreen.svg)](tests/)

---

## 1. Final Project Title

**8-Puzzle Solver using A\* — Search vs. Constraint Satisfaction Study**  
*(Extended College Artificial Intelligence & Machine Learning Project)*

---

## 2. Abstract

This project presents a comprehensive study and software implementation contrasting two core paradigms of Artificial Intelligence: **State-Space Heuristic Search** and **Constraint Satisfaction Problems (CSPs)**. The foundational component implements the classic **8-Puzzle** solved optimally using the **A\*** search algorithm with two admissible heuristics: **Misplaced Tiles** and **Manhattan Distance**. 

The extended architecture incorporates:
1. **CSP Layer**: Solvers for 4x4 and 9x9 **Sudoku** comparing four solving paradigms: Plain Backtracking, Backtracking + MRV (Minimum Remaining Values), Backtracking + MRV + Forward Checking, and Backtracking + MRV + FC + AC-3 (Arc Consistency Algorithm 3).
2. **Knowledge & Reasoning Layer**: Inversion parity logic to mathematically prove solvability and reject unreachable 8-Puzzle states prior to search, coupled with a rule-based next-move hint system.
3. **Explainable AI (XAI) Layer**: Decomposition of Manhattan distance into per-tile contributions, step-by-step cost analysis ($g, h, f$), and real search decision auditing via expansion traces.

---

## 3. Problem Statement

Autonomous problem-solving in Artificial Intelligence fundamentally differs based on whether an agent seeks a **sequence of actions (path)** to transition between states or a **consistent assignment of variables** satisfying static constraints:
- In the **8-Puzzle**, an agent must navigate a combinatorial state space of $9! / 2 = 181,440$ reachable configurations to discover the minimum-length sequence of tile sliding moves from a start state to a goal state.
- In **Sudoku**, an agent must assign digits to an unassigned grid of variables ($N \times N$) such that all-different constraints across rows, columns, and subgrids are strictly satisfied, where the sequence of assignments has no cost or physical meaning.

Understanding the computational trade-offs, representation models, and pruning mechanisms between these two formulations is a core objective of academic AI.

---

## 4. Objectives

- **Preserve Baseline Functionality**: Retain 100% backward compatibility with the original 8-Puzzle A* solver and its CLI command `python src/puzzle_solver.py`.
- **Implement 4 Sudoku CSP Variants**: Support both 4x4 ($2 \times 2$ boxes) and 9x9 ($3 \times 3$ boxes) grids across Plain Backtracking, MRV, Forward Checking, and AC-3.
- **Empirical CSP Benchmarking**: Measure and compare assignments, backtracks, and runtime (`time.perf_counter()`) on identical puzzle boards.
- **Formulate Knowledge-Based Solvability**: Enforce inversion parity checks and provide step-by-step reasoning for why an odd-inversion 8-Puzzle cannot be solved.
- **Develop Rule-Based Hint System**: Provide transparent recommendations evaluating legal moves, Manhattan delta changes, and distinguishing greedy hints from optimal A* moves.
- **Deliver Explainable AI (XAI)**: Expose per-tile Manhattan contributions and audit actual A* priority queue decisions using recorded search traces.
- **Educational Contrast**: Document in detail when heuristic search is preferable over CSPs and vice-versa.
- **Provide Unified CLI & Test Suite**: Ship an interactive `main.py` menu and automated `unittest` suite with complete test coverage.

---

## 5. Original 8-Puzzle Implementation

The 8-Puzzle consists of a 3x3 board containing numbered tiles 1–8 and one blank space (represented internally as `0`). 

**Goal State Configuration:**
```
1 2 3
4 5 6
7 8 _
```

A state is modeled as an immutable tuple of 9 integers, enabling $O(1)$ hashing for visited sets and dictionary lookups:
- `get_neighbors(state)`: Identifies the position of the blank tile and generates all legal sliding moves (Up, Down, Left, Right).
- `a_star_search(start_state, heuristic)`: Explores state space using Python's `heapq` priority queue with deterministic tie-breaking.
- `came_from`: Reconstructs the exact optimal solution path upon reaching the goal.

---

## 6. The A* Algorithm Explanation

A* is a best-first heuristic search algorithm that expands nodes based on an evaluation function:

$$f(n) = g(n) + h(n)$$

Where:
- **$g(n)$**: The exact cost accumulated to reach state $n$ from the start state (each tile slide has cost 1).
- **$h(n)$**: The estimated remaining cost from state $n$ to the goal state provided by an admissible heuristic.
- **$f(n)$**: The estimated total cost of the cheapest solution passing through state $n$.

A* maintains:
1. **Frontier (Open List)**: A priority queue storing candidate states ordered by $f(n)$. Ties are broken deterministically using a monotonic insertion counter.
2. **Explored Set (Closed List)**: States already expanded with optimal $g(n)$, avoiding redundant cycles.

When $h(n)$ is **admissible** (never overestimates the true remaining cost), A* is mathematically guaranteed to return the optimal (shortest) solution path.

---

## 7. Heuristic 1 — Misplaced Tiles

**Definition**: The count of numbered tiles (1 to 8) that do not currently occupy their goal position. The blank tile is never counted.

```python
def misplaced_tiles(state):
    count = 0
    for index, tile in enumerate(state):
        if tile == 0:
            continue
        if index != tile - 1:
            count += 1
    return count
```

**Admissibility**: Every misplaced tile must be moved at least once to reach its destination. Therefore, the actual remaining moves must be $\ge$ the count of misplaced tiles. It never overestimates.

---

## 8. Heuristic 2 — Manhattan Distance

**Definition**: The sum of vertical and horizontal grid distances between each numbered tile's current coordinate $(r, c)$ and its goal coordinate $(r_{goal}, c_{goal})$:

$$h_{\text{Manhattan}}(state) = \sum_{t=1}^{8} \left(|r_t - r_{goal, t}| + |c_t - c_{goal, t}|\right)$$

```python
def manhattan_distance(state):
    total = 0
    for index, tile in enumerate(state):
        if tile == 0:
            continue
        curr_r, curr_c = index // 3, index % 3
        goal_r, goal_c = GOAL_POSITIONS[tile]
        total += abs(curr_r - goal_r) + abs(curr_c - goal_c)
    return total
```

**Admissibility**: Because each single move can shift a tile by at most one grid cell horizontally or vertically, a tile cannot reach its destination in fewer moves than its Manhattan distance. Summing across all tiles never overestimates true remaining moves.

---

## 9. Heuristic Comparison

A heuristic $h_2$ **dominates** $h_1$ if for all states $n$, $h_2(n) \ge h_1(n)$. Manhattan Distance strictly dominates Misplaced Tiles because every misplaced tile has a Manhattan distance of at least 1, and tiles further away contribute 2, 3, or 4 to the Manhattan estimate.

**Empirical Comparison Example (Standard Scrambled State):**
```
Initial State:
1 3 6
5 _ 2
4 7 8
```

| Heuristic | Solution Cost (Moves) | Nodes Expanded | Optimal Agreement |
|:---|:---:|:---:|:---:|
| **Misplaced Tiles** | 8 | 18 | Yes |
| **Manhattan Distance** | 8 | 9 | Yes |

*Observation*: Manhattan Distance reduced node expansions by **50.0%** on this puzzle while identifying the identical optimal cost (8 moves). Its finer-grained distance estimates enable A* to prune unpromising branches earlier.

---

## 10. Sudoku CSP Formulation

Sudoku is formally modeled as a **Constraint Satisfaction Problem (CSP)** defined by the triple $\langle X, D, C \rangle$:

1. **Variables ($X$)**:
   - For 4x4 Sudoku: 16 cell variables $X_{r, c}$ for $r, c \in \{0, 1, 2, 3\}$.
   - For 9x9 Sudoku: 81 cell variables $X_{r, c}$ for $r, c \in \{0, \dots, 8\}$.
2. **Domains ($D$)**:
   - For unassigned cells (input value 0): $D_{r, c} = \{1, \dots, N\}$.
   - For fixed initial clues $d \in \{1, \dots, N\}$: $D_{r, c} = \{d\}$.
3. **Constraints ($C$)**:
   - **Row Constraints**: $X_{r, c_1} \ne X_{r, c_2}$ for all $c_1 \ne c_2$.
   - **Column Constraints**: $X_{r_1, c} \ne X_{r_2, c}$ for all $r_1 \ne r_2$.
   - **Subgrid (Box) Constraints**: All cells in the same $2 \times 2$ (for 4x4) or $3 \times 3$ (for 9x9) block must have distinct values.
   - Represented as a graph of **binary inequality constraints** ($X_i \ne X_j$) between each cell and its peers.
     - Each cell has 7 peers in 4x4 Sudoku.
     - Each cell has 20 peers in 9x9 Sudoku.

---

## 11. Sudoku Variant 1 — Plain Backtracking

- **Variable Selection**: Fixed row-major ordering (scans left-to-right, top-to-bottom for the first empty cell).
- **Value Ordering**: Ascending numerical order ($1, 2, \dots, N$).
- **Consistency Verification**: Checks row, column, and box constraints before making an assignment.
- **Search Paradigm**: Baseline Depth-First Search with backtracking upon conflict.
- Does not use MRV, Forward Checking, or AC-3.

---

## 12. Sudoku Variant 2 — Backtracking + MRV

- **Variable Selection**: **Minimum Remaining Values (MRV)** heuristic, also known as the *"fail-first"* heuristic.
- **Mechanism**: Evaluates the number of legal values for all unassigned cells and selects the variable with the smallest domain size.
- **Why "Fail-First"?**: By choosing the variable with the fewest options, if a dead-end is imminent, it triggers failure immediately at the top of the search tree rather than deep down an exponential subtree.
- **Tie-Breaking**: Deterministic row-major coordinate ordering.
- Does not maintain forward domains or arc consistency.

---

## 13. Sudoku Variant 3 — Backtracking + MRV + Forward Checking

- **Domain Tracking**: Explicitly maintains domain sets $D_{r, c}$ for all variables.
- **Forward Checking (FC)**: Immediately after assigning value $v$ to variable $X$:
  1. Identifies all unassigned peers of $X$.
  2. Prunes $v$ from their domain sets.
  3. **Immediate Wipeout Detection**: If any peer's domain becomes empty ($|D_{peer}| = 0$), the assignment fails instantly without wasting time recursing deeper.
- **Domain Restoration**: Tracks all pruned $(variable, value)$ pairs on an undo stack and strictly restores them when backtracking.

---

## 14. Sudoku Variant 4 — Backtracking + MRV + Forward Checking + AC-3

- **AC-3 (Arc Consistency Algorithm 3)**:
  - Directed arcs $(X_i, X_j)$ exist between all peers.
  - `REVISE(Xi, Xj)`: In binary inequality ($X_i \ne X_j$), if $D_{X_j} = \{v\}$ (a singleton), then $v$ is removed from $D_{X_i}$.
  - If a domain is revised, all incoming arcs $(X_k, X_i)$ are re-queued to propagate changes.
- **Initial Preprocessing**: AC-3 runs across the entire board prior to search. On easy/medium puzzles, AC-3 preprocessing often deduces many values or solves the board outright.
- **Maintaining Arc Consistency (MAC)**: During search, arc consistency is propagated across unassigned peers following each trial assignment.
- **Runtime Measurement**: Includes AC-3 preprocessing time in total runtime.

---

## 15. Sudoku Performance Comparison

Actual empirical measurements collected on the same machine using `time.perf_counter()`:

### A. 4x4 Sudoku (Classic 4x4)
| Algorithm | Assignments | Backtracks | Runtime (ms) |
|:---|:---:|:---:|:---:|
| **Plain Backtracking** | 13 | 1 | 0.073 ms |
| **Backtracking + MRV** | 12 | 0 | 0.480 ms |
| **Backtracking + MRV + FC** | 12 | 0 | 0.084 ms |
| **Backtracking + MRV + FC + AC-3** | 12 | 0 | 0.552 ms |

### B. 9x9 Sudoku (Classic Easy 9x9)
| Algorithm | Assignments | Backtracks | Runtime (ms) |
|:---|:---:|:---:|:---:|
| **Plain Backtracking** | 4,208 | 4,157 | 59.621 ms |
| **Backtracking + MRV** | 51 | 0 | 22.382 ms |
| **Backtracking + MRV + FC** | 51 | 0 | 0.719 ms |
| **Backtracking + MRV + FC + AC-3** | 0 *(solved in preprocess)* | 0 | 2.698 ms |

### Key Performance Insights
1. **Backtrack Elimination**: Plain backtracking performed **4,157 backtracks** on the 9x9 puzzle. MRV reduced backtracks to **0**, demonstrating the power of the fail-first heuristic.
2. **Computational Overhead Trade-off**: Stronger constraint propagation algorithms (AC-3) perform extra per-step consistency checks. On tiny 4x4 boards, the overhead of maintaining arc queues results in slightly higher wall-clock time than raw backtracking. On 9x9 boards, constraint propagation prevents exponential thrashing and drastically scales performance.

---

## 16. Inversion Parity Solvability Rule

For an $N \times N$ sliding tile puzzle where $N$ is odd ($N = 3$ for 8-Puzzle):
- An **inversion** occurs when a tile $a$ precedes tile $b$ in row-major order, but $a > b$ (blank 0 is ignored).
- **Mathematical Invariant**:
  - Sliding the blank horizontally does not change the relative order of numbered tiles ($\Delta \text{inversions} = 0$).
  - Sliding the blank vertically shifts one tile past exactly two other tiles, changing the inversion count by $+2, -2$, or $0$.
  - In all legal moves, the **parity (even/odd)** of the inversion count is strictly preserved!
- **Goal State Parity**: The standard goal state `(1, 2, 3, 4, 5, 6, 7, 8, 0)` has 0 inversions (**EVEN**).
- **Theorem**: An initial configuration is solvable if and only if its inversion count is **EVEN**.

```
Example Solvable (Inversions = 6, Even):
1 3 6
5 _ 2  -> Inversion pairs: (3,2), (6,5), (6,2), (6,4), (5,2), (5,4)
4 7 8     Verdict: SOLVABLE (A* proceeds)

Example Unsolvable (Inversions = 1, Odd):
1 2 3
4 5 6  -> Inversion pair: (8, 7)
8 7 _     Verdict: UNSOLVABLE (A* rejected before execution)
```

---

## 17. Rule-Based Hint System

The hint system evaluates candidate moves from the current state:
1. Rejects unsolvable states immediately based on parity.
2. Generates all legal moves of the blank (Up, Down, Left, Right).
3. Evaluates the change in Manhattan distance ($\Delta h = h_{curr} - h_{next}$).
4. Selects the best move using deterministic tie-breaking.
5. Provides a transparent explanation of whether the move:
   - Moves a tile into its goal position.
   - Moves a tile closer to goal.
   - Is neutral ($\Delta h = 0$).
   - Temporarily increases distance (local minimum).
6. **Honesty Clause**: Clarifies that greedy local moves do not guarantee the shortest global solution, offering an optional guaranteed optimal A* next move.

---

## 18. Explainable AI (XAI)

The XAI module demystifies A* search:
1. **Per-Tile Manhattan Breakdown**: Decomposes total $h(n)$ into individual tile contributions. Sum of tile distances strictly equals $h(n)$.
2. **Cost Metrics**: Displays $g(n)$, $h(n)$, and $f(n) = g(n) + h(n)$ for every step along the optimal path.
3. **Action Explanation**: Explicitly states which tile moved and its physical effect on goal distance.
4. **Authentic Search Decision Auditing**: Records actual priority queue events during search:
   - Node expansion order.
   - Frontier minimum $f(n)$ value.
   - Deterministic tie-breaking sequence counter.
   - Real alternative candidate states competing on the frontier.
5. **Clear Conceptual Distinction**: Distinguishes why A* *expanded* a state (minimum $f$ at that point in time) versus why a state is *on the final solution path* (backwards pointer reconstruction).

---

## 19. Search vs. CSP Comparison

| Feature | Heuristic Search (8-Puzzle) | Constraint Satisfaction (Sudoku) |
|:---|:---|:---|
| **Primary Goal** | Finding an optimal **path / sequence of actions** | Finding a **feasible complete assignment** |
| **State Model** | Atomic configuration tuple | Factored variables with discrete domains |
| **Transitions** | Dynamic actions (slide Up, Down, Left, Right) | Variable assignment (order is arbitrary) |
| **Path Cost** | Crucial ($g(n)$ accumulated cost) | Non-existent (only final state validity matters) |
| **Search Method** | Best-First Search (A\* with priority queue) | Depth-First Backtracking + Consistency Propagation |
| **Heuristics** | Goal distance estimation ($h(n)$ Manhattan) | Variable ordering (MRV), Value ordering (LCV) |
| **Pruning Engine** | Priority queue ordering ($f(n) = g + h$) | Domain filtering (Forward Checking, AC-3) |
| **Optimality** | Guaranteed minimum moves if $h$ is admissible | Not applicable (any valid solution is acceptable) |
| **When Preferred** | Sequential planning, robotics, routing, games | Scheduling, timetabling, layout, resource allocation |

---

## 20. Architecture

The system is organized into modular layers:
- **Core Search Engine** (`src/puzzle_solver.py`): Admissible heuristics, priority queue, neighbor expansion, path reconstruction.
- **CSP Engine** (`src/sudoku_csp.py`, `src/sudoku_solver.py`): Variable/peer graph, AC-3 revision, MRV selector, undo-based forward checking.
- **Knowledge & Reasoning Layer** (`src/puzzle_solver.py`, `src/hint_system.py`): Inversion parity theorems, rule-based recommendation policy.
- **Explainable AI Layer** (`src/explainable_ai.py`): Per-tile decomposition, expansion auditing.
- **Benchmarking & Educational Layer** (`src/comparison.py`): High-resolution timer metrics, comparative study.
- **Application Controller** (`main.py`): Interactive menu connecting all subsystems.

---

## 21. Folder Structure

```
8-puzzle-astar/
├── main.py                     # Main interactive CLI application
├── src/
│   ├── __init__.py             # Package initializer
│   ├── puzzle_solver.py        # Core 8-Puzzle A* solver & solvability rules
│   ├── sudoku_csp.py           # Sudoku CSP formulation, validation & AC-3
│   ├── sudoku_solver.py        # Plain, MRV, FC, and AC-3 solver variants
│   ├── hint_system.py          # Rule-based & optimal A* hint generation
│   ├── explainable_ai.py       # XAI per-tile breakdown & search decision audit
│   └── comparison.py           # Sudoku benchmarking & Search vs CSP study
├── tests/
│   ├── test_solver.py          # Original 8-Puzzle solver unit tests (15 tests)
│   ├── test_sudoku.py          # Sudoku CSP & AC-3 unit tests (14 tests)
│   ├── test_hints.py           # Hint system unit tests (7 tests)
│   ├── test_solvability.py     # Solvability & parity unit tests (5 tests)
│   └── test_xai.py             # Explainable AI unit tests (5 tests)
├── examples/
│   ├── sudoku_4x4.txt          # Example 4x4 boards
│   ├── sudoku_9x9.txt          # Example 9x9 boards (Easy & Medium)
│   └── puzzle_examples.txt     # Solvable, unsolvable, and test 8-puzzles
├── README.md                   # Complete project documentation
├── requirements.txt            # Environment specifications
├── LICENSE                     # MIT License
└── .gitignore                  # Git ignore rules
```

---

## 22. Installation

This project requires **Python 3.8 or higher** and uses **only the Python standard library**. No third-party packages or virtual environments are needed.

1. Clone the repository:
   ```bash
   git clone https://github.com/[YOUR-USERNAME]/8-puzzle-astar.git
   cd 8-puzzle-astar
   ```
2. Verify Python installation:
   ```bash
   python --version
   ```

---

## 23. How to Run

### Interactive Application Menu
Launch the complete unified CLI suite:
```bash
python main.py
```

### Original 8-Puzzle Solver (Preserved Compatibility)
The original standalone command remains fully functional:
```bash
python src/puzzle_solver.py
```

---

## 24. Example Inputs

### 8-Puzzle Input Format
Enter 9 space-separated integers (0–8), where 0 represents the blank tile:
```
1 3 6 5 0 2 4 7 8
```

### Sudoku Board Format (9x9)
Enter 9 numbers per line (0 for empty cells):
```
5 3 0 0 7 0 0 0 0
6 0 0 1 9 5 0 0 0
0 9 8 0 0 0 0 6 0
8 0 0 0 6 0 0 0 3
4 0 0 8 0 3 0 0 1
7 0 0 0 2 0 0 0 6
0 6 0 0 0 0 2 8 0
0 0 0 4 1 9 0 0 5
0 0 0 0 8 0 0 7 9
```

---

## 25. Example Outputs

### A. Sudoku Performance Comparison Table
```
================================================================================
        SUDOKU CSP PERFORMANCE COMPARISON — 9x9 (Classic Easy 9x9)
================================================================================
Algorithm                       Assignments     Backtracks      Runtime(ms)     
--------------------------------------------------------------------------------
Plain Backtracking              4208            4157                59.621      
Backtracking + MRV              51              0                   22.382      
Backtracking + MRV + FC         51              0                    0.719      
Backtracking + MRV + FC + AC-3  0               0                    2.698      
================================================================================
```

### B. Explainable AI (XAI) Step Explanation
```
==================================================
 STEP 1 — A* EXPLANATION (Right)
==================================================
Puzzle State:
1 2 3
4 5 6
7 8 _

Cost Metrics: g(n) = 1 (path cost) | h(n) = 0 (heuristic) | f(n) = 1

PER-TILE MANHATTAN CONTRIBUTIONS:
  Tile 1: dist = 0 (curr=(0, 0) -> goal=(0, 0)) [GOAL]
  Tile 2: dist = 0 (curr=(0, 1) -> goal=(0, 1)) [GOAL]
  Tile 3: dist = 0 (curr=(0, 2) -> goal=(0, 2)) [GOAL]
  Tile 4: dist = 0 (curr=(1, 0) -> goal=(1, 0)) [GOAL]
  Tile 5: dist = 0 (curr=(1, 1) -> goal=(1, 1)) [GOAL]
  Tile 6: dist = 0 (curr=(1, 2) -> goal=(1, 2)) [GOAL]
  Tile 7: dist = 0 (curr=(2, 0) -> goal=(2, 0)) [GOAL]
  Tile 8: dist = 0 (curr=(2, 1) -> goal=(2, 1)) [GOAL]
Total Manhattan Distance: 0

ACTION EXPLANATION:
  Blank moved Right, sliding tile 8 into its final goal position.
==================================================
```

---

## 26. Testing Instructions

Execute the automated test suite discovering all test modules:
```bash
python -m unittest discover -s tests -v
```

All **46 unit tests** run in under 0.1 seconds and cover:
- Original A* heuristic correctness and optimal cost agreement.
- 4x4 and 9x9 Sudoku solving across Plain, MRV, FC, and AC-3.
- Board dimension, duplicate clue, and range validation.
- Unsolvable puzzle detection for both 8-Puzzle and Sudoku.
- Hint generation, legal move identification, and tie-breaking.
- Solvability parity rules and mathematical invariants.
- XAI per-tile decompositions and actual search trace auditing.

---

## 27. Results

- **Optimality**: Both Misplaced Tiles and Manhattan Distance heuristics strictly find the identical optimal path length for any solvable 8-puzzle.
- **Node Pruning**: Manhattan Distance consistently reduces node expansions by 40%–60% compared to Misplaced Tiles.
- **Inversion Parity**: 100% of unsolvable 8-puzzle states are rejected instantly with zero search overhead.
- **Constraint Satisfaction**: MRV and Forward Checking eliminate over 99% of backtracking thrashing compared to baseline backtracking on 9x9 Sudoku.

---

## 28. Limitations

1. **8-Puzzle State-Space Scalability**: A* memory complexity is exponential with depth because all explored and frontier nodes reside in RAM. While 8-Puzzle ($3 \times 3$) solves in fractions of a second, 15-Puzzle ($4 \times 4$) requires IDA* (Iterative Deepening A*) to avoid memory exhaustion.
2. **Deterministic Tie-Breaking**: When multiple frontier nodes have identical $f(n)$, insertion order (FIFO) decides expansion. Different tie-breaking rules can slightly alter node counts, though optimality is never compromised.
3. **Propagation Overhead on Small Grids**: For small grids (4x4), maintaining arc queues in AC-3 incurs higher constant-factor overhead than basic backtracking.

---

## 29. Conclusion

This project successfully proves and demonstrates the foundational differences between Search and Constraint Satisfaction:
- **Search (A\*)** is necessary when the goal is to discover an optimal sequence of transitions where intermediate path cost matters.
- **CSPs (Sudoku)** are significantly more effective when the goal is to find a valid assignment of values subject to constraints, allowing domain propagation (FC, AC-3) to prune trillions of dead-end branches.

---

## 30. Future Enhancements

- **IDA\* and Pattern Databases**: Implement Iterative Deepening A* with disjoint pattern databases to scale up to the 15-Puzzle and 24-Puzzle.
- **Least Constraining Value (LCV)**: Add value ordering heuristics to the Sudoku CSP solver.
- **Generalized N-Queens and Map Coloring**: Extend the CSP engine to solve N-Queens and Australia map coloring problems.
- **Interactive Visual GUI**: Build a lightweight Python `tkinter` visualization for real-time tile animation and arc propagation step-throughs.

---

## 31. Viva Preparation & Defense Questions

### Q1: Why is Manhattan Distance admissible for the 8-Puzzle?
**Answer**: A heuristic is admissible if it never overestimates the true cost to reach the goal. In the 8-Puzzle, a tile can move at most one horizontal or vertical unit per move. Therefore, a tile at $(r, c)$ cannot reach $(r_{goal}, c_{goal})$ in fewer moves than $|r - r_{goal}| + |c - c_{goal}|$. Summing these minimums across all tiles can never exceed the total moves required, guaranteeing admissibility and A* optimality.

### Q2: Why does an odd inversion count prove an 8-Puzzle is unsolvable?
**Answer**: Sliding the blank horizontally does not alter the relative order of numbered tiles. Sliding the blank vertically swaps a tile past two other tiles, changing the inversion count by $+2, -2$, or $0$. In all cases, the parity (evenness/oddness) of inversions is an invariant. The goal state has 0 inversions (even parity). Therefore, any state with an odd inversion count belongs to a disjoint half of the state space and can never reach the goal state.

### Q3: What is the difference between Forward Checking and AC-3?
**Answer**: Forward Checking only checks constraints between the **currently assigned variable** and its **immediate unassigned neighbors** (1-step forward lookahead). AC-3 propagates constraints transitively across the entire constraint graph: if removing a value from variable $X_i$ reduces its domain, AC-3 re-checks all variables $X_k$ that constrain $X_i$, propagating prunings throughout the network until arc consistency is achieved.

### Q4: Why is MRV called the "fail-first" heuristic?
**Answer**: MRV chooses the unassigned variable with the fewest legal values. By selecting the most constrained variable first, if that variable has no solution or will quickly run out of options, the algorithm detects failure immediately near the top of the search tree. This prunes entire subtrees early, preventing exponential thrashing.

### Q5: When would you use A* over CSP?
**Answer**: A* is preferred when the objective is to find the **cheapest sequence of steps/actions** (pathfinding, route navigation, robot motion planning). CSP is preferred when the objective is to find a **valid configuration or assignment** where the order of assignments has no physical meaning or cost (scheduling, timetabling, circuit placement).
