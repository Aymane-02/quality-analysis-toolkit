"""
Generate a realistic synthetic measurement dataset for SPC analysis.
Scenario: a machined part with a critical dimension, target = 10.00 mm,
specification limits 9.95-10.05 mm. Measured in subgroups of 5 over 40
time periods. A small process shift is introduced partway to make the
control charts meaningful (and realistic for a QA scenario).
"""
import numpy as np
import pandas as pd

np.random.seed(42)

TARGET = 10.00      # mm, nominal dimension
USL = 10.05         # upper spec limit
LSL = 9.95          # lower spec limit
PROCESS_SD = 0.012  # natural process variation
N_SUBGROUPS = 40
SUBGROUP_SIZE = 5

rows = []
for sg in range(1, N_SUBGROUPS + 1):
    # Introduce a small upward shift from subgroup 26 onward (tool wear)
    mean_shift = 0.018 if sg >= 26 else 0.0
    for unit in range(1, SUBGROUP_SIZE + 1):
        value = np.random.normal(TARGET + mean_shift, PROCESS_SD)
        rows.append({
            "subgroup": sg,
            "unit": unit,
            "measurement_mm": round(value, 4),
        })

df = pd.DataFrame(rows)
df.to_csv("data/measurements.csv", index=False)
print(f"Generated {len(df)} measurements across {N_SUBGROUPS} subgroups.")
print(df.head())
print("\nOverall mean:", round(df.measurement_mm.mean(), 4),
      "| overall std:", round(df.measurement_mm.std(), 4))
