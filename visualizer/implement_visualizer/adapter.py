from algorithms.state import board_state

class tree_data_node:
    def __init__(self, id, state, level, parent_id, label, heuristic, colour=None):
        self.id = id
        self.state = state
        self.depth = level - 1
        self.parent_id = parent_id
        self.label = label
        self.heuristic = heuristic  
        self.colour = colour

class tree_data:
    def __init__(self, list_of_nodes: list[tree_data_node]):
        self.nodes = list_of_nodes

    def add_node(self, id, state:list, level:int, parent_id, heuristic=None, move: str | None = None, colour=None):
        move_map = {"up": "U", "down": "D", "left": "L", "right": "R"}
        move_label = move_map.get(move, move) if move else ""

        label_parts: list[str] = []
        if move_label:
            label_parts.append(str(move_label))
        if heuristic is not None:
            try:
                label_parts.append(f"{float(heuristic):.1f}")
            except (TypeError, ValueError):
                label_parts.append(str(heuristic))

        label = "\n".join(label_parts)

        node = tree_data_node(id, state, level, parent_id, label, heuristic, "black" if colour is None else colour)
        self.nodes.append(node)

class state_to_tree_adapter(tree_data):
    def __init__(self, explored:set, frontier:set, final_state:board_state|None=None):
        super().__init__([])
        self._convert_state(explored, frontier, final_state)

    def _convert_state(self, explored: set[board_state], frontier: set[board_state], final_state: board_state|None=None):
        if final_state:
            red_path = set(final_state.get_path())
        for state in explored:
            state_id = hash(state)
            parent_id = hash(state.parent) if state.parent else None
            if final_state and (state in red_path): #type: ignore
                self.add_node(state_id, state.board_list, state.level, parent_id, heuristic=state.cost_f, move=getattr(state, "move", None), colour="red")
            else:
                self.add_node(state_id, state.board_list, state.level, parent_id, heuristic=state.cost_f, move=getattr(state, "move", None))
        for state in frontier:
            state_id = hash(state)
            parent_id = hash(state.parent) if state.parent else None
            self.add_node(state_id, state.board_list, state.level, parent_id, heuristic=state.cost_f, move=getattr(state, "move", None), colour="orange")
