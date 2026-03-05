from board import board_8_puzzle
from algorithms.algorithms import algorithms

if __name__ == "__main__":
    board = board_8_puzzle()
    board.shuffle(50)
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