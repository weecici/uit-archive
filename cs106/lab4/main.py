import os
import time
from glob import glob
from ortools.algorithms.python import knapsack_solver

TIME_LIMIT = 3 * 60

#
POSSIBLE_SIZES = [50, 100, 200, 500, 1000, 2000, 5000, 10000]
TEST_CASE_DIR = "test_cases"
CAPACITY_DIR = "R01000"
FILENAME = "s007.kp"

#
LOG_DIR = "logs"


def load_test_case(
    test_type: int, test_size: int
) -> tuple[list[int], list[list[int]], list[int]]:
    """Loads the test cases for the knapsack problem.
    Returns:
        A tuple containing the (capacities, profits, weights) and  for the knapsack problem.
    """

    assert test_type >= 0 and test_type <= 12, "Invalid test type"
    assert test_size in POSSIBLE_SIZES, "Invalid test size"

    SIZE_DIR = f"n{test_size:05d}"
    TEST_TYPE_DIR = glob(os.path.join(TEST_CASE_DIR, f"{test_type:02d}*"))[0]

    profits = []
    weights = [[]]
    with open(os.path.join(TEST_TYPE_DIR, SIZE_DIR, CAPACITY_DIR, FILENAME)) as f:
        lines = f.readlines()
        capacities = [int(lines[2].strip())]
        for i in range(4, len(lines)):
            profit, weight = map(int, lines[i].strip().split())
            profits.append(profit)
            weights[0].append(weight)

    return capacities, profits, weights


if __name__ == "__main__":
    solver = knapsack_solver.KnapsackSolver(
        knapsack_solver.SolverType.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER,
        "23520199 - CS106 Assignment 4",
    )

    os.makedirs(LOG_DIR, exist_ok=True)
    csv_file_path = os.path.join(LOG_DIR, "result_table.csv")

    with open(csv_file_path, "a", encoding="utf-8") as f_csv:
        if os.stat(csv_file_path).st_size == 0:
            f_csv.write("Test Case,Value,Total Weight,Time Taken,Optimal?\n")

        for test_type in range(13):
            for test_size in POSSIBLE_SIZES:

                pattern = os.path.join(TEST_CASE_DIR, f"{test_type:02d}*")
                TEST_TYPE_DIR = glob(pattern)[0].split(os.sep)[-1]
                SIZE_DIR = f"n{test_size:05d}"
                test_case_name = f"{SIZE_DIR}_{CAPACITY_DIR}_{FILENAME.split('.')[0]}"
                log_file_path = os.path.join(
                    LOG_DIR, TEST_TYPE_DIR, f"{test_case_name}.log"
                )
                if os.path.exists(log_file_path):
                    print(
                        f"Skipping {TEST_TYPE_DIR}/{test_case_name} (log already exists)"
                    )
                    continue

                capacities, profits, weights = load_test_case(
                    test_type=test_type,
                    test_size=test_size,
                )

                solver.init(profits, weights, capacities)
                solver.set_time_limit(TIME_LIMIT)

                start = time.time()
                computed_value = solver.solve()
                time_taken = time.time() - start

                is_optimal = "Yes" if solver.is_solution_optimal() else "No"

                total_weight = 0
                for i in range(len(profits)):
                    if solver.best_solution_contains(i):
                        total_weight += weights[0][i]

                os.makedirs(os.path.join(LOG_DIR, TEST_TYPE_DIR), exist_ok=True)
                with open(log_file_path, "w") as f:
                    f.write(f"Total value: {computed_value}\n")
                    f.write(f"Total weight: {total_weight}\n")
                    f.write(f"Is optimal: {is_optimal}\n")
                    f.write(f"Time taken: {time_taken}\n")

                f_csv.write(
                    f"{TEST_TYPE_DIR}/{test_case_name},{computed_value},{total_weight},{time_taken:.2f},{is_optimal}\n"
                )
                f_csv.flush()  # Force write to file instantly instead of buffering!

                print(
                    f"Finished {TEST_TYPE_DIR}/{test_case_name} | Value: {computed_value} | Optimal: {is_optimal} | Time: {time_taken:.2f}s"
                )

                del capacities, profits, weights
