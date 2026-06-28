"""Part III -- a quantitative ethics case study on real classroom discourse.

Runs the model on the TalkMoves corpus (real K-12 mathematics lesson transcripts) and
walks the analysis step by step, for both senses of "ethics + education":

  edu1  the raw data            -- one real lesson as a turn timeline of talk moves
  edu2  the state vector        -- talk-move mix -> (a, d, g) for contrasting lessons
  edu3  transition operators    -- T_ts, T_st, the holonomy, and the power C (eq. 23, 26)
  edu4  ethics IN education      -- the (C, Theta) power-geometry plane across the corpus
  edu5  ethics education         -- teacher uptake = genuine vs forged classroom deliberation
  edu6  synthesis                -- how autonomy, generativity, and uptake move with grade

Requires the corpus in data_cache/talkmoves/ (see experiments/fetch_talkmoves.py).
Run:  PYTHONPATH=. python experiments/edu_casestudy.py
"""

from __future__ import annotations

import os
import numpy as np

from fluid_socio import education as edu
from fluid_socio.operators import holonomy_sign
from _common import get_plt, save

CORPUS = "data_cache/talkmoves"
MACRO_COLORS = ["#c9c9c9", "#d9a441", "#2f9e6f"]  # Passive, Controlling, Generative
STUDENT_LABELS = {1: "None", 2: "Relating", 3: "Asking", 4: "Claim", 5: "Reasoning"}


def _path(name):
    return os.path.join(CORPUS, name + ".xlsx")


def _student_move_counts(lesson):
    s = lesson.move[lesson.role == "S"]
    return {k: int(np.sum(s == k)) for k in range(1, 6)}


# --------------------------------------------------------------------------- #
# edu1  the raw data: one lesson as a turn timeline
# --------------------------------------------------------------------------- #
def fig_transcript(rows):
    # a medium-length lesson with a real back-and-forth
    cand = [r for r in rows if 90 <= r["n_utterances"] <= 240]
    cand.sort(key=lambda r: -r["g"])
    lesson = edu.load_lesson(_path(cand[5]["name"]))
    n = min(len(lesson.role), 110)
    print(f"edu1 transcript: '{lesson.name}' (grade {lesson.grade}), showing {n} utterances")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(figsize=(15, 3.2))
    for i in range(n):
        y = 1 if lesson.role[i] == "T" else 0
        ax.add_patch(plt.Rectangle((i, y - 0.4), 0.9, 0.8,
                     color=MACRO_COLORS[lesson.macro[i]]))
    ax.set_xlim(0, n); ax.set_ylim(-0.6, 1.6)
    ax.set_yticks([0, 1]); ax.set_yticklabels(["student", "teacher"])
    ax.set_xlabel("utterance (in order)")
    import matplotlib.patches as mp
    ax.legend(handles=[mp.Patch(color=MACRO_COLORS[k], label=lab)
                       for k, lab in enumerate(edu.MACRO)], ncol=3, loc="upper right")
    ax.set_title(f"Ethics in education, edu1 -- a real lesson as a turn sequence of talk "
                 f"moves\n'{lesson.name}' (grade {lesson.grade})", fontsize=11)
    fig.tight_layout()
    save(fig, "edu1_transcript.png")


