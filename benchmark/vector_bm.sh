#!/bin/bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
DATA_DIR="$ROOT_DIR/results"

N_VALS=(2 4 8 10 12 14 16)
M_VALS=(1 3 7 9 11 13 15)

THREAD_LIST=(${THREADS:-16})
REPEATS=${REPEATS:-10}
NREPEAT=${NREPEAT:-20}

echo "=========================================="
echo " Part 2.6: OpenMP Matrix-Vector Benchmark"
echo "=========================================="
echo "Threads: ${THREAD_LIST[*]}"
echo "N exponents: ${N_VALS[*]} (Rows = 2^N)"
echo "M exponents: ${M_VALS[*]} (Cols = 2^M)"
echo "Repeats per config: $REPEATS"
echo "Internal repeats (-nrepeat): $NREPEAT"
echo "Output: results/vector.csv"
echo "=========================================="

mkdir -p "$DATA_DIR"
if [ ! -f "$ROOT_DIR/vector" ]; then
    echo "Compiling vector binary with OpenMP..."
    g++ -O3 -fopenmp "$ROOT_DIR/tp_openmp_part_2_vector.cpp" -o "$ROOT_DIR/vector"
fi

valid_shapes=0
for n in "${N_VALS[@]}"; do
    for m in "${M_VALS[@]}"; do
        if [ $((n + m)) -lt 30 ]; then
            valid_shapes=$((valid_shapes + 1))
        fi
    done
done
total_runs=$((valid_shapes * ${#THREAD_LIST[@]}))

current=0
for t in "${THREAD_LIST[@]}"; do
    export OMP_NUM_THREADS=$t
    echo "--- Benchmarking with OMP_NUM_THREADS=$t ---"

    for n in "${N_VALS[@]}"; do
        for m in "${M_VALS[@]}"; do
            if [ $((n + m)) -ge 30 ]; then
                echo "[SKIP] N=$n (2^$n), M=$m (2^$m) -> exceeds safe memory limit (>4GB / 32-bit int overflow)"
                continue
            fi

            current=$((current + 1))
            echo "[$current/$total_runs] (T=$t) N=$n (2^$n rows), M=$m (2^$m cols)..."

            for ((r=1; r<=REPEATS; r++)); do
                (cd "$DATA_DIR" && "$ROOT_DIR/vector" -N "$n" -M "$m" -nrepeat "$NREPEAT" > /dev/null)
            done
        done
    done
done

echo "=========================================="
echo "Benchmark completed! Results saved in results/vector.csv"
echo "=========================================="
