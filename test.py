from board import board_8_puzzle
from algorithms.algorithms import algorithms

def test_bfs():
    board = board_8_puzzle([[1,2,5], [3,4,0], [6,7,8]])
    # board.shuffle(50)
    print(board)
    solver = algorithms(board)

    path = solver.bfs()
    if path:
        print(f"Solved in {len(path) - 1} moves:\n") # type: ignore
        for step, state in enumerate(path): # type: ignore
            print(f"Step {step}:")
            print(state.board)   # uses your __str__
            print()
    else:
        print("No solution found.")

# def test_visuals():
#     from visualizer.draw_tree import draw_tree

#     board = board_8_puzzle([[1,2,5], [3,4,0], [6,7,8]])
#     solver = algorithms(board)
#     state_path = solver.bfs()

#     if state_path:
#         drawer = draw_tree(state_path[-1])
#         drawer.draw(title="BFS Search Tree", out_file="bfs_tree.png")
#     else:
#         print("No solution found.")

# tou need to be based on the frontier and explored of the algorithm

if __name__ == "__main__":
    test_visuals()

