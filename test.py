from board import board_8_puzzle
from algorithms.algorithms import algorithms
from algorithms.reporting import generate_full_report

import os
import random
import shutil
import stat


def _save_report(result: algorithms.result, out_file: str) -> None:
    try:
        result.save_report(out_file)
    except ModuleNotFoundError as exc:
        print(str(exc))
        if out_file.lower().endswith(".pdf"):
            fallback = os.path.splitext(out_file)[0] + ".txt"
            print(f"Falling back to text report: {fallback}")
            result.save_report(fallback)


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


SUBMISSION_INITIAL = [[2, 1, 5], [3, 4, 0], [6, 7, 8]]


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


def run_submission_visualization(*, output_root: str = "output", include_dfs: bool = False) -> None:
    """Generate visualization PNGs for the submission case only.

    Requirements implemented:
    - Clear output_root every time before generating.
    - Put each model's PNGs under output_root/<model_name>/
    - Do NOT visualize the random case.
    """

    # Requirement: each run should replace the previous run output entirely.
    _clear_output_dir(output_root)

    board = board_8_puzzle([row.copy() for row in SUBMISSION_INITIAL])

    # Requirement: each model gets its own folder under output/.
    bfs_dir = os.path.join(output_root, "bfs")
    dfs_dir = os.path.join(output_root, "dfs")
    ids_dir = os.path.join(output_root, "ids")
    a_man_dir = os.path.join(output_root, "a_star_manhattan")
    a_euc_dir = os.path.join(output_root, "a_star_euclidean")

    os.makedirs(dfs_dir, exist_ok=True)  # created even if DFS visuals are skipped
    os.makedirs(ids_dir, exist_ok=True)  # IDS currently has no PNG visualization output.

    try:
        algorithms(board.copy()).bfs(True, output_dir=bfs_dir)

        # DFS can expand a huge number of nodes before it finds the (short) solution,
        # which would generate a massive number of PNGs and make the run very slow.
        if include_dfs:
            algorithms(board.copy()).dfs(True, output_dir=dfs_dir)
        algorithms(board.copy()).A_star(True, heuristic="manhattan", output_dir=a_man_dir)
        algorithms(board.copy()).A_star(True, heuristic="euclidean", output_dir=a_euc_dir)
    except ModuleNotFoundError as exc:
        print(str(exc))
        print("(Visualizer requires matplotlib in your active environment.)")


def generate_report(
    board: board_8_puzzle | None = None,
    out_file: str = "report.pdf",
) -> None:
    """Run all 5 algorithms on *board* and produce a single combined PDF report.

    Each call deletes the old report and generates a fresh one.
    """
    if board is None:
        board = board_8_puzzle([row.copy() for row in SUBMISSION_INITIAL])

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


if __name__ == "__main__":
    generate_report()
