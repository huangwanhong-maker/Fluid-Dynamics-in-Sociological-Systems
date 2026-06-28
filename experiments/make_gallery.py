"""Run the entire figure gallery: every formal step of the model, in order.

Run:  PYTHONPATH=. python experiments/make_gallery.py
Figures are written to assets/.
"""

from __future__ import annotations

import importlib

STAGES = [
    # Part 1 -- the dynamics / formalism
    ("Stage I   -- fluid model", "stage1_fluid"),
    ("Stage I   -- Proposition 2.1", "prop_2_1"),
    ("Stage I   -- flow demo", "flow_demo"),
    ("Stage II  -- relational field", "stage2_field"),
    ("Stage II/III -- non-commutativity", "stage3_nonabelian"),
    ("Stage III -- braid statistics", "stage4_braid"),
    ("Stage IV/V -- skeleton/flesh, relational base", "stage5_limits"),
    ("Stage VI  -- operationalization", "stage6_ethics"),
    # Part 2 -- the ethics model
    ("Ethics e1-e3 -- criterion, power geometry, trilemma", "ethics_criterion"),
    ("Ethics e4    -- solidification", "ethics_solidification"),
    ("Ethics e5-e6 -- deliberation attractors, genuine/forged", "ethics_deliberation"),
    ("Ethics e7-e8 -- illness, intimate trolley", "ethics_cases"),
]


def main():
    for title, module_name in STAGES:
        print(f"\n{'='*70}\n{title}\n{'='*70}")
        module = importlib.import_module(module_name)
        module.main()
    print(f"\n{'='*70}\nGallery complete -- see assets/.\n{'='*70}")


if __name__ == "__main__":
    main()
