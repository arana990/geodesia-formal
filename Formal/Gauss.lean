/-
Copyright (c) 2026 Daniel Arana. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Daniel Arana
-/
import Mathlib

/-!
# `k′₀ = 0` é teorema, e o teorema é Gauss

Formalização da afirmação de `tide/prem_carga.py::numeros_de_love_de_carga_grau_zero`:
o número de Love de carga do grau `0` para o potencial é **exatamente zero**, para
qualquer solução elástica — e não por convenção.

## O que estava em causa

O grau `0` de uma carga superficial é o monopolo: uma camada de massa uniforme sobre a
Terra inteira. A superfície afunda (`h′₀ ≈ −0,132` no PREM), mas o potencial exterior
**não muda** para além do da massa acrescentada: a deformação move massa para dentro, a
massa total não muda, e o monopolo exterior só depende dela.

⚠️ **O docstring da função de Green deste projeto chamava a isto «uma DECLARAÇÃO, não uma
medida»**, e estava errado nos dois pontos: é derivável, e o integrador devolve `1,4e-13`.
Este ficheiro fecha a terceira leitura possível — que fosse coincidência numérica.

## Por que a prova NÃO passa pelo teorema da divergência

O caminho natural seria potencial-teórico: lei de Gauss sobre a bola, monopolo exterior.
⚠️⚠️ **Esse caminho está bloqueado no mathlib de hoje, e foi medido antes de se escolher
outro:** o teorema da divergência existe apenas sobre **caixas** (`Icc a b`), não sobre
bolas ou esferas, e a biblioteca de funções harmónicas tem `437` linhas com apenas
propriedades de fecho — sem valor médio, sem potencial newtoniano, sem harmónicas
esféricas. Formalizar por ali seria construir a infraestrutura primeiro.

✅ **O caminho que funciona é o que a nossa própria derivação usa**, e o conteúdo é o
mesmo: uma identidade de EDO mais o teorema fundamental do cálculo. Em `n = 0` o sistema
elasto-gravitacional reduz-se a quatro equações, das quais só duas tocam o potencial:

    y₅′ = ρy₁ − y₅/x + y₆          (o potencial)
    y₆′ = (ρy₁ − y₆)/x             (o seu fluxo)

⇒ **`x·y₆` é a massa perturbada encerrada, e `y₅ = x·y₆` diz que o potencial na
superfície É essa massa.** É Gauss, escrito em coordenadas radiais.

## O que se prova, e o que fica em prosa

Prova-se a cadeia inteira: `(x·y₆)′ = ρy₁`, depois `(x·y₅ − x·y₆·x)′ = 0`, depois a
constância no aberto, depois que a regularidade na origem a fixa em zero.

⚠️ **A regularidade na origem é HIPÓTESE FÍSICA, não algébrica.** Ela diz que a solução
escolhida é a regular — o que o integrador impõe ao arrancar de `r₀` com a série regular —
e Lean não a deriva. É a única hipótese deste ficheiro que não é de não-divisão-por-zero.
-/

namespace Mapgravy

open Filter Set

/-- **EN:** From the degree-0 flux equation, `x·y₆` has derivative `ρy₁`: it is the enclosed perturbed mass —
the radial form of Gauss's law, obtained from the ODE alone.

**`(x·y₆)′ = ρy₁`.** A equação do fluxo, integrada uma vez.

⇒ `x·y₆(x)` é a **massa perturbada encerrada** dentro do raio `x`: a sua derivada é a
densidade de fonte. É a forma radial da lei de Gauss, e sai só da EDO. -/
theorem flux_accumulates_the_source (y₆ ρy₁ : ℝ → ℝ) (x : ℝ) (hx : x ≠ 0)
    (h : HasDerivAt y₆ ((ρy₁ x - y₆ x) / x) x) :
    HasDerivAt (fun t => t * y₆ t) (ρy₁ x) x := by
  have h2 : HasDerivAt (fun t => t * y₆ t)
      (1 * y₆ x + x * ((ρy₁ x - y₆ x) / x)) x := (hasDerivAt_id x).mul h
  have e : 1 * y₆ x + x * ((ρy₁ x - y₆ x) / x) = ρy₁ x := by field_simp; ring
  rwa [e] at h2

