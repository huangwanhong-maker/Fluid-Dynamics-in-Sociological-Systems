"""Demonstration: the value flow actually runs.

Evolves a random initial vorticity field (2D decaying turbulence) and saves a montage
of vorticity snapshots plus the total enstrophy curve, so the integrator's behaviour is
visible: like vortices merge, fine structure dissipates, circulation organizes into
large coherent structures. This is the "flow layer" of the model running on its own,
before any power coupling.

Run:  PYTHONPATH=. python experiments/flow_demo.py
"""

from __future__ import annotations

import os

import numpy as np

from fluid_socio import Grid2D
from fluid_socio.fluid import FluidModel


def random_vorticity(grid, seed=0, k_peak=6.0, amp=8.0):
    """Random vorticity with energy concentrated near wavenumber ``k_peak``."""
    rng = np.random.default_rng(seed)
    noise = rng.standard_normal((grid.nx, grid.ny))
    nhat = np.fft.fft2(noise)
    k = np.sqrt(grid.K2)
    spectrum = (k**2) * np.exp(-((k - k_peak) ** 2) / (2 * 2.0**2))
    field = np.real(np.fft.ifft2(nhat * spectrum))
    field -= field.mean()
    return amp * field / np.max(np.abs(field))


def enstrophy(grid, omega):
    """Total enstrophy 0.5 * integral(omega^2) -- a scalar measure of how much
    circulation the flow carries."""
    return 0.5 * float(np.sum(omega**2)) * grid.cell_area()


def main():
    grid = Grid2D(128, 128)
    model = FluidModel(grid, nu=2e-3)  # pure flow: no power coupling
    state = model.make_state(omega=random_vorticity(grid, seed=3))

    n_snaps = 5
    steps_between = 120
    dt = 1.5e-3

    snapshots = [state.omega.copy()]
    times = [0.0]
    ens_t, ens_v = [0.0], [enstrophy(grid, state.omega)]

    for s in range(n_snaps - 1):
        for _ in range(steps_between):
            state = model.step(state, dt)
            ens_t.append(model.t)
            ens_v.append(enstrophy(grid, state.omega))
        snapshots.append(state.omega.copy())
        times.append(model.t)

    print("Flow demonstration -- 2D decaying turbulence")
    print("=" * 50)
    for t, w in zip(times, snapshots):
        print(f"  t = {t:5.2f}   enstrophy = {enstrophy(grid, w):8.3f}   "
              f"max|omega| = {np.max(np.abs(w)):6.3f}")

    _save_figure(grid, snapshots, times, ens_t, ens_v)


def _save_figure(grid, snapshots, times, ens_t, ens_v):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover
        print(f"(skipping figure: {exc})")
        return

    os.makedirs("assets", exist_ok=True)
    n = len(snapshots)
    fig = plt.figure(figsize=(3 * n, 6))
    vmax = np.max(np.abs(snapshots[0]))

    for i, (t, w) in enumerate(zip(times, snapshots)):
        ax = fig.add_subplot(2, n, i + 1)
        ax.imshow(w.T, origin="lower", cmap="RdBu_r", vmin=-vmax, vmax=vmax)
        ax.set_title(f"vorticity, t = {t:.2f}")
        ax.set_xticks([])
        ax.set_yticks([])

    ax = fig.add_subplot(2, 1, 2)
    ax.plot(ens_t, ens_v, color="black")
    ax.set_xlabel("time")
    ax.set_ylabel("enstrophy")
    ax.set_title("Enstrophy decays as fine structure dissipates (viscous solidification)")
    ax.grid(True, alpha=0.3)

    fig.suptitle("Value flow on its own: 2D decaying turbulence", fontsize=13)
    fig.tight_layout()
    path = os.path.join("assets", "flow_demo.png")
    fig.savefig(path, dpi=120)
    print(f"  figure saved to {path}")


if __name__ == "__main__":
    main()
