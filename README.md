# OpenMP Practical Lab

## Build

```bash
# Part 1: Pi
g++ -O3 -fopenmp tp_openmp_part_1_pi.cpp -o pi

# Part 2: Matrix-Vector
g++ -O3 -fopenmp tp_openmp_part_2_vector.cpp -o vector

# Part 3: Fibonacci
g++ -O3 -fopenmp -DFS=17 tp_openmp_part_3_fib.cpp -o fib
```

## Run

You can control the number of threads with `OMP_NUM_THREADS`:

```bash
# Part 1: Pi (-N <num_steps>)
OMP_NUM_THREADS=4 ./pi -N 100000000

# Part 2: Matrix-Vector (-N <log2_rows> -M <log2_cols> -nrepeat <count>)
OMP_NUM_THREADS=4 ./vector -N 9 -M 9 -nrepeat 100

# Part 3: Fibonacci (-N <num_nodes> -nrepeat <count>)
OMP_NUM_THREADS=4 ./fib -N 10 -nrepeat 20
```

## Run Benchmarks

Alternatively, run the automated benchmark scripts:

```bash
./benchmark/pi_bm.sh
./benchmark/vector_bm.sh
./benchmark/fib_bm.sh
```
