"""Multi-algorithm PDF report generator for the 8-Puzzle project.

Generates a single combined PDF with:
  - Cover page (project title, start/goal boards, timestamp)
  - Comparison table across all algorithms
  - Per-algorithm detail pages (DS, explanation, stats, solution path)
  - Full-path pages for longer solutions
  - Closing page with assumptions and extra work

Backward-compatible ``save_search_report`` for single-algorithm use.
"""

from __future__ import annotations

from datetime import datetime
from typing import Iterable
import importlib
import os

from board import board_8_puzzle
from algorithms.state import board_state

# ─── colour palette ──────────────────────────────────────────────────────────
_CLR_PRIMARY   = "#1a237e"
_CLR_ACCENT    = "#00bcd4"
_CLR_TILE_BG   = "#e8eaf6"
_CLR_TILE_ZERO = "#ffffff"
_CLR_HEADER_BG = "#283593"
_CLR_ROW_EVEN  = "#f5f5f5"
_CLR_ROW_ODD   = "#ffffff"
_CLR_SUCCESS   = "#2e7d32"
_CLR_FAIL      = "#c62828"

# ─── algorithm metadata ──────────────────────────────────────────────────────
_ALGO_INFO: dict[str, dict[str, str]] = {
    "BFS": {
        "full_name": "Breadth-First Search (BFS)",
        "data_structure": "FIFO Queue (collections.deque) + visited set (hash set)",
        "explanation": (
            "BFS explores the search tree level-by-level, expanding every node "
            "at the current depth before moving deeper.  Because each move has "
            "unit cost, BFS is both complete and optimal — it always finds the "
            "shortest solution path.  The frontier is a FIFO queue; a hash-set "
            "tracks visited states for O(1) duplicate detection."
        ),
    },
    "DFS": {
        "full_name": "Depth-First Search (DFS)",
        "data_structure": "LIFO Stack (Python list) + visited set (hash set)",
        "explanation": (
            "DFS dives as deep as possible along each branch before back-tracking. "
            "It uses a stack (LIFO order).  DFS is memory-efficient but NOT optimal: "
            "it may find a very long path even when a short one exists.  A state-"
            "expansion limit prevents runaway execution."
        ),
    },
    "IDS": {
        "full_name": "Iterative Deepening Search (IDS)",
        "data_structure": "LIFO Stack (Python list) + visited set (per iteration)",
        "explanation": (
            "IDS runs depth-limited DFS repeatedly, increasing the depth limit by 1 "
            "each iteration.  It combines BFS's optimality/completeness with DFS's "
            "low memory usage.  The overhead of re-expansion is bounded by a constant "
            "factor for tree-like graphs."
        ),
    },
    "A*": {
        "full_name": "A* Search",
        "data_structure": (
            "Priority Queue (min-heap via heapq) ordered by f = g + h, "
            "plus best_g dictionary for stale-entry pruning"
        ),
        "explanation": (
            "A* expands the node with the lowest f(n) = g(n) + h(n), where g is the "
            "cost-so-far and h is an admissible heuristic estimate.  With an admissible "
            "and consistent heuristic A* is both optimal and complete.  A best_g "
            "dictionary prunes stale heap entries whose g-cost has already been improved."
        ),
    },
}


def _algo_key(name: str) -> str:
    return name.strip().upper().replace("_", "").replace("-", "").replace(" ", "")


def _get_algo_info(name: str, heuristic: str | None = None) -> dict[str, str]:
    key = _algo_key(name)
    if key in ("ASTAR", "A*"):
        key = "A*"
    base = _ALGO_INFO.get(key, {
        "full_name": name or "Search Algorithm",
        "data_structure": "(not specified)",
        "explanation": "Custom search algorithm.",
    })
    info = dict(base)
    if heuristic and key == "A*":
        info["full_name"] = f"A* Search ({heuristic})"
        info["explanation"] += f"  Heuristic used: {heuristic}."
    return info


def _format_moves(path: list[board_state]) -> str:
    move_map = {"up": "U", "down": "D", "left": "L", "right": "R"}
    moves = [move_map.get(s.move, s.move) for s in path[1:] if s.move]
    return " \u2192 ".join(moves) if moves else "(none)"

