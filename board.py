import random

class board_8_puzzle:
    def __init__(self, board: None|list[list[int]] = None):
        if board is not None:
            self._board = self._2d_list_to_int(board)
        else:
            self._board = 12345678

    def _2d_list_to_int(self, board: list[list[int]]) -> int:
        """
        Converts a 2D list representation of the board to a single integer for hashing.
        For example, the board:
            [[1, 2, 5],
             [3, 4, 0],
             [6, 7, 8]]
        would be converted to the integer 125340678.
        """
        result = 0
        for i in range(3):
            for j in range(3):
                result = result * 10 + board[i][j]
        return result

    def goal_test(self) -> bool:
        """
        Checks if the current board state is the goal state.
        """
        return self._board == 12345678

    def move_zero(self, direction: str) -> bool:
        """
        Moves the zero tile up/down/left/right if possible.
        Returns True if the move was successful, False otherwise.
        """
        board_str = str(self._board).zfill(9)
        zero_index = board_str.index('0')
        row, col = divmod(zero_index, 3)
        if direction == "up" and row > 0:
            swap_index = (row - 1) * 3 + col
        elif direction == "down" and row < 2:
            swap_index = (row + 1) * 3 + col
        elif direction == "left" and col > 0:
            swap_index = row * 3 + (col - 1)
        elif direction == "right" and col < 2:
            swap_index = row * 3 + (col + 1)
        else:
            return False
        
        # Swap the zero with the target tile
        board_list = list(board_str)
        board_list[zero_index], board_list[swap_index] = board_list[swap_index], board_list[zero_index]
        self._board = int("".join(board_list))
        return True

    @property
    def board(self) -> list[list[int]]:
        """
        Returns the current board state as a 2D list.
        """
        board_str = str(self._board).zfill(9)
        return [list(map(int, board_str[i:i+3])) for i in range(0, 9, 3)]

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
                    flag = True
        if not flag:
            raise ValueError("Board must contain a zero.")
        
        self._board = self._2d_list_to_int(new_board)
    
    @property
    def board_list(self) -> list[int]:
        return [int(digit) for digit in str(self._board).zfill(9)]

    def copy(self):
        new = board_8_puzzle.__new__(board_8_puzzle)
        new._board = self._board
        return new

    def shuffle(self, moves: int = 100):
        """
        Generates a random board state by making a series of random moves from the goal state.
        made it by moves so it is guaranteed to be solvable
        """
        directions = ["up", "down", "left", "right"]
        for _ in range(moves):
            self.move_zero(random.choice(directions))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, board_8_puzzle):
            return NotImplemented
        return self._board == other._board

    def __hash__(self) -> int:
        return hash(self._board)

    def __str__(self):
        """
        prints:
            0 1 2
            3 4 5
            6 7 8
        """
        board_str = str(self._board).zfill(9)
        return board_str[0:3] + "\n" + board_str[3:6] + "\n" + board_str[6:9]


if __name__ == "__main__":
    board = board_8_puzzle()
    print(board)