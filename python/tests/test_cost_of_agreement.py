"""Gates on the published numbers that support the consequence drawn in `draft3.md`.

⚠️ The rule of this house is §0.3c #2: *against what, exactly?* Here it is against the
PDFs of `@tocho2024argentina` and `@sanchez2021ihrs`, not against the module, which would
be circular. Without the archive on disk the source gates `skip`, and the arithmetic ones
keep running.
"""

from __future__ import annotations

import pathlib
import re
import subprocess

import pytest

from cost_of_agreement import (  # in mapgravy: mapgravy.experiments.cost_of_agreement
    AGAINST_OTHER_GROUP_2,
    BETWEEN_THE_TWO_OTHER_GROUPS,
    GUIMARAES_2025,
    AGAINST_OTHER_GROUP,
    AGAINST_EARLIER_DETERMINATION,
    sign_agrees_with_the_W0LVD_column,
    LINKED_BY_IDENTITY,
    IHRS_TARGET,
    TABLE_3,
    to_height,
)

_BIB = pathlib.Path(__file__).resolve().parents[2] / "bibliografia"


def _digits(pdf: str, layout: bool = True) -> str:
    path = _BIB / pdf
    if not path.exists():
        pytest.skip(f"{pdf} is not in this machine's archive")
    cmd = ["pdftotext"] + (["-layout"] if layout else []) + [str(path), "-"]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    return re.sub(r"\D", "", out)


def _letters(pdf: str) -> str:
    path = _BIB / pdf
    if not path.exists():
        pytest.skip(f"{pdf} is not in this machine's archive")
    out = subprocess.run(
        ["pdftotext", str(path), "-"], capture_output=True, text=True, check=True
    ).stdout
    return re.sub(r"[^a-z]", "", out.lower())


@pytest.mark.parametrize("e", TABLE_3, ids=lambda e: e.label)
def test_every_value_of_table_3_occurs_in_the_PDF_of_Gomez(e):
    """BITES: changing one decimal of any row fails.

    `pdftotext` mangles the paper's punctuation (`0:46 ˙ 1:78` for `0,46 ± 1,78`), so what
    is compared is the run of DIGITS, which survives the damage.

    ⚠️⚠️ **And that is why it is NOT enough, which was found out the hard way on
    2026-09-15.** A run of digits is **blind to the sign**: `046178` matches `+0.46` and
    `−0.46`. The first three values of this table are NEGATIVE, the manuscript published
    them positive for two days, and this gate was green the whole time. The sibling below
    closes the gap, and the lesson is §0.3c's: *what does the gate assert, exactly?* This
    one asserts that the digits occur, never that the quantity is the right one.
    """
    target = f"{abs(e.value):.2f}{e.sigma:.2f}".replace(".", "")
    assert target in _digits("tocho2024argentina.pdf"), (e.label, target)


def test_the_SIGN_of_every_row_is_redone_from_the_W0LVD_column():
    """BITES: flipping the sign of any row of the table fails.

    ⚠️⚠️ **Born of a published error.** The minus glyph is lost in extraction: `pdftotext`
    emits `\x02`, and `pdftohtml` does not recover it either, because the PDF font carries
    no Unicode map for that glyph. Measured over the whole archive: **`160` of `160`
    extracted files contain control characters**, and `U+0002` appears `16 575` times.
    Reading a number from there and trusting its sign is therefore never safe.

    ✅ **The remedy is not to extract better; it is to CROSS-CHECK.** The `W0LVD` column of
    the same table consists of digits only, survives intact, and determines the sign by
    arithmetic: `δW₀ = W₀ − W₀LVD` with the conventional `W₀`. This gate redoes that
    arithmetic for the four rows.

    ⚠️ The tolerance is `0.03 m²s⁻²` because the table publishes `δW₀` to two decimals and
    `W₀LVD` to two: the rounding of the two columns need not close exactly.
    """
    residuals = sign_agrees_with_the_W0LVD_column()
    # ⚠️ The Guimarães (2025) row has INTERNAL slack of 0.08 within Table 9 itself
    # (`W₀ − W0LVD = 7.03` against `6.95` in the next column); its own tolerance, stated
    # in the module. The sign is still decided by the column: 7.03 ≈ +6.95, not −6.95.
    off = {n: r for n, r in residuals.items()
           if abs(r) > (0.10 if n == GUIMARAES_2025.label else 0.03)}
    assert not off, (
        f"sign or value do not match the W0LVD column: {off}. "
        "The column decides; the minus glyph does not survive extraction.")


