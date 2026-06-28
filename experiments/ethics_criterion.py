"""Ethics, part 1 -- the good/bad criterion and the geometry of power.

  e1  the good/bad criterion   -- the SIGN of a cycle's holonomy: generative (good),
                                  appropriative (neutral), dominative (bad)
  e2  power-to vs power-over    -- the SAME power, two geometries: one works toward its own
                                  dissolution, the other fixes the other in dependence
  e3  the trilemma              -- power and generativity co-originate (Prop. 4.1): you
                                  cannot have a generative relation without power

Run:  PYTHONPATH=. python experiments/ethics_criterion.py
"""

from __future__ import annotations

import numpy as np

from fluid_socio.operators import holonomy_sign
from fluid_socio.nonabelian import su2, commutator_norm
from _common import get_plt, save


# --------------------------------------------------------------------------- #
# e1  the good/bad criterion: the sign of a cycle's holonomy
# --------------------------------------------------------------------------- #
def fig_criterion():
    t = np.linspace(0, 1, 50)
    # Three archetypal relations as (autonomy, dependence) trajectories.
    relations = {
        "generative\n(good cycle)": dict(
            a=(0.30, 0.80), d=(0.60, 0.20), color="seagreen"),
        "appropriative\n(neutral: transfer only)": dict(
            a=(0.45, 0.55), d=(0.45, 0.55), color="slategray"),
        "dominative\n(bad cycle)": dict(
            a=(0.50, 0.28), d=(0.40, 0.72), color="indianred"),
    }
    print("e1 good/bad criterion = sign of the holonomy:")
    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
    for axi, (name, r) in zip(ax, relations.items()):
        a = r["a"][0] + (r["a"][1] - r["a"][0]) * t
        d = r["d"][0] + (r["d"][1] - r["d"][0]) * t
        theta = (a[-1] - a[0]) - (d[-1] - d[0])
        sign = holonomy_sign(theta)
        verdict = {1: "Theta > 0  GOOD", 0: "Theta ~ 0  neutral",
                   -1: "Theta < 0  BAD"}[sign]
        print(f"   {name.splitlines()[0]:14s}  Theta = {theta:+.2f}  ({verdict})")
        axi.plot(t, a, color="darkgreen", lw=2.2, label="autonomy a(t)")
        axi.plot(t, d, color="firebrick", lw=2.2, label="dependence d(t)")
        axi.fill_between(t, a, d, color=r["color"], alpha=0.12)
        axi.set_title(f"{name}\nTheta = {theta:+.2f}   [{verdict}]", fontsize=10,
                      color=r["color"])
        axi.set_xlabel("one relational cycle"); axi.set_ylim(0, 1)
        axi.grid(True, alpha=0.3)
    ax[0].set_ylabel("state"); ax[0].legend(loc="center left", fontsize=8)
    fig.suptitle("Ethics e1: the good/bad criterion is the SIGN of the holonomy "
                 "(Theta = d(autonomy) - d(dependence))", fontsize=12)
    fig.tight_layout()
    save(fig, "e1_good_bad_criterion.png")


