"""Ethics e7-e8 -- two hard cases (paper 2, sec. 6).

Both are unintelligible on the equilibrium picture and tractable once authorship is
relational and the relevant quantity is the holonomy.

  e7  illness                  -- authorship was never solitary; the care relation is the
                                  site across which it was always distributed. Illness makes
                                  visible what was already true.
  e8  the intimate trolley     -- aggregation breaks down: the beloved is non-substitutable,
                                  not a countable unit on the same axis as strangers.

Run:  PYTHONPATH=. python experiments/ethics_cases.py
"""

from __future__ import annotations

import numpy as np

from _common import get_plt, save


# --------------------------------------------------------------------------- #
# e7  illness and the distribution of authorship
# --------------------------------------------------------------------------- #
def fig_illness():
    severity = np.linspace(0, 1, 100)
    solitary = 1 - severity                       # solitary authorship capacity declines
    relational_genuine = 1 - 0.12 * severity      # distributed: the patient stays co-author
    relational_forged = (1 - severity) * 0.75     # form kept, value extracted from patient
    print("e7 illness: solitary authorship "
          f"{solitary[0]:.2f}->{solitary[-1]:.2f} (collapses -> external legislator); "
          f"relational genuine {relational_genuine[0]:.2f}->{relational_genuine[-1]:.2f} "
          "(patient remains an author)")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(1, 2, figsize=(14, 5.2), sharey=True)

    # Solitary picture: capacity declines, an external legislator fills the gap.
    ax[0].plot(severity, solitary, color="navy", lw=2.5, label="patient's solitary authorship")
    ax[0].fill_between(severity, solitary, 1.0, color="indianred", alpha=0.18)
    ax[0].text(0.55, 0.78, "gap filled by an\nEXTERNAL legislator\n(carer / clinician /"
               " institution\nre-enters as author)", color="firebrick", fontsize=9)
    ax[0].set_title("the solitary picture\nillness reads as a failure of authorship")
    ax[0].set_xlabel("illness severity"); ax[0].set_ylabel("authorship")
    ax[0].legend(loc="lower left"); ax[0].grid(True, alpha=0.3); ax[0].set_ylim(0, 1.05)

    # Relational picture: authorship is distributed; the holonomy sign distinguishes
    # genuine care from forged.
    ax[1].plot(severity, relational_genuine, color="seagreen", lw=2.5,
               label="genuine care (value returns to patient)")
    ax[1].plot(severity, relational_forged, color="indianred", lw=2.5,
               label="forged care (form kept, patient extracted)")
    ax[1].text(0.1, 0.5, "authorship was ALWAYS\ndistributed across the\ncare relation;\n"
               "illness only makes it visible", color="seagreen", fontsize=9)
    ax[1].set_title("the relational picture\nauthorship is a property of the relation")
    ax[1].set_xlabel("illness severity")
    ax[1].legend(loc="upper right"); ax[1].grid(True, alpha=0.3)

    fig.suptitle("Ethics e7: illness -- the care relation is the site across which "
                 "authorship was always distributed (the holonomy sign judges the care)",
                 fontsize=11)
    fig.tight_layout()
    save(fig, "e7_illness_authorship.png")


# --------------------------------------------------------------------------- #
# e8  the intimate trolley: the breakdown of aggregation
# --------------------------------------------------------------------------- #
def fig_trolley():
    N = np.arange(1, 9)
    print("e8 intimate trolley: utilitarian value is the count N (on the aggregation "
          "axis); the beloved's value is a holonomy OFF that axis -- the comparison is "
          "ill-posed.")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(1, 2, figsize=(14, 5.4))

    # Left: the standard trolley -- everyone is a countable, interchangeable unit.
    ax[0].scatter(N, np.zeros_like(N), s=120, color="slategray", zorder=3)
    ax[0].plot(N, np.zeros_like(N), color="slategray", lw=1, alpha=0.5)
    ax[0].scatter([0], [0], s=160, color="slategray", marker="s", zorder=3)
    ax[0].text(4, 0.12, "strangers: interchangeable units on one axis\n"
               "value = the count N  ->  'divert: 5 > 1'", ha="center", fontsize=9)
    ax[0].set_xlim(-1, 9); ax[0].set_ylim(-0.6, 1.2)
    ax[0].set_xlabel("number of persons N  (the aggregation axis)")
    ax[0].set_yticks([])
    ax[0].set_title("the standard trolley:\naggregation -- a question about sums")

    # Right: inside intimacy -- the beloved is off the aggregation axis.
    ax[1].scatter(N, np.zeros_like(N), s=90, color="slategray", zorder=3, alpha=0.8)
    ax[1].annotate("", xy=(8.2, 0), xytext=(1, 0),
                   arrowprops=dict(arrowstyle="->", color="slategray", lw=1.5))
    ax[1].text(4.5, -0.18, "aggregation axis (count N)", ha="center", color="slategray",
               fontsize=9)
    ax[1].scatter([2.0], [1.0], s=260, color="crimson", marker="*", zorder=4)
    ax[1].text(2.3, 1.0, "the beloved:\nnon-substitutable,\nvalue = a holonomy\n"
               "NOT on the N-axis", color="crimson", fontsize=9, va="center")
    ax[1].annotate("no neutral switch-operator:\nthe relational subject is ON the track",
                   xy=(2.0, 0.5), xytext=(4.2, 0.62), color="crimson", fontsize=9,
                   arrowprops=dict(arrowstyle="->", color="crimson"))
    ax[1].set_xlim(-1, 9); ax[1].set_ylim(-0.6, 1.3)
    ax[1].set_xlabel("number of persons N  (the aggregation axis)")
    ax[1].set_ylabel("relational value (holonomy)")
    ax[1].set_title("the intimate trolley:\naggregation breaks down -- a different axis")

    fig.suptitle("Ethics e8: inside an intimacy the question is not 'which sum is larger?' "
                 "but whether the judgement returns value to the relation or extracts it",
                 fontsize=11)
    fig.tight_layout()
    save(fig, "e8_intimate_trolley.png")


def main():
    fig_illness()
    fig_trolley()


if __name__ == "__main__":
    main()
