/-
Copyright (c) 2026 Daniel Arana. All rights reserved.
Released under GPL-3.0 license as described in the file LICENSE.
Authors: Daniel Arana
-/
import Mathlib

-- ⚠️ O `linter.style.header` do mathlib exige a string "Released under Apache 2.0",
-- que é a licença DELE. Este repositório é GPL-3.0 (ver LICENSE). Desligar o linter
-- é a saída certa; trocar o cabeçalho para calar o aviso declararia licença falsa.
set_option linter.style.header false

/-!
# A separação geoide/quase-geoide é IDENTIDADE, não duas rotas

Formalização do aviso do `CLAUDE.md` §0.1 (registo de convenções) e do docstring de
`geodesy/conventions.py::geopotential_to_helmert_height`.

## O que aconteceu, e por que isto merece uma prova

Este projeto tem duas funções que calculam a separação geoide/quase-geoide:

* `geoid_quasigeoid_separation`, que aplica `H* − H = δg_B · H / γ`;
* a diferença entre `geopotential_to_normal_height` e `geopotential_to_helmert_height`,
  que é a mesma separação obtida por outro caminho.

Elas concordam, e **essa concordância foi lida como confirmação independente** — o
§0.3c #1, *rigor apontado para a referência errada*. Não é confirmação nenhuma: as duas
são **a mesma expressão**, e a única coisa que a comparação mede é o resíduo de segunda
ordem das duas implementações (`0,07 cm` de rms nos `222` marcos do GSVS17).

O que se prova aqui é a álgebra que torna isso inevitável. ⚠️ **Depois disto, «são duas
rotas independentes» deixa de ser uma leitura possível.**

## A física, em três linhas

A gravidade média de Helmert ao longo da linha de prumo vem da redução de
Poincaré–Prey: descer da superfície custa o gradiente de ar livre `FA` **menos** duas
vezes a placa de Bouguer, e a média ao longo do prumo é metade disso. Escrevendo
`B = 2πGρ` para a placa:

  `k = (FA − 2B) / 2`

O passo que fecha tudo é que `k − FA/2 = −B` **exatamente**, e é ele que faz a
diferença entre a gravidade observada reduzida e a normal reduzida colapsar no
distúrbio de Bouguer.
-/

namespace Mapgravy

/-- O coeficiente de Helmert, `k = (FA − 2B)/2`, com `FA` o gradiente de ar livre e
`B = 2πGρ` a placa de Bouguer. Os valores clássicos do NAVD 88 são
`FA = 0,3086` e `B = 0,1119` mGal/m, que dão `k = 0,0424`. -/
noncomputable def kHelmert (FA B : ℝ) : ℝ := (FA - 2 * B) / 2

/-- **O passo que carrega tudo.** `k − FA/2 = −B`, exatamente e sem hipótese nenhuma.

⚠️ É aqui que a «independência» morre: o `k` de Helmert **contém** a placa de Bouguer
por construção, logo qualquer coisa construída com `k` já traz `B` dentro. -/
theorem kHelmert_sub_half_FA (FA B : ℝ) : kHelmert FA B - FA / 2 = -B := by
  unfold kHelmert
  ring

/-- A gravidade média de Helmert ao longo do prumo: a observada no marco, `g`, mais
`k H`. -/
noncomputable def gBarraHelmert (g FA B H : ℝ) : ℝ := g + kHelmert FA B * H

/-- A gravidade normal média ao longo do prumo: a normal na superfície, `γ`, mais
metade do gradiente de ar livre. ⚠️ Meio `FA` e não `k`: é a única diferença entre as
duas, e é ela a separação inteira. -/
noncomputable def gammaBarra (gamma FA H : ℝ) : ℝ := gamma + FA / 2 * H

/-- O distúrbio de Bouguer: o distúrbio de gravidade menos a placa.

