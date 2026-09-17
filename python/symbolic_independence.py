"""Grades, by symbolic algebra, how much independence there is between two routes.

The question this experiment answers is that of the introduction of `draft3.md`: when
two published procedures agree, is that agreement evidence of anything, or a consequence
of their being the same expression rearranged?

The procedure is mechanical and has three classes, decided in this order:

1. ``IDENTITY``     — the difference between the routes simplifies to zero. The
   agreement is forced; disagreeing would be an arithmetic error.
2. ``SHARED_ONLY``  — the difference is NOT zero, but every quantity that survives in
   it has already entered both routes. No new data is confronted: what the comparison
   measures is the difference between two numerical treatments of the same inputs,
   and not the quantity being determined.
3. ``OWN_DATA``     — at least one quantity that went through only one of the routes
   survives in the difference. There is empirical content to be tested, and the size
   of the agreement says something.

⚠️ **What this experiment does NOT do.** It does not read the papers: it evaluates the
TRANSLATION we made of each paper into symbols, and that translation is in the
``source`` field of each case, with the passage cited. A misreading of ours produces a
wrong verdict with nothing failing; it is §0.3c #2 of this house (*against what,
exactly?*), and the mitigation is the citation standing next to it.

Run: ``python symbolic_independence.py``  (copy of mapgravy/experiments/symbolic_independence.py)
"""

from __future__ import annotations

from dataclasses import dataclass, field

import sympy as sp

# SHARED quantities: they enter both routes of the case.
h = sp.Symbol("h")                    # ellipsoidal height (GNSS)
Hn = sp.Symbol("H_ast")               # normal height, = C/gamma_bar
zeta_mod = sp.Symbol("zeta_mod")      # height anomaly of the gravimetric model
gamma = sp.Symbol("gamma_barra", positive=True)
W0 = sp.Symbol("W_0")
Wp = sp.Symbol("W_P")                 # potential at the benchmark, the same for both routes
C = sp.Symbol("C")                    # local geopotential number, the same in both routes
T = sp.Symbol("T")                    # disturbing potential of the model, the same in both
U_P = sp.Symbol("U_P")                # normal potential at P, in ellipsoidal coordinates
U0 = sp.Symbol("U_0")                 # normal potential on the ellipsoid surface
W0_IHRF = sp.Symbol("W_0^IHRF")
W0 = sp.Symbol("W_0")                 # global reference geopotential
W_P = sp.Symbol("W(P)")               # potential at the point
H_orto = sp.Symbol("H")               # orthometric height, from levelling
N0 = sp.Symbol("N_0")                 # zero-degree term of the undulation
gamma0 = sp.Symbol("gammabar_l0", positive=True)   # the γ̄_{l0} of Eq. (5) of Guo and Xue
V_sar = sp.Symbol("V_SAR")            # ALOS-1 subsidence rate, Vu (2020) Eq. (10)
t_lag = sp.Symbol("t")                # the 7 years between levelling and GNSS, Vu (2020)
zeta0 = sp.Symbol("zeta_0")           # zero-degree term, Vu (2020) Eq. (3)

# OWN-DATA quantities: they go through ONE route only.
zeta_stokes = sp.Symbol("zeta_res_Stokes")   # Stokes residual over terrestrial gravimetry
zeta_rtm = sp.Symbol("zeta_RTM")             # residual terrain reduction, over the DEM

OWN = {zeta_stokes, zeta_rtm}

IDENTITY, SHARED_ONLY, OWN_DATA = "IDENTITY", "SHARED_ONLY", "OWN_DATA"

#: ⚠️ The fourth verdict, and it is not a class: it is the refusal to grade. A case is
#: graded only if BOTH routes can be read in the source. When one of them lives in a work
#: that is out of reach, the difference can be written but its symbols cannot be classified
#: as shared or own, and guessing would repeat the defect this module exists to catch.
#: Added on 2026-09-15, while checking Vu's equations.
UNDETERMINED = "UNDETERMINED"


@dataclass(frozen=True)
class Case:
    key: str
    routes: tuple[str, str]
    route_a: sp.Expr
    route_b: sp.Expr
    source: str
    expected: str
    note: str = field(default="")
    #: ⚠️⚠️ **The symbols that enter one route only, IN THIS case.** It was a global
    #: constant until 2026-09-15, and that was wrong: `h` is shared in the Argentine case,
    #: where both routes consume it, and might not be in another. A class computed with
    #: the wrong list is as false as a misspelt expression.
    own: frozenset = field(default_factory=frozenset)
    #: Source that would be needed to grade and that is out of reach. Filled in ⇒ the
    #: case returns `UNDETERMINED` instead of a class.
    missing: str = field(default="")


def grade(case: Case) -> tuple[str, sp.Expr, set[sp.Symbol]]:
    """Returns (class, simplified difference, own-data symbols in it)."""
    diff = sp.simplify(sp.expand(case.route_a - case.route_b))
    if case.missing:
        return UNDETERMINED, diff, set()
    if diff == 0:
        return IDENTITY, diff, set()
    own = diff.free_symbols & (case.own or OWN)
    return (OWN_DATA if own else SHARED_ONLY), diff, own


# ---------------------------------------------------------------- the three cases

