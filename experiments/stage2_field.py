"""Stage II -- the relational field and its defects (paper sec. 4).

  06  symmetry breaking G -> H        -- the vacuum manifold M = G/H ~= S^1 (eq. 7)
  07  subjects as defects             -- pi_1(S^1) = Z: integer-winding subjects (eq. 9)
  08  abelian holonomy around a defect-- hol(gamma) sees only the enclosed charge (eq.10)

Run:  PYTHONPATH=. python experiments/stage2_field.py
"""

from __future__ import annotations

import numpy as np

from fluid_socio import Grid2D
from fluid_socio.field import (
    phase_field, winding_density, find_defects, loop_winding, running_holonomy,
)
from _common import get_plt, save


# --------------------------------------------------------------------------- #
# 06  Symmetry breaking: the vacuum manifold M = G/H ~= S^1
# --------------------------------------------------------------------------- #
def fig_symmetry_breaking():
    # The Mexican-hat potential V(Phi) = (|Phi|^2 - 1)^2 over the complex order parameter.
    n = 300
    re = np.linspace(-1.8, 1.8, n)
    RE, IM = np.meshgrid(re, re)
    mod2 = RE**2 + IM**2
    V = (mod2 - 1.0) ** 2

    # A realized broken state on a 2D domain: a phase field with two defects, with the
    # amplitude |Phi| dipping to zero at the cores.
    grid = Grid2D(128, 128)
    defects = [(grid.lx * 0.38, grid.ly * 0.5, +1), (grid.lx * 0.64, grid.ly * 0.5, -1)]
    theta = phase_field(grid, defects)
    amp = np.ones_like(theta)
    for cx, cy, _ in defects:
        r = np.hypot(grid.X - cx, grid.Y - cy)
        amp = amp * np.tanh(r / 0.18)

    print("06 symmetry breaking: vacuum manifold M = G/H ~= S^1 (|Phi| = 1 circle); "
          "two defects placed (+1, -1).")

    plt = get_plt()
    if plt is None:
        return
    import matplotlib.colors as mcolors
    fig = plt.figure(figsize=(13, 5.4))

    ax0 = fig.add_subplot(1, 2, 1)
    cf = ax0.contourf(RE, IM, V, levels=30, cmap="inferno")
    th = np.linspace(0, 2 * np.pi, 200)
    ax0.plot(np.cos(th), np.sin(th), color="cyan", lw=2.5)
    ax0.text(0, 0, "G\n(symmetric:\nPhi = 0)", color="white", ha="center", va="center",
             fontsize=9)
    ax0.text(0.0, 1.25, "M = G/H ~= S^1\n(vacuum manifold)", color="cyan", ha="center",
             fontsize=10, weight="bold")
    ax0.set_aspect("equal"); ax0.set_xlabel("Re Phi"); ax0.set_ylabel("Im Phi")
    ax0.set_title("the potential and its broken vacua")
    fig.colorbar(cf, ax=ax0, fraction=0.046, label="V(Phi)")

    # Right: broken field, phase as hue, amplitude as brightness.
    ax1 = fig.add_subplot(1, 2, 2)
    hue = (theta + np.pi) / (2 * np.pi)
    hsv = np.stack([hue, np.ones_like(hue), np.clip(amp, 0, 1)], axis=-1)
    rgb = mcolors.hsv_to_rgb(hsv)
    ax1.imshow(np.transpose(rgb, (1, 0, 2)), origin="lower")
    ax1.set_title("a realized broken state Phi(x): phase = hue, |Phi| = brightness")
    ax1.set_xticks([]); ax1.set_yticks([])

    fig.suptitle("Stage II (eq. 7): breaking G -> H generates the order-parameter space "
                 "M = G/H; subjects appear only after breaking", fontsize=12)
    fig.tight_layout()
    save(fig, "06_symmetry_breaking.png")