def test_the_IHRS_target_is_declared_in_the_source_and_is_one_centimetre():
    """The sentence of `@sanchez2021ihrs` p. 3 that fixes `±0.1 m²s⁻² = ±1 cm`.

    ⚠️ **This gate exists because its sibling does not reach this sentence.** The
    `test_toda_citacao_textual_VEM_DA_FONTE_que_o_marcador_declara` compares against
    `bibliografia/md/`, and the extraction of THIS source merges the two columns: right
    after "± 1 cm" comes text from the neighbouring column, and "in height" never appears
    there. The manuscript therefore quotes only up to "± 1 cm", which falls below that
    gate's 18-letter threshold and is skipped by it. Here the WHOLE sentence is checked,
    and against the PDF, which has no such damage.
    """
    letters = _letters("sanchez2021ihrs.pdf")
    assert "equivalenttocminheight" in letters, "the whole sentence, contiguous, in the source"
    assert "reachinganaccuracyaround" in letters
    assert abs(to_height(IHRS_TARGET) - 1.0) < 0.05, to_height(IHRS_TARGET)


def test_the_two_routes_linked_by_identity_agree_EXACTLY():
    """Not "very well": to the two published decimals, the difference is zero.

    It is the difference between this case and a measured agreement, and it is what
    the introduction asserts.
    """
    assert LINKED_BY_IDENTITY == 0.0, LINKED_BY_IDENTITY


def test_the_comparison_that_CAN_disagree_disagrees_by_more_than_half_a_metre():
    """And it is the one the paper leaves open, while reporting the other as consistency."""
    assert AGAINST_OTHER_GROUP > 6.5, AGAINST_OTHER_GROUP
    assert 68.0 < to_height(AGAINST_OTHER_GROUP) < 74.0
    assert AGAINST_OTHER_GROUP / IHRS_TARGET > 60.0


def test_the_THIRD_comparison_could_disagree_and_AGREES():
    """BITES: forgetting the comparison against Tocho and Vergos fails the paper's claim.

    ⚠️⚠️ **The manuscript said Sánchez and Sideris's was "the only one that could
    disagree", and that was false.** Tocho and Vergos (2015) used `542` benchmarks of the
    previous system (SRVN71) and EGM2008, data different from this table's, hence they
    could disagree. They agreed to `0.04 m²s⁻²`, and the paper's own conclusions say so:
    *"Results agree with the previous estimation of Tocho and Vergos (2015) but show
    differences with the one made by Sánchez and Sideris (2017)"*.

    ✅ Including it **strengthens** the argument instead of weakening it: of the three
    comparisons in the table, the two that could disagree give `0.4 cm` and `71 cm`, and
    the one that could not gives `0.0`, and it is this last one the conclusions report as
    consistency between methods.
    """
    assert AGAINST_EARLIER_DETERMINATION < 0.10, AGAINST_EARLIER_DETERMINATION
    assert to_height(AGAINST_EARLIER_DETERMINATION) < 1.0
    # and it is SMALLER than the IHRS target, which is the point
    assert AGAINST_EARLIER_DETERMINATION < IHRS_TARGET


def test_the_declared_uncertainty_is_an_order_above_the_IHRS_target():
    """What makes the reading costly: the agreement is exact, what it validates is decimetric."""
    sigma = max(e.sigma for e in TABLE_3[:2])
    assert to_height(sigma) > 10.0, to_height(sigma)
    assert sigma / IHRS_TARGET > 10.0, sigma / IHRS_TARGET


def test_the_third_determination_occurs_in_the_PDF_of_Guimaraes_2025():
    """The three numbers of the "Argentina" row of Table 9 (p. 20) and the sentence on p. 19.

    The third determination is what gives the class-3 comparison of the Argentine case
    THREE points, two of them agreeing with each other. Checked against the archive's
    PDF; without it, skip.
    """
    d = _digits("guimaraes2025sam.pdf")
    g = GUIMARAES_2025
    for number in (f"{g.w0lvd:.2f}", f"{g.value:.2f}", f"{g.sigma:.2f}", "0.71", "0.03"):
        assert number.replace(".", "").replace(",", "") in d, f"{number} is not in the PDF"
    letters = _letters("guimaraes2025sam.pdf")
    assert "inargentinatheverticaldatumparameterfoundinthispaperwas" in letters
    assert "mezetalfound" in letters and "inbothapproaches" in letters   # "Gómez": the ó drops in normalisation


def test_the_two_other_groups_agree_with_each_other_and_disagree_with_Gomez():
    """What the manuscript now asserts: two against one, and the numbers."""
    assert 4.0 < to_height(BETWEEN_THE_TWO_OTHER_GROUPS) < 5.0          # 4.5 cm between SS and GMB
    assert 70.0 < to_height(AGAINST_OTHER_GROUP_2) < 80.0               # 75 cm against Gómez M1
    assert BETWEEN_THE_TWO_OTHER_GROUPS < GUIMARAES_2025.sigma + 0.49   # within the summed bars
