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
    return sum;
}

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
    return sum;
}

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
    return sum;
}

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

    printf("\n %s pi with %ld steps is %lf in %lf seconds\n ", name, num_steps, pi, time);
    logger.log(name, num_steps, pi, time);
}

struct BenchmarkCase
{
    const char *name;
    PiCalculator func;
};

BenchmarkCase cases[] = {
    {"sequential", pi_sequential},
    {"critical", pi_critical},
    {"atomic", pi_atomic},

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
