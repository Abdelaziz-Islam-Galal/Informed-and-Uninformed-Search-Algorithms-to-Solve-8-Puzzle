from functools import total_ordering
from board import board_8_puzzle

@total_ordering # to fill in the other comparison methods based on __lt__
class board_state:
    def __init__(self, board: board_8_puzzle, parent: None|board_state = None, heuristics: bool = False):
        self.board = board
        self.parent = parent
        self.level = 0 if parent is None else parent.level + 1
        
        if not heuristics:
            self.cost = self.level
        else:
            pass
    
        # find neighbors by moving the zero tile in all possible directions and creating new states for each valid move
        self.neighbors = []
        for direction in ["up", "down", "left", "right"]:
            new_board = self.board.copy()
            if new_board.move_zero(direction):
                self.neighbors.append(board_state(new_board, self))

    def is_goal(self) -> bool:
        if self.board.goal_test():
            return True
        return False
    
    # comparison for this class objects to be comparable for heap in priority queue
    def __lt__(self, other):
        """Defines the less-than comparison based on cost / level."""
        if not isinstance(other, board_state):
            raise TypeError("Comparison is only supported between board_state instances.")
        
        if self.cost is not None and other.cost is not None:
            return self.cost < other.cost
        else:
            return self.level < other.level