⚠️ **O símbolo é `δg_B` e não `Δg_B`, e a distinção não é cosmética.** A literatura reserva
`Δ` para a ANOMALIA — `Δg = g_P − γ_Q`, com a gravidade normal avaliada noutro ponto — e
`δ` para o DISTÚRBIO, `δg = g_P − γ_P`, no mesmo ponto (`@hofmann2006`, eqs. 2-228 e
2-232). A derivação deste ficheiro parte do distúrbio, logo o que ela produz é o distúrbio
de Bouguer.
↩️ **A primeira versão escrevia `Δg_B` no docstring enquanto a função se chamava
`disturbioBouguer`** — a prova a contradizer-se na notação, num projeto cujo manuscrito
trata precisamente de confundir convenções. Apanhado por auditoria conceitual em
2026-09-10. -/
noncomputable def disturbioBouguer (dg B H : ℝ) : ℝ := dg - B * H

/-- **Primeiro teorema: as duas gravidades médias diferem pelo distúrbio de BOUGUER**,
e não por algo novo.

Com `dg = g − γ` o distúrbio de gravidade,

  `ḡ_Helmert − γ̄ = δg_B`

⚠️ Nenhuma hipótese física entra: sai só de `k = (FA − 2B)/2`. -/
theorem gBarra_sub_gammaBarra (g gamma FA B H : ℝ) :
    gBarraHelmert g FA B H - gammaBarra gamma FA H
      = disturbioBouguer (g - gamma) B H := by
  unfold gBarraHelmert gammaBarra disturbioBouguer kHelmert
  ring

/-- **O teorema principal: `H* − H = δg_B · H / γ̄` é uma IDENTIDADE.**

As duas alturas saem do MESMO número geopotencial `C`, cada uma dividida pela sua
gravidade média: `C = ḡ·H` para Helmert e `C = γ̄·H*` para a normal. Daí

  `H* − H = Δg_B · H / γ̄`

⚠️ **As hipóteses são só as duas definições e uma não-divisão-por-zero.** Não há física a
acrescentar: quem comparar as duas rotas esperando confirmação independente está a
conferir uma fórmula contra ela mesma.

⚠️⚠️ **E o enunciado tem uma subtileza que o Lean me obrigou a ver.** A primeira versão
deste teorema escrevia a hipótese como `H = C / ḡ(H)` — e o `subst` recusou-a, porque
`H` ocorre nos DOIS lados: a altura de Helmert é definida por uma equação **implícita**
(é por isso que `geopotential_to_helmert_height` itera três vezes em vez de dividir uma
vez). A forma correta é multiplicativa, `C = ḡ(H)·H`, que diz o mesmo sem circularidade.

⚠️ **Fica também explícito onde vive o resíduo que o projeto mede.** Aqui `γ̄` é avaliada
ao longo da MESMA linha de prumo `H` que a de Helmert. Na cadeia, `H*` sai de `γ̄`
avaliada ao longo do seu próprio prumo — e a diferença entre avaliar `γ̄` em `H` ou em
`H*` **é** o resíduo de segunda ordem de `0,07 cm` de rms nos `222` marcos do GSVS17.
⇒ a identidade é exata sob a hipótese escrita; o que a comparação numérica mede é a folga
dessa hipótese, e nada mais. -/
theorem separacao_e_identidade (C g gamma FA B H Hstar : ℝ)
    (hgamma : gammaBarra gamma FA H ≠ 0)
    (hH : C = gBarraHelmert g FA B H * H)
    (hHstar : C = gammaBarra gamma FA H * Hstar) :
    Hstar - H = disturbioBouguer (g - gamma) B H * H / gammaBarra gamma FA H := by
  have hstar : Hstar = gBarraHelmert g FA B H * H / gammaBarra gamma FA H := by
    rw [eq_div_iff hgamma, mul_comm]
    exact hHstar.symm.trans hH
  rw [hstar, ← gBarra_sub_gammaBarra g gamma FA B H]
  field_simp

/-- ✅ **O controlo aritmético: o `0,0424` do NAVD 88 sai dos dois literais publicados.**

