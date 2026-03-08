from collections import deque
import heapq
from .state import board_state

class queue:
    # using deque for efficient insertion at the beginning of the data (a list will take O(n))
    def __init__(self):
        self.items = deque()

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.items.popleft()
        raise IndexError("Dequeue from an empty queue")

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)
    
class stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        raise IndexError("Pop from an empty stack")

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)
    
class priority_queue:
    def __init__(self):
        self.items = []

    def insert(self, item: board_state):
        heapq.heappush(self.items, item)

    def pop(self):
        if not self.is_empty():
            return heapq.heappop(self.items)
        raise IndexError("Pop from an empty priority queue")
    
    # # NOTE: needs to be revised when implementing A*
    # def decrease_key(self, item: board_state):
    #     for index, current_item in enumerate(self.items):
    #         if current_item == item:
    #             if item.cost_f < current_item.cost_f:
    #                 self.items[index].cost_f = item.cost_f
    #                 self.items[index].parent = item.parent
    #                 heapq.heapify(self.items)
    #             return
    #     raise ValueError("Item not found in the priority queue")

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)
    