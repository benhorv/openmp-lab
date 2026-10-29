#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 13,
    'figure.dpi': 300,
    'svg.fonttype': 'none'
})

os.makedirs('figures', exist_ok=True)

df = pd.read_csv('parameters.csv', header=None, names=['method', 'steps', 'pi', 'time', 'threads'])
df['method'] = df['method'].str.strip('\"')
df = df[df['method'] != 'split_sequential']

colors = {
    'sequential': '#4A5568',
    'reduction': '#2B6CB0',
    'atomic': '#DD6B20',
    'critical': '#E53E3E',
    'split_reduction': '#319795',
    'split_atomic': '#38A169',
    'split_critical': '#D69E2E',
}

markers = {
    'sequential': 'o',
    'reduction': 's',
    'atomic': 'P',
    'critical': 'X',
    'split_reduction': '^',
    'split_atomic': 'D',
    'split_critical': 'v',
}

stats = df[df['steps'] == 100000000].groupby(['method', 'threads'])['time'].mean().reset_index()
threads = [1, 2, 4, 8, 16]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2), sharey=True)

unsplit_order = ['critical', 'atomic', 'sequential']
for method in unsplit_order:
    sub = stats[stats['method'] == method].sort_values('threads')
    ax1.plot(
        sub['threads'], sub['time'],
        label=method, color=colors[method],
        marker=markers[method], markersize=6, linewidth=1.8,
        linestyle='--' if method == 'sequential' else '-'
    )

ax1.set_xscale('log', base=2)
ax1.set_yscale('log')
ax1.set_xticks(threads)
ax1.get_xaxis().set_major_formatter(plt.ScalarFormatter())
ax1.set_xlabel('Thread Count')
ax1.set_ylabel('Execution Time (seconds) [Log Scale]')
ax1.set_title('(a) Per-Iteration Synchronization (Unsplit)')
ax1.grid(True, which='both', linestyle='--', alpha=0.5)
ax1.legend(loc='lower left', frameon=True, framealpha=0.95, edgecolor='#CBD5E0')

split_order = ['sequential', 'reduction', 'split_critical', 'split_atomic', 'split_reduction']
for method in split_order:
    sub = stats[stats['method'] == method].sort_values('threads')
    ax2.plot(
        sub['threads'], sub['time'],
        label=method, color=colors[method],
        marker=markers[method], markersize=6, linewidth=1.8,
        linestyle='--' if method == 'sequential' else '-'
    )

ax2.set_xscale('log', base=2)
ax2.set_xticks(threads)
ax2.get_xaxis().set_major_formatter(plt.ScalarFormatter())
ax2.set_xlabel('Thread Count')
ax2.set_title('(b) Private Accumulation (Split & Reduction)')
ax2.grid(True, which='both', linestyle='--', alpha=0.5)
ax2.legend(loc='upper right', frameon=True, framealpha=0.95, edgecolor='#CBD5E0')

fig.suptitle('Strong Scaling: Execution Time vs. Threads ($N = 10^8$ steps)', fontsize=13, y=0.98)
fig.tight_layout()

fig.savefig('figures/runtime_vs_threads.svg', format='svg', bbox_inches='tight')
fig.savefig('figures/runtime_vs_threads.png', format='png', dpi=300, bbox_inches='tight')
plt.close(fig)

print("Figure 1 generated successfully: figures/runtime_vs_threads.svg")

baseline = stats[(stats['method'] == 'sequential') & (stats['threads'] == 1)]
if baseline.empty or baseline.iloc[0]['time'] <= 0:
    raise ValueError('Missing one-thread sequential baseline for speedup calculation')

baseline_time = baseline.iloc[0]['time']
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))

speedup_groups = [
    (ax1, ['critical', 'atomic'], '(a) Per-Iteration Synchronization'),
    (ax2, ['reduction', 'split_critical', 'split_atomic', 'split_reduction'], '(b) Private Accumulation'),
]

for ax, methods, title in speedup_groups:
    for method in methods:
        sub = stats[stats['method'] == method].sort_values('threads').copy()
        sub['speedup'] = baseline_time / sub['time']
        ax.plot(
            sub['threads'], sub['speedup'],
            label=method, color=colors[method],
            marker=markers[method], markersize=6, linewidth=1.8
        )

    ax.plot(threads, threads, color='#4A5568', linestyle=':', linewidth=1.5, label='Ideal scaling')
    ax.axhline(1, color='#718096', linestyle='--', linewidth=1.2, label='Sequential baseline')
    ax.set_xscale('log', base=2)
    ax.set_xticks(threads)
    ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
    ax.set_xlabel('Thread Count')
    ax.set_title(title)
    ax.grid(True, which='both', linestyle='--', alpha=0.5)
    ax.legend(frameon=True, framealpha=0.95, edgecolor='#CBD5E0')

ax1.set_yscale('log')
ax1.set_ylim(0.001, 20)
ax1.set_ylabel('Speedup factor (log scale)')
ax2.set_ylim(bottom=0)
ax2.set_ylabel('Speedup over one-thread sequential')
fig.suptitle('Strong Scaling: Speedup vs. Threads ($N = 10^8$ steps)', fontsize=13, y=0.98)
fig.tight_layout()

fig.savefig('figures/speedup_vs_threads.svg', format='svg', bbox_inches='tight')
fig.savefig('figures/speedup_vs_threads.png', format='png', dpi=300, bbox_inches='tight')
plt.close(fig)

print("Figure 2 generated successfully: figures/speedup_vs_threads.svg")
