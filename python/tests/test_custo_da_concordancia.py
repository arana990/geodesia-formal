"""Portões dos números publicados que sustentam a consequência do `draft3.md`.

⚠️ A regra desta casa é o §0.3c #2: *contra o quê, exatamente?* Aqui é contra os
PDFs de `@tocho2024argentina` e `@sanchez2021ihrs` — não contra o módulo, que
seria circular. Sem o acervo em disco os portões de fonte dão `skip`, e os de
aritmética continuam a correr.
"""

from __future__ import annotations

import pathlib
import re
import subprocess

import pytest

from custo_da_concordancia import (  # no mapgravy: mapgravy.experiments.custo_da_concordancia
    CONTRA_DETERMINACAO_ALHEIA,
    CONTRA_DETERMINACAO_ANTERIOR,
    sinal_confere_com_a_coluna_W0LVD,
    LIGADAS_POR_IDENTIDADE,
    META_IHRS,
    TABELA_3,
    em_altura,
)

_BIB = pathlib.Path(__file__).resolve().parents[2] / "bibliografia"


def _digitos(pdf: str, layout: bool = True) -> str:
    caminho = _BIB / pdf
    if not caminho.exists():
        pytest.skip(f"{pdf} não está no acervo desta máquina")
    cmd = ["pdftotext"] + (["-layout"] if layout else []) + [str(caminho), "-"]
    saida = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    return re.sub(r"\D", "", saida)


def _letras(pdf: str) -> str:
    caminho = _BIB / pdf
    if not caminho.exists():
        pytest.skip(f"{pdf} não está no acervo desta máquina")
    saida = subprocess.run(
        ["pdftotext", str(caminho), "-"], capture_output=True, text=True, check=True
    ).stdout
    return re.sub(r"[^a-z]", "", saida.lower())


@pytest.mark.parametrize("e", TABELA_3, ids=lambda e: e.rotulo)
def test_cada_valor_da_tabela_3_ocorre_no_PDF_de_Gomez(e):
    """MORDE: mudar uma casa decimal de qualquer linha reprova.

    O `pdftotext` estraga a pontuação do artigo (`0:46 ˙ 1:78` pelo `0,46 ± 1,78`),
    então o que se compara é a corrida de DÍGITOS, que sobrevive ao dano.

    ⚠️⚠️ **E é por isso que ele NÃO basta, o que se descobriu do pior modo em 2026-09-15.**
    Uma corrida de dígitos é **cega ao sinal**: `046178` casa com `+0,46` e com `−0,46`. Os
    três primeiros valores desta tabela são NEGATIVOS, o manuscrito publicou-os positivos
    durante dois dias, e este portão esteve verde o tempo todo. O irmão abaixo é que fecha
    a lacuna, e a lição é a do §0.3c: *o portão afirma o quê, exatamente?* — este afirma
    que os dígitos ocorrem, nunca que a quantidade é a certa.
    """
    alvo = f"{abs(e.valor):.2f}{e.sigma:.2f}".replace(".", "")
    assert alvo in _digitos("tocho2024argentina.pdf"), (e.rotulo, alvo)


def test_o_SINAL_de_cada_linha_e_refeito_pela_coluna_W0LVD():
    """MORDE: trocar o sinal de qualquer linha da tabela reprova.

    ⚠️⚠️ **Nasceu de um erro publicado.** O glifo do menos perde-se na extração — o
    `pdftotext` emite `\x02`, e o `pdftohtml` também não o recupera, porque a fonte do PDF
    não traz mapa Unicode para aquele glifo. Medido no acervo inteiro: **`160` de `160`
    ficheiros extraídos têm caracteres de controlo**, e `U+0002` aparece `16 575` vezes.
    Ler um número dali e confiar no sinal é, portanto, sempre inseguro.

    ✅ **O remédio não é extrair melhor — é CRUZAR.** A coluna `W0LVD` da mesma tabela é
    composta só por dígitos, sobrevive intacta, e determina o sinal por aritmética:
    `δW₀ = W₀ − W₀LVD` com o `W₀` convencional. Este portão refaz essa conta para as
    quatro linhas.

    ⚠️ A tolerância é `0,03 m²s⁻²` porque a tabela publica `δW₀` a duas casas e o `W₀LVD`
    a duas: o arredondamento das duas colunas não tem de fechar exatamente.
    """
    residuos = sinal_confere_com_a_coluna_W0LVD()
    fora = {n: r for n, r in residuos.items() if abs(r) > 0.03}
    assert not fora, (
        f"o sinal ou o valor não batem com a coluna W0LVD: {fora}. "
        "É a coluna que decide — o glifo do menos não sobrevive à extração.")


