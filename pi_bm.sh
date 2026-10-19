#!/bin/bash

echo "Bonjour, $USER !"
echo "Pi Benchmark"
echo "=========================="

# Configuration
MIN_STEPS=${MIN_STEPS:-10000}           # smallest problem size
MAX_STEPS=${MAX_STEPS:-100000000}       # largest problem size (1T is too slow for sequential)
STEP_MULTIPLIER=${STEP_MULTIPLIER:-100} # multiply steps by this each iteration
MAX_THREADS=${MAX_THREADS:-$(nproc)}    # max threads, defaults to number of CPUs
REPEATS=${REPEATS:-10}                  # number of times each test is repeated

# Build thread counts as powers of 2 up to MAX_THREADS
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

for threads in "${THREAD_COUNTS[@]}"; do
    export OMP_NUM_THREADS=$threads
    steps=$MIN_STEPS
    while [ $steps -le $MAX_STEPS ]; do
        for ((r=1; r<=REPEATS; r++)); do
            ./pi -N $steps
        done
        steps=$((steps * STEP_MULTIPLIER))
    done
done
