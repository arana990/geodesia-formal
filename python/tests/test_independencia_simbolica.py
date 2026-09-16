"""Portões do graduador de independência entre duas rotas.

⚠️ O que estes portões protegem é o GRADUADOR, não a leitura dos artigos. A
tradução de cada artigo para símbolos é nossa e está citada no experimento; se
ela estiver errada, o veredito sai errado e nada aqui reprova (§0.3c #2).
"""

from __future__ import annotations

import re

import sympy as sp

from independencia_simbolica import (  # no mapgravy: mapgravy.experiments.independencia_simbolica
    CASOS,
    INDETERMINADO,
    DADO_PROPRIO,
    IDENTIDADE,
    PROPRIO,
    SO_PARTILHADO,
    Caso,
    gamma,
    gradua,
    h,
    zeta_mod,
    Hn,
)


def test_cada_caso_publicado_recebe_o_grau_que_o_manuscrito_afirma():
    for caso in CASOS:
        grau, dif, _ = gradua(caso)
        assert grau == caso.esperado, (caso.chave, grau, caso.esperado, dif)


def test_NENHUM_caso_publicado_e_identidade_estrita():
    """MORDE: declarar um dos três como identidade reprova, e a razão é um erro nosso.

    ⚠️⚠️ **Até 2026-09-15 este portão exigia o contrário** — que houvesse exatamente um caso
    de grau `IDENTIDADE`, o de `@tocho2024argentina`. Uma revisão adversarial mostrou que a
    tradução daquele caso para símbolos **assumia a conclusão**: escrevia as duas rotas como
    duas reorganizações da mesma expressão, em vez de as ler como a fonte as publica. Lendo
    a eq. (9) e a eq. (12) como estão, a diferença é o erro de linearização
    `(dγ/dh)·h·(h−2ζ)/2`, que vale `−16 cm` a `1000 m` — e os próprios autores escrevem que
    a eq. (9) é «only approximated theoretically».

    ⇒ **nenhum dos três casos publicados é identidade estrita**, e o artigo passa a dizê-lo.
    O que os une é outra coisa, mais robusta: na diferença entre as duas rotas de cada um
    não sobrevive grandeza que não tenha entrado nas duas — salvo em Guo e Xue, onde
    sobrevive, e por isso ele é do terceiro grau.
    """
    identidades = [c.chave for c in CASOS if c.esperado == IDENTIDADE]
    assert not identidades, (
        f"{identidades} declarado(s) como identidade estrita. Nenhum caso PUBLICADO o é; "
        "a identidade estrita deste trabalho é a separação geoide/quase-geoide, que é "
        "nossa e está provada em Lean.")


def test_o_graduador_MORDE_quando_se_tira_o_dado_proprio():
    """Sabotagem: sem os resíduos de Stokes e de terreno, Guo e Xue viraria identidade.

    Se este teste falhasse, o graduador estaria a devolver o esperado em vez de
    medir a expressão — e os três vereditos não valeriam nada.
    """
    # ⚠️ Desde 2026-09-15 há DOIS casos de grau 3 (Vu fechou nesse grau); sabota-se cada um.
    originais = [c for c in CASOS if c.esperado == DADO_PROPRIO]
    assert originais, "deixou de haver caso de dado próprio para sabotar"
    for original in originais:
        _sabota(original)


def _sabota(original):
    # ⚠️ A lista é do CASO desde 2026-09-15, não global — sabotar a global deixaria o
    # portão a medir o que já não existe, e ele passaria por ler a coisa errada.
    sem_proprio = Caso(
        chave=original.chave + "-sabotado",
        rotas=original.rotas,
        rota_a=original.rota_a,
        rota_b=original.rota_a,          # as duas rotas iguais ⇒ nada sobra na diferença
        fonte="sabotagem do portão",
        esperado=IDENTIDADE,
        proprios=original.proprios,
    )
    grau, dif, proprios = gradua(sem_proprio)
    assert grau == IDENTIDADE and dif == 0 and not proprios, (grau, dif)


def test_o_graduador_SEPARA_dado_proprio_de_residuo_so_partilhado():
    """Um resíduo que só reembrulha entradas partilhadas NÃO é dado próprio."""
    disfarcado = Caso(
        chave="residuo-de-entradas-partilhadas",
        rotas=("a", "b"),
        rota_a=-gamma * ((h - Hn) - zeta_mod),
        rota_b=-gamma * ((h - Hn) - zeta_mod) + gamma * sp.Rational(1, 100) * zeta_mod,
        fonte="construído",
        esperado=SO_PARTILHADO,
    )
    grau, dif, proprios = gradua(disfarcado)
    assert grau == SO_PARTILHADO, (grau, dif)
    assert not proprios and dif != 0, (dif, proprios)


