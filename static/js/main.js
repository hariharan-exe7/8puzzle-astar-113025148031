/**
 * AI Search & CSP Solver — Frontend JavaScript Controller
 * Vanilla ES6 JavaScript for 8-Puzzle, Sudoku CSP, and Comparisons
 */

document.addEventListener("DOMContentLoaded", function () {
    initPuzzleModule();
    initSudokuModule();
    initComparisonModule();
});

// ==========================================================================
// 1. 8-Puzzle Module Controller
// ==========================================================================
function initPuzzleModule() {
    const puzzleInputs = document.getElementById("puzzle-inputs");
    if (!puzzleInputs) return;

    const presetSelect = document.getElementById("puzzle-preset");
    const heuristicSelect = document.getElementById("heuristic-select");
    const btnSolve = document.getElementById("btn-solve-puzzle");
    const btnSolvability = document.getElementById("btn-check-solvability");
    const btnHint = document.getElementById("btn-get-hint");
    const btnReset = document.getElementById("btn-reset-puzzle");

    const alertBox = document.getElementById("puzzle-alert");
    const placeholder = document.getElementById("puzzle-placeholder");
    const loadingBox = document.getElementById("puzzle-loading");

    const solvabilityOutput = document.getElementById("solvability-output");
    const hintOutput = document.getElementById("hint-output");
    const solutionOutput = document.getElementById("solution-output");

    const stepperBoard = document.getElementById("stepper-board");
    const btnPrevStep = document.getElementById("btn-prev-step");
    const btnNextStep = document.getElementById("btn-next-step");
    const stepperIndicator = document.getElementById("stepper-indicator");

    let currentSteps = [];
    let currentStepIdx = 0;

    // Helper: Show alert message
    function showAlert(msg, isError = true) {
        alertBox.className = `alert ${isError ? "alert-danger" : "alert-success"}`;
        alertBox.textContent = msg;
        alertBox.classList.remove("d-none");
    }

    function hideAlert() {
        alertBox.classList.add("d-none");
        alertBox.textContent = "";
    }

    function hideAllOutputs() {
        if (solvabilityOutput) solvabilityOutput.classList.add("d-none");
        if (hintOutput) hintOutput.classList.add("d-none");
        if (solutionOutput) solutionOutput.classList.add("d-none");
        if (placeholder) placeholder.classList.remove("d-none");
    }

    function setLoading(isLoading) {
        if (isLoading) {
            loadingBox.classList.remove("d-none");
            if (placeholder) placeholder.classList.add("d-none");
            hideAlert();
        } else {
            loadingBox.classList.add("d-none");
        }
        [btnSolve, btnSolvability, btnHint, btnReset].forEach(b => {
            if (b) b.disabled = isLoading;
        });
    }

    // Read current 9 numbers from inputs
    function getPuzzleState() {
        const state = [];
        for (let i = 0; i < 9; i++) {
            const input = document.getElementById(`tile-${i}`);
            const val = parseInt(input.value, 10);
            if (isNaN(val) || val < 0 || val > 8) {
                throw new Error(`Tile ${i + 1} must be an integer between 0 and 8.`);
            }
            state.push(val);
        }
        const sorted = [...state].sort((a, b) => a - b);
        for (let i = 0; i < 9; i++) {
            if (sorted[i] !== i) {
                throw new Error("Puzzle must contain each number 0 to 8 exactly once without duplicates.");
            }
        }
        return state;
    }

    // Set state into input tiles
    function setPuzzleState(arr) {
        for (let i = 0; i < 9; i++) {
            const input = document.getElementById(`tile-${i}`);
            if (input) {
                input.value = arr[i];
                if (arr[i] === 0) {
                    input.classList.add("blank-tile");
                } else {
                    input.classList.remove("blank-tile");
                }
            }
        }
    }

    // Tile input styling listener
    for (let i = 0; i < 9; i++) {
        const input = document.getElementById(`tile-${i}`);
        if (input) {
            input.addEventListener("input", function () {
                const val = parseInt(this.value, 10);
                if (val === 0) {
                    this.classList.add("blank-tile");
                } else {
                    this.classList.remove("blank-tile");
                }
            });
        }
    }

    // Preset selector change
    if (presetSelect) {
        presetSelect.addEventListener("change", function () {
            const arr = this.value.split(",").map(Number);
            setPuzzleState(arr);
            hideAlert();
            hideAllOutputs();
        });
    }

    // Reset button
    if (btnReset) {
        btnReset.addEventListener("click", function () {
            if (presetSelect) presetSelect.value = "1,2,3,4,0,6,7,5,8";
            setPuzzleState([1, 2, 3, 4, 0, 6, 7, 5, 8]);
            hideAlert();
            hideAllOutputs();
        });
    }

    // Render single step on visual board
    function renderStep(idx) {
        if (!currentSteps || currentSteps.length === 0) return;
        currentStepIdx = Math.max(0, Math.min(idx, currentSteps.length - 1));
        const step = currentSteps[currentStepIdx];

        // Update visual tiles
        stepperBoard.innerHTML = "";
        step.state_flat.forEach(val => {
            const tileEl = document.createElement("div");
            tileEl.className = `stepper-tile ${val === 0 ? "blank" : ""}`;
            tileEl.textContent = val === 0 ? "" : val;
            stepperBoard.appendChild(tileEl);
        });

        // Update indicator
        stepperIndicator.textContent = `Step ${currentStepIdx} of ${currentSteps.length - 1} (${step.move_name})`;

        // Update Stepper buttons
        btnPrevStep.disabled = currentStepIdx === 0;
        btnNextStep.disabled = currentStepIdx === currentSteps.length - 1;

        // Update XAI costs
        document.getElementById("xai-g").textContent = step.g;
        document.getElementById("xai-h").textContent = step.h;
        document.getElementById("xai-f").textContent = step.f;
        document.getElementById("xai-action").textContent = step.move_name;
        document.getElementById("xai-desc").textContent = step.action_desc;

        // Update Per-Tile Manhattan Table
        const tbody = document.getElementById("xai-tile-tbody");
        tbody.innerHTML = "";
        step.per_tile.forEach(item => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>Tile ${item.tile}</strong></td>
                <td>(${item.current_pos[0]}, ${item.current_pos[1]})</td>
                <td>(${item.goal_pos[0]}, ${item.goal_pos[1]})</td>
                <td>${item.distance}</td>
                <td>${item.is_home ? '<span class="home-badge">&check; In Goal</span>' : 'Displaced'}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    if (btnPrevStep) {
        btnPrevStep.addEventListener("click", () => renderStep(currentStepIdx - 1));
    }
    if (btnNextStep) {
        btnNextStep.addEventListener("click", () => renderStep(currentStepIdx + 1));
    }

    // SOLVE PUZZLE ACTION
    if (btnSolve) {
        btnSolve.addEventListener("click", async function () {
            hideAlert();
            let state;
            try {
                state = getPuzzleState();
            } catch (err) {
                showAlert(err.message);
                return;
            }

            setLoading(true);
            try {
                const response = await fetch("/api/puzzle/solve", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        state: state,
                        heuristic: heuristicSelect.value
                    })
                });

                const data = await response.json();
                setLoading(false);

                if (!data.success) {
                    showAlert(data.error || "Failed to solve puzzle.");
                    hideAllOutputs();
                    return;
                }

                // Show Solution Panel
                hideAllOutputs();
                if (placeholder) placeholder.classList.add("d-none");
                solutionOutput.classList.remove("d-none");

                document.getElementById("sol-cost").textContent = data.cost;
                document.getElementById("sol-nodes").textContent = data.nodes_expanded;
                document.getElementById("sol-time").textContent = data.runtime_ms;

                currentSteps = data.steps;
                renderStep(0);
            } catch (err) {
                setLoading(false);
                showAlert("Server connection error: " + err.message);
            }
        });
    }

    // CHECK SOLVABILITY ACTION
    if (btnSolvability) {
        btnSolvability.addEventListener("click", async function () {
            hideAlert();
            let state;
            try {
                state = getPuzzleState();
            } catch (err) {
                showAlert(err.message);
                return;
            }

            setLoading(true);
            try {
                const response = await fetch("/api/puzzle/solvability", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ state: state })
                });

                const data = await response.json();
                setLoading(false);

                if (!data.success) {
                    showAlert(data.error || "Failed to check solvability.");
                    return;
                }

                hideAllOutputs();
                if (placeholder) placeholder.classList.add("d-none");
                solvabilityOutput.classList.remove("d-none");

                const badge = document.getElementById("solvability-badge");
                if (data.is_solvable) {
                    badge.className = "badge badge-success";
                    badge.textContent = "SOLVABLE";
                } else {
                    badge.className = "badge badge-danger";
                    badge.textContent = "UNSOLVABLE";
                }

                document.getElementById("solvability-inversions").textContent = data.inversion_count;
                document.getElementById("solvability-parity").textContent = data.parity;
                document.getElementById("solvability-sequence").textContent = data.tiles_sequence.join(", ");

                const pairsText = data.inversion_pairs.length > 0
                    ? data.inversion_pairs.map(p => `(${p[0]}, ${p[1]})`).join(" ")
                    : "None (0 inversions)";
                document.getElementById("solvability-pairs").textContent = pairsText;
                document.getElementById("solvability-rule").textContent = data.rule;
            } catch (err) {
                setLoading(false);
                showAlert("Server error: " + err.message);
            }
        });
    }

    // GET HINT ACTION
    if (btnHint) {
        btnHint.addEventListener("click", async function () {
            hideAlert();
            let state;
            try {
                state = getPuzzleState();
            } catch (err) {
                showAlert(err.message);
                return;
            }

            setLoading(true);
            try {
                const response = await fetch("/api/puzzle/hint", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ state: state })
                });

                const data = await response.json();
                setLoading(false);

                if (!data.success) {
                    showAlert(data.error || "Failed to generate hint.");
                    return;
                }

                const gh = data.greedy_hint;
                if (!gh.solvable) {
                    showAlert(gh.message || "Cannot generate hint for unsolvable state.");
                    return;
                }

                hideAllOutputs();
                if (placeholder) placeholder.classList.add("d-none");
                hintOutput.classList.remove("d-none");

                if (gh.solved) {
                    document.getElementById("hint-move").textContent = "N/A";
                    document.getElementById("hint-tile").textContent = "N/A";
                    document.getElementById("hint-curr-h").textContent = "0";
                    document.getElementById("hint-new-h").textContent = "0";
                    document.getElementById("hint-reason").textContent = "The puzzle is already in the goal state!";
                } else {
                    document.getElementById("hint-move").textContent = gh.recommended_move;
                    document.getElementById("hint-tile").textContent = gh.moving_tile;
                    document.getElementById("hint-curr-h").textContent = gh.current_manhattan;
                    document.getElementById("hint-new-h").textContent = gh.new_manhattan;
                    document.getElementById("hint-reason").textContent = gh.reason;
                }

                // Optimal hint
                const optBox = document.getElementById("optimal-hint-box");
                if (data.optimal_hint && data.optimal_hint.solvable && !data.optimal_hint.solved) {
                    optBox.classList.remove("d-none");
                    document.getElementById("optimal-hint-text").textContent =
                        `Move blank ${data.optimal_hint.recommended_move} (sliding tile ${data.optimal_hint.moving_tile}) ` +
                        `as step 1 of the optimal ${data.optimal_hint.total_optimal_cost}-move shortest path.`;
                } else {
                    optBox.classList.add("d-none");
                }
            } catch (err) {
                setLoading(false);
                showAlert("Server error: " + err.message);
            }
        });
    }
}


