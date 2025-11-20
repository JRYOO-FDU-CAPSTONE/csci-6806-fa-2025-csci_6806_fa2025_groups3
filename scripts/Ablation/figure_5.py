import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({
    "font.size": 11, "axes.titlesize": 11, "axes.labelsize": 11,
    "xtick.labelsize": 11, "ytick.labelsize": 11, "legend.fontsize": 11
})
ORANGE = "#FB8C00"
GREEN = "#43A047"
RED = "#E53935"

def annotate_norm(ax, x, y, color):
    y_min, y_max = ax.get_ylim()
    for i, (xi, yi) in enumerate(zip(x, y)):
        dy = 0.02*(y_max - y_min)
        ax.annotate(f"{yi:.3f}", (xi, yi), ha='center',
                    va=('bottom' if i % 2 == 0 else 'top'),
                    color=color, xytext=(0, (dy if i % 2 == 0 else -dy)),
                    textcoords='offset points')

def fetch_figure_5_data(csv_path="fig5.csv"):
    df = pd.read_csv(csv_path)
    tau_norm_x = df['tau_norm_x'].values
    tau_norm = df['tau_norm'].values
    cap_norm_x = df['cap_norm_x'].values
    cap_norm = df['cap_norm'].values
    atti_norm_x = df['atti_norm_x'].values
    atti_norm = df['atti_norm'].values
    return tau_norm_x, tau_norm, cap_norm_x, cap_norm, atti_norm_x, atti_norm

tau_norm_x, tau_norm, cap_norm_x, cap_norm, atti_norm_x, atti_norm = fetch_figure_5_data("/csci-6806-fa-2025-csci_6806_fa2025_groups3/Ablation/fig5.csv")

fig5, ax5 = plt.subplots(figsize=(8, 5))
ax5.axhline(1.0, color="#777777", linestyle="--", linewidth=1)
ax5.plot(tau_norm_x, tau_norm, marker='o', color=ORANGE, linewidth=2, label="DT-SLRU: $\\tau_{DT}$")
ax5.plot(cap_norm_x, cap_norm, marker='s', color=GREEN, linewidth=2, label="EDE: protected cap")
ax5.plot(atti_norm_x, atti_norm, marker='^', color=RED, linewidth=2, linestyle='--', label="EDE: $\\alpha_{TTI}$")
annotate_norm(ax5, tau_norm_x, tau_norm, ORANGE)
annotate_norm(ax5, cap_norm_x, cap_norm, GREEN)
annotate_norm(ax5, atti_norm_x, atti_norm, RED)
ax5.set_xlabel("Parameter value (dimensionless)")
ax5.set_ylabel("Normalized Peak DT (× baseline)")
ax5.set_title("Figure 5: Normalized Peak DT across E1/E2 parameter sweeps")
ax5.grid(True, alpha=0.3); ax5.legend(loc="upper left")
fig5.tight_layout()
fig5.savefig("FIG5_normalized_orange_green_red.png", dpi=200)