# --------------------------------------------------------------------------- #
# 07  Subjects as defects: pi_1(S^1) = Z
# --------------------------------------------------------------------------- #
def fig_defects():
    grid = Grid2D(160, 160)
    defects = [
        (grid.lx * 0.30, grid.ly * 0.32, +1),
        (grid.lx * 0.70, grid.ly * 0.34, -1),
        (grid.lx * 0.35, grid.ly * 0.70, -1),
        (grid.lx * 0.68, grid.ly * 0.68, +1),
    ]
    theta = phase_field(grid, defects)
    found = find_defects(grid, theta)
    charges = sorted(c for _, _, c in found)
    print(f"07 subjects as defects: placed {len(defects)}, detected {len(found)}; "
          f"charges {charges}  (pi_1(S^1) = Z, integer winding)")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.8))

    im = ax[0].imshow(theta.T, origin="lower", cmap="twilight", vmin=-np.pi, vmax=np.pi)
    for x, y, q in found:
        ax[0].scatter([x / grid.dx], [y / grid.dy], s=120,
                      facecolors="none",
                      edgecolors="lime" if q > 0 else "red", linewidths=2)
        ax[0].text(x / grid.dx, y / grid.dy + 6, f"{q:+d}",
                   color="lime" if q > 0 else "red", ha="center", weight="bold")
    ax[0].set_title("order-parameter phase theta(x) on S^1\n(defects = subjects, "
                    "charge = winding)")
    ax[0].set_xticks([]); ax[0].set_yticks([])
    fig.colorbar(im, ax=ax[0], fraction=0.046, label="theta")

    w = winding_density(grid, theta)
    vmax = np.max(np.abs(w))
    im2 = ax[1].imshow(w.T, origin="lower", cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    ax[1].set_title("topological charge density\n(persistence = conservation of winding)")
    ax[1].set_xticks([]); ax[1].set_yticks([])
    fig.colorbar(im2, ax=ax[1], fraction=0.046)

    fig.suptitle("Stage II (eq. 9): a subject is a defect carrying a non-trivial class "
                 "in pi_k(G/H) -- identity is topological, not substantial", fontsize=12)
    fig.tight_layout()
    save(fig, "07_defects_winding.png")


# --------------------------------------------------------------------------- #
# 08  Abelian holonomy: it sees only the enclosed charge
# --------------------------------------------------------------------------- #
def fig_abelian_holonomy():
    grid = Grid2D(160, 160)
    cx, cy = grid.lx * 0.5, grid.ly * 0.5
    theta = phase_field(grid, [(cx, cy, +1)])

    enclosing = (40, 120, 40, 120)     # contains the defect
    avoiding = (95, 150, 95, 150)      # does not

    w_in = loop_winding(grid, theta, *enclosing)
    w_out = loop_winding(grid, theta, *avoiding)
    run = running_holonomy(grid, theta, *enclosing)
    print(f"08 abelian holonomy: enclosing loop winding = {w_in:+.3f} (=> hol = e^(2pi i)); "
          f"avoiding loop winding = {w_out:+.3f}")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.6))

    ax[0].imshow(theta.T, origin="lower", cmap="twilight", vmin=-np.pi, vmax=np.pi)
    for box, color, lab, wv in [(enclosing, "lime", "encloses defect", w_in),
                                (avoiding, "white", "avoids defect", w_out)]:
        i0, i1, j0, j1 = box
        ax[0].plot([i0, i1, i1, i0, i0], [j0, j0, j1, j1, j0], color=color, lw=2)
        ax[0].text((i0 + i1) / 2, j1 + 4, f"{lab}\nwinding = {wv:+.2f}",
                   color=color, ha="center", fontsize=8, weight="bold")
    ax[0].scatter([cx / grid.dx], [cy / grid.dy], s=80, marker="x", color="red")
    ax[0].set_title("a single +1 defect and two loops")
    ax[0].set_xticks([]); ax[0].set_yticks([])

    ax[1].plot(np.arange(len(run)), run / np.pi, color="crimson")
    ax[1].axhline(2.0, ls="--", color="gray")
    ax[1].text(0.02, 2.05, "2 pi  (= 1 full winding)", color="gray", transform=
               ax[1].get_yaxis_transform())
    ax[1].set_xlabel("position along the loop")
    ax[1].set_ylabel("accumulated phase / pi")
    ax[1].set_title("holonomy builds up over the WHOLE loop\n(present nowhere along it; "
                    "a residue of the circuit)")
    ax[1].grid(True, alpha=0.3)

    fig.suptitle("Stage II (eq. 10): the abelian holonomy is quantized by the charge it "
                 "encloses -- surplus is a property of the cycle, not of any point",
                 fontsize=12)
    fig.tight_layout()
    save(fig, "08_abelian_holonomy.png")


def main():
    fig_symmetry_breaking()
    fig_defects()
    fig_abelian_holonomy()


if __name__ == "__main__":
    main()
