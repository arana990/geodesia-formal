"""What the manuscript claims about the CAS is still true, checked every day.

⚠️ **IN-PROCESS sibling of `test_experimentos_self_check.py`, and it exists by measurement.**
That one runs the `_self_check()`s in subprocesses and is entirely marked `slow`: 16
interpreters importing `numpy`/`sympy`/`matplotlib` next to 10 `xdist` workers took the
fast loop from `~100 s` to `4m44`, with two blowing up on timeout. Here the module is
imported, with no subprocess and no file written, and the cost drops to a few
simplifications.

⚠️ **Why THIS one and not the others:** the manuscript (`draft3.md`) claims things only
this experiment supports: *"decides three of the five"*, *"the invariance too"*, *"accepts
the implicit form that was refused"*. If `sympy` changes behaviour in a future version the
manuscript starts claiming what is no longer true, and it is in the daily loop that this
has to show.
"""
from __future__ import annotations

import cas_versus_lean as cas  # in mapgravy: mapgravy.experiments.cas_versus_lean


def test_the_CAS_decides_the_three_rational_relations():
    """The half of the reviewer's objection that HOLDS, and which the manuscript concedes."""
    assert cas.r1_helmert_separation(), "the Helmert separation should be decided"
    assert cas.r2_rigid_limit(), "the rigid limit should be decided"
    value, invariance = cas.r3_asymptotic_ratio()
    assert value, "the value of the asymptotic ratio should be decided"
    assert invariance, "the INVARIANCE too: g and mu drop out of the simplified ratio"


def test_the_CAS_accepts_the_hypothesis_the_proof_system_REFUSED():
    """The half that does NOT hold, and which is the manuscript's argument.

    A CAS computes with whatever is written to it: it accepts the implicit form
    `H = C/ḡ(H)` and returns two roots without saying which one is the physics, and it
    accepts a WRONG hypothesis returning three. It is the distinction this paper is about,
    applied to the tool.
    """
    r = cas.ill_posed_hypothesis_passes_the_cas()
    assert r["roots_of_the_implicit"] == 2, r
    assert r["roots_of_the_wrong"] == 3, r


def test_the_vacuity_at_n_zero_is_NOT_the_proof_systems():
    """⚠️ The example against us, and therefore the most important one to lock.

    The manuscript says the statement at `n = 0` closes without asserting anything **in
    both tools**. If one day this stopped holding in `sympy`, the paper's sentence would
    be choosing the convenient example, and nobody would notice.
    """
    assert cas.degree_zero_in_the_cas() == 1


def test_the_two_relations_out_of_reach_are_declared():
    assert len(cas.OUT_OF_REACH) == 2, cas.OUT_OF_REACH
