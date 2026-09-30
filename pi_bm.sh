#!/bin/bash

echo "Bonjour, $USER !"

echo "Pi Benchmark"

echo "=========================="
export OMP_NUM_THREADS=1
./pi -N 1000000
./pi -N 100000000
./pi -N 10000000000
./pi -N 1000000000000

export OMP_NUM_THREADS=2
./pi -N 1000000
./pi -N 100000000
./pi -N 10000000000
./pi -N 1000000000000

export OMP_NUM_THREADS=4
./pi -N 1000000
./pi -N 100000000
./pi -N 10000000000
./pi -N 1000000000000

export OMP_NUM_THREADS=8
./pi -N 1000000
./pi -N 100000000
./pi -N 10000000000
./pi -N 1000000000000

export OMP_NUM_THREADS=16
./pi -N 1000000
./pi -N 100000000
./pi -N 10000000000
./pi -N 1000000000000
