# Figure Gallery

One visualization per formal step of the model, each backed by real computation. Regenerate
the whole set with:

```bash
PYTHONPATH=. python experiments/make_gallery.py     # all figures -> assets/
```

or run any single stage script in `experiments/`. Every figure obeys the model's own limits:
only the **sign, order, and non-commutativity** of a holonomy are ever reported, never an
absolute magnitude (paper §4.5, §10.1).

---

## Stage I — the fluid model (§2)

| Figure | Step | What it shows (computed) |
|--------|------|--------------------------|
| ![](assets/01_continuity_source.png) | continuity with a source (eq. 1) | value stock grows from a source — **not conserved** (total 0.33 → 1.32) |
| ![](assets/02_power_history.png) | power = flux history (eq. 3) | power field accumulates where value flowed; α-dominant **remembers**, β-dominant **forgets** |
| ![](assets/03_vorticity_holonomy.png) | vorticity & holonomy (eqs. 4–5) | holonomy measured around three relational loops; signs +/+/− match enclosed circulation |
| ![](assets/04_proposition_2_1.png) | **Proposition 2.1** | appropriation contributes **+3.3e-12** to the holonomy; generation **−0.74** — appropriation is curl-free |
| ![](assets/05_helmholtz_power.png) | dominance vs generative (Remark 2.1) | unique Helmholtz split: dominance (gradient, curl ≈ 1.7e-13) vs generative (solenoidal, curl 4.75) |
| ![](assets/flow_demo.png) | the flow runs | 2D decaying turbulence; enstrophy decays smoothly (viscous solidification) |

## Stage II — the relational field (§4)

| Figure | Step | What it shows |
|--------|------|---------------|
| ![](assets/06_symmetry_breaking.png) | breaking G→H (eq. 7) | Mexican-hat potential with vacuum manifold **M = G/H ≅ S¹**; a realized broken state |
| ![](assets/07_defects_winding.png) | subjects as defects (eq. 9) | 4 placed defects, 4 detected, charges [−1,−1,+1,+1] — **π₁(S¹)=ℤ**, integer winding |
| ![](assets/08_abelian_holonomy.png) | abelian holonomy (eq. 10) | enclosing-loop winding **+1.000**, avoiding-loop **0.000**; holonomy builds over the whole loop |

## Stage II/III — power as non-commutativity (eq. 11)

| Figure | Step | What it shows |
|--------|------|---------------|
| ![](assets/09_noncommutativity.png) | abelian vs non-abelian | Bloch sphere: abelian endpoint gap **1.7e-16** (order irrelevant) vs non-abelian **1.58** (order matters = power) |

## Stage III — braid statistics (§4.7–6)

| Figure | Step | What it shows |
|--------|------|---------------|
| ![](assets/10_braid_relation.png) | braid generators & Yang-Baxter (eq. 15) | σ₁σ₂σ₁ = σ₂σ₁σ₂ as isotopic braid diagrams; residual **3e-16** for both reps |
| ![](assets/11_three_demands.png) | the three non-abelian demands (§5.3) | power (commutator 1.80), resonance (dim Hₙ = Fibonacci), generativity (τ×τ = 1+τ) |
| ![](assets/12_universality_discrimination.png) | **Proposition 6.1** | Ising = **6 discrete** reachable holonomies (discriminates) vs Fibonacci = **dense** (cannot) |

## Stage IV / V — the protected remainder and the relational base (§7, §9)

| Figure | Step | What it shows |
|--------|------|---------------|
| ![](assets/16_skeleton_flesh.png) | skeleton vs flesh (§7) | under perturbation: holonomy winding **invariant** (+1→+1, skeleton); local detail re-written (flesh, 0.34 rad) |
| ![](assets/17_group_field_base.png) | the relational base (§9) | D₄ Cayley graph as configuration space; field Φ winds once; **r·s ≠ s·r** = power in the base |

## Stage VI — operationalization & the educational case study (§10)

| Figure | Step | What it shows |
|--------|------|---------------|
| ![](assets/13_state_vectors.png) | state vectors (eq. 24) | (autonomy, dependence, generative output) trajectories per cohort |
| ![](assets/14_power_geometry.png) | the geometry of power | the (C, Θ) plane: both cohorts have power C>0, split into power-to (Θ>0) vs power-over (Θ<0) |
| ![](assets/15_education_case_study.png) | **falsifiable prediction** (§10.5) | Θ **separates** cohorts (gap 0.98) while exam scores **overlap** (gap 2.5) — model supported |

