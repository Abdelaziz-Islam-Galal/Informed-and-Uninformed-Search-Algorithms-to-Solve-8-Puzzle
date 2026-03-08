from __future__ import annotations

from functools import total_ordering
import math

from board import board_8_puzzle

@total_ordering  # to fill in the other comparison methods based on __lt__
class board_state:
    def __init__(
        self,
        board: board_8_puzzle,
        parent: board_state | None = None,
        move: str | None = None,
        Manhattan_heuristics: bool = False,
        eucledian_heuristics: bool = False,
    ):
        self.board = board
        self.parent = parent
        # The action taken from parent -> this state (e.g., 'up', 'down', 'left', 'right')
        self.move = move
        self.cost = 0 if parent is None else parent.cost + 1 # cost = (level-1)
        self._neighbors: list[board_state] | None = None

        if Manhattan_heuristics and eucledian_heuristics:
            raise ValueError("Cannot use both Manhattan and Eucledian heuristics at the same time.")

        self._heuristics: str | None = None
        if Manhattan_heuristics:
            self._heuristics = "manhattan"
        elif eucledian_heuristics:
            self._heuristics = "eucledian"
        elif parent is not None and parent._heuristics is not None:
            self._heuristics = parent._heuristics

        if self._heuristics == "manhattan":
            self.cost_f: float | None = self.cost + self.manhattan_heuristic_quantity()
        elif self._heuristics == "eucledian":
            self.cost_f = self.cost + self.eucledian_heuristic_quantity()
        else:
            self.cost_f = None

    @property
    def neighbors(self) -> list[board_state]: # find neighbours only once
        # error where each neighbour searches for its own neighbours is resolved using property
        # and by not calling the neighbors property in the constructor
        if self._neighbors is None:
            neighbors: list[board_state] = []
            for direction in ["up", "down", "left", "right"]:
                new_board = self.board.copy()
                if new_board.move_zero(direction):
                    neighbors.append(board_state(new_board, self, move=direction))
            self._neighbors = neighbors

        return self._neighbors

    def manhattan_heuristic_quantity(self) -> int:
        total = 0
        for index, value in enumerate(self.board.board_list):
            if value == 0:
                continue
            row, col = divmod(index, 3)
            goal_row, goal_col = divmod(value, 3)
            total += abs(row - goal_row) + abs(col - goal_col)
        return total

    def eucledian_heuristic_quantity(self) -> float:
        total = 0.0
        for index, value in enumerate(self.board.board_list):
            if value == 0:
                continue
            row, col = divmod(index, 3)
            goal_row, goal_col = divmod(value, 3)
            total += math.sqrt((row - goal_row) ** 2 + (col - goal_col) ** 2)
        return total

    def get_path(self) -> list['board_state']:
        """Traces back from goal to start via parent pointers."""
        path = []
        current = self
        while current is not None:
            path.append(current)
            current = current.parent
        return list(reversed(path))
    
    @property
    def board_list(self):
        return self.board.board_list
    
    @property
    def level(self):
        return self.cost

    def is_goal(self) -> bool:
        return self.board.goal_test()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, board_state):
            return NotImplemented
        return self.board == other.board

    def __hash__(self) -> int:
        """Allows board_state instances to be used in sets and dictionaries like explored and priority queue."""
        return hash(self.board)

    def __lt__(self, other: board_state) -> bool:
        """Defines the less-than comparison based on cost / level."""
        if not isinstance(other, board_state):
            raise TypeError("Comparison is only supported between board_state instances.")

        if self.cost_f is not None and other.cost_f is not None:
            return self.cost_f < other.cost_f
        return self.cost < other.cost