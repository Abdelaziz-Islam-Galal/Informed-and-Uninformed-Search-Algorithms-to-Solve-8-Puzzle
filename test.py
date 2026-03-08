from board import board_8_puzzle
from algorithms.algorithms import algorithms
from algorithms.reporting import generate_full_report

import os
import random
import shutil
import stat
import time


OUTPUT_ROOT: str = "output"
BFS_DIR = os.path.join(OUTPUT_ROOT, "bfs")
DFS_DIR = os.path.join(OUTPUT_ROOT, "dfs")
IDS_DIR = os.path.join(OUTPUT_ROOT, "ids")
A_MAN_DIR = os.path.join(OUTPUT_ROOT, "a_star_manhattan")
A_EUC_DIR = os.path.join(OUTPUT_ROOT, "a_star_euclidean")

SUBMISSION_INITIAL = [[1, 2, 5], [3, 4, 0], [6, 7, 8]]
VISUALIZE = False

def _clear_output_dir(output_root: str = "output") -> None:
    """Delete output_root entirely so each run starts fresh.

    On Windows, some files may be marked read-only; onerror makes deletion robust.
    """

    def _onerror(func, path, exc_info):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            raise

    if os.path.isdir(output_root):
        shutil.rmtree(output_root, onerror=_onerror)
    os.makedirs(output_root, exist_ok=True)

def _moves_string(result: algorithms.result) -> str:
    if not result.goal_state:
        return "N/A"
    path = result.goal_state.get_path()
    move_map = {"up": "U", "down": "D", "left": "L", "right": "R"}
    moves = [move_map.get(s.move, s.move) for s in path[1:]]
    return " ".join(m for m in moves if m)

def _print_result(name: str, result: algorithms.result) -> None:
    print(f"{name}:")
    print(f"  Solved: {result.goal_state is not None}")
    print(f"  Expanded nodes: {len(result.explored)}")
    print(f"  Cost of path: {result.goal_state.level if result.goal_state else 'N/A'}")
    print(f"  Search depth: {result.max_depth}")
    print(f"  Moves (U/D/L/R): {_moves_string(result)}")
    print(f"  Time: {result.time_taken:.4f} sec")


def run_bfs(board: board_8_puzzle) -> algorithms.result:
    result = algorithms(board.copy()).bfs(VISUALIZE, BFS_DIR)
    _print_result("BFS", result)
    return result


def run_dfs(board: board_8_puzzle) -> algorithms.result:
    result = algorithms(board.copy()).dfs(VISUALIZE, DFS_DIR)
    _print_result("DFS", result)
    return result


def run_ids(board: board_8_puzzle) -> algorithms.result:
    result = algorithms(board.copy()).ids(VISUALIZE, IDS_DIR)
    _print_result("IDS", result)
    return result


def run_a_star_manhattan(board: board_8_puzzle) -> algorithms.result:
    result = algorithms(board.copy()).A_star(VISUALIZE, heuristic="manhattan", output_dir=A_MAN_DIR)
    _print_result("A* (Manhattan)", result)
    return result


def run_a_star_euclidean(board: board_8_puzzle) -> algorithms.result:
    result = algorithms(board.copy()).A_star(VISUALIZE  , heuristic="euclidean", output_dir=A_EUC_DIR)
    _print_result("A* (Euclidean)", result)
    return result


def run_submission_case() -> None:
    board = board_8_puzzle([row.copy() for row in SUBMISSION_INITIAL])
    print("CASE 1: SUBMISSION (fixed)")
    print("Start board:")
    print(board)
    print("-" * 60)
    run_bfs(board)
    run_dfs(board)
    run_ids(board)
    run_a_star_manhattan(board)
    run_a_star_euclidean(board)
    

def generate_report(board: board_8_puzzle | None = None, out_file: str = "report.pdf") -> None:
    if board is None:
        board = board_8_puzzle([row.copy() for row in SUBMISSION_INITIAL])

    _clear_output_dir(OUTPUT_ROOT)
    results: dict[str, algorithms.result] = {}
    results["BFS"]            = run_bfs(board)
    results["DFS"]            = run_dfs(board)
    results["IDS"]            = run_ids(board)
    results["A* Manhattan"]   = run_a_star_manhattan(board)
    results["A* Euclidean"]   = run_a_star_euclidean(board)

    generate_full_report(
        results=results,
        start_board=board,
        out_file=out_file,
    )


def find_astar_heuristic_difference_example(
    *,
    shuffle_moves_options: list[int] | None = None,
    seed_range: range = range(0, 300),
    time_limit_seconds: float = 15.0,
) -> board_8_puzzle | None:
    """Find a solvable board where A* expands different nodes under the two heuristics.

    Note: Manhattan and Euclidean are both admissible for the 8-puzzle. The point of this
    function is to find a harder instance where Manhattan (usually more informed) leads
    to fewer expansions than Euclidean.
    """

    if shuffle_moves_options is None:
        shuffle_moves_options = [25, 30, 35, 40, 45, 50]

    start_time = time.time()
    for shuffle_moves in shuffle_moves_options:
        for seed in seed_range:
            if time.time() - start_time > time_limit_seconds:
                print("Timed out without finding a difference example.")
                return None

            random.seed(seed)
            board = board_8_puzzle()
            board.shuffle(shuffle_moves)

            man = algorithms(board.copy()).A_star(False, heuristic="manhattan")
            euc = algorithms(board.copy()).A_star(False, heuristic="euclidean")

            if man.goal_state is None or euc.goal_state is None:
                continue

            man_expanded = len(man.explored)
            euc_expanded = len(euc.explored)

            if man_expanded != euc_expanded:
                print("FOUND example board")
                print(f"shuffle_moves={shuffle_moves}, seed={seed}")
                print("Board:")
                print(board)
                print(f"Expanded nodes: Manhattan={man_expanded}, Euclidean={euc_expanded}")
                print(f"Cost of path:   Manhattan={man.goal_state.level}, Euclidean={euc.goal_state.level}")
                return board

    print("No difference found in the given search budget.")
    return None


if __name__ == "__main__":
    TEST = [[8,7,6], [5,4,3], [2,1,0]]
    test_puzzle = board_8_puzzle(TEST)
    generate_report(test_puzzle, out_file="test_report.pdf")
