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

        self._heuristics = None
        if Manhattan_heuristics:
            self._heuristics = "manhattan"
        elif eucledian_heuristics:
            self._heuristics = "eucledian"

        if Manhattan_heuristics and eucledian_heuristics:
            raise ValueError("Cannot use both Manhattan and Eucledian heuristics at the same time.")

        if self._heuristics == "manhattan" or (self.parent and self.parent._heuristics == "manhattan"):
            self.cost_f = self.cost + self.manhattan_heuristic_quantity()
        elif self._heuristics == "eucledian" or (self.parent and self.parent._heuristics == "eucledian"):
            self.cost_f = self.cost + self.eucledian_heuristic_quantity()
        else:
            self.cost_f: int | None = self.cost

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

    def get_path(self) -> list['board_state']:
        """Traces back from goal to start via parent pointers."""
        path = []
        current = self
        while current is not None:
            path.append(current)
            current = current.parent
        return list(reversed(path))

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