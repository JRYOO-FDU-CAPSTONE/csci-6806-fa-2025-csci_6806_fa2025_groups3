import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({
    "font.size": 11, "axes.titlesize": 11, "axes.labelsize": 11,
    "xtick.labelsize": 11, "ytick.labelsize": 11, "legend.fontsize": 11
})
ORANGE = "#FB8C00"

def annotate_points(ax, x, y, fmt, color):
    y_min, y_max = ax.get_ylim()
    for i, (xi, yi) in enumerate(zip(x, y)):
        dy = 0.02*(y_max - y_min)
        ax.annotate(fmt.format(yi), (xi, yi),
                    ha='center',
                    va=('bottom' if i % 2 == 0 else 'top'),
                    color=color, xytext=(0, (dy if i % 2 == 0 else -dy)),
                    textcoords='offset points')

def fetch_figure_1_data(csv_path="fig1.csv"):
    df = pd.read_csv(csv_path)
    tau_vals = df['tau_vals'].values
    peak_dt = df['peak_dt'].values
    tau_default = 0.5
    return tau_vals, peak_dt, tau_default

tau_vals, peak_dt, tau_default = fetch_figure_1_data("/Users/royzsec/csci-6806-fa-2025-csci_6806_fa2025_groups3/Ablation/fig1.csv")

fig1, ax1 = plt.subplots(figsize=(8, 5))
ax1.plot(tau_vals, peak_dt, marker='o', color=ORANGE, linewidth=2, label="E1 — DT-SLRU")
ax1.axvline(tau_default, color=ORANGE, linestyle='--', linewidth=1.5, label="Baseline (τDT = 0.5)")
ax1.set_xlabel(r"$\tau_{DT}$ (dimensionless)")
ax1.set_ylabel("Peak Disk-head Time (seconds)")
ax1.set_title("Figure 1: Peak DT vs $\\tau_{DT}$ (DT-SLRU)")
annotate_points(ax1, tau_vals, peak_dt, "{:.3f} s", ORANGE)
ax1.grid(True, alpha=0.3); ax1.legend(loc="upper right")
fig1.tight_layout()
fig1.savefig("FIG1_dt_slru_orange.png", dpi=200)

