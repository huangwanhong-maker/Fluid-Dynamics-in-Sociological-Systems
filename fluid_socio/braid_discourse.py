"""Non-abelian holonomy of real classroom discourse, and an empirical probe of Prop. 6.1.

Part III's first pass measured power as the non-commutativity of *stochastic* transition
matrices -- a classical shadow. This module lifts the discourse to a genuinely non-abelian,
representation-valued holonomy (Stage III, eq. 10), so that the model's deepest claim --
that discriminating power requires a *non-universal* (constrained) reachable set of
holonomies (Prop. 6.1) -- can be tested on data.

Construction. Each utterance is an SU(2) rotation:
    axis  = its discourse macro-state    (Passive -> z, Controlling -> x, Generative -> y;
                                          orthogonal axes, so moves do NOT commute)
    angle = kappa * sqrt(word count)     (a real, continuous magnitude from the transcript)
A stretch of discourse is the path-ordered product of these rotations -- its holonomy. The
holonomy depends on the ORDER of moves (non-commutativity = power), which is exactly the
structure a shuffled null model destroys while preserving move and length frequencies.

The reachable set is the cloud of holonomies {U |0>} over many windows. Prop. 6.1 asks
whether it is dense (universal -> no robust good/bad predicate) or constrained
(non-universal -> a robust predicate can exist). The axis/angle assignment is a stipulation;
what is empirical is the order of real moves and the resulting holonomy structure.
"""

from __future__ import annotations

import numpy as np

from .nonabelian import su2

# Orthogonal rotation axes for the three discourse macro-states (maximally non-abelian).
AXES = {0: (0.0, 0.0, 1.0),   # Passive     -> z
        1: (1.0, 0.0, 0.0),   # Controlling -> x
        2: (0.0, 1.0, 0.0)}   # Generative  -> y


def utterance_unitary(macro: int, words: float, kappa: float) -> np.ndarray:
    """SU(2) rotation for one utterance: axis from the macro-state, angle from its length."""
    return su2(AXES[macro], kappa * np.sqrt(max(words, 1.0)))


def holonomy(macros, words, kappa: float) -> np.ndarray:
    """Path-ordered product U_n ... U_1 of the per-utterance rotations (eq. 10)."""
    U = np.eye(2, dtype=complex)
    for m, w in zip(macros, words):
        U = utterance_unitary(int(m), float(w), kappa) @ U
    return U


def bloch(U: np.ndarray) -> np.ndarray:
    """Bloch vector of U|0> -- the reachable state from the north pole."""
    psi = U @ np.array([1.0, 0.0], dtype=complex)
    return np.array([2 * np.real(np.conj(psi[0]) * psi[1]),
                     2 * np.imag(np.conj(psi[0]) * psi[1]),
                     abs(psi[0]) ** 2 - abs(psi[1]) ** 2])


def window_holonomies(lesson, W: int = 8, step: int = 3, kappa: float = 0.55):
    """Holonomies of sliding windows of W consecutive utterances; returns SU(2) matrices."""
    m, w = lesson.macro, lesson.words
    out = []
    for i in range(0, max(len(m) - W, 1), step):
        out.append(holonomy(m[i:i + W], w[i:i + W], kappa))
    return out


def window_points(lesson, **kw) -> np.ndarray:
    return np.array([bloch(U) for U in window_holonomies(lesson, **kw)])


def lesson_signature(lesson, **kw) -> np.ndarray:
    """A stable per-lesson holonomy signature: the centroid of its window Bloch points."""
    pts = window_points(lesson, **kw)
    return pts.mean(axis=0) if len(pts) else np.zeros(3)


def shuffled_lesson(lesson, seed: int):
    """A copy with the utterance ORDER permuted (move and length frequencies preserved).

    This is the null model: it keeps everything except the non-commutative structure that
    order carries, so any holonomy effect that survives shuffling is not about power."""
    from .education import Lesson
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(lesson.macro))
    return Lesson(lesson.name, lesson.grade, lesson.role[perm], lesson.move[perm],
                  lesson.macro[perm], lesson.words[perm])


# --------------------------------------------------------------------------- #
# coverage of the group: the universality / non-universality measure
# --------------------------------------------------------------------------- #
def coverage(points: np.ndarray, n_lat: int = 12, n_lon: int = 24):
    """Occupancy and normalized entropy of the reachable set over an equal-area binning of
    the Bloch sphere. High -> dense (universal); low -> constrained (non-universal)."""
    if len(points) == 0:
        return 0.0, 0.0
    z = np.clip(points[:, 2], -1, 1)
    phi = np.arctan2(points[:, 1], points[:, 0])
    lat = np.minimum((((z + 1) / 2) * n_lat).astype(int), n_lat - 1)   # equal-area in z
    lon = np.minimum(((phi + np.pi) / (2 * np.pi) * n_lon).astype(int), n_lon - 1)
    flat = lat * n_lon + lon
    counts = np.bincount(flat, minlength=n_lat * n_lon).astype(float)
    occupied = float(np.mean(counts > 0))
    p = counts / counts.sum()
    nz = p[p > 0]
    entropy = float(-np.sum(nz * np.log(nz)) / np.log(len(counts)))
    return occupied, entropy


def haar_points(n: int, seed: int = 0) -> np.ndarray:
    """Bloch points of Haar-random SU(2) -- the fully universal (dense) reference: U|0> is
    uniform on the sphere."""
    rng = np.random.default_rng(seed)
    z = rng.uniform(-1, 1, n)
    phi = rng.uniform(0, 2 * np.pi, n)
    r = np.sqrt(1 - z * z)
    return np.column_stack([r * np.cos(phi), r * np.sin(phi), z])
