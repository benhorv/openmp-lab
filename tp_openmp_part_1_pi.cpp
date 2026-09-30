/*

This program will numerically compute the integral of

                  4/(1+x*x)

from 0 to 1.  The value of this integral is pi -- which
is great since it gives us an easy way to check the answer.

History: Written by Tim Mattson, 11/1999.
         Modified/extended by Jonathan Rouzaud-Cornabas, 10/2022
*/

#include <limits>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <sys/time.h>

#include <omp.h>

#include "csv_logger.hpp"

extern CSVLogger logger;

static long num_steps = 100000000;
double step;

using PiCalculator = double (*)(long num_steps, double step);

double pi_sequential(long num_steps, double step)
{

    int i;
    double x, sum = 0.0;

    for (i = 1; i <= num_steps; i++)
    {
        x = (i - 0.5) * step;
        sum = sum + 4.0 / (1.0 + x * x);
    }
    return sum * step;
}

// same as atomic, just not on the hardware level
// it's 4 times slower than atomic
double pi_critical(long num_steps, double step)
{

    int i;
    double x, sum = 0.0;

#pragma omp parallel for private(i, x) shared(sum) firstprivate(num_steps)
    for (i = 1; i <= num_steps; i++)
    {
        x = (i - 0.5) * step;
#pragma omp critical
        sum = sum + 4.0 / (1.0 + x * x);
    }
    return sum * step;
}

// all threads read one single shared variable, the threads take turns, and wait for eachother
// they have to sync at each iteration of the loop, and give the right of calculation to each other
// this takes a lot of time
double pi_atomic(long num_steps, double step)
{

    int i;
    double x, sum = 0.0;

#pragma omp parallel for private(i, x) shared(sum) firstprivate(num_steps)
    for (i = 1; i <= num_steps; i++)
    {
        x = (i - 0.5) * step;
#pragma omp atomic
        sum = sum + 4.0 / (1.0 + x * x);
    }
    return sum * step;
}

// here each thread works simultaneously, they calculate subsums
// it's summed up in the end
// it's about twice as fast as the sequential solution!
double pi_reduction(long num_steps, double step)
{

    int i;
    double x, sum = 0.0;

#pragma omp parallel for reduction(+ : sum) private (i, x) firstprivate(num_steps)
    for (i = 1; i <= num_steps; i++)
    {
        x = (i - 0.5) * step;
        sum = sum + 4.0 / (1.0 + x * x);
    }
    return sum * step;
}

double pi_split_atomic(long num_steps, double step)
{
    double sum = 0.0;
    #pragma omp parallel
    {
        int num_threads = omp_get_num_threads();
        int thread_id = omp_get_thread_num();
        double x, split_sum = 0.0;

        int start = 1 + thread_id * (num_steps / num_threads);
        int end = start + (num_steps / num_threads) - 1;
        for (int i = start; i <= end; i++)
        {
            x = (i - 0.5) * step;
            split_sum = split_sum + 4.0 / (1.0 + x * x);
        }
        #pragma omp atomic
        sum = sum + split_sum;
    }
    return sum * step;
}

double pi_split_critical(long num_steps, double step)
{
    double sum = 0.0;
    #pragma omp parallel
    {
        int num_threads = omp_get_num_threads();
        int thread_id = omp_get_thread_num();
        double x, split_sum = 0.0;

        int start = 1 + thread_id * (num_steps / num_threads);
        int end = start + (num_steps / num_threads) - 1;
        for (int i = start; i <= end; i++)
        {
            x = (i - 0.5) * step;
            split_sum = split_sum + 4.0 / (1.0 + x * x);
        }
        #pragma omp critical
        sum = sum + split_sum;
    }
    return sum * step;
}

double pi_split_sequential(long num_steps, double step)
{
    double sum = 0.0;
    int num_threads = omp_get_num_threads();
    int thread_id = omp_get_thread_num();
    double x, split_sum = 0.0;

    int start = 1 + thread_id * (num_steps / num_threads);
    int end = start + (num_steps / num_threads) - 1;
    for (int i = start; i <= end; i++)
    {
        x = (i - 0.5) * step;
        split_sum = split_sum + 4.0 / (1.0 + x * x);
    }
    sum = sum + split_sum;
    return sum * step;
}

double pi_split_reduction(long num_steps, double step)
{
    double sum = 0.0;
    #pragma omp parallel reduction(+:sum)
    {
        int num_threads = omp_get_num_threads();
        int thread_id = omp_get_thread_num();
        double x, split_sum = 0.0;

        int start = 1 + thread_id * (num_steps / num_threads);
        int end = start + (num_steps / num_threads) - 1;
        for (int i = start; i <= end; i++)
        {
            x = (i - 0.5) * step;
            split_sum = split_sum + 4.0 / (1.0 + x * x);
        }
        sum = sum + split_sum;
    }
    return sum * step;
}

// 1 2 3 4 5


// 6 7 8 9 10

void run_benchmark(const char *name, PiCalculator func, long num_steps, double step)
{
    int i;
    double x, sum = 0.0;

    step = 1.0 / (double)num_steps;

    // Timer products.
    struct timeval begin, end;

    gettimeofday(&begin, NULL);

    // run function
    double pi = func(num_steps, step);

    gettimeofday(&end, NULL);

    // Calculate time.
    double time = 1.0 * (end.tv_sec - begin.tv_sec) +
                  1.0e-6 * (end.tv_usec - begin.tv_usec);

    int threads = omp_get_max_threads();
    printf("\n %s with %d threads calculates pi with %ld steps is %lf in %lf seconds\n ", name, threads, num_steps, pi, time);
    logger.log(name, num_steps, pi, time, threads);
}

struct BenchmarkCase
{
    const char *name;
    PiCalculator func;
};

BenchmarkCase cases[] = {
    {"sequential", pi_sequential},
    {"reduction", pi_reduction},
    {"atomic", pi_atomic},
    {"critical", pi_critical},
    {"split_atomic", pi_split_atomic},
    {"split_sequential", pi_split_sequential},
    {"split_reduction", pi_split_reduction},
    {"split_critical", pi_split_critical},

};

int main(int argc, char **argv)
{
    CSVLogger logger("pi.csv");

    // Read command line arguments.
    for (int i = 0; i < argc; i++)
    {
        if ((strcmp(argv[i], "-N") == 0) || (strcmp(argv[i], "-num_steps") == 0))
        {
            num_steps = atol(argv[++i]);
            printf("  User num_steps is %ld\n", num_steps);
        }
        else if ((strcmp(argv[i], "-h") == 0) || (strcmp(argv[i], "-help") == 0))
        {
            printf("  Pi Options:\n");
            printf("  -num_steps (-N) <int>:      Number of steps to compute Pi (by default 100000000)\n");
            printf("  -help (-h):            print this message\n\n");
            exit(1);
        }
    }

    for (const auto &test : cases)
    {
        run_benchmark(test.name, test.func, num_steps, step);
    }
}
