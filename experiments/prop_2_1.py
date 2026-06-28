"""Demonstration: appropriation generates no circulation (Proposition 2.1).

Splits a power force into its appropriative (gradient) and generative (solenoidal)
parts via the Helmholtz decomposition, evolves the value flow under each, and shows
that only the generative part moves the holonomy. Saves a figure to ``outputs/``.

Run:  PYTHONPATH=. python experiments/prop_2_1.py
"""

from __future__ import annotations

import os

import numpy as np

from fluid_socio import Grid2D, helmholtz_decomposition, circulation_loop
from fluid_socio.operators import holonomy_sign
from fluid_socio.fluid import FluidModel


def smooth_field(grid, seed):
    rng = np.random.default_rng(seed)
    f = grid.zero()
    for kx, ky in [(1, 0), (0, 1), (2, 1), (1, 2), (3, 1)]:
        a, b = rng.standard_normal(2)
        f += a * np.cos(kx * grid.X + ky * grid.Y) + b * np.sin(kx * grid.X + ky * grid.Y)
    return f


def evolve(grid, omega0, px, py, steps=60, dt=2e-3):
    model = FluidModel(grid, nu=1e-3, alpha=0.0, beta=0.0, power_gain=1.0)
    state = model.make_state(omega=omega0)
    state.px, state.py = px, py
    for _ in range(steps):
        state = model.step(state, dt)
    ux, uy = model.velocity(state.omega)
    return state.omega, circulation_loop(grid, ux, uy, 24, 104, 24, 104)


def main():
    grid = Grid2D(128, 128)
    omega0 = -grid.laplacian(smooth_field(grid, seed=5))

    raw_x, raw_y = smooth_field(grid, 6), smooth_field(grid, 7)
    (gx, gy), (sx, sy) = helmholtz_decomposition(grid, raw_x, raw_y)

    zero = grid.zero()
    _, c_base = evolve(grid, omega0, zero, zero)
    w_grad, c_grad = evolve(grid, omega0, gx, gy)
    w_sol, c_sol = evolve(grid, omega0, sx, sy)

    grad_contrib = c_grad - c_base
    sol_contrib = c_sol - c_base

    print("Proposition 2.1 -- appropriation generates no circulation")
    print("=" * 60)
    print(f"  baseline holonomy (no force)      : {c_base:+.6f}")
    print(f"  appropriative (gradient) force    : {c_grad:+.6f}")
    print(f"  generative   (solenoidal) force   : {c_sol:+.6f}")
    print("-" * 60)
    print(f"  contribution of appropriation     : {grad_contrib:+.3e}  "
          f"(sign {holonomy_sign(grad_contrib)})")
    print(f"  contribution of generation        : {sol_contrib:+.3e}  "
          f"(sign {holonomy_sign(sol_contrib)})")
    print("-" * 60)
    ratio = abs(sol_contrib) / max(abs(grad_contrib), 1e-15)
    print(f"  generation / appropriation ratio  : {ratio:.3e}")
    print("  => appropriation is curl-free; only circulation generates surplus.")

    _save_figure(grid, gx, gy, sx, sy, w_grad - _evolve_base(grid, omega0),
                 w_sol - _evolve_base(grid, omega0), grad_contrib, sol_contrib)


def _evolve_base(grid, omega0):
    w, _ = evolve(grid, omega0, grid.zero(), grid.zero())
    return w


def _save_figure(grid, gx, gy, sx, sy, dw_grad, dw_sol, grad_contrib, sol_contrib):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover
        print(f"(skipping figure: {exc})")
        return

    os.makedirs("assets", exist_ok=True)
    fig, ax = plt.subplots(2, 2, figsize=(10, 9))

    sl = (slice(None, None, 6), slice(None, None, 6))
    ax[0, 0].quiver(grid.X[sl], grid.Y[sl], gx[sl], gy[sl])
    ax[0, 0].set_title("Appropriative force (gradient part)")
    ax[0, 1].quiver(grid.X[sl], grid.Y[sl], sx[sl], sy[sl])
    ax[0, 1].set_title("Generative force (solenoidal part)")

    vmax = max(np.max(np.abs(dw_grad)), np.max(np.abs(dw_sol)), 1e-12)
    ax[1, 0].imshow(dw_grad.T, origin="lower", cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    ax[1, 0].set_title(f"Vorticity change from appropriation\n(holonomy {grad_contrib:+.2e})")
    ax[1, 1].imshow(dw_sol.T, origin="lower", cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    ax[1, 1].set_title(f"Vorticity change from generation\n(holonomy {sol_contrib:+.2e})")
    for a in ax.flat:
        a.set_xticks([])
        a.set_yticks([])

    fig.suptitle("Proposition 2.1: only generative (solenoidal) power moves the holonomy",
                 fontsize=13)
    fig.tight_layout()
    path = os.path.join("assets", "04_proposition_2_1.png")
    fig.savefig(path, dpi=120)
    print(f"  figure saved to {path}")


if __name__ == "__main__":
    main()
