/-
Copyright (c) 2026 Daniel Arana. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Daniel Arana
-/
import Mathlib

/-!
# A maré permanente de Ekman (1989): o que é conversão e o que é constante

Formalização do registo `geodesy/conventions.py` (Paper 4; inventário em
`docs/inventario_convencoes_formal.md`). As fórmulas são as de Ekman (1989), *Impacts of
geodynamic phenomena on systems for height and gravity*, Bull. Géod. 63.

↩️ **Revisto em 2026-09-16 depois de um parecer adversarial**
(`docs/pareceres/paper4_revisao_adversarial_2026-09-16.md`), que classificou os oito teoremas
da primeira versão como vazios ou tautológicos, e que estava certo. O que este ficheiro
afirma hoje é dito com o alcance que o parecer mediu:

* **Nenhum teorema aqui é matemática:** o `sympy` decide todos numa linha. O que eles
  compram é (i) prender os sete literais de Ekman e a relação entre eles num sítio que não
  compila se um mudar sem o outro, e (ii) escrever a hipótese sob a qual cada relação vale.
* **T7 tem poder discriminante de ~1 %**, não mais: apanha um dígito transposto entre os
  dois pares de constantes, não uma fonte errada. Se Ekman tivesse derivado os dois pares
  do mesmo `A` errado, T7 fechava na mesma. As tolerâncias são as que a fonte declara
  («within 0.1 cm and 0.1 µgal», p. 281), e não o resíduo observado.
* **T3 não é descoberta.** O comentário de `_levels_height_diff` omite o termo da crosta, e
  o teste `test_eq12_deriva_da_eq15_por_H_igual_h_menos_N`, do mesmo commit, já dizia que
  a relação «deixa de valer sem o termo de deformação» nos pares com *tide-free*. O teorema
  transcreve isso — e, nesta versão, sem excluir sistema nenhum: a crosta é um nível por
  sistema, nulo no *tide-free*, e a identidade vale nos três.
* **`converte_*` valem para QUALQUER função de níveis.** Não protegem o registo de um nível
  editado num só ramo — protegem a forma «converter = somar diferença de níveis», que é o
  que `tide_convert` faz, e nada mais.

## Física (para o leitor, não para o verificador)

A eq. (1), `W/g = 9,9 − 29,6 sin²φ` cm, e a eq. (2), `−∂W/∂r = −30,4 + 91,2 sin²φ` µGal, são o
MESMO potencial `W` — Ekman di-lo na página («*N = W/g, as well as […] g = −∂W/∂r*»), sem o
fator de Love `δ`, que só entra na eq. (3). Para um potencial zonal de grau 2,
`W = A r² (1 − 3 sin²φ)`, vale `∂W/∂r = 2W/r`, logo `C0_grav = −2g·C0_geoide/R` e a razão dos
coeficientes é `3` em módulo nos dois pares. Isso é o que T7 prende — e é o que o registo
Python tem como quatro literais independentes, sem nada que os ligue.
-/

namespace Mapgravy

/-! ## As constantes de Ekman, presas ao valor publicado

⚠️ Vivem também em `geodesy/conventions.py` (`EKMAN_*`, `LOVE_K`, `LOVE_H`, `DELTA_GRAV`),
e **nada liga as duas cópias** — é o item D1 do parecer, por fazer. -/

/-- Eq. (1), termo constante do nível do geoide, em cm. -/
noncomputable def ekmanGeoidC0 : ℝ := 9.9
/-- Eq. (1), coeficiente de `sin²φ`, em cm, guardado POSITIVO: a eq. (1) é `C0 − C2·sin²φ`. -/
noncomputable def ekmanGeoidC2 : ℝ := 29.6
/-- Eq. (2), termo constante da gravidade, em µGal. -/
noncomputable def ekmanGravityC0 : ℝ := -30.4
/-- Eq. (2), coeficiente de `sin²φ`, em µGal: a eq. (2) é `C0 + C2·sin²φ`. -/
noncomputable def ekmanGravityC2 : ℝ := 91.2
/-- Número de Love do potencial, `k = 0,30` (p. 282, antes da eq. (5), cf. Melchior 1978). -/
noncomputable def loveK : ℝ := 0.30
/-- Número de Love do deslocamento vertical, `h = 0,62` (§1.5, eq. (18)). -/
noncomputable def loveH : ℝ := 0.62
/-- Fator gravimétrico da correção tradicional, `δ = 1,16` (eq. (3)). -/
noncomputable def deltaGrav : ℝ := 1.16

