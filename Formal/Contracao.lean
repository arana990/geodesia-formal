/-
Copyright (c) 2026 Daniel Arana. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Daniel Arana
-/
import Mathlib
import Formal.Alturas

/-!
# Por que três iterações bastam: a iteração da altura normal é uma contração

D2(b) do parecer de 2026-09-16 (`docs/pareceres/paper4_revisao_adversarial_2026-09-16.md`):
o único candidato desta frente que não é `ring`, e o único que faz uma PREVISÃO que se
confronta com uma medida.

`geopotential_to_normal_height` itera `H ← C/γ̄(H)` três vezes e a docstring diz «converge
em poucas iterações porque a dependência é fraca». Aqui isso vira teorema com constante:
com `φ(H) = C/(γ₀ − a·H)`, para `H₁, H₂` num intervalo em que `γ̄ ≥ m > 0`,

  `|φ(H₁) − φ(H₂)| ≤ (C·a/m²) · |H₁ − H₂|`,

logo o erro cai por `q = C·a/m²` a cada passo, e depois de `n` passos vale
`|H_n − H*| ≤ qⁿ·|H₀ − H*|`. Com `C = 40 000 m²s⁻²` (≈ 4 km), `a = FA/2 = 1,543·10⁻⁶ s⁻²` e
`m = 9,7 m/s²`, `q = 6,56·10⁻⁴`; o chute `H₀ = C/γ₀` está a `2,62 m` da raiz; e a previsão
do teorema para três iterações é `q³·2,62 = 7,4·10⁻¹⁰ m`.

**Medido antes de enunciar** (`docs/painel/formal_convencoes.md`, T6): o resíduo das três
iterações do código a `4 082 m` é `6,9·10⁻¹⁰ m`. A previsão fecha com a medida a `7 %` —
e o código usa o modelo quadrático por latitude, não este linear: o termo que falta aqui
é o que explica a diferença. É a primeira vez neste diretório que um teorema prevê um
número que um script mediu de forma independente.

## O que este ficheiro NÃO faz

Não usa `ContractingWith` da mathlib: o que se quer não é o ponto fixo de Banach (a
existência da raiz já está em `Alturas.lean`, com forma fechada), é a CONSTANTE `q`
explícita e o erro após `n` passos — e isso é uma indução de dez linhas sobre a
desigualdade de Lipschitz, mais legível do que o instanciar da estrutura métrica.
-/

namespace Mapgravy

/-- A iteração do registo: `φ(H) = C / (γ₀ − a·H)`, com `a = FA/2`. -/
noncomputable def iteracaoAlturaNormal (gamma0 a C H : ℝ) : ℝ := C / (gamma0 - a * H)

/-- **Lipschitz com constante explícita.** Se `γ̄(H₁), γ̄(H₂) ≥ m > 0`, então
`|φ(H₁) − φ(H₂)| ≤ (C·a/m²)·|H₁ − H₂|`. -/
theorem iteracao_lipschitz (gamma0 a C H₁ H₂ m : ℝ) (hC : 0 ≤ C) (ha : 0 ≤ a) (hm : 0 < m)
    (h₁ : m ≤ gamma0 - a * H₁) (h₂ : m ≤ gamma0 - a * H₂) :
    |iteracaoAlturaNormal gamma0 a C H₁ - iteracaoAlturaNormal gamma0 a C H₂|
      ≤ C * a / m ^ 2 * |H₁ - H₂| := by
  unfold iteracaoAlturaNormal
  have d₁ : 0 < gamma0 - a * H₁ := lt_of_lt_of_le hm h₁
  have d₂ : 0 < gamma0 - a * H₂ := lt_of_lt_of_le hm h₂
  have key : C / (gamma0 - a * H₁) - C / (gamma0 - a * H₂)
      = C * a * (H₁ - H₂) / ((gamma0 - a * H₁) * (gamma0 - a * H₂)) := by
    field_simp; ring
  rw [key, abs_div, abs_mul, abs_mul, abs_of_nonneg hC, abs_of_nonneg ha,
      abs_of_pos (mul_pos d₁ d₂)]
  have hden : m ^ 2 ≤ (gamma0 - a * H₁) * (gamma0 - a * H₂) := by
    calc m ^ 2 = m * m := by ring
      _ ≤ (gamma0 - a * H₁) * (gamma0 - a * H₂) :=
          mul_le_mul h₁ h₂ hm.le d₁.le
  rw [div_le_iff₀ (mul_pos d₁ d₂)]
  calc C * a * |H₁ - H₂|
      = C * a / m ^ 2 * |H₁ - H₂| * m ^ 2 := by field_simp
    _ ≤ C * a / m ^ 2 * |H₁ - H₂| * ((gamma0 - a * H₁) * (gamma0 - a * H₂)) := by
        apply mul_le_mul_of_nonneg_left hden
        positivity

