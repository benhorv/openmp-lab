#!/bin/bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
DATA_DIR="$ROOT_DIR/results"

echo "Bonjour, $USER !"
echo "Pi Benchmark"
echo "=========================="

MIN_STEPS=${MIN_STEPS:-10000}
MAX_STEPS=${MAX_STEPS:-100000000}
STEP_MULTIPLIER=${STEP_MULTIPLIER:-100}
MAX_THREADS=${MAX_THREADS:-$(nproc)}
REPEATS=${REPEATS:-10}

THREAD_COUNTS=()
t=1
while [ $t -le $MAX_THREADS ]; do
    THREAD_COUNTS+=($t)
    t=$((t * 2))
done

echo "Thread counts: ${THREAD_COUNTS[@]}"
echo "Steps: $MIN_STEPS to $MAX_STEPS (x$STEP_MULTIPLIER)"
echo "Repeats: $REPEATS"
echo "=========================="

mkdir -p "$DATA_DIR"
if [ ! -f "$ROOT_DIR/pi" ]; then
    g++ -O3 -fopenmp "$ROOT_DIR/tp_openmp_part_1_pi.cpp" -o "$ROOT_DIR/pi"
fi

for threads in "${THREAD_COUNTS[@]}"; do
    export OMP_NUM_THREADS=$threads
    steps=$MIN_STEPS
    while [ $steps -le $MAX_STEPS ]; do
        for ((r=1; r<=REPEATS; r++)); do
            (cd "$DATA_DIR" && "$ROOT_DIR/pi" -N $steps)
        done
        steps=$((steps * STEP_MULTIPLIER))
    done
done
