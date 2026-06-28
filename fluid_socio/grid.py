"""Periodic 2D grid with spectral (FFT) differential operators.

On a periodic domain the Fourier transform diagonalizes differentiation, so every
operator the model needs -- gradient, divergence, curl, Laplacian, and the inverse
Laplacian (Poisson solve) -- is exact up to floating point. This is what makes
Proposition 2.1 testable to machine precision: the curl of a gradient is identically
zero in Fourier space.

Convention: a scalar field ``f`` is a real array of shape ``(nx, ny)`` with ``f[i, j]``
the value at position ``(x_i, y_j)``. A vector field is a pair ``(fx, fy)`` of such arrays.
"""

from __future__ import annotations

import numpy as np


class Grid2D:
    """A doubly-periodic rectangular grid with spectral calculus.

    Parameters
    ----------
    nx, ny:
        Number of grid points along x and y.
    lx, ly:
        Physical extent of the domain along x and y.
    """

    def __init__(self, nx: int = 128, ny: int = 128, lx: float = 2 * np.pi, ly: float = 2 * np.pi):
        self.nx, self.ny = nx, ny
        self.lx, self.ly = lx, ly
        self.dx, self.dy = lx / nx, ly / ny

        # Real-space coordinates (cell-centered, origin at 0).
        self.x = np.arange(nx) * self.dx
        self.y = np.arange(ny) * self.dy
        self.X, self.Y = np.meshgrid(self.x, self.y, indexing="ij")

        # Angular wavenumbers for each axis.
        kx = 2 * np.pi * np.fft.fftfreq(nx, d=self.dx)
        ky = 2 * np.pi * np.fft.fftfreq(ny, d=self.dy)
        self.KX, self.KY = np.meshgrid(kx, ky, indexing="ij")
        self.K2 = self.KX**2 + self.KY**2

        # For the inverse Laplacian: avoid division by zero at the zero (mean) mode.
        self._K2_inv = np.zeros_like(self.K2)
        nonzero = self.K2 > 0
        self._K2_inv[nonzero] = 1.0 / self.K2[nonzero]

    # -- elementary derivatives -------------------------------------------------

    def ddx(self, f: np.ndarray) -> np.ndarray:
        """Partial derivative d/dx."""
        return np.real(np.fft.ifft2(1j * self.KX * np.fft.fft2(f)))

    def ddy(self, f: np.ndarray) -> np.ndarray:
        """Partial derivative d/dy."""
        return np.real(np.fft.ifft2(1j * self.KY * np.fft.fft2(f)))

    def grad(self, f: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Gradient of a scalar field, returned as ``(df/dx, df/dy)``."""
        fhat = np.fft.fft2(f)
        gx = np.real(np.fft.ifft2(1j * self.KX * fhat))
        gy = np.real(np.fft.ifft2(1j * self.KY * fhat))
        return gx, gy

    def div(self, fx: np.ndarray, fy: np.ndarray) -> np.ndarray:
        """Divergence of a vector field: d(fx)/dx + d(fy)/dy."""
        return self.ddx(fx) + self.ddy(fy)

    def curl(self, fx: np.ndarray, fy: np.ndarray) -> np.ndarray:
        """Scalar (out-of-plane) curl of a 2D vector field: d(fy)/dx - d(fx)/dy.

        This is the vorticity when applied to a velocity field, and the circulation
        source when applied to a force field (the ``curl f_pow`` term of eq. 6).
        """
        return self.ddx(fy) - self.ddy(fx)

    def laplacian(self, f: np.ndarray) -> np.ndarray:
        """Laplacian of a scalar field."""
        return np.real(np.fft.ifft2(-self.K2 * np.fft.fft2(f)))

    # -- inverse Laplacian ------------------------------------------------------

    def solve_poisson(self, rhs: np.ndarray) -> np.ndarray:
        """Solve the periodic Poisson equation ``laplacian(phi) = rhs`` for ``phi``.

        The solution is fixed to zero mean (the only ambiguity on a periodic domain).
        The mean of ``rhs`` is discarded, as required for solvability.
        """
        phihat = -np.fft.fft2(rhs) * self._K2_inv
        return np.real(np.fft.ifft2(phihat))

    # -- helpers ---------------------------------------------------------------

    def cell_area(self) -> float:
        return self.dx * self.dy

    def zero(self) -> np.ndarray:
        """An all-zeros scalar field of the right shape."""
        return np.zeros((self.nx, self.ny))
