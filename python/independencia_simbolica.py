"""Gradua, por álgebra simbólica, quanta independência há entre duas rotas.

A pergunta que este experimento responde é a do [@sec:intro-erro] do `draft3.md`:
quando dois procedimentos publicados concordam, essa concordância é evidência de
alguma coisa, ou é consequência de eles serem a mesma expressão reorganizada?

O procedimento é mecânico e tem três graus, decididos nesta ordem:

1. ``IDENTIDADE``    — a diferença entre as rotas simplifica a zero. A
   concordância é forçada; discordar seria erro de aritmética.
2. ``SO_PARTILHADO`` — a diferença NÃO é nula, mas toda grandeza que sobrevive
   nela já entrou nas duas rotas. Nenhum dado novo é confrontado: o que a
   comparação mede é a diferença entre dois tratamentos numéricos das
   mesmas entradas, e não a grandeza que se quer determinar.
3. ``DADO_PROPRIO``  — na diferença sobrevive ao menos uma grandeza que passou
   por uma só das rotas. Há conteúdo empírico a ser testado, e a magnitude da
   concordância diz alguma coisa.

⚠️ **O que este experimento NÃO faz.** Ele não lê os artigos: ele avalia a
TRADUÇÃO que nós fizemos de cada artigo para símbolos, e essa tradução está no
campo ``fonte`` de cada caso, com a passagem citada. Um erro de leitura nosso
produz um veredito errado sem que nada reprove — é o §0.3c #2 desta casa
(*contra o quê, exatamente?*), e a mitigação é a citação estar ao lado.

Rodar: ``python independencia_simbolica.py``  (cópia do mapgravy/experiments)
"""

from __future__ import annotations

from dataclasses import dataclass, field

import sympy as sp

# Grandezas PARTILHADAS: entram nas duas rotas do caso.
h = sp.Symbol("h")                    # altura elipsoidal (GNSS)
Hn = sp.Symbol("H_ast")               # altura normal, = C/gamma_barra
zeta_mod = sp.Symbol("zeta_mod")      # anomalia de altura do modelo gravimétrico
gamma = sp.Symbol("gamma_barra", positive=True)
W0 = sp.Symbol("W_0")
Wp = sp.Symbol("W_P")                 # potencial no marco, o mesmo para as duas rotas
C = sp.Symbol("C")                    # número geopotencial local, o mesmo nas duas rotas
T = sp.Symbol("T")                    # potencial perturbador do modelo, o mesmo nas duas
U_P = sp.Symbol("U_P")                # potencial normal em P, nas coordenadas elipsoidais
U0 = sp.Symbol("U_0")                 # potencial normal na superfície do elipsoide
W0_IHRF = sp.Symbol("W_0^IHRF")
W0 = sp.Symbol("W_0")                 # geopotencial de referência global
W_P = sp.Symbol("W(P)")               # potencial no ponto
H_orto = sp.Symbol("H")               # altura ortométrica, do nivelamento
N0 = sp.Symbol("N_0")                 # termo de grau zero da ondulação
gamma0 = sp.Symbol("gammabar_l0", positive=True)   # o γ̄_{l0} da eq. (5) de Guo e Xue
V_sar = sp.Symbol("V_SAR")            # taxa de subsidência do ALOS-1, Vu (2020) eq. (10)
t_lag = sp.Symbol("t")                # os 7 anos entre nivelamento e GNSS, Vu (2020)
zeta0 = sp.Symbol("zeta_0")           # termo de grau zero, Vu (2020) eq. (3)

# Grandezas de DADO PRÓPRIO: passam por UMA só das rotas.
zeta_stokes = sp.Symbol("zeta_res_Stokes")   # resíduo de Stokes sobre gravimetria terrestre
zeta_rtm = sp.Symbol("zeta_RTM")             # redução de terreno residual, sobre o MDE

PROPRIO = {zeta_stokes, zeta_rtm}

IDENTIDADE, SO_PARTILHADO, DADO_PROPRIO = "IDENTIDADE", "SO_PARTILHADO", "DADO_PROPRIO"

#: ⚠️ O quarto veredito, e ele não é um grau: é a recusa de graduar. Um caso só se gradua
#: se as DUAS rotas puderem ser lidas na fonte. Quando uma delas vive num trabalho que não
#: está ao alcance, a diferença pode ser escrita mas os seus símbolos não podem ser
#: classificados em partilhado ou próprio — e adivinhar seria repetir o defeito que este
#: módulo existe para apanhar. Acrescentado em 2026-09-15, ao conferir as equações de Vu.
INDETERMINADO = "INDETERMINADO"


