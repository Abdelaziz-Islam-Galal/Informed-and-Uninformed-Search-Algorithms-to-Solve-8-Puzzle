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

def test_a_star(visual: bool = False):
    board = board_8_puzzle([[1, 2, 5], [3, 4, 0], [6, 7, 8]])
    solver = algorithms(board)
    result: algorithms.result|None = solver.A_star(visual, heuristic="manhattan")
    if result:
        result.save_report("report.txt")

def compare_a_star_heuristics():
    board = board_8_puzzle([[1, 2, 5], [3, 4, 0], [6, 7, 8]])
    solver = algorithms(board)

    man = solver.A_star(False, heuristic="manhattan")
    euc = solver.A_star(False, heuristic="euclidean")

    print("A* Heuristic Comparison")
    print("- Manhattan:")
    print(f"  Expanded nodes: {len(man.explored)}")
    print(f"  Cost of path: {man.goal_state.level if man.goal_state else 'N/A'}")
    print(f"  Time: {man.time_taken:.4f} sec")
    print("- Euclidean:")
    print(f"  Expanded nodes: {len(euc.explored)}")
    print(f"  Cost of path: {euc.goal_state.level if euc.goal_state else 'N/A'}")
    print(f"  Time: {euc.time_taken:.4f} sec")

    if man.goal_state and euc.goal_state:
        if len(man.explored) < len(euc.explored):
            print("Result: Manhattan expanded fewer nodes on this puzzle.")
        elif len(man.explored) > len(euc.explored):
            print("Result: Euclidean expanded fewer nodes on this puzzle.")
        else:
            print("Result: Both expanded the same number of nodes on this puzzle.")

if __name__ == "__main__":
    # test_bfs()
    compare_a_star_heuristics()