---

# Part 2 — The Ethics Model

The same dynamics read in a normative register (see the README's *Part 2* section for the concept
mapping). One figure per claim.

| Figure | Step | What it shows |
|--------|------|---------------|
| ![](assets/e1_good_bad_criterion.png) | good/bad criterion | the **sign** of a cycle's holonomy: generative (Θ=+0.90), appropriative (Θ=0), dominative (Θ=−0.54) |
| ![](assets/e2_power_to_over.png) | power-to vs power-over | same power (C=0.8), opposite surplus sign; power-to decays toward its own dissolution |
| ![](assets/e3_trilemma.png) | the trilemma (Prop. 4.1) | power and generativity **co-originate** — the curves coincide; "generative yet powerless" is empty |
| ![](assets/e4_solidification.png) | solidification (§5.3) | α-dominant power = historical drag → vorticity collapses to **1%** (the bad cycle as a process) |
| ![](assets/e5_attractors.png) | deliberative attractors | fixed point vs limit cycle vs **holonomic spiral** (config returns, value climbs) |
| ![](assets/e6_genuine_forged.png) | genuine vs forged | sign of the holonomy on the deliberative loop: value **returned** (+0.30) vs **extracted** (−0.18) |
| ![](assets/e7_illness_authorship.png) | illness | authorship distributed across the care relation; the holonomy sign judges genuine vs forged care |
| ![](assets/e8_intimate_trolley.png) | the intimate trolley | the beloved is off the aggregation axis — non-substitutable; aggregation breaks down |

---

# Part 3 — Case Study: Quantitative Ethics in Real Classrooms

The instrument applied to the **TalkMoves corpus** (169 real K-12 math lessons, grades 3–12;
Suresh et al., LREC 2022). Fetch with `python experiments/fetch_talkmoves.py`, then
`python experiments/edu_casestudy.py`.

| Figure | Step | What it shows (from real data) |
|--------|------|--------------------------------|
| ![](assets/edu1_transcript.png) | the raw data | one lesson as a turn sequence of talk moves (teacher/student × Passive/Controlling/Generative) |
| ![](assets/edu2_state_vector.png) | state vector (a,d,g) | two real lessons at the extremes: Θ=+0.96 (generative) vs Θ=−1.00 (dominative) |
| ![](assets/edu3_transition_operators.png) | transition operators | `T_ts`, `T_st`, the holonomy, and the commutator (power 𝒞=1.59 for this lesson) |
| ![](assets/edu4_power_geometry.png) | **ethics in education** | the (𝒞, Θ) plane over 169 lessons: mean 𝒞≈0.82, Θ>0 in 48% — power-to vs power-over |
| ![](assets/edu5_genuine_forged.png) | **ethics education** | teacher uptake (mean 0.20, 8% genuine); corr(uptake, autonomy)=+0.25 |
| ![](assets/edu6_synthesis.png) | synthesis | the quantities by grade; the Θ distribution (symmetric around 0) |

---

### Module map

| Module | Provides |
|--------|----------|
| `fluid_socio/grid.py` | periodic 2D grid, spectral operators |
| `fluid_socio/operators.py` | Helmholtz decomposition, holonomy diagnostics |
| `fluid_socio/fluid.py` | value/power flow (vorticity–streamfunction) |
| `fluid_socio/field.py` | order-parameter field, topological defects, U(1) holonomy |
| `fluid_socio/nonabelian.py` | SU(2) path-ordered holonomy, non-commutativity, Bloch sphere |
| `fluid_socio/braid.py` | braid representations (Ising, Fibonacci), Yang-Baxter, reachable sets |
| `fluid_socio/ethics.py` | §10 operationalization: state vectors, transition operators, Θ, C |
| `fluid_socio/deliberation.py` | deliberation dynamics: the three attractors, holonomy on the deliberative loop |
| `fluid_socio/education.py` | Part 3: ingest TalkMoves transcripts → (a,d,g), transition operators, Θ, 𝒞, uptake |