@dataclass(frozen=True)
class Caso:
    chave: str
    rotas: tuple[str, str]
    rota_a: sp.Expr
    rota_b: sp.Expr
    fonte: str
    esperado: str
    nota: str = field(default="")
    #: ⚠️⚠️ **Os símbolos que entram numa rota só, NESTE caso.** Era uma constante global
    #: até 2026-09-15, e isso estava errado: `h` é partilhado no caso argentino, onde as
    #: duas rotas o consomem, e podia não o ser noutro. Um grau calculado com a lista
    #: errada é tão falso quanto uma expressão mal escrita.
    proprios: frozenset = field(default_factory=frozenset)
    #: Fonte que seria precisa para graduar e que não está ao alcance. Preenchido ⇒ o caso
    #: devolve `INDETERMINADO` em vez de um grau.
    falta: str = field(default="")


def gradua(caso: Caso) -> tuple[str, sp.Expr, set[sp.Symbol]]:
    """Devolve (grau, diferença simplificada, símbolos de dado próprio nela)."""
    dif = sp.simplify(sp.expand(caso.rota_a - caso.rota_b))
    if caso.falta:
        return INDETERMINADO, dif, set()
    if dif == 0:
        return IDENTIDADE, dif, set()
    proprios = dif.free_symbols & (caso.proprios or PROPRIO)
    return (DADO_PROPRIO if proprios else SO_PARTILHADO), dif, proprios


# ---------------------------------------------------------------- os três casos

CASOS: tuple[Caso, ...] = (
    Caso(
        chave="tocho2024argentina",
        rotas=("eq. (9): a linearizada", "eq. (12): a rigorosa"),
        # ⚠️⚠️ ESTA TRADUÇÃO FOI REFEITA A 2026-09-15, e o veredito MUDOU.
        # A primeira versão escrevia as duas rotas como duas reorganizações da mesma
        # expressão, e dava IDENTIDADE. Era leitura nossa, não o que o artigo publica.
        # Lendo a eq. (9) e a eq. (12) como estão na fonte, a diferença NÃO é nula: é o
        # erro de linearização, que cresce com o quadrado da altura.
        #
        # Rota A, eq. (9): usa `gamma` no teluroide vezes `h` como diferença de potencial
        # normal — uma aproximação. `DeltaW0 = W0_IHRF - U0` é definido antes da eq. (6).
        rota_a=gamma * h - C - T + (W0_IHRF - U0),
        # Rota B, eq. (12): usa `U(P)` calculado nas coordenadas elipsoidais de P, que é o
        # potencial normal exato. Nenhuma linearização.
        rota_b=W0_IHRF - C - U_P - T,
        fonte="@tocho2024argentina eq. (9) e eq. (12), p. 275",
        esperado=SO_PARTILHADO,
        nota="«Both methods demonstrated consistency with each other»; e os próprios "
             "autores escrevem que a eq. (9) é «only approximated theoretically»",
    ),
    Caso(
        chave="vu2021vietname",
        rotas=("2021: eq. (4) com o T do PVC", "2020: eqs. (2), (10), (14), (15)"),
        # ⚠️⚠️ TERCEIRA versão desta tradução (2026-09-15). A primeira era inventada; a
        # segunda, refeita pelas equações de 2021, ficou INDETERMINADA porque a rota de 2020
        # vivia noutro artigo. O artigo de 2020 ESTAVA no acervo — eu tinha afirmado que
        # não sem verificar —, e as suas equações fecham o caso.
        #
        # 2021, eq. (4) com o W da eq. (3):   W₀^LVD = U(P) + T + H*·γ̄
        # 2020, eqs. (14)+(15)+(2)+(10):       W₀^LVD = W₀ − γ̄·((h − H* + t·V) − ζ_mod − ζ₀)
        #   onde a eq. (10) corrige a anomalia de altura de GNSS/nivelamento pela
        #   subsidência: V é a taxa anual interpolada de dados SAR do ALOS-1, t = 7 anos.
        rota_a=U_P + T + gamma * Hn,
        rota_b=W0 - gamma * ((h - Hn + t_lag * V_sar) - zeta_mod - zeta0),
        fonte="@vu2021vietname eqs. (3), (4) e (11), p. 3; @vu2020mekong eqs. (2), (10), "
              "(14) e (15), pp. 13–17",
        esperado=DADO_PROPRIO,
        # As 29 121 gravimetrias são as MESMAS nos dois trabalhos, logo `T` (Stokes, 2021) e
        # `ζ_mod` (GEOID_LSC, 2020) saem do mesmo dado e diferem por tratamento. `h` entra
        # nos dois (em 2021 pelo `U(P)`). O que entra numa rota só é `V`: a taxa de
        # subsidência é OBSERVAÇÃO — SAR —, e não deriva de `h`, `H*` nem da gravimetria.
        proprios=frozenset({V_sar}),
        nota="«This proves that the applied method is reliable»",
    ),
    Caso(
        chave="guoxue2023offset",
        rotas=("eq. (5): números geopotenciais", "eq. (12): problema de valor de contorno"),
        # ⚠️⚠️ TRADUÇÃO REFEITA A 2026-09-15, pelas equações lidas na página. A anterior
        # escrevia duas variantes da MESMA rota — uma com resíduos, outra sem — e não era o
        # que o artigo compara. As duas abordagens que ele confronta são:
        #     eq.  (5)  ΔH* = (W₀ − W(P) − H*·γ) / γ₀     ← números geopotenciais
        #     eq. (12)  ΔH* = h − H − N₀ − ζ_m            ← PVC
        rota_a=(W0 - W_P - Hn * gamma) / gamma0,
        rota_b=h - H_orto - N0 - zeta_mod,
        fonte="@guoxue2023offset eq. (5), p. 8, e eq. (12), p. 9",
        esperado=DADO_PROPRIO,
        # Cada rota consome grandeza que a outra não vê: a primeira o potencial no ponto e
        # a altura normal; a segunda a altura elipsoidal de GNSS, a ortométrica do
        # nivelamento, o termo de grau zero e a anomalia de altura do modelo.
        proprios=frozenset({W_P, Hn, h, H_orto, N0, zeta_mod}),
        nota="«Remarkably, these values are in agreement»; e a conclusão (3) abre por "
             "«Theoretical derivation and numerical analysis indicate…»",
    ),
)


