/-
Copyright (c) 2026 Daniel Arana. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Daniel Arana
-/
import Mathlib
import Formal.Helmert

/-!
# Sistemas de altura: o ponto fixo da altura normal, e a ponte `N`/`ζ`

Segunda parte da auditoria formal de `geodesy/conventions.py` (Paper 4; inventário em
`docs/inventario_convencoes_formal.md`, teoremas T5, T6, T8, T9).

↩️ **Revisto em 2026-09-16 depois de um parecer adversarial**
(`docs/pareceres/paper4_revisao_adversarial_2026-09-16.md`). O que este ficheiro afirma,
com o alcance que o parecer mediu:

## O ponto fixo (T5) — sobre um modelo MAIS SIMPLES que o do código

`geopotential_to_normal_height` calcula `H* = C/γ̄(H*)` por três iterações de ponto fixo.
Aqui a média é o modelo LINEAR `γ̄(H) = γ₀ − (FA/2)·H`, e a equação `H = C/γ̄(H)` é uma
quadrática com duas raízes; a física é a que está abaixo de `γ₀/FA` (`≈ 3 178 km`), e
nesse intervalo é única.

⚠️⚠️ **Isto NÃO é o que `_gamma_barra_ms2` faz.** O registo chama `normal_gravity(φ, H/2)`,
que tem coeficiente linear DEPENDENTE DA LATITUDE e um termo QUADRÁTICO: a equação real é
uma cúbica com UMA raiz real (medido pelo parecer: `C = 10⁴` dá `1 019,947 m` e um par
complexo). A «segunda raiz» e a cota que a exclui são artefacto do modelo linear — e a
cota `FA·H < γ₀` é vácua por 2,5 ordens de grandeza para qualquer altura terrestre. Este
teorema **não cobre** o defeito que a função de facto teve (coeficiente `O(f)` baixo,
2026-08-17). Fica como registo do modelo, não como auditoria do código. O resíduo das três
iterações do código contra a raiz do PRÓPRIO modelo do código foi medido:
`< 10⁻⁶ mm` até `4 082 m` (`docs/painel/formal_convencoes.md`).

## A ponte entre as duas convenções de `γ̄` — é uma substituição, não uma hipótese

`Helmert.lean` escreve a média como `γ_Q + (FA/2)H` com `γ_Q` no teluroide; o registo
avalia `γ(H/2)` a partir do elipsoide. `meanNormalGravity_from_ellipsoid` mostra que
coincidem quando se passa `γ_Q := γ₀ − FA·H` — e isso é o ARGUMENTO que se passa, não uma
hipótese que o teorema imponha: nada obriga um chamador a passá-lo. É a mesma
invisibilidade que o docstring de `bouguerAnomaly` denuncia, e este teorema não a resolve;
regista-a.

## `N` e `ζ` (T8, T9)

`h = H + N` e `h = H* + ζ` são a mesma altura elipsoidal; logo `N − ζ = H* − H`, que é a
identidade de `separation_is_identity` vista pelo lado das alturas — e é a mistura de
`ζ` com `N` que o §0.2b do painel documenta como o maior termo do orçamento do Paper 2.
-/

namespace Mapgravy

/-! ## A média da gravidade normal, nas duas convenções -/

/-- Gravidade normal média entre o elipsoide e a altura `H`, no modelo linear:
`γ̄ = γ₀ − (FA/2)H`. É o `γ(H/2)` de `_gamma_barra_ms2`. -/
noncomputable def meanNormalGravityFromEllipsoid (gamma0 FA H : ℝ) : ℝ :=
  gamma0 - FA / 2 * H

/-- A média «do teluroide para baixo» de `Helmert.lean` e a média «do elipsoide para
cima» do registo coincidem **quando** `γ_Q = γ₀ − FA·H`. A hipótese é a ponte. -/
theorem meanNormalGravity_from_ellipsoid (gamma0 FA H : ℝ) :
    meanNormalGravity (gamma0 - FA * H) FA H = meanNormalGravityFromEllipsoid gamma0 FA H := by
  unfold meanNormalGravity meanNormalGravityFromEllipsoid; ring