CASES: tuple[Case, ...] = (
    Case(
        key="tocho2024argentina",
        routes=("Eq. (9): the linearised one", "Eq. (12): the rigorous one"),
        # ⚠️⚠️ THIS TRANSLATION WAS REDONE ON 2026-09-15, and the verdict CHANGED.
        # The first version wrote the two routes as two rearrangements of the same
        # expression, and gave IDENTITY. That was our reading, not what the paper
        # publishes. Reading Eq. (9) and Eq. (12) as they stand in the source, the
        # difference is NOT zero: it is the linearisation error, which grows with the
        # square of the height.
        #
        # Route A, Eq. (9): uses `gamma` at the telluroid times `h` as the normal
        # potential difference, an approximation. `DeltaW0 = W0_IHRF - U0` is defined
        # before Eq. (6).
        route_a=gamma * h - C - T + (W0_IHRF - U0),
        # Route B, Eq. (12): uses `U(P)` computed at the ellipsoidal coordinates of P,
        # which is the exact normal potential. No linearisation.
        route_b=W0_IHRF - C - U_P - T,
        source="@tocho2024argentina eq. (9) and eq. (12), p. 275",
        expected=SHARED_ONLY,
        note='"Both methods demonstrated consistency with each other"; and the authors '
             'themselves write that Eq. (9) is "only approximated theoretically"',
    ),
    Case(
        key="vu2021vietname",
        routes=("2021: Eq. (4) with the T of the BVP", "2020: Eqs. (2), (10), (14), (15)"),
        # ⚠️⚠️ THIRD version of this translation (2026-09-15). The first was invented; the
        # second, redone from the 2021 equations, came out UNDETERMINED because the 2020
        # route lived in another paper. The 2020 paper WAS in the archive (I had claimed
        # it was not, without checking), and its equations close the case.
        #
        # 2021, Eq. (4) with the W of Eq. (3):   W₀^LVD = U(P) + T + H*·γ̄
        # 2020, Eqs. (14)+(15)+(2)+(10):         W₀^LVD = W₀ − γ̄·((h − H* + t·V) − ζ_mod − ζ₀)
        #   where Eq. (10) corrects the GNSS/levelling height anomaly for subsidence:
        #   V is the annual rate interpolated from ALOS-1 SAR data, t = 7 years.
        route_a=U_P + T + gamma * Hn,
        route_b=W0 - gamma * ((h - Hn + t_lag * V_sar) - zeta_mod - zeta0),
        source="@vu2021vietname eqs. (3), (4) and (11), p. 3; @vu2020mekong eqs. (2), (10), "
               "(14) and (15), pp. 13–17",
        expected=OWN_DATA,
        # The 29 121 gravity observations are the SAME in both works, so `T` (Stokes, 2021)
        # and `ζ_mod` (GEOID_LSC, 2020) come from the same data and differ by treatment.
        # `h` enters both (in 2021 through `U(P)`). What enters one route only is `V`: the
        # subsidence rate is an OBSERVATION, SAR, and does not derive from `h`, `H*` or
        # the gravimetry.
        own=frozenset({V_sar}),
        note='"This proves that the applied method is reliable"',
    ),
    Case(
        key="guoxue2023offset",
        routes=("Eq. (5): geopotential numbers", "Eq. (12): boundary value problem"),
        # ⚠️⚠️ TRANSLATION REDONE ON 2026-09-15, from the equations read on the page. The
        # previous one wrote two variants of the SAME route, one with residuals and one
        # without, and that is not what the paper compares. The two approaches it
        # confronts are:
        #     Eq.  (5)  ΔH* = (W₀ − W(P) − H*·γ) / γ₀     ← geopotential numbers
        #     Eq. (12)  ΔH* = h − H − N₀ − ζ_m            ← BVP
        route_a=(W0 - W_P - Hn * gamma) / gamma0,
        route_b=h - H_orto - N0 - zeta_mod,
        source="@guoxue2023offset eq. (5), p. 8, and eq. (12), p. 9",
        expected=OWN_DATA,
        # Each route consumes a quantity the other does not see: the first the potential
        # at the point and the normal height; the second the GNSS ellipsoidal height, the
        # levelled orthometric height, the zero-degree term and the model height anomaly.
        own=frozenset({W_P, Hn, h, H_orto, N0, zeta_mod}),
        note='"Remarkably, these values are in agreement"; and conclusion (3) opens with '
             '"Theoretical derivation and numerical analysis indicate…"',
    ),
)


def main() -> int:
    width = max(len(c.key) for c in CASES)
    failures = 0
    print(f"{'case':<{width}}  {'class':<14}  difference of the routes")
    print("-" * (width + 60))
    for case in CASES:
        cls, diff, own = grade(case)
        mark = "ok" if cls == case.expected else "DIVERGES"
        if cls != case.expected:
            failures += 1
        print(f"{case.key:<{width}}  {cls:<14}  {sp.srepr(diff) and sp.sstr(diff)}")
        print(f"{'':<{width}}  {mark:<14}  routes: {case.routes[0]} x {case.routes[1]}")
        if own:
            print(f"{'':<{width}}  {'':<14}  own data in the difference: "
                  f"{', '.join(sorted(str(s) for s in own))}")
        print(f"{'':<{width}}  {'':<14}  source: {case.source}")
        print()
    print(f"{len(CASES) - failures} of {len(CASES)} cases graded as the manuscript asserts.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
