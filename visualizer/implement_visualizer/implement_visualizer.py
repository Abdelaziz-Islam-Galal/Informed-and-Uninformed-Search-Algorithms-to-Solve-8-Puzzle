import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import defaultdict

from visualizer.implement_visualizer.adapter import tree_data

LEVEL_HEIGHT = 1.4
LEAF_SPACING = 1.1

"""
- add heuristics if given
- red for path
- orange for frontier

->needs a flag for the end tree?
"""

class tree_visualizer:
    CELL = 0.22          # size of one puzzle cell in figure units
    GRID = 3 * CELL      # full grid width/height
    HALF = GRID / 2

    def __init__(self, level_height=1.4, leaf_spacing=1.1):
        self._level_height = level_height
        self._leaf_spacing = leaf_spacing

    @property
    def level_height(self) -> float:
        return self._level_height

    @level_height.setter
    def level_height(self, value:float|None):
        if value is None:
            self._level_height = LEVEL_HEIGHT
            return
        if value <= 0:
            raise ValueError("level_height must be positive.")
        self._level_height:float = value

    @property
    def leaf_spacing(self) -> float:
        return self._leaf_spacing

    @leaf_spacing.setter
    def leaf_spacing(self, value:float|None):
        if value is None:
            self._leaf_spacing = LEAF_SPACING
            return
        if value <= 0:
            raise ValueError("leaf_spacing must be positive.")
        self._leaf_spacing:float = value

    class tree_layout:
        def __init__(self, tree: tree_data, level_height:float|None=LEVEL_HEIGHT, leaf_spacing:float|None=LEAF_SPACING):
            self.level_height:float|None = level_height
            self.leaf_spacing:float|None = leaf_spacing

            self.tree = tree

        def _build_tree_meta(self):
            """Return children map and depth map."""
            children = defaultdict(list)
            depth    = {}

            for node in self.tree.nodes:
                depth[node.id] = node.depth
                if node.parent_id is not None:
                    children[node.parent_id].append(node.id)

            return children, depth


        def _assign_x_positions(self, root_id, children, leaf_spacing=1.0):
            """
            Assign x positions via a post-order leaf-counting pass.
            Every leaf gets its own slot; internal nodes centre over their children.
            Returns dict {node_id: x}.
            """
            x_pos   = {}
            counter = [0]          # mutable counter shared across recursive calls

            def _assign(nid):
                kids = children[nid]
                if not kids:
                    x_pos[nid] = counter[0] * leaf_spacing
                    counter[0] += 1
                else:
                    for k in kids:
                        _assign(k)
                    x_pos[nid] = (x_pos[kids[0]] + x_pos[kids[-1]]) / 2

            _assign(root_id)
            return x_pos


        def compute_layout(self):
            """
            Returns dict {node_id: (cx, cy)} and figure size (width, height).
            """
            children, depth = self._build_tree_meta()

            root_id = next(n.id for n in self.tree.nodes if n.parent_id is None)
            x_pos = self._assign_x_positions(root_id, children, self.leaf_spacing) #type: ignore

            max_depth = max(depth.values())
            layout    = {}

            for nid in x_pos:
                cx = x_pos[nid]
                cy = (max_depth - depth[nid]) * self.level_height   # root at top
                layout[nid] = (cx, cy)

            # figure size driven by data extents
            all_x  = [v[0] for v in layout.values()]
            all_y  = [v[1] for v in layout.values()]
            margin = 0.8
            fig_w  = (max(all_x) - min(all_x) + 2 * margin) * 1.1
            fig_h  = (max(all_y) - min(all_y) + 2 * margin) * 1.1

            # shift so minimum x/y starts at margin
            ox = min(all_x) - margin
            oy = min(all_y) - margin
            layout = {nid: (cx - ox, cy - oy) for nid, (cx, cy) in layout.items()}

            return layout, (max(fig_w, 4), max(fig_h, 4))


    def draw_grid(self, ax, state, cx, cy, colour):
        """
        Draw a 3x3 puzzle grid centred at (cx, cy).
        red=True  → red outer border instead of black.
        orange=True → orange outer border instead of black.
        """
        x0 = cx - self.HALF # first cell's left edge
        y0 = cy - self.HALF # first cell's bottom edge

        border_color = colour if colour is not None else "black"
        ax.add_patch(patches.FancyBboxPatch(
            (x0, y0), self.GRID, self.GRID,
            boxstyle="round,pad=0.01",
            linewidth=2.0 if border_color == "red" else 1.5,
            edgecolor=border_color, facecolor="white", zorder=2))

        for i in range(3):
            for j in range(3):
                val = state[i * 3 + j] # mapping i,j to 1D list index
                rx  = x0 + j * self.CELL # cell's left edge
                ry  = y0 + (2 - i) * self.CELL # cell's bottom edge (i=0 is top row)

                ax.add_patch(patches.Rectangle(
                    (rx, ry), self.CELL, self.CELL,
                    linewidth=0.8, edgecolor="black",
                    facecolor="white", zorder=3))

                if val != 0: # if tile is zero then it is blank and we don't draw a number
                    ax.text(rx + self.CELL / 2, ry + self.CELL / 2, str(val),
                            ha="center", va="center",
                            fontsize=7, color="black",
                            fontweight="bold", zorder=4)


    def draw_arrow(self, axes, x1, y1, x2, y2, label=""):
        """Arrow from (x1,y1) to (x2,y2) with a midpoint label."""
        axes.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color="black", lw=1.0, mutation_scale=10))
        if label:
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            # small white box behind text for readability
            axes.text(mx, my, label, ha="center", va="center", fontsize=7.5,
                    bbox=dict(facecolor="white", edgecolor="none", pad=1))

    def render_tree(self, tree: tree_data, title="", out_file="tree.png"):

        layout, (fig_w, fig_h) = self.tree_layout(tree, level_height=self.level_height, leaf_spacing=self.leaf_spacing).compute_layout()
        # compute_layout(tree, level_height=level_height, leaf_spacing=leaf_spacing)

        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_facecolor("#f9f9f9")
        fig.patch.set_facecolor("#f9f9f9")

        # set axis limits from layout + margin
        all_x = [v[0] for v in layout.values()]
        all_y = [v[1] for v in layout.values()]
        ax.set_xlim(min(all_x) - 0.6, max(all_x) + 0.6)
        ax.set_ylim(min(all_y) - 0.6, max(all_y) + 0.6)

        # draw arrows first (behind grids)
        for node in tree.nodes:
            if node.parent_id is None:
                continue
            px, py = layout[node.parent_id]
            cx, cy = layout[node.id]
            # attach arrow to bottom of parent grid, top of child grid
            self.draw_arrow(ax, px, py - self.HALF, cx, cy + self.HALF, label=node.label)

        # draw grids on top
        for node in tree.nodes:
            cx, cy = layout[node.id]
            self.draw_grid(ax, node.state, cx, cy, colour=node.colour)

        ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
        plt.tight_layout()
        plt.savefig(out_file, dpi=150, bbox_inches="tight")
        print(f"Saved → {out_file}")
