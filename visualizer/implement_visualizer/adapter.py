from algorithms.state import board_state

class tree_data_node:
    def __init__(self, id, state, parent_id, label, heuristic, colour=None):
        self.id = id
        self.state = state
        self.parent_id = parent_id
        self.label = label
        self.heuristic = heuristic  
        self.colour = colour

class tree_data:
    def __init__(self, list_of_nodes: list[tree_data_node]):
        self.nodes = list_of_nodes

    def add_node(self, id, state:list, parent_id, heuristic, colour=None):
        label = ""
        if heuristic is not None:
            label = f"{heuristic}"

        node = tree_data_node(id, state, parent_id, label, heuristic, colour)
        self.nodes.append(node)

class state_to_tree_adapter(tree_data):
    def __init__(self, explored:set, frontier:set, final_state:board_state|None=None):
        super().__init__([])
        self._convert_state(explored, frontier, final_state)

    def _convert_state(self, explored, frontier, final_state=None):
        if final_state:
            red_path = set(final_state.get_path())
        for state in explored:
            state_id = hash(state)
            parent_id = hash(state.parent) if state.parent else None
            if final_state and (state in red_path): #type: ignore
                self.add_node(state_id, state.board_list, parent_id, heuristic=state.cost_f, colour="red")
            else:
                self.add_node(state_id, state.board_list, parent_id, heuristic=state.cost_f)
        for state in frontier:
            state_id = hash(state)
            parent_id = hash(state.parent) if state.parent else None
            self.add_node(state_id, state.board_list, parent_id, heuristic=state.cost_f, colour="orange")

"""
I added colours to node but not using them yet
I need to make sure if no folder output then create one
"""