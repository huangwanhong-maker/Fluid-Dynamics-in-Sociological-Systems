# Model Notes — Fluid Dynamics in Sociological Systems

Working notes distilled from the two source papers, organized for implementation as a
Python project. Each formula is tagged with its **epistemic status** as the author defines it:

- **stipulation** — a modeling choice (could have been made otherwise)
- **theorem** — a mathematical fact, true independent of interpretation
- **interpretation** — a philosophical identification the formalism cannot establish
- **argument-from-adequacy** — conditional: *if* feature X is to be representable, *then* property P
- **open** — explicitly out of scope / unfinished

Sources:
- `papers/fluid_to_braid-v2.pdf` — Huang, *From Fluid to Braid* (the model)
- `papers/authorship_without_equilibrium.pdf` — Huang, *Authorship Without Equilibrium* (case study)

---

## 0. The one-sentence core

Genuine relational value is **non-possessive**: it is the **holonomy** (path-dependent residue) of
a closed relational loop, not a stock held at a point. The appropriative / gradient / scalar-reducible
part of any flow is curl-free and contributes **zero** to circulation. Power is the **non-commutativity**
of that holonomy. Everything else is built to make these two claims precise and falsifiable.

---

## 1. Stage I — The fluid model (paper 1, §2)

Status of the whole stage: *entry point and a failed first foundation*, but **reinstated** at the
dynamical layer (§5) as the language of flow, and kept throughout for its one theorem (Prop 2.1).

Domain Ω ⊆ ℝ^d, value density ρ(x,t) ≥ 0, value velocity u(x,t) (velocity is primary, not density).

| # | Equation | Status | Implementation hook |
|---|----------|--------|---------------------|
| (1) | ∂_t ρ + ∇·(ρu) = S(ρ,ψ) | stipulation | continuity w/ source; S≠0 is the departure from real fluid dynamics |
| (2) | ∂_t u + (u·∇)u = −∇P(ρ) + ν∇²u + f_pow | stipulation | momentum: appropriation (−∇P), inertia/drag (ν∇²u), power force (f_pow) |
| (3) | ∂_t p = αJ − βp, J = ρu, f_pow = f(p) | stipulation | power = history of value flux; α/β = solidification order parameter |
| (4) | ω := ∇×u | definition | value vorticity |
| (5) | hol(γ) := ∮_γ u·dℓ = ∫_Σ ω·dA | definition | net value generated traversing loop γ once |

**Reading of the terms:**
- −∇P = **appropriative drive** (value flows downhill, dense→sparse; gradient of a scalar by construction)
- ν∇²u = **relational inertia / historical drag**; ν is the *solidification parameter* (large ν → laminar/frozen, small ν → turbulent/generative)
- f_pow = **power force**, coupling channel between value and power
- α dominates → positive feedback locks flow into frozen appropriative channel; β dominates → system keeps flowing

### Proposition 2.1 (Appropriation is irrotational) — THE central theorem

Taking curl of (2), ∇×∇P = 0 annihilates the pressure term:

    (6)  ∂_t ω + (u·∇)ω = (ω·∇)u + ν∇²ω + ∇×f_pow

- Pressure gradient is **absent**. A purely appropriative flow u = −∇φ has ω = 0 and **hol(γ) = 0** for every contractible loop. **(theorem)**
- Circulation can arise only from: (a) **vortex stretching** (ω·∇)u — a generative cycle amplifying itself, or (b) **curl of power** ∇×f_pow — asymmetry not reducible to a scalar.
- **Interpretive premise** that makes it bite: appropriation = the part of the force derivable from a scalar potential. Granting that, *whatever reduces to a single scalar comparison cannot by itself generate value around a closed loop* (accumulation, ranking, priced exchange are all scalar-reducible).

**Remark 2.1** — Helmholtz-decompose f_pow: **gradient part** = strict dominance hierarchy (irrotational, generates nothing) vs **solenoidal part** = generative power. Dominating vs generative power = gradient vs solenoidal under a unique Helmholtz decomposition (given BCs).

**→ First buildable result:** integrate (1)–(3) on a grid, confirm numerically that adding any pure-gradient
force leaves ∮ u·dℓ unchanged, and that only ∇×f_pow or vortex stretching moves the holonomy.

---

## 2. Stage II — The relational field (paper 1, §4)

The real foundation. Order of construction matters (do **not** start from braid group or from a chosen M).

