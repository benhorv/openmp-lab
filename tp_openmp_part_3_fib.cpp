/*
**  HISTORY: Written by Tim Mattson, Nov 1999.
*            Modified and extended by Jonathan Rouzaud-Cornabas, Oct 2022
*/

#include <limits>
#include <cstdio>
#include <cstdlib>
#include <cstring>

#include <algorithm>

#include <vector>
#include <omp.h>

#include "csv_logger.hpp"

static int N = 40;

#ifndef FS
#define FS 13
#endif

typedef struct node
{
   int data;
   int fibdata;
   struct node *next;
} Node;

int fib(int n)
{
   int x, y;
   if (n < 2)
   {
      return (n);
   }
   else
   {
      x = fib(n - 1);
      y = fib(n - 2);
      return (x + y);
   }
}

void processwork(struct node *p)
{
   int n;
   n = p->data;
   p->fibdata = fib(n);
}

struct node *init_list(struct node *p)
{
   int i;
   struct node *head = NULL;
   struct node *temp = NULL;

   head = (struct node *)malloc(sizeof(struct node));
   p = head;
   p->data = FS;
   p->fibdata = 0;
   for (i = 0; i < N; i++)
   {
      temp = (struct node *)malloc(sizeof(struct node));
      p->next = temp;
      p = temp;
      p->data = FS + i + 1;
      p->fibdata = i + 1;
   }
   p->next = NULL;
   return head;
}

using FibProcessor = void (*)(std::vector<Node *> &nodes);

void process_sequential(std::vector<Node *> &nodes)
{
   //while (p != NULL)
      //{
      //  p = p->next;
      //}
   for (int index = static_cast<int>(nodes.size()) - 1; index >= 0; index--)
   {
      processwork(nodes[index]);
   }
}

void process_parallel(std::vector<Node *> &nodes)
{
#pragma omp parallel for
   for (int index = static_cast<int>(nodes.size()) - 1; index >= 0; index--)
   {
      processwork(nodes[index]);
   }
}

void process_parallel_static(std::vector<Node *> &nodes)
{
#pragma omp parallel for schedule(static)
   for (int index = static_cast<int>(nodes.size()) - 1; index >= 0; index--)
   {
      processwork(nodes[index]);
   }
}

void process_parallel_dynamic(std::vector<Node *> &nodes)
{
#pragma omp parallel for schedule(dynamic)
   for (int index = static_cast<int>(nodes.size()) - 1; index >= 0; index--)
   {
      processwork(nodes[index]);
   }
}

long long fib_checksum(const std::vector<Node *> &nodes)
{
   long long checksum = 0;
   for (const Node *current : nodes)
   {
      checksum += current->fibdata;
   }
   return checksum;
}

long long run_benchmark(const char *name, FibProcessor func, std::vector<Node *> &nodes,
                        int nrepeat, CSVLogger &fib_logger)
{
   // Timer products.
   double begin = omp_get_wtime();
   for (int repeat = 0; repeat < nrepeat; repeat++)
   {
      func(nodes);
   }
   double end = omp_get_wtime();

   // Calculate time.
   double time = end - begin;
   long long checksum = fib_checksum(nodes);
   int threads = omp_get_max_threads();

   printf("  %s with %d threads computes %zu Fibonacci values; checksum %lld in %f seconds\n",
          name, threads, nodes.size(), checksum, time);
   fib_logger.log(name, threads, N, FS, nrepeat, checksum, time);
   return checksum;
}

struct BenchmarkCase
{
   const char *name;
   FibProcessor func;
};

BenchmarkCase cases[] = {
    {"sequential", process_sequential},
    {"parallel", process_parallel},
   {"parallel_static", process_parallel_static},
    {"parallel_dynamic", process_parallel_dynamic},
};

int main(int argc, char *argv[])
{
   int nrepeat = 1;

   // Read command line arguments.
   for (int i = 0; i < argc; i++)
   {
      if ((strcmp(argv[i], "-N") == 0) || (strcmp(argv[i], "-num_node") == 0))
      {
         N = atoi(argv[++i]);
         printf("  User num_node is %d\n", N);
      }
      else if (strcmp(argv[i], "-nrepeat") == 0)
      {
         nrepeat = atoi(argv[++i]);
      }
      else if ((strcmp(argv[i], "-h") == 0) || (strcmp(argv[i], "-help") == 0))
      {
         printf("  Fib Options:\n");
         printf("  -num_node (-N) <int>:      Number of node computing fibonnaci numbers (by default 5)\n");
         printf("  -nrepeat <int>:            number of repetitions per benchmark (default: 1)\n");
         printf("  -help (-h):            print this message\n\n");
         exit(1);
      }
   }

   struct node *p = NULL;
   struct node *temp = NULL;
   struct node *head = NULL;

   printf("Process linked list\n");
   printf("  Each linked list node will be processed by function 'processwork()'\n");
   printf("  Each ll node will compute %d fibonacci numbers beginning with %d\n", N, FS);

   p = init_list(p);
   head = p;

   std::vector<Node*> nodes;

   while (p != NULL)
   {
      nodes.push_back(p);
      p = p->next;
   }

   // we tried: sequential, parallel for, parallel schedule(dynamic)
   // somehow didn't make a difference
   // we tried with 8 and 16 threads
   // that was the problem!
   // we usually had only 7-9 tasks, because FS was set to 38
   // I changed FS to a smaller number, and made N greater
   // I also limited the number of threads to 2 and 4 so the scheduling would really make sense
   // also, reverse order also mattered, but would be nicer with sorting (try?)
   // schedule has really an impact, but normal parallel works too

   CSVLogger fib_logger("fib.csv");
   long long expected_checksum = -1;
   for (const auto &test : cases)
   {
      long long checksum = run_benchmark(test.name, test.func, nodes, nrepeat, fib_logger);
      if (expected_checksum == -1)
      {
         expected_checksum = checksum;
      }
      else if (checksum != expected_checksum)
      {
         printf("  Error: checksum %lld != expected checksum %lld\n", checksum, expected_checksum);
      }
   }

   p = head;
   while (p != NULL)
   {
      printf("%d : %d\n", p->data, p->fibdata);
      temp = p->next;
      free(p);
      p = temp;
   }
   free(p);

   return 0;
}
