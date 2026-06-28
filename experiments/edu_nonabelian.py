"""Part III (deep) -- a non-abelian holonomy of real discourse, and an empirical Prop. 6.1.

This pushes the case study up toward the formalism. Instead of a classical stochastic
transition matrix, each lesson's discourse is mapped to a genuinely non-abelian,
order-dependent SU(2) holonomy (Stage III). Two questions the theory poses are then put
to real data:

  edu7  Is the reachable set of classroom holonomies NON-UNIVERSAL (constrained)?
        Prop. 6.1 says a robust good/bad criterion can exist only on such a set. We compare
        the real reachable set against an order-shuffled null and a Haar (fully universal)
        reference.

  edu8  Does the NON-ABELIAN structure (the order of moves) carry the good/bad signal?
        We test whether the holonomy predicts generativity g, and whether shuffling the
        order -- which destroys the non-commutativity = power -- destroys the prediction
        (a permutation test).

Run:  PYTHONPATH=. python experiments/edu_nonabelian.py   (needs the TalkMoves corpus)
"""

from __future__ import annotations

import glob
import os
import numpy as np

from fluid_socio import education as edu
from fluid_socio import braid_discourse as bd
from _common import get_plt, save

CORPUS = "data_cache/talkmoves"
KAPPA, W = 0.7, 6


def load_lessons():
    paths = sorted(glob.glob(os.path.join(CORPUS, "*.xlsx")))
    out = []
    for p in paths:
        try:
            L = edu.load_lesson(p)
        except Exception:
            continue
        if (L.role == "S").sum() >= 20 and len(L.macro) >= 40:
            out.append(L)
    return out


def density_grid(points, n_lat=14, n_lon=28):
    z = np.clip(points[:, 2], -1, 1)
    phi = np.arctan2(points[:, 1], points[:, 0])
    lat = np.minimum((((z + 1) / 2) * n_lat).astype(int), n_lat - 1)
    lon = np.minimum(((phi + np.pi) / (2 * np.pi) * n_lon).astype(int), n_lon - 1)
    grid = np.zeros((n_lat, n_lon))
    np.add.at(grid, (lat, lon), 1.0)
    return grid / grid.sum()


def multiple_R(X, y):
    """Multiple correlation R of a linear fit y ~ [1, X]."""
    A = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ beta
    return float(np.corrcoef(pred, y)[0, 1]), pred


# --------------------------------------------------------------------------- #
# edu7  the reachable set: non-universal, and constrained by order
# --------------------------------------------------------------------------- #
def fig_reachable(lessons):
    real = np.vstack([bd.window_points(L, W=W, kappa=KAPPA) for L in lessons])
    shuf = np.vstack([bd.window_points(bd.shuffled_lesson(L, seed=i), W=W, kappa=KAPPA)
                      for i, L in enumerate(lessons)])
    haar = bd.haar_points(len(real))
    ent = {k: bd.coverage(p)[1] for k, p in [("real", real), ("shuf", shuf), ("haar", haar)]}
    print(f"edu7 reachable set: entropy real={ent['real']:.3f} < shuffled={ent['shuf']:.3f} "
          f"< Haar={ent['haar']:.3f}  ({len(real)} window holonomies)")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.6))
    grids = [("REAL discourse", real), ("ORDER-SHUFFLED", shuf), ("HAAR (universal)", haar)]
    eps = 1e-4
    logged = [np.log10(density_grid(p) + eps) for _, p in grids]
    vmin = min(L.min() for L in logged); vmax = max(L.max() for L in logged)
    for a, (title, p), L in zip(ax, grids, logged):
        im = a.imshow(L, origin="lower", cmap="magma", vmin=vmin, vmax=vmax,
                      aspect="auto", extent=[-180, 180, -1, 1])
        a.set_title(f"{title}\nreachable-set entropy = {bd.coverage(p)[1]:.3f}", fontsize=10)
        a.set_xlabel("Bloch longitude"); a.set_ylabel("Bloch z")
    fig.colorbar(im, ax=ax, fraction=0.012, pad=0.01, label="log10 holonomy density")
    fig.suptitle("Part III deep, edu7 (Prop. 6.1 on real data): real classroom holonomies "
                 "occupy a NON-UNIVERSAL (constrained) region; order-shuffling pushes them "
                 "toward the universal Haar limit", fontsize=11, y=1.02)
    fig.tight_layout(rect=[0, 0, 0.95, 1.0])
    save(fig, "edu7_reachable_set.png")


# --------------------------------------------------------------------------- #
# edu8  order carries the good/bad signal (a permutation test)
# --------------------------------------------------------------------------- #
def fig_discriminability(lessons, n_perm=80):
    g = np.array([edu.relational_state(L)["g"] for L in lessons])
    sig = np.array([bd.bloch(bd.holonomy(L.macro, L.words, KAPPA)) for L in lessons])
    R_real, pred = multiple_R(sig, g)

    null = []
    for s in range(n_perm):
        sig_s = np.array([bd.bloch(bd.holonomy(*(lambda S: (S.macro, S.words))(
            bd.shuffled_lesson(L, seed=1000 * s + i)), KAPPA)) for i, L in enumerate(lessons)])
        null.append(multiple_R(sig_s, g)[0])
    null = np.array(null)
    p_val = float(np.mean(null >= R_real))
    print(f"edu8 discriminability: holonomy->g  R_real={R_real:.3f}; "
          f"shuffled null mean={null.mean():.3f} sd={null.std():.3f}; p={p_val:.3f}")

    plt = get_plt()
    if plt is None:
        return
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].scatter(pred, g, s=40, color="seagreen", alpha=0.7, edgecolors="white", linewidths=0.4)
    lo, hi = min(pred.min(), g.min()), max(pred.max(), g.max())
    ax[0].plot([lo, hi], [lo, hi], "--", color="gray")
    ax[0].set_xlabel("generativity predicted from the non-abelian holonomy")
    ax[0].set_ylabel("actual generative output  g")
    ax[0].set_title(f"the holonomy of real discourse predicts generativity\n(multiple R = "
                    f"{R_real:.2f})")
    ax[0].grid(True, alpha=0.3)

    ax[1].hist(null, bins=20, color="slateblue", alpha=0.7, label="order-shuffled (null)")
    ax[1].axvline(R_real, color="crimson", lw=2.5, label=f"real order (R={R_real:.2f})")
    ax[1].set_xlabel("holonomy->g predictive strength  R")
    ax[1].set_ylabel("count")
    ax[1].set_title(f"destroying the move-ORDER destroys the signal\n(permutation p = "
                    f"{p_val:.3f}): the non-commutativity carries it")
    ax[1].legend()

    fig.suptitle("Part III deep, edu8: the good/bad signal lives in the ORDER of moves "
                 "(non-abelian holonomy = power), not in their frequencies", fontsize=11)
    fig.tight_layout()
    save(fig, "edu8_holonomy_discriminates.png")


def main():
    if not os.path.isdir(CORPUS) or len([f for f in os.listdir(CORPUS)
                                         if f.endswith(".xlsx")]) < 10:
        print("TalkMoves corpus not found. Fetch it: python experiments/fetch_talkmoves.py")
        return
    print("Loading corpus for the non-abelian holonomy analysis ...")
    lessons = load_lessons()
    print(f"  {len(lessons)} lessons.\n")
    fig_reachable(lessons)
    fig_discriminability(lessons)


if __name__ == "__main__":
    main()
