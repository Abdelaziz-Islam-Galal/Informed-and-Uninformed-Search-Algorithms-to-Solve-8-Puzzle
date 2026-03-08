from board import board_8_puzzle
from algorithms.algorithms import algorithms

import random


SUBMISSION_INITIAL = [[1, 2, 5], [3, 4, 0], [6, 7, 8]]


def _moves_string(result: algorithms.result) -> str:
    if not result.goal_state:
        return "N/A"
    path = result.goal_state.get_path()
    move_map = {"up": "U", "down": "D", "left": "L", "right": "R"}
    moves = [move_map.get(s.move, s.move) for s in path[1:]]
    return " ".join(m for m in moves if m)


def _search_depth(result: algorithms.result) -> int:
    return max((state.level for state in result.explored), default=0)


def _print_result(name: str, result: algorithms.result) -> None:
    print(f"{name}:")
    print(f"  Solved: {result.goal_state is not None}")
    print(f"  Expanded nodes: {len(result.explored)}")
    print(f"  Cost of path: {result.goal_state.level if result.goal_state else 'N/A'}")
    print(f"  Search depth: {_search_depth(result)}")
    print(f"  Moves (U/D/L/R): {_moves_string(result)}")
    print(f"  Time: {result.time_taken:.4f} sec")


def run_bfs(board: board_8_puzzle) -> algorithms.result:
    result = algorithms(board.copy()).bfs(False)
    _print_result("BFS", result)
    return result


def run_dfs(board: board_8_puzzle) -> algorithms.result:
    result = algorithms(board.copy()).dfs(False)
    _print_result("DFS", result)
    return result


def run_ids(board: board_8_puzzle) -> algorithms.result:
    result = algorithms(board.copy()).ids(False)
    _print_result("IDS", result)
    return result


def run_a_star_manhattan(board: board_8_puzzle) -> algorithms.result:
    result = algorithms(board.copy()).A_star(False, heuristic="manhattan")
    _print_result("A* (Manhattan)", result)
    return result


def run_a_star_euclidean(board: board_8_puzzle) -> algorithms.result:
    result = algorithms(board.copy()).A_star(False, heuristic="euclidean")
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


def run_random_case(*, shuffle_moves: int = 25, seed: int = 0) -> None:
    random.seed(seed)
    board = board_8_puzzle()
    board.shuffle(shuffle_moves)

    print("CASE 2: RANDOM (shuffled)")
    print(f"Shuffle moves: {shuffle_moves}, seed: {seed}")
    print("Start board:")
    print(board)
    print("-" * 60)
    # On harder boards BFS/DFS/IDS can be very slow, so default to A* only.
    run_a_star_manhattan(board)
    run_a_star_euclidean(board)


if __name__ == "__main__":
    run_submission_case()
    run_random_case(shuffle_moves=25, seed=0)