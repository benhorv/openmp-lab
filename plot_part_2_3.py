#!/usr/bin/env python3
import os

import matplotlib.pyplot as plt
import pandas as pd

DATA_DIR = "benchmark_data"
FIGURE_DIR = "figures"

COLORS = {
    "sequential": "#3E7652",
    "parallel": "#D1783C",
    "simd_reduction": "#397C8A",
    "parallel_static": "#3978A0",
    "parallel_dynamic": "#A84F4F",
}


def plot(csv_path, columns, methods, labels, title, output, speedup=False):
    data = pd.read_csv(csv_path, header=None, names=columns)
    data["method"] = data["method"].str.strip('"')
    data["runtime_ms"] = data["time"] / data["nrepeat"] * 1000
    summary = data.groupby(["method", "threads"])["runtime_ms"].agg(["mean", "std"]).reset_index()

    if speedup:
        baseline = summary[(summary["method"] == "sequential") & (summary["threads"] == 1)].iloc[0]
        baseline_mean, baseline_std = baseline["mean"], baseline["std"]

    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    for method, label in zip(methods, labels):
        method_data = summary[summary["method"] == method].sort_values("threads")
        mean = method_data["mean"]
        error = method_data["std"].fillna(0)

        if speedup:
            value = baseline_mean / mean
            error = value * ((baseline_std / baseline_mean) ** 2 + (error / mean) ** 2) ** 0.5
        else:
            value = mean

        ax.errorbar(
            method_data["threads"],
            value,
            yerr=error,
            label=label,
            color=COLORS[method],
            marker="o",
            markersize=5,
            capsize=3,
            linewidth=2,
        )

    thread_counts = sorted(data["threads"].unique())
    if speedup:
        ax.plot(thread_counts, thread_counts, color="#66736B", linestyle="--", linewidth=1.5, label="Ideal scaling")
        ax.axhline(1, color="#A0A8A2", linestyle=":", linewidth=1.2, label="Sequential baseline")

    ax.set_title(title)
    ax.set_ylabel("Speedup over one-thread sequential (x)" if speedup else "Mean runtime per iteration (ms)")
    ax.set_xlabel("OpenMP thread count")
    ax.set_xticks(thread_counts)
    ax.set_ylim(bottom=0)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#D9DFDA", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncol=2)

    fig.tight_layout()
    for extension in ("svg", "png"):
        fig.savefig(os.path.join(FIGURE_DIR, f"{output}.{extension}"), bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(FIGURE_DIR, exist_ok=True)

    datasets = [
        (
            "part2",
            os.path.join(DATA_DIR, "thread_scaling", "vector.csv"),
            ["method", "threads", "N", "M", "nrepeat", "problem_size", "time", "bandwidth"],
            ["sequential", "parallel", "simd_reduction"],
            ["Sequential", "Parallel", "SIMD reduction"],
            "Matrix-vector",
        ),
        (
            "part3",
            os.path.join(DATA_DIR, "thread_scaling", "fib.csv"),
            ["method", "threads", "N", "FS", "nrepeat", "checksum", "time"],
            ["sequential", "parallel", "parallel_static", "parallel_dynamic"],
            ["Sequential", "Default", "Static", "Dynamic"],
            "Fibonacci",
        ),
    ]

    for part, csv_path, columns, methods, labels, name in datasets:
        part_label = part.replace("part", "Part ")
        for speedup in (False, True):
            selected = methods[1:] if speedup else methods
            selected_labels = labels[1:] if speedup else labels
            kind = "speedup" if speedup else "runtime"
            title = f"{part_label}: {name} {kind} scaling"
            plot(csv_path, columns, selected, selected_labels, title, f"{part}_{kind}", speedup)

    print("Generated figures for 2 and 3")


if __name__ == "__main__":
    main()
