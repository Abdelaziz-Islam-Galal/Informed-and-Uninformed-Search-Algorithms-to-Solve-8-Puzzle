class tree_data_node:
    def __init__(self, id, state, parent_id, label, heuristic):
        self.id = id
        self.state = state
        self.parent_id = parent_id
        self.label = label
        self.heuristic = heuristic  

class tree_data:
    def __init__(self, list_of_nodes: list[tree_data_node]):
        self.nodes = list_of_nodes

    def add_node(self, id, state, parent_id, label, heuristic):
        node = tree_data_node(id, state, parent_id, label, heuristic)
        self.nodes.append(node)

class state_to_tree_adapter(tree_data):
    pass