/-- O `γ` de Ekman, eq. (6): NÃO é literal. A eq. (17) tem `(1 + k)` onde a eq. (21) tem
`(γ + h)`, logo `γ = 1 + k − h`. -/
noncomputable def gammaEkman : ℝ := 1 + loveK - loveH

/-- **T2.** O `γ` derivado reproduz o `0,68` que Ekman imprime. É aritmética; o que prende
é que `gammaEkman` seja DERIVADO e não digitado. -/
theorem gammaEkman_eq : gammaEkman = 0.68 := by
  unfold gammaEkman loveK loveH; norm_num

/-! ## T7 — os dois pares de constantes são UM par

As tolerâncias abaixo saem da precisão que Ekman declara (p. 281: «within 0.1 cm and
0.1 µgal»), propagada: com `C0 ∈ [9,8; 10,0]` e `C2 ∈ [29,5; 29,7]`, a razão do geoide fica
em `[2,95; 3,03]`, logo `|C2/C0 − 3| ≤ 0,05`; para a gravidade, `|C2/C0 + 3| ≤ 0,014`; e o
`C0` da gravidade previsto do do geoide varia de `30,14` a `30,79` µGal conforme `C0` e
`R ∈ [6 371; 6 378] km`, logo `|previsto − publicado| ≤ 0,4`. ⚠️ A primeira versão usava
`0,011` e `0,1`, sintonizados ao resíduo observado — o parecer apanhou-o. -/

/-- Gravidade média usada na conversão cm → µGal, m/s². ⚠️ Redigitada; ver D1. -/
noncomputable def gravidadeMedia : ℝ := 9.80665
/-- Raio médio da Terra, m. ⚠️ Redigitado; ver D1. -/
noncomputable def raioMedio : ℝ := 6371000

/-- **T7a.** Na eq. (2), `C2/C0 = −3` dentro da precisão declarada (exato nos literais). -/
theorem ekmanGravity_ratio_is_degree_two :
    |ekmanGravityC2 / ekmanGravityC0 + 3| ≤ 0.014 := by
  unfold ekmanGravityC2 ekmanGravityC0
  rw [abs_le]; constructor <;> norm_num

/-- **T7b.** Na eq. (1), `C2/C0 = 3` (com `C2` guardado positivo) dentro da precisão
declarada: `29,6/9,9 = 2,990`. -/
theorem ekmanGeoid_ratio_is_degree_two :
    |ekmanGeoidC2 / ekmanGeoidC0 - 3| ≤ 0.05 := by
  unfold ekmanGeoidC2 ekmanGeoidC0
  rw [abs_le]; constructor <;> norm_num

/-- **T7c.** O termo constante da eq. (2) é o da eq. (1) convertido por `−2g/R`
(cm → m, m/s² → µGal): `−30,48` contra `−30,4` publicado, dentro da precisão declarada. -/
theorem ekmanGravityC0_from_geoid :
    |(-(2 * gravidadeMedia * (ekmanGeoidC0 / 100) / raioMedio) * 1e8) - ekmanGravityC0|
      ≤ 0.4 := by
  unfold gravidadeMedia ekmanGeoidC0 raioMedio ekmanGravityC0
  rw [abs_le]; constructor <;> norm_num

/-! ## Os níveis por sistema, e a estrutura da conversão (T1, T3) -/

/-- Os três sistemas de maré permanente. -/
inductive SistemaMare
  | mean | zero | tideFree
  deriving DecidableEq

open SistemaMare

/-- Nível do geoide por sistema, em cm, dado `a = W/g` (eq. 1): Ekman eqs. (15)–(17). -/
noncomputable def nivelGeoide (a : ℝ) : SistemaMare → ℝ
  | mean => (1 + loveK) * a
  | zero => loveK * a
  | tideFree => 0

