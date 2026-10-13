# 8-Puzzle Solver using A* — Search vs. Constraint Satisfaction Study

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-46%20passed-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An AI mini-project that compares two core paradigms on classic puzzles:

- **Heuristic search:** the 8-Puzzle solved optimally with **A\*** using two admissible heuristics (Misplaced Tiles, Manhattan Distance).
- **Constraint satisfaction:** 4x4 and 9x9 **Sudoku** solved with four CSP techniques (Plain Backtracking, MRV, MRV + Forward Checking, MRV + FC + AC-3).

It also includes a knowledge-based solvability checker (inversion parity), a rule-based hint system, an Explainable-AI (XAI) layer, a command-line menu and a Flask web dashboard.

---

## Features

| Area | What it does |
|---|---|
| **A\* search** | Optimal 8-Puzzle solutions, `heapq` frontier with deterministic tie-breaking |
| **Heuristics** | Misplaced Tiles and Manhattan Distance, with side-by-side node-count comparison |
| **Solvability reasoning** | Inversion-parity theorem rejects unsolvable states before any search runs |
| **Hints** | Greedy rule-based hint plus the guaranteed-optimal A* move (they can differ) |
| **XAI** | Per-tile Manhattan contributions, g/h/f at every step, audit of real expansion decisions |
| **Sudoku CSP** | 4x4 and 9x9 grids; Plain, MRV, MRV+FC, MRV+FC+AC-3; assignments, backtracks, runtime |
| **Interfaces** | Interactive CLI (`main.py`) and web dashboard (`app.py`) |
| **Quality** | 46 unit tests, input validation on every entry point |

---

## Quick start

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
pip install -r requirements.txt     # installs Flask only; all AI code uses the standard library
```

### Run the web dashboard
```bash
python app.py
# open http://127.0.0.1:5000
```
Pages: Home, 8-Puzzle (solver, hints, XAI step-through), Sudoku, Comparison, About.

### Run the interactive CLI
```bash
python main.py
```
Menu: `1` Solve 8-Puzzle · `2` Compare heuristics · `3` Check solvability · `4` Hint · `5` XAI explanation · `6` Solve 4x4 Sudoku · `7` Solve 9x9 Sudoku · `8` Compare Sudoku algorithms · `9` Search vs. CSP study · `0` Exit

### Run the original standalone solver
```bash
python src/puzzle_solver.py
# enter 9 numbers, 0 = blank, e.g.  1 3 6 5 0 2 4 7 8
```

### Run the tests
```bash
python -m unittest discover -s tests -v
```

---

## Input formats

**8-Puzzle:** nine integers 0-8 in row-major order, `0` is the blank. Goal state: `1 2 3 4 5 6 7 8 0`.

```
1 3 6 5 0 2 4 7 8
```

**Sudoku:** one row per line, `0` for an empty cell (4 numbers per row for 4x4, 9 for 9x9).

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

More samples are in [`examples/`](examples/).

---

## How it works

### A* and the heuristics
A* expands the frontier state with the lowest `f(n) = g(n) + h(n)`. Both heuristics are admissible, so the first time the goal is popped its cost is optimal.

- **Misplaced Tiles:** number of tiles (not the blank) not in their goal cell.
- **Manhattan Distance:** sum over tiles of |row difference| + |column difference|. It dominates Misplaced Tiles, so it prunes more.

### Solvability (knowledge layer)
Sliding the blank never changes the parity of the inversion count, and the goal has 0 inversions. A 3x3 state is therefore solvable **if and only if its inversion count is even**. Unsolvable inputs are rejected immediately with the inversion pairs shown.

### Sudoku as a CSP
Variables are cells, domains are digits 1..N, constraints are "not equal" between peers in the same row, column and box (7 peers in 4x4, 20 in 9x9).

| Variant | Idea |
|---|---|
| Plain Backtracking | Row-major cell order, ascending values, consistency check per assignment |
| + MRV | Pick the cell with the fewest legal values first ("fail-first") |
| + Forward Checking | Prune the assigned value from peers; fail immediately on an empty domain; undo on backtrack |
| + AC-3 | Arc-consistency propagation before and during search; easy boards can be solved with zero search assignments |

---

## Measured results

Measured by running this code (Python 3.12.3, Flask 3.1.3). Counts are deterministic; runtimes depend on your machine.

### 8-Puzzle test cases

| Start state | Optimal moves | Nodes expanded (Manhattan / Misplaced) |
|---|---|---|
| `1 2 3 4 5 6 7 8 0` (goal) | 0 | 1 / 1 |
| `1 2 3 4 5 6 7 0 8` | 1 | 2 / 2 |
| `1 2 3 4 0 6 7 5 8` | 2 | 3 / 3 |
| `1 2 3 0 4 6 7 5 8` | 3 | 4 / 4 |
| `1 3 6 5 0 2 4 7 8` | 8 | 13 / 19 |
| `8 6 7 2 5 4 3 0 1` (hardest, depth 31) | 31 | 20,291 / 143,840 |
| `1 2 3 4 5 6 8 7 0` | rejected (1 inversion) | — |
| `8 1 2 0 4 3 7 6 5` | rejected (11 inversions) | — |

On `1 3 6 5 0 2 4 7 8`, Manhattan expands **13** nodes versus **19** for Misplaced Tiles (31.6% fewer).

### Large-sample verification
- **Parity rule:** checked against exhaustive breadth-first search over all 362,880 permutations. 181,440 are solvable, with **0 mismatches**.
- **Optimality:** on 400 random solvable states (seed 42, mean depth 22) both heuristics returned the optimal cost **400/400** times.
- **Pruning:** mean nodes expanded 16,103.5 (Misplaced) vs 1,706.0 (Manhattan), about **89% fewer** in aggregate; Manhattan never expanded more nodes on any sampled state.

### Sudoku CSP (assignments / backtracks, in the order Plain · MRV · MRV+FC · MRV+FC+AC-3)

| Board | Assignments | Backtracks | Median runtime (ms) |
|---|---|---|---|
| 4x4, 4 clues | 13 / 12 / 12 / 12 | 1 / 0 / 0 / 0 | 0.03 / 0.28 / 0.04 / 0.14 |
| 4x4, 8 clues | 8 / 8 / 8 / 0 | 0 / 0 / 0 / 0 | 0.02 / 0.09 / 0.02 / 0.11 |
| 9x9 classic (30 clues) | 4208 / 51 / 51 / 0 | 4157 / 0 / 0 / 0 | 29.1 / 11.2 / 0.44 / 2.27 |
| 9x9 medium (36 clues) | 54 / 45 / 45 / 0 | 9 / 0 / 0 / 0 | 0.54 / 8.13 / 0.36 / 1.63 |

Takeaways: MRV removes backtracking on these boards, forward checking makes it far cheaper per step, and AC-3 adds preprocessing overhead that does not always pay off on easy boards. On the 9x9 medium board plain backtracking was actually the fastest in wall-clock time.

---

## Web API

All endpoints accept and return JSON and validate input (errors return HTTP 400 with an `error` message).

| Method & path | Body | Purpose |
|---|---|---|
| `POST /api/puzzle/solve` | `{"state":[1,3,6,5,0,2,4,7,8],"heuristic":"manhattan"}` | Solve with A* (`"manhattan"` or `"misplaced"`) |
| `POST /api/puzzle/solvability` | `{"state":[...]}` | Inversion-parity audit |
| `POST /api/puzzle/hint` | `{"state":[...]}` | Greedy and optimal hints |
| `POST /api/puzzle/compare` | `{"state":[...]}` | Heuristic comparison |
| `POST /api/sudoku/solve` | `{"board":[[...]],"algorithm":"ac3"}` | Solve (`plain`, `mrv`, `fc`, `ac3`) |
| `POST /api/sudoku/compare` | `{"board":[[...]]}` | Run all four variants on one board |

Example:
```bash
curl -X POST http://127.0.0.1:5000/api/puzzle/solve \
  -H "Content-Type: application/json" \
  -d '{"state":[1,3,6,5,0,2,4,7,8],"heuristic":"manhattan"}'
