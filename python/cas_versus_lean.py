"""What a computer-algebra system decides about the five relations, and what it does not.

⚠️⚠️ **This experiment exists because an adversarial review asked the right question**:
*"why Lean and not a CAS? `sympy.simplify` decides the rational identities in one line,
in a project that is already Python"*. The honest answer is not an opinion: it is to run
the CAS. Run, it confirms half of the objection and refutes the other half.

RESULT, in one line: **`sympy` decides three of the five in one line each; the other two
cannot be expressed in it**; and where it fails it is not on the algebra but on the
HYPOTHESES: it gladly accepts an ill-posed statement, and even a wrong one.

⚠️ What this experiment does NOT claim: that Lean is preferable for the rational class.
For those three a CAS is cheaper, and the manuscript now says so.
"""
from __future__ import annotations

import sys

import sympy as sp

#: `simplify(e) == 0` is the identity test used throughout this file.
_zero = lambda e: sp.simplify(e) == 0


def r1_helmert_separation() -> bool:
    """`ḡ − γ̄ = Δg_B`, with `γ_Q = g − Δg` and the mean normal gravity `γ_Q + (FA/2)H`."""
    g, FA, B, H = sp.symbols("g FA B H", positive=True)
    Dg = sp.Symbol("Delta_g")
    k = (FA - 2 * B) / 2
    gbar = g + k * H
    gammabar = (g - Dg) + FA / 2 * H
    return _zero((gbar - gammabar) - (Dg - B * H))


def r2_rigid_limit() -> bool:
    """`δₙ` and `D` equal 1 when `h = k = 0`."""
    n, h, k = sp.symbols("n h k")
    delta = 1 + (2 / n) * h - ((n + 1) / n) * k
    D = 1 + k - h
    return (_zero(delta.subs({h: 0, k: 0}) - 1) and _zero(D.subs({h: 0, k: 0}) - 1))


def r3_asymptotic_ratio() -> tuple[bool, bool]:
    """The ratio equals `−(1−2ν)/(2(1−ν))`, and `g` and `μ` drop out of it.

    Returns `(decides_the_value, decides_the_invariance)`. ⚠️ The invariance, which the
    manuscript treats as the result, the CAS **also** exhibits: `g` and `μ` disappear from
    the simplified expression. Saying otherwise would be selling dear what is cheap.
    """
    g, nu, G, mu = sp.symbols("g nu G mu", positive=True)
    hinf = -g**2 * (1 - nu) / (2 * sp.pi * G * mu)
    nlinf = (1 - 2 * nu) * g**2 / (4 * sp.pi * G * mu)
    ratio = sp.simplify(nlinf / hinf)
    return _zero(ratio + (1 - 2 * nu) / (2 * (1 - nu))), not ({g, mu} & ratio.free_symbols)


def ill_posed_hypothesis_passes_the_cas() -> dict:
    """The CAS accepts `H = C/ḡ(H)`, the statement Lean REFUSED, and the wrong one too.

    ⚠️⚠️ **This is where the difference lies, and not in the algebra.** The proof system
    refused the form `H = C/ḡ(H)` because `H` occurs on both sides, and that refusal is
    what made visible that the Helmert height is defined by an **implicit** equation. The
    CAS accepts it, simplifies it and returns two roots, without saying which one is the
    physics. And it accepts, just as naturally, a WRONG version of the hypothesis (swapped
    exponent), returning three.

    ⇒ a CAS computes with whatever is written to it; it has no notion of an ill-posed
    statement or of a missing hypothesis. It is the class of defect this paper is about.
    """
    g, FA, B, H, C = sp.symbols("g FA B H C", positive=True)
    k = (FA - 2 * B) / 2
    right = sp.Eq(H, C / (g + k * H))
    wrong = sp.Eq(H, C / (g + k * H**2))       # swapped exponent, a plausible defect
    return {"accepts_the_implicit": True,
            "roots_of_the_implicit": len(sp.solve(right, H)),
            "accepts_the_wrong": True,
            "roots_of_the_wrong": len(sp.solve(wrong, H))}


def degree_zero_in_the_cas():
    """⚠️ **Against us:** the vacuity at `n = 0` is NOT a peculiarity of Lean.

    The manuscript recorded that the proof system's total division (`x/0 = 0`) makes the
    rigid limit provable without hypothesis, which makes it vacuous at `n = 0`. Measured:
    `sympy` cancels the `n` before substituting and returns **the same 1**. ⇒ the trap is
    in the shape of the expression, not in the tool, and blaming Lean would be choosing
    the example that suits us.
    """
    n, h, k = sp.symbols("n h k")
    delta = 1 + (2 / n) * h - ((n + 1) / n) * k
    return sp.simplify(delta.subs({h: 0, k: 0})).subs(n, 0)


#: The two relations a CAS cannot even STATE, with the reason.
OUT_OF_REACH = {
    "well-posedness (Hörmander ⟹ Lions–Sznitman)":
        "quantifies over the boundary points and speaks of angles between vectors in an "
        "inner-product space; and the converse requires CONSTRUCTING a counterexample and "
        "proving that it is one",
    "k'₀ = 0 by conservation of mass":
        "goes through an ODE, a constancy argument on a connected open set and the "
        "fundamental theorem of calculus; the CAS solves the ODE and does not prove "
        "uniqueness under the stated hypotheses",
}


def main() -> int:
    v3, inv3 = r3_asymptotic_ratio()
    decides = {"R1 Helmert separation": r1_helmert_separation(),
               "R2 rigid limit": r2_rigid_limit(),
               "R3 asymptotic ratio (value)": v3,
               "R3 asymptotic ratio (invariance)": inv3}
    print("== what sympy DECIDES, in one line each ==")
    for name, v in decides.items():
        print(f"   {'yes' if v else 'NO':>4}  {name}")
    print(f"\n== what it cannot even state ({len(OUT_OF_REACH)}) ==")
    for name, reason in OUT_OF_REACH.items():
        print(f"   {name}\n      {reason}")
    h = ill_posed_hypothesis_passes_the_cas()
    print("\n== where the difference lies: the HYPOTHESES ==")
    print(f"   accepts `H = C/ḡ(H)`, which Lean refused, and returns "
          f"{h['roots_of_the_implicit']} roots without saying which one is the physics")
    print(f"   accepts the WRONG hypothesis (swapped exponent) and returns "
          f"{h['roots_of_the_wrong']} roots")
    print(f"\n== against us ==\n   delta(n=0, h=k=0) in sympy = {degree_zero_in_the_cas()} "
          "-- the same vacuity, hence it is not Lean's")
    return 0


def _self_check() -> None:
    assert r1_helmert_separation(), "R1 should be decided by the CAS"
    assert r2_rigid_limit(), "R2 should be decided by the CAS"
    v, inv = r3_asymptotic_ratio()
    assert v and inv, "R3 and its invariance should be decided by the CAS"
    h = ill_posed_hypothesis_passes_the_cas()
    assert h["roots_of_the_implicit"] == 2 and h["roots_of_the_wrong"] == 3, h
    assert len(OUT_OF_REACH) == 2
    assert degree_zero_in_the_cas() == 1, "the vacuity at n=0 also occurs in the CAS"
    print("self-check OK")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        _self_check()
    else:
        raise SystemExit(main())
