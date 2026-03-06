from .data_structures import queue, stack, priority_queue
from board import board_8_puzzle
from .state import board_state

class algorithms:
    def __init__(self, puzzle: board_8_puzzle):
        self._puzzle = puzzle
        
    def bfs(self) -> board_state|None:
        start = board_state(self._puzzle, None, False)
        explored = set()
        frontier = queue()
        search_frontier = set() # for o(1) search instead of O(n) in the queue
        # o(1) because the set uses hashing

        frontier.enqueue(start)
        search_frontier.add(start)
    
        while not frontier.is_empty():
            state: board_state = frontier.dequeue()
            explored.add(state)
            search_frontier.remove(state)

            if state.is_goal():
                return state

            for neighbor in state.neighbors:
                if neighbor not in explored and neighbor not in search_frontier:
                    frontier.enqueue(neighbor)
                    search_frontier.add(neighbor)

        return None
    