```
G  --symmetry breaking (given, NOT explained: open)-->  H
M = G/H                                  (order-parameter space, derived)
subjects = defects, types π_k(G/H)       (identity topological, not substantial; derived)
surplus = holonomy P exp ∮_γ A           (theorem + interpretation; stock = local Φ(x))
power = noncommutativity of holonomy     (arises iff residual H is non-abelian)
braid statistics π_1(C_n(Σ)) = B_n(Σ)    (theorem + representation)
dynamical layer: fluid flow reinstated   (Stage I in its proper role)
```

- (7) **M = G/H** — order-parameter space generated, not posited
- (8) Φ: Σ → M = G/H — broken-state field (Σ = relational connectivity, NOT assumed a fixed/2D space)
- (9) **defect types = π_k(G/H)** — standard topological defect classification
  - example: G/H ≃ S¹ ⇒ π_1(S¹) = ℤ ⇒ subjects = integer winding (no-self / Lacanian structural subject)
- (10) **hol(γ) = P exp ∮_γ A** — surplus = path-ordered holonomy of canonical connection A on the H-bundle G→G/H
  - **two levels, do not conflate:** value **stock** = Φ(x) (local, appropriable) vs **surplus** = hol(γ) (non-local, only non-possessive circulation generates it)
  - structural template = Marxian circuit M−C−M′, ΔM = the holonomy
- (11) **H abelian ⇒ hol commutes (no power); H non-abelian ⇒ hol(γ₁)hol(γ₂) ≠ hol(γ₂)hol(γ₁)** — power = non-commutativity

**Surplus=holonomy** constrained on 3 sides (interpretation, not free metaphor): forced by Prop 2.1; has surplus-not-stock character (path-dependent, present nowhere); continuous with geometric-phase usage.

**Power=non-commutativity**: "order of acts changes outcome" *is* non-commutativity; right ontological grain (exercised not owned — Foucault).

### Proposition 4.1 (Power–generativity co-origination)
Power, resonance-without-fusion, generativity = **three faces of one condition: H non-abelian**.
- **Trilemma:** of {(i) subjects+generativity, (ii) no power, (iii) not collapsing to void} — no two co-exist with the third.
- **Justice** = shaping the geometry of *ineliminable* asymmetry so surplus is **returned not retained** (power-to vs power-over), NOT abolishing power. Power abolition = generativity abolition = "equality of the void."

### Defect statistics (§4.7)
- (12) C_n(Σ) = (Σⁿ \ Δ)/S_n — config space of n indistinguishable defects
- (13) **π_1(C_n(Σ)) = B_n(Σ)** — braid group **computed, not posited** (theorem). 2D is sufficient not necessary for non-abelian statistics.
- (14)(15) braid relations: σ_iσ_j = σ_jσ_i (|i−j|≥2); **σ_iσ_{i+1}σ_i = σ_{i+1}σ_iσ_{i+1}** (Yang–Baxter, the nontrivial content)
- (16) fusion rule **a⊗b = ⊕_c N^c_{ab} c** (categorification for variable subject-number; braided/modular tensor category)

### Open dynamical layer (§4.9)
Action L[Φ], defect creation rates, emergent background Σ = **open programme**. Kinematics in hand; dynamics not.

### Subjects/types limit (§4.10) → resolved in Stage IV
Homotopy class fixes **type** not **token**. Same-charge defects interchangeable in topological data. Token identity (haecceity, irreplaceability of the beloved) ⇒ lives in the **flesh** (§7), not the skeleton.

---

## 3. Stage III — Braid representation (paper 1, §5.3–§6)

- ϱ: B_n → U(H_n), good/bad criterion carried by **ϱ(b)**. H_n = fusion space; braiding ϱ(σ_i) = two meaning-worlds resonating.
- **Three non-abelian demands** (arguments-from-adequacy, premises P/R/G stated explicitly):
  - **Prop 5.1 (power):** premise P (order = causal credit asymmetry) ⇒ ϱ(σ_iσ_j) ≠ ϱ(σ_jσ_i)
  - **Prop 5.2 (resonance-without-fusion):** premise R (coupling neither juxtaposes nor merges) ⇒ dim H_n > 1
  - **Prop 5.3 (generativity):** premise G (outcome not fixed by relata) ⇒ Σ_c N^c_{ab} > 1 (multi-channel fusion)
  - These three = the three defining marks of **non-abelian anyonic statistics**, recovered one-to-one.

