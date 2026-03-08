from __future__ import annotations

from dataclasses import dataclass
import os

from algorithms.data_structures import queue, stack, priority_queue
from board import board_8_puzzle
from algorithms.state import board_state
from time import time
from visualizer.tree_drawer import tree_drawer as _tree_drawer

class algorithms:
    LIMIT_STATES = 10000000
    
    def __init__(self, puzzle: board_8_puzzle):
        self._puzzle = puzzle
        
    @dataclass
    class result:
        explored: set
        start_state: board_state
        goal_state: board_state|None
        time_taken: float
        max_depth: int

        # Metadata for reporting (kept optional for backward compatibility)
        algorithm: str = ""
        heuristic: str | None = None
        data_structure: str = ""
        assumptions: list[str] | None = None
        extra_work: list[str] | None = None

        def save_report(self, out_file: str = "report.pdf"):
            from algorithms.reporting import save_search_report

            save_search_report(
                explored=self.explored,
                start_state=self.start_state,
                goal_state=self.goal_state,
                time_taken=self.time_taken,
                out_file=out_file,
                algorithm=self.algorithm,
                heuristic=self.heuristic,
                data_structure=self.data_structure,
                assumptions=self.assumptions,
                extra_work=self.extra_work,
            )
        def __str__(self):
            return f"Algorithm: {self.algorithm}\nHeuristic: {self.heuristic}\nData Structure: {self.data_structure}\nAssumptions: {self.assumptions}\nExtra Work: {self.extra_work}\nTime Taken: {self.time_taken:.4f} sec\nExplored Nodes: {len(self.explored)}\nStart State:\n{self.start_state.board}\nGoal State:\n{self.goal_state.board if self.goal_state else 'N/A'}"


    def bfs(self, visual_output: bool, output_dir: str = "output") -> algorithms.result:
        if visual_output:
            os.makedirs(output_dir, exist_ok=True)  # ensure output_dir exists
            visualizer_input_list: list[tuple[set, set, str, str]] = []

        max_depth = 0
        limit_counter = 0
        start_time = time()
        start = board_state(self._puzzle, None)
        explored = set()
        frontier = queue()
        search_frontier = set() # for o(1) search instead of O(n) in the queue
        # o(1) because the set uses hashing

        frontier.enqueue(start)
        search_frontier.add(start)
        
        if visual_output:
            counter = 0
            visualizer_input_list.append( # type: ignore
                (
                    explored.copy(),
                    search_frontier.copy(),
                    f"step {counter}",
                    os.path.join(output_dir, f"{counter}.png"), # type: ignore  # write under output_dir
                )
            )  # type: ignore
            counter+=1

        while not frontier.is_empty():
            state: board_state = frontier.dequeue()
            explored.add(state)
            limit_counter += 1
            max_depth = max(max_depth, state.level)
            search_frontier.remove(state)

            if state.is_goal():
                time_taken = time() - start_time
                if visual_output:
                    drawer = _tree_drawer()
                    for input in visualizer_input_list: # type: ignore
                        drawer.draw(input[0], input[1], None, title=input[2], out_file=input[3]) # type: ignore
                    drawer.draw(
                        explored.copy(),
                        search_frontier.copy(),
                        state,
                        f"step {counter} (goal)", # type: ignore
                        os.path.join(output_dir, f"{counter}.png"), # type: ignore  # write under output_dir
                    )  # type: ignore
                
                return self.result(explored, start, state, time_taken, max_depth, algorithm="BFS", data_structure="FIFO Queue (collections.deque) + visited set")

            if limit_counter >= self.LIMIT_STATES:
                print(f"Reached state limit of {self.LIMIT_STATES}. Terminating search.")
                return self.result(explored, start, None, time() - start_time, max_depth, algorithm="BFS", data_structure="FIFO Queue (collections.deque) + visited set")

            for neighbor in state.neighbors:
                if neighbor not in explored and neighbor not in search_frontier:
                    frontier.enqueue(neighbor)
                    search_frontier.add(neighbor)

            if visual_output:
                visualizer_input_list.append( # type: ignore
                    (
                        explored.copy(),
                        search_frontier.copy(),
                        f"step {counter}", # type: ignore
                        os.path.join(output_dir, f"{counter}.png"), # type: ignore  # write under output_dir
                    )
                )  #type: ignore
                counter += 1 # type: ignore

        return self.result(explored, start, None, time() - start_time, max_depth, algorithm="BFS", data_structure="FIFO Queue (collections.deque) + visited set")


    def ids(self, visual_output: bool, output_dir: str = "output") -> algorithms.result:
        if visual_output:
            os.makedirs(output_dir, exist_ok=True)
            visualizer_input_list: list[tuple[set, set, str, str]] = []
            counter = 0

        start_time = time()
        start_node = board_state(self._puzzle, None)

        all_explored = set()
        max_depth = 0
        limit = 0

        print("Starting IDS Search...")

        while True:
            frontier = stack()
            frontier.push(start_node)

            explored_in_this_run = set()
            frontier_set = {start_node}
            goal_node = None

            # Snapshot the initial state of this DLS iteration
            if visual_output:
                visualizer_input_list.append(  # type: ignore
                    (
                        all_explored.copy(),
                        frontier_set.copy(),
                        f"step {counter}", # type: ignore
                        os.path.join(output_dir, f"{counter}.png"), # type: ignore 
                    )
                )
                counter += 1  # type: ignore

            while not frontier.is_empty():
                current = frontier.pop()
                frontier_set.remove(current)
                explored_in_this_run.add(current)
                max_depth = max(max_depth, current.level)


                if current.is_goal():
                    goal_node = current
                    break

                if current.level < limit:
                    for neighbor in reversed(current.neighbors):
                        if neighbor not in explored_in_this_run and neighbor not in frontier_set:
                            frontier.push(neighbor)
                            frontier_set.add(neighbor)

                # Snapshot after each node expansion
                if visual_output:
                    visualizer_input_list.append(  # type: ignore
                        (
                            (all_explored | explored_in_this_run).copy(),
                            frontier_set.copy(),
                            f"step {counter}", # type: ignore
                            os.path.join(output_dir, f"{counter}.png"), # type: ignore
                        )
                    )
                    counter += 1  # type: ignore

            all_explored.update(explored_in_this_run)

            if goal_node:
                time_taken = time() - start_time
                if visual_output:
                    drawer = _tree_drawer()
                    for input_data in visualizer_input_list:  # type: ignore
                        drawer.draw(input_data[0], input_data[1], None, title=input_data[2], out_file=input_data[3])
                    drawer.draw(
                        all_explored.copy(),
                        frontier_set.copy(),
                        goal_node,
                        f"step {counter}",  # type: ignore
                        os.path.join(output_dir, f"{counter}.png"),  # type: ignore
                    )
                return self.result(all_explored, start_node, goal_node, time_taken, max_depth, algorithm="IDS", data_structure="LIFO Stack (Python list) + visited set (per iteration)")

            # If not found, increase the depth limit and try again (Iterate)
            limit += 1
            # Failsafe to prevent infinite loops in case of unsolvable boards
            if limit > 500: 
                break

        return self.result(all_explored, start_node, None, time() - start_time, max_depth, algorithm="IDS", data_structure="LIFO Stack (Python list) + visited set (per iteration)")
            
    def dfs(self, visual_output: bool, output_dir: str = "output") -> algorithms.result:
        if visual_output:
            os.makedirs(output_dir, exist_ok=True)  # ensure output_dir exists before writing PNGs
            visualizer_input_list: list[tuple[set, set, str, str]] = []
            counter = 0

        start_time = time()
        start = board_state(self._puzzle, None)

        explored = set()
        frontier = stack() 
        search_frontier = set() 
        max_depth = 0
        limit_counter = 0

        frontier.push(start)
        search_frontier.add(start)

        if visual_output:
            visualizer_input_list.append( # type: ignore
                (explored.copy(), search_frontier.copy(), f"step {counter}", os.path.join(output_dir, f"{counter}.png")))  # type: ignore
            counter += 1 # type: ignore

        while not frontier.is_empty():
            state: board_state = frontier.pop()
            search_frontier.remove(state)
            explored.add(state)
            max_depth = max(max_depth, state.level)
            limit_counter += 1

            if state.is_goal():
                print(f"Goal found at depth {state.level} with {len(explored)} nodes explored.")
                time_taken = time() - start_time
                
                if visual_output:
                    drawer = _tree_drawer()
                    for input_data in visualizer_input_list: # type: ignore
                        drawer.draw(input_data[0], input_data[1], None, title=input_data[2], out_file=input_data[3])
                    drawer.draw(
                        explored.copy(),
                        search_frontier.copy(),
                        state,
                        f"step {counter} (goal)", # type: ignore
                        os.path.join(output_dir, f"{counter}.png"), # type: ignore  # write under output_dir
                    )
                
                return self.result(explored, start, state, time_taken, max_depth, algorithm="DFS", data_structure="LIFO Stack (Python list) + visited set")

            if limit_counter >= self.LIMIT_STATES:
                print(f"Reached state limit of {self.LIMIT_STATES}. Terminating search.")
                return self.result(explored, start, None, time() - start_time, max_depth, algorithm="DFS", data_structure="LIFO Stack (Python list) + visited set")


            for neighbor in reversed(state.neighbors):
                if neighbor not in explored and neighbor not in search_frontier:
                    frontier.push(neighbor)
                    search_frontier.add(neighbor)

            if visual_output:
                visualizer_input_list.append( # type: ignore # type: ignore
                    (
                        explored.copy(),
                        search_frontier.copy(),
                        f"step {counter}", # type: ignore
                        os.path.join(output_dir, f"{counter}.png"), # type: ignore  # type: ignore # write under output_dir
                    )
                )  # type: ignore
                counter += 1 # type: ignore

        return self.result(explored, start, None, time() - start_time, max_depth, algorithm="DFS", data_structure="LIFO Stack (Python list) + visited set")

    
    def A_star(self, visual_output: bool, heuristic: str = "manhattan", output_dir: str = "output") -> algorithms.result:
        if visual_output:
            os.makedirs(output_dir, exist_ok=True)
            visualizer_input_list: list[tuple[set, set, str, str]] = []
            counter = 0

        start_time = time()
        heuristic_normalized = heuristic.strip().lower().replace("-", "").replace("_", "")
        if heuristic_normalized in {"manhattan", "manhattandistance"}:
            start = board_state(self._puzzle, None, Manhattan_heuristics=True)
            heuristic_label = "Manhattan"
        elif heuristic_normalized in {"euclidean", "eucledian", "euclideandistance", "euclediandistance"}:
            start = board_state(self._puzzle, None, eucledian_heuristics=True)
            heuristic_label = "Euclidean"
        else:
            raise ValueError("A_star heuristic must be 'manhattan' or 'euclidean'.")

        explored: set[board_state] = set()
        frontier = priority_queue()
        frontier_view: set[board_state] = set()
        best_g: dict[board_state, int] = {start: start.cost}
        max_depth = 0
        limit_counter = 0

        frontier.insert(start)
        frontier_view.add(start)
        if visual_output:
            visualizer_input_list.append( # type: ignore
                (
                    explored.copy(),
                    frontier_view.copy(),
                    f"step {counter}", # type: ignore
                    os.path.join(output_dir, f"{counter}.png"), # type: ignore
                )
            )
            counter += 1 # type: ignore

        while not frontier.is_empty():
            state: board_state = frontier.pop()
            frontier_view.discard(state)

            best_known = best_g.get(state)
            if best_known is None or state.cost != best_known:#ADD MORE SECURITY TO CHECK THERE IS ONE NODE WITH OPTIMAL COST FOUND
                continue

            explored.add(state)
            max_depth = max(max_depth, state.level)
            limit_counter += 1

            if state.is_goal():
                time_taken = time() - start_time
                if visual_output:
                    drawer = _tree_drawer()
                    for input in visualizer_input_list:  # type: ignore
                        drawer.draw(input[0], input[1], None, title=input[2], out_file=input[3])  # type: ignore
                    drawer.draw(
                        explored.copy(),
                        frontier_view.copy(),
                        state,
                        title=f"step {counter} (goal)", # type: ignore
                        out_file=os.path.join(output_dir, f"{counter}.png"), # type: ignore
                    )  # type: ignore
                return self.result(
                    explored,
                    start,
                    state,
                    time_taken,
                    algorithm="A*",
                    heuristic=heuristic_label,
                    data_structure="Priority queue (min-heap via heapq) ordered by f=g+h + best_g dictionary",
                    max_depth=max_depth,
                )

            if limit_counter >= self.LIMIT_STATES:
                print(f"Reached state limit of {self.LIMIT_STATES}. Terminating search.")
                return self.result(explored, start, None, time() - start_time, max_depth, algorithm="A*", heuristic=heuristic_label, data_structure="Priority queue (min-heap via heapq) ordered by f=g+h + best_g dictionary")

            for neighbor in state.neighbors:
                tentative_g = neighbor.cost
                prev_best = best_g.get(neighbor)
                if prev_best is None or tentative_g < prev_best:#node=NONE MEAN THAT WE DIDN'T ADD IT TO best_g YET SO IT DIDN'T HAVE VALUE
                    best_g[neighbor] = tentative_g              #tentative_g < prev_best CHECK THAT WE WILL ADD THE OPTIMAL COST OF THE NODE 
                    frontier.insert(neighbor)   #THE SORTING TECHNIC HER DEPEND ON __lt__ which depend on f=g+h in state.py 
                    frontier_view.add(neighbor)

            if visual_output:
                visualizer_input_list.append( # type: ignore
                    (
                        explored.copy(),
                        frontier_view.copy(),
                        f"step {counter}",  # type: ignore
                        os.path.join(output_dir, f"{counter}.png"), # type: ignore
                    )
                )  # type: ignore
                counter += 1 # type: ignore

        return self.result(explored, start, None, time() - start_time, max_depth)