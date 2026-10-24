#!/bin/bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DATA_DIR="$SCRIPT_DIR/benchmark_data/thread_scaling"
CSV_FILE="$DATA_DIR/fib.csv"

CXX=${CXX:-g++}
NODES=${NODES:-10}
FS=${FS:-17}
NREPEAT=${NREPEAT:-20}
TARGET_SAMPLES=${SAMPLES:-10}
THREAD_LIST=(${THREADS:-1 2 4 8})

binary=$(mktemp "${TMPDIR:-/tmp}/openmp-fib.XXXXXX")
trap 'rm -f "$binary"' EXIT

mkdir -p "$DATA_DIR"
"$CXX" -O3 -fopenmp -DFS="$FS" "$SCRIPT_DIR/tp_openmp_part_3_fib.cpp" -o "$binary"

for threads in "${THREAD_LIST[@]}"; do
    if [[ -f "$CSV_FILE" ]]; then
        existing=$(awk -F, \
            -v threads="$threads" \
            -v nodes="$NODES" \
            -v start="$FS" \
            -v repeats="$NREPEAT" \
            '$1 == "\"sequential\"" && $2 == threads && $3 == nodes && $4 == start && $5 == repeats { count++ }
             END { print count + 0 }' "$CSV_FILE")
    else
        existing=0
    fi

    missing=$((TARGET_SAMPLES - existing))
    if ((missing <= 0)); then
        printf 'OMP_NUM_THREADS=%s: already has %s samples\n' "$threads" "$existing"
        continue
    fi

    printf 'OMP_NUM_THREADS=%s: running %s additional samples\n' "$threads" "$missing"
    for ((sample = 0; sample < missing; sample++)); do
        (cd "$DATA_DIR" && OMP_NUM_THREADS="$threads" "$binary" -N "$NODES" -nrepeat "$NREPEAT" > /dev/null)
    done
done

printf 'Results: %s\n' "$CSV_FILE"
