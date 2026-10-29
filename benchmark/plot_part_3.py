#!/usr/bin/env python3
import os
import pandas as pd
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
RESULTS_DIR = os.path.join(ROOT_DIR, 'results')
FIGURES_DIR = os.path.join(ROOT_DIR, 'figures')

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

COLORS = {
    'sequential': '#4A5568',
    'parallel': '#D1783C',
    'parallel_static': '#3978A0',
    'parallel_dynamic': '#A84F4F',
}
LABELS = {
    'sequential': 'Sequential',
    'parallel': 'Default',
    'parallel_static': 'Static',
    'parallel_dynamic': 'Dynamic',
}

df = pd.read_csv(
    os.path.join(RESULTS_DIR, 'fib.csv'),
    header=None,
    usecols=[0, 1, 4, 6],
    names=['method', 'threads', 'rep', 'time'],
)
df['method'] = df['method'].str.strip('"')
df['ms'] = (df['time'] / df['rep']) * 1000
stats = df.groupby(['method', 'threads'])['ms'].mean().reset_index()

base_ms = stats[(stats['method'] == 'sequential') & (stats['threads'] == 1)]['ms'].iloc[0]
stats['speedup'] = base_ms / stats['ms']
threads = sorted(stats['threads'].unique())

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.3))
for method, label in LABELS.items():
    subset = stats[stats['method'] == method].sort_values('threads')
    ax1.plot(subset['threads'], subset['ms'], label=label, color=COLORS[method], marker='o', lw=1.8)
    if method != 'sequential':
        ax2.plot(subset['threads'], subset['speedup'], label=label, color=COLORS[method], marker='o', lw=1.8)

ax2.plot(threads, threads, '--', color='#66736B', lw=1.5, label='Ideal scaling')
ax2.axhline(1, color='#A0A8A2', linestyle=':', lw=1.2, label='Sequential baseline')

for axis, ylabel, subtitle in [
    (ax1, 'Mean Runtime per iteration (ms)', '(a) Execution Time vs Threads'),
    (ax2, 'Speedup over Sequential (x)', '(b) Speedup vs Threads'),
]:
    axis.set(title=subtitle, xlabel='OpenMP Thread Count', ylabel=ylabel, xticks=threads, ylim=(0, None))
    axis.grid(True, linestyle='--', alpha=0.5)
    axis.legend(frameon=True, framealpha=0.9, fontsize=9)

fig.suptitle('Part 3: Fibonacci Workload Scaling ($N=10, FS=17$)', fontsize=12, y=0.98)
fig.tight_layout()

os.makedirs(FIGURES_DIR, exist_ok=True)
for extension in ('svg', 'png'):
    fig.savefig(
        os.path.join(FIGURES_DIR, f'part3_scaling.{extension}'),
        bbox_inches='tight',
        dpi=300 if extension == 'png' else None,
    )
plt.close(fig)
print('Generated Part 3 figures: figures/part3_scaling.svg')