/-
Copyright (c) 2026 Daniel Arana. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Daniel Arana
-/
import Mathlib

/-!
# A razão de Boussinesq depende SÓ de `ν`, e é isso que a torna um oráculo

Formalização da propriedade que sustenta a verificação cruzada da §5.15 do painel de
frentes, e a `#sec:oceanica-love-calculados` do livro.

## Por que esta propriedade é o resultado, e não a fórmula

Em grau alto, uma Terra estratificada responde a uma carga como um semi-espaço elástico
com as propriedades da camada mais superficial — nada mais do modelo entra. Daí saem duas
formas fechadas, uma para o deslocamento vertical e outra para o horizontal:

  `h'∞  = −g²(1−ν) / (2πGμ)`        (a eq. 36 de `@farrell1972carga`)
  `(n·l')∞ = (1−2ν)g² / (4πGμ)`     (o análogo horizontal, derivado neste projeto)

Cada uma sozinha exige conhecer `g`, `μ` e `ν` do modelo. **A razão entre as duas não:**
`g` e `μ` cancelam, e sobra uma função só de `ν`.

⚠️⚠️ **É esse cancelamento que transforma a fórmula num ORÁCULO.** Sem ele, comparar o
nosso `l'` com o de `@farrell1972carga` exigiria saber o `μ` do modelo dele — que o artigo
não tabula. Com ele, bastam os `v_p` e `v_s` que a Fig. 2 publica, de que sai `ν`
diretamente. ⇒ a razão prevê o `∞` da Tabela A2 dele a quatro dígitos, e é a única
verificação externa que o `l'` tem.

## O que se prova aqui, e o que fica de fora

Prova-se que a razão **não depende** de `g` nem de `μ` — quantificando sobre eles. ⚠️ Isso
é mais forte que calcular a razão num caso: é dizer que nenhuma escolha daqueles dois
parâmetros a move.

⚠️ **Não se prova a física.** Que o deslocamento de superfície de um semi-espaço sob carga
harmónica seja `u_z = −p(1−ν)/(μk)` e `u_x = −(1−2ν)p/(2μk)` é a solução de Boussinesq, e
Lean não tem o que dizer sobre ela. O que se prova é que, **dadas** as duas formas, a razão
é a que se afirma e é invariante nos parâmetros que se afirma.
-/

namespace Mapgravy

/-- `h'∞ = −g²(1−ν)/(2πGμ)` — o limite de grau alto do deslocamento VERTICAL sob carga. -/
noncomputable def hInf (G g mu nu : ℝ) : ℝ := -g ^ 2 * (1 - nu) / (2 * Real.pi * G * mu)

/-- `(n·l')∞ = (1−2ν)g²/(4πGμ)` — o mesmo para o deslocamento HORIZONTAL. -/
noncomputable def nlInf (G g mu nu : ℝ) : ℝ :=
  (1 - 2 * nu) * g ^ 2 / (4 * Real.pi * G * mu)

/-- **EN:** Given the two Boussinesq high-degree (asymptotic) forms, the ratio `(n·l')∞ / h'∞` equals
`−(1−2ν)/(2(1−ν))`: `g` and `μ` cancel. The only hypotheses are non-vanishing conditions.

**O teorema: a razão vale `−(1−2ν)/(2(1−ν))`, e `g` e `μ` desapareceram.**

⚠️ As hipóteses são todas de não-divisão-por-zero — `G`, `g`, `μ` não nulos e `ν ≠ 1`.
Nenhuma é física: a física está nas duas definições. -/
theorem boussinesq_ratio (G g mu nu : ℝ)
    (hG : G ≠ 0) (hg : g ≠ 0) (hmu : mu ≠ 0) (hnu : nu ≠ 1) :
    nlInf G g mu nu / hInf G g mu nu = -(1 - 2 * nu) / (2 * (1 - nu)) := by
  have hpi : Real.pi ≠ 0 := Real.pi_ne_zero
  have h1 : (1 : ℝ) - nu ≠ 0 := sub_ne_zero.mpr (Ne.symm hnu)
  unfold nlInf hInf
  field_simp
  ring

/-- **EN:** The Boussinesq ratio is invariant under any change of `G`, `g`, `μ` at fixed Poisson ratio `ν` —
which is what lets it serve as an oracle for a model whose `μ` is not tabulated.

**A INVARIÂNCIA, que é o que faz da razão um oráculo.**

Duas escolhas quaisquer de `(g, μ)` — e de `G`, já agora — dão a MESMA razão, desde que o
`ν` seja o mesmo. ⚠️ É este enunciado, e não o anterior, que autoriza a comparação com um
modelo cujo `μ` não conhecemos.

