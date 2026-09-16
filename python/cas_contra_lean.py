"""O que um sistema de álgebra simbólica decide das cinco relações, e o que não decide.

⚠️⚠️ **Este experimento existe porque uma revisão adversarial fez a pergunta certa**:
*«por que Lean e não um CAS? `sympy.simplify` decide as identidades racionais numa linha,
num projeto que já é Python»*. A resposta honesta não é opinião — é correr o CAS. Corrido,
ele confirma metade da objeção e refuta a outra metade.

RESULTADO, em uma linha: **o `sympy` decide três das cinco em uma linha cada; as outras
duas não são exprimíveis nele**; e no que falha não é na álgebra, é nas HIPÓTESES — ele
aceita de bom grado um enunciado mal-posto, e até um enunciado errado.

⚠️ O que este experimento NÃO afirma: que Lean seja preferível para a classe racional. Para
essas três, um CAS é mais barato, e o manuscrito passa a dizê-lo.
"""
from __future__ import annotations

import sys

import sympy as sp

#: `simplify(e) == 0` é o teste de identidade usado em todo o ficheiro.
_zero = lambda e: sp.simplify(e) == 0


def r1_separacao_de_helmert() -> bool:
    """`ḡ − γ̄ = Δg_B`, com `γ_Q = g − Δg` e a média normal `γ_Q + (FA/2)H`."""
    g, FA, B, H = sp.symbols("g FA B H", positive=True)
    Dg = sp.Symbol("Delta_g")
    k = (FA - 2 * B) / 2
    gbar = g + k * H
    gammabar = (g - Dg) + FA / 2 * H
    return _zero((gbar - gammabar) - (Dg - B * H))


def r2_limite_rigido() -> bool:
    """`δₙ` e `D` valem 1 quando `h = k = 0`."""
    n, h, k = sp.symbols("n h k")
    delta = 1 + (2 / n) * h - ((n + 1) / n) * k
    D = 1 + k - h
    return (_zero(delta.subs({h: 0, k: 0}) - 1) and _zero(D.subs({h: 0, k: 0}) - 1))


def r3_razao_assintotica() -> tuple[bool, bool]:
    """A razão vale `−(1−2ν)/(2(1−ν))`, e `g` e `μ` somem dela.

    Devolve `(decide_o_valor, decide_a_invariancia)`. ⚠️ A invariância, que o manuscrito
    trata como o resultado, o CAS **também** a exibe: `g` e `μ` desaparecem da expressão
    simplificada. Dizer o contrário seria vender caro o que é barato.
    """
    g, nu, G, mu = sp.symbols("g nu G mu", positive=True)
    hinf = -g**2 * (1 - nu) / (2 * sp.pi * G * mu)
    nlinf = (1 - 2 * nu) * g**2 / (4 * sp.pi * G * mu)
    razao = sp.simplify(nlinf / hinf)
    return _zero(razao + (1 - 2 * nu) / (2 * (1 - nu))), not ({g, mu} & razao.free_symbols)


def hipotese_malposta_passa_no_cas() -> dict:
    """O CAS aceita `H = C/ḡ(H)` — o enunciado que o Lean RECUSOU — e o errado também.

    ⚠️⚠️ **É aqui que a diferença está, e não na álgebra.** O sistema de provas recusou a
    forma `H = C/ḡ(H)` porque `H` ocorre nos dois lados, e foi essa recusa que tornou
    visível que a altura de Helmert é definida por equação **implícita**. O CAS aceita-a,
    simplifica-a e devolve duas raízes — sem dizer qual é a física. E aceita, com a mesma
    naturalidade, uma versão ERRADA da hipótese (expoente trocado), devolvendo três.

    ⇒ um CAS computa com o que se lhe escreve; não tem noção de enunciado mal-posto nem de
    hipótese em falta. É a classe de defeito que este artigo trata.
    """
    g, FA, B, H, C = sp.symbols("g FA B H C", positive=True)
    k = (FA - 2 * B) / 2
    certa = sp.Eq(H, C / (g + k * H))
    errada = sp.Eq(H, C / (g + k * H**2))       # expoente trocado, defeito plausível
    return {"aceita_a_implicita": True,
            "raizes_da_implicita": len(sp.solve(certa, H)),
            "aceita_a_errada": True,
            "raizes_da_errada": len(sp.solve(errada, H))}


