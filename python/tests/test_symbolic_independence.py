"""Gates on the independence grader for two routes.

⚠️ What these gates protect is the GRADER, not the reading of the papers. The translation
of each paper into symbols is ours and is cited in the experiment; if it is wrong, the
verdict comes out wrong and nothing here fails (§0.3c #2).
"""

from __future__ import annotations

import re

import sympy as sp

from symbolic_independence import (  # in mapgravy: mapgravy.experiments.symbolic_independence
    CASES,
    UNDETERMINED,
    OWN_DATA,
    IDENTITY,
    OWN,
    SHARED_ONLY,
    Case,
    gamma,
    grade,
    h,
    zeta_mod,
    Hn,
)


def test_every_published_case_receives_the_class_the_manuscript_asserts():
    for case in CASES:
        cls, diff, _ = grade(case)
        assert cls == case.expected, (case.key, cls, case.expected, diff)


def test_NO_published_case_is_a_strict_identity():
    """BITES: declaring one of the three an identity fails, and the reason is an error of ours.

    ⚠️⚠️ **Until 2026-09-15 this gate demanded the opposite**: that there be exactly one
    case of class `IDENTITY`, that of `@tocho2024argentina`. An adversarial review showed
    that the translation of that case into symbols **assumed the conclusion**: it wrote
    the two routes as two rearrangements of the same expression, instead of reading them
    as the source publishes them. Reading Eq. (9) and Eq. (12) as they stand, the
    difference is the linearisation error `(dγ/dh)·h·(h−2ζ)/2`, worth `−16 cm` at
    `1000 m`, and the authors themselves write that Eq. (9) is "only approximated
    theoretically".

    ⇒ **none of the three published cases is a strict identity**, and the paper now says
    so. What unites them is something else, more robust: in the difference between the
    two routes of each, no quantity survives that has not entered both, except in Guo and
    Xue, where one does, and that is why it is of the third class.
    """
    identities = [c.key for c in CASES if c.expected == IDENTITY]
    assert not identities, (
        f"{identities} declared as strict identity. No PUBLISHED case is one; the strict "
        "identity of this work is the geoid–quasigeoid separation, which is ours and is "
        "proved in Lean.")


def test_the_grader_BITES_when_the_own_data_is_removed():
    """Sabotage: without the Stokes and terrain residuals, Guo and Xue would become identity.

    If this test failed, the grader would be returning the expected value instead of
    measuring the expression, and the three verdicts would be worth nothing.
    """
    # ⚠️ Since 2026-09-15 there are TWO class-3 cases (Vu closed in that class); each is sabotaged.
    originals = [c for c in CASES if c.expected == OWN_DATA]
    assert originals, "there is no own-data case left to sabotage"
    for original in originals:
        _sabotage(original)


def _sabotage(original):
    # ⚠️ The list belongs to the CASE since 2026-09-15, not global; sabotaging the global
    # would leave the gate measuring what no longer exists, and it would pass by reading
    # the wrong thing.
    without_own = Case(
        key=original.key + "-sabotaged",
        routes=original.routes,
        route_a=original.route_a,
        route_b=original.route_a,          # both routes equal ⇒ nothing is left in the difference
        source="gate sabotage",
        expected=IDENTITY,
        own=original.own,
    )
    cls, diff, own = grade(without_own)
    assert cls == IDENTITY and diff == 0 and not own, (cls, diff)


def test_the_grader_SEPARATES_own_data_from_a_shared_only_residual():
    """A residual that only repackages shared inputs is NOT own data."""
    disguised = Case(
        key="residual-of-shared-inputs",
        routes=("a", "b"),
        route_a=-gamma * ((h - Hn) - zeta_mod),
        route_b=-gamma * ((h - Hn) - zeta_mod) + gamma * sp.Rational(1, 100) * zeta_mod,
        source="constructed",
        expected=SHARED_ONLY,
    )
    cls, diff, own = grade(disguised)
    assert cls == SHARED_ONLY, (cls, diff)
    assert not own and diff != 0, (diff, own)


