"""What it costs to read as validation an agreement forced by identity.

⚠️ **Every number here is PUBLISHED, not ours.** This module computes no geodesy: it puts
side by side four values of Table 3 of `@tocho2024argentina` and the declared IHRS target
of `@sanchez2021ihrs`, and does the arithmetic the manuscript asserts. Its reason to exist
is `CLAUDE.md` §0.3 #10, the gate before the prose; its reason to live in a versioned
file is §0.3c #6: a number that exists only in conversation does not enter a paper.

The point, and it lies entirely **inside the same table of the same paper**:

- Method 1 and Method 2 are linked by an algebraic identity and give the SAME value to
  two decimals. The difference between them is `0.00 m²s⁻²`, and the Conclusions report
  it as *"Both methods demonstrated consistency with each other"*;
- on the next row of the table, the determination of another group, `@sanchezsideris2017`,
  differs by `6.97 m²s⁻²`, and the paper says *"Reasons for this discrepancy are subject
  of further study"*.

⇒ the comparison that **cannot** disagree is reported as consistency; the one that
**can**, and disagrees by `71 cm`, is left open. The IHRS target is `1 cm`.
"""

from __future__ import annotations

from dataclasses import dataclass

W0_IHRS = 62636853.4  # m²/s², IAG Res. 1 (2015); in mapgravy it comes from geodesy/constants.py

#: Normal gravity used only to convert potential into height, `ζ = δW/γ`.
#: GRS80 reference value at mid latitude; the conversion is an order of magnitude and a
#: choice between `9.78` and `9.83` moves the `71 cm` by less than `1 cm`.
GAMMA = 9.81

#: Declared IHRS target, `@sanchez2021ihrs` p. 3: "evaluating the possibility of reaching
#: an accuracy around ± 0.1 m2 s−2 (equivalent to ± 1 cm in height)".
IHRS_TARGET = 0.10


@dataclass(frozen=True)
class Estimate:
    label: str
    value: float          # δW₀, m²s⁻²
    sigma: float          # m²s⁻²
    provenance: str
    w0lvd: float          # the column that decides the sign, m²s⁻²


#: Conventional value of the reference geopotential (IAG Res. 1, 2015). ⚠️ **Imported, not
#: retyped**: the gate `test_nenhum_modulo_redefine_constante_central` caught it being
#: written by hand here, and rightly so: a second copy of a central constant is how copies
#: of numbers age in silence. It serves to recover the SIGN of each row of the table from
#: the `W0LVD` column, which is immune to the extraction damage described below.
W0_CONVENTIONAL = W0_IHRS

#: Table 3 of `@tocho2024argentina`, p. 278. Units: m²s⁻².
#:
#: ⚠️⚠️ **THE SIGN OF THE FIRST THREE WAS READ WRONG UNTIL 2026-09-15, and the defect is in
#: the EXTRACTION, not in the source.** `pdftotext` emits `\x02` in place of the minus: the
#: PDF font carries no Unicode map for that glyph, and `pdftohtml` does not recover it
#: either. The first three rows carry that `\x02` and the fourth does not:
#:
#:     Method 1   \x020:46 ± 1:78   62636853:88
#:     δW0_SS       6:51 ± 0:49     62636846:89      <- no \x02
#:
#: ⇒ the table's convention is `δW₀ = W₀ − W₀LVD`, and the `W0LVD` column confirms the sign
#: without depending on the extraction: `62636853.4 − 62636853.88 = −0.48 ≈ −0.46`, and
#: `62636853.4 − 62636846.89 = +6.51`. The gate `sign_agrees_with_the_W0LVD_column`
#: redoes that arithmetic for every row.
TABLE_3: tuple[Estimate, ...] = (
    Estimate("Method 1", -0.46, 1.78, "height-anomaly route", 62636853.88),
    Estimate("Method 2", -0.46, 1.37, "the same equation rearranged", 62636853.87),
    Estimate("Tocho and Vergos (2015)", -0.50, 0.14,
             "other benchmarks (542, SRVN71) and another model (EGM2008)", 62636853.90),
    Estimate("Sánchez and Sideris (2017)", 6.51, 0.49,
             "another group's determination", 62636846.89),
)


def to_height(dw: float) -> float:
    """Converts a potential difference into centimetres of height."""
    return dw / GAMMA * 100.0


def between(a: str, b: str) -> float:
    """Absolute difference in m²s⁻² between two rows of the table, by label."""
    (x,) = [e for e in TABLE_3 if e.label == a]
    (y,) = [e for e in TABLE_3 if e.label == b]
    return abs(x.value - y.value)


#: The quantities the manuscript asserts, all derived from what is above.
#: ⚠️ The name says "shared", not "identity": the two routes are NOT the same expression
#: rearranged (they differ by the linearisation error of Eq. (9)), but in the difference
#: between them no quantity survives that has not entered both. See `symbolic_independence`.
SHARED_DATA_ONLY = between("Method 1", "Method 2")
LINKED_BY_IDENTITY = SHARED_DATA_ONLY   # old name, kept so as not to break callers
AGAINST_OTHER_GROUP = between("Method 1", "Sánchez and Sideris (2017)")
#: ⚠️ The THIRD comparison, which the manuscript omitted until 2026-09-15. Tocho and Vergos
#: used `542` benchmarks of the previous system (SRVN71) and EGM2008, data different from
#: this table's, hence they COULD disagree. They agreed to `0.04 m²s⁻²`. Omitting it made
#: the sentence "the only one that could disagree" false, and weakened the argument rather
#: than strengthening it: with it, two comparisons are capable of disagreeing, one agrees
#: and the other fails by `71 cm`.
AGAINST_EARLIER_DETERMINATION = between("Method 1", "Tocho and Vergos (2015)")
LARGEST_SIGMA = max(e.sigma for e in TABLE_3[:2])