// ==========================================================================
// 2. Sudoku Module Controller
// ==========================================================================
function initSudokuModule() {
    const boardEl = document.getElementById("sudoku-board");
    if (!boardEl) return;

    let currentSize = 9;

    const btnSize4 = document.getElementById("btn-size-4");
    const btnSize9 = document.getElementById("btn-size-9");
    const presetSelect = document.getElementById("sudoku-preset");
    const algoSelect = document.getElementById("sudoku-algorithm");
    const btnSolve = document.getElementById("btn-solve-sudoku");
    const btnLoad = document.getElementById("btn-load-sudoku");
    const btnClear = document.getElementById("btn-clear-sudoku");

    const alertBox = document.getElementById("sudoku-alert");
    const placeholder = document.getElementById("sudoku-placeholder");
    const loadingBox = document.getElementById("sudoku-loading");
    const solutionPanel = document.getElementById("sudoku-solution-panel");

    // Presets definitions
    const SUDOKU_PRESETS = {
        4: [
            {
                name: "Classic 4x4",
                board: [
                    [1, 0, 0, 4],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [3, 0, 0, 2]
                ]
            },
            {
                name: "Moderate 4x4",
                board: [
                    [0, 2, 4, 0],
                    [1, 0, 0, 3],
                    [4, 0, 0, 2],
                    [0, 1, 3, 0]
                ]
            }
        ],
        9: [
            {
                name: "Classic Easy 9x9",
                board: [
                    [5, 3, 0, 0, 7, 0, 0, 0, 0],
                    [6, 0, 0, 1, 9, 5, 0, 0, 0],
                    [0, 9, 8, 0, 0, 0, 0, 6, 0],
                    [8, 0, 0, 0, 6, 0, 0, 0, 3],
                    [4, 0, 0, 8, 0, 3, 0, 0, 1],
                    [7, 0, 0, 0, 2, 0, 0, 0, 6],
                    [0, 6, 0, 0, 0, 0, 2, 8, 0],
                    [0, 0, 0, 4, 1, 9, 0, 0, 5],
                    [0, 0, 0, 0, 8, 0, 0, 7, 9]
                ]
            },
            {
                name: "Medium 9x9",
                board: [
                    [0, 0, 0, 2, 6, 0, 7, 0, 1],
                    [6, 8, 0, 0, 7, 0, 0, 9, 0],
                    [1, 9, 0, 0, 0, 4, 5, 0, 0],
                    [8, 2, 0, 1, 0, 0, 0, 4, 0],
                    [0, 0, 4, 6, 0, 2, 9, 0, 0],
                    [0, 5, 0, 0, 0, 3, 0, 2, 8],
                    [0, 0, 9, 3, 0, 0, 0, 7, 4],
                    [0, 4, 0, 0, 5, 0, 0, 3, 6],
                    [7, 0, 3, 0, 1, 8, 0, 0, 0]
                ]
            }
        ]
    };

    function showAlert(msg, isError = true) {
        alertBox.className = `alert ${isError ? "alert-danger" : "alert-success"}`;
        alertBox.textContent = msg;
        alertBox.classList.remove("d-none");
    }

    function hideAlert() {
        alertBox.classList.add("d-none");
        alertBox.textContent = "";
    }

    function setLoading(isLoading) {
        if (isLoading) {
            loadingBox.classList.remove("d-none");
            if (placeholder) placeholder.classList.add("d-none");
            if (solutionPanel) solutionPanel.classList.add("d-none");
            hideAlert();
        } else {
            loadingBox.classList.add("d-none");
        }
        [btnSolve, btnLoad, btnClear].forEach(b => {
            if (b) b.disabled = isLoading;
        });
    }

    // Populate preset dropdown
    function updatePresetOptions() {
        presetSelect.innerHTML = "";
        SUDOKU_PRESETS[currentSize].forEach((p, idx) => {
            const opt = document.createElement("option");
            opt.value = idx;
            opt.textContent = p.name;
            presetSelect.appendChild(opt);
        });
    }

    // Render grid input cells
    function renderBoard(size) {
        boardEl.className = `sudoku-grid size-${size}`;
        boardEl.innerHTML = "";
        for (let r = 0; r < size; r++) {
            for (let c = 0; c < size; c++) {
                const cell = document.createElement("input");
                cell.type = "number";
                cell.min = 1;
                cell.max = size;
                cell.className = "sudoku-cell";
                cell.id = `cell-${r}-${c}`;
                cell.dataset.row = r;
                cell.dataset.col = c;
                boardEl.appendChild(cell);
            }
        }
    }

    function setBoardValues(grid2d) {
        const size = grid2d.length;
        for (let r = 0; r < size; r++) {
            for (let c = 0; c < size; c++) {
                const cell = document.getElementById(`cell-${r}-${c}`);
                if (cell) {
                    const val = grid2d[r][c];
                    cell.value = val === 0 ? "" : val;
                    cell.classList.remove("clue", "solved");
                    if (val !== 0) {
                        cell.classList.add("clue");
                    }
                }
            }
        }
    }

    function getBoardValues() {
        const grid = [];
        for (let r = 0; r < currentSize; r++) {
            const row = [];
            for (let c = 0; c < currentSize; c++) {
                const cell = document.getElementById(`cell-${r}-${c}`);
                const val = parseInt(cell.value, 10);
                row.push(isNaN(val) ? 0 : val);
            }
            grid.push(row);
        }
        return grid;
    }

    // Tab buttons
    if (btnSize4) {
        btnSize4.addEventListener("click", () => switchSize(4));
    }
    if (btnSize9) {
        btnSize9.addEventListener("click", () => switchSize(9));
    }

    function switchSize(size) {
        currentSize = size;
        btnSize4.classList.toggle("active", size === 4);
        btnSize9.classList.toggle("active", size === 9);
        updatePresetOptions();
        renderBoard(size);
        setBoardValues(SUDOKU_PRESETS[size][0].board);
        hideAlert();
        if (solutionPanel) solutionPanel.classList.add("d-none");
        if (placeholder) placeholder.classList.remove("d-none");
    }

    if (btnLoad) {
        btnLoad.addEventListener("click", () => {
            const idx = parseInt(presetSelect.value, 10);
            setBoardValues(SUDOKU_PRESETS[currentSize][idx].board);
            hideAlert();
            if (solutionPanel) solutionPanel.classList.add("d-none");
            if (placeholder) placeholder.classList.remove("d-none");
        });
    }

    if (btnClear) {
        btnClear.addEventListener("click", () => {
            const empty = Array(currentSize).fill(0).map(() => Array(currentSize).fill(0));
            setBoardValues(empty);
            hideAlert();
            if (solutionPanel) solutionPanel.classList.add("d-none");
            if (placeholder) placeholder.classList.remove("d-none");
        });
    }

    // Algorithm Insight descriptions
    const ALGO_DESCRIPTIONS = {
        ac3: {
            title: "Backtracking + MRV + Forward Checking + AC-3",
            text: "Runs Arc Consistency (AC-3) across all binary inequality peers as an initial preprocessing step. During search, it chooses the Minimum Remaining Values cell and maintains arc consistency across active peers."
        },
        fc: {
            title: "Backtracking + MRV + Forward Checking",
            text: "Selects variables using the MRV ('fail-first') heuristic. After assigning a value, it immediately prunes that value from the domains of all unassigned peers, detecting domain wipeouts before recursing deeper."
        },
        mrv: {
            title: "Backtracking + MRV (Minimum Remaining Values)",
            text: "Evaluates legal candidates on-demand for unassigned cells and chooses the most constrained variable first. Does not maintain domain pruning."
        },
        plain: {
            title: "Plain Backtracking (Baseline DFS)",
            text: "Standard recursive depth-first search. Scans in fixed row-major order and tries values 1 to N, checking constraints before each trial assignment."
        }
    };

    // SOLVE SUDOKU
    if (btnSolve) {
        btnSolve.addEventListener("click", async function () {
            hideAlert();
            const board = getBoardValues();
            const algoKey = algoSelect.value;

            setLoading(true);
            try {
                const response = await fetch("/api/sudoku/solve", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        board: board,
                        algorithm: algoKey
                    })
                });

                const data = await response.json();
                setLoading(false);

                if (!data.success) {
                    showAlert(data.error || "Could not solve this Sudoku puzzle.");
                    return;
                }

                // Show solution panel
                if (placeholder) placeholder.classList.add("d-none");
                solutionPanel.classList.remove("d-none");

                // Populate metrics
                document.getElementById("metric-assignments").textContent = data.assignments;
                document.getElementById("metric-backtracks").textContent = data.backtracks;
                document.getElementById("metric-runtime").textContent = data.runtime_ms;

                // Highlight clues vs solved cells
                const clueLookup = new Set(data.clues.map(c => `${c[0]}-${c[1]}`));
                for (let r = 0; r < data.size; r++) {
                    for (let c = 0; c < data.size; c++) {
                        const cell = document.getElementById(`cell-${r}-${c}`);
                        if (cell) {
                            cell.value = data.solved_board[r][c];
                            cell.classList.remove("clue", "solved");
                            if (clueLookup.has(`${r}-${c}`)) {
                                cell.classList.add("clue");
                            } else {
                                cell.classList.add("solved");
                            }
                        }
                    }
                }

                // Set insights
                const insight = ALGO_DESCRIPTIONS[algoKey] || ALGO_DESCRIPTIONS.ac3;
                document.getElementById("insight-title").textContent = insight.title;
                document.getElementById("insight-text").textContent = insight.text;
            } catch (err) {
                setLoading(false);
                showAlert("Server error: " + err.message);
            }
        });
    }

    // Initialize board on load
    updatePresetOptions();
    renderBoard(currentSize);
    setBoardValues(SUDOKU_PRESETS[currentSize][0].board);
}