def _draw_board(ax, matrix: list[list[int]], *, title: str = "", fontsize: int = 20) -> None:
    patches_mod = importlib.import_module("matplotlib.patches")
    ax.set_xlim(-0.05, 3.05)
    ax.set_ylim(-0.05, 3.05)
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", color=_CLR_PRIMARY, pad=6)

    for r in range(3):
        for c in range(3):
            val = matrix[r][c]
            bg = _CLR_TILE_ZERO if val == 0 else _CLR_TILE_BG
            rect = patches_mod.FancyBboxPatch(
                (c + 0.04, 2.04 - r), 0.92, 0.92,
                boxstyle="round,pad=0.06",
                facecolor=bg, edgecolor=_CLR_PRIMARY, linewidth=1.5,
            )
            ax.add_patch(rect)
            txt = "" if val == 0 else str(val)
            ax.text(
                c + 0.5, 2.5 - r, txt,
                ha="center", va="center",
                fontsize=fontsize, fontweight="bold",
                color=_CLR_PRIMARY, family="monospace",
            )


def save_search_report(
    explored: set[board_state],
    start_state: board_state,
    goal_state: board_state | None,
    time_taken: float,
    max_depth: int,
    out_file: str = "report.pdf",
    algorithm: str = "",
    heuristic: str | None = None,
    data_structure: str = "",
    assumptions: list[str] | None = None,
    extra_work: list[str] | None = None,
) -> None:
    """Save a single-algorithm report (wraps generate_full_report)."""
    from algorithms.algorithms import algorithms as _alg

    res = _alg.result(
        explored=explored,
        start_state=start_state,
        goal_state=goal_state,
        time_taken=time_taken,
        max_depth=max_depth,
        algorithm=algorithm,
        heuristic=heuristic,
        data_structure=data_structure,
        assumptions=assumptions,
        extra_work=extra_work,
    )
    generate_full_report(
        results={algorithm or "single": res},
        start_board=start_state.board,
        out_file=out_file,
    )


def generate_full_report(
    *,
    results: dict[str, object],        # key = label, value = algorithms.result
    start_board: board_8_puzzle,
    out_file: str = "report.pdf",
    assumptions: list[str] | None = None,
    extra_work: list[str] | None = None,
) -> None:
    """Generate a polished multi-algorithm PDF (or .txt fallback).

    Deletes *out_file* first so each run starts fresh.
    """
    if os.path.isfile(out_file):
        os.remove(out_file)

    final_assumptions = assumptions or [
        "The board is a standard 3\u00d73 8-puzzle with exactly one blank tile (0).",
        "The goal state is the canonical ordering: 0 1 2 / 3 4 5 / 6 7 8.",
        "If the initial state is unsolvable (wrong parity), no algorithm will find a path.",
        "Shuffle-based sample runs always generate solvable instances (random moves from goal).",
        "A state-expansion limit (LIMIT_STATES) prevents runaway execution for DFS/BFS.",
    ]
    final_extras = extra_work or [
        "Traceable step-by-step path with directional move labels (U / D / L / R).",
        "Interactive tkinter GUI with algorithm picker, speed slider, and live statistics.",
        "Per-algorithm search-tree PNG visualization stored in output/<algorithm>/.",
        "Combined PDF report with cover page, comparison table, and per-algorithm details.",
    ]

    if out_file.lower().endswith(".pdf"):
        _generate_pdf(results, start_board, out_file, final_assumptions, final_extras)
        print(f"\u2713 PDF report saved to: {out_file}")
    elif out_file.lower().endswith(".txt"):
        _generate_txt(results, start_board, out_file, final_assumptions, final_extras)
        print(f"\u2713 Text report saved to: {out_file}")
    else:
        print(_build_txt(results, start_board, final_assumptions, final_extras))


