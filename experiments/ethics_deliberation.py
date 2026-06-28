"""Ethics e5-e6 -- deliberation as dynamics (the *Authorship Without Equilibrium* case).

  e5  the three attractors      -- fixed point (reflective equilibrium) vs limit cycle
                                  (bare repetition) vs holonomic spiral (authorship that
                                  carries value forward)
  e6  genuine vs forged          -- the sign of the holonomy on the deliberative loop:
                                  value returned to participants vs net-extracted (fuel)

Run:  PYTHONPATH=. python experiments/ethics_deliberation.py
"""

from __future__ import annotations

import numpy as np

from fluid_socio.deliberation import (
    integrate, fixed_point_deriv, limit_cycle_deriv, spiral_deriv,
    value_staircase, deliberation_holonomy,
)
from _common import get_plt, save


# --------------------------------------------------------------------------- #
# e5  the three candidate attractors
# --------------------------------------------------------------------------- #
def fig_attractors():
    dt, steps = 0.004, 750
    fixed = integrate(fixed_point_deriv(), (1.2, 0.0, 0.0), dt, steps)
    cycle = integrate(limit_cycle_deriv(), (0.25, 0.0, 0.0), dt, steps)
    spiral = integrate(spiral_deriv(holonomy_rate=0.45), (1.0, 0.0, 0.0), dt, steps)
    print("e5 attractors: fixed-point value gain "
          f"{fixed[-1,2]-fixed[0,2]:+.2f}; limit-cycle {cycle[-1,2]-cycle[0,2]:+.2f}; "
          f"spiral {spiral[-1,2]-spiral[0,2]:+.2f}")

    plt = get_plt()
    if plt is None:
        return
    fig = plt.figure(figsize=(15, 5.2))
    panels = [
        (fixed, "FIXED POINT\n(reflective equilibrium:\nthe questions stop -> authorship ends)",
         "indianred"),
        (cycle, "LIMIT CYCLE\n(bare repetition:\nreturns exactly, nothing gained)", "goldenrod"),
        (spiral, "HOLONOMIC SPIRAL\n(configuration returns,\nvalue carried forward)", "seagreen"),
    ]
    for i, (traj, title, color) in enumerate(panels):
        ax = fig.add_subplot(1, 3, i + 1, projection="3d")
        ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], color=color, lw=1.8)
        ax.scatter(*traj[0], color="black", s=30)
        ax.scatter(*traj[-1], color=color, s=60)
        ax.set_xlabel("judgement config x"); ax.set_ylabel("config y")
        ax.set_zlabel("accumulated value")
        ax.set_zlim(-0.1, 1.6)
        ax.set_title(title, fontsize=9)
    fig.suptitle("Ethics e5: only the holonomic spiral honours both return (the questions "
                 "recur) and gain (value accumulates) -- paper 2, sec. 3", fontsize=12)
    fig.tight_layout()
    save(fig, "e5_attractors.png")


# --------------------------------------------------------------------------- #
# e6  genuine vs forged deliberation
# --------------------------------------------------------------------------- #
def fig_genuine_forged():
    t_g, v_g, ang = value_staircase(+0.30, n_circuits=6)
    t_f, v_f, _ = value_staircase(-0.18, n_circuits=6)
    h_g = deliberation_holonomy(v_g)
    h_f = deliberation_holonomy(v_f)
    print(f"e6 genuine vs forged: holonomy per circuit genuine = {h_g:+.2f} "
          f"(value returned), forged = {h_f:+.2f} (value extracted -> fuel)")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(1, 2, figsize=(14, 5))

    # The base configuration returns identically for both (same recurring questions).
    ax[0].plot(t_g, np.cos(ang), color="slategray", lw=1.5)
    ax[0].set_xlabel("deliberative circuits"); ax[0].set_ylabel("judgement configuration")
    ax[0].set_title("the base returns: the same questions recur\n(identical for genuine and "
                    "forged)")
    ax[0].grid(True, alpha=0.3)

    # The value diverges: genuine accumulates, forged is extracted.
    ax[1].plot(t_g, v_g, color="seagreen", lw=2.4, label=f"genuine (holonomy {h_g:+.2f}/circuit)")
    ax[1].plot(t_f, v_f, color="indianred", lw=2.4, label=f"forged (holonomy {h_f:+.2f}/circuit)")
    ax[1].axhline(0, color="black", lw=1)
    ax[1].fill_between(t_f, v_f, 0, color="indianred", alpha=0.12)
    ax[1].annotate("value returned to\nthe participants", (t_g[-1], v_g[-1]),
                   xytext=(2.2, 1.4), color="seagreen", fontsize=9,
                   arrowprops=dict(arrowstyle="->", color="seagreen"))
    ax[1].annotate("value net-extracted:\nthe affected used as fuel", (t_f[-1], v_f[-1]),
                   xytext=(1.2, -1.05), color="indianred", fontsize=9,
                   arrowprops=dict(arrowstyle="->", color="indianred"))
    ax[1].set_xlabel("deliberative circuits"); ax[1].set_ylabel("accumulated value (holonomy)")
    ax[1].set_title("the value does NOT return the same:\ngenuine vs forged = the SIGN of "
                    "the holonomy")
    ax[1].legend(loc="upper left"); ax[1].grid(True, alpha=0.3)

    fig.suptitle("Ethics e6: genuine deliberation returns value to its authors (positive "
                 "holonomy); forged keeps the form while extracting it (paper 2, Claim 5.1)",
                 fontsize=11)
    fig.tight_layout()
    save(fig, "e6_genuine_forged.png")


def main():
    fig_attractors()
    fig_genuine_forged()


if __name__ == "__main__":
    main()
