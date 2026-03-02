from data_structures import queue, stack, priority_queue
from board import state

class bfs():
    def __init__(self, initial_state: state):
        self.start = initial_state
        self.explored = set()
        self.frontier = queue()
        self.frontier.enqueue(self.start)

    def run(self) -> bool:
        while not self.frontier.is_empty():
            state: state = self.frontier.dequeue()
            self.explored.add(state)

            if state.is_goal():
                return True

            for neighbor in state.neighbors:
                if neighbor not in self.explored and neighbor not in self.frontier.items:
                    self.frontier.enqueue(neighbor)

        return False
    
