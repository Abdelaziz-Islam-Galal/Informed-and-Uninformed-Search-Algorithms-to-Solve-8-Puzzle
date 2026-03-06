from visualizer.implement_visualizer.implement_visualizer import tree_visualizer
from visualizer.implement_visualizer.adapter import state_to_tree_adapter
from algorithms.state import board_state

class tree_drawer:
    def __init__(self):
        self.visualizer = tree_visualizer()

    def draw(self, explored:set, frontier:set, final_state:board_state|None=None, title="", out_file="puzzle_tree.png"):
        self.adapter = state_to_tree_adapter(explored, frontier, final_state)
        self.visualizer.render_tree(self.adapter, title=title, out_file=out_file) # type: ignore

