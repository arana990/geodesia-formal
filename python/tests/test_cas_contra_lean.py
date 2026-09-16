"""O que o manuscrito afirma sobre o CAS continua verdade — verificado todos os dias.

⚠️ **Irmão IN-PROCESS do `test_experimentos_self_check.py`, e existe por medida.** Aquele
corre os `_self_check()` por subprocesso e está todo marcado `slow`: 16 interpretadores a
importar `numpy`/`sympy`/`matplotlib` ao lado de 10 trabalhadores do `xdist` levaram o laço
rápido de `~100 s` a `4m44`, com dois a rebentar por timeout. Aqui importa-se o módulo, sem
subprocesso e sem escrever ficheiro, e o custo cai para o de umas simplificações.

⚠️ **Por que ESTE e não os outros:** a §1.5 do `draft3.md` afirma coisas que só este
experimento sustenta — *«decide três das cinco»*, *«a invariância também»*, *«aceita a
forma implícita que foi recusada»*. Se o `sympy` mudar de comportamento numa versão futura,
o manuscrito passa a afirmar o que já não é verdade, e é no laço diário que isso tem de
aparecer. Os outros `_self_check()` verificam sobretudo que um PNG foi escrito.
"""
from __future__ import annotations

import cas_contra_lean as cas  # no mapgravy: mapgravy.experiments.cas_contra_lean


def test_o_CAS_decide_as_tres_relacoes_racionais():
    """A metade da objeção do revisor que PROCEDE, e que o manuscrito concede."""
    assert cas.r1_separacao_de_helmert(), "a separação de Helmert devia ser decidida"
    assert cas.r2_limite_rigido(), "o limite rígido devia ser decidido"
    valor, invariancia = cas.r3_razao_assintotica()
    assert valor, "o valor da razão assintótica devia ser decidido"
    assert invariancia, "a INVARIÂNCIA também — g e mu somem da razão simplificada"


def test_o_CAS_aceita_a_hipotese_que_o_sistema_de_provas_RECUSOU():
    """A metade que NÃO procede, e que é o argumento do manuscrito.

    Um CAS calcula com o que se lhe escreve: aceita a forma implícita `H = C/ḡ(H)` e
    devolve duas raízes sem dizer qual é a física, e aceita uma hipótese ERRADA devolvendo
    três. É a distinção que este artigo trata, aplicada à ferramenta.
    """
    r = cas.hipotese_malposta_passa_no_cas()
    assert r["raizes_da_implicita"] == 2, r
    assert r["raizes_da_errada"] == 3, r


def test_a_vacuidade_em_n_zero_NAO_e_do_sistema_de_provas():
    """⚠️ O exemplo contra nós, e por isso o mais importante de trancar.

    O manuscrito diz que o enunciado em `n = 0` fecha sem afirmar nada **nas duas
    ferramentas**. Se um dia isto deixasse de valer no `sympy`, a frase do artigo passaria
    a escolher o exemplo conveniente — e ninguém daria por isso.
    """
    assert cas.grau_zero_no_cas() == 1


def test_as_duas_relacoes_fora_do_alcance_estao_declaradas():
    assert len(cas.FORA_DO_ALCANCE) == 2, cas.FORA_DO_ALCANCE
