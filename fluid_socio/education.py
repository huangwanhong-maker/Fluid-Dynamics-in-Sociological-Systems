"""Part III pipeline -- quantitative ethics analysis of real classroom discourse.

Ingests the TalkMoves corpus (K-12 mathematics lesson transcripts annotated for teacher
and student discursive moves; Suresh et al., LREC 2022, CC BY-NC-SA 4.0) and computes the
model's scale-invariant quantities from real interaction data.

The bridge from §10 to data:

- The relational state vector s = (a, d, g) (eq. 24) is read from the talk-move mix:
    a (autonomy)           = share of student moves that initiate / connect (claim, relate)
    g (generative output)  = share that reason / explain (claim, providing reasoning)
    d (dependence)         = the teacher's share of the floor (teacher utterances / all)

- The transition operators T_{t->s}, T_{s->t} (eq. 23) are estimated from the turn
  sequence on a common 3-macro-state space {Passive, Controlling, Generative}, so the
  holonomy H = T_ts T_st and the power C = ||T_ts T_st - T_st T_ts|| (eq. 26) are defined.

- Genuine vs forged deliberation (paper 2, Claim 5.1) is the teacher's UPTAKE of student
  contributions: after a student makes a claim or gives reasoning, does the teacher take it
  up (revoice / restate / relate / mark) -- value returned to the student, the student as
  co-author -- or move on (value extracted)?

Only sign / order / non-commutativity are reported, never an absolute magnitude (§4.5).
"""

from __future__ import annotations

import glob
import os
import re
import warnings
from dataclasses import dataclass

import numpy as np

warnings.filterwarnings("ignore")  # openpyxl style chatter


# Canonical taxonomies, keyed by the leading integer of each tag (robust to casing/wording).
TEACHER_MOVES = {1: "None", 2: "Keeping Everyone Together", 3: "Getting Students to Relate",
                 4: "Restating", 5: "Revoicing", 6: "Marking", 7: "Context",
                 8: "Press for Accuracy", 9: "Press for Reasoning"}
STUDENT_MOVES = {1: "None", 2: "Relating to Another Student", 3: "Asking for More Information",
                 4: "Making a Claim", 5: "Providing Reasoning"}

# Macro-state of the relational discourse: P(assive), C(ontrolling/eliciting), G(enerative).
MACRO = ["Passive", "Controlling", "Generative"]
TEACHER_MACRO = {1: 0, 7: 0,                 # None, Context -> Passive
                 2: 1, 8: 1, 4: 1,           # Keeping-together, Press-accuracy, Restating -> Controlling
                 3: 2, 5: 2, 9: 2, 6: 2}     # Relate, Revoice, Press-reasoning, Mark -> Generative
STUDENT_MACRO = {1: 0,                       # None -> Passive
                 3: 1,                       # Asking-for-info -> Controlling (needs scaffolding)
                 2: 2, 4: 2, 5: 2}           # Relate, Claim, Reasoning -> Generative

# Student moves counted toward each component of the state vector.
_AUTONOMY = {2, 4}        # relating to another, making a claim
_GENERATIVE = {4, 5}      # making a claim, providing reasoning
# Teacher moves that take up / build on a student contribution (uptake = value returned).
_UPTAKE = {3, 4, 5, 6}    # getting-to-relate, restating, revoicing, marking


def _tag_num(value) -> int | None:
    """The leading integer of a talk-move tag string (e.g. '5 - Revoicing' -> 5)."""
    if value is None:
        return None
    m = re.match(r"\s*(\d+)", str(value))
    return int(m.group(1)) if m else None


@dataclass
class Lesson:
    name: str
    grade: int | None
    role: np.ndarray        # 'T' or 'S' per utterance, in order
    move: np.ndarray        # canonical move number (or 0 if none) per utterance
    macro: np.ndarray       # macro-state index 0/1/2 per utterance
    words: np.ndarray = None  # word count per utterance (a continuous magnitude feature)


def grade_from_name(name: str) -> int | None:
    m = re.search(r"[Gg]rade\s*(\d+)", name) or re.search(r"(\d+)\s*th\s*grade", name.lower())
    return int(m.group(1)) if m else None


def load_lesson(path: str) -> Lesson:
    """Read one transcript .xlsx into an ordered sequence of (role, move, macro)."""
    import pandas as pd
    df = pd.read_excel(path)
    roles, moves, macros, words = [], [], [], []
    for _, row in df.iterrows():
        spk = str(row.get("Speaker", "")).strip()
        if not spk or spk.lower() == "nan":
            continue
        if spk == "T":
            role = "T"
            num = _tag_num(row.get("Teacher Tag"))
            macro = TEACHER_MACRO.get(num, 0)
        else:  # any named student, 'SS', 'Others'
            role = "S"
            num = _tag_num(row.get("Student Tag"))
            macro = STUDENT_MACRO.get(num, 0)
        roles.append(role)
        moves.append(num or 0)
        macros.append(macro)
        sent = row.get("Sentence")
        words.append(len(str(sent).split()) if sent is not None and str(sent) != "nan" else 1)
    name = os.path.splitext(os.path.basename(path))[0]
    return Lesson(name, grade_from_name(name), np.array(roles), np.array(moves),
                  np.array(macros, dtype=int), np.array(words, dtype=float))