def test_o_caso_que_NAO_SE_PODE_GRADUAR_declara_a_fonte_que_falta():
    """MORDE: marcar um caso como INDETERMINADO sem dizer o que falta reprova.

    ⚠️⚠️ **O quarto veredito não é um grau — é a recusa de graduar**, e existe desde
    2026-09-15 porque o caso de Vu não se pode decidir com o acervo. A diferença entre as
    duas rotas é `T − γ̄·ζ_mod`: o potencial perturbador integrado naquele trabalho contra
    o que o modelo de 2020 dá. Classificá-la exige saber se os dois saem do mesmo dado e
    do mesmo tratamento, e **o trabalho de 2020 não está no acervo**.

    ✅ **Declarar a ignorância é o resultado**, e é melhor que um grau adivinhado: foi
    adivinhar que produziu o erro do caso-título. Um caso indeterminado tem de nomear a
    fonte em falta, para que quem a obtiver saiba o que fazer com ela.
    """
    # ⚠️ Já não há caso indeterminado entre os três: o de Vu fechou quando o artigo de 2020
    # — que ESTAVA no acervo — foi lido. O veredito fica disponível, e o que se exige é que
    # quem o use nomeie a fonte em falta; verifica-se num caso sintético.
    from independencia_simbolica import Caso, h  # no mapgravy: mapgravy.experiments.independencia_simbolica
    sintetico = Caso(chave="sintetico", rotas=("a", "b"), rota_a=h, rota_b=2 * h,
                     fonte="eq. (1)", esperado=INDETERMINADO, falta="@obra_que_falta")
    assert gradua(sintetico)[0] == INDETERMINADO
    indeterminados = [c for c in CASOS if c.esperado == INDETERMINADO] + [sintetico]
    for caso in indeterminados:
        assert caso.falta, f"{caso.chave}: indeterminado sem dizer o que falta"
        assert "@" in caso.falta, (
            f"{caso.chave}: o que falta tem de nomear a CHAVE da fonte, para se poder ir "
            f"buscá-la: {caso.falta!r}")


def test_os_simbolos_PROPRIOS_sao_por_caso_e_nao_globais():
    """MORDE: voltar a classificar por uma lista global reprova.

    ⚠️ Era global até 2026-09-15, e estava errado: `h` entra nas duas rotas do caso
    argentino, logo é partilhado ali — mas nada garante que o seja noutro caso. Um grau
    calculado com a lista errada é tão falso quanto uma expressão mal escrita, e não se
    distingue dela por nenhum sinal exterior.
    """
    campos = {f.name for f in CASOS[0].__dataclass_fields__.values()}
    assert "proprios" in campos, "o caso deixou de declarar os seus próprios símbolos"
    (guoxue,) = [c for c in CASOS if c.chave == "guoxue2023offset"]
    _, dif, proprios = gradua(guoxue)
    assert proprios, "o caso de grau 3 deixou de identificar o que sobra na diferença"


def test_toda_rota_declara_a_EQUACAO_NUMERADA_que_traduz():
    """MORDE: um caso cuja `fonte` não nomeie equações numeradas reprova.

    ⚠️⚠️ **Nasceu do pior achado desta frente.** Ao conferir as quatro fontes na página, o
    autor perguntou se as expressões que tínhamos **existiam** nos artigos. Duas não
    existiam: nem a de Vu — cujas `21` equações numeradas não contêm `W₀ − γ̄H*` nem `h` —,
    nem a de Guo e Xue, cuja eq. (12) é `ΔH* = h − H − N₀ − ζ_m`, em **alturas e sem `γ`**,
    onde nós escrevíamos `−γ̄((h − H*) − ζ_mod)`.

    ⇒ o modo de falha não era «lemos a equação errada». Era **«escrevemos o que
    esperávamos que a equação dissesse»** — expressões montadas de conhecimento geral,
    nunca lidas na página. Um `sympy` não distingue as duas coisas, e nenhum portão o pode
    fazer.

    ✅ **O que ESTE portão faz, e é modesto:** obriga cada caso a nomear a equação numerada
    que diz traduzir. Não verifica a tradução — verifica que ela se compromete com um alvo
    conferível, e é esse compromisso que torna o lote 9 do `docs/monta_conferencia.py`
    possível. A conferência continua a ser humana, e está registada em
    `docs/formulas_conferidas.md`.
    """
    sem_equacao = [c.chave for c in CASOS if not re.search(r"eqs?\. \(\d", c.fonte)]
    assert not sem_equacao, (
        f"{sem_equacao}: a fonte não nomeia equação numerada. Uma rota que não se "
        "compromete com uma equação da página não pode ser conferida contra ela — e foi "
        "assim que duas traduções inventadas sobreviveram.")

