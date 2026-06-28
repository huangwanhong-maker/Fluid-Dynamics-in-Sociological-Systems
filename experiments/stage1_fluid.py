"""Stage I -- the fluid model (paper sec. 2).

Four figures, one per load-bearing piece of the fluid layer:

  01  continuity with a source        -- value is generated, not conserved (eq. 1)
  02  power as the history of flux     -- p accumulates where value flowed (eq. 3)
  03  vorticity and holonomy           -- circulation around relational loops (eqs. 4-5)
  05  Helmholtz split of the power     -- dominance (gradient) vs generative (solenoidal)
                                          power, Remark 2.1

(04 is the Proposition 2.1 figure, produced by experiments/prop_2_1.py.)

Run:  PYTHONPATH=. python experiments/stage1_fluid.py
"""

from __future__ import annotations

import numpy as np

from fluid_socio import Grid2D, helmholtz_decomposition, circulation_loop
from fluid_socio.operators import holonomy_sign
from fluid_socio.fluid import FluidModel
from _common import get_plt, save


# --------------------------------------------------------------------------- #
# 01  Continuity with a source: value is not conserved (eq. 1)
# --------------------------------------------------------------------------- #
def fig_continuity_source():
    grid = Grid2D(128, 128)

    # A localized generation site S(x): value emerges here (an order parameter realizing
    # background potential), then is advected away by a swirling flow.
    cx, cy = grid.lx * 0.35, grid.ly * 0.5
    r2 = (grid.X - cx) ** 2 + (grid.Y - cy) ** 2
    source_field = 6.0 * np.exp(-r2 / (2 * 0.25**2))

    def source(g, state, t):
        return source_field

    # A fixed background swirl (one big vortex) to transport the generated value.
    psi = 1.5 * np.cos(grid.X) * np.cos(grid.Y)
    omega_bg = -grid.laplacian(psi)

    model = FluidModel(grid, nu=1e-3, source=source)
    state = model.make_state(omega=omega_bg, rho=grid.zero())  # start empty

    snaps, times = [], []
    for k in range(4):
        for _ in range(70):
            state = model.step(state, 2e-3)
        snaps.append(state.rho.copy())
        times.append(model.t)

    total = [float(np.sum(s) * grid.cell_area()) for s in snaps]
    print("01 continuity: total value stock grows from a source (not conserved):")
    for t, tot in zip(times, total):
        print(f"     t={t:4.2f}  total stock = {tot:7.3f}")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(1, 4, figsize=(16, 4.2))
    vmax = np.max(snaps[-1])
    for a, s, t in zip(ax, snaps, times):
        im = a.imshow(s.T, origin="lower", cmap="viridis", vmin=0, vmax=vmax)
        a.contour(source_field.T, levels=[1.0], colors="white", linewidths=0.8, alpha=0.6)
        a.set_title(f"value density rho,  t={t:.2f}")
        a.set_xticks([]); a.set_yticks([])
    fig.colorbar(im, ax=ax, fraction=0.012, pad=0.01)
    fig.suptitle("Stage I (eq. 1): value is generated at a source S and advected -- "
                 "it is not conserved", fontsize=13)
    save(fig, "01_continuity_source.png")