def _build_txt(results, start_board, assumptions, extras) -> str:
    lines: list[str] = []
    lines.append("=" * 70)
    lines.append("   8-PUZZLE SEARCH REPORT")
    lines.append(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)
    lines.append("")
    lines.append("Initial state:")
    lines.append(str(start_board))
    lines.append("")
    lines.append("Goal state:")
    lines.append(str(board_8_puzzle()))
    lines.append("")

    for label, res in results.items():
        info = _get_algo_info(res.algorithm, res.heuristic)
        lines.append("-" * 70)
        lines.append(f"  {info['full_name']}")
        lines.append("-" * 70)
        solved = res.goal_state is not None
        cost = res.goal_state.level if res.goal_state else "N/A"
        lines.append(f"  Solved:          {'Yes' if solved else 'No'}")
        lines.append(f"  Expanded nodes:  {len(res.explored)}")
        lines.append(f"  Cost of path:    {cost}")
        lines.append(f"  Search depth:    {res.max_depth}")
        lines.append(f"  Running time:    {res.time_taken:.4f} sec")
        lines.append(f"  Data structure:  {res.data_structure or info['data_structure']}")
        lines.append("")
        lines.append(f"  Explanation: {info['explanation']}")
        lines.append("")

        if res.goal_state:
            path = res.goal_state.get_path()
            lines.append(f"  Moves: {_format_moves(path)}")
            lines.append("")
            move_map = {"up": "U", "down": "D", "left": "L", "right": "R"}
            for step, state in enumerate(path):
                mv = "START" if step == 0 else move_map.get(state.move, state.move or "?")
                lines.append(f"  Step {step} [{mv}]  g={state.level}")
                for row in state.board.board:
                    lines.append("    " + " ".join(str(c) for c in row))
                lines.append("")

    lines.extend(_build_astar_heuristic_comparison_txt(results))

    lines.append("=" * 70)
    lines.append("ASSUMPTIONS")
    for a in assumptions:
        lines.append(f"  \u2022 {a}")
    lines.append("")
    lines.append("EXTRA WORK")
    for e in extras:
        lines.append(f"  \u2022 {e}")
    lines.append("=" * 70)
    return "\n".join(lines) + "\n"


def _generate_txt(results, start_board, out_file, assumptions, extras) -> None:
    parent = os.path.dirname(out_file)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(_build_txt(results, start_board, assumptions, extras))


