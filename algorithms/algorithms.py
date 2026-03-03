from .data_structures import queue, stack, priority_queue
from board import board_8_puzzle
from .state import board_state

class algorithms:
    def __init__(self, puzzle: board_8_puzzle):
        self._puzzle = puzzle
        
    def bfs(self) -> bool|board_8_puzzle:
        start = board_state(self._puzzle, None, False)
        explored = set()
        frontier = queue()
        frontier.enqueue(start)

        while not frontier.is_empty():
            state: board_state = frontier.dequeue()
            explored.add(state)

            if state.is_goal():
                return state.board

            for neighbor in state.neighbors:
                if neighbor not in explored and neighbor not in frontier.items:
                    frontier.enqueue(neighbor)

        return False
    