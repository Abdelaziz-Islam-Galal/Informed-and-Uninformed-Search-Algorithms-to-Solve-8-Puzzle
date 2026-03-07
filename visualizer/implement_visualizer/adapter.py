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
        self._root_node = None

    @property
    def root_node(self):
        return self._root_node

    @root_node.setter
    def root_node(self, root_node:tree_data_node):
        self._root_node = root_node

    def add_node(self, id, state:list, level:int, parent_id, heuristic, colour=None):
        label = ""
        if heuristic is not None:
            label = f"{heuristic}"

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
            if state.parent:
                parent_id = hash(state.parent)
            else:
                parent_id = None
                self.root_node = tree_data_node(state_id, state.board_list, state.level, parent_id, "", state.cost_f)
            if final_state and (state in red_path): #type: ignore
                self.add_node(state_id, state.board_list, state.level, parent_id, heuristic=state.cost_f, colour="red")
            else:
                self.add_node(state_id, state.board_list, state.level, parent_id, heuristic=state.cost_f)
        for state in frontier:
            state_id = hash(state)
            if state.parent:
                parent_id = hash(state.parent)
            else:
                parent_id = None
                self.root_node = tree_data_node(state_id, state.board_list, state.level, parent_id, "", state.cost_f)
            self.add_node(state_id, state.board_list, state.level, parent_id, heuristic=state.cost_f, colour="orange")
