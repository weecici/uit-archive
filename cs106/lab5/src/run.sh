#!/usr/bin/env bash

COMMAND="uv run pacman.py"
LOG_DIR="logs"
STUDENT_ID=23520199
DEPTH=2
MAX_PARALLEL=10

CHOSEN_LAYOUTS=(
  "originalClassic"
  "trickyClassic"
  "trappedClassic"
  "contestClassic"
  "capsuleClassic"
)

EVAL_FUNCS=(
  "scoreEvaluationFunction"
  "betterEvaluationFunction"
)

AGENT_TYPES=(
  "MinimaxAgent"
  "AlphaBetaAgent"
  "ExpectimaxAgent"
)


TASK_LIST=$(mktemp)

for EVAL_FUNC in "${EVAL_FUNCS[@]}"; do
    for LAYOUT in "${CHOSEN_LAYOUTS[@]}"; do
        for AGENT_TYPE in "${AGENT_TYPES[@]}"; do
            # Create directory structure ahead of time
            AGENT_LOG_DIR="$LOG_DIR/$EVAL_FUNC/$LAYOUT/$AGENT_TYPE"
            mkdir -p "$AGENT_LOG_DIR"

            for NUM in $(seq 0 4); do
                SEED=$((STUDENT_ID + NUM))
                LOG_FILE_PATH="$AGENT_LOG_DIR/seed${SEED}.log"
                
                # Append the full command to the task list
                echo "$COMMAND -a evalFn=${EVAL_FUNC},depth=${DEPTH} -p ${AGENT_TYPE} -l ${LAYOUT} -s ${SEED} -q --frameTime 0 > $LOG_FILE_PATH 2>&1" >> "$TASK_LIST"
            done
        done
    done
done

cat "$TASK_LIST" | xargs -I {} -P "$MAX_PARALLEL" bash -c "{}"

rm "$TASK_LIST"
echo "All tasks completed."