# --------------------------------------------------------------------------- #
# 02  Power as the history of value flux (eq. 3)
# --------------------------------------------------------------------------- #
def fig_power_history():
    grid = Grid2D(128, 128)

    # A steady swirling flow; power p accumulates along the flux J = rho u.
    psi = 1.2 * np.sin(grid.X) * np.sin(grid.Y)
    omega0 = -grid.laplacian(psi)

    def run(alpha, beta):
        model = FluidModel(grid, nu=2e-3, alpha=alpha, beta=beta, power_gain=0.0)
        state = model.make_state(omega=omega0)
        mags = []
        for _ in range(200):
            state = model.step(state, 2e-3)
            mags.append(float(np.mean(np.hypot(state.px, state.py))))
        return state, mags

    remember, mags_r = run(alpha=1.0, beta=0.2)   # alpha-dominant: power remembers
    forget, mags_f = run(alpha=1.0, beta=3.0)     # beta-dominant: power forgets

    print("02 power history: mean |p| at end -- "
          f"remember(a/b=5)={mags_r[-1]:.3f}  forget(a/b=0.33)={mags_f[-1]:.3f}")

    plt = get_plt()
    if plt is None:
        return
    fig = plt.figure(figsize=(14, 4.6))
    ux, uy = FluidModel(grid).velocity(omega0)

    ax0 = fig.add_subplot(1, 3, 1)
    sl = (slice(None, None, 7), slice(None, None, 7))
    ax0.quiver(grid.X[sl], grid.Y[sl], ux[sl], uy[sl], color="steelblue")
    ax0.set_title("value flux  J = rho u")
    ax0.set_xticks([]); ax0.set_yticks([])

    ax1 = fig.add_subplot(1, 3, 2)
    pmag = np.hypot(remember.px, remember.py)
    im = ax1.imshow(pmag.T, origin="lower", cmap="magma")
    ax1.set_title("accumulated power |p|\n(alpha-dominant: remembers)")
    ax1.set_xticks([]); ax1.set_yticks([])
    fig.colorbar(im, ax=ax1, fraction=0.046)

    ax2 = fig.add_subplot(1, 3, 3)
    tt = np.arange(len(mags_r)) * 2e-3
    ax2.plot(tt, mags_r, label="alpha/beta = 5  (remember)", color="crimson")
    ax2.plot(tt, mags_f, label="alpha/beta = 0.33  (forget)", color="navy")
    ax2.set_xlabel("time"); ax2.set_ylabel("mean |p|")
    ax2.set_title("power = flux history\n(eq. 3: d_t p = alpha J - beta p)")
    ax2.legend(); ax2.grid(True, alpha=0.3)

    fig.suptitle("Stage I (eq. 3): power is a gradient continually rewritten by the "
                 "history of value flux", fontsize=13)
    fig.tight_layout()
    save(fig, "02_power_history.png")


