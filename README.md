# Provas verificadas por máquina de cinco relações da geodesia física

> **Se chegou aqui por um artigo:** este diretório contém a formalização completa das
> cinco relações que o artigo declara verificadas. Ele é autocontido — as únicas
> dependências são o Lean 4 e a biblioteca `mathlib`, ambos fixados por versão nos
> ficheiros `lean-toolchain` e `lake-manifest.json`. Nenhum dado observacional é usado.
>
> **Para reproduzir**, veja *Como reproduzir* abaixo. **Para verificar**, não basta a
> compilação: veja *O que «provado» quer dizer aqui*, que é a secção que interessa.
>
> Licença GPL-3.0 (ficheiro `LICENSE`). Como citar: ficheiro `CITATION.cff`.

---

## O que está aqui


Lean 4 + mathlib4. **Só os teoremas ESTRUTURAIS do projeto entram aqui** — as linhas
empíricas do painel são medição, e Lean não tem o que dizer sobre elas. Um número de Monte
Carlo, um desvio contra o benchmark do Colorado, um `δ` ajustado: nada disso pertence a
este diretório.

| ficheiro | teorema | o que estava em prosa antes |
|---|---|---|
| `Helmert.lean` | `separacao_e_identidade` — `H* − H = Δg_B·H/γ̄` é **identidade**, não duas rotas independentes | `CLAUDE.md` §0.1 e o docstring de `conventions.py::geopotential_to_helmert_height`, onde a concordância entre as duas rotas foi lida como confirmação independente (§0.3c #1) |
| `Gauss.lean` | `potencial_iguala_a_massa_encerrada` — `y₅ = M` no interior, logo `k′₀ = 0` para qualquer solução elástica | o docstring da nossa Green chamava a `k′₀ = 0` *«uma DECLARAÇÃO, não uma medida»*, e estava errado nos dois pontos. ⚠️ A prova NÃO passa pelo teorema da divergência — medido: no mathlib ele existe só sobre **caixas**, e a biblioteca de harmónicas tem `437` linhas sem valor médio nem potencial newtoniano |
| `BemPostura.lean` | `hormander_implica_lions_sznitman` — a condição de unicidade de `@hormander1976` implica a de bem-postura de Lions–Sznitman, e a recíproca é **falsa** (com contraexemplo) | as duas condições coexistiam no `CLAUDE.md` §1 sem que a relação estivesse escrita; media-se que **ambas valem** no domínio do GSVS17, o que não é o mesmo que uma implicar a outra |
| `Boussinesq.lean` | `razao_nao_depende_de_g_nem_de_mu` — a razão `(n·l')∞/h'∞` depende **só de `ν`**; `g` e `μ` cancelam | é o que transforma a forma fechada num **oráculo**: `@farrell1972carga` não tabula `μ`, mas publica `v_p`/`v_s` na Fig. 2, de que sai `ν`. O painel registou durante uma frente inteira que `l'` **não tinha oráculo** — a ausência era de TABELA |
| `FatoresDeMare.lean` | `dicotomia_do_limite_rigido` — `δₙ` e `γ` valem **exatamente `1`** no limite rígido, para todo grau. ↩️ A metade do deslocamento saiu daqui: era um `(0:ℝ) = 0` sem conteúdo, e é hoje `Boussinesq.deslocamento_desaparece_no_limite_rigido`, um limite a sério no regime assintótico | a **regra emergente** de `docs/frentes_de_desenvolvimento.md`, apoiada em quatro casos observados: *uma grandeza cujo limite rígido não anula a série pode dispensar números de Love; uma que o anularia tem de os aplicar* |

`Formal/Axiomas.lean` não é prova: é o portão. Ver abaixo.

## Como reproduzir

```
cd formal
lake exe cache get     # baixa os .olean do mathlib (sem isto, horas de build)
lake build             # ~6 s com a cache quente
```

A versão está **fixada** por `lean-toolchain` (v4.33.1) e `lake-manifest.json` (o *rev*
exato do mathlib). Sem os dois, a prova não reproduz — e por isso os dois são versionados
enquanto `.lake/` (gigabytes) é ignorado.

⚠️ **A cache do mathlib é partilhada entre projetos na mesma máquina.** Aqui ela já estava
em disco (do projeto irmão `mapscint`) e o `lake update` levou `14 s` em vez de horas.
Num clone novo, conte com o download.

## O que "provado" quer dizer aqui

**`lake build` verde NÃO basta**, e é a distinção mais importante deste ficheiro: uma prova
com `sorry` **compila**. O portão é `#print axioms`, e o aceitável são só os três padrão do
Lean — `propext`, `Classical.choice`, `Quot.sound`. Qualquer `sorryAx` reprova.

O `Formal/Axiomas.lean` imprime a lista de cada teorema **no próprio build**, e
o conjunto de testes do projeto verifica-a. São **dez** portões hoje; os seis que seguem são os que valem para quem lê de fora:

| portão | o que trava | custo |
|---|---|---|
| `nenhuma_prova_esta_por_fechar` | `sorry` no código | textual |
| `as_versoes_do_lean_e_do_mathlib_estao_FIXADAS_e_versionadas` | prova irreproduzível | textual |
| `todo_teorema_provado_esta_na_lista_do_portao_de_axiomas` | **teorema que ninguém verifica** | textual |
| `o_README_do_formal_lista_cada_ficheiro_de_prova` | este README a envelhecer | textual |
| `as_provas_compilam` | apodrecimento por subida de mathlib | `~6 s`, `slow` |
| `nenhum_teorema_usa_axioma_fora_dos_TRES_padrao` | **`sorry` que compila** | `~6 s`, `slow` |

⚠️ O terceiro é o portão que impede o portão de mentir: o `Axiomas.lean` só verifica os
teoremas que **nomeia**, e um teorema fora daquela lista passaria por verificado.

⚠️ **Sem toolchain Lean na máquina os dois portões lentos dão `skip`.** Num clone assim
eles não protegem nada, e o verde deles não deve ser lido como garantia.

## ⚠️ O que NÃO está provado

**A tradução da física para as hipóteses.** No `Helmert.lean`, que a gravidade média de
Helmert seja `g + kH` com `k = (FA − 2B)/2` é a redução de Poincaré–Prey, e continua
argumento em prosa (`conventions.py`, e `@zilkoski1992navd88` para a forma do NAVD 88). O
que está provado é que, **dadas** as definições, a álgebra fecha e as duas rotas são a
mesma.

⚠️ **E há uma folga de hipótese que a formalização tornou explícita**, o que é o melhor
que ela fez até agora: o teorema avalia `γ̄` ao longo da **mesma** linha de prumo que a de
Helmert, enquanto a cadeia a avalia ao longo do prumo de `H*`. A diferença entre as duas
avaliações **é** o resíduo de segunda ordem de `0,07 cm` de rms nos `222` marcos do
GSVS17. ⇒ a identidade é exata sob a hipótese escrita, e o que a comparação numérica mede
é a folga dessa hipótese — não confirmação independente de nada.

## Convenções

Cabeçalho de copyright em cada ficheiro, `set_option linter.style.header false` (o linter
do mathlib exige a licença DELE, que é Apache 2.0; este repositório é GPL-3.0 — trocar o
cabeçalho para calar o aviso declararia licença falsa), e `namespace Mapgravy`.

Os docstrings carregam a **ciência**, não só a matemática: por que o teorema importa, o que
ele desmente, e onde a tradução para a física continua em prosa.