# --------------------------------------------------------------------------- #
# edu2  the state vector (a, d, g) for two contrasting lessons
# --------------------------------------------------------------------------- #
def fig_state_vector(rows):
    rows_ok = [r for r in rows if r["n_student_moves"] >= 30]
    gen = max(rows_ok, key=lambda r: r["theta_long"])
    dom = min(rows_ok, key=lambda r: r["theta_long"])
    print(f"edu2 state vectors: generative='{gen['name']}' (Theta={gen['theta_long']:+.2f}), "
          f"dominative='{dom['name']}' (Theta={dom['theta_long']:+.2f})")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(2, 2, figsize=(13, 7))
    for col, (r, tag, color) in enumerate([(gen, "generative (Theta>0)", "seagreen"),
                                           (dom, "dominative (Theta<0)", "indianred")]):
        lesson = edu.load_lesson(_path(r["name"]))
        counts = _student_move_counts(lesson)
        tot = max(sum(counts.values()), 1)
        ax[0, col].bar([STUDENT_LABELS[k] for k in range(1, 6)],
                       [counts[k] / tot for k in range(1, 6)], color=color, alpha=0.8)
        ax[0, col].set_title(f"{tag}\n'{lesson.name[:38]}' (grade {lesson.grade})\n"
                             f"a={r['a']:.2f}  d={r['d']:.2f}  g={r['g']:.2f}", fontsize=10)
        ax[0, col].set_ylabel("share of student moves"); ax[0, col].set_ylim(0, 0.8)
        ax[0, col].tick_params(axis="x", rotation=30)

        traj = edu.state_trajectory(lesson, n_seg=4)
        xs = np.arange(1, 5)
        ax[1, col].plot(xs, [t["a"] for t in traj], "o-", color="darkgreen", label="autonomy a")
        ax[1, col].plot(xs, [t["d"] for t in traj], "s-", color="firebrick", label="dependence d")
        ax[1, col].plot(xs, [t["g"] for t in traj], "^-", color="steelblue", label="generative g")
        ax[1, col].set_xlabel("lesson quarter"); ax[1, col].set_ylim(0, 1)
        ax[1, col].set_title(f"trajectory  (Theta = d_a - d_d = {r['theta_long']:+.2f})",
                             fontsize=10)
        ax[1, col].grid(True, alpha=0.3)
    ax[1, 0].legend(fontsize=8)
    fig.suptitle("Part III, edu2 -- the relational state vector (a, d, g) read from the "
                 "talk-move mix (eq. 24)", fontsize=12)
    fig.tight_layout()
    save(fig, "edu2_state_vector.png")


# --------------------------------------------------------------------------- #
# edu3  transition operators, holonomy, and power
# --------------------------------------------------------------------------- #
def fig_operators(rows):
    r = max((x for x in rows if x["n_student_moves"] >= 40), key=lambda x: x["C"])
    lesson = edu.load_lesson(_path(r["name"]))
    T_ts, T_st = edu.transition_operators(lesson)
    H = T_ts @ T_st
    comm = T_ts @ T_st - T_st @ T_ts
    print(f"edu3 operators: '{lesson.name}'  C={r['C']:.2f}  theta_hol={r['theta_hol']:+.2f}")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(1, 4, figsize=(17, 4.2))
    short = ["P", "C", "G"]
    for a, M, title in [
        (ax[0], T_ts, "T_(t->s): P(student | teacher)"),
        (ax[1], T_st, "T_(s->t): P(teacher | student)"),
        (ax[2], H, "holonomy  H = T_ts T_st"),
        (ax[3], comm, f"commutator  (power C = {r['C']:.2f})"),
    ]:
        im = a.imshow(M, cmap="magma" if M is not comm else "RdBu_r",
                      vmin=(None if M is not comm else -np.max(np.abs(comm))),
                      vmax=(None if M is not comm else np.max(np.abs(comm))))
        a.set_xticks(range(3)); a.set_xticks(range(3)); a.set_yticks(range(3))
        a.set_xticklabels(short); a.set_yticklabels(short)
        a.set_title(title, fontsize=9)
        for i in range(3):
            for j in range(3):
                a.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center",
                       color="white" if (M is not comm and M[i, j] > 0.4) else "black",
                       fontsize=8)
        fig.colorbar(im, ax=a, fraction=0.046)
    fig.suptitle("Part III, edu3 -- transition operators on {Passive, Controlling, "
                 "Generative}; power = their non-commutativity (eqs. 23, 26)", fontsize=11)
    fig.tight_layout()
    save(fig, "edu3_transition_operators.png")


