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

= Calculating Pi

#figure(
  image("figures/runtime_vs_threads.svg", width: 100%),
  caption: [
    *Execution Time vs. Thread Count*
  ],
) <fig-runtime-comparison>

#v(2em)

== Performance analysis

I have displayed the differrent methods on the two graphs. Both graphs show the runtime of the benchmarks by thread count. The first grahp shows an increase of the runtime with the increase of the number of threads. It's because the synchronisation between threads happen in each loop, costing a lot of performance. In the other cases, where sequential and the manual splits are displayed, we can see a decline in execution time, which is because the calculation is actually distributed between the threads, and the costy synchronisation is executed only as many time as many threads there are (16 times in case of 16 threads for example).

= Matrix-Vector Calculation

== Sequential

=== Performance

#figure(
  image("figures/vector_sequential.svg", width: 100%),
  caption: [
    *Sequential Matrix-Vector Performance*
  ],
) <fig-vector-sequential>

=== Analysis