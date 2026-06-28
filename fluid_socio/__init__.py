"""Fluid Dynamics in Sociological Systems.

A computational realization of the fluid layer of Huang, *From Fluid to Braid*.

The package is organized in layers that mirror the paper:

- ``grid``        — periodic 2D grid with exact (spectral) differential operators
- ``operators``   — Helmholtz decomposition and the holonomy / circulation diagnostic
- ``fluid``       — the value/power flow (eqs 1-6, 17-19) as a vorticity-streamfunction model

Invariants enforced throughout (see ``NOTES.md`` §9):

1. Only the *sign*, *order*, and *non-commutativity* of a holonomy are meaningful;
   absolute magnitude is never reported as a result (paper §4.5, §10.1).
2. The value *stock* (local density rho) and the *surplus* (non-local circulation) are
   kept strictly separate.
3. A pure-gradient ("appropriative") force leaves the holonomy invariant — Proposition 2.1.
   This is asserted as a unit test, not assumed.
"""

from .grid import Grid2D
from .operators import helmholtz_decomposition, circulation_loop, circulation_stokes
from .fluid import FluidModel

__all__ = [
    "Grid2D",
    "helmholtz_decomposition",
    "circulation_loop",
    "circulation_stokes",
    "FluidModel",
]
