"""Stage III -- braid statistics and the discrimination constraint (paper sec. 4.7-6).

  10  braid generators and Yang-Baxter -- sigma_i sigma_{i+1} sigma_i =
                                           sigma_{i+1} sigma_i sigma_{i+1} (eq. 15)
  11  the three non-abelian demands     -- power, resonance, generativity (sec. 5.3)
  12  universality vs discrimination     -- non-universal (Ising, finite image, can
                                           discriminate) vs universal (Fibonacci, dense
                                           image, cannot) (Prop 6.1)

Run:  PYTHONPATH=. python experiments/stage4_braid.py
"""

from __future__ import annotations

import numpy as np

from fluid_socio.braid import (
    ising_generators, fibonacci_generators, braid_relation_residual, commutator_residual,
    reachable_states, count_distinct, fibonacci_fusion_dim,
)
from _common import get_plt, save


# --------------------------------------------------------------------------- #
# braid-diagram drawing
# --------------------------------------------------------------------------- #
def draw_braid(ax, word, n, colors, row_h=1.0, lw=3.0):
    """Draw a braid diagram. ``word`` is a list of 1-based generator indices (positive =
    left strand over, negative = right strand over). Time runs downward."""
    slots = list(range(n))  # slots[x] = strand id currently in column x
    y = 0.0
    for g in word:
        i = abs(g) - 1  # 0-based left column of the crossing
        over_left = g > 0
        for c in range(n):
            if c in (i, i + 1):
                continue
            ax.plot([c, c], [y, y - row_h], color=colors[slots[c]], lw=lw, solid_capstyle="round")
        # the two crossing strands: left column goes to the right, right column to left
        t = np.linspace(0, 1, 40)
        ya = y - row_h * t
        left_x = i + 0.5 * (1 - np.cos(np.pi * t))         # column i  -> i+1
        right_x = (i + 1) - 0.5 * (1 - np.cos(np.pi * t))  # column i+1 -> i
        sid_left, sid_right = slots[i], slots[i + 1]
        if over_left:  # the strand starting at the left column passes OVER
            over_x, over_c = left_x, colors[sid_left]
            under_x, under_c = right_x, colors[sid_right]
        else:
            over_x, over_c = right_x, colors[sid_right]
            under_x, under_c = left_x, colors[sid_left]
        _draw_with_gap(ax, under_x, ya, under_c, lw)                 # under (broken)
        ax.plot(over_x, ya, color=over_c, lw=lw, solid_capstyle="round", zorder=3)  # over
        slots[i], slots[i + 1] = slots[i + 1], slots[i]
        y -= row_h
    ax.set_xlim(-0.6, n - 0.4)
    ax.set_ylim(y - 0.2, 0.2)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_aspect("equal")


def _draw_with_gap(ax, xs, ys, color, lw, gap=0.16):
    """Draw an under-strand: same curve but with a gap at the crossing midpoint."""
    n = len(xs)
    mid = n // 2
    half = max(1, int(gap * n))
    ax.plot(xs[: mid - half], ys[: mid - half], color=color, lw=lw, solid_capstyle="round",
            zorder=2)
    ax.plot(xs[mid + half:], ys[mid + half:], color=color, lw=lw, solid_capstyle="round",
            zorder=2)


# --------------------------------------------------------------------------- #
# 10  braid generators and the Yang-Baxter relation
# --------------------------------------------------------------------------- #
def fig_braid_relation():
    cols = ["#d62728", "#1f77b4", "#2ca02c"]
    res_i = braid_relation_residual(*ising_generators())
    res_f = braid_relation_residual(*fibonacci_generators())
    print(f"10 Yang-Baxter residual: Ising = {res_i:.2e}, Fibonacci = {res_f:.2e} "
          "(both satisfy the braid relation)")

    plt = get_plt()
    if plt is None:
        return
    fig = plt.figure(figsize=(13, 5.5))

    ax1 = fig.add_subplot(1, 4, 1)
    draw_braid(ax1, [1], 2, cols)
    ax1.set_title("sigma_1\n(swap 1,2)")
    ax2 = fig.add_subplot(1, 4, 2)
    draw_braid(ax2, [-1], 2, cols)
    ax2.set_title("sigma_1^{-1}")

    ax3 = fig.add_subplot(1, 4, 3)
    draw_braid(ax3, [1, 2, 1], 3, cols)
    ax3.set_title("sigma_1 sigma_2 sigma_1")
    ax4 = fig.add_subplot(1, 4, 4)
    draw_braid(ax4, [2, 1, 2], 3, cols)
    ax4.set_title("sigma_2 sigma_1 sigma_2")

    fig.text(0.62, 0.5, "=", fontsize=30, ha="center", va="center")
    fig.suptitle("Stage III (eq. 15): the braid group is computed (pi_1 of defect "
                 "configuration space); its non-trivial relation is Yang-Baxter",
                 fontsize=12)
    fig.tight_layout()
    save(fig, "10_braid_relation.png")


