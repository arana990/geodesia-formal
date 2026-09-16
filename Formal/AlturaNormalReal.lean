/-
Copyright (c) 2026 Daniel Arana. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Daniel Arana
-/
import Mathlib
import Formal.Contracao

/-!
# A altura normal sobre o modelo que o código USA: a cúbica, a raiz única, e a contração

D2(a) do parecer de 2026-09-16. `Alturas.lean` e `Contracao.lean` formalizam o modelo
LINEAR `γ̄ = γ₀ − a·H`; o parecer mostrou que `_gamma_barra_ms2` não usa esse modelo: chama
`normal_gravity(φ, H/2) = γ₀(φ) − c₁(φ)·(H/2) + c₂(φ)·(H/2)²`, com `c₁` o coeficiente exato
de Bruns e `c₂` o termo de segunda ordem. Aqui o modelo é esse:

  `γ̄(H) = γ₀ − (c₁/2)·H + (c₂/4)·H²`,

e a equação do ponto fixo `H·γ̄(H) = C` é uma CÚBICA. O que se prova, sem cálculo
diferencial (só álgebra sobre diferenças):

* **`psi_strictMono`** — `ψ(H) = H·γ̄(H)` é estritamente crescente em `[0, H_max]` sempre que
  `c₁·H_max < γ₀` e `c₂ ≥ 0`. Logo **há no máximo uma raiz** nessa faixa
  (`normalHeightReal_unique`), e **há uma** para `0 ≤ C ≤ ψ(H_max)`
  (`normalHeightReal_exists`, valor intermédio). É o «uma raiz real» que o parecer mediu
  numericamente (`C = 10⁴`: `1 019,947 m` e um par complexo), agora demonstrado.
* **`gammaBarReal_lipschitz`** — o termo quadrático só AJUDA: para `H` abaixo de `c₁/c₂`
  (`≈ 4 300 km`), a inclinação de `γ̄` fica entre `−c₁/2` e `0`, logo `γ̄` é Lipschitz com a
  MESMA constante `a = c₁/2` do modelo linear. ⇒ a cota de `Contracao.lean`,
  `q = C·a/m²`, vale para o modelo do código, e a previsão que o gate
  `test_contracao_preve_o_residuo.py` confronta com a medida deixa de ser sobre um modelo
  simplificado.

## O que se prende sobre o coeficiente, e o que NÃO se prova

`brunsCoef γ₀ M N ω = γ₀·(1/M + 1/N) + 2ω²` é a identidade de Bruns em `h = 0` — a forma
que `_bruns_altura_coef` implementa desde 2026-08-17, quando substituiu o literal
`0,3087691 − 0,0004398·sin²φ` (a forma `O(f)` de Heiskanen–Moritz, sem fonte), que ficava
`1,07·10⁻⁵ mGal/m` baixo. ⚠️ **Derivar Bruns do potencial normal está fora do alcance
deste diretório** (não há Somigliana–Pizzetti na mathlib); aqui a identidade é DEFINIÇÃO.
O que se prende é o que a definição permite: que, com os raios de curvatura do GRS80 a
`45°`, o literal antigo **não é** o valor de Bruns — difere por mais de `10⁻⁵ mGal/m`
(`literal_antigo_nao_e_bruns`). É um pino, não uma dedução: teria recusado o literal se
existisse em 2026-08-16, e é a primeira vez que um teorema deste diretório cobre um
defeito que o projeto de facto cometeu — na forma de pino, dita assim.
-/

namespace Mapgravy

/-! ## O modelo do código -/

/-- `γ̄(H) = normal_gravity(φ, H/2) = γ₀ − (c₁/2)·H + (c₂/4)·H²`. -/
noncomputable def gammaBarReal (gamma0 c1 c2 H : ℝ) : ℝ :=
  gamma0 - c1 / 2 * H + c2 / 4 * H ^ 2

/-- `ψ(H) = H·γ̄(H)`: a equação do ponto fixo é `ψ(H) = C`. -/
noncomputable def psi (gamma0 c1 c2 H : ℝ) : ℝ := H * gammaBarReal gamma0 c1 c2 H

/-- **A diferença de `ψ` fatoriza**, e é isto que dispensa o cálculo: para `H₁ ≤ H₂`,
`ψ(H₂) − ψ(H₁) = (H₂ − H₁)·[γ₀ − (c₁/2)(H₁ + H₂) + (c₂/4)(H₁² + H₁H₂ + H₂²)]`. -/
theorem psi_sub (gamma0 c1 c2 H₁ H₂ : ℝ) :
    psi gamma0 c1 c2 H₂ - psi gamma0 c1 c2 H₁
      = (H₂ - H₁) * (gamma0 - c1 / 2 * (H₁ + H₂) + c2 / 4 * (H₁ ^ 2 + H₁ * H₂ + H₂ ^ 2)) := by
  unfold psi gammaBarReal; ring