Precedente do defeito que ele impede: o painel registou durante uma frente inteira que
`n·l'` **não tinha oráculo independente**, porque nenhuma fonte do acervo publica `l'` de
carga do PREM. A ausência era de TABELA; a razão sempre esteve disponível. -/
theorem ratio_independent_of_g_and_mu
    (G₁ g₁ mu₁ G₂ g₂ mu₂ nu : ℝ)
    (h₁ : G₁ ≠ 0) (h₂ : g₁ ≠ 0) (h₃ : mu₁ ≠ 0)
    (h₄ : G₂ ≠ 0) (h₅ : g₂ ≠ 0) (h₆ : mu₂ ≠ 0) (hnu : nu ≠ 1) :
    nlInf G₁ g₁ mu₁ nu / hInf G₁ g₁ mu₁ nu
      = nlInf G₂ g₂ mu₂ nu / hInf G₂ g₂ mu₂ nu := by
  rw [boussinesq_ratio G₁ g₁ mu₁ nu h₁ h₂ h₃ hnu,
      boussinesq_ratio G₂ g₂ mu₂ nu h₄ h₅ h₆ hnu]

/-- `ν` a partir das velocidades sísmicas: `ν = (v_p² − 2v_s²) / (2(v_p² − v_s²))`.

É por aqui que a verificação externa entra: `@farrell1972carga` **não** tabula `μ` nem `ν`
do modelo dele, mas publica `v_p` e `v_s` da camada de topo na Fig. 2 (p. 784). -/
noncomputable def poissonFromVelocities (vp vs : ℝ) : ℝ :=
  (vp ^ 2 - 2 * vs ^ 2) / (2 * (vp ^ 2 - vs ^ 2))

