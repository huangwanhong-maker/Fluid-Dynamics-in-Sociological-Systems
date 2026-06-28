"""Stage IV / V -- the protected remainder and the relational base (paper sec. 7, 9).

  16  skeleton and flesh    -- the holonomy is robust to local perturbation (skeleton,
                               carries the good/bad criterion); local detail is exactly
                               what topological protection discards (flesh, token identity)
  17  the relational base    -- a group as configuration space (group field theory): the
                               Cayley graph, a field Phi: Gamma -> M, and power as the
                               non-commutativity of the base, g g' != g' g

Run:  PYTHONPATH=. python experiments/stage5_limits.py
"""

from __future__ import annotations

import numpy as np

from fluid_socio import Grid2D
from fluid_socio.field import phase_field, loop_winding
from _common import get_plt, save


# --------------------------------------------------------------------------- #
# 16  skeleton and flesh
# --------------------------------------------------------------------------- #
def _smooth_noise(grid, amp, seed):
    rng = np.random.default_rng(seed)
    field = grid.zero()
    for kx, ky in [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2), (2, 2)]:
        a, b = rng.standard_normal(2)
        field += a * np.cos(kx * grid.X + ky * grid.Y) + b * np.sin(kx * grid.X + ky * grid.Y)
    field /= np.max(np.abs(field))
    return amp * field


def fig_skeleton_flesh():
    grid = Grid2D(160, 160)
    cx, cy = grid.lx * 0.5, grid.ly * 0.5
    clean = phase_field(grid, [(cx, cy, +1)])
    # Local perturbation ("flesh"): smooth, sub-threshold so it spawns no new defect.
    noisy = np.angle(np.exp(1j * (clean + _smooth_noise(grid, 0.9, seed=4))))

    box = (30, 130, 30, 130)
    w_clean = loop_winding(grid, clean, *box)
    w_noisy = loop_winding(grid, noisy, *box)
    # local (flesh) change: pointwise phase difference RMS
    flesh_rms = float(np.sqrt(np.mean(np.angle(np.exp(1j * (noisy - clean))) ** 2)))
    print(f"16 skeleton/flesh: enclosed holonomy winding (skeleton) {w_clean:+.3f} -> "
          f"{w_noisy:+.3f} (invariant under perturbation); "
          f"local detail (flesh) RMS change = {flesh_rms:.3f} rad (re-written)")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(1, 3, figsize=(15, 5))
    ax[0].imshow(clean.T, origin="lower", cmap="twilight", vmin=-np.pi, vmax=np.pi)
    ax[0].set_title(f"clean relation\nholonomy winding = {w_clean:+.2f}")
    ax[1].imshow(noisy.T, origin="lower", cmap="twilight", vmin=-np.pi, vmax=np.pi)
    ax[1].set_title(f"+ local perturbation (the flesh)\nholonomy winding = {w_noisy:+.2f} "
                    "(unchanged)")
    for a in ax[:2]:
        i0, i1, j0, j1 = box
        a.plot([i0, i1, i1, i0, i0], [j0, j0, j1, j1, j0], color="lime", lw=2)
        a.set_xticks([]); a.set_yticks([])

    ax[2].bar(["skeleton\n(holonomy winding)", "flesh\n(local detail)"],
              [abs(w_noisy - w_clean), flesh_rms], color=["steelblue", "darkorange"])
    ax[2].set_ylabel("change under perturbation")
    ax[2].set_title("topological protection:\nskeleton invariant, flesh re-written")

    fig.suptitle("Stage IV (sec. 7): value = topological skeleton (robust, normative) + "
                 "local flesh (token identity, exactly what protection discards)", fontsize=11)
    fig.tight_layout()
    save(fig, "16_skeleton_flesh.png")


# --------------------------------------------------------------------------- #
# 17  the relational base: group field theory on a Cayley graph
# --------------------------------------------------------------------------- #
def _elem_label(g):
    k, f = g
    rot = {0: "", 1: "r", 2: "r2", 3: "r3"}[k]
    if not rot and not f:
        return "e"
    return (rot if rot else "") + ("s" if f else "")