# --------------------------------------------------------------------------- #
# e2  power-to vs power-over: the same power, two geometries
# --------------------------------------------------------------------------- #
def fig_power_geometry():
    t = np.linspace(0, 1, 100)
    # Equal initial power (asymmetry), opposite surplus sign.
    # power-to: asymmetry decays toward 0 -- the upstream serves its own dissolution.
    e_to = 0.8 * (1 - 0.85 * t)
    # power-over: asymmetry persists/grows -- the other is fixed in dependence.
    e_over = 0.8 * (1 + 0.4 * t)
    theta_to, theta_over = +0.9, -0.6
    print(f"e2 power-to vs power-over: equal initial power 0.80; "
          f"power-to asymmetry {e_to[0]:.2f}->{e_to[-1]:.2f} (Theta={theta_to:+.1f}); "
          f"power-over {e_over[0]:.2f}->{e_over[-1]:.2f} (Theta={theta_over:+.1f})")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].plot(t, e_to, color="seagreen", lw=2.5, label="power-to (generative)")
    ax[0].plot(t, e_over, color="indianred", lw=2.5, label="power-over (dominative)")
    ax[0].set_xlabel("time in the relation"); ax[0].set_ylabel("power edge (asymmetry)")
    ax[0].set_title("the SAME power, two trajectories\n"
                    "power-to works toward its own dissolution;\n"
                    "power-over fixes the other in dependence")
    ax[0].legend(); ax[0].grid(True, alpha=0.3); ax[0].set_ylim(0, 1.3)

    # The (C, Theta) reading: same |power|, opposite surplus sign.
    ax[1].axhline(0, color="black", lw=1)
    ax[1].scatter([0.8], [theta_to], s=160, color="seagreen", zorder=3,
                  label="power-to")
    ax[1].scatter([0.8], [theta_over], s=160, color="indianred", zorder=3,
                  label="power-over")
    ax[1].annotate("returns surplus\n(serves the other's capacity)", (0.8, theta_to),
                   xytext=(0.45, 0.6), color="seagreen", fontsize=9,
                   arrowprops=dict(arrowstyle="->", color="seagreen"))
    ax[1].annotate("retains surplus\n(fixes dependence)", (0.8, theta_over),
                   xytext=(0.4, -0.85), color="indianred", fontsize=9,
                   arrowprops=dict(arrowstyle="->", color="indianred"))
    ax[1].fill_between([0, 1.1], 0, 1.1, color="seagreen", alpha=0.06)
    ax[1].fill_between([0, 1.1], -1.1, 0, color="indianred", alpha=0.06)
    ax[1].set_xlim(0, 1.1); ax[1].set_ylim(-1.1, 1.1)
    ax[1].set_xlabel("power strength  C  (non-commutativity)")
    ax[1].set_ylabel("holonomy sign  Theta  (surplus returned vs retained)")
    ax[1].set_title("justice is the geometry, not the magnitude:\n"
                    "same C, opposite sign of the surplus")
    ax[1].legend(loc="center right")

    fig.suptitle("Ethics e2: power-to and power-over are one non-commutativity in two "
                 "geometries (sec. 4.4)", fontsize=12)
    fig.tight_layout()
    save(fig, "e2_power_to_over.png")


# --------------------------------------------------------------------------- #
# e3  the trilemma: power and generativity co-originate (Prop. 4.1)
# --------------------------------------------------------------------------- #
def fig_trilemma():
    # Interpolate the residual symmetry from abelian (lambda=0) to non-abelian (lambda=1)
    # by tilting one holonomy's axis away from the other. Both power and generativity are
    # functions of the SAME non-abelianness, so they rise together.
    lam = np.linspace(0, 1, 60)
    U1 = su2((0, 0, 1), 1.4)
    power, gen = [], []
    for L in lam:
        ax_tilt = (np.sin(L * np.pi / 2), 0, np.cos(L * np.pi / 2))
        U2 = su2(ax_tilt, 1.4)
        power.append(commutator_norm(U1, U2))
        # generativity proxy: the mixing / multi-channel opening = sin of the relative
        # axis angle (0 = single channel/abelian, 1 = maximally multi-channel).
        gen.append(np.sin(L * np.pi / 2))
    power = np.array(power) / max(power)
    gen = np.array(gen)
    print(f"e3 trilemma: at lambda=0 power={power[0]:.2f} gen={gen[0]:.2f} (abelian: "
          f"subjects but barren); at lambda=1 power={power[-1]:.2f} gen={gen[-1]:.2f} "
          "(non-abelian: generativity AND power) -- they co-originate")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(lam, power, color="crimson", lw=4.0, ls="--", alpha=0.9,
            label="power (non-commutativity)")
    ax.plot(lam, gen, color="seagreen", lw=2.2, label="generativity (multi-channel fusion)")
    ax.fill_between(lam, 0, np.minimum(power, gen), color="goldenrod", alpha=0.15)
    ax.set_xlabel("degree of symmetry breaking  ->  non-abelian residue  (lambda)")
    ax.set_ylabel("normalized magnitude")
    ax.set_title("Ethics e3: the trilemma -- power and generativity share one root\n"
                 "(Prop. 4.1: you cannot pull up the one without the other; the two curves "
                 "coincide)", fontsize=11)
    # annotate the three regimes (kept inside the axes)
    ax.axvline(0, color="gray", ls=":", alpha=0.6)
    ax.text(0.03, 0.96, "lambda=0: full / abelian residue\nsubjects but no power AND no "
            "generativity\n(the barren equality)", fontsize=8, va="top")
    ax.text(0.97, 0.55, "lambda=1: non-abelian\ngenerativity requires power\n"
            "(the only generative world)", fontsize=8, ha="right", color="crimson")
    ax.text(0.5, 0.10, "the dream of generative-yet-powerless\nlives in this gap -- which is empty",
            fontsize=9, ha="center", color="saddlebrown", style="italic")
    ax.legend(loc="lower right"); ax.grid(True, alpha=0.3); ax.set_ylim(0, 1.12)
    fig.tight_layout()
    save(fig, "e3_trilemma.png")


def main():
    fig_criterion()
    fig_power_geometry()
    fig_trilemma()


if __name__ == "__main__":
    main()
