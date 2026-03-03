from functools import total_ordering
from board import board_8_puzzle

@total_ordering  # to fill in the other comparison methods based on __lt__
class board_state:
    def __init__(
        self,
        board: board_8_puzzle,
        parent: board_state | None = None,
        Manhattan_heuristics: bool = False,
        eucledian_heuristics: bool = False
    ):
        self.board = board
        self.parent = parent
        self.cost = 0 if parent is None else parent.cost + 1 # cost = (level-1)
        self._neighbors: list[board_state] | None = None

        if not Manhattan_heuristics and not eucledian_heuristics:
            self.cost_f: int | None = self.cost 
        elif Manhattan_heuristics:
            self.cost_f = self.cost + self.manhattan_heuristic_quantity()
        elif eucledian_heuristics:
            self.cost_f = self.cost + self.eucledian_heuristic_quantity()

    @property
    def neighbors(self) -> list[board_state]: # find neighbours only once
        # error where each neighbour searches for its own neighbours is resolved using property
        # and by not calling the neighbors property in the constructor
        if self._neighbors is None:
            neighbors: list[board_state] = []
            for direction in ["up", "down", "left", "right"]:
                new_board = self.board.copy()
                if new_board.move_zero(direction):
                    neighbors.append(board_state(new_board, self))
            self._neighbors = neighbors

        return self._neighbors

    def manhattan_heuristic_quantity(self) -> int:
        pass

    def eucledian_heuristic_quantity(self) -> int:
        pass

    def is_goal(self) -> bool:
        return self.board.goal_test()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, board_state):
            raise TypeError("Comparison is only supported between board_state instances.")
        return tuple(self.board.board_list) == tuple(other.board.board_list)

    def __hash__(self) -> int:
        """Allows board_state instances to be used in sets and dictionaries like explored and priority queue."""
        return hash(tuple(self.board.board_list))

    def __lt__(self, other: board_state) -> bool:
        """Defines the less-than comparison based on cost / level."""
        if not isinstance(other, board_state):
            raise TypeError("Comparison is only supported between board_state instances.")

        if self.cost_f is not None and other.cost_f is not None:
            return self.cost_f < other.cost_f
        return self.cost < other.cost