from visualizer.implement_visualizer.implement_visualizer import tree_visualizer
from visualizer.implement_visualizer.adapter import state_to_tree_adapter
from algorithms.state import board_state

class tree_drawer:
    def __init__(self):
        self.visualizer = tree_visualizer()

    def draw(self, explored:set, frontier:set, final_state:board_state|None=None, title="", level_height:float|None=None, leaf_spacing:float|None=None, out_file="puzzle_tree.png"):
        self.visualizer.level_height = level_height
        self.visualizer.leaf_spacing = leaf_spacing
        self.adapter = state_to_tree_adapter(explored, frontier, final_state)
        self.visualizer.render_tree(self.adapter, title=title, out_file=out_file)

