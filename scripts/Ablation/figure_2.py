import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({
    "font.size": 11, "axes.titlesize": 11, "axes.labelsize": 11,
    "xtick.labelsize": 11, "ytick.labelsize": 11, "legend.fontsize": 11
})
ORANGE = "#FB8C00"

def fetch_figure_2_data(csv_path="fig2.csv"):
    df = pd.read_csv(csv_path)
    tau_vals = df['tau_vals'].values
    hit_rate = df['hit_rate'].values
    tau_default = 0.5
    return tau_vals, hit_rate, tau_default

tau_vals, hit_rate, tau_default = fetch_figure_2_data("/csci-6806-fa-2025-csci_6806_fa2025_groups3/Ablation/fig2.csv")

fig2, ax2 = plt.subplots(figsize=(8, 5))
ax2.plot(tau_vals, hit_rate, marker='s', color=ORANGE, linewidth=2, label="E1 — DT-SLRU")
ax2.axvline(tau_default, color=ORANGE, linestyle='--', linewidth=1.5, label="Baseline (τDT = 0.5)")
ax2.set_xlabel(r"$\tau_{DT}$ (dimensionless)")
ax2.set_ylabel("Hit Rate (%)")
ax2.set_title("Figure 2: Hit Rate vs $\\tau_{DT}$ (DT-SLRU)")
ymin, ymax = ax2.get_ylim()
for i, (x, y) in enumerate(zip(tau_vals, hit_rate)):
    dy = 0.02*(ymax - ymin)
    ax2.annotate(f"{y:.1f} %", (x, y), ha='center',
                 va=('bottom' if i % 2 == 0 else 'top'),
                 color=ORANGE, xytext=(0, (dy if i % 2 == 0 else -dy)),
                 textcoords='offset points')
ax2.grid(True, alpha=0.3); ax2.legend(loc="upper right")
fig2.tight_layout()
fig2.savefig("FIG2_dt_slru_orange.png", dpi=200)