def _d4():
    """Dihedral group D_4 as elements (k, f) = r^k s^f, with right-multiplication by the
    generators r (rotation) and s (reflection). Returns elements, positions, and edges."""
    elems = [(k, f) for f in (0, 1) for k in range(4)]

    def mul_r(g):  # g * r
        k, f = g
        return ((k + (1 if f == 0 else -1)) % 4, f)

    def mul_s(g):  # g * s
        k, f = g
        return (k, (f + 1) % 2)

    pos = {}
    for (k, f) in elems:
        radius = 2.3 if f == 0 else 1.15
        ang = np.pi / 2 * k + (np.pi / 4 if f == 1 else 0)
        pos[(k, f)] = (radius * np.cos(ang), radius * np.sin(ang))
    return elems, pos, mul_r, mul_s


def fig_group_base():
    elems, pos, mul_r, mul_s = _d4()
    # A relational field Phi: Gamma -> M = S^1 that winds once around the rotation cycle
    # (a defect on the Cayley-graph loop e -> r -> r^2 -> r^3 -> e).
    phi = {g: (np.pi / 2) * g[0] for g in elems}

    # Non-commutativity of the base: r*s vs s*r land on different group elements = power.
    e = (0, 0)
    rs = mul_s(mul_r(e))   # (e*r)*s
    sr = mul_r(mul_s(e))   # (e*s)*r
    print(f"17 group base: D_4 Cayley graph; r*s = {rs}, s*r = {sr}  -> "
          f"{'NON-COMMUTATIVE (power)' if rs != sr else 'commutative'}; "
          "Phi winds once around the rotation 4-cycle (a relational defect)")

    plt = get_plt()
    if plt is None:
        return
    import matplotlib.cm as cm
    plt_mod = plt
    fig, ax = plt.subplots(1, 2, figsize=(13, 6))

    for axi, title, highlight in [
        (ax[0], "field Phi: Gamma -> M on the Cayley graph\n(color = phase; winds once "
                "= a relational defect)", "winding"),
        (ax[1], "power = non-commutativity of the base\nr*s  !=  s*r", "noncomm"),
    ]:
        # edges
        for g in elems:
            for mul, color, style in [(mul_r, "gray", "-"), (mul_s, "lightsteelblue", "-")]:
                h = mul(g)
                x0, y0 = pos[g]; x1, y1 = pos[h]
                axi.plot([x0, x1], [y0, y1], style, color=color, lw=1.2, alpha=0.7, zorder=1)
        # nodes
        for g in elems:
            x, y = pos[g]
            val = phi[g] % (2 * np.pi)
            c = cm.twilight(val / (2 * np.pi))
            axi.scatter([x], [y], s=460, color=c, edgecolors="black", zorder=3)
            label = _elem_label(g)
            # white text on dark nodes, black on light
            lum = 0.3 if (val > 2.2 and val < 4.1) else 0.8
            axi.text(x, y, label, ha="center", va="center", fontsize=9, zorder=4,
                     color="white" if lum < 0.5 else "black", weight="bold")
        axi.set_aspect("equal"); axi.axis("off"); axi.set_title(title, fontsize=10)

    # highlight the rotation 4-cycle (the loop carrying the winding) on the left
    cyc = [(0, 0), (1, 0), (2, 0), (3, 0), (0, 0)]
    xs = [pos[g][0] for g in cyc]; ys = [pos[g][1] for g in cyc]
    ax[0].plot(xs, ys, color="crimson", lw=2.5, zorder=2)

    # highlight r*s and s*r paths on the right
    def arrow(axi, g, h, color):
        x0, y0 = pos[g]; x1, y1 = pos[h]
        axi.annotate("", xy=(x1, y1), xytext=(x0, y0),
                     arrowprops=dict(arrowstyle="-|>", color=color, lw=2.5))
    e = (0, 0); r = mul_r(e); s = mul_s(e)
    arrow(ax[1], e, r, "crimson"); arrow(ax[1], r, mul_s(r), "crimson")
    arrow(ax[1], e, s, "navy"); arrow(ax[1], s, mul_r(s), "navy")
    ax[1].text(*pos[mul_s(r)], "  r*s", color="crimson", fontsize=10, weight="bold")
    ax[1].text(*pos[mul_r(s)], "  s*r", color="navy", fontsize=10, weight="bold")

    fig.suptitle("Stage V (sec. 9): the aggressive limit -- the configuration space is "
                 "itself a group; power is g g' != g' g", fontsize=12)
    fig.tight_layout()
    save(fig, "17_group_field_base.png")


def main():
    fig_skeleton_flesh()
    fig_group_base()


if __name__ == "__main__":
    main()
