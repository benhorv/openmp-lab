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

df = pd.read_csv('vector.csv', header=None,
                 names=['version', 'threads', 'N', 'M', 'nrepeat', 'problem_size', 'time', 'bandwidth'])

agg = df.groupby(['N', 'M'])[['problem_size', 'time', 'bandwidth']].agg(['mean', 'std']).reset_index()
agg.columns = ['_'.join(c).strip('_') for c in agg.columns]

# Create Figure with 2 subplots: Heatmap (left) and Clean Line Plot (right)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

# -------------------------------------------------------------
# Panel (a): 2D Heatmap of Memory Bandwidth
# -------------------------------------------------------------
# Build grid
n_sorted = sorted(agg['N'].unique())
m_sorted = sorted(agg['M'].unique())

pivot_bw = agg.pivot(index='N', columns='M', values='bandwidth_mean').reindex(index=n_sorted[::-1], columns=m_sorted)

# Plot heatmap using imshow
data_matrix = pivot_bw.values
im = ax1.imshow(data_matrix, cmap='YlGnBu', aspect='auto', vmin=0, vmax=19)

# Format ticks with 2^exponent labels
y_labels = [f'$2^{{{int(np.log2(n))}}}$\n({n})' for n in n_sorted[::-1]]
x_labels = [f'$2^{{{int(np.log2(m))}}}$\n({m})' for m in m_sorted]

ax1.set_xticks(range(len(m_sorted)))
ax1.set_xticklabels(x_labels)
ax1.set_yticks(range(len(n_sorted)))
ax1.set_yticklabels(y_labels)

ax1.set_xlabel('Columns $M$ ($2^M$)')
ax1.set_ylabel('Rows $N$ ($2^N$)')
ax1.set_title('(a) Memory Bandwidth (GB/s) Heatmap')
ax1.grid(False)

# Add text annotations in each cell
for i in range(len(n_sorted)):
    for j in range(len(m_sorted)):
        val = data_matrix[i, j]
        if np.isnan(val):
            ax1.text(j, i, 'N/A\n(>RAM)', ha='center', va='center', color='red', fontsize=8, weight='bold')
        else:
            text_color = 'white' if val > 12 else 'black'
            ax1.text(j, i, f'{val:.1f}', ha='center', va='center', color=text_color, fontsize=9.5, weight='bold')

cbar = fig.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
cbar.set_label('Bandwidth (GB/s)', rotation=270, labelpad=15)

# -------------------------------------------------------------
# Panel (b): Representative Scaling Curves (Clean, uncluttered)
# -------------------------------------------------------------
# Select 4 representative N values to avoid clutter: Small, Medium, Large, Huge
selected_n = [16, 256, 4096, 65536]
colors = ['#4A5568', '#319795', '#2B6CB0', '#D69E2E']
markers = ['o', 's', '^', 'D']

for n, col, mkr in zip(selected_n, colors, markers):
    sub = agg[agg['N'] == n].sort_values('M')
    n_exp = int(np.log2(n))
    ax2.errorbar(
        sub['M'], sub['bandwidth_mean'], yerr=sub['bandwidth_std'],
        label=f'$N = 2^{{{n_exp}}}$ ({n} rows)', color=col,
        marker=mkr, markersize=6, capsize=3, linewidth=1.8
    )

# Reference lines
ax2.axhline(10.7, color='#E53E3E', linestyle='--', linewidth=1.5, label='DRAM Saturation (~10.7 GB/s)')
ax2.axvline(8, color='#805AD5', linestyle=':', linewidth=1.5, label='L1 Cache Pinning ($M = 8$)')

ax2.set_xscale('log', base=2)
ax2.set_xticks(m_sorted)
ax2.get_xaxis().set_major_formatter(plt.ScalarFormatter())
ax2.set_xlabel('Columns $M$ ($2^M$)')
ax2.set_ylabel('Effective Memory Bandwidth (GB/s)')
ax2.set_title('(b) Bandwidth vs. Columns (Selected Rows $N$)')
ax2.set_ylim(0, 25)
ax2.grid(True, which='both', linestyle='--', alpha=0.5)
ax2.legend(loc='upper right', frameon=True, framealpha=0.95, edgecolor='#CBD5E0')

fig.suptitle('Sequential Matrix-Vector Performance ($y^T \\cdot A \\cdot x$)', fontsize=13, y=0.98)
fig.tight_layout()

# Save SVG and PNG
fig.savefig('figures/vector_sequential.svg', format='svg', bbox_inches='tight')
fig.savefig('figures/vector_sequential.png', format='png', dpi=300, bbox_inches='tight')
plt.close(fig)

print("Regenerated figures/vector_sequential.svg cleanly!")