# --------------------------------------------------------------------------- #
# 03  Vorticity and holonomy around relational loops (eqs. 4-5)
# --------------------------------------------------------------------------- #
def fig_vorticity_holonomy():
    grid = Grid2D(128, 128)
    # Two co-rotating blobs of vorticity + one counter-rotating, to give loops of
    # different holonomy sign.
    def blob(cx, cy, s, amp):
        r2 = (grid.X - cx) ** 2 + (grid.Y - cy) ** 2
        return amp * np.exp(-r2 / (2 * s**2))

    omega = (blob(2.0, 3.1, 0.6, 6.0)
             + blob(4.3, 3.1, 0.6, 5.0)
             - blob(3.1, 1.2, 0.55, 5.5))
    omega -= omega.mean()
    ux, uy = FluidModel(grid).velocity(omega)

    # Measure holonomy around three loops.
    loops = {
        "A (encloses +)": (28, 60, 50, 82),
        "B (encloses +)": (70, 102, 50, 82),
        "C (encloses -)": (44, 86, 8, 40),
    }
    print("03 vorticity & holonomy: hol = oint u.dl around relational loops")
    results = {}
    for name, box in loops.items():
        h = circulation_loop(grid, ux, uy, *box)
        results[name] = (box, h)
        print(f"     loop {name:16s}  hol = {h:+.4f}   sign {holonomy_sign(h):+d}")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.6))
    vmax = np.max(np.abs(omega))
    im = ax[0].imshow(omega.T, origin="lower", cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    ax[0].set_title("value vorticity  omega = curl u  (eq. 4)")
    ax[0].set_xticks([]); ax[0].set_yticks([])
    fig.colorbar(im, ax=ax[0], fraction=0.046)

    spd = np.hypot(ux, uy)
    ax[1].streamplot(grid.x, grid.y, ux.T, uy.T, color=spd.T, cmap="viridis", density=1.3)
    for name, (box, h) in results.items():
        i0, i1, j0, j1 = box
        x0, x1 = grid.x[i0], grid.x[i1]
        y0, y1 = grid.y[j0], grid.y[j1]
        color = "crimson" if h > 0 else "navy"
        ax[1].plot([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0], color=color, lw=2)
        ax[1].text((x0 + x1) / 2, y1 + 0.1, f"{name}\nhol={h:+.2f}",
                   color=color, ha="center", fontsize=8, weight="bold")
    ax[1].set_title("holonomy  hol(gamma) = oint u.dl  (eq. 5)")
    ax[1].set_xticks([]); ax[1].set_yticks([])
    fig.suptitle("Stage I (eqs. 4-5): the normative object is circulation -- "
                 "the holonomy of a closed relational loop", fontsize=13)
    fig.tight_layout()
    save(fig, "03_vorticity_holonomy.png")


# --------------------------------------------------------------------------- #
# 05  Helmholtz split: dominance vs generative power (Remark 2.1)
# --------------------------------------------------------------------------- #
def fig_helmholtz_power():
    grid = Grid2D(128, 128)
    rng = np.random.default_rng(11)

    def smooth(seed):
        f = grid.zero()
        r = np.random.default_rng(seed)
        for kx, ky in [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)]:
            a, b = r.standard_normal(2)
            f += a * np.cos(kx * grid.X + ky * grid.Y) + b * np.sin(kx * grid.X + ky * grid.Y)
        return f

    fx, fy = smooth(1), smooth(2)
    (gx, gy), (sx, sy) = helmholtz_decomposition(grid, fx, fy)

    # The gradient part is the gradient of a potential -- a dominance landscape.
    potential = grid.solve_poisson(grid.div(fx, fy))
    curl_dom = grid.curl(gx, gy)
    curl_gen = grid.curl(sx, sy)
    print("03b Helmholtz: max|curl(dominance)| = "
          f"{np.max(np.abs(curl_dom)):.2e}   max|curl(generative)| = "
          f"{np.max(np.abs(curl_gen)):.2e}")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(1, 3, figsize=(15, 5))
    sl = (slice(None, None, 7), slice(None, None, 7))

    im0 = ax[0].imshow(potential.T, origin="lower", cmap="cividis")
    ax[0].quiver(grid.X[sl], grid.Y[sl], gx[sl], gy[sl], color="white", alpha=0.8)
    ax[0].set_title("DOMINANCE power (gradient part)\nflows downhill on a scalar order; "
                    "curl = 0")
    ax[0].set_xticks([]); ax[0].set_yticks([])
    fig.colorbar(im0, ax=ax[0], fraction=0.046)

    im1 = ax[1].imshow(curl_gen.T, origin="lower", cmap="RdBu_r")
    ax[1].quiver(grid.X[sl], grid.Y[sl], sx[sl], sy[sl], color="black", alpha=0.7)
    ax[1].set_title("GENERATIVE power (solenoidal part)\nnon-zero curl: a real source of "
                    "circulation")
    ax[1].set_xticks([]); ax[1].set_yticks([])
    fig.colorbar(im1, ax=ax[1], fraction=0.046)

    ax[2].bar(["dominance\n(gradient)", "generative\n(solenoidal)"],
              [np.max(np.abs(curl_dom)), np.max(np.abs(curl_gen))],
              color=["slategray", "crimson"])
    ax[2].set_ylabel("max | curl of power |")
    ax[2].set_title("only generative power\ncan source the holonomy")

    fig.suptitle("Stage I (Remark 2.1): a unique Helmholtz split separates dominating "
                 "from generative power", fontsize=13)
    fig.tight_layout()
    save(fig, "05_helmholtz_power.png")


def main():
    fig_continuity_source()
    fig_power_history()
    fig_vorticity_holonomy()
    fig_helmholtz_power()


if __name__ == "__main__":
    main()
