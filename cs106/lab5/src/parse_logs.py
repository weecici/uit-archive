import os
import glob
import numpy as np
import datetime

base_dir = "logs"
eval_funcs = ["scoreEvaluationFunction", "betterEvaluationFunction"]
maps = [
    "originalClassic",
    "trickyClassic",
    "trappedClassic",
    "contestClassic",
    "capsuleClassic",
]
agents = ["MinimaxAgent", "AlphaBetaAgent", "ExpectimaxAgent"]

summary_file_path = "logs/summary_logs.txt"

with open(summary_file_path, "w") as summary_file:
    summary_file.write(f"--- PACMAN AI LOG SUMMARY ---\n")
    summary_file.write(f"Generated at: {datetime.datetime.now()}\n\n")

    for ef in eval_funcs:
        summary_file.write(
            f"===========================================================\n"
        )
        summary_file.write(f"EVALUATION FUNCTION: {ef}\n")
        summary_file.write(
            f"===========================================================\n\n"
        )

        for m in maps:
            summary_file.write(f"  MAP: {m}\n")
            summary_file.write(
                f"  --------------------------------------------------\n"
            )
            for a in agents:
                scores = []
                wins = []
                times = []
                path = os.path.join(base_dir, ef, m, a)

                # Check mapping exists
                if not os.path.exists(path):
                    continue

                summary_file.write(f"    AGENT: {a}\n")

                # read files
                for seed in range(23520199, 23520204):
                    log_file = os.path.join(path, f"seed{seed}.log")
                    if os.path.exists(log_file):
                        with open(log_file, "r") as f:
                            lines = [l.strip() for l in f.readlines() if l.strip()]
                            if len(lines) >= 3:
                                time_s = float(lines[-1])
                                is_win = lines[-2] == "True"
                                score = float(lines[-3])
                                scores.append(score)
                                wins.append(1 if is_win else 0)
                                times.append(time_s)
                                summary_file.write(
                                    f"      Seed {seed}: Score: {score:>7.1f} | Win: {'Yes' if is_win else 'No ':>3} | Time: {time_s:>6.3f}s\n"
                                )

                if scores:
                    mean_score = np.mean(scores)
                    std_score = np.std(scores)
                    win_rate = np.mean(wins) * 100
                    mean_time = np.mean(times)
                    max_score = np.max(scores)
                    min_score = np.min(scores)

                    summary_file.write(
                        f"      -> SUMMARY: Win Rate: {win_rate:>5.1f}% | Avg Score: {mean_score:>8.2f} (±{std_score:>8.2f}) | Min: {min_score:>7.1f} | Max: {max_score:>7.1f} | Avg Time: {mean_time:>6.3f}s\n"
                    )
                else:
                    summary_file.write(f"      -> NO LOGS FOUND\n")
            summary_file.write("\n")

print(f"Summary successfully written to {os.path.abspath(summary_file_path)}")
