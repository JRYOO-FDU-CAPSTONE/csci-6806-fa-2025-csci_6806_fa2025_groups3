import matplotlib.pyplot as plt
plt.rcParams.update({"font.size": 11})

tau_x   = [0.05, 0.10, 0.20, 0.50, 1.00]
tau_norm= [1.086, 1.052, 1.034, 1.000, 0.974]
cap_x    = [0.1, 0.3, 0.5, 0.7, 0.9]
cap_norm = [1.060, 1.000, 0.945, 0.975, 1.000]
atti_x    = [0.1, 0.3, 0.5, 0.7, 0.9]
atti_norm = [1.022, 0.934, 1.025, 1.089, 1.245]

def annotate(ax, xs, ys, color):
    ymin = min(ys)
    spread = max(ys) - min(ys) or 0.05
    off = 0.03 * spread
    for x, y in zip(xs, ys):
        below = abs(y - ymin) < 1e-9
        ax.text(x, y - off if below else y + off, f"{y:.3f}",
                ha="center", va="top" if below else "bottom",
                color=color, fontsize=11, fontweight=600)

