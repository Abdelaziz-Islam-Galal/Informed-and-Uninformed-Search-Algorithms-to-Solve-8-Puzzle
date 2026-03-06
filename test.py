from board import board_8_puzzle
from algorithms.algorithms import algorithms

def test_bfs():
    board = board_8_puzzle([[1,2,5], [3,4,0], [6,7,8]])
    # board.shuffle(50)
    print(board)
    solver = algorithms(board)

    result: algorithms.result|None = solver.bfs(False)
    result.save_report("report.txt")

def test_visuals():
    board = board_8_puzzle([[1,2,5], [3,4,0], [6,7,8]])
    solver = algorithms(board)
    result: algorithms.result|None = solver.bfs(True)
    if result:
        result.save_report("output/report.txt")

if __name__ == "__main__":
    # test_bfs()
    test_visuals()

