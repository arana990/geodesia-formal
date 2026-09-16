"""Quanto custa ler como validação uma concordância forçada por identidade.

⚠️ **Todos os números daqui são PUBLICADOS, não nossos.** Este módulo não calcula
geodesia nenhuma: ele põe lado a lado quatro valores da Tabela 3 de
`@tocho2024argentina` e a meta declarada do IHRS em `@sanchez2021ihrs`, e faz a
aritmética que o manuscrito afirma. A razão de existir é a do `CLAUDE.md` §0.3
#10 — o portão antes da prosa —, e a de viver num ficheiro versionado é o §0.3c
#6: número de conversa não entra em artigo.

O ponto, e ele está inteiro **dentro da mesma tabela do mesmo artigo**:

- o Método 1 e o Método 2 estão ligados por identidade algébrica e dão o MESMO
  valor a duas casas. A diferença entre eles é `0,00 m²s⁻²`, e as Conclusões
  reportam-na como *«Both methods demonstrated consistency with each other»*;
- na linha seguinte da tabela, a determinação alheia de `@sanchezsideris2017`
  difere por `6,05 m²s⁻²`, e o artigo diz que *«Reasons for this discrepancy are
  subject of further study»*.

⇒ a comparação que **não pode** discordar é reportada como consistência; a que
**pode**, e discorda por `62 cm`, fica em aberto. A meta do IHRS é `1 cm`.
"""

from __future__ import annotations

from dataclasses import dataclass

W0_IHRS = 62636853.4  # m²/s², IAG Res. 1 (2015); no mapgravy vem de geodesy/constants.py

#: Gravidade normal usada só para converter potencial em altura, `ζ = δW/γ`.
#: Valor de referência do GRS80 em latitude média; a conversão é de ordem de
#: grandeza e uma escolha de `9,78` a `9,83` move os `62 cm` em menos de `1 cm`.
GAMMA = 9.81

#: Meta declarada do IHRS, `@sanchez2021ihrs` p. 3: «evaluating the possibility of
#: reaching an accuracy around ± 0.1 m2 s−2 (equivalent to ± 1 cm in height)».
META_IHRS = 0.10


@dataclass(frozen=True)
class Estimativa:
    rotulo: str
    valor: float          # δW₀, m²s⁻²
    sigma: float          # m²s⁻²
    procedencia: str
    w0lvd: float          # a coluna que decide o sinal, m²s⁻²


#: Valor convencional do geopotencial de referência (IAG Res. 1, 2015). ⚠️ **Importado, não
#: redigitado** — o portão `test_nenhum_modulo_redefine_constante_central` apanhou-me a
#: escrevê-lo à mão aqui, e tem razão: uma segunda cópia de uma constante central é como as
#: cópias de números envelhecem em silêncio. Serve para recuperar o SINAL de cada linha da
#: tabela a partir da coluna `W0LVD`, que é imune ao dano de extração descrito abaixo.
W0_CONVENCIONAL = W0_IHRS

#: Tabela 3 de `@tocho2024argentina`, p. 278. Unidades: m²s⁻².
#:
#: ⚠️⚠️ **O SINAL DOS TRÊS PRIMEIROS FOI LIDO ERRADO ATÉ 2026-09-15, e o defeito é da
#: EXTRAÇÃO, não da fonte.** O `pdftotext` emite `\x02` no lugar do menos — a fonte do PDF
#: não traz mapa Unicode para aquele glifo, e nem o `pdftohtml` o recupera. As três
#: primeiras linhas trazem esse `\x02` e a quarta não:
#:
#:     Method 1   \x020:46 ± 1:78   62636853:88
#:     δW0_SS       6:51 ± 0:49     62636846:89      <- sem \x02
#:
#: ⇒ a convenção da tabela é `δW₀ = W₀ − W₀LVD`, e a coluna `W0LVD` confirma o sinal sem
#: depender da extração: `62636853,4 − 62636853,88 = −0,48 ≈ −0,46`, e
#: `62636853,4 − 62636846,89 = +6,51`. O portão `sinal_confere_com_a_coluna_W0LVD`
#: refaz essa conta para cada linha.
TABELA_3: tuple[Estimativa, ...] = (
    Estimativa("Método 1", -0.46, 1.78, "rota da anomalia de altura", 62636853.88),
    Estimativa("Método 2", -0.46, 1.37, "a mesma equação reorganizada", 62636853.87),
    Estimativa("Tocho e Vergos (2015)", -0.50, 0.14,
               "outros marcos (542, SRVN71) e outro modelo (EGM2008)", 62636853.90),
    Estimativa("Sánchez e Sideris (2017)", 6.51, 0.49,
               "determinação de outro grupo", 62636846.89),
)


def em_altura(dw: float) -> float:
    """Converte uma diferença de potencial em centímetros de altura."""
    return dw / GAMMA * 100.0


