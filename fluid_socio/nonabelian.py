"""Non-abelian holonomy and power as non-commutativity (paper sec. 4.3, eq. 11).

When the residual symmetry H is non-abelian the holonomy is a genuine transformation,
not a mere phase, and the order of traversal matters:

    H abelian      =>  hol(g1) hol(g2)  =  hol(g2) hol(g1)        (no power)
    H non-abelian  =>  hol(g1) hol(g2) != hol(g2) hol(g1)        (power)

We realize this with G = SU(2) acting on the Bloch sphere S^2 = SU(2)/U(1) -- itself an
order-parameter space G/H. A holonomy is an SU(2) element (a rotation of the sphere);
"power" is the failure of two holonomies to commute, measured by the commutator
|| U1 U2 - U2 U1 ||.
"""

from __future__ import annotations

import numpy as np

# Pauli matrices.
SIGMA = (
    np.array([[0, 1], [1, 0]], dtype=complex),
    np.array([[0, -1j], [1j, 0]], dtype=complex),
    np.array([[1, 0], [0, -1]], dtype=complex),
)
I2 = np.eye(2, dtype=complex)


def su2(axis, angle: float) -> np.ndarray:
    """The SU(2) element rotating by ``angle`` about a unit ``axis``:
    ``U = cos(t/2) I - i sin(t/2) (n . sigma)``."""
    n = np.asarray(axis, dtype=float)
    n = n / np.linalg.norm(n)
    ndotsig = n[0] * SIGMA[0] + n[1] * SIGMA[1] + n[2] * SIGMA[2]
    return np.cos(angle / 2) * I2 - 1j * np.sin(angle / 2) * ndotsig


def path_ordered_holonomy(segments) -> np.ndarray:
    """Path-ordered product of SU(2) elements along a loop.

    ``segments`` is a list of ``(axis, angle)``; the holonomy is the ordered product
    ``U_n ... U_2 U_1`` (later segments act on the left), the discrete form of the
    path-ordered exponential P exp(integral A).
    """
    U = I2.copy()
    for axis, angle in segments:
        U = su2(axis, angle) @ U
    return U


def commutator_norm(U1: np.ndarray, U2: np.ndarray) -> float:
    """The power measure ``|| U1 U2 - U2 U1 ||`` (Frobenius). Zero iff the holonomies
    commute (abelian residue, no power)."""
    return float(np.linalg.norm(U1 @ U2 - U2 @ U1))


def bloch_vector(U: np.ndarray, v0=(0.0, 0.0, 1.0)) -> np.ndarray:
    """Image of a Bloch vector ``v0`` under the SO(3) rotation corresponding to ``U``.

    A spinor state |psi> has Bloch vector <psi|sigma|psi>; conjugating by U rotates it.
    We start from the spin-up state at the north pole and apply U.
    """
    # Build the spinor whose Bloch vector is v0 (north pole -> |0>).
    v0 = np.asarray(v0, dtype=float)
    # Density matrix rho = (I + v0 . sigma)/2, then rho' = U rho U^dagger.
    rho = 0.5 * (I2 + v0[0] * SIGMA[0] + v0[1] * SIGMA[1] + v0[2] * SIGMA[2])
    rho = U @ rho @ U.conj().T
    return np.array([np.real(np.trace(rho @ SIGMA[k])) for k in range(3)])


def transport_path(holonomies, v0=(0.0, 0.0, 1.0)):
    """Bloch-vector waypoints as a sequence of holonomies is applied cumulatively."""
    pts = [np.asarray(v0, dtype=float)]
    U = I2.copy()
    for H in holonomies:
        U = H @ U
        pts.append(bloch_vector(U, v0))
    return np.array(pts)
