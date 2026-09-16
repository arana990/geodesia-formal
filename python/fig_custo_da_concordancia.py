"""As duas comparações da Tabela 3 de Gómez e colaboradores, postas na mesma escala.

⚠️ **A figura existe porque o argumento central do artigo estava só em prosa.** O
`draft3.md` dizia que uma comparação dá `0,00 m²s⁻²` e a outra `6,05`, e que a meta
do IHRS é `0,10` — três números soltos, que o leitor tem de segurar ao mesmo tempo
para ver a assimetria. Postos num eixo só, a assimetria vê-se de uma vez.

O que a figura afirma, e nada mais:

- os dois métodos do próprio trabalho caem no MESMO ponto, a duas casas publicadas, e é
  essa coincidência que as Conclusões daquele artigo reportam como consistência. ⚠️ Eles
  **não** são a mesma expressão reorganizada — diferem pelo erro de linearização da eq. (9),
  que vale `−16 cm` a `1000 m` de altitude —, mas na diferença entre eles não sobrevive
  nenhuma grandeza que não tenha entrado nos dois;
- a determinação de **outro grupo, com dado próprio** — a única comparação daquela
  tabela que podia discordar — fica a `6,05 m²s⁻²`, e o artigo declara as razões em
  aberto;
- a **meta declarada do IHRS** é `0,10 m²s⁻²`, e cabe dentro da espessura do próprio
  marcador: é `18×` menor que a incerteza de cada estimativa.

⚠️ **Todos os valores são PUBLICADOS e vêm do módulo versionado**, nunca transcritos
aqui — a fonte é `custo_da_concordancia.py`, cujos números os portões conferem contra
o PDF do artigo original.
"""
from __future__ import annotations

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from matplotlib.ticker import FuncFormatter

import custo_da_concordancia as _c  # no mapgravy: mapgravy.experiments.custo_da_concordancia


def _virgula(x: float, casas: int = 2) -> str:
    """O manuscrito escreve `6{,}05`; uma figura com ponto decimal destoa da página."""
    # ⚠️ o sinal também: `-` é hífen, e o eixo de uma figura de artigo usa o MENOS
    # tipográfico, como o resto da página.
    return f"{x:.{casas}f}".replace(".", ",").replace("-", "\u2212")

_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_out")
_DEFAULT_PNG = os.path.join(_OUT, "fig_custo_da_concordancia.png")


def figura(out_path: str = _DEFAULT_PNG) -> str:
    os.makedirs(_OUT, exist_ok=True)
    t = {e.rotulo: e for e in _c.TABELA_3}
    m1, m2 = t["Método 1"], t["Método 2"]
    ss = t["Sánchez e Sideris (2017)"]

    fig, ax = plt.subplots(figsize=(6.9, 3.3))

    #: As três linhas do gráfico. O Método 1 e o 2 partilham a MESMA abscissa por
    #: identidade algébrica — desenhá-los em `y` distintos é o que os torna visíveis.
    tv = t["Tocho e Vergos (2015)"]
    pontos = [(ss, 2.4, "Sánchez e Sideris (2017)\ndeterminação de outro grupo", "cima"),
              (tv, 1.2, "Tocho e Vergos (2015)", "cima"),
              (m2, 0.4, "Método 2  (a eq. (2) reorganizada)", "cima"),
              (m1, -0.4, "Método 1", "baixo")]
    for e, y, rotulo, lado in pontos:
        ax.errorbar(e.valor, y, xerr=e.sigma, fmt="o", ms=6, color="black",
                    ecolor="0.45", elinewidth=1.2, capsize=3.5, zorder=3)
        dy, va = (0.22, "bottom") if lado == "cima" else (-0.22, "top")
        ax.text(e.valor, y + dy, rotulo, ha="center", va=va, fontsize=7.5)

    # A comparação que NÃO pode discordar: os dois métodos caem na MESMA abscissa.
    ax.annotate("", xy=(m1.valor, -0.4), xytext=(m2.valor, 0.4),
                arrowprops=dict(arrowstyle="-", lw=1.6, color="black"))
    ax.text(m2.valor + m2.sigma + 0.25, 0.0,
            f"{_virgula(_c.LIGADAS_POR_IDENTIDADE)} m²s⁻²  —  sem dado que a outra não veja",
            ha="left", va="center", fontsize=7.5, style="italic")

    # As duas que PODEM discordar: uma concorda, a outra não.
    ax.text(tv.valor + tv.sigma + 0.25, 1.2,
            f"542 marcos, outro modelo — podia discordar e não discorda:\n"
            f"{_virgula(_c.CONTRA_DETERMINACAO_ANTERIOR)} m²s⁻², abaixo da meta",
            ha="left", va="center", fontsize=7.5, style="italic", color="0.25")
    ax.annotate("", xy=(m1.valor, -1.75), xytext=(ss.valor, -1.75),
                arrowprops=dict(arrowstyle="<->", lw=1.1, color="0.35"))
    ax.text((m1.valor + ss.valor) / 2, -1.92,
            f"{_virgula(_c.CONTRA_DETERMINACAO_ALHEIA)} m²s⁻²  =  "
            f"{_c.em_altura(_c.CONTRA_DETERMINACAO_ALHEIA):.0f} cm",
            ha="center", va="top", fontsize=8, style="italic", color="0.25")

    # A meta do IHRS, à escala.
    ax.annotate("", xy=(m1.valor - _c.META_IHRS, 3.35), xytext=(m1.valor + _c.META_IHRS, 3.35),
                arrowprops=dict(arrowstyle="|-|", lw=1.2, color="black", mutation_scale=3))
    ax.text(m1.valor + 0.34, 3.35,
            f"meta declarada do IHRS: $\\pm${_virgula(_c.META_IHRS)} m²s⁻² "
            f"({_c.em_altura(_c.META_IHRS):.0f} cm)",
            ha="left", va="center", fontsize=7.5)

    ax.set_xlabel("parâmetro de datum $\\delta W_0$ (m²s⁻²)", fontsize=8.5)
    ax.set_yticks([])
    ax.set_ylim(-2.4, 3.85)
    ax.set_xlim(-2.6, 8.4)
    ax.tick_params(labelsize=8)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: _virgula(v, 0)))
    ax.spines[["left", "right", "top"]].set_visible(False)
    ax.grid(True, axis="x", lw=0.4, color="0.90", zorder=0)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path


if __name__ == "__main__":
    print("figura ->", figura(sys.argv[1] if len(sys.argv) > 1 else _DEFAULT_PNG))