/-- Nível da gravidade por sistema, em µGal, dado `b = −∂W/∂r` (eq. 2): eqs. (9)–(11). -/
noncomputable def nivelGravidade (b : ℝ) : SistemaMare → ℝ
  | mean => deltaGrav * b
  | zero => (deltaGrav - 1) * b
  | tideFree => 0

/-- Nível da DIFERENÇA de altura nivelada entre duas estações, em cm, dado
`s = sin²φ_N − sin²φ_S`: eqs. (12)–(14). -/
noncomputable def nivelDifAltura (s : ℝ) : SistemaMare → ℝ
  | mean => ekmanGeoidC2 * gammaEkman * s
  | zero => ekmanGeoidC2 * (gammaEkman - 1) * s
  | tideFree => 0

/-- Nível da deformação da CROSTA entre as duas estações, em cm: `h·(a_N − a_S)`, presente
nos sistemas `mean` e `zero` (que mantêm a deformação) e nulo no `tide-free` (que a
remove). É o termo que o comentário de `_levels_height_diff` omitia. -/
noncomputable def nivelCrosta (s : ℝ) : SistemaMare → ℝ
  | mean => -ekmanGeoidC2 * loveH * s
  | zero => -ekmanGeoidC2 * loveH * s
  | tideFree => 0

/-- Converter um valor do sistema `de` para o sistema `para` é somar a diferença de
níveis. É o que `tide_convert` faz em todos os ramos. -/
noncomputable def converte (nivel : SistemaMare → ℝ) (de para : SistemaMare) (x : ℝ) : ℝ :=
  x + (nivel para - nivel de)

/-- **T1.** Para QUALQUER função de níveis, «somar a diferença» é transitivo e invertível:
`A→A` é identidade, `A→B→C = A→C`, `A→B→A = id`. ⚠️ Não protege o registo de um nível
editado — vale para todo `nivel`; protege só a forma da conversão. -/
theorem converte_self (nivel : SistemaMare → ℝ) (s : SistemaMare) (x : ℝ) :
    converte nivel s s x = x := by
  unfold converte; ring

theorem converte_trans (nivel : SistemaMare → ℝ) (a b c : SistemaMare) (x : ℝ) :
    converte nivel b c (converte nivel a b x) = converte nivel a c x := by
  unfold converte; ring

theorem converte_inv (nivel : SistemaMare → ℝ) (a b : SistemaMare) (x : ℝ) :
    converte nivel b a (converte nivel a b x) = x := by
  unfold converte; ring

/-- **T3.** Em cada sistema, o nível da diferença de altura nivelada é o negativo da
diferença de nível do geoide entre as estações, mais o nível da crosta — nos TRÊS sistemas,
sem exclusão: `H = h − N` com `h` deformado pela crosta. A hipótese `a_N − a_S = −29,6·s` é
a eq. (1) aplicada às duas estações (o termo `9,9` cancela). É `ring`, e é o que o teste
`test_eq12_deriva_da_eq15_por_H_igual_h_menos_N` já afirmava em Python. -/
theorem nivelDifAltura_eq_neg_geoide_add_crosta (aN aS s : ℝ)
    (h : aN - aS = -ekmanGeoidC2 * s) (sys : SistemaMare) :
    nivelDifAltura s sys = -(nivelGeoide aN sys - nivelGeoide aS sys) + nivelCrosta s sys := by
  cases sys with
  | mean =>
      simp only [nivelDifAltura, nivelGeoide, nivelCrosta, gammaEkman]
      have h2 : (1 + loveK) * aN - (1 + loveK) * aS = (1 + loveK) * (aN - aS) := by ring
      rw [h2, h]; ring
  | zero =>
      simp only [nivelDifAltura, nivelGeoide, nivelCrosta, gammaEkman]
      have h2 : loveK * aN - loveK * aS = loveK * (aN - aS) := by ring
      rw [h2, h]; ring
  | tideFree =>
      simp only [nivelDifAltura, nivelGeoide, nivelCrosta]; ring

end Mapgravy