def test_a_meta_do_IHRS_esta_declarada_na_fonte_e_e_de_um_centimetro():
    """A frase de `@sanchez2021ihrs` p. 3 que fixa `±0,1 m²s⁻² = ±1 cm`.

    ⚠️ **Este portão existe porque o irmão não alcança esta frase.** O
    `test_toda_citacao_textual_VEM_DA_FONTE_que_o_marcador_declara` compara
    contra `bibliografia/md/`, e a extração DESTA fonte funde as duas colunas:
    logo a seguir a «± 1 cm» entra texto da coluna vizinha, e o «in height»
    nunca lá aparece. O manuscrito cita por isso só até «± 1 cm», que fica
    abaixo do limiar de 18 letras daquele portão e é saltada por ele. Aqui a
    frase INTEIRA é conferida, e contra o PDF, que não tem esse dano.
    """
    letras = _letras("sanchez2021ihrs.pdf")
    assert "equivalenttocminheight" in letras, "a frase inteira, contígua, na fonte"
    assert "reachinganaccuracyaround" in letras
    assert abs(em_altura(META_IHRS) - 1.0) < 0.05, em_altura(META_IHRS)


def test_as_duas_rotas_ligadas_por_identidade_concordam_EXATAMENTE():
    """Não «muito bem»: a duas casas publicadas, a diferença é zero.

    É a diferença entre este caso e uma concordância medida — e é o que a
    [@sec:intro-literatura] afirma.
    """
    assert LIGADAS_POR_IDENTIDADE == 0.0, LIGADAS_POR_IDENTIDADE


def test_a_comparacao_que_PODE_discordar_discorda_por_mais_de_meio_metro():
    """E é a que o artigo deixa em aberto, enquanto reporta a outra como consistência."""
    assert CONTRA_DETERMINACAO_ALHEIA > 6.5, CONTRA_DETERMINACAO_ALHEIA
    assert 68.0 < em_altura(CONTRA_DETERMINACAO_ALHEIA) < 74.0
    assert CONTRA_DETERMINACAO_ALHEIA / META_IHRS > 60.0


def test_a_TERCEIRA_comparacao_podia_discordar_e_CONCORDA():
    """MORDE: esquecer a comparação contra Tocho e Vergos reprova o enunciado do artigo.

    ⚠️⚠️ **O manuscrito dizia que a de Sánchez e Sideris era «a única que podia
    discordar», e era falso.** Tocho e Vergos (2015) usaram `542` marcos do sistema
    anterior (SRVN71) e o EGM2008 — dado diferente do desta tabela —, logo podiam
    discordar. Concordaram a `0,04 m²s⁻²`, e as conclusões do próprio artigo o dizem:
    *«Results agree with the previous estimation of Tocho and Vergos (2015) but show
    differences with the one made by Sánchez and Sideris (2017)»*.

    ✅ Incluí-la **reforça** o argumento em vez de o enfraquecer: das três comparações da
    tabela, as duas que podiam discordar dão `0,4 cm` e `71 cm`, e a que não podia dá
    `0,0` — e é esta última que as conclusões reportam como consistência entre métodos.
    """
    assert CONTRA_DETERMINACAO_ANTERIOR < 0.10, CONTRA_DETERMINACAO_ANTERIOR
    assert em_altura(CONTRA_DETERMINACAO_ANTERIOR) < 1.0
    # e ela é MENOR que a meta do IHRS, o que é o ponto
    assert CONTRA_DETERMINACAO_ANTERIOR < META_IHRS


def test_a_incerteza_declarada_e_uma_ordem_acima_da_meta_do_IHRS():
    """O que torna a leitura cara: a concordância é exata, o que ela valida é decimétrico."""
    sigma = max(e.sigma for e in TABELA_3[:2])
    assert em_altura(sigma) > 10.0, em_altura(sigma)
    assert sigma / META_IHRS > 10.0, sigma / META_IHRS