def grau_zero_no_cas():
    """⚠️ **Contra nós:** a vacuidade em `n = 0` NÃO é peculiaridade do Lean.

    O manuscrito registou que a divisão total do sistema de provas (`x/0 = 0`) torna o
    limite rígido demonstrável sem hipótese, o que o faz vazio em `n = 0`. Medido: o
    `sympy` cancela o `n` antes de substituir e devolve **o mesmo 1**. ⇒ a armadilha é da
    forma da expressão, não da ferramenta, e dizer que é do Lean seria escolher o exemplo
    que nos convém.
    """
    n, h, k = sp.symbols("n h k")
    delta = 1 + (2 / n) * h - ((n + 1) / n) * k
    return sp.simplify(delta.subs({h: 0, k: 0})).subs(n, 0)


#: As duas relações que um CAS não pode sequer ENUNCIAR, com a razão.
FORA_DO_ALCANCE = {
    "bem-postura (Hörmander ⟹ Lions–Sznitman)":
        "quantifica sobre os pontos da fronteira e fala de ângulos entre vetores num "
        "espaço com produto interno; e a recíproca exige CONSTRUIR um contraexemplo e "
        "provar que o é",
    "k'₀ = 0 por conservação de massa":
        "passa por uma EDO, por um argumento de constância num aberto conexo e pelo "
        "teorema fundamental do cálculo; o CAS resolve a EDO e não prova a unicidade "
        "sob as hipóteses declaradas",
}


def main() -> int:
    v3, inv3 = r3_razao_assintotica()
    decide = {"R1 separação de Helmert": r1_separacao_de_helmert(),
              "R2 limite rígido": r2_limite_rigido(),
              "R3 razão assintótica (valor)": v3,
              "R3 razão assintótica (invariância)": inv3}
    print("== o que o sympy DECIDE, numa linha cada ==")
    for nome, v in decide.items():
        print(f"   {'sim' if v else 'NAO':>4}  {nome}")
    print(f"\n== o que ele não pode sequer enunciar ({len(FORA_DO_ALCANCE)}) ==")
    for nome, razao in FORA_DO_ALCANCE.items():
        print(f"   {nome}\n      {razao}")
    h = hipotese_malposta_passa_no_cas()
    print("\n== onde a diferença está: as HIPÓTESES ==")
    print(f"   aceita `H = C/ḡ(H)`, que o Lean recusou, e devolve "
          f"{h['raizes_da_implicita']} raízes sem dizer qual é a física")
    print(f"   aceita a hipótese ERRADA (expoente trocado) e devolve "
          f"{h['raizes_da_errada']} raízes")
    print(f"\n== contra nós ==\n   delta(n=0, h=k=0) no sympy = {grau_zero_no_cas()} "
          "— a mesma vacuidade, logo ela não é do Lean")
    return 0


def _self_check() -> None:
    assert r1_separacao_de_helmert(), "R1 devia ser decidida pelo CAS"
    assert r2_limite_rigido(), "R2 devia ser decidida pelo CAS"
    v, inv = r3_razao_assintotica()
    assert v and inv, "R3 e a sua invariância deviam ser decididas pelo CAS"
    h = hipotese_malposta_passa_no_cas()
    assert h["raizes_da_implicita"] == 2 and h["raizes_da_errada"] == 3, h
    assert len(FORA_DO_ALCANCE) == 2
    assert grau_zero_no_cas() == 1, "a vacuidade em n=0 também ocorre no CAS"
    print("self-check OK")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        _self_check()
    else:
        raise SystemExit(main())