### Proposition 6.1 (Universality precludes robust discrimination) — the self-limit
- Def 6.1: {ϱ_n} **universal** if ϱ_n(B_n) dense in PU(H_n). Predicate Φ **holonomy-factoring** if Φ(b)=Φ̂(ϱ(b)); **robust** if decision boundary stable (constant on δ-balls).
- **Prop 6.1 (theorem):** universal ⇒ no holonomy-factoring predicate has both nontrivial content AND robust discrimination. *Omnipotence and normative judgment are inversely related.*
- **Required object: non-abelian YET non-universal.** Band is non-empty (finite non-abelian quotients; Jones reps at non-universal roots of unity). Whether the band carries a *normatively interpretable* robust invariant = **central open problem** (marked, not claimed).

---

## 4. Stage III′ — Dynamical layer (paper 1, §5): fluid reinstated

On the **generated** space G/H (not an assumed stage). Same equations as Stage I:

    (17)  ∂_t ρ + ∇·(ρu) = S
    (18)  ∂_t ω + (u·∇)ω = (ω·∇)u + ν∇²ω + ∇×f(p)
    (19)  ∂_t p = αρu − βp,   ω = ∇×u

Three couplings that lock this layer to generation:
1. **S** = defect creation/annihilation rate (imported from §4.6, no longer a hand-patch)
2. circulation ω = time-resolved version of holonomy (10)
3. **Prop 2.1 lives here** — founding theorem of the flow

**Solidification (§5.3):** α/β controls whether power forgets (β dominant, flow maintained) or accumulates (α dominant, frozen). Solidification = collapse of generative cycle to a fixed point where ω→0, surplus→0 = dynamical face of the bad cycle. Justice has a dynamical reading: **keep the system away from the solidified fixed point.**

---

## 5. Stage IV — Skeleton & flesh (paper 1, §7)

    value = topological skeleton  +  local flesh
            [ϱ(b), type,            [token identity,
             normative criterion]    singular detail]

Topological protection = chief virtue (good/bad insensitive to accident) AND chief danger (would call singular detail "noise"). Three things the braid layer cannot see, all living **below the fixed-sector shadow**: token identity, subject-number, emergent background. **Remark 7.1 (conjecture):** the good = appropriate *proportion* of skeleton and flesh. Holonomy criterion is necessary, not sufficient.

---

## 6. Stage V — Aggressive limit: relational base (paper 1, §9)

