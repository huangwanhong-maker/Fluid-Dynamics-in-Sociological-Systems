"""Stage II/III -- power as the non-commutativity of holonomy (paper eq. 11).

  09  abelian vs non-abelian holonomy  -- order-independence (no power) vs
                                          order-dependence (power), on the Bloch sphere
                                          S^2 = SU(2)/U(1)

Run:  PYTHONPATH=. python experiments/stage3_nonabelian.py
"""

from __future__ import annotations

import numpy as np

from fluid_socio.nonabelian import su2, path_ordered_holonomy, commutator_norm, bloch_vector
from _common import get_plt, save


def _arc(axis, angle, start, n=40):
    """Bloch-sphere waypoints as the rotation (axis, angle) is applied to ``start``."""
    return np.array([bloch_vector(su2(axis, angle * k / n), start) for k in range(n + 1)])


def _two_orders(axis1, ang1, axis2, ang2, start):
    """Return the two transported paths (gamma1-then-gamma2, gamma2-then-gamma1) and
    their endpoints."""
    # order 1: apply U1 then U2
    a1 = _arc(axis1, ang1, start)
    p1 = a1[-1]
    a2 = _arc(axis2, ang2, p1)
    path_12 = np.vstack([a1, a2])
    # order 2: apply U2 then U1
    b1 = _arc(axis2, ang2, start)
    q1 = b1[-1]
    b2 = _arc(axis1, ang1, q1)
    path_21 = np.vstack([b1, b2])
    return path_12, path_21


def _draw_sphere(ax):
    u = np.linspace(0, 2 * np.pi, 40)
    v = np.linspace(0, np.pi, 20)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_surface(x, y, z, color="lightgray", alpha=0.15, linewidth=0)
    ax.plot_wireframe(x, y, z, color="gray", alpha=0.15, rstride=4, cstride=4)
    ax.set_box_aspect((1, 1, 1))
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])


def _plot_case(ax, axis1, ang1, axis2, ang2, start, title):
    _draw_sphere(ax)
    p12, p21 = _two_orders(axis1, ang1, axis2, ang2, start)
    ax.plot(*p12.T, color="crimson", lw=2.5, label="gamma1 then gamma2")
    ax.plot(*p21.T, color="navy", lw=2.5, label="gamma2 then gamma1")
    ax.scatter(*start, color="black", s=40)
    ax.scatter(*p12[-1], color="crimson", s=80, depthshade=False)
    ax.scatter(*p21[-1], color="navy", s=80, depthshade=False)
    U1 = su2(axis1, ang1)
    U2 = su2(axis2, ang2)
    gap = float(np.linalg.norm(p12[-1] - p21[-1]))
    ax.set_title(f"{title}\ncommutator ||U1U2-U2U1|| = {commutator_norm(U1, U2):.3f}\n"
                 f"endpoint gap = {gap:.3f}", fontsize=10)
    return gap


def main():
    start = np.array([0.0, 0.0, 1.0])  # north pole

    plt = get_plt()
    if plt is None:
        # still print the numbers
        U_ab = (su2((0, 0, 1), 1.2), su2((0, 0, 1), 2.0))
        U_na = (su2((1, 0, 0), 1.2), su2((0, 1, 0), 2.0))
        print(f"09 commutator: abelian={commutator_norm(*U_ab):.3f}  "
              f"non-abelian={commutator_norm(*U_na):.3f}")
        return

    fig = plt.figure(figsize=(13, 6))
    ax0 = fig.add_subplot(1, 2, 1, projection="3d")
    ax1 = fig.add_subplot(1, 2, 2, projection="3d")

    # Abelian residue H = U(1): both holonomies rotate about the SAME axis -> commute.
    # (Start off-axis so the rotation is visible.)
    start_ab = np.array([np.sin(0.6), 0.0, np.cos(0.6)])
    gap_ab = _plot_case(ax0, (0, 0, 1), 1.3, (0, 0, 1), 2.1, start_ab,
                        "ABELIAN H = U(1): order does NOT matter")

    # Non-abelian residue H: holonomies about different axes -> do not commute = POWER.
    gap_na = _plot_case(ax1, (1, 0, 0), 1.3, (0, 1, 0), 2.1, start,
                        "NON-ABELIAN H: order MATTERS (= power)")
    ax1.legend(loc="upper left", fontsize=8)

    print(f"09 non-commutativity: abelian endpoint gap = {gap_ab:.3e} (coincide), "
          f"non-abelian gap = {gap_na:.3f} (differ)")

    fig.suptitle("Stage II/III (eq. 11): power is the order-dependence of holonomy, "
                 "arising exactly when the residual symmetry H is non-abelian", fontsize=12)
    fig.tight_layout()
    save(fig, "09_noncommutativity.png")


if __name__ == "__main__":
    main()
