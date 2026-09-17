"""The two comparisons of Table 3 of Gómez et al., put on the same scale.

⚠️ **The figure exists because the paper's central argument was prose only.** The
`draft3.md` said that one comparison gives `0.00 m²s⁻²` and the other `6.97`, and that the
IHRS target is `0.10`: three loose numbers the reader has to hold at once to see the
asymmetry. Put on a single axis, the asymmetry is seen at a glance.

What the figure asserts, and nothing more:

- the two methods of the paper itself fall on the SAME point, to the two published
  decimals, and it is that coincidence the Conclusions of that paper report as
  consistency. ⚠️ They are **not** the same expression rearranged (they differ by the
  linearisation error of Eq. (9), worth `−16 cm` at `1000 m` of altitude), but in the
  difference between them no quantity survives that has not entered both;
- the determination of **another group, with its own data**, the only comparison in
  that table that could disagree, sits at `6.97 m²s⁻²`, and the paper declares the
  reasons open;
- the **declared IHRS target** is `0.10 m²s⁻²`, and fits inside the thickness of the
  marker itself: it is `18×` smaller than the uncertainty of each estimate.

⚠️ **All values are PUBLISHED and come from the versioned module**, never transcribed
here: the source is `cost_of_agreement.py`, whose numbers the gates check against the
PDF of the original paper.
"""
from __future__ import annotations

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from matplotlib.ticker import FuncFormatter

import cost_of_agreement as _c  # in mapgravy: mapgravy.experiments.cost_of_agreement


def _decimal(x: float, places: int = 2, lang: str = "pt") -> str:
    """The Portuguese manuscript writes `6{,}97`; a figure with a decimal point would clash
    with the page. In the English version the separator is the point: the figure follows
    the language of the manuscript that includes it (2026-09-17: `draft3_en` came out
    with Portuguese figures)."""
    # ⚠️ the sign too: `-` is a hyphen, and the axis of a paper figure uses the
    # typographic MINUS, like the rest of the page.
    s = f"{x:.{places}f}"
    if lang == "pt":
        s = s.replace(".", ",")
    return s.replace("-", "\u2212")


#: The figure's texts, per language. The keys are the SAME in both: a new text enters both
#: or neither (gate `test_fig_custo_tem_os_mesmos_textos_nas_duas_linguas`).
_TEXTS = {
    "pt": {
        "ss": "Sánchez e Sideris (2017)\ndeterminação de outro grupo",
        "tv": "Tocho e Vergos (2015)",
        "m2": "Método 2  (a eq. (2) reorganizada)",
        "m1": "Método 1",
        "identidade": "{v} m²s⁻²  —  sem dado que a outra não veja",
        "anterior": "542 marcos, outro modelo — podia discordar e não discorda:\n{v} m²s⁻², abaixo da meta",
        "alheia": "{v} m²s⁻²  =  {cm} cm",
        "meta": "meta declarada do IHRS: $\\pm${v} m²s⁻² ({cm} cm)",
        "eixo": "parâmetro de datum $\\delta W_0$ (m²s⁻²)",
    },
    "en": {
        "ss": "Sánchez and Sideris (2017)\nanother group's determination",
        "tv": "Tocho and Vergos (2015)",
        "m2": "Method 2  (Eq. (2) rearranged)",
        "m1": "Method 1",
        "identidade": "{v} m² s⁻²  —  no input the other does not see",
        "anterior": "542 benchmarks, another model — could disagree and does not:\n{v} m² s⁻², below the target",
        "alheia": "{v} m² s⁻²  =  {cm} cm",
        "meta": "declared IHRS target: $\\pm${v} m² s⁻² ({cm} cm)",
        "eixo": "datum parameter $\\delta W_0$ (m² s⁻²)",
    },
}

_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_out")
_DEFAULT_PNG = os.path.join(_OUT, "fig_cost_of_agreement.png")
#: the English version, with the name WRITTEN OUT: the figure gate requires the script to
#: mention the file it writes, and `.replace(".png", "_en.png")` does not mention it.
_DEFAULT_PNG_EN = os.path.join(_OUT, "fig_cost_of_agreement_en.png")