def main() -> int:
    largura = max(len(c.chave) for c in CASOS)
    falhas = 0
    print(f"{'caso':<{largura}}  {'grau':<14}  diferenca das rotas")
    print("-" * (largura + 60))
    for caso in CASOS:
        grau, dif, proprios = gradua(caso)
        marca = "ok" if grau == caso.esperado else "DIVERGE"
        if grau != caso.esperado:
            falhas += 1
        print(f"{caso.chave:<{largura}}  {grau:<14}  {sp.srepr(dif) and sp.sstr(dif)}")
        print(f"{'':<{largura}}  {marca:<14}  rotas: {caso.rotas[0]} x {caso.rotas[1]}")
        if proprios:
            print(f"{'':<{largura}}  {'':<14}  dado proprio na diferenca: "
                  f"{', '.join(sorted(str(s) for s in proprios))}")
        print(f"{'':<{largura}}  {'':<14}  fonte: {caso.fonte}")
        print()
    print(f"{len(CASOS) - falhas} de {len(CASOS)} casos graduados como o manuscrito afirma.")
    return 1 if falhas else 0


def folha_de_conferencia() -> str:
    """A folha do lote 9 do `docs/monta_conferencia.py`, emitida DO CÓDIGO.

    ⚠️⚠️ **Este lote nasce de um erro que custou o título do artigo.** A tradução do caso
    argentino escrevia as duas rotas como duas reorganizações da mesma expressão, e o
    graduador — corretamente — devolveu identidade. As equações da fonte são outras, e a
    diferença entre elas não é nula. Nenhum portão o podia apanhar: todos leem a TRADUÇÃO,
    e nenhum lê o artigo original.

    ⇒ o que esta folha põe ao lado da página é, para cada caso, **a expressão que o
    graduador de facto recebe** — não uma transcrição à mão dela. Quem confere lê a
    equação impressa e pergunta uma coisa só: *é esta?*
    """
    linhas = [
        "# Lote 9 — as rotas que o teste de independência recebe",
        "",
        "**Gerado de `mapgravy/experiments/independencia_simbolica.py`.** Cada bloco traz a",
        "expressão que o graduador recebe, o grau que ela produz, e a passagem da fonte de",
        "onde foi lida. Confira contra as páginas que se seguem.",
        "",
        "⚠️ **O que se confere é se a rota escrita É a equação impressa.** Não se confere se",
        "o grau está certo: esse é consequência, e sai sozinho da expressão.",
        "",
    ]
    for caso in CASOS:
        grau, dif, proprios = gradua(caso)
        linhas += [
            f"## {caso.chave}",
            "",
            f"- **fonte declarada:** {caso.fonte}",
            f"- **rota A** ({caso.rotas[0]}): `{sp.sstr(caso.rota_a)}`",
            f"- **rota B** ({caso.rotas[1]}): `{sp.sstr(caso.rota_b)}`",
            f"- diferença: `{sp.sstr(dif)}`",
            f"- grau: **{grau}**"
            + (f" — sobrevive: {', '.join(sorted(str(s) for s in proprios))}" if proprios else ""),
            "",
        ]
    linhas += [
        "## Os símbolos, e o que cada um tem de ser na página",
        "",
        "| símbolo | o que é |",
        "|---|---|",
        "| `h` | altura elipsoidal do marco |",
        "| `H_ast` | altura normal |",
        "| `C` | número geopotencial local |",
        "| `T` | potencial perturbador do modelo |",
        "| `U_P` | potencial normal em `P`, nas coordenadas elipsoidais |",
        "| `U_0` | potencial normal na superfície do elipsoide |",
        "| `W_0^IHRF` | valor convencional do geopotencial de referência |",
        "| `gamma_barra` | gravidade normal média; `gamma_Q`, no teluroide |",
        "| `zeta_mod` | anomalia de altura do modelo gravimétrico |",
        "| `zeta_res_Stokes`, `zeta_RTM` | os resíduos que só uma das rotas vê |",
        "",
    ]
    return "\n".join(linhas)


if __name__ == "__main__":
    raise SystemExit(main())