/-- **EN:** Given the degree-0 potential ODE and `M′ = ρy₁`, the combination `x·y₅ − x·M` has zero derivative;
an exact identity with no hypothesis on `y₅` beyond its ODE.

**`(x·y₅ − x·M)′ = 0`**, com `M` a massa encerrada (`M′ = ρy₁`).

⚠️ **É identidade exata, e nenhuma hipótese sobre `y₅` ou `M` entra além das suas EDOs.**
A primeira versão desta prova acrescentou `y₅ x = M x` como hipótese — que é parte da
conclusão. O cancelamento não precisa dela: `(x·y₅)′ = xρy₁ + M` e `(x·M)′ = M + xρy₁`. -/
theorem potential_minus_mass_is_constant (y₅ M ρy₁ : ℝ → ℝ) (x : ℝ) (hx : x ≠ 0)
    (hM : HasDerivAt M (ρy₁ x) x)
    (h5 : HasDerivAt y₅ (ρy₁ x - y₅ x / x + M x / x) x) :
    HasDerivAt (fun t => t * y₅ t - t * M t) (0 : ℝ) x := by
  have a1 : HasDerivAt (fun t => t * y₅ t)
      (1 * y₅ x + x * (ρy₁ x - y₅ x / x + M x / x)) x := (hasDerivAt_id x).mul h5
  have a2 : HasDerivAt (fun t => t * M t) (1 * M x + x * ρy₁ x) x :=
    (hasDerivAt_id x).mul hM
  have h0 : (1 * y₅ x + x * (ρy₁ x - y₅ x / x + M x / x)) - (1 * M x + x * ρy₁ x) = 0 := by
    field_simp
    ring
  have := a1.sub a2
  rwa [h0] at this

/-- **EN:** A real function with zero derivative on the open interval `(0, a)` is constant there — a mathlib
fact restated for the chain.

Derivada nula num aberto convexo implica função constante. -/
theorem constant_on_open_interval (a : ℝ) (F : ℝ → ℝ)
    (hF : ∀ x ∈ Ioo (0:ℝ) a, HasDerivAt F 0 x)
    (x y : ℝ) (hx : x ∈ Ioo (0:ℝ) a) (hy : y ∈ Ioo (0:ℝ) a) :
    F x = F y :=
  (convex_Ioo (0:ℝ) a).is_const_of_fderivWithin_eq_zero (f := F) (𝕜 := ℝ)
    (fun z hz => ((hF z hz).differentiableAt).differentiableWithinAt)
    (fun z hz => by
      rw [fderivWithin_eq_fderiv ((isOpen_Ioo).uniqueDiffWithinAt hz)
        (hF z hz).differentiableAt]
      ext
      simp [(hF z hz).deriv]) hx hy

/-- **EN:** A function constant on `(0, a)` whose one-sided limit at the origin is `0` vanishes on `(0, a)`. The
limit hypothesis is the regularity of the chosen solution: a physical choice, not a derived fact.

**A regularidade na origem fixa a constante em zero.**

⚠️ **É aqui que entra a única hipótese física deste ficheiro.** `hreg` diz que a solução
é a REGULAR — a que não diverge em `r = 0` —, e é ela que o integrador impõe ao arrancar
com a série regular. Lean não a deriva de nada: é escolha do problema. -/
theorem constant_is_zero (a : ℝ) (ha : 0 < a) (F : ℝ → ℝ)
    (hconst : ∀ u ∈ Ioo (0:ℝ) a, ∀ v ∈ Ioo (0:ℝ) a, F u = F v)
    (hreg : Tendsto F (nhdsWithin 0 (Ioo (0:ℝ) a)) (nhds 0))
    (x : ℝ) (hx : x ∈ Ioo (0:ℝ) a) : F x = 0 := by
  have hne : (nhdsWithin (0:ℝ) (Ioo 0 a)).NeBot := by
    rw [nhdsWithin_Ioo_eq_nhdsGT ha]; infer_instance
  have hc : Tendsto F (nhdsWithin (0:ℝ) (Ioo 0 a)) (nhds (F x)) := by
    apply Tendsto.congr' _ tendsto_const_nhds
    filter_upwards [self_mem_nhdsWithin] with u hu
    exact hconst x hx u hu
  exact tendsto_nhds_unique hc hreg

