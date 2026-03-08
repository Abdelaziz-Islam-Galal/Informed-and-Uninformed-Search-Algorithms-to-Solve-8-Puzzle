from __future__ import annotations

from dataclasses import dataclass
import os

from algorithms.data_structures import queue, stack, priority_queue
from board import board_8_puzzle
from algorithms.state import board_state
from time import time


class algorithms:
    def __init__(self, puzzle: board_8_puzzle):
        self._puzzle = puzzle
        
    @dataclass
    class result:
        explored: set
        start_state: board_state
        goal_state: board_state|None
        time_taken: float

        # Metadata for reporting (kept optional for backward compatibility)
        algorithm: str = ""
        heuristic: str | None = None
        data_structure: str = ""
        assumptions: list[str] | None = None
        extra_work: list[str] | None = None

        def save_report(self, out_file: str = "report.pdf"):
            """Save a report to .pdf or .txt.

            Matches typical deliverables:
            - path to goal (traceable steps)
            - cost of path, nodes expanded, search depth, running time
            - data structures used + brief algorithm explanation + assumptions + sample run

            Output modes:
            - If out_file ends with .pdf: generates a PDF report (summary + steps).
            - If out_file ends with .txt: writes a plain text report.
            - Otherwise: prints the report to stdout.
            """

            def _normalize_algo_name(name: str) -> str:
                return (name or "").strip().upper()

            def _default_assumptions() -> list[str]:
                return [
                    "Board is a 3x3 8-puzzle and contains exactly one 0 tile.",
                    "If the initial state is unsolvable, the search may fail to find a solution.",
                    "Shuffle-based sample runs generate solvable instances (moves from goal).",
                ]

            def _default_extra_work() -> list[str]:
                return [
                    "Traceable step-by-step path with move labels (U/D/L/R).",
                    "PDF report export (and TXT fallback).",
                ]

            def _algorithm_explanation(algo: str, heuristic: str | None) -> str:
                algo_norm = _normalize_algo_name(algo)
                if algo_norm == "BFS":
                    return (
                        "BFS (Breadth-First Search) explores the state space level-by-level. "
                        "It uses a FIFO queue for the frontier and a visited set to avoid repeats. "
                        "For unit edge costs, BFS is complete and finds the shortest path."
                    )
                if algo_norm in {"A*", "ASTAR", "A_STAR"}:
                    h = (heuristic or "heuristic").strip()
                    return (
                        "A* orders the frontier by f(n)=g(n)+h(n), where g is the path cost so far and h is a heuristic estimate. "
                        f"This run uses: {h}. With an admissible heuristic, A* is optimal and complete."
                    )
                if algo_norm == "DFS":
                    return (
                        "DFS (Depth-First Search) explores by going as deep as possible before backtracking. "
                        "It uses a stack (LIFO). DFS is not optimal in general and may get deep without finding the shortest solution."
                    )
                return "Search algorithm run (no detailed description provided)."

            def _format_moves(path: list[board_state]) -> str:
                move_map = {"up": "U", "down": "D", "left": "L", "right": "R"}
                moves = [move_map.get(s.move, s.move) for s in path[1:]]
                moves = [m for m in moves if m]
                return " ".join(moves) if moves else "(none)"

            def _build_report() -> tuple[str, list[board_state], dict[str, str]]:
                """Build a plain-text report and return (text, path, summary_fields)."""
                algo_norm = _normalize_algo_name(self.algorithm)
                heuristic = (self.heuristic or "").strip() or None

                nodes_expanded = len(self.explored)
                explored_levels = [state.level for state in self.explored] if self.explored else []
                search_depth = max(explored_levels, default=0)

                summary: dict[str, str] = {
                    "Algorithm": self.algorithm or "(unspecified)",
                    "Heuristic": heuristic or "N/A",
                    "Nodes expanded": str(nodes_expanded),
                    "Search depth": str(search_depth),
                    "Running time": f"{self.time_taken:.4f} seconds",
                    "Data structures": self.data_structure or "(not specified)",
                }

                lines: list[str] = []
                lines.append("8-Puzzle Search Report")
                lines.append("=" * 26)
                for k, v in summary.items():
                    lines.append(f"{k}: {v}")
                lines.append("")
                lines.append("Initial state:")
                lines.append(str(self.start_state.board))
                lines.append("")
                lines.append("Goal state:")
                lines.append(str(board_8_puzzle()))
                lines.append("")
                lines.append("Algorithm explanation:")
                lines.append(_algorithm_explanation(self.algorithm, heuristic))
                lines.append("")

                assumptions = self.assumptions or _default_assumptions()
                lines.append("Assumptions:")
                for a in assumptions:
                    lines.append(f"- {a}")
                lines.append("")

                extras = self.extra_work or _default_extra_work()
                lines.append("Extra work:")
                for e in extras:
                    lines.append(f"- {e}")
                lines.append("")

                if not self.goal_state:
                    lines.append("Result: No solution found.")
                    return "\n".join(lines) + "\n", [], summary

                goal_path_local = self.goal_state.get_path()
                cost_of_path = self.goal_state.level
                summary["Cost of path"] = str(cost_of_path)
                summary["Path to goal (moves)"] = _format_moves(goal_path_local)

                lines.append("Result:")
                lines.append(f"- Cost of path: {cost_of_path}")
                lines.append(f"- Path to goal (moves): {summary['Path to goal (moves)']}")
                lines.append("")
                lines.append("Trace (path to solution):")
                lines.append("" )
                for step, state in enumerate(goal_path_local):
                    move_txt = "START" if step == 0 else (state.move or "")
                    move_map = {"up": "U", "down": "D", "left": "L", "right": "R"}
                    move_short = "START" if step == 0 else (move_map.get(move_txt, move_txt) or "")
                    f_txt = ""
                    if state.cost_f is not None:
                        f_txt = f" | f={state.cost_f:.3f}"
                    lines.append(f"Step {step}: move={move_short} | g={state.level}{f_txt}")
                    lines.append(str(state.board))
                    lines.append("")

                return "\n".join(lines) + "\n", goal_path_local, summary

            def _save_pdf(path: str, report_text: str, goal_path_local: list[board_state], summary: dict[str, str]) -> None:
                try:
                    import importlib

                    plt = importlib.import_module("matplotlib.pyplot")
                    PdfPages = importlib.import_module("matplotlib.backends.backend_pdf").PdfPages
                except ModuleNotFoundError as exc:
                    raise ModuleNotFoundError(
                        "matplotlib is required to generate PDF reports. "
                        "Install it in your venv using: .venv/Scripts/python.exe -m pip install matplotlib"
                    ) from exc

                def _draw_board(ax, matrix: list[list[int]], title: str) -> None:
                    ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
                    ax.set_xlim(0, 3)
                    ax.set_ylim(0, 3)
                    ax.set_aspect("equal")
                    ax.axis("off")
                    # Grid
                    for i in range(4):
                        ax.plot([0, 3], [i, i], color="black", linewidth=1)
                        ax.plot([i, i], [0, 3], color="black", linewidth=1)
                    # Numbers
                    for r in range(3):
                        for c in range(3):
                            val = matrix[r][c]
                            txt = "" if val == 0 else str(val)
                            ax.text(
                                c + 0.5,
                                2.5 - r,
                                txt,
                                ha="center",
                                va="center",
                                fontsize=18,
                                family="monospace",
                            )

                with PdfPages(path) as pdf:
                    # Summary page: text + initial/goal boards
                    fig = plt.figure(figsize=(8.27, 11.69))  # A4 portrait
                    fig.suptitle("8-Puzzle Search Report", fontsize=16, fontweight="bold", y=0.985)

                    # Text block (top-left)
                    summary_lines = [f"{k}: {v}" for k, v in summary.items()]
                    fig.text(
                        0.06,
                        0.93,
                        "\n".join(summary_lines),
                        fontsize=11,
                        family="monospace",
                        va="top",
                    )

                    # Boards (top-right)
                    ax_init = fig.add_axes([0.58, 0.74, 0.36, 0.18])
                    _draw_board(ax_init, self.start_state.board.board, "Initial")
                    ax_goal = fig.add_axes([0.58, 0.53, 0.36, 0.18])
                    _draw_board(ax_goal, board_8_puzzle().board, "Goal")

                    # Explanation / assumptions / extra (bottom)
                    explanation = _algorithm_explanation(self.algorithm, self.heuristic)
                    assumptions = self.assumptions or _default_assumptions()
                    extras = self.extra_work or _default_extra_work()
                    bottom_lines: list[str] = []
                    bottom_lines.append("Algorithm explanation:")
                    bottom_lines.append(explanation)
                    bottom_lines.append("")
                    bottom_lines.append("Assumptions:")
                    bottom_lines.extend([f"- {a}" for a in assumptions])
                    bottom_lines.append("")
                    bottom_lines.append("Extra work:")
                    bottom_lines.extend([f"- {e}" for e in extras])
                    fig.text(0.06, 0.48, "\n".join(bottom_lines), fontsize=10, family="monospace", va="top")

                    pdf.savefig(fig)
                    plt.close(fig)

                    # Steps pages (one step per page): board + trace info
                    if goal_path_local:
                        for step, state in enumerate(goal_path_local):
                            move_txt = "START" if step == 0 else (state.move or "")
                            move_map = {"up": "U", "down": "D", "left": "L", "right": "R"}
                            move_short = "START" if step == 0 else (move_map.get(move_txt, move_txt) or "")
                            fig = plt.figure(figsize=(8.27, 11.69))
                            fig.suptitle(f"Step {step}  (move: {move_short})", fontsize=14, fontweight="bold", y=0.985)

                            # Trace numbers
                            trace_lines = [f"g (cost so far): {state.level}"]
                            if state.cost_f is not None:
                                trace_lines.append(f"f = g + h: {state.cost_f:.3f}")
                            if self.heuristic:
                                trace_lines.append(f"Heuristic: {self.heuristic}")
                            fig.text(0.06, 0.93, "\n".join(trace_lines), fontsize=11, family="monospace", va="top")

                            ax = fig.add_axes([0.18, 0.35, 0.64, 0.5])
                            _draw_board(ax, state.board.board, "")

                            pdf.savefig(fig)
                            plt.close(fig)

            report_text, goal_path_local, summary = _build_report()

            out_lower = (out_file or "").lower()
            if out_lower.endswith(".pdf"):
                _save_pdf(out_file, report_text, goal_path_local, summary)
                print(f"Saved PDF report to: {out_file}")
                return

            if out_lower.endswith(".txt"):
                with open(out_file, "w", encoding="utf-8") as f:
                    f.write(report_text)
                print(f"Saved text report to: {out_file}")
                return

            # Fallback: print to stdout
            print(report_text)


    def bfs(self, visual_output:bool) -> algorithms.result:
        """Breadth-First Search (BFS).

        Uses:
        - Frontier: FIFO queue
        - Visited/explored: set (hashing) to avoid revisiting states
        """
        if visual_output:
            os.makedirs("output", exist_ok=True)
            visualizer_input_list: list[tuple[set, set, str, str]] = []

        start_time = time()
        start = board_state(self._puzzle, None)
        explored = set()
        frontier = queue()
        search_frontier = set() # for o(1) search instead of O(n) in the queue
        # o(1) because the set uses hashing

        frontier.enqueue(start)
        search_frontier.add(start)
        if visual_output:
            counter = 0
            visualizer_input_list.append((explored.copy(), search_frontier.copy(), f"step {counter} (start)", f"output/{counter}.png")) # type: ignore
            counter+=1

        while not frontier.is_empty():
            state: board_state = frontier.dequeue()
            explored.add(state)
            search_frontier.remove(state)

            if state.is_goal():
                time_taken = time() - start_time
                if visual_output:
                    from visualizer.tree_drawer import tree_drawer as _tree_drawer
                    drawer = _tree_drawer()
                    for input in visualizer_input_list: # type: ignore
                        drawer.draw(input[0], input[1], None, title=input[2], out_file=input[3]) # type: ignore
                    drawer.draw(explored.copy(), search_frontier.copy(), state, f"step {counter} (start)", f"output/{counter}.png") # type: ignore
                
                return self.result(
                    explored,
                    start,
                    state,
                    time_taken,
                    algorithm="BFS",
                    heuristic=None,
                    data_structure="Queue (FIFO) using collections.deque + explored/frontier sets",
                )

            for neighbor in state.neighbors:
                if neighbor not in explored and neighbor not in search_frontier:
                    frontier.enqueue(neighbor)
                    search_frontier.add(neighbor)

            if visual_output:
                visualizer_input_list.append((explored.copy(), search_frontier.copy(), f"step {counter}", f"output/{counter}.png")) #type: ignore
                counter += 1 # type: ignore

        return self.result(
            explored,
            start,
            None,
            time() - start_time,
            algorithm="BFS",
            heuristic=None,
            data_structure="Queue (FIFO) using collections.deque + explored/frontier sets",
        )
    
    def A_star(
        self,
        visual_output: bool,
        heuristic: str = "manhattan",
        output_dir: str = "output",
    ) -> algorithms.result:
        """A* search.

        Uses:
        - Frontier: priority queue (min-heap) ordered by f=g+h
        - best_g dict: tracks best known g-cost per state to skip stale heap entries
        """
        if visual_output:
            os.makedirs(output_dir, exist_ok=True)
            visualizer_input_list: list[tuple[set, set, str, str]] = []
            counter = 0

        start_time = time()
        heuristic_normalized = heuristic.strip().lower().replace("-", "").replace("_", "")
        if heuristic_normalized in {"manhattan", "manhattandistance"}:
            start = board_state(self._puzzle, None, Manhattan_heuristics=True)
            heuristic_label = "Manhattan"
        elif heuristic_normalized in {"euclidean", "eucledian", "euclideandistance", "euclediandistance"}:
            start = board_state(self._puzzle, None, eucledian_heuristics=True)
            heuristic_label = "Euclidean"
        else:
            raise ValueError("A_star heuristic must be 'manhattan' or 'euclidean'.")

        explored: set[board_state] = set()
        frontier = priority_queue()
        frontier_view: set[board_state] = set()
        best_g: dict[board_state, int] = {start: start.cost}

        frontier.insert(start)
        frontier_view.add(start)
        if visual_output:
            visualizer_input_list.append(
                (
                    explored.copy(),
                    frontier_view.copy(),
                    f"step {counter} (start)",
                    os.path.join(output_dir, f"{counter}.png"),
                )
            )
            counter += 1

        while not frontier.is_empty():
            state: board_state = frontier.pop()
            frontier_view.discard(state)

            best_known = best_g.get(state)
            if best_known is None or state.cost != best_known:#ADD MORE SECURITY TO CHECK THERE IS ONE NODE WITH OPTIMAL COST FOUND
                continue

            explored.add(state)

            if state.is_goal():
                time_taken = time() - start_time
                if visual_output:
                    from visualizer.tree_drawer import tree_drawer as _tree_drawer
                    drawer = _tree_drawer()
                    for input in visualizer_input_list:  # type: ignore
                        drawer.draw(input[0], input[1], None, title=input[2], out_file=input[3])  # type: ignore
                    drawer.draw(
                        explored.copy(),
                        frontier_view.copy(),
                        state,
                        title=f"step {counter} (goal)",
                        out_file=os.path.join(output_dir, f"{counter}.png"),
                    )  # type: ignore
                return self.result(
                    explored,
                    start,
                    state,
                    time_taken,
                    algorithm="A*",
                    heuristic=heuristic_label,
                    data_structure="Priority queue (min-heap via heapq) ordered by f=g+h + best_g dictionary",
                )

            for neighbor in state.neighbors:
                tentative_g = neighbor.cost
                prev_best = best_g.get(neighbor)
                if prev_best is None or tentative_g < prev_best:#node=NONE MEAN THAT WE DIDN'T ADD IT TO best_g YET SO IT DIDN'T HAVE VALUE
                    best_g[neighbor] = tentative_g              #tentative_g < prev_best CHECK THAT WE WILL ADD THE OPTIMAL COST OF THE NODE 
                    frontier.insert(neighbor)   #THE SORTING TECHNIC HER DEPEND ON __lt__ which depend on f=g+h in state.py 
                    frontier_view.add(neighbor)

            if visual_output:
                visualizer_input_list.append(
                    (
                        explored.copy(),
                        frontier_view.copy(),
                        f"step {counter}",
                        os.path.join(output_dir, f"{counter}.png"),
                    )
                )  # type: ignore
                counter += 1

        return self.result(
            explored,
            start,
            None,
            time() - start_time,
            algorithm="A*",
            heuristic=heuristic_label,
            data_structure="Priority queue (min-heap via heapq) ordered by f=g+h + best_g dictionary",
        )
   