"""The value/power flow as a 2D vorticity-streamfunction model.

This realizes the fluid layer of the paper (eqs 1-6 and, in its reinstated role,
17-19) on a periodic domain. We carry three fields:

- ``omega``    -- value vorticity  (eq. 4); the streamfunction recovers the velocity
- ``rho``      -- value *stock* density (eq. 1), advected with a source ``S``
- ``p = (px, py)`` -- the power field (eq. 3), the history of value flux

The velocity is recovered from the vorticity by the streamfunction, which makes the
flow incompressible (div u = 0). This is the natural home of Proposition 2.1, whose
statement is about the vorticity equation: the appropriative pressure gradient never
appears in it, so only ``curl(f_pow)`` (and, in 3D, vortex stretching) can change the
circulation.

Governing update (2D, so vortex stretching ``(omega . grad) u`` vanishes):

    d omega / dt = -(u . grad) omega + nu * laplacian(omega) + curl(f_pow)
    d rho   / dt = -(u . grad) rho   + S
    d p     / dt = alpha * (rho * u) - beta * p
    f_pow        = power_gain * p
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from .grid import Grid2D


@dataclass
class State:
    """The full field state. Supports the arithmetic an RK time-step needs."""

    omega: np.ndarray
    rho: np.ndarray
    px: np.ndarray
    py: np.ndarray

    def __add__(self, other: "State") -> "State":
        return State(
            self.omega + other.omega,
            self.rho + other.rho,
            self.px + other.px,
            self.py + other.py,
        )

    def __mul__(self, c: float) -> "State":
        return State(self.omega * c, self.rho * c, self.px * c, self.py * c)

    __rmul__ = __mul__

    def copy(self) -> "State":
        return replace(
            self,
            omega=self.omega.copy(),
            rho=self.rho.copy(),
            px=self.px.copy(),
            py=self.py.copy(),
        )


class FluidModel:
    """Value/power flow on a periodic grid.

    Parameters
    ----------
    grid:
        The spatial grid.
    nu:
        Viscosity / relational inertia (eq. 2). Large ``nu`` solidifies the flow toward
        laminar structure; small ``nu`` permits turbulence and new structure.
    alpha, beta:
        Power-field reinforcement and forgetting rates (eq. 3). The ratio ``alpha/beta``
        is the solidification order parameter: ``alpha``-dominant locks the flow into a
        frozen appropriative channel; ``beta``-dominant keeps it flowing.
    power_gain:
        Coupling strength of ``f_pow = power_gain * p`` back into the momentum/vorticity.
    drag_kappa:
        Solidification drag. Accumulated power acts as "relational inertia / historical
        drag" (sec. 2.2): a friction on the flow proportional to ``|p|^2`` that damps
        vorticity where value has repeatedly flowed,
            d omega / dt  +=  - drag_kappa * |p|^2 * omega.
        With alpha-dominant power (which remembers its history) this is a positive
        feedback -- flux builds power, power builds drag, drag freezes the flow -- so the
        circulating structure collapses to a frozen, appropriative fixed point (sec. 5.3).
        This is the modeling choice that unifies the two things the paper independently
        calls "the solidification parameter": viscosity (drag) and the ratio alpha/beta.
    source:
        The value source ``S`` (eq. 1). ``None`` means no source (pure transport);
        otherwise a function ``S(grid, state, t) -> array`` or a constant array.
    """

    def __init__(
        self,
        grid: Grid2D,
        nu: float = 1e-3,
        alpha: float = 0.0,
        beta: float = 1.0,
        power_gain: float = 0.0,
        drag_kappa: float = 0.0,
        source=None,
    ):
        self.grid = grid
        self.nu = nu
        self.alpha = alpha
        self.beta = beta
        self.power_gain = power_gain
        self.drag_kappa = drag_kappa
        self.source = source
        self.t = 0.0

    # -- derived quantities -----------------------------------------------------

    def velocity(self, omega: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Recover the incompressible velocity ``u = (d psi/dy, -d psi/dx)`` from
        vorticity, where the streamfunction solves ``laplacian(psi) = -omega``."""
        psi = self.grid.solve_poisson(-omega)
        ux = self.grid.ddy(psi)
        uy = -self.grid.ddx(psi)
        return ux, uy

    def force(self, px: np.ndarray, py: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """The power force ``f_pow = power_gain * p`` (default coupling ``f(p) = p``)."""
        return self.power_gain * px, self.power_gain * py

    def _source_term(self, state: State) -> np.ndarray:
        if self.source is None:
            return self.grid.zero()
        if callable(self.source):
            return self.source(self.grid, state, self.t)
        return self.source

    # -- dynamics ---------------------------------------------------------------

    def rhs(self, state: State) -> State:
        """Time derivative of the full state."""
        g = self.grid
        ux, uy = self.velocity(state.omega)

        def advect(f):
            return ux * g.ddx(f) + uy * g.ddy(f)

        fx, fy = self.force(state.px, state.py)
        domega = -advect(state.omega) + self.nu * g.laplacian(state.omega) + g.curl(fx, fy)
        if self.drag_kappa:
            # historical drag: accumulated power frictionally damps the vorticity
            domega = domega - self.drag_kappa * (state.px**2 + state.py**2) * state.omega
        drho = -advect(state.rho) + self._source_term(state)
        dpx = self.alpha * (state.rho * ux) - self.beta * state.px
        dpy = self.alpha * (state.rho * uy) - self.beta * state.py
        return State(domega, drho, dpx, dpy)

    def step(self, state: State, dt: float) -> State:
        """Advance the state by ``dt`` using midpoint (RK2) integration."""
        k1 = self.rhs(state)
        mid = state + k1 * (0.5 * dt)
        k2 = self.rhs(mid)
        new = state + k2 * dt
        self.t += dt
        return new

    # -- construction helpers ---------------------------------------------------

    def make_state(self, omega=None, rho=None) -> State:
        """Build an initial state, defaulting to zero vorticity and unit density."""
        g = self.grid
        omega = g.zero() if omega is None else omega
        rho = np.ones((g.nx, g.ny)) if rho is None else rho
        return State(omega.copy(), rho.copy(), g.zero(), g.zero())
