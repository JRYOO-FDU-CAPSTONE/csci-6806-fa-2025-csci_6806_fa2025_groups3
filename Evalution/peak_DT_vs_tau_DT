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

def fetch_fig5_data(csv_path="a4_fig5_peak_dt_vs_tau_dt.csv"):
    df = pd.read_csv(csv_path)
    tau_dt = df['tau_dt'].values
    peak_vs_tau = df['peak_vs_tau'].values
    baseline_tau = 0.5
    return tau_dt, peak_vs_tau, baseline_tau

set_baleen_style()
tau_dt, peak_vs_tau, baseline_tau = fetch_fig5_data()
COLORS = {"E1": "#6A1B9A"}

plt.figure(figsize=(7.2, 4.6))
ax = plt.gca()
ax.plot(tau_dt, peak_vs_tau, marker="o", color=COLORS["E1"], label="E1—DT-SLRU")
label_points(ax, tau_dt, peak_vs_tau, COLORS["E1"], up_down_pattern=(+10, -12))
ax.axvline(baseline_tau, color="red", linestyle="--", linewidth=1.2, label="Baseline (tau_DT)")
ax.set_title("Figure 5: Peak DT vs tau_DT (E1 DT-SLRU)")
ax.set_xlabel("tau_DT (× default)")
ax.set_ylabel("Peak Disk-head Time (seconds)")
ax.legend(frameon=True, edgecolor="black", loc="best")
beautify(ax)
savefig(os.path.join("figures”, "figure_5.png"))
