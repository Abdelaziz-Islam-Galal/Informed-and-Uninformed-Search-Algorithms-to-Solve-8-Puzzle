from board import board_8_puzzle
from algorithms.algorithms import algorithms

if __name__ == "__main__":
    board = board_8_puzzle()
    board.shuffle(3)
    print(board)
    solver = algorithms(board)
    result = solver.bfs()
    print("Goal found:\n", result)