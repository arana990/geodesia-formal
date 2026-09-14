/-
Copyright (c) 2026 Daniel Arana. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Daniel Arana
-/
import Mathlib

/-!
# O limite rígido decide quem precisa de números de Love

Formalização da **regra emergente** do projeto, hoje registada em prosa e apoiada em
quatro casos observados (`docs/frentes_de_desenvolvimento.md`):

> *uma grandeza cujo limite rígido não anula a série pode dispensar números de Love; uma
> que o anularia tem de os aplicar.*

## De onde veio a regra, e por que uma prova ajuda

Ela nasceu de uma previsão pré-registada que **acertou numa grandeza e errou na outra**.
Esperava-se que a opção `RIGIDEARTH=1` do `PREDICT` aplicasse um número de Love tanto na
inclinação como no deslocamento horizontal. Aplica no deslocamento e **não** aplica na
inclinação — e a razão é a que este ficheiro prova:

* o fator da inclinação é `γ = 1 + k − h`, e `γ(0,0) = 1`;
* o do deslocamento horizontal é o próprio `l`, e `l = 0` no limite rígido.

Uma série de deslocamento de Terra rígida seria **identicamente nula**, e o programa não
teria o que escrever. ⇒ ali o número de Love não é refinamento, é condição de existência.

⚠️ **O que se prova aqui é a metade algébrica da regra**, e é ela que a torna previsível
em vez de observada: que os fatores da gravidade e da inclinação valem exatamente `1` no
limite rígido, para **todo** grau, e que os do deslocamento valem `0`. A metade física —
que «aplicar um fator `1`» seja o mesmo que «não aplicar fator» — é a definição de fator
multiplicativo, e essa não precisa de prova.

⚠️⚠️ **E o que NÃO se prova:** que o `PREDICT` faça isto. Que ele aplique `l` e não
aplique `γ` é medida, registada no painel com o seu domínio (Schiltach/BFO, `168` épocas,
catálogo HW95). Lean não tem o que dizer sobre o comportamento de um binário.
-/

namespace Mapgravy

/-- O fator gravimétrico do grau `n`, `δₙ = 1 + (2/n)hₙ − ((n+1)/n)kₙ`.

⚠️ **O grau entra como real e não como natural**, e é deliberado: a fórmula divide por
`n`, e a divisão em `ℕ` truncaria. O `hn : (n:ℝ) ≠ 0` aparece em cada teorema por isso. -/
noncomputable def gravimetricFactor (n h k : ℝ) : ℝ := 1 + (2 / n) * h - ((n + 1) / n) * k

/-- O fator de diminuição da inclinação, `γ = 1 + k − h`. Não depende do grau. -/
noncomputable def tiltFactor (h k : ℝ) : ℝ := 1 + k - h

/-- **EN:** In the rigid limit (`h = k = 0`) the gravimetric factor equals exactly `1` for every degree.
It holds for all real `n` only because Lean's division is total (`x/0 = 0`); degree `0` has no physical meaning here.

**O limite rígido do fator gravimétrico é `1`, para TODO grau.**

É a metade da regra que decide que a gravidade pode dispensar números de Love: aplicar um
fator `1` é não aplicar fator nenhum, e a série de Terra rígida sobrevive intacta.

⚠️⚠️ **Não há hipótese, e a razão é uma armadilha do Lean que vale conhecer.** Escrevi
primeiro `(hn : n ≠ 0)`, esperando precisar dela para dividir por `n` — e o compilador
avisou que a hipótese **não é usada**. Em Lean a divisão é TOTAL: `x / 0 = 0` por
definição, logo `(2/n) * 0 = 0` vale mesmo em `n = 0`.

⇒ o teorema é mais forte sem a hipótese, e ao mesmo tempo **isso não significa que o grau
`0` faça sentido aqui**. A totalidade da divisão é uma conveniência do Lean, não uma
afirmação sobre a física: em `n = 0` o `δ` do projeto não está definido, e é o
`gravimetricFactor_eq_one_iff` abaixo — onde a hipótese É necessária — que mostra a diferença. **Um
teorema verdadeiro em Lean pode ser vazio de conteúdo físico, e distinguir os dois casos é
trabalho do leitor, não do compilador.** -/
theorem gravimetricFactor_rigid (n : ℝ) : gravimetricFactor n 0 0 = 1 := by
  unfold gravimetricFactor
  simp

/-- **EN:** In the rigid limit the tilt (diminishing) factor `γ = 1 + k − h` equals exactly `1`.

**O limite rígido do fator da inclinação também é `1`**, e aqui sem hipótese nenhuma:
`γ` não divide por nada. -/
theorem tiltFactor_rigid : tiltFactor 0 0 = 1 := by
  unfold tiltFactor
  ring

/-- **EN:** The algebraic half of the rigid-limit rule: gravimetric factor and tilt factor both equal exactly `1`
for a rigid Earth. The displacement half is NOT here — see `displacement_vanishes_in_rigid_limit`, which holds only asymptotically.

**A metade que este ficheiro pode provar: `δ` e `γ` sobrevivem ao limite rígido.**

«Sobreviver» é valer **exatamente `1`**, que é mais forte que ser não-nulo: um fator
multiplicativo igual a `1` deixa a série como está, e é por isso que a gravidade e a
inclinação de Terra rígida ficam bem definidas SEM modelo de Terra nenhum.

