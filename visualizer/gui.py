"""
8-Puzzle Solver - Interactive GUI
==================================
Run:  python gui.py

Features
--------
* Smooth animated tile sliding (configurable speed)
* Algorithm picker: BFS · DFS · IDS · A* Manhattan · A* Euclidean
* Shuffle with adjustable difficulty (slider)
* Manual tile input (click "Edit" to type any solvable board)
* Auto-play / step-by-step navigation (◀ ▶)
* Live statistics panel (expanded nodes, cost, search depth, time, path moves)
* Modern dark theme with colour-coded tiles and glow effects
* Goal-state celebration animation (green flash)
"""

from __future__ import annotations

import os, sys
# Ensure the project root is on sys.path so "board" / "algorithms" imports work
# when this file is executed directly (python visualizer/gui.py).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import threading
import tkinter as tk
from tkinter import messagebox
from typing import Callable

from board import board_8_puzzle
from algorithms.algorithms import algorithms

# ─── palette ────────────────────────────────────────────────────────────────────
BG           = "#1e1e2e"
PANEL_BG     = "#2a2a3c"
TILE_COLORS  = {
    1: "#f38ba8", 2: "#fab387", 3: "#f9e2af",
    4: "#a6e3a1", 5: "#89dceb", 6: "#74c7ec",
    7: "#cba6f7", 8: "#f5c2e7",
}
TILE_TEXT     = "#1e1e2e"
EMPTY_COLOR   = "#313244"
GOAL_FLASH    = "#a6e3a1"
BTN_BG        = "#45475a"
BTN_FG        = "#cdd6f4"
BTN_ACTIVE    = "#585b70"
ACCENT        = "#89b4fa"
LABEL_FG      = "#cdd6f4"
STAT_VAL      = "#f9e2af"
BORDER_COLOR  = "#585b70"

TILE_SIZE     = 120
GAP           = 6
BOARD_PAD     = 24
ANIM_STEPS    = 12          # frames per tile slide
ANIM_MS       = 14          # ms per animation frame
AUTOPLAY_BASE = 500         # ms between auto-play steps (modified by speed slider)

FONT_TILE     = ("Segoe UI", 36, "bold")
FONT_BTN      = ("Segoe UI", 11)
FONT_LABEL    = ("Segoe UI", 10)
FONT_STAT_VAL = ("Segoe UI", 12, "bold")
FONT_TITLE    = ("Segoe UI", 18, "bold")
FONT_SMALL    = ("Segoe UI", 9)


# ─── helper: move string ────────────────────────────────────────────────────────
_MOVE_MAP = {"up": "U", "down": "D", "left": "L", "right": "R"}


def _path_moves(result: algorithms.result) -> list[str]:
    if not result.goal_state:
        return []
    path = result.goal_state.get_path()
    return [_MOVE_MAP.get(s.move, "?") for s in path[1:] if s.move]


def _path_boards(result: algorithms.result) -> list[list[list[int]]]:
    if not result.goal_state:
        return []
    return [
        [row[:] for row in s.board.board]
        for s in result.goal_state.get_path()
    ]