# --------------------------------------------------------------------------- #
# 11  the three non-abelian demands (sec. 5.3)
# --------------------------------------------------------------------------- #
def fig_three_demands():
    b1, b2 = fibonacci_generators()
    comm = commutator_residual(b1, b2)
    dims = [fibonacci_fusion_dim(n) for n in range(1, 8)]
    print(f"11 three demands: power |rho(s1)rho(s2)-rho(s2)rho(s1)| = {comm:.3f}; "
          f"resonance dim H_n = {dims}; generativity tau x tau = 1 + tau (2 channels)")

    plt = get_plt()
    if plt is None:
        return
    fig = plt.figure(figsize=(14, 4.8))
    cols = ["#d62728", "#1f77b4", "#2ca02c"]

    # Power: sigma1 sigma2 vs sigma2 sigma1 as braids + commutator value.
    ax0 = fig.add_subplot(1, 3, 1)
    diff = np.abs(b1 @ b2 - b2 @ b1)
    im = ax0.imshow(diff, cmap="magma")
    ax0.set_title(f"POWER (premise P)\n|rho(s1 s2) - rho(s2 s1)| != 0\ncommutator = "
                  f"{comm:.3f}")
    ax0.set_xticks([0, 1]); ax0.set_yticks([0, 1])
    fig.colorbar(im, ax=ax0, fraction=0.046)

    # Resonance: fusion space dimension > 1.
    ax1 = fig.add_subplot(1, 3, 2)
    ax1.bar(range(1, 8), dims, color="teal")
    ax1.set_xlabel("number of anyons n"); ax1.set_ylabel("dim H_n")
    ax1.set_title("RESONANCE (premise R)\ndim H_n > 1: a degenerate joint state\n"
                  "(Fibonacci numbers)")
    for x, d in zip(range(1, 8), dims):
        ax1.text(x, d + 0.1, str(d), ha="center", fontsize=8)

    # Generativity: multi-channel fusion tau x tau = 1 + tau.
    ax2 = fig.add_subplot(1, 3, 3)
    ax2.axis("off")
    ax2.set_title("GENERATIVITY (premise G)\nmulti-channel fusion: outcome not fixed")
    # draw two incoming tau and two outgoing channels
    ax2.plot([0.2, 0.5], [0.9, 0.55], color=cols[0], lw=3)
    ax2.plot([0.8, 0.5], [0.9, 0.55], color=cols[1], lw=3)
    ax2.text(0.15, 0.93, "tau", fontsize=12); ax2.text(0.82, 0.93, "tau", fontsize=12)
    ax2.plot([0.5, 0.30], [0.55, 0.18], color="gray", lw=3)
    ax2.plot([0.5, 0.70], [0.55, 0.18], color="gray", lw=3)
    ax2.text(0.26, 0.08, "1", fontsize=13, color="black")
    ax2.text(0.68, 0.08, "tau", fontsize=13, color="black")
    ax2.text(0.5, 0.62, "tau x tau", ha="center", fontsize=11, weight="bold")
    ax2.text(0.5, 0.30, "= 1 + tau", ha="center", fontsize=11)
    ax2.set_xlim(0, 1); ax2.set_ylim(0, 1)

    fig.suptitle("Stage III (sec. 5.3): power, resonance-without-fusion, and generativity "
                 "each force a non-abelian representation", fontsize=12)
    fig.tight_layout()
    save(fig, "11_three_demands.png")


# --------------------------------------------------------------------------- #
# 12  universality vs discrimination (Prop 6.1)
# --------------------------------------------------------------------------- #
def _sphere(ax):
    u = np.linspace(0, 2 * np.pi, 40); v = np.linspace(0, np.pi, 20)
    x = np.outer(np.cos(u), np.sin(v)); y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(x, y, z, color="gray", alpha=0.15, rstride=4, cstride=4)
    ax.plot_surface(x, y, z, color="lightgray", alpha=0.08, linewidth=0)
    ax.set_box_aspect((1, 1, 1)); ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])


def fig_universality():
    ising = ising_generators()
    fib = fibonacci_generators()
    pts_i = reachable_states(ising, n_words=2500, max_len=16, seed=3)
    pts_f = reachable_states(fib, n_words=2500, max_len=16, seed=3)
    n_i, n_f = count_distinct(pts_i), count_distinct(pts_f)
    print(f"12 Prop 6.1: Ising reachable points = {n_i} (finite -> robust discrimination); "
          f"Fibonacci = {n_f} (dense -> no robust discrimination)")

    plt = get_plt()
    if plt is None:
        return
    fig = plt.figure(figsize=(13, 6))
    ax0 = fig.add_subplot(1, 2, 1, projection="3d")
    _sphere(ax0)
    ax0.scatter(pts_i[:, 0], pts_i[:, 1], pts_i[:, 2], color="crimson", s=60, depthshade=True)
    ax0.set_title(f"NON-UNIVERSAL (Ising)\nreachable holonomies: {n_i} discrete points\n"
                  "=> a robust good/bad predicate EXISTS", fontsize=10)

    ax1 = fig.add_subplot(1, 2, 2, projection="3d")
    _sphere(ax1)
    ax1.scatter(pts_f[:, 0], pts_f[:, 1], pts_f[:, 2], color="navy", s=4, alpha=0.4)
    ax1.set_title(f"UNIVERSAL (Fibonacci)\nreachable holonomies: dense (~{n_f} sampled)\n"
                  "=> NO robust good/bad predicate", fontsize=10)

    fig.suptitle("Stage III (Prop 6.1): discriminating power requires non-universality -- "
                 "omnipotence and normative judgment are incompatible", fontsize=12)
    fig.tight_layout()
    save(fig, "12_universality_discrimination.png")


def main():
    fig_braid_relation()
    fig_three_demands()
    fig_universality()


if __name__ == "__main__":
    main()
