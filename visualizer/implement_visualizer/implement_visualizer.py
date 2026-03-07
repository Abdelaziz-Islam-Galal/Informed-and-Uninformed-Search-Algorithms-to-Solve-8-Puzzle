import matplotlib.pyplot as plt       # main plotting library - creates figures, axes, saves images
import matplotlib.patches as patches  # provides shape primitives: Rectangle, FancyBboxPatch, etc.
from collections import defaultdict   # dict subclass that returns a default value for missing keys (here: empty list for children)

from visualizer.implement_visualizer.adapter import tree_data  # our data model: a list of tree_data_node objects

"""
flow:
    1. tree_layout  -> computes (x, y) screen coordinates for every node
        to make it work dynamically we start placing children first then work ourselves to the parents centered
    2. render_tree  -> uses those coordinates to draw grids and arrows with matplotlib
        simple, based on a constant cell size

Colour conventions used throughout:
    - black  -> explored
    - orange -> frontier
    - red    -> final solution path
"""


class tree_visualizer:
    
    CELL = 0.22          # width/height of a single puzzle cell in figure units
    GRID = 3 * CELL      # total width/height of the 3x3 puzzle grid (3 cells wide)
    HALF = GRID / 2      # half the grid size
    LEVEL_HEIGHT = 1.4   # vertical distance between consecutive tree depth levels
    LEAF_SPACING = 1.1   # horizontal distance between adjacent leaf nodes


    # inner class: tree_layout -> for computing positions
    class tree_layout:
        def __init__(self, tree: tree_data, level_height: float, leaf_spacing: float):
            self.level_height: float | None = level_height
            self.leaf_spacing: float | None = leaf_spacing
            self.tree = tree


        def _build_tree_meta(self):
            """
            pass on all nodes once to:

            children : defaultdict(list)
                {root_id: [child1_id, child2_id], child1_id: [grandchild_id], …}
                Used later to traverse the tree top-down.

            depth : dict
                {each node_id : its depth} (root depth = 0, depth = level-1).
                used to calculate the y-coordinate: deeper nodes sit lower on screen.
            """
            children = defaultdict(list)  # use defaultdict not dict so missing keys automatically get [] instead of KeyError
            depth    = {}

            for node in self.tree.nodes:
                depth[node.id] = node.depth
                if node.parent_id is not None:
                    children[node.parent_id].append(node.id)

            return children, depth


        def _assign_x_positions(self, root_id, children, leaf_spacing=1.0):
            """
                1. recurse into all children first.
                2. leaf nodes get the next available integer slot (counter x spacing).
                3. internal nodes are centred over their leftmost and rightmost child.
            (so no two nodes overlap horizontally and parent nodes are visually centred above their subtree)

            Parameters:
                root_id      : id of the tree's root node (the start state)
                children     : {node_id: [child_id, …]} from _build_tree_meta
                leaf_spacing : horizontal distance between adjacent leaves

            Returns:
                dict {node_id: x_pos}  -> x coordinate for each node
            """
            x_pos   = {}
            counter = [0]   # list so the nested function _assign can mutate it (list is refrence based)

            def _assign(nid):
                kids = children[nid]   # direct children of this node

                if not kids:
                    # base case - leaf node: claim the next horizontal slot
                    x_pos[nid] = counter[0] * leaf_spacing # spacing is done for leaves and parents are centered
                    counter[0] += 1
                else:
                    # assign children first, then centre over them
                    for k in kids:
                        _assign(k)
                    
                    # centre between the leftmost and rightmost child's positions
                    x_pos[nid] = (x_pos[kids[0]] + x_pos[kids[-1]]) / 2

            _assign(root_id)  # assign id for root by recursing down the tree and starting by leafes
            return x_pos


        def compute_layout(self):
            """
            Returns
            -------
            layout    : dict {node_id: (cx, cy)}  - final centred coordinates for each node
            (fig_w, fig_h) : figure dimensions in inches
            """
            children, depth = self._build_tree_meta() 
            # children: dict with each node's children, depth: dict with each node's depth (root=0, increases by 1 each level)

            # The root is the unique node with no parent
            root_id = self.tree.root_node.id if self.tree.root_node else None
            if root_id is None:
                raise ValueError("Tree must have a root node with no parent_id")

            x_pos: dict = self._assign_x_positions(root_id, children, self.leaf_spacing)  # type: ignore

            max_depth = max(depth.values())   # deepest level in the tree
            layout    = {}
            
            # largest x and y to drive the figure size from
            max_x = None
            min_x = None
            max_y = None
            min_y = None

            # convert (x_pos, depth) -> (cx, cy)
            # cy is largest for depth=0 (root)
            # cy decreases as depth increases
            for nid in x_pos:
                cx = x_pos[nid]
                cy = (max_depth - depth[nid]) * self.level_height   # we invert the depth so root is at top
                layout[nid] = (cx, cy)
                if max_x is None or cx > max_x:
                    max_x = cx
                if min_x is None or cx < min_x:
                    min_x = cx
                if max_y is None or cy > max_y:
                    max_y = cy 
                if min_y is None or cy < min_y:
                    min_y = cy

            # figure size - driven by the spread of node positions plus a fixed margin
            margin = 0.8    # empty space after the outermost nodes
            fig_w  = (max_x - min_x + 2 * margin) * 1.1   # type: ignore  # add 10% extra width
            fig_h  = (max_y - min_y + 2 * margin) * 1.1   # type: ignore  # x2 accounting for padding from both sides (up-down/right-left)

            # shift so the minimum x/y starts exactly at `margin`
            # Without this, nodes near (0,0) would be clipped by the figure border
            ox = min_x - margin # type: ignore
            oy = min_y - margin # type: ignore
            layout = {nid: (cx - ox, cy - oy) for nid, (cx, cy) in layout.items()}

            # minimum figure size of 4×4 so tiny trees look accaptable
            return layout, (max(fig_w, 4), max(fig_h, 4))


    def draw_grid(self, ax, state, cx, cy, colour):
        """
        Draws one 3x3 puzzle board centred at figure coordinate (cx, cy).
            - rounded outer border rectangle (colour-coded by node role)
            - 9 inner cell rectangles on top of it
            - number label in each non-zero cell (0 = blank tile, drawn empty)

        Parameters
        ----------
        ax     : matplotlib Axes to draw on
        state  : flat list of 9 ints, e.g. [1, 2, 5, 3, 4, 0, 6, 7, 8]
        cx, cy : centre coordinate of the grid
        colour : border colour string ("black", "red", "orange")
                 defaults is "black"
        """
        # top-left corner of the grid (offset from centre by half the grid size)
        x0 = cx - self.HALF   # left edge
        y0 = cy - self.HALF   # bottom edge

        border_color = colour if colour is not None else "black"

        # Outer border 
        # zorder=2 puts it above the axis background but below the cell rectangles (cell rectangled = zorder=3)
        # (zorder is the z axis as of layers)
        ax.add_patch(patches.FancyBboxPatch(
            (x0, y0), self.GRID, self.GRID,
            boxstyle="round,pad=0.01",
            linewidth=2.0 if border_color == "red" else 1.5,  # red path (goal path) nodes get a thicker border
            edgecolor=border_color, facecolor="white", zorder=2))

        # individual cells 
        for i in range(3):       # row
            for j in range(3):   # column

                val = state[i * 3 + j]   # (i,j)

                # rx, ry = bottom-left corner of this cell
                rx = x0 + j * self.CELL         # left + shift right by j cells
                ry = y0 + (2 - i) * self.CELL   # bottom + shift up; (2-i) flips row '0' to the top

                # cell background rectangle
                ax.add_patch(patches.Rectangle(
                    (rx, ry), self.CELL, self.CELL,
                    linewidth=0.8, edgecolor="black",
                    facecolor="white", zorder=3))   # zorder=3: on top of the outer border

                # number label - 0 value = blank tile
                if val != 0:
                    ax.text(
                        rx + self.CELL / 2,   # horizontally centred in the cell
                        ry + self.CELL / 2,   # vertically centred in the cell
                        str(val),
                        ha="center", va="center",
                        fontsize=7, color="black",
                        fontweight="bold",
                        zorder=4)             # zorder=4: on top of everything else


    def draw_arrow(self, axes, x1, y1, x2, y2, label=""):
        """
        Draws an annotated arrow from (x1, y1) to (x2, y2).

        Parameters
        ----------
        axes        : matplotlib Axes to draw on
        x1, y1      : arrow start point (bottom-centre of parent grid)
        x2, y2      : arrow end point   (top-centre of child grid)
        label       : optional text to display at the arrow's midpoint
        """
        # annotate with an empty string so only the arrowhead is drawn (no text at tip)
        axes.annotate(
            "",
            xy=(x2, y2),       # arrowhead end point
            xytext=(x1, y1),   # arrow tail start point
            arrowprops=dict(
                arrowstyle="-|>",       # solid filled arrowhead
                color="black",
                lw=1.0,                 # line width
                mutation_scale=10       # arrowhead size
            )
        )

        if label:
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            axes.text(
                mx, my, label,
                ha="center", va="center",
                fontsize=7.5,
                bbox=dict(facecolor="white", edgecolor="none", pad=1)  # white box to be readable
            )

    def render_tree(self, tree: tree_data, title="", out_file="tree.png"):
        """
        main method: layout -> figure setup -> draw arrows -> draw grids -> save.

        Parameters
        ----------
        tree     : tree_data object containing all nodes to render
        title    : string shown as the figure title (e.g. "step 3")
        out_file : file path to save the PNG to (e.g. "output/3.png")
        """

        # Compute layout
        # Returns: layout dict {node_id: (cx, cy)}, and figure dimensions.
        layout, (fig_w, fig_h) = self.tree_layout(
            tree,
            level_height=self.LEVEL_HEIGHT,
            leaf_spacing=self.LEAF_SPACING
        ).compute_layout() # inner class instantiation then its main method called

        # Create figure
        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
        ax.set_aspect("equal")   # grids stay square; x to y ratio = 1
        ax.axis("off")           # hide axes data/lines/.. it is not a graph
        ax.set_facecolor("#f9f9f9")       # light grey axes background
        fig.patch.set_facecolor("#f9f9f9")  # same colour for the figure border area

        # Set axis limits
        # Computed from actual node positions so nothing gets clipped.
        all_x = [v[0] for v in layout.values()]
        all_y = [v[1] for v in layout.values()]
        ax.set_xlim(min(all_x) - 0.6, max(all_x) + 0.6)
        ax.set_ylim(min(all_y) - 0.6, max(all_y) + 0.6)

        # Draw arrows first (lower zorder - they go behind the grids)
        for node in tree.nodes:
            if node.parent_id is None:
                # Root node has no parent -> no incoming arrow to draw
                continue

            px, py = layout[node.parent_id]   # parent's centre coordinate
            cx, cy = layout[node.id]          # this node's centre coordinate

            # Arrows connect bottom-centre of the parent grid to top-centre of the child grid.
            self.draw_arrow(
                ax,
                px, py - self.HALF,   # start: bottom edge of parent grid
                cx, cy + self.HALF,   # end:   top edge of child grid
                label=node.label      # heuristic value label (empty string if not applicable)
            )

        # Draw puzzle grids on top of the arrows
        for node in tree.nodes:
            cx, cy = layout[node.id]
            self.draw_grid(ax, node.state, cx, cy, colour=node.colour)
            # node.colour is set by the adapter:
            #   "red"    -> on the solution path
            #   "orange" -> in the frontier
            #   "black"  -> explored (default)

        ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
        plt.tight_layout()   # adjust subplot params so grids/labels don't overflow figure bounds
        plt.savefig(out_file, dpi=150, bbox_inches="tight")   # 150 DPI = clear but not huge file size
        print(f"Saved -> {out_file}")