/-- **`ψ` é estritamente crescente em `[0, H_max]`** quando `c₁·H_max < γ₀` e `c₂ ≥ 0`. -/
theorem psi_strictMono (gamma0 c1 c2 Hmax H₁ H₂ : ℝ) (hc1 : 0 ≤ c1) (hc2 : 0 ≤ c2)
    (hmax : c1 * Hmax < gamma0) (h₁ : 0 ≤ H₁) (h₂ : H₂ ≤ Hmax) (hlt : H₁ < H₂) :
    psi gamma0 c1 c2 H₁ < psi gamma0 c1 c2 H₂ := by
  have hd : 0 < H₂ - H₁ := by linarith
  have hbr : 0 < gamma0 - c1 / 2 * (H₁ + H₂) + c2 / 4 * (H₁ ^ 2 + H₁ * H₂ + H₂ ^ 2) := by
    have hsum : c1 / 2 * (H₁ + H₂) ≤ c1 * Hmax := by nlinarith
    have hquad : 0 ≤ c2 / 4 * (H₁ ^ 2 + H₁ * H₂ + H₂ ^ 2) := by
      apply mul_nonneg (by linarith); nlinarith
    linarith
  have := psi_sub gamma0 c1 c2 H₁ H₂
  nlinarith [mul_pos hd hbr]

/-- **Unicidade.** Duas alturas normais do mesmo `C` em `[0, H_max]` coincidem. -/
theorem normalHeightReal_unique (gamma0 c1 c2 Hmax C H₁ H₂ : ℝ) (hc1 : 0 ≤ c1) (hc2 : 0 ≤ c2)
    (hmax : c1 * Hmax < gamma0)
    (b₁ : 0 ≤ H₁) (b₁' : H₁ ≤ Hmax) (b₂ : 0 ≤ H₂) (b₂' : H₂ ≤ Hmax)
    (e₁ : psi gamma0 c1 c2 H₁ = C) (e₂ : psi gamma0 c1 c2 H₂ = C) : H₁ = H₂ := by
  rcases lt_trichotomy H₁ H₂ with h | h | h
  · have := psi_strictMono gamma0 c1 c2 Hmax H₁ H₂ hc1 hc2 hmax b₁ b₂' h; linarith
  · exact h
  · have := psi_strictMono gamma0 c1 c2 Hmax H₂ H₁ hc1 hc2 hmax b₂ b₁' h; linarith

