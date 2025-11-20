import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({
    "font.size": 11, "axes.titlesize": 11, "axes.labelsize": 11,
    "xtick.labelsize": 11, "ytick.labelsize": 11, "legend.fontsize": 11
})
GREEN = "#43A047"

def annotate_points(ax, x, y, fmt, color):
    y_min, y_max = ax.get_ylim()
    for i, (xi, yi) in enumerate(zip(x, y)):
        dy = 0.02*(y_max - y_min)
        ax.annotate(fmt.format(yi), (xi, yi),
                    ha='center',
                    va=('bottom' if i % 2 == 0 else 'top'),
                    color=color, xytext=(0, (dy if i % 2 == 0 else -dy)),
                    textcoords='offset points')

def fetch_figure_3_data(csv_path="fig3.csv"):
    df = pd.read_csv(csv_path)
    cap_vals = df['cap_vals'].values
    peak_dt_cap = df['peak_dt_cap'].values
    cap_default = 0.30
    opt_lo_cap, opt_hi_cap = 0.45, 0.55
    return cap_vals, peak_dt_cap, cap_default, opt_lo_cap, opt_hi_cap

cap_vals, peak_dt_cap, cap_default, opt_lo_cap, opt_hi_cap = fetch_figure_3_data("/csci-6806-fa-2025-csci_6806_fa2025_groups3/Ablation/fig3.csv")

fig3, ax3 = plt.subplots(figsize=(8, 5))
ax3.fill_betweenx([min(peak_dt_cap)-0.1, max(peak_dt_cap)+0.1], opt_lo_cap, opt_hi_cap,
                  color=GREEN, alpha=0.12, label="Optimal region")
ax3.plot(cap_vals, peak_dt_cap, marker='o', color=GREEN, linewidth=2, label="E2 — EDE")
ax3.axvline(cap_default, color=GREEN, linestyle='--', linewidth=1.5, label="Baseline (cap = 0.3)")
ax3.set_xlabel("PROTECTED cap (fraction of cache)")
ax3.set_ylabel("Peak Disk-head Time (seconds)")
ax3.set_title("Figure 3: Peak DT vs PROTECTED cap (EDE)")
annotate_points(ax3, cap_vals, peak_dt_cap, "{:.3f} s", GREEN)
ax3.grid(True, alpha=0.3); ax3.legend(loc="upper right")
fig3.tight_layout()
fig3.savefig("FIG3_protected_cap_green.png", dpi=200)
