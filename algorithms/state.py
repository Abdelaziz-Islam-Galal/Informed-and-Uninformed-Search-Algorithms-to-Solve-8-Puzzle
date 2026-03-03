from __future__ import annotations

from functools import total_ordering

from board import board_8_puzzle


@total_ordering  # to fill in the other comparison methods based on __lt__
class board_state:
    def __init__(
        self,
        board: board_8_puzzle,
        parent: board_state | None = None,
        heuristics: bool = False,
    ):
        self.board = board
        self.parent = parent
        self.level = 0 if parent is None else parent.level + 1

        if not heuristics:
            self.cost: int | None = self.level
        else:
            self.cost = None

        self._neighbors: list[board_state] | None = None

    @property
    def neighbors(self) -> list[board_state]:
        if self._neighbors is None:
            neighbors: list[board_state] = []
            for direction in ["up", "down", "left", "right"]:
                new_board = self.board.copy()
                if new_board.move_zero(direction):
                    neighbors.append(board_state(new_board, self))
            self._neighbors = neighbors
        return self._neighbors

    def is_goal(self) -> bool:
        return self.board.goal_test()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, board_state):
            return NotImplemented
        return tuple(self.board.board_list) == tuple(other.board.board_list)

    def __hash__(self) -> int:
        return hash(tuple(self.board.board_list))

    def __lt__(self, other: board_state) -> bool:
        """Defines the less-than comparison based on cost / level."""
        if not isinstance(other, board_state):
            raise TypeError("Comparison is only supported between board_state instances.")

        if self.cost is not None and other.cost is not None:
            return self.cost < other.cost
        return self.level < other.level