# --------------------------------------------------------------------------- #
# edu4  ethics IN education: the (C, Theta) power-geometry plane
# --------------------------------------------------------------------------- #
def fig_power_geometry(rows):
    C = np.array([r["C"] for r in rows])
    Th = np.array([r["theta_long"] for r in rows])
    g = np.array([r["g"] for r in rows])
    frac_pos = float(np.mean(Th > 0))
    print(f"edu4 power geometry: {len(rows)} real lessons; mean C={C.mean():.2f}, "
          f"Theta>0 in {frac_pos*100:.0f}%")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(figsize=(9, 6.5))
    sc = ax.scatter(C, Th, c=g, cmap="viridis", s=45, alpha=0.85, edgecolors="white",
                    linewidths=0.4)
    ax.axhline(0, color="black", lw=1)
    xlim = ax.get_xlim()
    ax.fill_between(xlim, 0, ax.get_ylim()[1], color="seagreen", alpha=0.05)
    ax.fill_between(xlim, ax.get_ylim()[0], 0, color="indianred", alpha=0.05)
    ax.text(xlim[1]*0.98, ax.get_ylim()[1]*0.9, "generative / power-to", ha="right",
            color="seagreen", weight="bold")
    ax.text(xlim[1]*0.98, ax.get_ylim()[0]*0.9, "dominative / power-over", ha="right",
            va="bottom", color="indianred", weight="bold")
    ax.set_xlim(xlim)
    ax.set_xlabel("power strength  C = ||T_ts T_st - T_st T_ts||   (eq. 26)")
    ax.set_ylabel("holonomy sign  Theta = d(autonomy) - d(dependence)   (eq. 25)")
    ax.set_title(f"Part III, edu4 (ethics IN education): {len(rows)} real lessons\n"
                 "almost all carry power (C>0); they split on the sign of the surplus")
    fig.colorbar(sc, ax=ax, label="generative output  g")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    save(fig, "edu4_power_geometry.png")


# --------------------------------------------------------------------------- #
# edu5  ethics education: teacher uptake = genuine vs forged deliberation
# --------------------------------------------------------------------------- #
def fig_genuine_forged(rows):
    up = np.array([r["uptake"] for r in rows if r["uptake"] == r["uptake"]])
    a = np.array([r["a"] for r in rows if r["uptake"] == r["uptake"]])
    thr = 0.5
    frac_genuine = float(np.mean(up >= thr))
    corr = float(np.corrcoef(up, a)[0, 1])
    print(f"edu5 genuine/forged: mean uptake={up.mean():.2f}; "
          f"{frac_genuine*100:.0f}% of lessons >= {thr} (genuine); corr(uptake, autonomy)={corr:+.2f}")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(1, 2, figsize=(14, 5))
    ax[0].hist(up, bins=20, color="slategray", edgecolor="white")
    ax[0].axvline(thr, color="black", ls="--")
    ax[0].axvspan(0, thr, color="indianred", alpha=0.08)
    ax[0].axvspan(thr, 1, color="seagreen", alpha=0.08)
    ax[0].text(0.02, ax[0].get_ylim()[1]*0.9, "FORGED-leaning\n(student ideas\nrarely taken up)",
               color="firebrick", fontsize=9)
    ax[0].text(0.62, ax[0].get_ylim()[1]*0.9, "GENUINE\n(value returned\nto the student)",
               color="seagreen", fontsize=9)
    ax[0].set_xlabel("teacher uptake of student claims / reasoning")
    ax[0].set_ylabel("number of lessons")
    ax[0].set_title(f"uptake across {len(up)} real lessons\n(mean {up.mean():.2f}; only "
                    f"{frac_genuine*100:.0f}% are genuine-leaning)")

    ax[1].scatter(a, up, s=40, color="teal", alpha=0.7, edgecolors="white", linewidths=0.4)
    z = np.polyfit(a, up, 1)
    xs = np.linspace(a.min(), a.max(), 20)
    ax[1].plot(xs, np.polyval(z, xs), color="crimson", lw=2)
    ax[1].set_xlabel("student autonomy  a")
    ax[1].set_ylabel("teacher uptake (genuine deliberation)")
    ax[1].set_title(f"does the relation return value to its authors?\ncorr(uptake, autonomy) "
                    f"= {corr:+.2f}")
    ax[1].grid(True, alpha=0.3)

    fig.suptitle("Part III, edu5 (ethics education): genuine vs forged classroom "
                 "deliberation = whether student contributions circulate back (paper 2)",
                 fontsize=11)
    fig.tight_layout()
    save(fig, "edu5_genuine_forged.png")