// ==========================================================================
// 3. Comparison Module Controller
// ==========================================================================
function initComparisonModule() {
    // SECTION A: 8-Puzzle Comparison
    const btnPuzzleCompare = document.getElementById("btn-run-puzzle-compare");
    if (btnPuzzleCompare) {
        const puzzlePreset = document.getElementById("compare-puzzle-preset");
        const pAlert = document.getElementById("puzzle-compare-alert");
        const pLoading = document.getElementById("puzzle-compare-loading");
        const pResults = document.getElementById("puzzle-compare-results");
        const pTbody = document.getElementById("puzzle-compare-tbody");
        const pAnalysis = document.getElementById("puzzle-compare-analysis");

        btnPuzzleCompare.addEventListener("click", async function () {
            pAlert.classList.add("d-none");
            pResults.classList.add("d-none");
            pLoading.classList.remove("d-none");
            btnPuzzleCompare.disabled = true;

            const stateArr = puzzlePreset.value.split(",").map(Number);
            try {
                const response = await fetch("/api/puzzle/compare", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ state: stateArr })
                });

                const data = await response.json();
                pLoading.classList.add("d-none");
                btnPuzzleCompare.disabled = false;

                if (!data.success) {
                    pAlert.textContent = data.error || "Failed to compare heuristics.";
                    pAlert.className = "alert alert-danger";
                    pAlert.classList.remove("d-none");
                    return;
                }

                pTbody.innerHTML = `
                    <tr>
                        <td><strong>${data.misplaced.name}</strong></td>
                        <td>${data.misplaced.cost}</td>
                        <td>${data.misplaced.nodes_expanded}</td>
                        <td>${data.misplaced.runtime_ms} ms</td>
                        <td>Admissible (Optimal Cost)</td>
                    </tr>
                    <tr>
                        <td><strong>${data.manhattan.name}</strong></td>
                        <td>${data.manhattan.cost}</td>
                        <td>${data.manhattan.nodes_expanded}</td>
                        <td>${data.manhattan.runtime_ms} ms</td>
                        <td>Admissible &amp; Dominant</td>
                    </tr>
                `;

                pAnalysis.innerHTML = `
                    <h4>Heuristic Analysis:</h4>
                    <p>
                        Both heuristics found the identical optimal solution cost of <strong>${data.manhattan.cost} moves</strong>.
                        Manhattan Distance reduced node expansions from <strong>${data.misplaced.nodes_expanded}</strong> to
                        <strong>${data.manhattan.nodes_expanded}</strong> (a <strong>${data.reduction_percent}% reduction</strong>).
                        This confirms that Manhattan Distance is a more informed heuristic that prunes unpromising branches earlier.
                    </p>
                `;

                pResults.classList.remove("d-none");
            } catch (err) {
                pLoading.classList.add("d-none");
                btnPuzzleCompare.disabled = false;
                pAlert.textContent = "Server error: " + err.message;
                pAlert.className = "alert alert-danger";
                pAlert.classList.remove("d-none");
            }
        });
    }

    // SECTION B: Sudoku Comparison
    const btnSudokuCompare = document.getElementById("btn-run-sudoku-compare");
    if (btnSudokuCompare) {
        const sizeSelect = document.getElementById("compare-sudoku-size");
        const presetSelect = document.getElementById("compare-sudoku-preset");
        const sAlert = document.getElementById("sudoku-compare-alert");
        const sLoading = document.getElementById("sudoku-compare-loading");
        const sResults = document.getElementById("sudoku-compare-results");
        const sTbody = document.getElementById("sudoku-compare-tbody");

        const BOARDS = {
            4: [
                {
                    name: "Classic 4x4",
                    board: [
                        [1, 0, 0, 4],
                        [0, 0, 0, 0],
                        [0, 0, 0, 0],
                        [3, 0, 0, 2]
                    ]
                }
            ],
            9: [
                {
                    name: "Classic Easy 9x9",
                    board: [
                        [5, 3, 0, 0, 7, 0, 0, 0, 0],
                        [6, 0, 0, 1, 9, 5, 0, 0, 0],
                        [0, 9, 8, 0, 0, 0, 0, 6, 0],
                        [8, 0, 0, 0, 6, 0, 0, 0, 3],
                        [4, 0, 0, 8, 0, 3, 0, 0, 1],
                        [7, 0, 0, 0, 2, 0, 0, 0, 6],
                        [0, 6, 0, 0, 0, 0, 2, 8, 0],
                        [0, 0, 0, 4, 1, 9, 0, 0, 5],
                        [0, 0, 0, 0, 8, 0, 0, 7, 9]
                    ]
                },
                {
                    name: "Medium 9x9",
                    board: [
                        [0, 0, 0, 2, 6, 0, 7, 0, 1],
                        [6, 8, 0, 0, 7, 0, 0, 9, 0],
                        [1, 9, 0, 0, 0, 4, 5, 0, 0],
                        [8, 2, 0, 1, 0, 0, 0, 4, 0],
                        [0, 0, 4, 6, 0, 2, 9, 0, 0],
                        [0, 5, 0, 0, 0, 3, 0, 2, 8],
                        [0, 0, 9, 3, 0, 0, 0, 7, 4],
                        [0, 4, 0, 0, 5, 0, 0, 3, 6],
                        [7, 0, 3, 0, 1, 8, 0, 0, 0]
                    ]
                }
            ]
        };

        function updateSudokuComparePresets() {
            const sz = parseInt(sizeSelect.value, 10);
            presetSelect.innerHTML = "";
            BOARDS[sz].forEach((b, idx) => {
                const opt = document.createElement("option");
                opt.value = idx;
                opt.textContent = b.name;
                presetSelect.appendChild(opt);
            });
        }

        sizeSelect.addEventListener("change", updateSudokuComparePresets);
        updateSudokuComparePresets();

        btnSudokuCompare.addEventListener("click", async function () {
            sAlert.classList.add("d-none");
            sResults.classList.add("d-none");
            sLoading.classList.remove("d-none");
            btnSudokuCompare.disabled = true;

            const sz = parseInt(sizeSelect.value, 10);
            const bIdx = parseInt(presetSelect.value, 10);
            const board = BOARDS[sz][bIdx].board;

            try {
                const response = await fetch("/api/sudoku/compare", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ board: board })
                });

                const data = await response.json();
                sLoading.classList.add("d-none");
                btnSudokuCompare.disabled = false;

                if (!data.success) {
                    sAlert.textContent = data.error || "Failed to compare algorithms.";
                    sAlert.className = "alert alert-danger";
                    sAlert.classList.remove("d-none");
                    return;
                }

                sTbody.innerHTML = "";
                data.results.forEach(r => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td><strong>${r.method_name}</strong></td>
                        <td>${r.assignments}</td>
                        <td>${r.backtracks}</td>
                        <td>${r.runtime_ms} ms</td>
                        <td><span class="home-badge">${r.is_solved ? "Solved" : "Failed"}</span></td>
                    `;
                    sTbody.appendChild(tr);
                });

                sResults.classList.remove("d-none");
            } catch (err) {
                sLoading.classList.add("d-none");
                btnSudokuCompare.disabled = false;
                sAlert.textContent = "Server error: " + err.message;
                sAlert.className = "alert alert-danger";
                sAlert.classList.remove("d-none");
            }
        });
    }
}