/-- **EN:** Closed arithmetic check: with `v_p = 6.14`, `v_s = 3.55` km/s and Farrell's `h'∞ = −5.005`, the
ratio reproduces the tabulated `(n·l')∞ = 1.673` to within `1e-3`, the table's own resolution.

✅ **O controlo externo, em aritmética fechada.**

Com `v_p = 6,14` e `v_s = 3,55` km/s — os valores da Fig. 2 de `@farrell1972carga` para o
topo do Gutenberg–Bullen — o `ν` sai `≈ 0,2489` e a razão `≈ −0,3343`. Multiplicada pelo
`h'∞ = −5,005` da eq. (36) dele, dá `≈ 1,673`, que é o `∞` que a Tabela A2 imprime na
coluna `n·l'`.

⚠️ **A tolerância `1e-3` é a resolução da FONTE**, não uma folga escolhida: a Tabela A2
publica `1,673`, com três casas decimais. Apertar mais seria exigir do artigo uma precisão
que ele não imprime — o §0.3c-quater do `CLAUDE.md`. -/
theorem control_against_farrell :
    |(-5.005) * (-(1 - 2 * poissonFromVelocities 6.14 3.55)
        / (2 * (1 - poissonFromVelocities 6.14 3.55))) - 1.673| < 1e-3 := by
  unfold poissonFromVelocities
  norm_num [abs_lt]

/-! ## O limite rígido do deslocamento, provado em vez de assumido -/

/-- **EN:** The asymptotic (high-degree) vertical load Love number `h'∞` tends to `0` as the shear modulus
`μ → ∞`. Boussinesq regime only; this is not the rigid limit at finite degree.

**`h'∞ → 0` quando a rigidez diverge.**

Uma Terra rígida não se deforma, e é isso que este teorema afirma — no regime em que a
forma fechada vale. A prova é o que se espera: `h'∞` é uma constante dividida por `μ`, e
uma constante dividida por algo que tende para infinito tende para zero.

⚠️⚠️ **Este enunciado substitui um `(0 : ℝ) = 0`.** A versão anterior deste ficheiro tinha
um teorema em que `h` e `l` **não ocorriam**, e que portanto não afirmava nada sobre
deslocamento; o manuscrito citava-o a sustentar `h|rígido = l|rígido = 0`. Uma revisão
adversarial apanhou-o. O conteúdo físico — que a deformação *desaparece* quando a rigidez
cresce sem limite — é este limite, e é demonstrável.

⚠️ **O que ele NÃO é:** o limite rígido em grau finito. As formas fechadas de Boussinesq
são o comportamento de grau alto; obter `h, l → 0` para todo grau exigiria o sistema
elasto-gravitacional, que não está formalizado aqui. -/
theorem hInf_tendsto_zero_as_rigidity_diverges (G g nu : ℝ) :
    Filter.Tendsto (fun mu => hInf G g mu nu) Filter.atTop (nhds 0) := by
  have h : (fun mu => hInf G g mu nu)
      = fun mu => (-g ^ 2 * (1 - nu) / (2 * Real.pi * G)) / mu := by
    funext mu
    unfold hInf
    rw [div_div]
  rw [h]
  exact Filter.Tendsto.div_atTop tendsto_const_nhds Filter.tendsto_id

/-- **EN:** Likewise, the asymptotic horizontal load Love number `(n·l')∞` tends to `0` as `μ → ∞`;
Boussinesq regime only.

**`(n·l')∞ → 0` quando a rigidez diverge** — o mesmo para o deslocamento horizontal. -/
theorem nlInf_tendsto_zero_as_rigidity_diverges (G g nu : ℝ) :
    Filter.Tendsto (fun mu => nlInf G g mu nu) Filter.atTop (nhds 0) := by
  have h : (fun mu => nlInf G g mu nu)
      = fun mu => ((1 - 2 * nu) * g ^ 2 / (4 * Real.pi * G)) / mu := by
    funext mu
    unfold nlInf
    rw [div_div]
  rw [h]
  exact Filter.Tendsto.div_atTop tendsto_const_nhds Filter.tendsto_id

/-- **EN:** Both asymptotic displacement load Love numbers vanish in the rigid limit `μ → ∞`. This is the
displacement half of the rigid-limit dichotomy, established only in the Boussinesq (high-degree) regime.

**Os dois deslocamentos desaparecem juntos no limite rígido.**

É o enunciado que o manuscrito cita: no limite de rigidez infinita os fatores do
deslocamento — vertical e horizontal — tendem ambos para zero, e portanto a série que eles
multiplicam anula-se. O contraste com `δₙ = 1` e `D = 1` deixa de ser entre um teorema e
uma trivialidade, e passa a ser entre dois teoremas. -/
theorem displacement_vanishes_in_rigid_limit (G g nu : ℝ) :
    Filter.Tendsto (fun mu => hInf G g mu nu) Filter.atTop (nhds 0) ∧
    Filter.Tendsto (fun mu => nlInf G g mu nu) Filter.atTop (nhds 0) :=
  ⟨hInf_tendsto_zero_as_rigidity_diverges G g nu, nlInf_tendsto_zero_as_rigidity_diverges G g nu⟩

/-- **EN:** The same check as `control_against_farrell`, but through the definitions `nlInf`/`hInf` for arbitrary
non-zero `G`, `g`, `μ`. A common wrong factor in both definitions would still cancel and go undetected.

✅ **O mesmo controlo, agora sobre as DEFINIÇÕES `nlInf` e `hInf`, e não sobre a razão
escrita à mão.**

O `control_against_farrell` compara a forma `−(1−2ν)/(2(1−ν))` com o `1,673` da Tabela A2
de `@farrell1972carga` (`bibliografia/md/farrell1972carga.md`, l. 1783 e ss.: linha `∞*`,
colunas `−h'` = `5.005` e `n·l'` = `1.673`, *«Boussinesq approximation, equations 36»*);
mas nele `hInf` e `nlInf` NÃO OCORREM — um erro numa das duas definições só seria apanhado
pelo `boussinesq_ratio`. Este enunciado fecha esse elo: para QUALQUER `G`, `g`, `μ` não
nulos, `−5,005 · nlInf/hInf` cai a menos de `1e-3` do `1,673` publicado.

⚠️⚠️ **O que ele NÃO apanha, e nenhuma âncora do acervo apanha:** um mesmo fator errado nas
DUAS definições cancela na razão. Prender `hInf` sozinho ao `−5,005` exigiria o `μ` da
camada de topo do Gutenberg–Bullen, que o artigo não tabula (a Fig. 2 dá `v_p` e `v_s`,
não `ρ`). Fica registado como limite, não como portão. -/
theorem control_against_farrell_via_definitions (G g mu : ℝ)
    (hG : G ≠ 0) (hg : g ≠ 0) (hmu : mu ≠ 0) :
    |(-5.005) * (nlInf G g mu (poissonFromVelocities 6.14 3.55)
        / hInf G g mu (poissonFromVelocities 6.14 3.55)) - 1.673| < 1e-3 := by
  have hnu : poissonFromVelocities 6.14 3.55 ≠ 1 := by
    unfold poissonFromVelocities
    norm_num
  rw [boussinesq_ratio G g mu _ hG hg hmu hnu]
  exact control_against_farrell

end Mapgravy