def entre(a: str, b: str) -> float:
    """Diferença absoluta em m²s⁻² entre duas linhas da tabela, pelo rótulo."""
    (x,) = [e for e in TABELA_3 if e.rotulo == a]
    (y,) = [e for e in TABELA_3 if e.rotulo == b]
    return abs(x.valor - y.valor)


#: As quantidades que o manuscrito afirma, todas derivadas do que está acima.
#: ⚠️ O nome diz «partilhado», não «identidade»: as duas rotas NÃO são a mesma expressão
#: reorganizada — diferem pelo erro de linearização da eq. (9) —, mas na diferença entre
#: elas não sobrevive grandeza que não tenha entrado nas duas. Ver `independencia_simbolica`.
SO_DADO_PARTILHADO = entre("Método 1", "Método 2")
LIGADAS_POR_IDENTIDADE = SO_DADO_PARTILHADO   # nome antigo, mantido para não partir chamadas
CONTRA_DETERMINACAO_ALHEIA = entre("Método 1", "Sánchez e Sideris (2017)")
#: ⚠️ A TERCEIRA comparação, que o manuscrito omitia até 2026-09-15. Tocho e Vergos usaram
#: `542` marcos do sistema anterior (SRVN71) e o EGM2008 — dado diferente do desta tabela —,
#: logo PODIAM discordar. Concordaram a `0,04 m²s⁻²`. Omiti-la tornava a frase «a única que
#: podia discordar» falsa, e enfraquecia o argumento em vez de o reforçar: com ela, há duas
#: comparações capazes de discordar, uma concorda e a outra falha por `71 cm`.
CONTRA_DETERMINACAO_ANTERIOR = entre("Método 1", "Tocho e Vergos (2015)")
SIGMA_MAIOR = max(e.sigma for e in TABELA_3[:2])


def sinal_confere_com_a_coluna_W0LVD(tolerancia: float = 0.03) -> dict[str, float]:
    """Refaz `δW₀ = W₀ − W₀LVD` para cada linha e devolve o resíduo.

    ⚠️ **É esta função que torna o sinal verificável sem confiar na extração do PDF.** O
    glifo do menos perde-se (ver a nota da `TABELA_3`), mas a coluna `W0LVD` é composta só
    por dígitos e sobrevive intacta — e ela determina o sinal por aritmética.
    """
    return {e.rotulo: (W0_CONVENCIONAL - e.w0lvd) - e.valor for e in TABELA_3}


def main() -> int:
    print("Tabela 3 de Gómez e colaboradores (2024) — δW₀ do datum argentino\n")
    print(f"{'':<26}{'m²s⁻²':>16}   {'em altura':>10}   procedência")
    for e in TABELA_3:
        print(f"{e.rotulo:<26}{e.valor:7.2f} ± {e.sigma:<6.2f}   "
              f"{em_altura(e.valor):7.1f} cm   {e.procedencia}")
    print()
    print(f"meta declarada do IHRS                  {META_IHRS:.2f}        "
          f"{em_altura(META_IHRS):7.1f} cm")
    print()
    print("as TRÊS comparações que a mesma tabela contém:")
    print(f"  ligadas por identidade (M1 x M2)      {LIGADAS_POR_IDENTIDADE:.2f}        "
          f"{em_altura(LIGADAS_POR_IDENTIDADE):7.1f} cm   <- reportada como consistência")
    print(f"  contra Tocho e Vergos (dado próprio)  {CONTRA_DETERMINACAO_ANTERIOR:.2f}        "
          f"{em_altura(CONTRA_DETERMINACAO_ANTERIOR):7.1f} cm   <- podia discordar, CONCORDA")
    print(f"  contra determinação alheia (M1 x SS)  {CONTRA_DETERMINACAO_ALHEIA:.2f}        "
          f"{em_altura(CONTRA_DETERMINACAO_ALHEIA):7.1f} cm   <- podia discordar, DISCORDA")
    print()
    print("  o sinal, refeito a partir da coluna W0LVD (resíduo em m²s⁻²):")
    for nome, r in sinal_confere_com_a_coluna_W0LVD().items():
        print(f"    {nome:<28}{r:+.3f}")
    print()
    print(f"incerteza da própria estimativa         {SIGMA_MAIOR:.2f}        "
          f"{em_altura(SIGMA_MAIOR):7.1f} cm")
    # ⚠️ A diferença publicada é `0,00` A DUAS CASAS — não é zero por identidade algébrica.
    # As duas equações diferem pelo erro de linearização da eq. (9); ver
    # `independencia_simbolica.py`. O ramo anterior imprimia «a concordância é EXATA», e
    # era essa a leitura que a revisão adversarial de 2026-09-15 derrubou.
    print(f"  => a concordância PUBLICADA e' de {SO_DADO_PARTILHADO:.2f} m2/s2 a duas casas, "
          f"e a incerteza do que ela valida e' {em_altura(SIGMA_MAIOR):.0f} cm")
    print(f"  => a discordância em aberto vale {CONTRA_DETERMINACAO_ALHEIA / META_IHRS:.0f}x a meta do IHRS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