def test_the_case_that_CANNOT_BE_GRADED_declares_the_missing_source():
    """BITES: marking a case UNDETERMINED without saying what is missing fails.

    ⚠️⚠️ **The fourth verdict is not a class; it is the refusal to grade**, and it exists
    since 2026-09-15 because Vu's case could not be decided with the archive. The
    difference between the two routes is `T − γ̄·ζ_mod`: the disturbing potential
    integrated in that work against what the 2020 model gives. Classifying it requires
    knowing whether the two come from the same data and the same treatment, and **the
    2020 work was not in the archive**.

    ✅ **Declaring the ignorance is the result**, and it beats a guessed class: guessing
    is what produced the error of the title case. An undetermined case must name the
    missing source, so that whoever obtains it knows what to do with it.
    """
    # ⚠️ There is no undetermined case left among the three: Vu's closed when the 2020
    # paper, which WAS in the archive, was read. The verdict stays available, and what is
    # demanded is that whoever uses it names the missing source; checked on a synthetic case.
    from symbolic_independence import Case, h  # in mapgravy: mapgravy.experiments.symbolic_independence
    synthetic = Case(key="synthetic", routes=("a", "b"), route_a=h, route_b=2 * h,
                     source="eq. (1)", expected=UNDETERMINED, missing="@missing_work")
    assert grade(synthetic)[0] == UNDETERMINED
    undetermined = [c for c in CASES if c.expected == UNDETERMINED] + [synthetic]
    for case in undetermined:
        assert case.missing, f"{case.key}: undetermined without saying what is missing"
        assert "@" in case.missing, (
            f"{case.key}: what is missing must name the KEY of the source, so that it "
            f"can be fetched: {case.missing!r}")


def test_the_OWN_symbols_are_per_case_and_not_global():
    """BITES: going back to classifying by a global list fails.

    ⚠️ It was global until 2026-09-15, and that was wrong: `h` enters both routes of the
    Argentine case, so it is shared there, but nothing guarantees it is in another case.
    A class computed with the wrong list is as false as a misspelt expression, and cannot
    be told apart from it by any outward sign.
    """
    fields = {f.name for f in CASES[0].__dataclass_fields__.values()}
    assert "own" in fields, "the case no longer declares its own symbols"
    (guoxue,) = [c for c in CASES if c.key == "guoxue2023offset"]
    _, diff, own = grade(guoxue)
    assert own, "the class-3 case no longer identifies what is left in the difference"


def test_every_route_declares_the_NUMBERED_EQUATION_it_translates():
    """BITES: a case whose `source` names no numbered equation fails.

    ⚠️⚠️ **Born of the worst finding of this front.** While checking the four sources on
    the page, the author asked whether the expressions we had **existed** in the papers.
    Two did not: neither Vu's, whose `21` numbered equations contain neither `W₀ − γ̄H*`
    nor `h`, nor Guo and Xue's, whose Eq. (12) is `ΔH* = h − H − N₀ − ζ_m`, in **heights
    and without `γ`**, where we wrote `−γ̄((h − H*) − ζ_mod)`.

    ⇒ the failure mode was not "we read the wrong equation". It was **"we wrote what we
    expected the equation to say"**: expressions assembled from general knowledge, never
    read on the page. A `sympy` cannot tell the two apart, and no gate can.

    ✅ **What THIS gate does, and it is modest:** it forces each case to name the numbered
    equation it claims to translate. It does not verify the translation; it verifies
    that it commits to a checkable target, and that commitment is what makes lot 9 of
    `docs/monta_conferencia.py` possible. The checking remains human, and is recorded in
    `docs/formulas_conferidas.md`.
    """
    without_equation = [c.key for c in CASES if not re.search(r"eqs?\. \(\d", c.source)]
    assert not without_equation, (
        f"{without_equation}: the source names no numbered equation. A route that does "
        "not commit to an equation on the page cannot be checked against it, and that is "
        "how two invented translations survived.")