def _generate_pdf(results, start_board, out_file, assumptions, extras) -> None:
    try:
        plt = importlib.import_module("matplotlib.pyplot")
        PdfPages = importlib.import_module("matplotlib.backends.backend_pdf").PdfPages
        patches_mod = importlib.import_module("matplotlib.patches")
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "matplotlib is required to generate PDF reports.  "
            "Install with: pip install matplotlib"
        ) from exc

    parent = os.path.dirname(out_file)
    if parent:
        os.makedirs(parent, exist_ok=True)

    W, H = 8.27, 11.69  # A4

    with PdfPages(out_file) as pdf:
        # PAGE 1: COVER 
        fig = plt.figure(figsize=(W, H), facecolor="white")

        fig.text(
            0.5, 0.88, "8-Puzzle Search Report",
            ha="center", va="top",
            fontsize=28, fontweight="bold", color=_CLR_PRIMARY,
        )
        fig.text(
            0.5, 0.835, "Informed & Uninformed Search Algorithms",
            ha="center", va="top", fontsize=14, color="#546e7a",
        )
        fig.text(
            0.5, 0.805,
            f"Generated: {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}",
            ha="center", va="top", fontsize=10, color="#90a4ae",
        )

        line_ax = fig.add_axes([0.1, 0.785, 0.8, 0.005])
        line_ax.axhline(0.5, color=_CLR_ACCENT, linewidth=3)
        line_ax.axis("off")

        ax_start = fig.add_axes([0.12, 0.52, 0.32, 0.24])
        _draw_board(ax_start, start_board.board, title="Initial State")
        ax_goal = fig.add_axes([0.56, 0.52, 0.32, 0.24])
        _draw_board(ax_goal, board_8_puzzle().board, title="Goal State")

        algo_list = [
            _get_algo_info(r.algorithm, r.heuristic)["full_name"]
            for r in results.values()
        ]
        fig.text(
            0.5, 0.46, "Algorithms compared:",
            ha="center", fontsize=13, fontweight="bold", color=_CLR_PRIMARY,
        )
        fig.text(
            0.5, 0.435, "   \u2022   ".join(algo_list),
            ha="center", fontsize=10, color="#37474f", wrap=True,
        )
        pdf.savefig(fig); plt.close(fig)

        # PAGE 2: COMPARISON TABLE
        fig = plt.figure(figsize=(W, H), facecolor="white")
        fig.text(
            0.5, 0.94, "Algorithm Comparison",
            ha="center", fontsize=22, fontweight="bold", color=_CLR_PRIMARY,
        )

        headers = ["Algorithm", "Solved", "Expanded", "Cost", "Depth", "Time (s)"]
        rows = []
        for res in results.values():
            info = _get_algo_info(res.algorithm, res.heuristic)
            solved = res.goal_state is not None
            cost = res.goal_state.level if res.goal_state else "\u2014"
            rows.append([
                info["full_name"],
                "\u2713" if solved else "\u2717",
                str(len(res.explored)),
                str(cost),
                str(res.max_depth),
                f"{res.time_taken:.4f}",
            ])

        ax_table = fig.add_axes([0.05, 0.15, 0.9, 0.72])
        ax_table.axis("off")
        table = ax_table.table(
            cellText=rows, colLabels=headers,
            loc="upper center", cellLoc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.2)

        for j in range(len(headers)):
            cell = table[0, j]
            cell.set_facecolor(_CLR_HEADER_BG)
            cell.set_text_props(color="white", fontweight="bold")
            cell.set_edgecolor("white")

        for i in range(len(rows)):
            for j in range(len(headers)):
                cell = table[i + 1, j]
                cell.set_facecolor(_CLR_ROW_EVEN if i % 2 == 0 else _CLR_ROW_ODD)
                cell.set_edgecolor("#e0e0e0")
                if j == 1:
                    cell.set_text_props(
                        color=_CLR_SUCCESS if rows[i][1] == "\u2713" else _CLR_FAIL,
                        fontweight="bold",
                    )

        # Optional note under the table: A* heuristic comparison (Manhattan vs Euclidean)
        man, euc = _find_astar_heuristic_results(results)
        if man is not None and euc is not None:
            man_exp = len(getattr(man, "explored", []))
            euc_exp = len(getattr(euc, "explored", []))
            man_cost = getattr(getattr(man, "goal_state", None), "level", "N/A")
            euc_cost = getattr(getattr(euc, "goal_state", None), "level", "N/A")
            note = (
                "A* heuristics: Manhattan vs Euclidean.  "
                f"Expanded: {man_exp} vs {euc_exp}.  Cost: {man_cost} vs {euc_cost}.\n"
                "Admissibility: both are admissible (sum of per-tile distances, blank ignored).  "
                "Manhattan dominates Euclidean (L1 \u2265 L2), so it is more informed and typically expands fewer nodes."
            )
            fig.text(0.05, 0.06, note, fontsize=9, color="#37474f", va="bottom", wrap=True)

        pdf.savefig(fig); plt.close(fig)

        # PER-ALGORITHM DETAIL PAGES
        move_map = {"up": "U", "down": "D", "left": "L", "right": "R"}

        for res in results.values():
            info = _get_algo_info(res.algorithm, res.heuristic)
            solved = res.goal_state is not None

            fig = plt.figure(figsize=(W, H), facecolor="white")

            # Title bar
            title_ax = fig.add_axes([0, 0.92, 1, 0.06])
            title_ax.set_xlim(0, 1); title_ax.set_ylim(0, 1)
            title_ax.add_patch(patches_mod.Rectangle((0, 0), 1, 1, facecolor=_CLR_PRIMARY))
            title_ax.text(
                0.5, 0.5, info["full_name"],
                ha="center", va="center",
                fontsize=18, fontweight="bold", color="white",
            )
            title_ax.axis("off")

            # Statistics block
            ds = res.data_structure or info["data_structure"]
            cost = res.goal_state.level if res.goal_state else "N/A"
            status_txt = "SOLVED \u2713" if solved else "NOT SOLVED \u2717"

            stats = [
                f"Status:          {status_txt}",
                f"Expanded nodes:  {len(res.explored)}",
                f"Cost of path:    {cost}",
                f"Search depth:    {res.max_depth}",
                f"Running time:    {res.time_taken:.4f} sec",
                "",
                f"Data structure:  {ds}",
            ]
            fig.text(
                0.06, 0.88, "\n".join(stats),
                fontsize=10, family="monospace", va="top", color="#212121",
            )

            # Explanation
            fig.text(
                0.06, 0.62, "How it works:",
                fontsize=12, fontweight="bold", color=_CLR_PRIMARY, va="top",
            )
            fig.text(
                0.06, 0.595, info["explanation"],
                fontsize=9.5, va="top", wrap=True, color="#37474f",
            )

            # Solution path
            if solved:
                path = res.goal_state.get_path()
                fig.text(
                    0.06, 0.50,
                    f"Solution moves:  {_format_moves(path)}",
                    fontsize=10, family="monospace", va="top", color=_CLR_PRIMARY,
                )
                # Inline boards (up to 8)
                max_inline = min(len(path), 8)
                bw, bh = 0.105, 0.105
                start_x, y_pos = 0.04, 0.28
                for idx in range(max_inline):
                    st = path[idx]
                    x = start_x + idx * (bw + 0.012)
                    ax = fig.add_axes([x, y_pos, bw, bh])
                    mv = "S" if idx == 0 else move_map.get(st.move, "?")
                    _draw_board(ax, st.board.board, title=mv, fontsize=12)
                if len(path) > max_inline:
                    fig.text(
                        start_x + max_inline * (bw + 0.012),
                        y_pos + bh / 2,
                        f"\u2026 +{len(path) - max_inline} more",
                        fontsize=9, color="#78909c", va="center",
                    )
            else:
                fig.text(
                    0.06, 0.50,
                    "No solution found within the expansion limit.",
                    fontsize=11, color=_CLR_FAIL, va="top",
                )

            pdf.savefig(fig); plt.close(fig)

            # Full-path continuation pages for long solutions
            if solved:
                path = res.goal_state.get_path()
                if len(path) > 8:
                    _render_full_path_pages(pdf, plt, patches_mod, path, info["full_name"])

        # CLOSING PAGE: ASSUMPTIONS & EXTRA WORK
        fig = plt.figure(figsize=(W, H), facecolor="white")
        fig.text(
            0.5, 0.92, "Assumptions & Extra Work",
            ha="center", fontsize=22, fontweight="bold", color=_CLR_PRIMARY,
        )
        line_ax = fig.add_axes([0.1, 0.905, 0.8, 0.004])
        line_ax.axhline(0.5, color=_CLR_ACCENT, linewidth=2)
        line_ax.axis("off")

        y = 0.86
        fig.text(0.08, y, "Assumptions:", fontsize=14, fontweight="bold", color=_CLR_PRIMARY)
        y -= 0.03
        for a in assumptions:
            fig.text(0.10, y, f"\u2022  {a}", fontsize=10, color="#37474f", va="top", wrap=True)
            y -= 0.035
        y -= 0.02
        fig.text(0.08, y, "Extra Work:", fontsize=14, fontweight="bold", color=_CLR_PRIMARY)
        y -= 0.03
        for e in extras:
            fig.text(0.10, y, f"\u2022  {e}", fontsize=10, color="#37474f", va="top", wrap=True)
            y -= 0.035

        pdf.savefig(fig); plt.close(fig)


