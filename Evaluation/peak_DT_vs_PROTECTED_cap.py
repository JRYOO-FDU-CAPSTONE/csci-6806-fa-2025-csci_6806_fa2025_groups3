import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def set_baleen_style():
    plt.rcParams.update({
        "font.size": 11,
        "axes.titlesize": 11,
        "axes.labelsize": 11,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "axes.spines.top": True,
        "axes.spines.right": True,
        "axes.linewidth": 1.1,
        "lines.linewidth": 2.2,
        "lines.markersize": 6.5,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.grid": True,
        "grid.alpha": 0.22,
        "grid.linestyle": "--",
    })

def beautify(ax):
    for sp in ax.spines.values():
        sp.set_linewidth(1.1)
        sp.set_color("black")
    ax.grid(True, alpha=0.22, linestyle="--", linewidth=0.8)

def savefig(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    print("Saved:", path)

def label_points(ax, xs, ys, color, up_down_pattern=(+10, -12), fmt="{:.3f}\u00A0s"):
    for i, (x, y) in enumerate(zip(xs, ys)):
        dy = up_down_pattern[i % len(up_down_pattern)]
        va = "bottom" if dy > 0 else "top"
        ax.annotate(fmt.format(y),
                    (x, y),
                    xytext=(0, dy),
                    textcoords="offset points",
                    ha="center", va=va,
                    color=color,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.65))

def fetch_fig6_data(csv_path="a4_fig6_peak_dt_vs_cap.csv"):
    df = pd.read_csv(csv_path)
    cap_vals = df['cap_vals'].values
    peak_vs_cap = df['peak_vs_cap'].values
    baseline_cap = 0.3
    opt_cap_rng = (0.42, 0.50)
    return cap_vals, peak_vs_cap, baseline_cap, opt_cap_rng

set_baleen_style()
cap_vals, peak_vs_cap, baseline_cap, opt_cap_rng = fetch_fig6_data()
COLORS = {"E2": "#1565C0"}

plt.figure(figsize=(7.2, 4.6))
ax = plt.gca()
ax.plot(cap_vals, peak_vs_cap, marker="o", color=COLORS["E2"], label="E2—EDE")
label_points(ax, cap_vals, peak_vs_cap, COLORS["E2"], up_down_pattern=(+10, -12))
ax.axvline(baseline_cap, color="red", linestyle="--", linewidth=1.2, label="Baseline (cap = 0.3)")
ax.axvspan(opt_cap_rng[0], opt_cap_rng[1], color="green", alpha=0.12, label="Optimal region")
ax.set_title("Figure 6: Peak DT vs PROTECTED cap (E2 EDE)")
ax.set_xlabel("PROTECTED cap (fraction of cache)")
ax.set_ylabel("Peak Disk-head Time (seconds)")
ax.legend(frameon=True, edgecolor="black", loc="best")
beautify(ax)
savefig(os.path.join("figures”, "figure_6.png"))
