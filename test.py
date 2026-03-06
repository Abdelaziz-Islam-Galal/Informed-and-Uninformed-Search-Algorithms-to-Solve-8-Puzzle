from board import board_8_puzzle
from algorithms.algorithms import algorithms

def test_bfs():
    board = board_8_puzzle([[1,2,5], [3,4,0], [6,7,8]])
    # board.shuffle(50)
    print(board)
    solver = algorithms(board)

    result: algorithms.result|None = solver.bfs(False)
    if result:
        path = result.goal_path
        print(f"explored {len(result.explored)} states")
        print(f"Solved in {len(path) - 1} moves:\n") # type: ignore
        for step, state in enumerate(path): # type: ignore
            print(f"Step {step}:")
            print(state.board)   # uses your __str__
            print()
    else:
        print("No solution found.")

def test_visuals():
    board = board_8_puzzle([[1,2,5], [3,4,0], [6,7,8]])
    solver = algorithms(board)
    result: algorithms.result|None = solver.bfs(True)

if __name__ == "__main__":
    # test_bfs()
    test_visuals()

