"""
Statistical Process Control (SPC) analysis:
  - X-bar and R control charts (is the process stable / in control?)
  - Process capability Cp / Cpk (is the process meeting spec?)
  - Out-of-control detection (which subgroups need investigation?)
"""
import numpy as np
import pandas as pd

# Specification limits (from the part drawing)
USL, LSL, TARGET = 10.05, 9.95, 10.00

# SPC constants for subgroup size n=5 (standard Shewhart table)
A2, D3, D4, d2 = 0.577, 0.0, 2.114, 2.326

df = pd.read_csv("data/measurements.csv")
n = df.groupby("subgroup").size().iloc[0]

# Subgroup statistics
g = df.groupby("subgroup")["measurement_mm"]
stats = pd.DataFrame({"xbar": g.mean(), "R": g.max() - g.min()}).reset_index()

# Center lines
xbarbar = stats["xbar"].mean()   # grand mean
Rbar = stats["R"].mean()         # mean range

# Control limits
xbar_UCL = xbarbar + A2 * Rbar
xbar_LCL = xbarbar - A2 * Rbar
R_UCL = D4 * Rbar
R_LCL = D3 * Rbar

print("=== X-bar / R Control Chart ===")
print(f"Grand mean (CL): {xbarbar:.4f} mm")
print(f"X-bar UCL / LCL: {xbar_UCL:.4f} / {xbar_LCL:.4f}")
print(f"R-bar (CL): {Rbar:.4f} | R UCL / LCL: {R_UCL:.4f} / {R_LCL:.4f}")

# Out-of-control points (beyond X-bar limits)
ooc = stats[(stats.xbar > xbar_UCL) | (stats.xbar < xbar_LCL)]
print(f"\nOut-of-control subgroups (X-bar): {list(ooc.subgroup) if len(ooc) else 'none'}")

# Western Electric rule: 8+ consecutive points on one side of centerline
side = np.sign(stats.xbar.values - xbarbar)
runs = []
start = 0
for i in range(1, len(side) + 1):
    if i == len(side) or side[i] != side[start]:
        if i - start >= 8:
            runs.append((int(stats.subgroup.iloc[start]),
                         int(stats.subgroup.iloc[i - 1]), i - start))
        start = i
if runs:
    for a, b, ln in runs:
        print(f"Run of {ln} points on one side: subgroups {a}-{b} "
              f"(possible process shift)")
else:
    print("Runs of >=8 on one side: none")

# Process capability (uses within-subgroup sigma estimated from Rbar)
sigma = Rbar / d2
Cp  = (USL - LSL) / (6 * sigma)
Cpu = (USL - xbarbar) / (3 * sigma)
Cpl = (xbarbar - LSL) / (3 * sigma)
Cpk = min(Cpu, Cpl)

print("\n=== Process Capability ===")
print(f"Estimated process sigma: {sigma:.4f} mm")
print(f"Cp : {Cp:.2f}   (spread vs tolerance)")
print(f"Cpk: {Cpk:.2f}   (spread AND centering)")
target = 1.33
print(f"Industry target Cpk >= {target}: "
      f"{'PASS' if Cpk >= target else 'FAIL - process needs attention'}")

# Defect rate: parts outside spec
out = df[(df.measurement_mm > USL) | (df.measurement_mm < LSL)]
print(f"\nMeasured parts out of spec: {len(out)}/{len(df)} "
      f"({100*len(out)/len(df):.1f}%)")

# Save for plotting
stats.to_csv("data/_subgroup_stats.csv", index=False)
pd.DataFrame({
    "xbarbar":[xbarbar], "xbar_UCL":[xbar_UCL], "xbar_LCL":[xbar_LCL],
    "Rbar":[Rbar], "R_UCL":[R_UCL], "R_LCL":[R_LCL],
    "sigma":[sigma], "Cp":[Cp], "Cpk":[Cpk]
}).to_csv("data/_limits.csv", index=False)
