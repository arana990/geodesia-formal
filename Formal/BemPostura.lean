/-
Copyright (c) 2026 Daniel Arana. All rights reserved.
Released under GPL-3.0 license as described in the file LICENSE.
Authors: Daniel Arana
-/
import Mathlib

set_option linter.style.header false

/-!
# A condição de Hörmander implica a de Lions–Sznitman

Formalização da relação entre as duas condições de bem-postura que o PVCG deste projeto
invoca, e que até aqui coexistiam sem que a implicação estivesse escrita.

## As duas condições, e por que ninguém tinha dito qual implica qual

O `CLAUDE.md` §1 declara que a reflexão oblíqua é bem-posta onde o ângulo entre a
gravidade e a normal à superfície é `< 90°` — a condição de **Lions–Sznitman** (1984),
que vem do lado estocástico.

`@hormander1976` chega ao mesmo problema pelo lado das EDP e pede **mais** para a
unicidade (Teorema 1.5.1): que a **soma** de dois ângulos — o que `h` faz com a direção
radial, e o que `h` faz com a normal exterior — seja `< π/2 − δ`, com `δ > 0` em todo
ponto.

⚠️⚠️ **As duas condições convivem no projeto há meses, e a relação entre elas era só
observada:** mediu-se que no domínio do GSVS17 a soma máxima é `20,2°`, logo as duas valem.
Medir que ambas valem num domínio **não é** dizer que uma implica a outra — e a diferença
importa, porque quem verificasse só Lions–Sznitman poderia julgar ter unicidade.

## O que se prova

Que a hipótese de Hörmander implica a de Lions–Sznitman, **em geral** e não no nosso
domínio. A prova tem duas metades de dificuldade muito diferente, e vale a pena separá-las
porque só a segunda é onde erros vivem:

1. **a metade aritmética** — de `α + θ ≤ π/2 − δ` com `α, θ ≥ 0` e `δ > 0` sai `θ < π/2`.
   ⚠️ É quase trivial, e **depende inteiramente de os ângulos serem não-negativos**, que é
   uma propriedade da definição de ângulo e não uma hipótese que se possa esquecer;
2. **a ponte geométrica** — de `θ < π/2` para `⟪h, n⟫ > 0`, que é a forma em que a
   condição de Lions–Sznitman é de facto usada no código. É aqui que os erros de sinal
   moram, e é aqui que o Lean se paga.

⚠️ **O que NÃO se prova:** que Hörmander e Lions–Sznitman sejam as condições certas para
este problema, nem que o nosso domínio as satisfaça. A primeira é literatura; a segunda é
medida (`experiments/hipotese_de_hormander.py`, soma máxima `20,2°` na linha GSVS17).
-/

namespace Mapgravy

open InnerProductGeometry

variable {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]

/-- **A metade aritmética.** Se a soma dos dois ângulos de Hörmander respeita `π/2 − δ`
com `δ > 0`, então o ângulo com a normal — sozinho — é estritamente menor que `π/2`.

⚠️ **A hipótese que carrega tudo é `0 ≤ α`**, e ela não é uma suposição: é
`InnerProductGeometry.angle_nonneg`, propriedade da definição. Escrevê-la explicitamente é
o que impede a leitura errada de que o resultado precisaria de algo sobre a deflexão da
vertical. -/
theorem hormander_limita_a_obliquidade (α θ δ : ℝ)
    (hα : 0 ≤ α) (hδ : 0 < δ) (h : α + θ ≤ Real.pi / 2 - δ) :
    θ < Real.pi / 2 := by
  linarith

/-- **A ponte geométrica: ângulo `< π/2` é o mesmo que produto interno positivo.**

É a forma em que a condição de Lions–Sznitman entra no código — o motor testa o SINAL da
componente normal, não um ângulo. ⚠️ A equivalência precisa de os dois vetores serem
não-nulos, e é aí que ela pode falhar em silêncio: com `n = 0` o `angle` do mathlib devolve
`π/2` por convenção, e o produto interno é `0`.

