from algorithms.data_structures import queue, stack, priority_queue
from board import board_8_puzzle
from algorithms.state import board_state
from visualizer.tree_drawer import tree_drawer

class algorithms:
    def __init__(self, puzzle: board_8_puzzle):
        self._puzzle = puzzle
        
    def bfs(self, visual_output:bool) -> board_state|None:
        start = board_state(self._puzzle, None, False)
        explored = set()
        frontier = queue()
        search_frontier = set() # for o(1) search instead of O(n) in the queue
        # o(1) because the set uses hashing

        frontier.enqueue(start)
        search_frontier.add(start)
        if visual_output:
            counter = 0
            visualizer = tree_drawer()
            visualizer.draw(explored, search_frontier, title=f"step {counter}", out_file=f"output/{counter}.png")
            counter+=1

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

            if visual_output:
                visualizer.draw(explored, search_frontier, title=f"step {counter}", out_file=f"output/{counter}.png")
                counter += 1

        return None
    