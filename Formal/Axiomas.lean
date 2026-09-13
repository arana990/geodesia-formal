/-
Copyright (c) 2026 Daniel Arana. All rights reserved.
Released under GPL-3.0 license as described in the file LICENSE.
Authors: Daniel Arana
-/
import Formal.Helmert
import Formal.FatoresDeMare
import Formal.Boussinesq
import Formal.BemPostura
import Formal.Gauss

set_option linter.style.header false

/-!
# O portão de VERDADE das provas deste diretório

⚠️⚠️ **`lake build` verde NÃO basta**, e é a razão de este ficheiro existir. Uma prova com
`sorry` compila; o que ela deixa é um `sorryAx` na lista de axiomas. Este ficheiro imprime
os axiomas de cada teorema **no próprio build**, e o portão de Python
(`mapgravy/tests/test_formal.py`) exige que só apareçam os três padrão do Lean:
`propext`, `Classical.choice`, `Quot.sound`.

⚠️ **Todo teorema novo entra aqui no MESMO commit em que é provado.** Um teorema fora
desta lista não é verificado por ninguém — e há portão que compara as duas listas.
-/

#print axioms Mapgravy.kHelmert_sub_half_FA
#print axioms Mapgravy.gBarra_sub_gammaBarra
#print axioms Mapgravy.separacao_e_identidade
#print axioms Mapgravy.kHelmert_classico
#print axioms Mapgravy.gBarraHelmert_classico
#print axioms Mapgravy.gammaBarra_classico
#print axioms Mapgravy.disturbioBouguer_classico

#print axioms Mapgravy.delta_rigido
#print axioms Mapgravy.gama_rigido
#print axioms Mapgravy.dicotomia_do_limite_rigido
#print axioms Mapgravy.hInf_tende_a_zero_na_rigidez
#print axioms Mapgravy.nlInf_tende_a_zero_na_rigidez
#print axioms Mapgravy.deslocamento_desaparece_no_limite_rigido
#print axioms Mapgravy.delta_eq_one_iff
#print axioms Mapgravy.delta_grau_dois
#print axioms Mapgravy.gama_prem
#print axioms Mapgravy.delta_prem

#print axioms Mapgravy.razao_de_boussinesq
#print axioms Mapgravy.razao_nao_depende_de_g_nem_de_mu
#print axioms Mapgravy.controlo_contra_farrell
#print axioms Mapgravy.controlo_contra_farrell_nas_definicoes

#print axioms Mapgravy.hormander_limita_a_obliquidade
#print axioms Mapgravy.angulo_agudo_iff_produto_interno_positivo
#print axioms Mapgravy.hormander_implica_lions_sznitman
#print axioms Mapgravy.lions_sznitman_nao_implica_hormander

#print axioms Mapgravy.fluxo_acumula_a_fonte
#print axioms Mapgravy.potencial_menos_massa_e_constante
#print axioms Mapgravy.constante_no_aberto
#print axioms Mapgravy.constante_e_zero
#print axioms Mapgravy.potencial_iguala_a_massa_encerrada
#print axioms Mapgravy.k_carga_do_grau_zero_e_nulo
