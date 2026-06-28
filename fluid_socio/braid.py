"""The braid group and its representations (paper sec. 4.7-4.8, 5.3, 6).

The braid group B_n is the statistics of n indistinguishable defects (eq. 13). It is not
posited but computed as pi_1 of their configuration space. Here we work with concrete
unitary representations of B_3 on a 2-dimensional fusion space and use them to exhibit:

- the **braid relation** (Yang-Baxter, eq. 15) -- satisfied by both representations;
- the **three non-abelian demands** (sec. 5.3): non-commuting braiding (power), a
  fusion space of dimension > 1 (resonance), and multi-channel fusion (generativity);
- the **discrimination constraint** (Prop 6.1): a *non-universal* representation (Ising)
  has a finite, hence discrete, image -- a good/bad predicate can be read off robustly --
  while a *universal* one (Fibonacci) has a dense image, on which no robust
  holonomy-factoring predicate exists.

Both are standard anyon models; we use them as the paper's two sides of the admissible
band (Remark 6.3): "the Jones representations ... away from the universal Fibonacci-type
cases" give the finite-image examples.
"""

from __future__ import annotations

import numpy as np

PHI = (1 + np.sqrt(5)) / 2  # golden ratio


def ising_generators() -> tuple[np.ndarray, np.ndarray]:
    """Ising-anyon braiding on a 2D fusion space, as the phase gate and its Hadamard
    conjugate ``b1 = S``, ``b2 = H S H``.

    These satisfy the braid relation and generate the single-qubit Clifford group -- a
    non-abelian but FINITE (hence non-universal) image. The orbit of the |0> state is the
    six stabilizer states (an octahedron), so a robust good/bad predicate can be read off
    the reachable holonomy set.
    """
    H = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)
    b1 = np.array([[1, 0], [0, 1j]], dtype=complex)  # phase gate S
    b2 = H @ b1 @ H
    return b1, b2


def fibonacci_generators() -> tuple[np.ndarray, np.ndarray]:
    """Fibonacci-anyon braiding of three tau-anyons (a 2D fusion space).

    The image is DENSE in SU(2) -- universal. ``b2 = F b1 F`` with the involutory
    F-matrix ``F`` (``F^2 = I``).
    """
    R1 = np.exp(-4j * np.pi / 5)
    R2 = np.exp(3j * np.pi / 5)
    b1 = np.array([[R1, 0], [0, R2]], dtype=complex)
    inv_phi = 1 / PHI
    F = np.array([[inv_phi, np.sqrt(inv_phi)], [np.sqrt(inv_phi), -inv_phi]], dtype=complex)
    b2 = F @ b1 @ F
    return b1, b2


def braid_relation_residual(b1: np.ndarray, b2: np.ndarray) -> float:
    """Frobenius norm of ``b1 b2 b1 - b2 b1 b2`` -- zero iff the Yang-Baxter relation
    (eq. 15) holds."""
    return float(np.linalg.norm(b1 @ b2 @ b1 - b2 @ b1 @ b2))


def commutator_residual(b1: np.ndarray, b2: np.ndarray) -> float:
    """Frobenius norm of ``b1 b2 - b2 b1`` -- non-zero means power (sec. 5.3, premise P)."""
    return float(np.linalg.norm(b1 @ b2 - b2 @ b1))


def random_braid_word(gens, length: int, rng) -> np.ndarray:
    """Unitary of a random length-``length`` braid word in the given generators and
    their inverses."""
    U = np.eye(gens[0].shape[0], dtype=complex)
    for _ in range(length):
        g = gens[rng.integers(len(gens))]
        if rng.random() < 0.5:
            g = np.linalg.inv(g)
        U = g @ U
    return U


def _bloch(U: np.ndarray) -> np.ndarray:
    """Bloch vector of ``U |0>`` (the reachable state from the north pole)."""
    psi = U @ np.array([1.0, 0.0], dtype=complex)
    sx = 2 * np.real(np.conj(psi[0]) * psi[1])
    sy = 2 * np.imag(np.conj(psi[0]) * psi[1])
    sz = abs(psi[0]) ** 2 - abs(psi[1]) ** 2
    return np.array([sx, sy, sz])


def reachable_states(gens, n_words: int = 2000, max_len: int = 12, seed: int = 0):
    """Sample the reachable holonomy set as Bloch points ``rho(b) |0>``.

    A finite (non-universal) image gives a finite point set; a dense (universal) image
    fills the sphere. This is the visual content of Proposition 6.1.
    """
    rng = np.random.default_rng(seed)
    pts = []
    for _ in range(n_words):
        U = random_braid_word(gens, int(rng.integers(1, max_len + 1)), rng)
        pts.append(_bloch(U))
    return np.array(pts)


def count_distinct(points: np.ndarray, tol: float = 1e-3) -> int:
    """Number of distinct points up to ``tol`` -- finite for non-universal reps, and
    effectively the sample size for dense (universal) ones."""
    keep = []
    for p in points:
        if not any(np.linalg.norm(p - q) < tol for q in keep):
            keep.append(p)
    return len(keep)


def fibonacci_fusion_dim(n: int) -> int:
    """Dimension of the fusion space of ``n`` tau-anyons: the Fibonacci numbers.

    tau x tau = 1 + tau is multi-channel (two outcomes) -- the generativity premise G --
    and dim > 1 for n >= 3 is the resonance premise R.
    """
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return a
