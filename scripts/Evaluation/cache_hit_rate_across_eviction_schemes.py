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

def fetch_fig3_data(csv_path="a4_fig3_hit_rate.csv"):
    df = pd.read_csv(csv_path)
    hit_rate_pct = dict(zip(df['scheme'], df['hit_rate_pct']))
    return hit_rate_pct

set_baleen_style()
schemes = ["E0-LRU", "E1-DT-SLRU", "E2-EDE"]
hit_rate_pct = fetch_fig3_data()
COLORS = {"E0": "#C2185B", "E1": "#6A1B9A", "E2": "#1565C0"}
bar_colors = [COLORS["E0"], COLORS["E1"], COLORS["E2"]]

plt.figure(figsize=(7.2, 4.6))
ax = plt.gca()
xs = np.arange(len(schemes))
ys = [hit_rate_pct[s] for s in schemes]
ax.bar(xs, ys, color=bar_colors, edgecolor="black", linewidth=0.8)
ax.set_title("Figure 3: Cache Hit Rate (%) across eviction schemes (E0–E2)")
ax.set_xlabel("Eviction Scheme")
ax.set_ylabel("Hit Rate (%)")
ax.set_xticks(xs, schemes)
for x, y, c in zip(xs, ys, bar_colors):
    ax.annotate(f"{y:.1f}\u00A0%", (x, y), xytext=(0, 6), textcoords="offset points",
                ha="center", va="bottom", color=c, fontweight="bold")
beautify(ax)
savefig(os.path.join("figures”, "figure_3.png"))
