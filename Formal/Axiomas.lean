/-
Copyright (c) 2026 Daniel Arana. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Daniel Arana
-/
import Formal.Helmert
import Formal.FatoresDeMare
import Formal.Boussinesq
import Formal.BemPostura
import Formal.Gauss

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
#print axioms Mapgravy.meanGravity_sub_meanNormalGravity
#print axioms Mapgravy.separation_is_identity
#print axioms Mapgravy.kHelmert_classical
#print axioms Mapgravy.meanGravityHelmert_classical
#print axioms Mapgravy.meanNormalGravity_classical
#print axioms Mapgravy.bouguerAnomaly_classical

#print axioms Mapgravy.gravimetricFactor_rigid
#print axioms Mapgravy.tiltFactor_rigid
#print axioms Mapgravy.rigid_limit_dichotomy
#print axioms Mapgravy.hInf_tendsto_zero_as_rigidity_diverges
#print axioms Mapgravy.nlInf_tendsto_zero_as_rigidity_diverges
#print axioms Mapgravy.displacement_vanishes_in_rigid_limit
#print axioms Mapgravy.gravimetricFactor_eq_one_iff
#print axioms Mapgravy.gravimetricFactor_degree_two
#print axioms Mapgravy.tiltFactor_prem
#print axioms Mapgravy.gravimetricFactor_prem

#print axioms Mapgravy.boussinesq_ratio
#print axioms Mapgravy.ratio_independent_of_g_and_mu
#print axioms Mapgravy.control_against_farrell
#print axioms Mapgravy.control_against_farrell_via_definitions

#print axioms Mapgravy.hormander_bounds_obliquity
#print axioms Mapgravy.acute_angle_iff_inner_positive
#print axioms Mapgravy.hormander_implies_lions_sznitman
#print axioms Mapgravy.lions_sznitman_not_implies_hormander

#print axioms Mapgravy.flux_accumulates_the_source
#print axioms Mapgravy.potential_minus_mass_is_constant
#print axioms Mapgravy.constant_on_open_interval
#print axioms Mapgravy.constant_is_zero
#print axioms Mapgravy.potential_equals_enclosed_mass
#print axioms Mapgravy.load_love_number_degree_zero_is_null
