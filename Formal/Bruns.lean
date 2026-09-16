/-
Copyright (c) 2026 Daniel Arana. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Daniel Arana
-/
import Mathlib
import Formal.Helmert

/-!
# Anomalia e distúrbio de gravidade: a diferença é a variação de `γ` entre dois pontos

Terceira parte da auditoria formal de `geodesy/conventions.py` (Paper 4, T4 do inventário).

↩️ **Revisto em 2026-09-16 depois de um parecer adversarial**
(`docs/pareceres/paper4_revisao_adversarial_2026-09-16.md`). A primeira versão reclamava que
o registo «usa `δg ≈ Δg_FA` a primeira ordem sem escrever o que despreza» — **falso**:
`bouguer_from_disturbance` escreve a diferença, `(2/R)ζH = 1,3 cm` no Colorado, e aponta
para o teste que a gateia. E o teorema «linear» era tautológico: a hipótese `γ_P = γ_Q + d·ζ`
é a conclusão `Δg − δg = d·ζ` com outro nome, porque `Δg − δg ≡ γ_P − γ_Q` por definição.
O que sobra, dito com esse alcance:

## As definições, de Hofmann-Wellenhof & Moritz (2006), transcritas pelo autor

  (2-228)  `Δg = g_P − γ_Q`   — a ANOMALIA: gravidade normal num ponto `Q` distinto de `P`
  (2-232)  `δg = g_P − γ_P`   — o DISTÚRBIO: gravidade normal no próprio ponto `P`

⚠️ **Onde estão `P` e `Q` não é fixado por estas fórmulas.** No §2.12 de HM (a anomalia
clássica, a que a (2-228) pertence) `P` está no geoide e `Q` no elipsoide; na teoria de
Molodensky (cap. 8, o parágrafo antes da 8-113) `P` está na superfície e `Q` no teluroide,
e a distância entre eles é a anomalia de altura `ζ`. Os teoremas abaixo valem nas duas
leituras, porque só usam a diferença `γ_P − γ_Q`; a leitura de Molodensky é a do Paper 3.

## O que se prova

Só das definições, `Δg − δg = γ_P − γ_Q`. Isso é tudo o que a álgebra dá. O passo seguinte —
`γ_P − γ_Q ≈ (∂γ/∂h)·ζ`, com `∂γ/∂h ≈ −2γ/R` na aproximação esférica — é física, e fica
como DEFINIÇÃO do modelo linear e não como teorema: escrevê-lo como teorema seria
reescrever a definição. O número do Paper 3 (`+4,62 mGal` para `ζ = −15 m`) é `V:medido`
no manuscrito, e não pertence aqui — a primeira versão tinha-o como teorema, o portão do
`0 = 0` recusou-o, e a segunda versão contornou o portão com variáveis que cancelavam.
Apagado.

O que se prende, além da definição: que o gradiente esférico `2γ/R` e o gradiente de ar
livre clássico `FA = 0,3086 mGal/m` de `Helmert.lean` — o MESMO gradiente, em dois
módulos — sejam coerentes. Um só sinal: ambos em MÓDULO, como `Helmert.lean` já fazia.
-/

namespace Mapgravy

/-- (2-228): a anomalia de gravidade, com `γ` num ponto `Q` distinto de `P`. -/
def gravityAnomaly (gP gammaQ : ℝ) : ℝ := gP - gammaQ
/-- (2-232): o distúrbio de gravidade, com `γ` no próprio ponto `P`. -/
def gravityDisturbance (gP gammaP : ℝ) : ℝ := gP - gammaP

/-- **T4.** Só das definições: anomalia menos distúrbio é a variação de `γ` entre `Q` e
`P`. Nada mais entra, e nada mais se afirma. -/
theorem anomaly_sub_disturbance (gP gammaP gammaQ : ℝ) :
    gravityAnomaly gP gammaQ - gravityDisturbance gP gammaP = gammaP - gammaQ := by
  unfold gravityAnomaly gravityDisturbance; ring

/-- **T4′.** A anomalia de Bouguer de `Helmert.lean` calculada com o DISTÚRBIO em vez da
anomalia difere da correta por `γ_P − γ_Q` — é o que `bouguer_from_disturbance` faz, e é o
erro que o docstring dela quantifica em `(2/R)ζH`. Trivial, e nomeia a função. -/
theorem bouguerAnomaly_from_disturbance_error (gP gammaP gammaQ B H : ℝ) :
    bouguerAnomaly (gravityDisturbance gP gammaP) B H
      = bouguerAnomaly (gravityAnomaly gP gammaQ) B H - (gammaP - gammaQ) := by
  unfold bouguerAnomaly gravityDisturbance gravityAnomaly; ring

/-- Módulo do gradiente vertical da gravidade normal na aproximação esférica, `2γ/R`, em
mGal/m com `γ` em mGal e `R` em m. Mesmo sinal (positivo, em módulo) que o `FA` de
`Helmert.lean`. -/
noncomputable def sphericalGradientMagnitude (gamma R : ℝ) : ℝ := 2 * gamma / R

/-- **T4″.** O gradiente esférico com `γ = 980 665 mGal` e `R = 6 371 000 m` reproduz o
`FA = 0,3086` clássico a `0,001 mGal/m` (`0,3079` contra `0,3086`, `0,25 %`): as duas
constantes que o projeto usa para a mesma quantidade são coerentes. É aritmética; o que
prende é que sejam UMA quantidade em dois módulos. -/
theorem sphericalGradient_matches_classical_FA :
    |sphericalGradientMagnitude 980665 6371000 - 0.3086| < 0.001 := by
  unfold sphericalGradientMagnitude
  rw [abs_lt]; constructor <;> norm_num

end Mapgravy
