from __future__ import annotations

from typing import Iterable
import importlib
import os

from board import board_8_puzzle
from algorithms.state import board_state


def save_search_report(
    *,
    explored: set[board_state],
    start_state: board_state,
    goal_state: board_state | None,
    time_taken: float,
    out_file: str = "report.pdf",
    algorithm: str = "",
    heuristic: str | None = None,
    data_structure: str = "",
    assumptions: list[str] | None = None,
    extra_work: list[str] | None = None,
) -> None:
    """Save a search report to .pdf or .txt, or print to stdout.

    Includes deliverables typically required in 8-puzzle assignments:
    - path to goal (traceable steps)
    - cost of path, nodes expanded, search depth, running time
    - data structures used + brief algorithm explanation + assumptions + extra work
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

    def _algorithm_explanation(algo: str, heuristic_name: str | None) -> str:
        algo_norm = _normalize_algo_name(algo)
        if algo_norm == "BFS":
            return (
                "BFS (Breadth-First Search) explores the state space level-by-level. "
                "It uses a FIFO queue for the frontier and a visited set to avoid repeats. "
                "For unit edge costs, BFS is complete and finds the shortest path."
            )
        if algo_norm in {"A*", "ASTAR", "A_STAR"}:
            h = (heuristic_name or "heuristic").strip()
            return (
                "A* orders the frontier by f(n)=g(n)+h(n), where g is the path cost so far and h is a heuristic estimate. "
                f"This run uses: {h}. With an admissible heuristic, A* is optimal and complete."
            )
        if algo_norm in {"DFS"}:
            return (
                "DFS (Depth-First Search) explores by going as deep as possible before backtracking. "
                "It uses a stack (LIFO). DFS is not optimal in general and may get deep without finding the shortest solution."
            )
        if algo_norm in {"IDS"}:
            return (
                "IDS (Iterative Deepening Search) runs depth-limited DFS repeatedly with increasing depth limits. "
                "It combines DFS space usage with BFS-like completeness on unit-cost edges."
            )
        return "Search algorithm run (no detailed description provided)."

    def _format_moves(path: list[board_state]) -> str:
        move_map = {"up": "U", "down": "D", "left": "L", "right": "R"}
        moves = [move_map.get(s.move, s.move) for s in path[1:]]
        moves = [m for m in moves if m]
        return " ".join(moves) if moves else "(none)"

    def _search_depth(states: Iterable[board_state]) -> int:
        levels = [s.level for s in states]
        return max(levels, default=0)

    def _build_report_text() -> tuple[str, list[board_state], dict[str, str]]:
        heuristic_clean = (heuristic or "").strip() or None

        nodes_expanded = len(explored)
        search_depth = _search_depth(explored)

        summary: dict[str, str] = {
            "Algorithm": algorithm or "(unspecified)",
            "Heuristic": heuristic_clean or "N/A",
            "Nodes expanded": str(nodes_expanded),
            "Search depth": str(search_depth),
            "Running time": f"{time_taken:.4f} seconds",
            "Data structures": data_structure or "(not specified)",
        }

        lines: list[str] = []
        lines.append("8-Puzzle Search Report")
        lines.append("=" * 26)
        for k, v in summary.items():
            lines.append(f"{k}: {v}")
        lines.append("")
        lines.append("Initial state:")
        lines.append(str(start_state.board))
        lines.append("")
        lines.append("Goal state:")
        lines.append(str(board_8_puzzle()))
        lines.append("")
        lines.append("Algorithm explanation:")
        lines.append(_algorithm_explanation(algorithm, heuristic_clean))
        lines.append("")

        final_assumptions = assumptions or _default_assumptions()
        lines.append("Assumptions:")
        for a in final_assumptions:
            lines.append(f"- {a}")
        lines.append("")

        final_extras = extra_work or _default_extra_work()
        lines.append("Extra work:")
        for e in final_extras:
            lines.append(f"- {e}")
        lines.append("")

        if not goal_state:
            lines.append("Result: No solution found.")
            return "\n".join(lines) + "\n", [], summary

        goal_path = goal_state.get_path()
        cost_of_path = goal_state.level
        summary["Cost of path"] = str(cost_of_path)
        summary["Path to goal (moves)"] = _format_moves(goal_path)

        lines.append("Result:")
        lines.append(f"- Cost of path: {cost_of_path}")
        lines.append(f"- Path to goal (moves): {summary['Path to goal (moves)']}")
        lines.append("")
        lines.append("Trace (path to solution):")
        lines.append("")

        move_map = {"up": "U", "down": "D", "left": "L", "right": "R"}
        for step, state in enumerate(goal_path):
            move_txt = "START" if step == 0 else (state.move or "")
            move_short = "START" if step == 0 else (move_map.get(move_txt, move_txt) or "")
            f_txt = f" | f={state.cost_f:.3f}" if state.cost_f is not None else ""
            lines.append(f"Step {step}: move={move_short} | g={state.level}{f_txt}")
            lines.append(str(state.board))
            lines.append("")

        return "\n".join(lines) + "\n", goal_path, summary

    def _ensure_parent_dir(path: str) -> None:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)

    def _draw_board(ax, matrix: list[list[int]], title: str) -> None:
        ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
        ax.set_xlim(0, 3)
        ax.set_ylim(0, 3)
        ax.set_aspect("equal")
        ax.axis("off")

        for i in range(4):
            ax.plot([0, 3], [i, i], color="black", linewidth=1)
            ax.plot([i, i], [0, 3], color="black", linewidth=1)

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

    def _save_pdf(path: str, goal_path: list[board_state], summary: dict[str, str]) -> None:
        try:
            plt = importlib.import_module("matplotlib.pyplot")
            PdfPages = importlib.import_module("matplotlib.backends.backend_pdf").PdfPages
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "matplotlib is required to generate PDF reports. "
                "Install it in your venv using: .venv/Scripts/python.exe -m pip install matplotlib"
            ) from exc

        _ensure_parent_dir(path)

        with PdfPages(path) as pdf:
            # Summary page
            fig = plt.figure(figsize=(8.27, 11.69))  # A4
            fig.suptitle("8-Puzzle Search Report", fontsize=16, fontweight="bold", y=0.985)

            summary_lines = [f"{k}: {v}" for k, v in summary.items()]
            fig.text(0.06, 0.93, "\n".join(summary_lines), fontsize=11, family="monospace", va="top")

            ax_init = fig.add_axes([0.58, 0.74, 0.36, 0.18])
            _draw_board(ax_init, start_state.board.board, "Initial")
            ax_goal = fig.add_axes([0.58, 0.53, 0.36, 0.18])
            _draw_board(ax_goal, board_8_puzzle().board, "Goal")

            explanation = _algorithm_explanation(algorithm, heuristic)
            final_assumptions = assumptions or _default_assumptions()
            final_extras = extra_work or _default_extra_work()
            bottom_lines: list[str] = []
            bottom_lines.append("Algorithm explanation:")
            bottom_lines.append(explanation)
            bottom_lines.append("")
            bottom_lines.append("Assumptions:")
            bottom_lines.extend([f"- {a}" for a in final_assumptions])
            bottom_lines.append("")
            bottom_lines.append("Extra work:")
            bottom_lines.extend([f"- {e}" for e in final_extras])
            fig.text(0.06, 0.48, "\n".join(bottom_lines), fontsize=10, family="monospace", va="top")

            pdf.savefig(fig)
            plt.close(fig)

            # Steps
            move_map = {"up": "U", "down": "D", "left": "L", "right": "R"}
            for step, state in enumerate(goal_path):
                move_txt = "START" if step == 0 else (state.move or "")
                move_short = "START" if step == 0 else (move_map.get(move_txt, move_txt) or "")

                fig = plt.figure(figsize=(8.27, 11.69))
                fig.suptitle(f"Step {step}  (move: {move_short})", fontsize=14, fontweight="bold", y=0.985)

                trace_lines = [f"g (cost so far): {state.level}"]
                if state.cost_f is not None:
                    trace_lines.append(f"f = g + h: {state.cost_f:.3f}")
                if heuristic:
                    trace_lines.append(f"Heuristic: {heuristic}")
                fig.text(0.06, 0.93, "\n".join(trace_lines), fontsize=11, family="monospace", va="top")

                ax = fig.add_axes([0.18, 0.35, 0.64, 0.5])
                _draw_board(ax, state.board.board, "")

                pdf.savefig(fig)
                plt.close(fig)

    report_text, goal_path, summary = _build_report_text()

    out_lower = (out_file or "").lower()
    if out_lower.endswith(".pdf"):
        _save_pdf(out_file, goal_path, summary)
        print(f"Saved PDF report to: {out_file}")
        return

    if out_lower.endswith(".txt"):
        _ensure_parent_dir(out_file)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"Saved text report to: {out_file}")
        return

    print(report_text)
