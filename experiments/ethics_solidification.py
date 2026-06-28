"""Ethics e4 -- solidification: the dynamical death of a generative cycle (sec. 5.3).

Injustice, dynamically, is not a structure failing to be generated but a living,
circulating structure *running down* into a frozen, appropriative one. The power field
accumulates the history of value flux (eq. 3); when it accumulates without forgetting
(alpha-dominant), it acts as historical drag (~ |p|^2) that damps the vorticity until
circulation -- and hence surplus -- goes to zero. When power forgets (beta-dominant), the
flow stays alive.

Justice then has a dynamical reading: keep the relation away from the solidified fixed
point -- keep value circulating.

Run:  PYTHONPATH=. python experiments/ethics_solidification.py
"""

from __future__ import annotations

import numpy as np

from fluid_socio import Grid2D
from fluid_socio.fluid import FluidModel
from _common import get_plt, save


def vortices(grid, seed=1):
    rng = np.random.default_rng(seed)
    omega = grid.zero()
    for _ in range(6):
        cx, cy = rng.uniform(0, grid.lx), rng.uniform(0, grid.ly)
        s = rng.uniform(0.4, 0.7)
        amp = rng.choice([-1, 1]) * rng.uniform(4, 7)
        omega += amp * np.exp(-((grid.X - cx) ** 2 + (grid.Y - cy) ** 2) / (2 * s**2))
    return omega - omega.mean()


def enstrophy(grid, omega):
    return 0.5 * float(np.sum(omega**2)) * grid.cell_area()


def run(grid, omega0, alpha, beta, kappa, steps=1000, dt=2e-3):
    model = FluidModel(grid, nu=8e-4, alpha=alpha, beta=beta, power_gain=0.0,
                       drag_kappa=kappa)
    state = model.make_state(omega=omega0)
    ens = [enstrophy(grid, state.omega)]
    for _ in range(steps):
        state = model.step(state, dt)
        ens.append(enstrophy(grid, state.omega))
    return state, np.array(ens)


def main():
    grid = Grid2D(96, 96)
    omega0 = vortices(grid)
    e0 = enstrophy(grid, omega0)

    kappa = 0.25
    ratios = [(0.3, 5.0, "beta-dominant (forgets) -> stays alive"),
              (1.5, 1.5, "balanced"),
              (6.0, 0.3, "alpha-dominant (remembers) -> solidifies")]
    curves = []
    finals = {}
    for alpha, beta, label in ratios:
        state, ens = run(grid, omega0, alpha, beta, kappa)
        curves.append((label, alpha / beta, ens))
        finals[label] = state.omega
        print(f"e4 solidification: alpha/beta={alpha/beta:4.1f}  "
              f"enstrophy {ens[0]:.1f} -> {ens[-1]:.1f}  "
              f"({100*ens[-1]/ens[0]:.0f}% of initial circulation remains)")

    plt = get_plt()
    if plt is None:
        return
    fig = plt.figure(figsize=(15, 5))
    ax0 = fig.add_subplot(1, 3, 1)
    colors = ["seagreen", "goldenrod", "indianred"]
    tt = np.arange(len(curves[0][2])) * 2e-3
    for (label, ratio, ens), c in zip(curves, colors):
        ax0.plot(tt, ens / e0, color=c, lw=2.3, label=f"a/b={ratio:.1f}")
    ax0.set_xlabel("time"); ax0.set_ylabel("circulation (enstrophy) / initial")
    ax0.set_title("alpha/beta controls solidification\n(circulation = the capacity to "
                  "generate surplus)")
    ax0.legend(); ax0.grid(True, alpha=0.3); ax0.set_ylim(0, 1.05)

    alive = finals["beta-dominant (forgets) -> stays alive"]
    dead = finals["alpha-dominant (remembers) -> solidifies"]
    vmax = np.max(np.abs(omega0))
    ax1 = fig.add_subplot(1, 3, 2)
    ax1.imshow(alive.T, origin="lower", cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    ax1.set_title("ALIVE (beta-dominant)\ncirculation persists"); ax1.set_xticks([]); ax1.set_yticks([])
    ax2 = fig.add_subplot(1, 3, 3)
    ax2.imshow(dead.T, origin="lower", cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    ax2.set_title("SOLIDIFIED (alpha-dominant)\nvorticity -> 0, the bad cycle")
    ax2.set_xticks([]); ax2.set_yticks([])

    fig.suptitle("Ethics e4: solidification -- a generative cycle collapsing to a frozen, "
                 "appropriative fixed point (justice = keeping it circulating)", fontsize=12)
    fig.tight_layout()
    save(fig, "e4_solidification.png")


if __name__ == "__main__":
    main()