`@zilkoski1992navd88` publica `H = C/(g + 0.0424 H)`; os dois números de que ele vem
são o gradiente de ar livre `0,3086` e a placa de Bouguer `0,1119` mGal/m.

⚠️ Isto não é um teorema profundo — é um portão contra digitar o `0,0424` à mão, que é
o modo de falha que o §0.3c cataloga. -/
theorem kHelmert_classico : kHelmert 0.3086 0.1119 = 0.0424 := by
  unfold kHelmert
  norm_num


/-- ✅ **`ḡ = g + 0,0424 H`, a forma publicada da gravidade média de Helmert.**

`@hofmann2006` (`bibliografia/md/hofmann2006.md`, eq. 4–31): *«ḡ = g + 0.0424 H (g in
gal, H in km). The factor 0.0424 refers to the normal density ρ = 2.67 g/cm3»*; e
`@fluryrummel2009` (eq. 18): *«ḡ_PL = g_P + 0.0424 mGal/m H»*, que a eq. (17) deles
escreve por extenso como `g_P + 0.1543 H − 2πGρ₀H` — precisamente `g + (FA/2 − B)·H`.

⚠️ `kHelmert_classico` prende o coeficiente; este prende a DEFINIÇÃO que o usa — o sinal
e o sítio onde `k` entra. -/
theorem gBarraHelmert_classico (g H : ℝ) :
    gBarraHelmert g 0.3086 0.1119 H = g + 0.0424 * H := by
  unfold gBarraHelmert kHelmert
  norm_num

/-- ✅ **`γ̄ = γ_Q + 0,1543 H`, a forma publicada da gravidade normal média.**

`@fluryrummel2009` (`bibliografia/md/fluryrummel2009.md`, l. 359, a caminho da eq. 21):
*«With γ_Q ≈ γ̄ − 0.1543 mGal/m H_N ≈ γ̄ − 0.1543 mGal/m H»*. O `0,1543` é metade do
gradiente de ar livre `0,3086` da eq. (3–26) de `@hofmann2006`, e é a linearização da
eq. (4–60) dele a partir do teluroide em vez do elipsoide.

⚠️ Aqui `γ` é a normal NA SUPERFÍCIE (`γ_Q`, no teluroide), e é por isso que o termo entra
com `+`: descendo ao longo do prumo a gravidade normal cresce. -/
theorem gammaBarra_classico (gamma H : ℝ) :
    gammaBarra gamma 0.3086 H = gamma + 0.1543 * H := by
  unfold gammaBarra
  norm_num

/-- ✅ **A placa de Bouguer à densidade padrão: `2πGρH = 0,1119 H`.**

`@hofmann2006` (eqs. 3–27 e 3–28): *«A_B = 2πGρH […] With standard density ρ = 2.67
g cm−3 this becomes A_B = 0.1119 H [mgal] for H in meters»*. A forma «distúrbio menos
placa» é a eq. (22) de `@fluryrummel2009`, *«g_BO = g_P − γ_Q − 2πGρ₀H + g_TC»*, com a
correção de terreno posta de lado — que é o que a eq. (21) deles faz para chegar a
`γ̄ − ḡ = −g_BO`. ⚠️ Eles chamam-lhe *anomalia* porque avaliam `γ` no teluroide `Q`; a
forma é a mesma, e a distinção de nome é a que o docstring de `disturbioBouguer` discute.

⚠️ É o mais fraco dos três portões deste bloco: prende o literal e o SINAL da placa. O que
lhe dá conteúdo é o `gBarra_sub_gammaBarra`: com os três literais publicados, a identidade
dá `ḡ − γ̄ = g − γ − 0,1119 H`, que é a eq. (21) de `@fluryrummel2009`. -/
theorem disturbioBouguer_classico (dg H : ℝ) :
    disturbioBouguer dg 0.1119 H = dg - 0.1119 * H := by
  unfold disturbioBouguer
  norm_num

end Mapgravy
