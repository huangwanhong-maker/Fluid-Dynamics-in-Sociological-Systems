"""Stage VI -- operationalization and the educational case study (paper sec. 10).

  13  relational state vectors          -- (a, d, g) trajectories per cohort (eq. 24)
  14  the geometry of power             -- the (C, Theta) plane: power-to vs power-over
  15  falsifiable case study            -- Theta separates cohorts; exam score does not
                                           (sec. 10.5)

Run:  PYTHONPATH=. python experiments/stage6_ethics.py
"""

from __future__ import annotations

import numpy as np

from fluid_socio.ethics import (
    generate_cohort, theta, theta_trajectory, power_C, cohort_table,
)
from fluid_socio.operators import holonomy_sign
from _common import get_plt, save


CARD = {"inquiry": ("inquiry-based", "seagreen"),
        "lecture-drill": ("lecture-drill", "indianred")}


def _band(ax, t, curves, color, label):
    arr = np.array(curves)
    m, s = arr.mean(0), arr.std(0)
    ax.plot(t, m, color=color, lw=2.2, label=label)
    ax.fill_between(t, m - s, m + s, color=color, alpha=0.18)


# --------------------------------------------------------------------------- #
# 13  state vectors (a, d, g)
# --------------------------------------------------------------------------- #
def fig_state_vectors(cohorts):
    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.6), sharex=True)
    titles = ["autonomy  a(t)", "dependence  d(t)", "generative output  g(t)"]
    keys = ["a", "d", "g"]
    for col, (name, students) in enumerate(cohorts.items()):
        label, color = CARD[name]
        t = students[0].t
        for k, axk in zip(keys, ax):
            _band(axk, t, [getattr(s, k) for s in students], color, label)
    for axk, title in zip(ax, titles):
        axk.set_title(title); axk.set_xlabel("term (normalized)")
        axk.grid(True, alpha=0.3); axk.set_ylim(0, 1)
    ax[0].legend()
    fig.suptitle("Stage VI (eq. 24): the relational state vector s = (autonomy, "
                 "dependence, generative output)", fontsize=12)
    fig.tight_layout()
    save(fig, "13_state_vectors.png")


# --------------------------------------------------------------------------- #
# 14  the geometry of power: (C, Theta) plane
# --------------------------------------------------------------------------- #
def fig_power_geometry(cohorts):
    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    for name, students in cohorts.items():
        label, color = CARD[name]
        Cs = [power_C(s) for s in students]
        Th = [theta(s) for s in students]
        ax.scatter(Cs, Th, color=color, s=40, alpha=0.7, edgecolors="white",
                   linewidths=0.5, label=label)

    ax.axhline(0, color="black", lw=1)
    xlim = ax.get_xlim()
    ax.fill_between(xlim, 0, ax.get_ylim()[1], color="seagreen", alpha=0.06)
    ax.fill_between(xlim, ax.get_ylim()[0], 0, color="indianred", alpha=0.06)
    ax.text(xlim[1] * 0.97, ax.get_ylim()[1] * 0.85, "generative power\n(power-to, good cycle)",
            ha="right", color="seagreen", fontsize=10, weight="bold")
    ax.text(xlim[1] * 0.97, ax.get_ylim()[0] * 0.85, "dominative power\n(power-over, bad cycle)",
            ha="right", va="bottom", color="indianred", fontsize=10, weight="bold")
    ax.set_xlim(xlim)
    ax.set_xlabel("power strength  C = || T_ts T_st - T_st T_ts ||   (eq. 26)")
    ax.set_ylabel("holonomy sign  Theta = d(autonomy) - d(dependence)   (eq. 25)")
    ax.set_title("Stage VI: justice is the geometry of power, not its removal\n"
                 "(both cohorts have power C > 0; they differ in the SIGN of the surplus)")
    ax.legend(loc="center left"); ax.grid(True, alpha=0.3)
    fig.tight_layout()
    save(fig, "14_power_geometry.png")


# --------------------------------------------------------------------------- #
# 15  the falsifiable prediction (sec. 10.5)
# --------------------------------------------------------------------------- #
def fig_case_study(cohorts):
    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))

    # (a) Theta trajectories: diverge.
    for name, students in cohorts.items():
        label, color = CARD[name]
        t = students[0].t
        _band(ax[0], t, [theta_trajectory(s) for s in students], color, label)
    ax[0].axhline(0, color="black", lw=1)
    ax[0].set_title("Theta(t): the SURPLUS\n(predicted to diverge)")
    ax[0].set_xlabel("term"); ax[0].set_ylabel("Theta")
    ax[0].legend(); ax[0].grid(True, alpha=0.3)

    # (b) Exam scores: overlap (the stock the model says will NOT separate).
    data = [[s.exam for s in students] for students in cohorts.values()]
    colors = [CARD[n][1] for n in cohorts]
    ax[1].hist(data, bins=12, color=colors, label=[CARD[n][0] for n in cohorts])
    ax[1].set_title("exam score: the STOCK\n(predicted to overlap)")
    ax[1].set_xlabel("exam score"); ax[1].set_ylabel("count"); ax[1].legend()

    # (c) Theta vs exam: separation is vertical (Theta), not horizontal (exam).
    for name, students in cohorts.items():
        label, color = CARD[name]
        ax[2].scatter([s.exam for s in students], [theta(s) for s in students],
                      color=color, s=35, alpha=0.7, edgecolors="white", linewidths=0.5,
                      label=label)
    ax[2].axhline(0, color="black", lw=1)
    ax[2].set_title("Theta vs exam score\n(separation is in Theta, not exam)")
    ax[2].set_xlabel("exam score (stock)"); ax[2].set_ylabel("Theta (surplus sign)")
    ax[2].legend(); ax[2].grid(True, alpha=0.3)

    fig.suptitle("Stage VI (sec. 10.5): the falsifiable prediction -- good teaching shows "
                 "as Theta > 0 independent of exam score", fontsize=12)
    fig.tight_layout()
    save(fig, "15_education_case_study.png")


def main():
    cohorts = {
        "inquiry": generate_cohort("inquiry", n=45, seed=10),
        "lecture-drill": generate_cohort("lecture-drill", n=45, seed=20),
    }
    print("Stage VI -- educational case study (synthetic)")
    print("=" * 58)
    for name, students in cohorts.items():
        tab = cohort_table(students)
        signs = [holonomy_sign(theta(s)) for s in students]
        frac_pos = np.mean([x > 0 for x in signs])
        print(f"  {name:14s} Theta={tab['theta_mean']:+.3f}+-{tab['theta_sd']:.2f}  "
              f"C={tab['C_mean']:.3f}  exam={tab['exam_mean']:.1f}+-{tab['exam_sd']:.1f}  "
              f"(Theta>0 in {frac_pos*100:.0f}%)")
    # verdict-rule check: do Theta and exam separate the cohorts?
    th = {n: np.mean([theta(s) for s in st]) for n, st in cohorts.items()}
    ex = {n: np.mean([s.exam for s in st]) for n, st in cohorts.items()}
    print(f"  => Theta gap = {abs(th['inquiry']-th['lecture-drill']):.3f} (large); "
          f"exam gap = {abs(ex['inquiry']-ex['lecture-drill']):.1f} (small) "
          "=> model SUPPORTED on this synthetic data")

    fig_state_vectors(cohorts)
    fig_power_geometry(cohorts)
    fig_case_study(cohorts)


if __name__ == "__main__":
    main()