#: ⚠️ ADDED ON 2026-09-17: a THIRD determination of the Argentine parameter, later than
#: Table 3 and independent of both: Guimarães, Matos and Blitzkow (2025), Table 9, p. 20:
#: SAM_GEOID2023, `2 922` GNSS/levelling stations, adjustment with network tilts. It is not
#: in Gómez's table (it is later); it is here because it is the class-3 comparison that was
#: missing, and it sides with Sánchez and Sideris: `0.71 ± 0.03 m` against `0.66 ± 0.05`.
#: ⚠️ The `W0LVD` column of Table 9 gives `62 636 853.4 − 62 636 846.37 = 7.03`, and the
#: "Potential Parameter" column gives `6.95`: the table itself has `0.08 m²s⁻²` of internal
#: slack (0.8 cm; their error bar is 0.27). The sign gate accepts it with its own tolerance.
GUIMARAES_2025 = Estimate("Guimarães, Matos and Blitzkow (2025)", 6.95, 0.27,
                          "third group, SAM_GEOID2023, 2 922 stations", 62636846.37)
AGAINST_OTHER_GROUP_2 = abs(TABLE_3[0].value - GUIMARAES_2025.value)
BETWEEN_THE_TWO_OTHER_GROUPS = abs(TABLE_3[3].value - GUIMARAES_2025.value)


def sign_agrees_with_the_W0LVD_column(tolerance: float = 0.03) -> dict[str, float]:
    """Redoes `δW₀ = W₀ − W₀LVD` for every row and returns the residual.

    ⚠️ **This function is what makes the sign verifiable without trusting the PDF
    extraction.** The minus glyph is lost (see the note on `TABLE_3`), but the `W0LVD`
    column consists of digits only, survives intact, and determines the sign by arithmetic.
    """
    return {e.label: (W0_CONVENTIONAL - e.w0lvd) - e.value
            for e in (*TABLE_3, GUIMARAES_2025)}


def main() -> int:
    print("Table 3 of Gómez et al. (2024): δW₀ of the Argentine datum\n")
    print(f"{'':<28}{'m²s⁻²':>16}   {'in height':>10}   provenance")
    for e in TABLE_3:
        print(f"{e.label:<28}{e.value:7.2f} ± {e.sigma:<6.2f}   "
              f"{to_height(e.value):7.1f} cm   {e.provenance}")
    print()
    print(f"declared IHRS target                      {IHRS_TARGET:.2f}        "
          f"{to_height(IHRS_TARGET):7.1f} cm")
    print()
    print("the THREE comparisons the same table contains:")
    print(f"  linked by identity (M1 x M2)            {LINKED_BY_IDENTITY:.2f}        "
          f"{to_height(LINKED_BY_IDENTITY):7.1f} cm   <- reported as consistency")
    print(f"  against Tocho and Vergos (own data)     {AGAINST_EARLIER_DETERMINATION:.2f}        "
          f"{to_height(AGAINST_EARLIER_DETERMINATION):7.1f} cm   <- could disagree, AGREES")
    print(f"  against another group (M1 x SS)         {AGAINST_OTHER_GROUP:.2f}        "
          f"{to_height(AGAINST_OTHER_GROUP):7.1f} cm   <- could disagree, DISAGREES")
    print()
    print("  the sign, redone from the W0LVD column (residual in m²s⁻²):")
    for name, r in sign_agrees_with_the_W0LVD_column().items():
        print(f"    {name:<38}{r:+.3f}")
    print()
    print(f"uncertainty of the estimate itself        {LARGEST_SIGMA:.2f}        "
          f"{to_height(LARGEST_SIGMA):7.1f} cm")
    # ⚠️ The published difference is `0.00` TO TWO DECIMALS; it is not zero by algebraic
    # identity. The two equations differ by the linearisation error of Eq. (9); see
    # `symbolic_independence.py`. An earlier branch printed "the agreement is EXACT", and
    # that was the reading the adversarial review of 2026-09-15 brought down.
    print(f"  => the PUBLISHED agreement is {SHARED_DATA_ONLY:.2f} m2/s2 to two decimals, "
          f"and the uncertainty of what it validates is {to_height(LARGEST_SIGMA):.0f} cm")
    print(f"  => the open disagreement is {AGAINST_OTHER_GROUP / IHRS_TARGET:.0f}x the IHRS target")
    print()
    print("the THIRD determination, later than the table (Guimarães, Matos and Blitzkow 2025, Tab. 9):")
    g = GUIMARAES_2025
    print(f"  {g.label:<38}{g.value:5.2f} ± {g.sigma:<5.2f}  {to_height(g.value):6.1f} cm   {g.provenance}")
    print(f"  against Method 1                        {AGAINST_OTHER_GROUP_2:.2f}        "
          f"{to_height(AGAINST_OTHER_GROUP_2):7.1f} cm   <- could disagree, DISAGREES")
    print(f"  against Sánchez and Sideris             {BETWEEN_THE_TWO_OTHER_GROUPS:.2f}        "
          f"{to_height(BETWEEN_THE_TWO_OTHER_GROUPS):7.1f} cm   <- the two other groups AGREE with each other")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