Make Σ itself relational: Σ = Γ (a group; pure relation, Cayley's theorem). Group field theory.
- (20) Φ: Γ → M
- (21) defect = w(γ) = [Φ|_γ] ∈ π_1(M), w(γ)≠0 (winding on Cayley-graph loops)
- (22) **S[Φ] = Σ_γ V(Φ(γ)) + λ Σ_{γ,γ′} K(γ⁻¹γ′) Φ(γ)Φ(γ′)** — coupling refers only to relative relation γ⁻¹γ′, never an external position. Power = γγ′ ≠ γ′γ.
- **Three walls (all open):** (1) a group is *already-closed* (single-channel determinism) vs generativity → repair toward groupoid/category; (2) regress of the base (where does Γ / G come from); (3) group field theory itself unfinished. Presented as **toy model**, not demonstration.

---

## 7. Stage VI — Operationalization (paper 1, §10) ★ PRIMARY BUILD TARGET

Respects §4.5: **magnitude of holonomy is NOT measurable** (no empirical scale). Only **sign, order, non-commutativity** are scale-invariant and measurable.

**Discretization:** nodes = individuals (students, teachers); state vector s_i(t); connection → state-transition operator T_{i→j} along each edge.

    (23)  Ĥ(γ) = T_{i→j} T_{j→i}      — holonomy as ordered product of transitions around a cycle (estimable matrix)
    (24)  s_i(t) = (a_i(t), d_i(t), g_i(t))
            a = autonomy           (rate of self-initiated questions/tasks; self-initiated/assigned ratio in LMS logs)
            d = dependence         (fraction of tasks needing intervention; perf drop when scaffolding removed)
            g = generative output  (rate of new non-reproductive content; rubric-coded vs reproductive)

**Three computed quantities:**

    (25)  Θ(γ) = (a_i(t₂) − a_i(t₁)) − (d_i(t₂) − d_i(t₁))     — SIGN of holonomy
            Θ > 0  → positive holonomy = generative power = power-to = good cycle
            Θ ≈ 0  → zero holonomy = appropriative / pure-gradient = no surplus
            Θ < 0  → negative holonomy = power-over = bad cycle

    (26)  C = || T_{i→j}T_{j→i} − T_{j→i}T_{i→j} ||            — STRENGTH of power (non-commutativity)
            C ≈ 0 → near-symmetric (weak power, peer learning)
            C large → strongly asymmetric

    surplus vs stock: stock = testable countable knowledge (exam scores); surplus = non-attributable part of g and Θ.
            Prediction: stock-optimizing system (test prep) shows systematically low Θ even at high stock.

**Case study (§10.5):** two cohorts, lecture-drill vs inquiry-based, sample (a,d,g) fortnightly, estimate T from time-coded interaction.
- **Prediction (issued before data):** inquiry cohort Θ>0 trajectory (dependence ↓, autonomy ↑); lecture-drill Θ≤0; comparable exam scores (stock) but diverging Θ + transfer (surplus).
- **Verdict rule:** Θ trajectories diverge as predicted AND independent of exam score ⇒ supported. Θ covaries fully with exam score, or inquiry Θ not higher ⇒ falsified.

**Limits (§10.6):** T estimation needs lots of data; (a,d,g) construct validity must be established; Θ is first-order proxy for sign; causal identification needs controlled design; G,H↔real-situation correspondence has no canonical form.

---

## 8. Case study paper — Authorship Without Equilibrium (paper 2)

Applies the **holonomy criterion qualitatively** to Mazouz's deliberative justice. Not yet computational.

- **Setup:** fibre bundle. Base = space of judgement configurations (questions the affected return to). Fibre = space of value produced there. Deliberation = closed loop in base.
- **Three candidate attractors:**
  - *fixed point* = reflective equilibrium (settledness = success; ends authorship) ✗
  - *limit cycle* = bare repetition (returns to same place, nothing gained) ✗
  - **holonomic spiral** = config returns, value does not — non-trivial holonomy accumulated per circuit ✓
- **Claim 5.1 (genuine vs forged):** genuine = positive holonomy (value returned to participants who generate it); forged = zero/negative (appearance of deliberation maintained while value net-extracted; affected used as **fuel**).
- **Two orthogonal criteria, both required:** dynamical (does the cycle generate? positive holonomy) AND justice (is anyone used as fuel?). Positive holonomy is necessary, not sufficient.
- **Test cases:** illness (authorship was always distributed across the care relation, never solitary; illness makes visible what was already true) and intimate trolley (aggregation breaks down: the beloved is non-substitutable, not a countable unit; relational subject is *on* the track).
- **Structural claims linking to paper 1:** relational (not solitary) self-legislation; external legislator was always redundant; "relational divinity" = self-grounding of the relational subject (deflationary, structural). Maps to paper 1's: non-possessive holonomy, power-to vs power-over, skeleton (type) vs flesh (non-substitutable token).

**Bridge to compute:** the same Ĥ(γ)=T·T discretization (eqs 23–26) can in principle make "genuine vs forged deliberation" computable on a toy relational model — the paper does this only philosophically.

---

## 9. Implementation priorities (for the Python project)

1. **Fluid simulator** (`Stage I/III′`, eqs 1–6, 17–19): grid integrator; numerically demonstrate Prop 2.1 and the α/β solidification phase transition. Most self-contained, highest "shows the core" value.
2. **Holonomy operationalization** (`Stage VI`, eqs 23–26): the falsifiable bridge. State vectors (a,d,g), transition-operator estimation, Θ / C / surplus, lecture-drill vs inquiry on synthetic data.
3. **Authorship case study** (paper 2): genuine-vs-forged on a toy relational model, reusing the eq-23–26 machinery.
4. **Braid/defect layer** (`Stage II/III`): non-abelian non-universal representations; verify the admissible band (Prop 6.1). Most abstract.

### Invariants the code must respect (from the papers' own limits)
- **Never report an absolute holonomy magnitude** — only sign / order / non-commutativity are meaningful (§4.5, §10.1).
- Keep **stock (Φ, local) and surplus (holonomy, non-local) strictly separate** — they live at different levels.
- Mark every output with its epistemic status; do not let a theorem's exactness leak into an interpretive claim.
- A pure-gradient force MUST leave the holonomy invariant (Prop 2.1) — this is a built-in unit test.
