"""Stage VI -- the scale-invariant operationalization (paper sec. 10).

The continuous holonomy is discretized to a product of estimated transition operators
around a relational cycle (eq. 23):

    H_hat(gamma) = T_{i->j} T_{j->i}

Each node carries a relational state vector (eq. 24)

    s_i(t) = ( a_i(t), d_i(t), g_i(t) )   = (autonomy, dependence, generative output)

and the model computes only the scale-invariant quantities (sec. 10.1):

    Theta(gamma) = (a(t2) - a(t1)) - (d(t2) - d(t1))           sign of the holonomy (eq. 25)
    C            = || T_{i->j} T_{j->i} - T_{j->i} T_{i->j} ||  strength of power (eq. 26)

We never report an absolute holonomy magnitude; only sign, order, and non-commutativity.

This module provides a synthetic generative model of two teaching cohorts so the
falsifiable prediction of sec. 10.5 can be exercised end-to-end. Each student has two
latent parameters -- ``dominance`` (interaction asymmetry) and ``generativity`` (whether
the cycle returns value) -- from which BOTH the (a, d, g) trajectory and the transition
operators are built, so Theta and C are coherent readings of one underlying relation.
The numbers are illustrative, not measured (sec. 10.6).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Student:
    cohort: str
    dominance: float       # interaction asymmetry in [0, 1]; drives power strength C
    generativity: float    # value return in [-1, 1]; drives the sign of Theta
    t: np.ndarray          # sample times over the term (fortnightly)
    a: np.ndarray          # autonomy trajectory
    d: np.ndarray          # dependence trajectory
    g: np.ndarray          # generative-output trajectory
    exam: float            # exam score: testable, appropriable STOCK


# Cohort latent-parameter distributions (mean, sd) for (generativity, dominance).
COHORTS = {
    "inquiry":      {"gen": (0.65, 0.18), "dom": (0.50, 0.10)},   # generative power-to
    "lecture-drill": {"gen": (-0.35, 0.18), "dom": (0.80, 0.10)},  # dominative power-over
}


def generate_cohort(mode: str, n: int = 40, n_points: int = 7, seed: int = 0):
    """Generate a cohort of synthetic students for ``mode`` in ``COHORTS``."""
    rng = np.random.default_rng(seed)
    params = COHORTS[mode]
    t = np.linspace(0.0, 1.0, n_points)  # one term, normalized
    students = []
    for _ in range(n):
        gen = float(np.clip(rng.normal(*params["gen"]), -1, 1))
        dom = float(np.clip(rng.normal(*params["dom"]), 0, 1))

        a0 = rng.uniform(0.25, 0.40)
        d0 = rng.uniform(0.50, 0.65)
        noise = lambda s: rng.normal(0, s, n_points)
        a = np.clip(a0 + gen * 0.55 * t + noise(0.03), 0, 1)
        d = np.clip(d0 - gen * 0.45 * t + noise(0.03), 0, 1)
        g = np.clip(0.1 + np.maximum(gen, 0) * 0.6 * t + noise(0.03), 0, 1)

        # Exam score (STOCK): both cohorts learn content, so scores overlap and do NOT
        # track generativity -- the point of sec. 10.5. A little engagement dependence,
        # plus substantial cohort-independent noise.
        knowledge = 0.5 + 0.2 * dom + rng.normal(0, 0.12)
        exam = float(np.clip(60 + 25 * knowledge + rng.normal(0, 4), 0, 100))

        students.append(Student(mode, dom, gen, t, a, d, g, exam))
    return students


def transition_operators(student: Student):
    """Build the two edge operators of the teacher-student cycle from the latent params.

    ``T_ts`` (teacher acts on student) is an upper shear by the dominance; ``T_st``
    (student acts back) a lower shear, plus a generative coupling. Their commutator
    grows with dominance, giving the power strength C; pure peer symmetry (dominance 0)
    commutes (no power).
    """
    rho = student.dominance
    gam = student.generativity
    T_ts = np.array([[1.0, rho], [0.2 * gam, 1.0]])
    T_st = np.array([[1.0, 0.0], [0.5 * rho, 1.0]])
    return T_ts, T_st


def holonomy_operator(student: Student) -> np.ndarray:
    """H_hat(gamma) = T_{ts} T_{st} around the teacher-student loop (eq. 23)."""
    T_ts, T_st = transition_operators(student)
    return T_ts @ T_st


def theta(student: Student) -> float:
    """Theta = delta(autonomy) - delta(dependence): a scale-free proxy for the SIGN of
    the holonomy (eq. 25). >0 generative/power-to, <0 dominative/power-over, ~0
    appropriative."""
    da = student.a[-1] - student.a[0]
    dd = student.d[-1] - student.d[0]
    return float(da - dd)


def theta_trajectory(student: Student) -> np.ndarray:
    """Theta accumulated up to each sample time (for plotting the good/bad trajectory)."""
    da = student.a - student.a[0]
    dd = student.d - student.d[0]
    return da - dd


def power_C(student: Student) -> float:
    """C = || T_ts T_st - T_st T_ts ||: the strength of power = non-commutativity (eq. 26)."""
    T_ts, T_st = transition_operators(student)
    return float(np.linalg.norm(T_ts @ T_st - T_st @ T_ts))


def cohort_table(students) -> dict:
    """Summary statistics for a cohort."""
    return {
        "n": len(students),
        "theta_mean": float(np.mean([theta(s) for s in students])),
        "theta_sd": float(np.std([theta(s) for s in students])),
        "C_mean": float(np.mean([power_C(s) for s in students])),
        "exam_mean": float(np.mean([s.exam for s in students])),
        "exam_sd": float(np.std([s.exam for s in students])),
    }
