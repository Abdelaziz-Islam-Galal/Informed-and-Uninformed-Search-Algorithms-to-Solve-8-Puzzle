from board import board_8_puzzle
from algorithms.algorithms import algorithms
import os
import random


def _save_report(result: algorithms.result, out_file: str) -> None:
    try:
        result.save_report(out_file)
    except ModuleNotFoundError as exc:
        print(str(exc))
        if out_file.lower().endswith(".pdf"):
            fallback = os.path.splitext(out_file)[0] + ".txt"
            print(f"Falling back to text report: {fallback}")
            result.save_report(fallback)

def test_bfs():
    board = board_8_puzzle([[1,2,5], [3,4,0], [6,7,8]])
    # board.shuffle(50)
    print(board)
    solver = algorithms(board)

    result: algorithms.result|None = solver.bfs(False)
    if result:
        _save_report(result, "bfs_report.pdf")

def test_visuals():
    board = board_8_puzzle([[1,2,5], [3,4,0], [6,7,8]])
    solver = algorithms(board)
    result: algorithms.result|None = solver.bfs(True)
    if result:
        _save_report(result, "output/report.pdf")

def test_a_star(visual: bool = False):
    board = board_8_puzzle([[1, 2, 5], [3, 4, 0], [6, 7, 8]])
    solver = algorithms(board)
    result: algorithms.result|None = solver.A_star(visual, heuristic="manhattan")
    if result:
        _save_report(result, "report.pdf")

def compare_a_star_heuristics():
    board = board_8_puzzle([[1, 2, 5], [3, 4, 0], [6, 7, 8]])
    solver = algorithms(board)

    man = solver.A_star(False, heuristic="manhattan")
    euc = solver.A_star(False, heuristic="euclidean")

    def moves_string(result: algorithms.result) -> str:
        if not result.goal_state:
            return "N/A"
        path = result.goal_state.get_path()
        move_map = {"up": "U", "down": "D", "left": "L", "right": "R"}
        moves = [move_map.get(s.move, s.move) for s in path[1:]]
        return " ".join(m for m in moves if m)

    print("A* Heuristic Comparison")
    print("Start board:")
    print(board)
    print("- Manhattan:")
    print(f"  Expanded nodes: {len(man.explored)}")
    print(f"  Cost of path: {man.goal_state.level if man.goal_state else 'N/A'}")
    print(f"  Moves: {moves_string(man)}")
    print(f"  Time: {man.time_taken:.4f} sec")
    print("- Euclidean:")
    print(f"  Expanded nodes: {len(euc.explored)}")
    print(f"  Cost of path: {euc.goal_state.level if euc.goal_state else 'N/A'}")
    print(f"  Moves: {moves_string(euc)}")
    print(f"  Time: {euc.time_taken:.4f} sec")

    if man.goal_state and euc.goal_state:
        if len(man.explored) < len(euc.explored):
            print("Result: Manhattan expanded fewer nodes on this puzzle.")
        elif len(man.explored) > len(euc.explored):
            print("Result: Euclidean expanded fewer nodes on this puzzle.")
        else:
            print("Result: Both expanded the same number of nodes on this puzzle.")

    print("Note: For the 8-puzzle, both Manhattan and Euclidean are admissible heuristics.")
    print("(On very easy boards, they can expand the same number of nodes.)")


def compare_a_star_heuristics_shuffled(shuffle_moves: int = 25, seed: int = 0):
    """Compare heuristics on a harder, reproducible shuffled board."""
    random.seed(seed)
    base = board_8_puzzle()  # starts at goal
    base.shuffle(shuffle_moves)

    start_matrix = [row.copy() for row in base.board]
    man_board = board_8_puzzle([row.copy() for row in start_matrix])
    euc_board = board_8_puzzle([row.copy() for row in start_matrix])

    man = algorithms(man_board).A_star(False, heuristic="manhattan")
    euc = algorithms(euc_board).A_star(False, heuristic="euclidean")

    def moves_string(result: algorithms.result) -> str:
        if not result.goal_state:
            return "N/A"
        path = result.goal_state.get_path()
        move_map = {"up": "U", "down": "D", "left": "L", "right": "R"}
        moves = [move_map.get(s.move, s.move) for s in path[1:]]
        return " ".join(m for m in moves if m)

    print("A* Heuristic Comparison (Shuffled)")
    print(f"Shuffle moves: {shuffle_moves}, seed: {seed}")
    print("Start board:")
    print(man_board)
    print("- Manhattan:")
    print(f"  Expanded nodes: {len(man.explored)}")
    print(f"  Cost of path: {man.goal_state.level if man.goal_state else 'N/A'}")
    print(f"  Moves: {moves_string(man)}")
    print(f"  Time: {man.time_taken:.4f} sec")
    print("- Euclidean:")
    print(f"  Expanded nodes: {len(euc.explored)}")
    print(f"  Cost of path: {euc.goal_state.level if euc.goal_state else 'N/A'}")
    print(f"  Moves: {moves_string(euc)}")
    print(f"  Time: {euc.time_taken:.4f} sec")

    if man.goal_state and euc.goal_state:
        if len(man.explored) < len(euc.explored):
            print("Result: Manhattan expanded fewer nodes on this puzzle.")
        elif len(man.explored) > len(euc.explored):
            print("Result: Euclidean expanded fewer nodes on this puzzle.")
        else:
            print("Result: Both expanded the same number of nodes on this puzzle.")

    print("Note: Both heuristics are admissible; Manhattan is usually more informed.")


def compare_a_star_heuristics_with_visuals(shuffle_moves: int = 10, seed: int = 0):
    random.seed(seed)
    base = board_8_puzzle()
    base.shuffle(shuffle_moves)

    start_matrix = [row.copy() for row in base.board]
    man_board = board_8_puzzle([row.copy() for row in start_matrix])
    euc_board = board_8_puzzle([row.copy() for row in start_matrix])

    root_dir = os.path.join("output", f"shuffled_{shuffle_moves}_seed{seed}")
    man_dir = os.path.join(root_dir, "manhattan")
    euc_dir = os.path.join(root_dir, "euclidean")

    print("Visual start board:")
    print(man_board)
    try:
        print(f"Generating visuals for Manhattan in: {man_dir}")
        algorithms(man_board).A_star(True, heuristic="manhattan", output_dir=man_dir)
        print(f"Generating visuals for Euclidean in: {euc_dir}")
        algorithms(euc_board).A_star(True, heuristic="euclidean", output_dir=euc_dir)
    except ModuleNotFoundError as exc:
        print(str(exc))
        print("(Visualizer requires matplotlib in your venv.)")

if __name__ == "__main__":
    print("Running 8-puzzle tests...")
    print("=" * 60)
    compare_a_star_heuristics()
    print("=" * 60)
    compare_a_star_heuristics_shuffled(shuffle_moves=25, seed=0)
    print("=" * 60)
    # Uncomment if you want PNG tree visuals (requires matplotlib)
    # compare_a_star_heuristics_with_visuals(shuffle_moves=10, seed=0)
    print("=" * 60)
    test_a_star(visual=False)
    print("=" * 60)
    test_bfs()
    print("Done.")
