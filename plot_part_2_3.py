#!/usr/bin/env python3
import os
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

COLORS = {
    'sequential': '#4A5568',
    'parallel': '#D1783C',
    'simd_reduction': '#397C8A',
    'parallel_static': '#3978A0',
    'parallel_dynamic': '#A84F4F',
}


def plot_scaling_pair(csv_path, title, out_name, labels):
    df = pd.read_csv(csv_path, header=None, usecols=[0, 1, 4, 6], names=['method', 'threads', 'rep', 'time'])
    df['method'] = df['method'].str.strip('"')
    df['ms'] = (df['time'] / df['rep']) * 1000
    stats = df.groupby(['method', 'threads'])['ms'].mean().reset_index()

    base_ms = stats[(stats['method'] == 'sequential') & (stats['threads'] == 1)]['ms'].iloc[0]
    stats['speedup'] = base_ms / stats['ms']
    threads = sorted(stats['threads'].unique())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.3))
    for m, lbl in labels.items():
        sub = stats[stats['method'] == m].sort_values('threads')
        ax1.plot(sub['threads'], sub['ms'], label=lbl, color=COLORS[m], marker='o', lw=1.8)
        if m != 'sequential':
            ax2.plot(sub['threads'], sub['speedup'], label=lbl, color=COLORS[m], marker='o', lw=1.8)

    ax2.plot(threads, threads, '--', color='#66736B', lw=1.5, label='Ideal scaling')
    ax2.axhline(1, color='#A0A8A2', linestyle=':', lw=1.2, label='Sequential baseline')

    for ax, yl, subtitle in [
        (ax1, 'Mean Runtime per iteration (ms)', '(a) Execution Time vs Threads'),
        (ax2, 'Speedup over Sequential (x)', '(b) Speedup vs Threads'),
    ]:
        ax.set(title=subtitle, xlabel='OpenMP Thread Count', ylabel=yl, xticks=threads, ylim=(0, None))
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(frameon=True, framealpha=0.9, fontsize=9)

    fig.suptitle(title, fontsize=12, y=0.98)
    fig.tight_layout()

    os.makedirs('figures', exist_ok=True)
    for ext in ('svg', 'png'):
        fig.savefig(f'figures/{out_name}.{ext}', bbox_inches='tight', dpi=300 if ext == 'png' else None)
    plt.close(fig)


if __name__ == '__main__':
    plot_scaling_pair(
        'benchmark_data/thread_scaling/vector.csv',
        'Part 2: Matrix-Vector Strong Scaling ($N=512, M=512$)',
        'part2_scaling',
        {'sequential': 'Sequential', 'parallel': 'Parallel (Reduction)', 'simd_reduction': 'SIMD Reduction'},
    )
    plot_scaling_pair(
        'benchmark_data/thread_scaling/fib.csv',
        'Part 3: Fibonacci Workload Scaling ($N=10, FS=17$)',
        'part3_scaling',
        {'sequential': 'Sequential', 'parallel': 'Default', 'parallel_static': 'Static', 'parallel_dynamic': 'Dynamic'},
    )
    print("Generated clean scaling figures for Part 2 and Part 3 (no error bars).")
