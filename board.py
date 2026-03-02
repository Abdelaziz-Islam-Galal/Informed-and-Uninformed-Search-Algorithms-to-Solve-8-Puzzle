from functools import total_ordering


class board_8_puzzle:
    def __init__(self, board: None|list[list[int]] = None):
        if board is not None:
            self.board = board
        else:
            self._board = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
            self._zero_position = (0, 0)

    def goal_test(self) -> bool:
        """
        Checks if the current board state is the goal state.
        """
        return self.board == [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    
    def move_zero(self, direction: str) -> bool:
        """
        Moves the zero tile up/down/left/right if possible.
        Returns True if the move was successful, False otherwise.
        """
        def swap(i1, j1, i2, j2):
            self.board[i1][j1], self.board[i2][j2] = self.board[i2][j2], self.board[i1][j1]
            self._zero_position = (i2, j2)

        zero_i, zero_j = self.zero_position
        if direction == "up" or direction == "w" and zero_i > 0:
            swap(zero_i, zero_j, zero_i - 1, zero_j)
        elif direction == "down" or direction == "s" and zero_i < 2:
            swap(zero_i, zero_j, zero_i + 1, zero_j)
        elif direction == "left" or direction == "a" and zero_j > 0:
            swap(zero_i, zero_j, zero_i, zero_j - 1)
        elif direction == "right" or direction == "d" and zero_j < 2:
            swap(zero_i, zero_j, zero_i, zero_j + 1)
        else:
            return False
        return True
    
    @property
    def board(self) -> list[list[int]]:
        return self._board
    
    @board.setter
    def board(self, new_board: list[list[int]]):
        """
        assigns a new board state and updates the zero position.
        """
        if len(new_board) != 3 or any(len(row) != 3 for row in new_board):
            raise ValueError("Board must be a 3x3 matrix.")
        
        flag = False
        for i in range(3):
            for j in range(3):
                if new_board[i][j] == 0:
                    self._zero_position = (i, j)
                    flag = True
        if not flag:
            raise ValueError("Board must contain a zero.")
        
        self._board = new_board

    @property
    def zero_position(self) -> tuple[int, int]:
        return self._zero_position
    
    @property
    def board_list(self) -> list[int]:
        return [cell for row in self.board for cell in row]

    def copy(self):
        return board_8_puzzle([row.copy() for row in self.board])

    def __str__(self):
        """
        prints:
            0 1 2
            3 4 5
            6 7 8
        """
        return "\n".join(" ".join(str(cell) for cell in row) for row in self.board)
    
@total_ordering # to fill in the other comparison methods based on __lt__
class state:
    def __init__(self, board: board_8_puzzle, parent: None|state = None, cost: None|int = None):
        self.board = board
        self.parent = parent
        self.cost = cost

        self._level = 0 if parent is None else parent.level + 1
    
        self._neighbors = []
        for direction in ["up", "down", "left", "right"]:
            new_board = board.copy()
            if new_board.move_zero(direction):
                self._neighbors.append(state(new_board, self, None))

    def is_goal(self) -> bool:
        if self.board.goal_test():
            return True
        return False

    @property
    def level(self) -> int:
        return self._level        

    @property
    def neighbors(self) -> list[state]:
        return self._neighbors
    
    # comparison for this class objects to be comparable for heap in priority queue
    def __lt__(self, other):
        """Defines the less-than comparison based on cost / level."""
        if not isinstance(other, state):
            raise TypeError("Comparison is only supported between state instances.")
        
        if self.cost is not None and other.cost is not None:
            return self.cost < other.cost
        else:
            return self.level < other.level


if __name__ == "__main__":
    board = board_8_puzzle()
    print(board)