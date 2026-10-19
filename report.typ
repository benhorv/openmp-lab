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