/-- **Existência.** Para `0 ≤ C ≤ ψ(H_max)`, há `H ∈ [0, H_max]` com `ψ(H) = C`
(valor intermédio; `ψ` é polinómio). -/
theorem normalHeightReal_exists (gamma0 c1 c2 Hmax C : ℝ) (h0 : 0 ≤ Hmax)
    (hC : 0 ≤ C) (hC' : C ≤ psi gamma0 c1 c2 Hmax) :
    ∃ H ∈ Set.Icc 0 Hmax, psi gamma0 c1 c2 H = C := by
  have hcont : ContinuousOn (psi gamma0 c1 c2) (Set.Icc 0 Hmax) := by
    unfold psi gammaBarReal; fun_prop
  have h0' : psi gamma0 c1 c2 0 = 0 := by unfold psi; ring
  have := intermediate_value_Icc h0 hcont
  rw [h0'] at this
  exact this ⟨hC, hC'⟩

/-! ## O termo quadrático só ajuda: a constante de contração é a do modelo linear -/

/-- Para `H₁, H₂ ∈ [0, H_max]` com `c₂·H_max ≤ c₁` (isto é, `H_max ≤ c₁/c₂ ≈ 4 000 km`), a
inclinação de `γ̄` fica entre `−c₁/2` e `0`: `|γ̄(H₁) − γ̄(H₂)| ≤ (c₁/2)·|H₁ − H₂|`. -/
theorem gammaBarReal_lipschitz (gamma0 c1 c2 Hmax H₁ H₂ : ℝ) (hc2 : 0 ≤ c2)
    (hlim : c2 * Hmax ≤ c1) (b₁ : 0 ≤ H₁) (b₁' : H₁ ≤ Hmax) (b₂ : 0 ≤ H₂) (b₂' : H₂ ≤ Hmax) :
    |gammaBarReal gamma0 c1 c2 H₁ - gammaBarReal gamma0 c1 c2 H₂| ≤ c1 / 2 * |H₁ - H₂| := by
  have key : gammaBarReal gamma0 c1 c2 H₁ - gammaBarReal gamma0 c1 c2 H₂
      = (H₁ - H₂) * (-(c1 / 2) + c2 / 4 * (H₁ + H₂)) := by
    unfold gammaBarReal; ring
  rw [key, abs_mul, mul_comm]
  apply mul_le_mul_of_nonneg_right _ (abs_nonneg _)
  rw [abs_le]
  constructor
  · have : 0 ≤ c2 / 4 * (H₁ + H₂) := by positivity
    linarith
  · have : c2 / 4 * (H₁ + H₂) ≤ c1 / 2 := by nlinarith
    have : 0 ≤ c2 * Hmax := mul_nonneg hc2 (le_trans b₁ b₁')
    linarith

/-- **A contração do modelo do código tem a constante do modelo linear.** Se `γ̄_real ≥ m > 0`
em `H₁, H₂ ∈ [0, H_max]` e `c₂·H_max ≤ c₁`, então
`|C/γ̄(H₁) − C/γ̄(H₂)| ≤ (C·(c₁/2)/m²)·|H₁ − H₂|` — o `q` de `Contracao.lean` com `a = c₁/2`. -/
theorem iteracaoReal_lipschitz (gamma0 c1 c2 Hmax C H₁ H₂ m : ℝ) (hC : 0 ≤ C) (hc1 : 0 ≤ c1)
    (hc2 : 0 ≤ c2) (hm : 0 < m) (hlim : c2 * Hmax ≤ c1)
    (b₁ : 0 ≤ H₁) (b₁' : H₁ ≤ Hmax) (b₂ : 0 ≤ H₂) (b₂' : H₂ ≤ Hmax)
    (g₁ : m ≤ gammaBarReal gamma0 c1 c2 H₁) (g₂ : m ≤ gammaBarReal gamma0 c1 c2 H₂) :
    |C / gammaBarReal gamma0 c1 c2 H₁ - C / gammaBarReal gamma0 c1 c2 H₂|
      ≤ C * (c1 / 2) / m ^ 2 * |H₁ - H₂| := by
  set G₁ := gammaBarReal gamma0 c1 c2 H₁ with hG₁
  set G₂ := gammaBarReal gamma0 c1 c2 H₂ with hG₂
  have d₁ : 0 < G₁ := lt_of_lt_of_le hm g₁
  have d₂ : 0 < G₂ := lt_of_lt_of_le hm g₂
  have key : C / G₁ - C / G₂ = C * (G₂ - G₁) / (G₁ * G₂) := by field_simp
  have hlip : |G₂ - G₁| ≤ c1 / 2 * |H₁ - H₂| := by
    rw [abs_sub_comm]; exact gammaBarReal_lipschitz gamma0 c1 c2 Hmax H₁ H₂ hc2 hlim b₁ b₁' b₂ b₂'
  rw [key, abs_div, abs_mul, abs_of_nonneg hC, abs_of_pos (mul_pos d₁ d₂)]
  have hden : m ^ 2 ≤ G₁ * G₂ := by
    calc m ^ 2 = m * m := by ring
      _ ≤ G₁ * G₂ := mul_le_mul g₁ g₂ hm.le d₁.le
  rw [div_le_iff₀ (mul_pos d₁ d₂)]
  calc C * |G₂ - G₁| ≤ C * (c1 / 2 * |H₁ - H₂|) := by gcongr
    _ = C * (c1 / 2) / m ^ 2 * |H₁ - H₂| * m ^ 2 := by field_simp
    _ ≤ C * (c1 / 2) / m ^ 2 * |H₁ - H₂| * (G₁ * G₂) := by
        apply mul_le_mul_of_nonneg_left hden; positivity

/-! ## O coeficiente de Bruns: definição, e o pino contra o literal antigo -/

/-- Identidade de Bruns em `h = 0`: `−∂γ/∂h = γ₀·(1/M + 1/N) + 2ω²`, com `M` e `N` os raios
de curvatura meridiano e do primeiro vertical. É o que `_bruns_altura_coef` implementa.
⚠️ DEFINIÇÃO, não teorema: derivá-la do potencial normal está fora deste diretório. -/
noncomputable def brunsCoef (gamma0 M N omega : ℝ) : ℝ := gamma0 * (1 / M + 1 / N) + 2 * omega ^ 2

/-- **O pino.** Com os valores do GRS80 a `φ = 45°` — `γ₀ = 9,806199 m/s²`,
`M = 6 367 382 m`, `N = 6 388 838 m`, `ω = 7,292115·10⁻⁵ s⁻¹` — o coeficiente de Bruns é
`3,08560·10⁻⁶ s⁻²` (`0,308560 mGal/m`), e o literal que o código teve até 2026-08-17,
`0,3087691 − 0,0004398·sin²45° = 0,3085492 mGal/m`, fica a mais de `10⁻⁵ mGal/m` dele:
**não é o valor de Bruns.** Teria recusado o literal. -/
theorem literal_antigo_nao_e_bruns :
    1e-5 < |brunsCoef 9.806199 6367382 6388838 7.292115e-5 * 1e5 - 0.3085492| := by
  unfold brunsCoef
  rw [lt_abs]
  left
  norm_num

end Mapgravy
