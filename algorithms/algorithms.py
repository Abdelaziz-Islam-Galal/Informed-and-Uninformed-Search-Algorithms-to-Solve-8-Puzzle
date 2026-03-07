from __future__ import annotations

from dataclasses import dataclass
import os

from algorithms.data_structures import queue, stack, priority_queue
from board import board_8_puzzle
from algorithms.state import board_state
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
                move_txt = "START" if step == 0 else (state.move or "")
                print(f"Step {step} ({move_txt}):\n{state.board}\n")


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
                    from visualizer.tree_drawer import tree_drawer as _tree_drawer
                    drawer = _tree_drawer()
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
    
    def A_star(
        self,
        visual_output: bool,
        heuristic: str = "manhattan",
        output_dir: str = "output",
    ) -> algorithms.result:
        if visual_output:
            os.makedirs(output_dir, exist_ok=True)
            visualizer_input_list: list[tuple[set, set, str, str]] = []
            counter = 0

        start_time = time()
        heuristic_normalized = heuristic.strip().lower().replace("-", "").replace("_", "")
        if heuristic_normalized in {"manhattan", "manhattandistance"}:
            start = board_state(self._puzzle, None, Manhattan_heuristics=True)
        elif heuristic_normalized in {"euclidean", "eucledian", "euclideandistance", "euclediandistance"}:
            start = board_state(self._puzzle, None, eucledian_heuristics=True)
        else:
            raise ValueError("A_star heuristic must be 'manhattan' or 'euclidean'.")

        explored: set[board_state] = set()
        frontier = priority_queue()
        frontier_view: set[board_state] = set()
        best_g: dict[board_state, int] = {start: start.cost}

        frontier.insert(start)
        frontier_view.add(start)
        if visual_output:
            visualizer_input_list.append(
                (
                    explored.copy(),
                    frontier_view.copy(),
                    f"step {counter} (start)",
                    os.path.join(output_dir, f"{counter}.png"),
                )
            )
            counter += 1

        while not frontier.is_empty():
            state: board_state = frontier.pop()
            frontier_view.discard(state)

            best_known = best_g.get(state)
            if best_known is None or state.cost != best_known:#ADD MORE SECURITY TO CHECK THERE IS ONE NODE WITH OPTIMAL COST FOUND
                continue

            explored.add(state)

            if state.is_goal():
                time_taken = time() - start_time
                if visual_output:
                    from visualizer.tree_drawer import tree_drawer as _tree_drawer
                    drawer = _tree_drawer()
                    for input in visualizer_input_list:  # type: ignore
                        drawer.draw(input[0], input[1], None, title=input[2], out_file=input[3])  # type: ignore
                    drawer.draw(
                        explored.copy(),
                        frontier_view.copy(),
                        state,
                        title=f"step {counter} (goal)",
                        out_file=os.path.join(output_dir, f"{counter}.png"),
                    )  # type: ignore
                return self.result(explored, start, state, time_taken)

            for neighbor in state.neighbors:
                tentative_g = neighbor.cost
                prev_best = best_g.get(neighbor)
                if prev_best is None or tentative_g < prev_best:#node=NONE MEAN THAT WE DIDN'T ADD IT TO best_g YET SO IT DIDN'T HAVE VALUE
                    best_g[neighbor] = tentative_g              #tentative_g < prev_best CHECK THAT WE WILL ADD THE OPTIMAL COST OF THE NODE 
                    frontier.insert(neighbor)   #THE SORTING TECHNIC HER DEPEND ON __lt__ which depend on f=g+h in state.py 
                    frontier_view.add(neighbor)

            if visual_output:
                visualizer_input_list.append(
                    (
                        explored.copy(),
                        frontier_view.copy(),
                        f"step {counter}",
                        os.path.join(output_dir, f"{counter}.png"),
                    )
                )  # type: ignore
                counter += 1

        return self.result(explored, start, None, time() - start_time)
   