```

---

## Project structure

```
.
├── app.py                  # Flask web server and JSON API
├── main.py                 # Interactive CLI menu
├── requirements.txt        # Flask>=2.0.0
├── src/
│   ├── puzzle_solver.py    # 8-Puzzle model, heuristics, A*, parity rule
│   ├── hint_system.py      # Greedy and optimal hints
│   ├── explainable_ai.py   # Per-tile breakdown and search-trace audit
│   ├── sudoku_csp.py       # CSP model, validation, REVISE / AC-3
│   ├── sudoku_solver.py    # Plain, MRV, FC, AC-3 solvers
│   └── comparison.py       # Benchmarks and Search-vs-CSP study
├── templates/              # HTML pages (base, index, puzzle, sudoku, comparison, about)
├── static/                 # CSS and JavaScript
├── tests/                  # 5 unittest modules, 46 tests
├── examples/               # Sample puzzles
├── screenshots/            # Execution evidence
├── LICENSE                 # MIT
└── .gitignore
```

---

## Limitations

- **A\* memory** grows with search depth because all visited and frontier states are kept. Larger puzzles (15-Puzzle and up) need IDA\* or pattern databases.
- **MRV without propagation** rescans all cells each step and can be slower per step than plain backtracking on easy boards.
- **Small CSP benchmark:** only easy and medium Sudoku boards were measured, on a single machine.
- **Fixed goal:** the parity rule and heuristics assume the standard goal `1 2 3 4 5 6 7 8 0`.
- AC-3 reports `0` assignments when propagation alone solves the board, so that metric is not directly comparable with the other variants.

## Future work

- IDA\* with pattern databases for the 15-Puzzle
- Least-Constraining-Value ordering and a hard-Sudoku benchmark set
- N-Queens and map-colouring on the same CSP engine
- Animated AC-3 propagation in the web UI

---

## References

1. S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., Pearson, 2021.
2. P. E. Hart, N. J. Nilsson and B. Raphael, "A formal basis for the heuristic determination of minimum cost paths," *IEEE Trans. Systems Science and Cybernetics*, 4(2), 1968.
3. A. K. Mackworth, "Consistency in networks of relations," *Artificial Intelligence*, 8(1), 1977.
4. R. M. Haralick and G. L. Elliott, "Increasing tree search efficiency for constraint satisfaction problems," *Artificial Intelligence*, 14(3), 1980.

## Authors

`<Your name(s) and register number(s)>`

## License

Released under the [MIT License](LICENSE).