/-- A bola `|H − H*| ≤ r` fica dentro da região `γ̄ ≥ m` quando `γ̄(H*) − a·r ≥ m`. -/
theorem bola_dentro_da_regiao (gamma0 a Hstar H r m : ℝ) (ha : 0 ≤ a)
    (hreg : m ≤ gamma0 - a * Hstar - a * r) (hH : |H - Hstar| ≤ r) :
    m ≤ gamma0 - a * H := by
  have := (abs_le.mp hH).2
  nlinarith

/-- **O erro após `n` iterações.** Se `H*` é ponto fixo de `φ`, `q = C·a/m² ≤ 1`, e a bola de
raio `r = |H₀ − H*|` em torno de `H*` está na região `γ̄ ≥ m`, então
`|φⁿ(H₀) − H*| ≤ qⁿ·|H₀ − H*|` — e todos os iterados ficam na bola. -/
theorem erro_apos_n_iteracoes (gamma0 a C Hstar H₀ m : ℝ) (hC : 0 ≤ C) (ha : 0 ≤ a)
    (hm : 0 < m) (hfix : iteracaoAlturaNormal gamma0 a C Hstar = Hstar)
    (hq : C * a / m ^ 2 ≤ 1)
    (hreg : m ≤ gamma0 - a * Hstar - a * |H₀ - Hstar|) (n : ℕ) :
    |(iteracaoAlturaNormal gamma0 a C)^[n] H₀ - Hstar|
      ≤ (C * a / m ^ 2) ^ n * |H₀ - Hstar| := by
  set q := C * a / m ^ 2 with hqdef
  set r := |H₀ - Hstar| with hrdef
  have hq0 : 0 ≤ q := by positivity
  -- invariante: o iterado está na bola de raio r E satisfaz a cota geométrica
  have inv : ∀ k : ℕ, |(iteracaoAlturaNormal gamma0 a C)^[k] H₀ - Hstar| ≤ q ^ k * r
      ∧ |(iteracaoAlturaNormal gamma0 a C)^[k] H₀ - Hstar| ≤ r := by
    intro k
    induction k with
    | zero => simp [hrdef]
    | succ k ih =>
        obtain ⟨ihq, ihr⟩ := ih
        rw [Function.iterate_succ_apply']
        have hin : m ≤ gamma0 - a * (iteracaoAlturaNormal gamma0 a C)^[k] H₀ :=
          bola_dentro_da_regiao gamma0 a Hstar _ r m ha hreg ihr
        have hstar : m ≤ gamma0 - a * Hstar :=
          bola_dentro_da_regiao gamma0 a Hstar Hstar r m ha hreg
            (by simp only [sub_self, abs_zero]; positivity)
        have step := iteracao_lipschitz gamma0 a C _ Hstar m hC ha hm hin hstar
        rw [hfix] at step
        have hqk : |(iteracaoAlturaNormal gamma0 a C)^[k] H₀ - Hstar| ≤ q ^ k * r := ihq
        constructor
        · calc |iteracaoAlturaNormal gamma0 a C ((iteracaoAlturaNormal gamma0 a C)^[k] H₀) - Hstar|
              ≤ q * |(iteracaoAlturaNormal gamma0 a C)^[k] H₀ - Hstar| := step
            _ ≤ q * (q ^ k * r) := by gcongr
            _ = q ^ (k + 1) * r := by ring
        · calc |iteracaoAlturaNormal gamma0 a C ((iteracaoAlturaNormal gamma0 a C)^[k] H₀) - Hstar|
              ≤ q * |(iteracaoAlturaNormal gamma0 a C)^[k] H₀ - Hstar| := step
            _ ≤ 1 * r := by gcongr
            _ = r := one_mul r
  exact (inv n).1

/-! ## O número fica no Python, de propósito

`q³·|H₀ − H*| = 7,4·10⁻¹⁰ m` com `C = 40 000`, `a = 1,543·10⁻⁶`, `m = 9,7` é aritmética, e
um teorema que só a fizesse seria o mesmo «verdadeiro e vazio» que o parecer apanhou em
`Bruns.lean`. A confrontação previsão–medida vive em
`mapgravy/tests/test_contracao_preve_o_residuo.py`: calcula a cota do teorema com as
constantes do registo e exige que o resíduo MEDIDO das três iterações do código fique
abaixo dela — e não muito abaixo, para que a cota seja justa e não só verdadeira. -/

end Mapgravy