def _render_full_path_pages(pdf, plt, patches_mod, path, algo_name):
    """Extra pages that show every step of long solutions in a grid."""
    W, H = 8.27, 11.69
    cols, rows_per_page = 4, 5
    per_page = cols * rows_per_page
    move_map = {"up": "U", "down": "D", "left": "L", "right": "R"}

    for page_start in range(0, len(path), per_page):
        chunk = path[page_start:page_start + per_page]
        fig = plt.figure(figsize=(W, H), facecolor="white")

        title_ax = fig.add_axes([0, 0.95, 1, 0.04])
        title_ax.set_xlim(0, 1); title_ax.set_ylim(0, 1)
        title_ax.add_patch(patches_mod.Rectangle((0, 0), 1, 1, facecolor=_CLR_PRIMARY))
        title_ax.text(
            0.5, 0.5,
            f"{algo_name} \u2014 Full Path (steps {page_start}\u2013{page_start + len(chunk) - 1})",
            ha="center", va="center",
            fontsize=13, fontweight="bold", color="white",
        )
        title_ax.axis("off")

        bw, bh = 0.18, 0.14
        x_start, y_start = 0.06, 0.78

        for idx, state in enumerate(chunk):
            r_idx, c_idx = divmod(idx, cols)
            x = x_start + c_idx * (bw + 0.04)
            y = y_start - r_idx * (bh + 0.04)
            step_num = page_start + idx
            mv = "START" if step_num == 0 else move_map.get(state.move, state.move or "?")
            ax = fig.add_axes([x, y, bw, bh])
            _draw_board(ax, state.board.board, title=f"Step {step_num} [{mv}]", fontsize=13)

        pdf.savefig(fig); plt.close(fig)