# ─── main window ────────────────────────────────────────────────────────────────
class PuzzleGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("8-Puzzle Solver")
        self.configure(bg=BG)
        self.resizable(False, False)

        # state
        self._board = board_8_puzzle([[1, 2, 5], [3, 4, 0], [6, 7, 8]])
        self._path_boards: list[list[list[int]]] = []
        self._path_moves: list[str] = []
        self._step_idx = 0
        self._animating = False
        self._autoplay_id: str | None = None
        self._solving = False

        self._build_ui()
        self._draw_board(self._board.board)

    # ── UI construction ──────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        # — title bar —
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=16, pady=(14, 4))
        tk.Label(top, text="8-Puzzle Solver", font=FONT_TITLE, bg=BG, fg=ACCENT).pack(side="left")

        # — main layout: canvas | right panel —
        body = tk.Frame(self, bg=BG)
        body.pack(padx=16, pady=8)

        # canvas
        board_w = 3 * TILE_SIZE + 4 * GAP + 2 * BOARD_PAD
        board_h = board_w
        self._canvas = tk.Canvas(
            body, width=board_w, height=board_h,
            bg=EMPTY_COLOR, highlightthickness=2, highlightbackground=BORDER_COLOR,
        )
        self._canvas.grid(row=0, column=0, padx=(0, 14))

        # right panel
        rp = tk.Frame(body, bg=PANEL_BG, width=280, relief="flat", bd=0)
        rp.grid(row=0, column=1, sticky="ns")
        rp.grid_propagate(False)
        rp.configure(width=280)

        # ─ algorithm selector ─
        self._add_section(rp, "Algorithm")
        self._algo_var = tk.StringVar(value="A* Manhattan")
        algos = ["BFS", "DFS", "IDS", "A* Manhattan", "A* Euclidean"]
        for a in algos:
            rb = tk.Radiobutton(
                rp, text=a, variable=self._algo_var, value=a,
                bg=PANEL_BG, fg=LABEL_FG, selectcolor=BTN_BG,
                activebackground=PANEL_BG, activeforeground=LABEL_FG,
                font=FONT_LABEL, anchor="w",
            )
            rb.pack(fill="x", padx=18, pady=1)

        # ─ shuffle controls ─
        self._add_section(rp, "Shuffle")

        sf = tk.Frame(rp, bg=PANEL_BG)
        sf.pack(fill="x", padx=18, pady=2)
        tk.Label(sf, text="Moves:", bg=PANEL_BG, fg=LABEL_FG, font=FONT_LABEL).pack(side="left")
        self._shuffle_var = tk.IntVar(value=20)
        self._shuffle_scale = tk.Scale(
            sf, from_=5, to=200, orient="horizontal", variable=self._shuffle_var,
            bg=PANEL_BG, fg=LABEL_FG, troughcolor=BTN_BG, highlightthickness=0,
            font=FONT_SMALL, length=140,
        )
        self._shuffle_scale.pack(side="left", padx=4)

        bf = tk.Frame(rp, bg=PANEL_BG)
        bf.pack(fill="x", padx=18, pady=4)
        self._make_btn(bf, "Shuffle", self._on_shuffle).pack(side="left", expand=True, fill="x", padx=(0, 3))
        self._make_btn(bf, "Reset (Goal)", self._on_reset).pack(side="left", expand=True, fill="x", padx=(3, 0))

        # ─ custom board entry ─
        ef = tk.Frame(rp, bg=PANEL_BG)
        ef.pack(fill="x", padx=18, pady=4)
        self._entry_var = tk.StringVar(value="1 2 5 3 4 0 6 7 8")
        tk.Entry(
            ef, textvariable=self._entry_var, font=FONT_LABEL,
            bg=BTN_BG, fg=LABEL_FG, insertbackground=LABEL_FG, width=20, relief="flat",
        ).pack(side="left", expand=True, fill="x", padx=(0, 4))
        self._make_btn(ef, "Set", self._on_set_board).pack(side="left")

        # ─ solve button ─
        self._add_section(rp, "Solve")
        self._solve_btn = self._make_btn(rp, "▶  Solve", self._on_solve, wide=True)
        self._solve_btn.pack(fill="x", padx=18, pady=4)

        # ─ playback ─
        self._add_section(rp, "Playback")
        pf = tk.Frame(rp, bg=PANEL_BG)
        pf.pack(fill="x", padx=18, pady=2)
        self._prev_btn = self._make_btn(pf, "◀", self._on_prev)
        self._prev_btn.pack(side="left", expand=True, fill="x", padx=(0, 2))
        self._auto_btn = self._make_btn(pf, "Auto ▶", self._on_autoplay)
        self._auto_btn.pack(side="left", expand=True, fill="x", padx=2)
        self._next_btn = self._make_btn(pf, "▶", self._on_next)
        self._next_btn.pack(side="left", expand=True, fill="x", padx=(2, 0))

        spf = tk.Frame(rp, bg=PANEL_BG)
        spf.pack(fill="x", padx=18, pady=2)
        tk.Label(spf, text="Speed:", bg=PANEL_BG, fg=LABEL_FG, font=FONT_LABEL).pack(side="left")
        self._speed_var = tk.IntVar(value=3)
        tk.Scale(
            spf, from_=1, to=10, orient="horizontal", variable=self._speed_var,
            bg=PANEL_BG, fg=LABEL_FG, troughcolor=BTN_BG, highlightthickness=0,
            font=FONT_SMALL, length=140,
        ).pack(side="left", padx=4)

        self._step_label = tk.Label(rp, text="Step: - / -", font=FONT_LABEL, bg=PANEL_BG, fg=LABEL_FG)
        self._step_label.pack(padx=18, pady=2, anchor="w")

        # ─ statistics ─
        self._add_section(rp, "Statistics")
        self._stats: dict[str, tk.Label] = {}
        for key in ["Expanded", "Cost", "Search Depth", "Time", "Moves"]:
            row = tk.Frame(rp, bg=PANEL_BG)
            row.pack(fill="x", padx=18, pady=1)
            tk.Label(row, text=f"{key}:", font=FONT_LABEL, bg=PANEL_BG, fg=LABEL_FG).pack(side="left")
            val = tk.Label(row, text="-", font=FONT_STAT_VAL, bg=PANEL_BG, fg=STAT_VAL)
            val.pack(side="right")
            self._stats[key] = val

        # ─ status bar ─
        self._status = tk.Label(self, text="Ready", font=FONT_SMALL, bg=BG, fg=LABEL_FG, anchor="w")
        self._status.pack(fill="x", padx=16, pady=(0, 8))

    # ── helpers ──────────────────────────────────────────────────────────────
    @staticmethod
    def _add_section(parent: tk.Frame, title: str) -> None:
        tk.Label(
            parent, text=title.upper(), font=("Segoe UI", 9, "bold"),
            bg=PANEL_BG, fg=ACCENT, anchor="w",
        ).pack(fill="x", padx=18, pady=(10, 2))

    @staticmethod
    def _make_btn(parent: tk.Frame, text: str, cmd: Callable, *, wide: bool = False) -> tk.Button:
        return tk.Button(
            parent, text=text, command=cmd,
            bg=BTN_BG, fg=BTN_FG, activebackground=BTN_ACTIVE, activeforeground=BTN_FG,
            font=FONT_BTN, relief="flat", bd=0, padx=10, pady=4,
            cursor="hand2",
        )

    def _set_status(self, msg: str) -> None:
        self._status.config(text=msg)

    # ── drawing ──────────────────────────────────────────────────────────────
    def _draw_board(self, board: list[list[int]], *, goal_flash: bool = False) -> None:
        c = self._canvas
        c.delete("all")
        # background
        c.create_rectangle(0, 0, c.winfo_reqwidth(), c.winfo_reqheight(), fill=EMPTY_COLOR, outline="")
        for r in range(3):
            for col in range(3):
                val = board[r][col]
                x = BOARD_PAD + col * (TILE_SIZE + GAP) + GAP
                y = BOARD_PAD + r * (TILE_SIZE + GAP) + GAP
                if val == 0:
                    # subtle empty slot
                    c.create_rectangle(x, y, x + TILE_SIZE, y + TILE_SIZE,
                                       fill="#3b3b50", outline="#4a4a60", width=2)
                    continue
                color = GOAL_FLASH if goal_flash else TILE_COLORS.get(val, "#cdd6f4")
                # shadow
                c.create_rectangle(x + 3, y + 3, x + TILE_SIZE + 3, y + TILE_SIZE + 3,
                                   fill="#11111b", outline="")
                # tile
                c.create_rectangle(x, y, x + TILE_SIZE, y + TILE_SIZE,
                                   fill=color, outline=_darken(color), width=2)
                # number
                c.create_text(x + TILE_SIZE // 2, y + TILE_SIZE // 2,
                              text=str(val), font=FONT_TILE, fill=TILE_TEXT)

    def _animate_step(self, from_board: list[list[int]], to_board: list[list[int]], callback: Callable) -> None:
        """Animate the single tile that moved between two board states."""
        self._animating = True
        # find which tile moved
        moved_val = 0
        fr, fc, tr, tc = 0, 0, 0, 0
        for r in range(3):
            for col in range(3):
                if from_board[r][col] != to_board[r][col] and to_board[r][col] != 0:
                    moved_val = to_board[r][col]
                    tr, tc = r, col
                    # find where it was
                    for rr in range(3):
                        for cc in range(3):
                            if from_board[rr][cc] == moved_val:
                                fr, fc = rr, cc

        if moved_val == 0:
            self._animating = False
            callback()
            return

        # pixel coords
        def cell_xy(row: int, c: int) -> tuple[int, int]:
            return (
                BOARD_PAD + c * (TILE_SIZE + GAP) + GAP,
                BOARD_PAD + row * (TILE_SIZE + GAP) + GAP,
            )

        sx, sy = cell_xy(fr, fc)
        ex, ey = cell_xy(tr, tc)
        dx = (ex - sx) / ANIM_STEPS
        dy = (ey - sy) / ANIM_STEPS
        color = TILE_COLORS.get(moved_val, "#cdd6f4")

        # draw static board (with moved tile absent)
        temp = [row[:] for row in from_board]
        temp[fr][fc] = 0
        self._draw_board(temp)

        # create moving tile
        shadow = self._canvas.create_rectangle(
            sx + 3, sy + 3, sx + TILE_SIZE + 3, sy + TILE_SIZE + 3,
            fill="#11111b", outline="",
        )
        rect = self._canvas.create_rectangle(
            sx, sy, sx + TILE_SIZE, sy + TILE_SIZE,
            fill=color, outline=_darken(color), width=2,
        )
        txt = self._canvas.create_text(
            sx + TILE_SIZE // 2, sy + TILE_SIZE // 2,
            text=str(moved_val), font=FONT_TILE, fill=TILE_TEXT,
        )

        step = [0]

        def _tick() -> None:
            step[0] += 1
            self._canvas.move(shadow, dx, dy)
            self._canvas.move(rect, dx, dy)
            self._canvas.move(txt, dx, dy)
            if step[0] < ANIM_STEPS:
                self.after(ANIM_MS, _tick)
            else:
                self._animating = False
                self._draw_board(to_board)
                callback()

        self.after(ANIM_MS, _tick)

    # ── goal celebration ─────────────────────────────────────────────────────
    def _flash_goal(self, board: list[list[int]], n: int = 4) -> None:
        if n <= 0:
            self._draw_board(board)
            return
        self._draw_board(board, goal_flash=(n % 2 == 1))
        self.after(180, lambda: self._flash_goal(board, n - 1))

    # ── controls ─────────────────────────────────────────────────────────────
    def _on_shuffle(self) -> None:
        self._stop_autoplay()
        self._board = board_8_puzzle()
        self._board.shuffle(self._shuffle_var.get())
        self._draw_board(self._board.board)
        self._entry_var.set(" ".join(str(v) for v in self._board.board_list))
        self._clear_solution()
        self._set_status(f"Shuffled ({self._shuffle_var.get()} moves)")

    def _on_reset(self) -> None:
        self._stop_autoplay()
        self._board = board_8_puzzle()
        self._draw_board(self._board.board)
        self._entry_var.set("0 1 2 3 4 5 6 7 8")
        self._clear_solution()
        self._set_status("Board reset to goal state")

    def _on_set_board(self) -> None:
        self._stop_autoplay()
        raw = self._entry_var.get().replace(",", " ").split()
        if len(raw) != 9:
            messagebox.showerror("Invalid input", "Enter exactly 9 numbers (0-8) separated by spaces.")
            return
        try:
            nums = [int(x) for x in raw]
        except ValueError:
            messagebox.showerror("Invalid input", "All values must be integers 0-8.")
            return
        if sorted(nums) != list(range(9)):
            messagebox.showerror("Invalid input", "Board must contain each number 0-8 exactly once.")
            return
        matrix = [nums[i:i+3] for i in range(0, 9, 3)]
        self._board = board_8_puzzle(matrix)
        self._draw_board(self._board.board)
        self._clear_solution()
        self._set_status("Custom board set")

    def _on_solve(self) -> None:
        if self._solving:
            return
        self._stop_autoplay()
        self._clear_solution()
        algo = self._algo_var.get()
        self._set_status(f"Solving with {algo}…")
        self._solve_btn.config(state="disabled", text="Solving…")
        self._solving = True

        # run in background thread so GUI stays responsive
        board_copy = self._board.copy()
        threading.Thread(target=self._solve_worker, args=(board_copy, algo), daemon=True).start()

    def _solve_worker(self, board: board_8_puzzle, algo: str) -> None:
        solver = algorithms(board)
        result: algorithms.result | None = None
        try:
            if algo == "BFS":
                result = solver.bfs(False)
            elif algo == "DFS":
                result = solver.dfs(False)
            elif algo == "IDS":
                result = solver.ids(False)
            elif algo == "A* Manhattan":
                result = solver.A_star(False, heuristic="manhattan")
            elif algo == "A* Euclidean":
                result = solver.A_star(False, heuristic="euclidean")
        except Exception as exc:
            self.after(0, lambda: self._solve_done(None, str(exc)))
            return
        self.after(0, lambda: self._solve_done(result, None))

    def _solve_done(self, result: algorithms.result | None, error: str | None) -> None:
        self._solving = False
        self._solve_btn.config(state="normal", text="▶  Solve")
        if error:
            messagebox.showerror("Error", error)
            self._set_status("Error")
            return
        if result is None or result.goal_state is None:
            messagebox.showwarning("No solution", "The algorithm could not find a solution within the state limit.")
            self._set_status("No solution found")
            self._update_stats(result)
            return

        self._path_boards = _path_boards(result)
        self._path_moves = _path_moves(result)
        self._step_idx = 0
        self._update_stats(result)
        self._update_step_label()
        self._draw_board(self._path_boards[0])
        self._set_status(f"Solved! Cost={result.goal_state.level}  Expanded={len(result.explored)}")

    def _update_stats(self, result: algorithms.result | None) -> None:
        if result is None:
            for v in self._stats.values():
                v.config(text="-")
            return
        self._stats["Expanded"].config(text=str(len(result.explored)))
        cost = result.goal_state.level if result.goal_state else "N/A"
        self._stats["Cost"].config(text=str(cost))
        depth = result.max_depth
        self._stats["Search Depth"].config(text=str(depth))
        self._stats["Time"].config(text=f"{result.time_taken:.4f} s")
        moves = " ".join(self._path_moves) if self._path_moves else "-"
        self._stats["Moves"].config(text=moves)

    def _clear_solution(self) -> None:
        self._path_boards = []
        self._path_moves = []
        self._step_idx = 0
        self._update_step_label()
        for v in self._stats.values():
            v.config(text="-")

    def _update_step_label(self) -> None:
        total = len(self._path_boards)
        if total == 0:
            self._step_label.config(text="Step: - / -")
        else:
            self._step_label.config(text=f"Step: {self._step_idx} / {total - 1}")

    # ── playback ─────────────────────────────────────────────────────────────
    def _on_next(self) -> None:
        if self._animating or not self._path_boards:
            return
        if self._step_idx < len(self._path_boards) - 1:
            prev = self._step_idx
            self._step_idx += 1
            self._update_step_label()
            self._animate_step(
                self._path_boards[prev],
                self._path_boards[self._step_idx],
                self._check_goal,
            )

    def _on_prev(self) -> None:
        if self._animating or not self._path_boards:
            return
        self._stop_autoplay()
        if self._step_idx > 0:
            self._step_idx -= 1
            self._update_step_label()
            self._draw_board(self._path_boards[self._step_idx])

    def _on_autoplay(self) -> None:
        if self._autoplay_id is not None:
            self._stop_autoplay()
            return
        if not self._path_boards:
            return
        self._auto_btn.config(text="⏸ Pause")
        self._autoplay_tick()

    def _autoplay_tick(self) -> None:
        if self._animating:
            self._autoplay_id = self.after(50, self._autoplay_tick)
            return
        if self._step_idx >= len(self._path_boards) - 1:
            self._stop_autoplay()
            return
        delay = max(80, AUTOPLAY_BASE - self._speed_var.get() * 45)
        self._on_next()
        self._autoplay_id = self.after(delay, self._autoplay_tick)

    def _stop_autoplay(self) -> None:
        if self._autoplay_id is not None:
            self.after_cancel(self._autoplay_id)
            self._autoplay_id = None
        self._auto_btn.config(text="Auto ▶")

    def _check_goal(self) -> None:
        if self._step_idx == len(self._path_boards) - 1:
            self._flash_goal(self._path_boards[-1])

    # ── keyboard shortcuts ───────────────────────────────────────────────────
    def _bind_keys(self) -> None:
        self.bind("<Right>", lambda e: self._on_next())
        self.bind("<Left>", lambda e: self._on_prev())
        self.bind("<space>", lambda e: self._on_autoplay())
        self.bind("<Return>", lambda e: self._on_solve())


# ─── colour utility ─────────────────────────────────────────────────────────────
def _darken(hex_color: str, factor: float = 0.75) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r, g, b = int(r * factor), int(g * factor), int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


# ─── entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = PuzzleGUI()
    app._bind_keys()
    app.mainloop()
