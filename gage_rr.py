"""
Measurement System Analysis (MSA) — Gage R&R study.

Question answered: how much of the variation I observe comes from the
MEASUREMENT SYSTEM (gauge + operators) rather than from real part
differences? If the measurement system is too noisy, no downstream
process analysis (SPC, capability) can be trusted.

Design: 3 operators x 10 parts x 3 trials each (standard Gage R&R layout).
Data is synthetically generated with known variance components so the
method can be demonstrated and verified.
"""
import numpy as np
import pandas as pd

np.random.seed(7)

N_PARTS, N_OPERATORS, N_TRIALS = 10, 3, 3

# True (hidden) part values spread across a realistic range
part_true = np.random.normal(10.00, 0.05, N_PARTS)          # real part-to-part variation
operator_bias = np.array([0.000, 0.008, -0.005])            # reproducibility: operator offsets
repeat_sd = 0.006                                            # repeatability: gauge noise

rows = []
for p in range(N_PARTS):
    for o in range(N_OPERATORS):
        for t in range(N_TRIALS):
            value = part_true[p] + operator_bias[o] + np.random.normal(0, repeat_sd)
            rows.append({"part": p+1, "operator": o+1, "trial": t+1,
                         "measurement_mm": round(value, 4)})
df = pd.DataFrame(rows)
df.to_csv("data/gage_data.csv", index=False)

# --- Gage R&R via ANOVA-style variance components (range method equivalent) ---
# Repeatability (EV): from within operator-part cell ranges
cell = df.groupby(["part","operator"])["measurement_mm"]
Rbar = (cell.max() - cell.min()).mean()
d2_trials = 1.693   # d2 for n=3 trials
EV = Rbar / d2_trials                      # equipment variation (repeatability)

# Reproducibility (AV): from operator averages
op_means = df.groupby("operator")["measurement_mm"].mean()
Xdiff = op_means.max() - op_means.min()
d2_ops = 1.693
AV = np.sqrt(max((Xdiff/d2_ops)**2 - (EV**2)/(N_PARTS*N_TRIALS), 0))  # operator variation

# Part variation (PV)
part_means = df.groupby("part")["measurement_mm"].mean()
Rp = part_means.max() - part_means.min()
d2_parts = 3.078
PV = Rp / d2_parts

GRR = np.sqrt(EV**2 + AV**2)               # total gage R&R
TV  = np.sqrt(GRR**2 + PV**2)              # total variation

print("=== Gage R&R (Measurement System Analysis) ===")
print(f"Repeatability (EV, gauge noise)      : {EV:.4f} mm")
print(f"Reproducibility (AV, operator diff)  : {AV:.4f} mm")
print(f"Gage R&R (GRR = sqrt(EV^2+AV^2))     : {GRR:.4f} mm")
print(f"Part-to-part variation (PV)          : {PV:.4f} mm")
print(f"Total variation (TV)                 : {TV:.4f} mm")
print(f"\n%GRR (share of total variation)      : {100*GRR/TV:.1f}%")
pct = 100*GRR/TV
verdict = ("ACCEPTABLE (<10%)" if pct < 10 else
           "MARGINAL (10-30%) - use with caution" if pct < 30 else
           "UNACCEPTABLE (>30%) - fix the measurement system")
print(f"Verdict: {verdict}")
print(f"%Part variation                      : {100*PV/TV:.1f}%  (higher is better)")

pd.DataFrame({"EV":[EV],"AV":[AV],"GRR":[GRR],"PV":[PV],"TV":[TV],
             "pct_GRR":[pct]}).to_csv("data/_grr_results.csv", index=False)