def figure(out_path: str = _DEFAULT_PNG, lang: str = "pt") -> str:
    os.makedirs(_OUT, exist_ok=True)
    T = _TEXTS[lang]
    v = lambda x, places=2: _decimal(x, places, lang)
    t = {e.label: e for e in _c.TABLE_3}
    m1, m2 = t["Method 1"], t["Method 2"]
    ss = t["Sánchez and Sideris (2017)"]

    fig, ax = plt.subplots(figsize=(6.9, 3.3))

    #: The rows of the plot. Method 1 and 2 share the SAME abscissa to two published
    #: decimals; drawing them at distinct `y` is what makes them visible.
    tv = t["Tocho and Vergos (2015)"]
    points = [(ss, 2.4, T["ss"], "above"), (tv, 1.2, T["tv"], "above"),
              (m2, 0.4, T["m2"], "above"), (m1, -0.4, T["m1"], "below")]
    for e, y, label, side in points:
        ax.errorbar(e.value, y, xerr=e.sigma, fmt="o", ms=6, color="black",
                    ecolor="0.45", elinewidth=1.2, capsize=3.5, zorder=3)
        dy, va = (0.22, "bottom") if side == "above" else (-0.22, "top")
        ax.text(e.value, y + dy, label, ha="center", va=va, fontsize=7.5)

    # The comparison that CANNOT disagree: the two methods fall on the SAME abscissa.
    ax.annotate("", xy=(m1.value, -0.4), xytext=(m2.value, 0.4),
                arrowprops=dict(arrowstyle="-", lw=1.6, color="black"))
    ax.text(m2.value + m2.sigma + 0.25, 0.0,
            T["identidade"].format(v=v(_c.LINKED_BY_IDENTITY)),
            ha="left", va="center", fontsize=7.5, style="italic")

    # The two that CAN disagree: one agrees, the other does not.
    ax.text(tv.value + tv.sigma + 0.25, 1.2,
            T["anterior"].format(v=v(_c.AGAINST_EARLIER_DETERMINATION)),
            ha="left", va="center", fontsize=7.5, style="italic", color="0.25")
    ax.annotate("", xy=(m1.value, -1.75), xytext=(ss.value, -1.75),
                arrowprops=dict(arrowstyle="<->", lw=1.1, color="0.35"))
    ax.text((m1.value + ss.value) / 2, -1.92,
            T["alheia"].format(v=v(_c.AGAINST_OTHER_GROUP),
                               cm=f"{_c.to_height(_c.AGAINST_OTHER_GROUP):.0f}"),
            ha="center", va="top", fontsize=8, style="italic", color="0.25")

    # The IHRS target, to scale.
    ax.annotate("", xy=(m1.value - _c.IHRS_TARGET, 3.35), xytext=(m1.value + _c.IHRS_TARGET, 3.35),
                arrowprops=dict(arrowstyle="|-|", lw=1.2, color="black", mutation_scale=3))
    ax.text(m1.value + 0.34, 3.35,
            T["meta"].format(v=v(_c.IHRS_TARGET), cm=f"{_c.to_height(_c.IHRS_TARGET):.0f}"),
            ha="left", va="center", fontsize=7.5)

    ax.set_xlabel(T["eixo"], fontsize=8.5)
    ax.set_yticks([])
    ax.set_ylim(-2.4, 3.85)
    ax.set_xlim(-2.6, 8.4)
    ax.tick_params(labelsize=8)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: v(x, 0)))
    ax.spines[["left", "right", "top"]].set_visible(False)
    ax.grid(True, axis="x", lw=0.4, color="0.90", zorder=0)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path


if __name__ == "__main__":
    print("figure ->", figure(sys.argv[1] if len(sys.argv) > 1 else _DEFAULT_PNG))
    print("figure ->", figure(_DEFAULT_PNG_EN, lang="en"))
