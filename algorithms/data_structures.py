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
    
    def decrease_key(self, item: board_state) -> bool:
        """Decrease the priority of an existing state in the heap.

        For A* this means updating the stored node if we found a better path (lower g,
        hence lower f).  Returns True if an update happened, else False.
        """
        for current_item in self.items:
            if current_item == item:
                # Prefer comparing f when present; otherwise fall back to g.
                if current_item.cost_f is not None and item.cost_f is not None:
                    improved = item.cost_f < current_item.cost_f
                else:
                    improved = item.cost < current_item.cost

                if improved:
                    current_item.cost = item.cost
                    current_item.cost_f = item.cost_f
                    current_item.parent = item.parent
                    current_item.move = item.move
                    heapq.heapify(self.items)
                    return True
                return False
        return False

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)
    