/-- **EN:** The main theorem: under the two degree-0 ODEs and regularity at the origin, `y₅ = M` throughout the
interior — the degree-0 potential equals the enclosed mass, so the deformation contributes no monopole.

**O teorema: o potencial iguala a massa encerrada, logo `k′₀ = 0`.**

Juntando as quatro peças: `y₅ = M` em todo o interior, e em particular a razão
`y₅(x)/(x·y₆(x))` vale `1` — que é dizer que o potencial na superfície é exatamente o da
massa acrescentada, e portanto que a deformação **não contribui** com monopolo nenhum.

⚠️ As hipóteses são as duas EDOs, a definição de `M` como massa encerrada, e a
regularidade na origem. Nenhuma outra. -/
theorem potential_equals_enclosed_mass (a : ℝ) (ha : 0 < a) (y₅ M ρy₁ : ℝ → ℝ)
    (hM : ∀ x ∈ Ioo (0:ℝ) a, HasDerivAt M (ρy₁ x) x)
    (h5 : ∀ x ∈ Ioo (0:ℝ) a, HasDerivAt y₅ (ρy₁ x - y₅ x / x + M x / x) x)
    (hreg : Tendsto (fun t => t * y₅ t - t * M t) (nhdsWithin 0 (Ioo (0:ℝ) a)) (nhds 0))
    (x : ℝ) (hx : x ∈ Ioo (0:ℝ) a) :
    y₅ x = M x := by
  have hzero : ∀ z ∈ Ioo (0:ℝ) a, HasDerivAt (fun t => t * y₅ t - t * M t) 0 z :=
    fun z hz => potential_minus_mass_is_constant y₅ M ρy₁ z (ne_of_gt hz.1)
      (hM z hz) (h5 z hz)
  have hc := constant_is_zero a ha _
    (fun u hu v hv => constant_on_open_interval a _ hzero u v hu hv) hreg x hx
  have hxne : x ≠ 0 := ne_of_gt hx.1
  -- `hc : x * y₅ x - x * M x = 0`; factoriza-se o `x` e usa-se `x ≠ 0`
  have hfac : x * (y₅ x - M x) = 0 := by linarith [hc]
  rcases mul_eq_zero.mp hfac with h | h
  · exact absurd h hxne
  · linarith

/-- **EN:** The final arithmetic step only: given `y₅ x = M x` with `M x ≠ 0`, `y₅/M − 1 = 0`, i.e. `k′₀ = 0`.
The content lives in `potential_equals_enclosed_mass`; this theorem alone does not establish it.

✅ **O corolário que o projeto afirma: `k′₀ = 0`.**

Na normalização de `@farrell1972carga`, `k′₀ = y₅(a)/Φ_carga − 1`, e a condição de
superfície põe `Φ_carga = a·y₆(a) = M(a)`. Pelo teorema acima `y₅ = M`, logo a razão é `1`
e `k′₀` é zero.

⚠️ Enunciado sobre a razão e não sobre `y₅(a) − Φ` de propósito: é a razão que é
adimensional, e é ela que a normalização define.

⚠️⚠️ **Este enunciado é o passo ARITMÉTICO final, e o nome promete mais do que ele
entrega.** Dado `y₅ x = M x`, concluir `y₅ x / M x − 1 = 0` é `a/a − 1 = 0`. **O trabalho
está em `potential_equals_enclosed_mass`**, que prova aquela igualdade a partir do
sistema de equações e da condição de regularidade na origem; aqui só se lhe dá o nome
físico.

⇒ citar este teorema SOZINHO como estabelecendo `k'₀ = 0` seria o defeito que a auditoria
de 2026-09-11 procurava. O manuscrito cita a cadeia inteira — os cinco teoremas deste
ficheiro —, e é a cadeia que sustenta a afirmação. -/
theorem load_love_number_degree_zero_is_null (y₅ M : ℝ → ℝ) (x : ℝ)
    (hMx : M x ≠ 0) (h : y₅ x = M x) : y₅ x / M x - 1 = 0 := by
  rw [h, div_self hMx, sub_self]

end Mapgravy
