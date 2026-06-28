"""Unit tests for the spectral operators and the Proposition 2.1 invariant.

Run with:  python -m pytest tests/   (or)   python tests/test_operators.py
"""

import numpy as np

from fluid_socio import Grid2D, helmholtz_decomposition, circulation_loop, circulation_stokes
from fluid_socio.fluid import FluidModel


def _random_scalar(grid, seed=0):
    """A smooth random periodic scalar field (a few low Fourier modes)."""
    rng = np.random.default_rng(seed)
    field = grid.zero()
    for kx, ky in [(1, 0), (0, 1), (2, 1), (1, 2), (3, 2)]:
        a, b = rng.standard_normal(2)
        field += a * np.cos(kx * grid.X + ky * grid.Y) + b * np.sin(kx * grid.X + ky * grid.Y)
    return field


def test_curl_of_gradient_is_zero():
    """curl(grad phi) == 0 to machine precision -- the spectral identity behind Prop 2.1."""
    grid = Grid2D(64, 64)
    phi = _random_scalar(grid)
    gx, gy = grid.grad(phi)
    assert np.max(np.abs(grid.curl(gx, gy))) < 1e-10


def test_helmholtz_reconstruction():
    """A field equals the sum of its gradient and solenoidal parts, and the parts
    have the defining properties (curl-free / divergence-free)."""
    grid = Grid2D(64, 64)
    fx = _random_scalar(grid, seed=1)
    fy = _random_scalar(grid, seed=2)
    (gx, gy), (sx, sy) = helmholtz_decomposition(grid, fx, fy)
    assert np.max(np.abs((gx + sx) - fx)) < 1e-10
    assert np.max(np.abs((gy + sy) - fy)) < 1e-10
    assert np.max(np.abs(grid.curl(gx, gy))) < 1e-10   # gradient part is curl-free
    assert np.max(np.abs(grid.div(sx, sy))) < 1e-10    # solenoidal part is divergence-free


def test_stokes_consistency():
    """The line-integral holonomy matches the area integral of vorticity (Stokes)."""
    grid = Grid2D(128, 128)
    # A velocity field with known vorticity.
    psi = _random_scalar(grid, seed=3)
    ux, uy = grid.ddy(psi), -grid.ddx(psi)
    omega = grid.curl(ux, uy)
    loop = circulation_loop(grid, ux, uy, 20, 90, 30, 100)
    stokes = circulation_stokes(grid, omega, 20, 90, 30, 100)
    assert abs(loop - stokes) < 1e-2 * max(1.0, abs(stokes))


def test_proposition_2_1_appropriation_generates_no_circulation():
    """THE invariant. Proposition 2.1: the appropriative (pure-gradient) part of the
    power force makes *no contribution to the evolution of vorticity*, hence none to the
    holonomy; only the solenoidal (generative) part does.

    The honest test isolates the *force's contribution* by differencing against a
    no-force baseline that evolves under the same advection and viscosity. (Circulation
    around a fixed Eulerian loop is not itself conserved -- vorticity advects through its
    edges -- so a before/after comparison would conflate advection with the force.)

    This is the property the entire normative reading of the model rests on, so the code
    must not be able to violate it silently.
    """
    grid = Grid2D(128, 128)
    # Seed a flow with some circulation.
    psi0 = _random_scalar(grid, seed=5)
    omega0 = -grid.laplacian(psi0)
    loop_box = (24, 100, 24, 100)

    # Build a power field and split f_pow = p into gradient + solenoidal parts.
    raw_x = _random_scalar(grid, seed=6)
    raw_y = _random_scalar(grid, seed=7)
    (gx, gy), (sx, sy) = helmholtz_decomposition(grid, raw_x, raw_y)

    def evolved_circulation(px, py):
        # alpha = beta = 0 freezes the power field, so f_pow is constant in time and
        # the only thing distinguishing the runs is curl(f_pow).
        model = FluidModel(grid, nu=1e-3, alpha=0.0, beta=0.0, power_gain=1.0)
        state = model.make_state(omega=omega0)
        state.px, state.py = px, py
        for _ in range(60):
            state = model.step(state, dt=2e-3)
        ux, uy = model.velocity(state.omega)
        return circulation_loop(grid, ux, uy, *loop_box)

    zero = grid.zero()
    c_base = evolved_circulation(zero, zero)            # advection + viscosity only
    c_grad = evolved_circulation(gx, gy)               # + appropriative force
    c_sol = evolved_circulation(sx, sy)                # + generative force

    grad_contribution = abs(c_grad - c_base)
    sol_contribution = abs(c_sol - c_base)

    assert grad_contribution < 1e-6, (
        f"appropriation contributed {grad_contribution:.2e} to the holonomy (should be ~0)"
    )
    assert sol_contribution > 1e3 * max(grad_contribution, 1e-12), (
        f"generative contribution {sol_contribution:.2e} not clearly above "
        f"appropriative {grad_contribution:.2e}"
    )


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS  {name}")
    print("All tests passed.")
