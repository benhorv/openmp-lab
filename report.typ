#set page(
  paper: "a4",
  header: align(right)[
    #text(size: 8.5pt, fill: luma(100))[OpenMP Report - Benedek Horváth]
  ],
  footer: context align(center)[
    #text(size: 8.5pt, fill: luma(120))[#counter(page).display("1 / 1", both: true)]
  ]
)

#set text(
  font: ("New Computer Modern"),
  lang: "en",
)

#set par(
  justify: true,
  leading: 0.65em,
)

#show heading: set text(weight: "bold")
#set heading(numbering: "1.1")

// Title
#v(1em)
#align(center)[
  #text(size: 18pt, weight: "bold")[OpenMP Practical Lab Report]
]
#v(1.5em)

Benchmark tests executed on 16-core AMD CPU, 16GB of RAM, on Arch Linux. Worked together with Tomoki Mengel.

= Calculating Pi

#figure(
  image("figures/runtime_vs_threads.svg", width: 100%),
  caption: [
    *Execution Time vs. Thread Count*
  ],
) <fig-runtime-comparison>

#figure(
  image("figures/speedup_vs_threads.svg", width: 100%),
  caption: [
    *Speedup vs. Thread Count*
  ],
) <fig-speedup-comparison>

#v(2em)

== Performance analysis

I have displayed the differrent methods on the two graphs. Both graphs show the runtime of the benchmarks by thread count. The first grahp shows an increase of the runtime with the increase of the number of threads. It's because the synchronisation between threads happen in each loop, costing a lot of performance. In the other cases, where sequential and the manual splits are displayed, we can see a decline in execution time, which is because the calculation is actually distributed between the threads, and the costy synchronisation is executed only as many time as many threads there are (16 times in case of 16 threads for example).

= Matrix-Vector Calculation

#figure(
  image("figures/part2_scaling.svg", width: 100%),
  caption: [
    *Matrix-Vector Strong Scaling (Execution Time and Speedup)*
  ],
) <fig-vector-scaling>

#v(2em)

== Performance analysis

The graphs above show the performance differences between different methods, showing execution time and speedup as the thread count increases. The sequential version remains constant as expected. In the parallel reduction method, the loop over the rows is distributed across thraeds using OpenMP reduction, which makes runtime faster with a speedup of 3.9x with 8 threads. The SIMD method improves performance too by vectorising the inner row multiplications. Parallelising the floating point operations earns additional speedup, resulting in a 14x speedup.

#pagebreak()

= Fibonacci List

#figure(
  image("figures/part3_scaling.svg", width: 100%),
  caption: [
    *Fibonacci Workload Scaling by Scheduling Strategy (Execution Time and Speedup)*
  ],
) <fig-fib-scaling>

#v(2em)

== Performance analysis

We can see the different scheduling strategies on the diagrams, comparing their execution time and speedup across thread counts. The recursive Fibonacci calculation is not balanced, because computing higher Fibonacci numbers requires (exponentially) more operations, resulting in varying wrokload. In the static scheduling strategy, iterations are divided into fixed chunks between threads, so threads assigned to larger numbers do most of the calculation while other threads finish early and stay idle, leading to a modest speedup of only about 1.6x at 8 threads. However, the dynamic scheduling strategy allocates tasks to threads on demand as soon as they become available. This enables distributing the workload better, leading to much better thread utilisation and achieving a speedup of around 2.9x at 4 threads.

We had problems running the simulation, because initially we didn't understand why we don't see a difference between different strategies. As it turns out, the default configuration only worked on 7-8 numbers, so it wouldn't really make a difference in performance, since my computer has 16 threads. It means, that whatever the strategy is, the computation takes as long as the greates fibonacci number is calculated on the one of the threads. After realising, I adjusted the number of threads to a lower number, and also made the number of elements to be calculated higher, so the difference betweeen each strategy is more visible.
