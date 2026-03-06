from dataclasses import dataclass
import os

from algorithms.data_structures import queue, stack, priority_queue
from board import board_8_puzzle
from algorithms.state import board_state
from visualizer.tree_drawer import tree_drawer
from time import time


class algorithms:
    def __init__(self, puzzle: board_8_puzzle):
        self._puzzle = puzzle
        
    @dataclass
    class result:
        explored: set
        start_state: board_state
        goal_state: board_state|None
        time_taken: float

        def save_report(self, out_file="report.txt"):
            if not self.goal_state:
                print(f"Time taken: {self.time_taken:.4f} seconds\n")
                print(f"Number of states explored: {len(self.explored)}\n")
                print("No solution found.\n")
                return 

            goal_path: list[board_state] = self.goal_state.get_path()
            cost_of_path: int = self.goal_state.level
            search_depth: int = max(state.level for state in self.explored)
            print(f"Time taken: {self.time_taken:.4f} seconds\n")
            print(f"Number of states explored: {len(self.explored)}\n")
            print(f"Cost of path: {cost_of_path}\n")
            print(f"Search depth: {search_depth}\n")
            print("Path to solution:\n")
            for step, state in enumerate(goal_path):
                print(f"Step {step}:\n{state.board}\n")


    def bfs(self, visual_output:bool) -> algorithms.result:
        if visual_output:
            os.makedirs("output", exist_ok=True)
            visualizer_input_list: list[tuple[set, set, str, str]] = []

        start_time = time()
        start = board_state(self._puzzle, None, False)
        explored = set()
        frontier = queue()
        search_frontier = set() # for o(1) search instead of O(n) in the queue
        # o(1) because the set uses hashing

        frontier.enqueue(start)
        search_frontier.add(start)
        if visual_output:
            counter = 0
            visualizer_input_list.append((explored.copy(), search_frontier.copy(), f"step {counter} (start)", f"output/{counter}.png")) # type: ignore
            counter+=1

        while not frontier.is_empty():
            state: board_state = frontier.dequeue()
            explored.add(state)
            search_frontier.remove(state)

            if state.is_goal():
                time_taken = time() - start_time
                if visual_output:
                    drawer = tree_drawer()
                    for input in visualizer_input_list: # type: ignore
                        drawer.draw(input[0], input[1], None, title=input[2], out_file=input[3]) # type: ignore
                    drawer.draw(explored.copy(), search_frontier.copy(), state, f"step {counter} (start)", f"output/{counter}.png") # type: ignore
                
                return self.result(explored, start, state, time_taken)

            for neighbor in state.neighbors:
                if neighbor not in explored and neighbor not in search_frontier:
                    frontier.enqueue(neighbor)
                    search_frontier.add(neighbor)

            if visual_output:
                visualizer_input_list.append((explored.copy(), search_frontier.copy(), f"step {counter}", f"output/{counter}.png")) #type: ignore
                counter += 1 # type: ignore

        return self.result(explored, start, None, time() - start_time)
    