# --------------------------------------------------------------------------- #
# edu6  synthesis: how the relational quantities move with grade level
# --------------------------------------------------------------------------- #
def fig_synthesis(rows):
    by_grade = {}
    for r in rows:
        if r["grade"]:
            by_grade.setdefault(r["grade"], []).append(r)
    grades = sorted(by_grade)

    def series(metric):
        m = [np.nanmean([x[metric] for x in by_grade[gr]]) for gr in grades]
        return np.array(m)

    print(f"edu6 synthesis: grades {grades}; "
          f"corpus means a={np.mean([r['a'] for r in rows]):.2f}, "
          f"g={np.mean([r['g'] for r in rows]):.2f}, "
          f"uptake={np.nanmean([r['uptake'] for r in rows]):.2f}, "
          f"C={np.mean([r['C'] for r in rows]):.2f}")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(1, 2, figsize=(14, 5))
    for metric, color, lab in [("a", "darkgreen", "autonomy a"),
                               ("g", "steelblue", "generative output g"),
                               ("uptake", "seagreen", "uptake (genuine deliberation)"),
                               ("d", "firebrick", "dependence d")]:
        ax[0].plot(grades, series(metric), "o-", color=color, label=lab)
    ax[0].set_xlabel("grade level"); ax[0].set_ylabel("corpus mean")
    ax[0].set_title("how the relational quantities move with grade")
    ax[0].legend(fontsize=8); ax[0].grid(True, alpha=0.3); ax[0].set_ylim(0, 1)

    # the two headline distributions
    Th = np.array([r["theta_long"] for r in rows])
    up = np.array([r["uptake"] for r in rows if r["uptake"] == r["uptake"]])
    ax[1].hist(Th, bins=22, color="mediumpurple", alpha=0.7, label="Theta (good/bad sign)")
    ax[1].axvline(0, color="black", lw=1)
    ax[1].set_xlabel("Theta  (left = dominative, right = generative)")
    ax[1].set_ylabel("lessons")
    ax[1].set_title(f"distribution of the good/bad sign\n(Theta>0 in "
                    f"{np.mean(Th>0)*100:.0f}% of {len(rows)} lessons)")
    ax[1].legend(fontsize=8)

    fig.suptitle("Part III, edu6 -- synthesis across the corpus: two real findings about "
                 "the ethics of classroom relations", fontsize=11)
    fig.tight_layout()
    save(fig, "edu6_synthesis.png")


def main():
    if not os.path.isdir(CORPUS) or len([f for f in os.listdir(CORPUS)
                                         if f.endswith(".xlsx")]) < 10:
        print("TalkMoves corpus not found in data_cache/talkmoves/.")
        print("Fetch it first:  python experiments/fetch_talkmoves.py")
        return
    print("Loading and analyzing the TalkMoves corpus ...")
    rows = edu.analyze_corpus(CORPUS)
    print(f"  {len(rows)} lessons analyzed.\n")
    fig_transcript(rows)
    fig_state_vector(rows)
    fig_operators(rows)
    fig_power_geometry(rows)
    fig_genuine_forged(rows)
    fig_synthesis(rows)


if __name__ == "__main__":
    main()