# --------------------------------------------------------------------------- #
# the relational state vector (a, d, g)
# --------------------------------------------------------------------------- #
def relational_state(lesson: Lesson) -> dict:
    """The state vector (autonomy, dependence, generative output) for the whole lesson."""
    is_s = lesson.role == "S"
    student_moves = lesson.move[is_s]
    student_moves = student_moves[student_moves > 0]
    n_s = max(len(student_moves), 1)
    a = float(np.mean(np.isin(student_moves, list(_AUTONOMY))))
    g = float(np.mean(np.isin(student_moves, list(_GENERATIVE))))
    d = float(np.mean(lesson.role == "T"))           # teacher's share of the floor
    return {"a": a, "d": d, "g": g, "n_student_moves": len(student_moves),
            "n_utterances": len(lesson.role)}


def state_trajectory(lesson: Lesson, n_seg: int = 4):
    """(a, d, g) computed in ``n_seg`` equal windows along the lesson -- the longitudinal
    trajectory of eq. 24."""
    idx = np.linspace(0, len(lesson.role), n_seg + 1).astype(int)
    out = []
    for k in range(n_seg):
        sub = Lesson(lesson.name, lesson.grade, lesson.role[idx[k]:idx[k+1]],
                     lesson.move[idx[k]:idx[k+1]], lesson.macro[idx[k]:idx[k+1]])
        out.append(relational_state(sub))
    return out


def theta_longitudinal(lesson: Lesson, n_seg: int = 4) -> float:
    """Theta = d(autonomy) - d(dependence) across the lesson (eq. 25): the sign of the
    holonomy. >0 generative (autonomy rises, dependence falls), <0 dominative."""
    traj = state_trajectory(lesson, n_seg)
    da = traj[-1]["a"] - traj[0]["a"]
    dd = traj[-1]["d"] - traj[0]["d"]
    return float(da - dd)


# --------------------------------------------------------------------------- #
# transition operators, holonomy, and power
# --------------------------------------------------------------------------- #
def transition_operators(lesson: Lesson, smoothing: float = 0.25):
    """Estimate T_{t->s} and T_{s->t} on the macro-state space from the turn sequence.

    Each is a 3x3 row-stochastic matrix: T_ts[i, j] = P(student macro-state j | preceding
    teacher macro-state i), and conversely. Laplace smoothing keeps empty rows well-defined.
    """
    T_ts = np.full((3, 3), smoothing)
    T_st = np.full((3, 3), smoothing)
    r, m = lesson.role, lesson.macro
    for i in range(len(r) - 1):
        if r[i] == "T" and r[i + 1] == "S":
            T_ts[m[i], m[i + 1]] += 1
        elif r[i] == "S" and r[i + 1] == "T":
            T_st[m[i], m[i + 1]] += 1
    T_ts /= T_ts.sum(axis=1, keepdims=True)
    T_st /= T_st.sum(axis=1, keepdims=True)
    return T_ts, T_st


def holonomy_operator(lesson: Lesson) -> np.ndarray:
    """H(gamma) = T_ts T_st around the teacher-student cycle (eq. 23)."""
    T_ts, T_st = transition_operators(lesson)
    return T_ts @ T_st


def power_C(lesson: Lesson) -> float:
    """C = || T_ts T_st - T_st T_ts || -- the strength of power = non-commutativity (eq. 26)."""
    T_ts, T_st = transition_operators(lesson)
    return float(np.linalg.norm(T_ts @ T_st - T_st @ T_ts))


def theta_holonomy(lesson: Lesson) -> float:
    """Sign of the holonomy read from the operator: applying one teacher-student cycle to a
    neutral state, does it push the discourse toward Generative (+) or Passive (-)?"""
    H = holonomy_operator(lesson)
    start = np.array([1 / 3, 1 / 3, 1 / 3])
    end = start @ H                       # row-vector times row-stochastic matrix
    return float(end[2] - end[0])          # Generative mass - Passive mass


# --------------------------------------------------------------------------- #
# genuine vs forged deliberation (the uptake of student contributions)
# --------------------------------------------------------------------------- #
def uptake_rate(lesson: Lesson) -> float:
    """Among student claims / reasoning immediately followed by a teacher move, the fraction
    the teacher takes up (revoice / restate / relate / mark). High = genuine deliberation
    (value returned, the student a co-author); low = forged (value extracted)."""
    r, mv = lesson.role, lesson.move
    taken, total = 0, 0
    for i in range(len(r) - 1):
        if r[i] == "S" and mv[i] in _GENERATIVE and r[i + 1] == "T":
            total += 1
            if mv[i + 1] in _UPTAKE:
                taken += 1
    return float(taken / total) if total else np.nan


# --------------------------------------------------------------------------- #
# corpus-level driver
# --------------------------------------------------------------------------- #
def analyze_lesson(path: str) -> dict:
    lesson = load_lesson(path)
    st = relational_state(lesson)
    return {
        "name": lesson.name, "grade": lesson.grade,
        "a": st["a"], "d": st["d"], "g": st["g"],
        "n_student_moves": st["n_student_moves"], "n_utterances": st["n_utterances"],
        "theta_long": theta_longitudinal(lesson),
        "theta_hol": theta_holonomy(lesson),
        "C": power_C(lesson),
        "uptake": uptake_rate(lesson),
    }


def analyze_corpus(folder: str, min_student_moves: int = 15):
    """Analyze every transcript in ``folder``; keep lessons with enough student moves to be
    informative. Returns a list of metric dicts."""
    paths = sorted(glob.glob(os.path.join(folder, "*.xlsx")))
    rows = []
    for p in paths:
        try:
            r = analyze_lesson(p)
        except Exception:
            continue
        if r["n_student_moves"] >= min_student_moves:
            rows.append(r)
    return rows