⚠️⚠️ **A outra metade da dicotomia NÃO está aqui, e a razão é honesta.** Uma versão
anterior deste ficheiro fechava o enunciado com um terceiro conjunto `(0 : ℝ) = 0` — em que
`h` e `l` não ocorriam —, e o manuscrito citava-o a sustentar que o limite rígido do
deslocamento *estava verificado por máquina*. Não estava: aquilo não afirmava nada. Uma
revisão adversarial apanhou-o.

⇒ o limite rígido do deslocamento é agora um teorema a sério, e vive onde as formas
fechadas vivem: `Boussinesq.displacement_vanishes_in_rigid_limit`, que prova
`h'∞ → 0` e `(n·l')∞ → 0` quando `μ → ∞`. ⚠️ Ele vale no regime ASSINTÓTICO, que é onde
aquelas formas valem; em grau finito exigiria o sistema elasto-gravitacional, que não está
formalizado. -/
theorem rigid_limit_dichotomy (n : ℝ) :
    gravimetricFactor n 0 0 = 1 ∧ tiltFactor 0 0 = 1 :=
  ⟨gravimetricFactor_rigid n, tiltFactor_rigid⟩

/-- **EN:** For `n ≠ 0`, the gravimetric factor equals `1` if and only if `2h = (n+1)k`; so `δₙ = 1` does
not imply a rigid Earth.

**Quando é que `δₙ = 1` sem a Terra ser rígida?** Exatamente quando `2h = (n+1)k`.

⚠️ É a caracterização que impede uma leitura errada do teorema anterior: `δ = 1` **não**
implica `h = k = 0`. Há uma reta inteira de pares `(h,k)` em que o fator gravimétrico vale
`1` com a Terra a deformar-se — a subida do ponto e a redistribuição de massa cancelam-se
na gravidade.

Ela é a irmã exata do achado que o projeto irmão teve ao formalizar a anisotropia: lá a
condição de igualdade publicada era mais estreita que a verdadeira, e a formalização deu o
contraexemplo. -/
theorem gravimetricFactor_eq_one_iff (n h k : ℝ) (hn : n ≠ 0) :
    gravimetricFactor n h k = 1 ↔ 2 * h = (n + 1) * k := by
  unfold gravimetricFactor
  -- o `field_simp` limpa o `1/n` usando `hn`, e deixa `n + 2h − (n+1)k = n ↔ 2h = (n+1)k`
  field_simp
  constructor <;> intro h₁ <;> linarith

/-- **EN:** At degree 2 the general gravimetric factor reduces to the classical form `δ₂ = 1 + h − (3/2)k`.

✅ **O controlo: no grau `2` a fórmula geral dá a forma clássica** `δ₂ = 1 + h − (3/2)k`.

⚠️ Existe porque a fórmula geral é a que se implementa e a clássica é a que se cita; se
elas divergissem, a divergência passaria despercebida em toda a literatura de grau 2. -/
theorem gravimetricFactor_degree_two (h k : ℝ) : gravimetricFactor 2 h k = 1 + h - (3 / 2) * k := by
  unfold gravimetricFactor
  norm_num

/-- **EN:** Arithmetic check against a published value: PREM's `h₂ = 0.6032`, `k₂ = 0.2980` give the published
tilt factor `γ₂ = 0.6948`; pins the signs in the definition, not the physics.

✅ **O controlo contra VALOR publicado: o `γ₂` do PREM sai dos `h₂`, `k₂` do PREM.**

`@agnew2015mares` (`bibliografia/md/agnew2015mares.md`, l. 731–732) publica *«For a
standard modern Earth model (PREM), h2 = 0.6032, k2 = 0.2980»*, e três parágrafos adiante
(l. 768–769) *«γn being called the diminishing factor. For the PREM model, γ2 = 0.6948»*.
`1 + 0,2980 − 0,6032 = 0,6948`, exato às quatro casas que a fonte imprime.

⚠️ É a mesma classe de portão que `kHelmert_classical`: não prova física, prova que a
DEFINIÇÃO deste ficheiro é a fórmula que a fonte usa para chegar ao número que a fonte
publica — com os sinais de `h` e de `k` certos, que é onde uma transcrição erra. -/
theorem tiltFactor_prem : tiltFactor 0.6032 0.2980 = 0.6948 := by
  unfold tiltFactor
  norm_num

/-- **EN:** Arithmetic check: the same PREM `h₂`, `k₂` give the published degree-2 gravimetric factor
`δ₂ = 1.1562`.

✅ **O irmão para o fator gravimétrico, da MESMA passagem:** *«For the PREM model,
δ2 = 1.1562»* (`@agnew2015mares`, l. 759), e `1 + 0,6032 − (3/2)·0,2980 = 1,1562`.

⚠️ `gravimetricFactor_degree_two` só fixava a FORMA de grau `2`; este fixa o VALOR. Com `tiltFactor_prem`,
o par `(h₂, k₂)` fica preso a duas combinações independentes publicadas pela mesma fonte
para o mesmo modelo — um erro de sinal em `k` passaria num e não no outro. -/
theorem gravimetricFactor_prem : gravimetricFactor 2 0.6032 0.2980 = 1.1562 := by
  unfold gravimetricFactor
  norm_num

end Mapgravy
