from visualizer.implement_visualizer.implement_visualizer import tree_visualizer
from visualizer.implement_visualizer.adapter import state_to_tree_adapter

class draw_tree:
    def __init__(self, state):
        self.adapter = state_to_tree_adapter(state)
        self.visualizer = tree_visualizer()

    def draw(self, title="", level_height:float|None=None, leaf_spacing:float|None=None, out_file="puzzle_tree.png"):
        self.visualizer.level_height = level_height
        self.visualizer.leaf_spacing = leaf_spacing
        self.visualizer.render_tree(self.adapter, title=title, out_file=out_file)

