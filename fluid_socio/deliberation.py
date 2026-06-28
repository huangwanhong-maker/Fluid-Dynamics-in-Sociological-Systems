"""Deliberation dynamics (the case study: *Authorship Without Equilibrium*).

Paper 2 models deliberation as motion in a fibre bundle: the **base** is the space of
judgement configurations (the standing questions the affected keep returning to), and the
**fibre** over each configuration is the space of value the relation has produced there.
Deliberation traverses a closed loop in the base; the question is what the value does.

Three candidate attractors (sec. 3):

    fixed point     -- converge to one settled configuration (reflective equilibrium);
                       authorship ends when the questions stop.
    limit cycle     -- a closed orbit that returns exactly; the configuration recurs but
                       nothing is gained -- a circle, not a spiral.
    holonomic spiral-- the configuration returns while the value accumulates a non-trivial
                       remainder per circuit (a positive holonomy); authorship that returns
                       to its questions while carrying value forward.

The genuine/forged criterion (Claim 5.1) is then the SIGN of the holonomy on the loop:
genuine deliberation returns value to its participants (positive holonomy); forged
deliberation keeps the form while net-extracting value (zero or negative holonomy),
using the affected as fuel.

State is ``(x, y, v)``: ``(x, y)`` the base configuration, ``v`` the accumulated value.
"""

from __future__ import annotations

import numpy as np


def integrate(deriv, s0, dt: float, steps: int) -> np.ndarray:
    """Integrate ``ds/dt = deriv(s)`` with RK4. Returns an array of shape (steps+1, dim)."""
    s = np.asarray(s0, dtype=float)
    out = [s.copy()]
    for _ in range(steps):
        k1 = deriv(s)
        k2 = deriv(s + 0.5 * dt * k1)
        k3 = deriv(s + 0.5 * dt * k2)
        k4 = deriv(s + dt * k3)
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        out.append(s.copy())
    return np.array(out)


def fixed_point_deriv(omega=2 * np.pi, decay=0.6):
    """A spiral sink: the configuration settles to a point. Value is inert."""
    def f(s):
        x, y, v = s
        return np.array([-decay * x - omega * y, omega * x - decay * y, 0.0])
    return f


def limit_cycle_deriv(omega=2 * np.pi, pull=2.0):
    """A stable limit cycle at radius 1: the configuration recurs, value returns exactly."""
    def f(s):
        x, y, v = s
        g = pull * (1.0 - (x * x + y * y))
        return np.array([g * x - omega * y, g * y + omega * x, 0.0])
    return f


def spiral_deriv(omega=2 * np.pi, pull=2.0, holonomy_rate=0.5):
    """A holonomic spiral: the base is the limit cycle (configuration returns) while value
    accumulates at ``holonomy_rate`` per unit time -- a positive holonomy per circuit."""
    def f(s):
        x, y, v = s
        g = pull * (1.0 - (x * x + y * y))
        return np.array([g * x - omega * y, g * y + omega * x, holonomy_rate])
    return f


def value_staircase(holonomy_per_circuit: float, n_circuits: int = 6, per: int = 120):
    """Accumulated value across ``n_circuits`` deliberative circuits.

    Each circuit adds ``holonomy_per_circuit`` (positive = genuine/returned, negative =
    forged/extracted). Returns (time, value, config_angle)."""
    t, v, ang = [], [], []
    cur = 0.0
    for c in range(n_circuits):
        for k in range(per):
            frac = k / per
            t.append(c + frac)
            ang.append(2 * np.pi * frac)
            # value rises smoothly within the circuit by the per-circuit holonomy
            v.append(cur + holonomy_per_circuit * frac)
        cur += holonomy_per_circuit
    return np.array(t), np.array(v), np.array(ang)


def deliberation_holonomy(value: np.ndarray, per: int = 120) -> float:
    """Holonomy of one circuit = net change in value over a closed loop of the base."""
    return float(value[per] - value[0])