/-! ## T5 — o ponto fixo da altura normal é uma quadrática com UMA raiz física -/

/-- `H` é altura normal de `C` se satisfaz `H · γ̄(H) = C`, isto é, `H = C/γ̄(H)`. -/
def IsNormalHeight (gamma0 FA C H : ℝ) : Prop :=
  H * meanNormalGravityFromEllipsoid gamma0 FA H = C

/-- **T5a (unicidade).** Duas alturas normais do mesmo `C`, ambas abaixo de `γ₀/FA`,
são a mesma. A outra raiz da quadrática está ACIMA de `γ₀/FA` e não é altura de nada. -/
theorem normalHeight_unique (gamma0 FA C H₁ H₂ : ℝ)
    (h₁ : IsNormalHeight gamma0 FA C H₁) (h₂ : IsNormalHeight gamma0 FA C H₂)
    (b₁ : FA * H₁ < gamma0) (b₂ : FA * H₂ < gamma0) : H₁ = H₂ := by
  unfold IsNormalHeight meanNormalGravityFromEllipsoid at h₁ h₂
  -- (H₁ − H₂) · (γ₀ − (FA/2)(H₁ + H₂)) = 0, e o segundo fator é positivo
  have hfat : (H₁ - H₂) * (gamma0 - FA / 2 * (H₁ + H₂)) = 0 := by linear_combination h₁ - h₂
  have hpos : 0 < gamma0 - FA / 2 * (H₁ + H₂) := by linarith
  rcases mul_eq_zero.mp hfat with h | h
  · linarith
  · linarith

/-- **T5b (existência, forma fechada).** Com `γ₀² > 2·FA·C`, a raiz
`H = (γ₀ − √(γ₀² − 2·FA·C)) / FA` é altura normal de `C` e fica abaixo de `γ₀/FA`.
É a raiz para a qual a iteração do registo converge. -/
theorem normalHeight_closed_form (gamma0 FA C : ℝ) (hFA : 0 < FA)
    (hdisc : 2 * FA * C < gamma0 ^ 2) :
    IsNormalHeight gamma0 FA C ((gamma0 - Real.sqrt (gamma0 ^ 2 - 2 * FA * C)) / FA) ∧
    FA * ((gamma0 - Real.sqrt (gamma0 ^ 2 - 2 * FA * C)) / FA) < gamma0 := by
  have hD : 0 ≤ gamma0 ^ 2 - 2 * FA * C := by linarith
  have hs : Real.sqrt (gamma0 ^ 2 - 2 * FA * C) ^ 2 = gamma0 ^ 2 - 2 * FA * C :=
    Real.sq_sqrt hD
  have hsnn : 0 ≤ Real.sqrt (gamma0 ^ 2 - 2 * FA * C) := Real.sqrt_nonneg _
  constructor
  · unfold IsNormalHeight meanNormalGravityFromEllipsoid
    field_simp
    nlinarith [hs]
  · have : FA * ((gamma0 - Real.sqrt (gamma0 ^ 2 - 2 * FA * C)) / FA)
        = gamma0 - Real.sqrt (gamma0 ^ 2 - 2 * FA * C) := by field_simp
    rw [this]
    -- √(γ₀² − 2FA·C) > 0 porque o radicando é > 0 (hdisc), logo γ₀ − √ < γ₀
    have hspos : 0 < Real.sqrt (gamma0 ^ 2 - 2 * FA * C) :=
      Real.sqrt_pos.mpr (by linarith)
    linarith

/-! ## T6 — ida e volta: APAGADO

