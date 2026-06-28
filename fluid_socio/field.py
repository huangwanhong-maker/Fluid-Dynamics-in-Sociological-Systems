"""The relational field as an order parameter, and its topological defects (paper sec. 4).

After the symmetry breaking G -> H the broken state is a field Phi: Sigma -> M = G/H.
The simplest non-trivial case is M = G/H ~= S^1, where pi_1(S^1) = Z: subjects are
defects carrying an integer winding (eq. 9). Here we realize that case concretely as a
phase field theta(x, y) valued on the circle, with point defects of integer charge.

The canonical connection on the bundle G -> G/H is, for this abelian case, the flat
connection A = grad(theta) away from the cores, and the holonomy (eq. 10) around a loop
is exp(i * oint grad(theta).dl) = exp(i * 2*pi * (enclosed winding)). So the holonomy
sees only the topological charge enclosed -- the defining property the model needs.
"""

from __future__ import annotations

import numpy as np

from .grid import Grid2D


def phase_field(grid: Grid2D, defects: list[tuple[float, float, int]]) -> np.ndarray:
    """A phase field ``theta(x, y)`` in (-pi, pi] with the given point defects.

    ``defects`` is a list of ``(x, y, charge)``. Each contributes ``charge * angle`` to
    the phase, so a loop around it accumulates ``2*pi*charge``.
    """
    theta = grid.zero()
    for cx, cy, q in defects:
        theta = theta + q * np.arctan2(grid.Y - cy, grid.X - cx)
    return np.angle(np.exp(1j * theta))  # wrap to (-pi, pi]


def _wrap(d: np.ndarray) -> np.ndarray:
    """Wrap phase differences to (-pi, pi]."""
    return (d + np.pi) % (2 * np.pi) - np.pi


def winding_density(grid: Grid2D, theta: np.ndarray) -> np.ndarray:
    """Per-plaquette winding number (the topological charge density).

    Sums the wrapped phase differences counter-clockwise around each unit cell and
    divides by 2*pi. The result is ~0 everywhere except +/-1 at defect cores. Uses
    periodic neighbors; for an isolated-defect field keep cores away from the boundary.
    """
    tx = np.roll(theta, -1, axis=0)          # neighbor in +x
    txy = np.roll(tx, -1, axis=1)            # +x, +y
    ty = np.roll(theta, -1, axis=1)          # +y
    d1 = _wrap(tx - theta)
    d2 = _wrap(txy - tx)
    d3 = _wrap(ty - txy)
    d4 = _wrap(theta - ty)
    return (d1 + d2 + d3 + d4) / (2 * np.pi)


def find_defects(grid: Grid2D, theta: np.ndarray, tol: float = 0.5):
    """Locate defects as plaquettes whose winding number rounds to a non-zero integer.

    Returns a list of ``(x, y, charge)``.
    """
    w = winding_density(grid, theta)
    out = []
    ii, jj = np.where(np.abs(w) > tol)
    for i, j in zip(ii, jj):
        out.append((grid.x[i] + 0.5 * grid.dx, grid.y[j] + 0.5 * grid.dy, int(round(w[i, j]))))
    return out


def loop_winding(grid: Grid2D, theta: np.ndarray, i0: int, i1: int, j0: int, j1: int) -> float:
    """Total winding ``(1/2pi) oint grad(theta).dl`` around a rectangular loop.

    This is the abelian holonomy phase / 2*pi: an integer equal to the net charge the
    loop encloses, by the argument principle.
    """
    total = 0.0
    # bottom edge: i0..i1 at j0
    total += np.sum(_wrap(np.diff(theta[i0:i1 + 1, j0])))
    # right edge: j0..j1 at i1
    total += np.sum(_wrap(np.diff(theta[i1, j0:j1 + 1])))
    # top edge: i1..i0 at j1
    total += np.sum(_wrap(np.diff(theta[i0:i1 + 1, j1][::-1])))
    # left edge: j1..j0 at i0
    total += np.sum(_wrap(np.diff(theta[i0, j0:j1 + 1][::-1])))
    return total / (2 * np.pi)


def running_holonomy(grid: Grid2D, theta: np.ndarray, i0: int, i1: int, j0: int, j1: int):
    """The phase accumulated ``oint grad(theta).dl`` as a loop is traversed, returned as
    a cumulative array. Its final value is ``2*pi * (enclosed winding)``.

    Used to visualize that the holonomy is a property of the *whole* loop, building up
    to a quantized total rather than living at any one point.
    """
    edges = []
    # bottom (i0->i1 at j0)
    edges += [theta[i, j0] for i in range(i0, i1 + 1)]
    # right (j0->j1 at i1)
    edges += [theta[i1, j] for j in range(j0, j1 + 1)]
    # top (i1->i0 at j1)
    edges += [theta[i, j1] for i in range(i1, i0 - 1, -1)]
    # left (j1->j0 at i0)
    edges += [theta[i0, j] for j in range(j1, j0 - 1, -1)]
    edges = np.array(edges)
    steps = _wrap(np.diff(edges))
    return np.concatenate([[0.0], np.cumsum(steps)])
