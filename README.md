# Machine-checked proofs of five relations in physical geodesy

> **If a paper sent you here:** this directory holds the complete formalisation of the
> five relations the paper declares machine-verified. It is self-contained — the only
> dependencies are Lean 4 and the `mathlib` library, both pinned by version in
> `lean-toolchain` and `lake-manifest.json`. No observational data is used.
>
> **To reproduce**, see *How to reproduce* below. **To verify**, compiling is not enough:
> see *What "proved" means here*, which is the section that matters.
>
> Licence GPL-3.0 (file `LICENSE`). How to cite: file `CITATION.cff`.

---

## What is here

Lean 4 + mathlib4. **Only the project's STRUCTURAL theorems live here** — the empirical
results are measurements, and Lean has nothing to say about them. A Monte Carlo number, a
deviation against the Colorado benchmark, a fitted `δ`: none of that belongs in this
directory.

| file | theorem | what used to be prose |
|---|---|---|
| `Helmert.lean` | `separation_is_identity` — `H* − H = Δg_B·H/γ̄` is an **identity**, not two independent routes | an earlier version of our own code, where the agreement between the two routes was read as independent confirmation. It was not: the two are the same expression, and all the comparison measures is the second-order residual between two implementations |
| `Gauss.lean` | `potential_equals_enclosed_mass` — `y₅ = M` in the interior, hence `k′₀ = 0` for any elastic solution | the docstring of our own Green's function called `k′₀ = 0` *"a DECLARATION, not a measurement"*, and was wrong on both counts. ⚠️ The proof does NOT go through the divergence theorem — measured: in today's mathlib it exists only over **boxes**, and the harmonic-function library has `437` lines with no mean-value property and no Newtonian potential |
| `BemPostura.lean` | `hormander_implies_lions_sznitman` — Hörmander's (1976) uniqueness condition implies the Lions–Sznitman well-posedness condition, and the converse is **false** (with a counterexample) | the two conditions coexisted in our notes without the relation being written down; we had measured that **both hold** in the GSVS17 domain, which is not the same as one implying the other |
| `Boussinesq.lean` | `ratio_independent_of_g_and_mu` — the ratio `(n·l')∞/h'∞` depends **only on `ν`**; `g` and `μ` cancel | it is what turns the closed form into an **oracle**: Farrell (1972) does not tabulate `μ`, but publishes `v_p`/`v_s` in his Fig. 2, from which `ν` follows. For a whole work front our notes recorded that `l'` **had no oracle** — what was missing was a TABLE |
| `FatoresDeMare.lean` | `rigid_limit_dichotomy` — `δₙ` and `γ` equal **exactly `1`** in the rigid limit, for every degree. ↩️ The displacement half was moved out: it was a contentless `(0:ℝ) = 0`, and is today `displacement_vanishes_in_rigid_limit` in `Boussinesq.lean`, a real limit in the asymptotic regime | the **emergent rule** in our development notes, supported by four observed cases: *a quantity whose rigid limit does not annihilate the series may dispense with Love numbers; one that it would annihilate has to apply them* |

`Formal/Axiomas.lean` is not a proof: it is the gate. See below.

## How to reproduce

```
cd formal
lake exe cache get     # downloads the mathlib .olean files (without this: hours of build)
lake build             # ~6 s with a warm cache
```

The version is **pinned** by `lean-toolchain` (v4.33.1) and `lake-manifest.json` (the
exact mathlib *rev*). Without both, the proof does not reproduce — which is why both are
versioned while `.lake/` (gigabytes) is ignored.

⚠️ **The mathlib cache is shared between projects on the same machine.** Here it was
already on disk (from another project), and `lake update` took `14 s` instead of hours. On
a fresh clone, expect the download.

## What "proved" means here

**A green `lake build` is NOT enough**, and this is the most important distinction in this
file: a proof containing `sorry` **compiles**. The gate is `#print axioms`, and the only
acceptable output is Lean's three standard axioms — `propext`, `Classical.choice`,
`Quot.sound`. Any `sorryAx` fails.

`Formal/Axiomas.lean` prints the axiom list of every theorem **in the build itself**, and
the project's test suite checks it. There are **ten** gates today; the six below are the
ones that matter to an outside reader:

| gate | what it blocks | cost |
|---|---|---|
| `nenhuma_prova_esta_por_fechar` | a `sorry` in the code | textual |
| `as_versoes_do_lean_e_do_mathlib_estao_FIXADAS_e_versionadas` | an irreproducible proof | textual |
| `todo_teorema_provado_esta_na_lista_do_portao_de_axiomas` | **a theorem nobody verifies** | textual |
| `o_README_do_formal_lista_cada_ficheiro_de_prova` | this README going stale | textual |
| `as_provas_compilam` | rot from a mathlib upgrade | `~6 s`, `slow` |
| `nenhum_teorema_usa_axioma_fora_dos_TRES_padrao` | **a `sorry` that compiles** | `~6 s`, `slow` |

⚠️ The third is the gate that keeps the gate from lying: `Axiomas.lean` only checks the
theorems it **names**, and a theorem outside that list would pass for verified.

⚠️ **Without a Lean toolchain on the machine, the two slow gates report `skip`.** On such a
clone they protect nothing, and their green must not be read as a guarantee.

## ⚠️ What is NOT proved

**The translation from physics into the hypotheses.** In `Helmert.lean`, that Helmert's
mean gravity is `g + kH` with `k = (FA − 2B)/2` is the Poincaré–Prey reduction, and it
remains a prose argument (in our code's documentation, and in Zilkoski et al. (1992) for
the NAVD 88 form). What is proved is that, **given** the definitions, the algebra closes
and the two routes are the same.

⚠️ **And there is a gap in the hypotheses that the formalisation made explicit**, which is
the best thing it has done so far: the theorem evaluates `γ̄` along the **same** plumb line
as Helmert's, whereas our processing chain evaluates it along the plumb line of `H*`. The
difference between the two evaluations **is** the second-order residual of `0.07 cm` rms
over the `222` GSVS17 benchmarks. ⇒ the identity is exact under the hypothesis as written,
and what the numerical comparison measures is the slack in that hypothesis — not
independent confirmation of anything.

## Conventions

A copyright header in every file, `set_option linter.style.header false` (mathlib's linter
demands ITS licence, which is Apache 2.0; this repository is GPL-3.0 — swapping the header
to silence the warning would declare a false licence), and `namespace Mapgravy`.

Every theorem docstring opens with a one-line **`EN:`** summary of what it establishes;
the rest is in Portuguese and carries the **science**, not just the mathematics: why the
theorem matters, what it refutes, and where the translation into physics remains prose.
