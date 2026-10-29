#!/usr/bin/env python3
import os
import pandas as pd
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
RESULTS_DIR = os.path.join(ROOT_DIR, 'results')
FIGURES_DIR = os.path.join(ROOT_DIR, 'figures')

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

COLORS = {'sequential': '#4A5568', 'parallel': '#D1783C', 'simd_reduction': '#397C8A'}
LABELS = {'sequential': 'Sequential', 'parallel': 'Parallel (Reduction)', 'simd_reduction': 'SIMD Reduction'}

df = pd.read_csv(os.path.join(RESULTS_DIR, 'vector.csv'), header=None, usecols=[0, 1, 4, 6], names=['method', 'threads', 'rep', 'time'])
df['method'] = df['method'].str.strip('"')
df['ms'] = (df['time'] / df['rep']) * 1000
stats = df.groupby(['method', 'threads'])['ms'].mean().reset_index()

base_ms = stats[(stats['method'] == 'sequential') & (stats['threads'] == 1)]['ms'].iloc[0]
stats['speedup'] = base_ms / stats['ms']
threads = sorted(stats['threads'].unique())

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.3))
for m, lbl in LABELS.items():
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

fig.suptitle('Part 2: Matrix-Vector Strong Scaling ($N=512, M=512$)', fontsize=12, y=0.98)
fig.tight_layout()

os.makedirs(FIGURES_DIR, exist_ok=True)
for ext in ('svg', 'png'):
    fig.savefig(os.path.join(FIGURES_DIR, f'part2_scaling.{ext}'), bbox_inches='tight', dpi=300 if ext == 'png' else None)
plt.close(fig)
print("Generated Part 2 figures: figures/part2_scaling.svg")