A primeira versão tinha `normalHeight_roundtrip : IsNormalHeight … H → H·γ̄(H) = C` com prova
`:= h` — a hipótese É a conclusão, um `0 = 0` com variáveis ligadas que o portão de sintaxe
não vê. Apagado no parecer de 2026-09-16. O que «ida e volta» afirma de útil é numérico e
está gateado em Python (`test_C_e_H_estrela_ida_e_volta_recuperam_a_entrada`). -/

/-! ## T8 e T9 — `N` e `ζ` -/

/-- **T8.** A altura elipsoidal é uma só: `h = H + N = H* + ζ`. Logo `N − ζ = H* − H`. É
subtrair duas equações. ⚠️ O que ele aponta é real e não foi este teorema que o achou: a
docstring de `geoid_quasigeoid_separation` dizia `N − ζ = H − H*` e a de
`geopotential_to_helmert_height`, no mesmo ficheiro, `H* − H`. O teorema provava o livro
(HM 8-113); quem leu o registo foi o parecer. Corrigido em 2026-09-16. -/
theorem geoid_minus_zeta_eq_height_diff (h H N Hstar zeta : ℝ)
    (hN : h = H + N) (hz : h = Hstar + zeta) : N - zeta = Hstar - H := by
  linarith

/-- Converter `N → ζ` é subtrair a separação `sep = N − ζ`; `ζ → N` é somá-la
(`convert_geoid_quantity`). -/
def geoidToZeta (sep N : ℝ) : ℝ := N - sep
def zetaToGeoid (sep zeta : ℝ) : ℝ := zeta + sep

/-- **T9.** Ida e volta são a identidade, nos dois sentidos — para QUALQUER `sep`. ⚠️ Nada
aqui liga `sep` a `N − ζ` de T8: trocar o sinal nos dois ramos preserva a involução. O que
se afirma é só a forma «subtrair e depois somar». -/
theorem geoid_zeta_involution (sep x : ℝ) :
    zetaToGeoid sep (geoidToZeta sep x) = x ∧ geoidToZeta sep (zetaToGeoid sep x) = x := by
  unfold zetaToGeoid geoidToZeta; constructor <;> ring

/-! ## D4 — ligar `sep` ao que `convert_geoid_quantity` de facto soma

`convert_geoid_quantity` não subtrai um `sep` qualquer: subtrai
`geoid_quasigeoid_separation = Δg_B·H/γ̄`, e T9 sozinho não o dizia. O teorema abaixo fecha
o triângulo: com as hipóteses de `separation_is_identity` (as duas alturas vêm do MESMO
`C`) e a de T8 (a altura elipsoidal é uma só), subtrair essa separação a `N` **dá `ζ`** —
e somá-la a `ζ` dá `N`. É a conversão do registo, com a separação do `Helmert.lean` e não
com um real livre. -/

/-- **D4.** `N − Δg_B·H/γ̄ = ζ` e `ζ + Δg_B·H/γ̄ = N`, sob as hipóteses de
`separation_is_identity` e de `geoid_minus_zeta_eq_height_diff`. Liga T8, T9 e
`Helmert.lean`; é o que `convert_geoid_quantity` faz. -/
theorem convert_geoid_quantity_is_exact (h H N Hstar zeta C g gamma FA B : ℝ)
    (hgamma : meanNormalGravity gamma FA H ≠ 0)
    (hH : C = meanGravityHelmert g FA B H * H)
    (hHstar : C = meanNormalGravity gamma FA H * Hstar)
    (hN : h = H + N) (hz : h = Hstar + zeta) :
    geoidToZeta (bouguerAnomaly (g - gamma) B H * H / meanNormalGravity gamma FA H) N = zeta ∧
    zetaToGeoid (bouguerAnomaly (g - gamma) B H * H / meanNormalGravity gamma FA H) zeta = N := by
  have hsep := separation_is_identity C g gamma FA B H Hstar hgamma hH hHstar
  have hNz := geoid_minus_zeta_eq_height_diff h H N Hstar zeta hN hz
  unfold geoidToZeta zetaToGeoid
  constructor <;> linarith

end Mapgravy
