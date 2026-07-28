import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

df = pd.read_csv("data/measurements.csv")
stats = pd.read_csv("data/_subgroup_stats.csv")
L = pd.read_csv("data/_limits.csv").iloc[0]
USL, LSL, TARGET = 10.05, 9.95, 10.00
BLUE, RED, GREY = '#4A7BA7', '#C0392B', '#7F8C8D'
plt.rcParams.update({'figure.dpi':110, 'font.size':10})

# 1. X-bar chart
fig, ax = plt.subplots(figsize=(8,4))
ax.plot(stats.subgroup, stats.xbar, '-o', color=BLUE, markersize=4, linewidth=1)
ax.axhline(L.xbarbar, color='green', linewidth=1.2, label='Center line')
ax.axhline(L.xbar_UCL, color=RED, linestyle='--', linewidth=1.2, label='Control limits')
ax.axhline(L.xbar_LCL, color=RED, linestyle='--', linewidth=1.2)
ooc = stats[(stats.xbar > L.xbar_UCL) | (stats.xbar < L.xbar_LCL)]
ax.scatter(ooc.subgroup, ooc.xbar, color=RED, zorder=5, s=60, label='Out of control')
ax.axvline(25.5, color=GREY, linestyle=':', linewidth=1)
ax.text(26, ax.get_ylim()[1], ' tool-wear shift', color=GREY, va='top', fontsize=8)
ax.set_xlabel('Subgroup'); ax.set_ylabel('Sample mean (mm)')
ax.set_title('X-bar Control Chart — sample means over time'); ax.legend(fontsize=8)
plt.tight_layout(); plt.savefig('xbar_chart.png'); plt.close()

# 2. R chart
fig, ax = plt.subplots(figsize=(8,4))
ax.plot(stats.subgroup, stats.R, '-o', color=BLUE, markersize=4, linewidth=1)
ax.axhline(L.Rbar, color='green', linewidth=1.2, label='Center line')
ax.axhline(L.R_UCL, color=RED, linestyle='--', linewidth=1.2, label='UCL')
ax.set_xlabel('Subgroup'); ax.set_ylabel('Sample range (mm)')
ax.set_title('R Control Chart — within-sample variation'); ax.legend(fontsize=8)
plt.tight_layout(); plt.savefig('r_chart.png'); plt.close()

# 3. Capability histogram
fig, ax = plt.subplots(figsize=(8,4))
ax.hist(df.measurement_mm, bins=25, color=BLUE, alpha=0.7, edgecolor='white')
for x, c, lab in [(USL,RED,'USL'), (LSL,RED,'LSL'), (TARGET,'green','Target')]:
    ax.axvline(x, color=c, linestyle='--', linewidth=1.4, label=lab)
ax.set_xlabel('Measurement (mm)'); ax.set_ylabel('Count')
ax.set_title(f'Process Capability — Cp={L.Cp:.2f}, Cpk={L.Cpk:.2f}'); ax.legend(fontsize=8)
plt.tight_layout(); plt.savefig('capability_histogram.png'); plt.close()
print("Saved: xbar_chart.png, r_chart.png, capability_histogram.png")