Precedente do que ela protege: o `CLAUDE.md` §1 avisa que *«o sinal `−δg` só vale para `s`
apontando para FORA»*, e que a mesma condição escrita ao longo da gravidade troca de sinal.
Uma condição de bem-postura escrita com o vetor errado passa despercebida. -/
theorem angulo_agudo_iff_produto_interno_positivo (x y : V) (hx : x ≠ 0) (hy : y ≠ 0) :
    angle x y < Real.pi / 2 ↔ 0 < inner ℝ x y := by
  have hnx : 0 < ‖x‖ := norm_pos_iff.mpr hx
  have hny : 0 < ‖y‖ := norm_pos_iff.mpr hy
  have hcos : Real.cos (angle x y) = inner ℝ x y / (‖x‖ * ‖y‖) := cos_angle x y
  constructor
  · intro hlt
    have h0 : 0 < Real.cos (angle x y) :=
      Real.cos_pos_of_mem_Ioo ⟨by linarith [angle_nonneg x y, Real.pi_pos], hlt⟩
    rw [hcos] at h0
    have hden : 0 < ‖x‖ * ‖y‖ := by positivity
    exact (div_pos_iff_of_pos_right hden).mp h0
  · intro hpos
    by_contra hge
    push_neg at hge
    have h0 : Real.cos (angle x y) ≤ 0 :=
      Real.cos_nonpos_of_pi_div_two_le_of_le hge (by linarith [angle_le_pi x y, Real.pi_pos])
    rw [hcos] at h0
    have : 0 < inner ℝ x y / (‖x‖ * ‖y‖) := by positivity
    linarith

/-- **O teorema: a condição de Hörmander implica a de Lions–Sznitman.**

Dados a vertical `h` e a normal exterior `n`, ambos não-nulos, se a soma do ângulo de `h`
com a radial `r` e do ângulo de `h` com `n` respeita `π/2 − δ` com `δ > 0`, então
`⟪h, n⟫ > 0` — que é a condição de bem-postura que o motor de reflexão exige.

⚠️ **A implicação é ESTRITA e vale só nesta direção.** Lions–Sznitman **não** implica
Hörmander: a condição dele limita um ângulo só, e nada diz sobre a deflexão da vertical.
⇒ verificar a condição do motor não dá unicidade; verificar a de Hörmander dá as duas. -/
theorem hormander_implica_lions_sznitman (h n r : V) (hh : h ≠ 0) (hn : n ≠ 0)
    (δ : ℝ) (hδ : 0 < δ)
    (hsoma : angle h r + angle h n ≤ Real.pi / 2 - δ) :
    0 < inner ℝ h n := by
  have hθ : angle h n < Real.pi / 2 :=
    hormander_limita_a_obliquidade _ _ δ (angle_nonneg h r) hδ hsoma
  exact (angulo_agudo_iff_produto_interno_positivo h n hh hn).mp hθ

/-- ⚠️ **A recíproca é FALSA, e este teorema di-lo construtivamente.**

Existe uma configuração em que a condição de Lions–Sznitman vale — `⟪h, n⟫ > 0` — e a de
Hörmander falha para todo `δ > 0`: basta a vertical fazer um ângulo grande com a radial.

⇒ é o que impede a leitura de que as duas condições sejam equivalentes, e a que o projeto
esteve perto de fazer ao medir que ambas valem no seu domínio. **Valerem juntas num
domínio é medida; implicarem-se é teorema, e só numa direção.**

Toma-se `h = n` (ângulo nulo, condição do motor satisfeita com folga máxima) e `r` oposto
a `h`, de que `angle h r = π`. -/
theorem lions_sznitman_nao_implica_hormander (h : V) (hh : h ≠ 0) :
    0 < inner ℝ h h ∧ ¬ (angle h (-h) + angle h h ≤ Real.pi / 2) := by
  refine ⟨real_inner_self_pos.mpr hh, ?_⟩
  rw [angle_self_neg_of_nonzero hh, angle_self hh]
  have := Real.pi_pos
  linarith

end Mapgravy
