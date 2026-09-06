# 8-Puzzle Solver using A* Search

## 1. Project Overview

This project implements an optimal 8-Puzzle solver using the A* search algorithm.

Two admissible heuristics are implemented and compared:

1. Misplaced Tiles
2. Manhattan Distance

The comparison is based on the number of nodes expanded while solving the same puzzle.

---

## 2. Problem Statement

The 8-Puzzle consists of eight numbered tiles and one blank space arranged in a 3 × 3 grid.

The objective is to move the tiles until they reach the goal state:

    1 2 3
    4 5 6
    7 8 0

Here, `0` represents the blank space.

---

## 3. Objective

The objectives of this project are:

- Implement A* search.
- Solve the 8-Puzzle optimally.
- Implement Misplaced Tiles heuristic.
- Implement Manhattan Distance heuristic.
- Compare both heuristics.
- Count nodes expanded.
- Demonstrate the advantage of a more informed heuristic.

---

## 4. A* Search

A* uses the evaluation function:

    f(n) = g(n) + h(n)

Where:

- `g(n)` = cost from the initial state to node n.
- `h(n)` = estimated cost from node n to the goal.
- `f(n)` = estimated total cost.

The node with the smallest estimated total cost is selected for expansion.

---

## 5. Heuristics

### Misplaced Tiles

The Misplaced Tiles heuristic counts the number of tiles that are not in their correct positions.

The blank tile is ignored.

For example:

    1 2 3
    4 5 6
    8 7 0

Tiles 7 and 8 are misplaced.

Therefore:

    h(n) = 2

---

### Manhattan Distance

The Manhattan Distance heuristic calculates how many horizontal and vertical moves each tile needs to reach its goal position.

Formula:

    |current row - goal row|
    +
    |current column - goal column|

The blank tile is ignored.

---

## 6. Admissibility

An admissible heuristic never overestimates the actual minimum cost required to reach the goal.

Both Misplaced Tiles and Manhattan Distance are admissible heuristics for the 8-Puzzle.

Therefore, A* using these heuristics can find an optimal solution.

---

## 7. Why Manhattan Distance is More Informed

Misplaced Tiles only determines whether a tile is in the correct position.

Manhattan Distance also considers how far each tile is from its goal position.

Therefore, Manhattan Distance provides more information about the remaining cost.

Because of this, it generally allows A* to focus its search more effectively and expand fewer nodes.

The exact number of expanded nodes can depend on implementation details and tie-breaking.

---

## 8. Example Input

    1 3 6 5 0 2 4 7 8

---

## 9. Running the Program

From the project root:

```text
python src/puzzle_solver.py