# Referee Report — *Surrogate-Mediated Cross-Catalog Validation of Numerical Relativity Binary Black Hole Waveforms*

**Manuscript:** `project/paper.tex` (671 lines, as of 2026-08-14)
**Recommendation:** **Major revision required — do not publish in present form.**

---

## 0. Scope and method of this review

I read the manuscript, then independently re-derived every quantitative claim from the
result files the manuscript itself cites in its `% Results on disk:` comments
(`project/results/*.csv`, `project/results_seobnrv4phm/*.csv`, `project/figs/*.png`),
and inspected the pipeline source (`nrcatalogtools/waveform/matching.py`,
`nrcatalogtools/waveform/modes.py`).

Throughout I distinguish:

- **[VERIFIED]** — checked directly against the on-disk data/figures/code.
- **[INFERENCE]** — my reading of what the evidence implies; the authors may have a rebuttal.
- **[UNRESOLVED]** — I could not determine this from the material available.

The underlying idea — using a surrogate as a common evaluation point to sidestep
parameter-space mismatch between catalogs — is sound, useful, and worth publishing. The
problem is not the idea. The problem is that **the numbers in the manuscript do not match
the numbers in the analysis outputs it cites**, and several headline conclusions are
contradicted by the authors' own data. Those are fixable, but they must be fixed before
this can be assessed as science.

---

## 1. Executive summary of the most serious problems

| # | Issue | Severity |
|---|---|---|
| M1 | Tables III and V, and the associated text statistics, are **not reproducible** from the cited CSVs — several entries differ by factors of 2–3 | Blocking |
| M2 | The physical explanation offered for the "anomalous" pilot modes explains numbers that **no longer exist** in the data | Blocking |
| M3 | The analysis sample contains **8 BNS and 1 BHNS simulations**, all mislabelled as NRSur7dq4 training data | Blocking |
| M4 | The SEOBNRv4PHM "controlled comparison" contains **no RIT, no MAYA, and no spinning simulations**, yet is used to overturn Section IV's interpretation | Blocking |
| M5 | "Out-of-sample extrapolation beyond the training domain" is claimed repeatedly, but **no simulation in the study has q > 4** | Blocking |
| M6 | In-sample (training-set) simulations reach match 0.38 — the validation claim is contradicted by its own dataset | Major |
| M7 | The eccentricity "power law" is not present in the data; cross-catalog eccentricities are not commensurable | Major |
| M8 | "Amplitude discrepancy" reasoning is invalid: the match is normalized | Major |
| M9 | Introduction claims BMS + SO(3) optimization was performed; Section VI says it is future work | Major |
| M10 | No NR resolution / extraction-order control; mixed RIT resolutions silently pooled | Major |

---

## 2. Reproducibility of the reported numbers

### M1. Table V and the batch statistics do not match the cited results file **[VERIFIED]**

`paper.tex:451–467` cites `project/results/batch_aligned_{sxs,rit,maya}.csv`. Recomputing
median / 10th-percentile over categories (b,d) from `results/batch_aligned_all.csv` — using
exactly the sample sizes the manuscript quotes (SXS N=579, RIT N=229, MAYA N=49, which
**do** reproduce) — gives:

| Mode | SXS paper | SXS on disk | MAYA paper | MAYA on disk | RIT paper | RIT on disk |
|---|---|---|---|---|---|---|
| (2,2) | 0.9923 / 0.9496 | **0.9990 / 0.9735** | 0.9728 / 0.8439 | **0.9958 / 0.9603** | 0.9231 / 0.4941 | 0.9339 / 0.4982 |
| (2,1) | 0.8541 / 0.3739 | **0.9971 / 0.5314** | 0.9843 / 0.3775 | **0.9895 / 0.3562** | 0.9676 / 0.7152 | 0.9685 / 0.7215 |
| (3,3) | 0.9865 / 0.2926 | **0.9937 / 0.4329** | 0.9707 / 0.3120 | **0.9856 / 0.2851** | 0.7710 / 0.3241 | 0.7817 / 0.3241 |
| (4,4) | 0.9819 / 0.8768 | **0.9934 / 0.9048** | 0.9709 / 0.4383 | **0.9800 / 0.4727** | 0.7829 / 0.3895 | 0.7851 / 0.3925 |
| (3,2) | 0.8580 / 0.4615 | **0.9960 / 0.8852** | 0.9794 / 0.7781 | **0.9873 / 0.8583** | 0.9700 / 0.6452 | 0.9707 / 0.6496 |
| (4,3) | 0.6711 / 0.2989 | **0.9816 / 0.4466** | 0.9765 / 0.4615 | **0.9783 / 0.4545** | 0.8248 / 0.5763 | 0.8251 / 0.5766 |

The RIT column reproduces to ~1%. **The SXS and MAYA columns do not.** The SXS (4,3) median
differs by 0.31 in match; the SXS (3,2) median by 0.14. The text in `paper.tex:479, 502, 506`
repeats the stale SXS/MAYA numbers verbatim.

**[INFERENCE]** The table appears to have been assembled from a mixture of analysis
generations — the RIT rows from the current run, the SXS/MAYA rows from an earlier one.
Every statistic in Section IV.B must be regenerated from a single, versioned analysis run,
and the run's provenance (commit hash, date) stated in the paper.

### M2. Table III and the pilot "anomaly" narrative **[VERIFIED]**

`paper.tex:372–389` cites `results/SXS_BBH_0162_mode_matches.csv`. Compare:

| Mode | Paper (Table III) | `SXS_BBH_0162_mode_matches.csv` |
|---|---|---|
| (2,2) | 0.9931 | 0.99737 |
| (2,1) | **0.350 ‡** | **0.99642** |
| (3,3) | 0.9844 | 0.98900 |
| (4,4) | 0.9778 | 0.98642 |
| (3,2) | **0.569 ‡** | **0.99309** |
| (4,3) | **0.406 ‡** | **0.98507** |

All three "anomalous" values are gone in the current data; every mode is ≥ 0.985.

This matters far beyond a table correction. `paper.tex:419` builds a three-sentence physical
mechanism on those numbers:

> "The (3,2) mode exhibits a near-cancellation between mass-ratio and spin-orbit sourced
> terms at certain spin configurations. Small errors in the surrogate's relative weighting
> of these contributions can produce large fractional amplitude errors, especially near a
> local minimum in the interpolation."

**[INFERENCE]** This is a physical explanation constructed to rationalise what the authors'
own subsequent analysis indicates were pipeline artifacts. A referee cannot distinguish
"we discovered a physical effect" from "we explained a bug" unless the analysis is
regenerated. Delete the mechanism, or re-derive it from data that actually shows the effect.

Note that Table IV (phases) *does* reproduce against the same CSV (e.g. 0162 (2,2):
0.005 / 47 cyc vs 0.004984 / 46.86 on disk). So Tables III and IV in the same manuscript
come from different analysis generations — an internal inconsistency.

Separately, `paper.tex:415` states: *"The reported matches of these modes for SXS:BBH:0001
(0.28–0.35) merely reflect numerical noise."* Table III shows dashes for those modes, and
the CSV gives 0.533, 0.433, 0.447. The quoted range 0.28–0.35 appears in **neither** the
table nor the data.

---

## 3. Sample construction and data hygiene

### M3. Neutron-star binaries in a BBH catalog comparison **[VERIFIED]**

`results/batch_aligned_all.csv` contains:

```
SXS:NSNS:0003  b  calibration=True     SXS:NSNS:0008  b  calibration=True
SXS:NSNS:0004  b  calibration=True     SXS:NSNS:0009  b  calibration=True
SXS:NSNS:0005  b  calibration=True     SXS:NSNS:0010  b  calibration=True
SXS:NSNS:0006  b  calibration=True     SXS:BHNS:0002  b  calibration=True  match_22 = 0.881
SXS:NSNS:0007  b  calibration=True
```

Eight binary-neutron-star and one black-hole–neutron-star simulation sit in category (b),
the non-spinning quasi-circular subset that feeds Table V and the in-sample/out-of-sample
split. All nine are flagged as **NRSur7dq4 training simulations**, which is impossible —
NRSur7dq4 is trained on vacuum BBH only. Eight yield NaN and drop out silently; `SXS:BHNS:0002`
survives with match 0.881 and is counted as an in-sample calibration point.

This is direct proof that the calibration flag in
`catalog_organization/sxs_classification.json` is contaminated, which undermines the
in-sample/out-of-sample partition that Section IV.B.1 and the Conclusions present as a
headline result.

### Training-set size: 1528 vs 1731 **[VERIFIED]**

- `paper.tex:163` and `paper.tex:311`: NRSur7dq4 is *"trained on 1528 SpEC simulations"*.
- `paper.tex:305` and Table I: *"1,731 of its simulations were used as training data"*.
- `results/nrsur7dq4_training_simulations.txt` header: *"total count: 1731"*.

The manuscript states two different training-set sizes 150 lines apart, and the larger,
unexplained one is what actually defines "in-sample" in the analysis. 203 simulations are
being treated as training data that the cited NRSur7dq4 reference does not list as such.
The provenance of this list must be documented.

### Unphysical metadata propagated into the statistics **[VERIFIED]**

| Symptom | Count | Example |
|---|---|---|
| `f_lower_nr` < 5 Hz or > 200 Hz | 55 rows | `SXS:BBH:3995`: 7.3×10⁻⁹ Hz; `GT0389`: 554 Hz |
| `f_lower_nr` exactly 12.5032 Hz | 268 RIT rows | identical value across unrelated simulations |
| `f_lower_nr` exactly 37.5095 Hz | 192 RIT rows | idem |
| `f_lower_nr` = 0 | 14 rows | — |
| `n_cycles_22` < 10 | 236 RIT, 25 SXS, 5 MAYA | `RIT:eBBH:1350`: 0.50 cycles |
| `n_cycles_22` ≈ 1 | several | `SXS:BBH:4292`: 1.001 cyc, match 0.341 |

**[INFERENCE]** The repeated 12.5032/37.5095 Hz values are a metadata fallback, not
per-simulation physics. 460 of 686 RIT rows (67%) carry one of these two defaults. A
"phase difference per cycle" computed with a denominator of 0.5 cycles is meaningless, and
these rows are inside the reported distributions and CDFs. The batch needs a validity filter
(minimum cycle count, physical `f_lower` range, non-NaN modes) with the rejection count
reported.

### Mixed RIT resolutions pooled without comment **[VERIFIED]**

RIT simulation IDs carry a resolution tag. In the quasi-circular subset: `n100` × 94,
`n120` × 93, `n140` × 38, plus `n144`, `n200`, `n130`. The manuscript never states which
resolution was used or that resolutions are mixed. Since `n100` is the coarsest RIT grid,
part of the "RIT low-match population" may simply be resolution, not code systematics.
This is testable by the authors and should be tested.

### Sample-definition inconsistency **[VERIFIED]**

`paper.tex:438` says the batch is *"all simulations in categories (a)–(d) ... that fall
within the NRSur7dq4 prior volume"*, giving 774 SXS / 686 RIT / 188 MAYA. Table I defines
the prior volume as *"q ≤ 4, |χ| ≤ 0.8, and e = 0"*, under which categories (a) and (c) are
**zero by construction** and the in-prior a–d totals would be 587 / 234 / 51. In fact 195
of the 774 SXS rows, 457 of 686 RIT rows, and 139 of 188 MAYA rows are eccentric.

So "1,648 simulations within the surrogate's prior volume" is not what was analysed:
**two-thirds of the RIT sample and three-quarters of the MAYA sample lie outside the
surrogate's stated domain by construction.** Abstract and Section IV.B must say this
plainly, because it changes how every catalog-level statistic is read.

Also unexplained: Table V's N (579/229/49) is smaller than the in-prior b+d counts in
Table I (587/234/51). The attrition is never mentioned.

---

## 4. Claims contradicted by the authors' own data

### M4 + M5. The SEOBNRv4PHM section cannot support its conclusion **[VERIFIED]**

`results_seobnrv4phm/batch_aligned_all.csv` contains **250 rows**, and:

- **all 250 are SXS.** Zero RIT. Zero MAYA.
- **only categories (a) and (b)** — non-spinning eccentric (175) and non-spinning
  quasi-circular (75). Zero aligned-spin simulations.
- modes **(3,2) and (4,3) are 100% NaN** — only four modes were computed.
- in the quasi-circular subset there are **5 simulations with q > 3.5**.

Against this, the manuscript states:

| Claim | Location | Status |
|---|---|---|
| "Our evaluation using SEOBNRv4PHM across the quasi-circular **and aligned-spin** parameter space" | `paper.tex:624` | **False** — no spinning simulations in the run |
| "the hotspot ... **universally present across catalogs** ... completely vanishes" | `paper.tex:643` | **Untestable** — RIT and MAYA absent |
| "demonstrating that the **underlying NR codes** agree well beyond the surrogate's ... domain" | Fig. 9 caption | **Unsupported** — one code (SpEC) is plotted; Fig. 9's legend reads "SXS" only |
| "**definitively proves** that the inter-catalog mismatches ... are overwhelmingly dominated by out-of-sample extrapolation errors" | `paper.tex:647` | **Not supported** at any evidential level |

Two further problems:

1. **The control does not cover the region it claims to overturn.** The Fig. 7 hotspots are
   located at χ_eff ∈ (0.25, 0.5] and (−0.5, −0.25] (`paper.tex:544`). The SEOBNRv4PHM run
   contains **only χ = 0** simulations. The controlled comparison is blind to the hotspot's
   own parameter region.

2. **A blunter instrument shows less structure.** On the *identical* SXS simulations, the
   quasi-circular median (2,2) mismatch is 7.3×10⁻³ against SEOBNRv4PHM versus 5.2×10⁻⁴
   against NRSur7dq4 — a factor of 14 higher noise floor. Structure at the 10⁻³ level is
   invisible under a 10⁻² floor. The disappearance of a feature when you switch to a less
   accurate reference is expected regardless of the feature's origin, and therefore
   distinguishes nothing.

**M5, the q > 4 issue (the point you raised).** This is worse than a figure-range mismatch:
`max(q) = 4.0000` across **all three catalogs in both datasets** — the entire study lives
inside the surrogate's training domain in mass ratio. Yet the manuscript refers to
"out-of-sample extrapolation" or "beyond the training domain" at `paper.tex:473` (Fig. 4
caption), `paper.tex:498` (Fig. 6 caption), `paper.tex:631` (Fig. 9 caption), and
`paper.tex:647`. Fig. 9 has no data above q = 4, and Fig. 3's q-axis terminates at 4.

Degradation *at* q ≈ 4 is boundary **interpolation** error (sparse training grid near a
domain edge), not extrapolation. Either restrict the language accordingly, or extend the
sample above q = 4 — where NRSur7dq4 genuinely extrapolates and the question becomes real.

Finally, `paper.tex:616` and Fig. 9's caption call SEOBNRv4PHM a *"time-domain
phenomenological model"*. It is an **effective-one-body** model. The distinction is
load-bearing here: the paper's whole argument is about what an independent modelling
approach implies, and EOB vs. IMRPhenom is exactly that distinction.

### M6. In-sample simulations fail, which contradicts the validation claim **[VERIFIED]**

Within the SXS quasi-circular calibration (training) subset:

```
SXS:BBH:0276   q=3.00  χ2z=-0.30  e=0      match_22 = 0.380   Δφ/cyc = 0.008
SXS:BBH:0223   q=1.00  χ1z=+0.30  e=0      match_22 = 0.447   Δφ/cyc = 0.215
SXS:BBH:1145   q=1.25  χ=0        e=0      match_22 = 0.518   Δφ/cyc = 0.003
SXS:BHNS:0002  (not a BBH)                 match_22 = 0.881
SXS:BBH:0200   q=3.27  χ≈0        e=4e-4   match_22 = 0.924
```

Minimum in-sample match = 0.380; only 97.9% exceed 0.985.

Against this the Conclusions (`paper.tex:603`) assert *"the 342 calibration simulations
exhibit a near-uniform (2,2) match above 0.985"*, and Fig. 6's caption asserts
*"near-perfect agreement (mismatch ∼ 10⁻³) for the calibration set validates the surrogate's
interpolation fidelity"*. Fig. 6(b)'s own CDF shows a calibration tail extending to
mismatch ≈ 0.6.

**[INFERENCE]** A surrogate reproduces its training data to ≈10⁻³ by construction. A match
of 0.38 with a phase error of 0.008 rad/cycle — i.e. the phasing is *excellent* while the
match collapses — is not a surrogate failure mode. It is the signature of a pipeline
failure (epoch/time-alignment, band selection, or padding). `SXS:BBH:1145` has
`f_lower_nr = 51.8 Hz` against `f_lower_sur = 26.2 Hz`, which is itself anomalous for a
q = 1.25 SXS run.

**This is the single most valuable diagnostic in the dataset**, and I would urge the authors
to use it rather than bury it: the in-sample subset is a calibrated null test with a known
answer. Every in-sample point that fails is a pipeline bug, by definition. Fix those, and
the credibility of the entire out-of-sample tail — including the RIT population — can be
assessed for the first time.

### The calibration count is wrong in three places **[VERIFIED]**

- `paper.tex:504`: "trained on **342** of the 579 SXS quasi-circular simulations"
- `paper.tex:603`: "the **342** calibration simulations ... the **242** out-of-sample simulations" — but 579 − 342 = **237**, not 242
- `results/batch_aligned_all.csv`: 337 flagged True, 242 False (337 + 242 = 579 ✓)
- `figs/fig5_sxs_cal_mismatch_cdf.png` legend: "SXS (NRSur cal.) (**N=329**)", "(non-cal.) (N=242)"

Four numbers (342, 337, 329, 237) for one quantity. The 329 is the non-NaN subset of 337;
242 is correct; 342 appears to come from Table I (60 + 282) and is inconsistent with the
CSV the analysis actually used.

### M7. The eccentricity results do not show what is claimed **[VERIFIED]**

Median (2,2) mismatch vs. eccentricity, categories (a)–(d):

| e bin | SXS | RIT | MAYA |
|---|---|---|---|
| (0, 10⁻⁴] | 9.2×10⁻⁴ | — | — |
| (10⁻⁴, 10⁻³] | 9.8×10⁻⁴ | **2.5×10⁻¹** | 2.3×10⁻³ |
| (10⁻³, 5×10⁻³] | 5.8×10⁻⁴ | **4.0×10⁻²** | 4.5×10⁻³ |
| (5×10⁻³, 10⁻²] | 7.2×10⁻⁴ | 1.5×10⁻³ | 4.6×10⁻³ |
| (10⁻², 2×10⁻²] | 2.1×10⁻³ | 2.6×10⁻³ | 2.4×10⁻³ |
| (2×10⁻², 5×10⁻²] | 1.7×10⁻³ | 9.0×10⁻³ | 4.7×10⁻³ |
| (5×10⁻², 10⁻¹] | 9.7×10⁻³ | 4.3×10⁻² | 1.8×10⁻² |
| (10⁻¹, 0.3] | 8.7×10⁻² | 1.5×10⁻¹ | 6.0×10⁻² |
| (0.3, 1.0] | 4.5×10⁻¹ | 4.0×10⁻¹ | 3.1×10⁻¹ |

Against this:

1. **"From e = 0.005 to 0.05, the (2,2) mismatch grows by over two orders of magnitude"**
   (`paper.tex:539`). For SXS it grows from 7.2×10⁻⁴ to 1.7×10⁻³ — a factor of **2.4**.
   The onset visible in Fig. 8(a) is at e ≈ 0.02–0.03, not 0.005. The plateau extends
   roughly three decades in e before anything happens.

2. **"Similar limits are recovered for the RIT and MAYA catalogs (< 10⁻² for e < 10⁻³)"**
   (`paper.tex:537`). RIT's median mismatch in that bin is **0.248** — 25 times the stated
   bound, and the *worst* bin in the entire RIT column. RIT's mismatch is
   **anti-correlated** with eccentricity over the low-e range. This is visible by eye in
   Fig. 8(a): the red cluster near e ≈ 10⁻³ sits at mismatch 0.1–1.0, above eccentric SXS
   points at e ≈ 0.1.

3. **"a deterministic power law"** (Fig. 8 caption, `paper.tex:533`, `paper.tex:539`,
   abstract). No exponent, no fit, no uncertainty is reported anywhere. If a power law is
   claimed, fit it per mode and per catalog and give exponents with errors; the prediction
   that higher harmonics scale as m is quantitative and directly testable. As it stands,
   "deterministic power law" is not a result.

4. **Cross-catalog eccentricities are not commensurable.** [INFERENCE, but strongly
   supported] Fig. 3's eccentricity column shows the three catalogs occupying disjoint
   bands: SXS quasi-circular at e ∈ [10⁻⁵, 10⁻³], RIT at e ∈ [7×10⁻⁴, 3×10⁻³], MAYA at
   e ∈ [10⁻³, 10⁻²]. That is a signature of three different *definitions and reporting
   conventions* for a reference eccentricity (SXS fits orbital-frequency oscillations at
   relaxation; RIT and MAYA use different estimators at different epochs, and some SXS
   metadata values are upper bounds rather than measurements). The paper treats the
   horizontal axis as a physical variable and reads catalog differences off it. Either
   recompute a common eccentricity estimator on the waveforms (e.g. `gw_eccentricity`) or
   state explicitly that the axis is catalog-defined and refrain from cross-catalog
   inference along it.

### M-fig. Fig. 7's "hotspots" are single-outlier bin means **[VERIFIED]**

`paper.tex:544` quotes bin-mean mismatches. Recomputing on the (q, χ_eff) grid:

| Catalog | Bin | N | **mean** | **median** |
|---|---|---|---|---|
| SXS | q ∈ (3.5,4.0], χ_eff ∈ (0.25,0.5] | 8 | 0.146 | **0.0017** |
| SXS | q ∈ (1.5,2.0], χ_eff ∈ (−0.25,0] | 33 | 0.142 | **0.0010** |
| RIT | q ∈ (3.0,3.5], χ_eff ∈ (0.5,0.75] | **1** | 0.564 | 0.564 |
| RIT | q ∈ (3.5,4.0], χ_eff ∈ (0.25,0.5] | **2** | 0.431 | 0.431 |
| RIT | q ∈ (2.0,2.5], χ_eff ∈ (0,0.25] | 6 | 0.521 | 0.487 |

The paper's ≈0.14 for SXS reproduces — as a **mean over 8 points whose median is 0.0017**.
The "pronounced hotspot" is one or two failing simulations, and the SXS median at q > 3.5
in the quasi-circular subset is 0.9987. Report medians (or means with N and dispersion);
do not describe an N = 1 bin as a hotspot.

Two presentational problems compound this: Fig. 7 is captioned "Parameter-space heatmaps"
but is a **scatter plot** — the binned means quoted in the text cannot be read off it at
all. And the q-axis is populated only at q ≈ 1, 1.25, 1.5, 2, 3, 4, so the binning is over
a sparse discrete grid.

Relatedly, `paper.tex:481` states the low-match RIT population is *"concentrated at high
|χ_eff| and q ∼ 4"*. The 12 worst RIT quasi-circular simulations span q = 1.82–4.00 with
|χ_eff| ≲ 0.24, and they arrive in spin-swapped pairs:

```
RIT:BBH:0191  q=2.414  χ1z=-0.500  χ2z=+0.650   match 0.345
RIT:BBH:0187  q=2.414  χ1z=+0.500  χ2z=-0.650   match 0.383
RIT:BBH:0133  q=2.194  χ1z=+0.350  χ2z=-0.530   match 0.383
RIT:BBH:0135  q=2.194  χ1z=-0.530  χ2z=+0.350   match 0.384
RIT:BBH:0517  q=4.000  χ1z=-0.400  χ2z=+0.250   match 0.408
RIT:BBH:0562  q=4.000  χ1z=+0.400  χ2z=-0.250   match 0.424
```

**[INFERENCE]** Failures that come in ± spin-exchange pairs, at large |χ1z − χ2z| and
modest χ_eff, are the classic signature of a **body-1/body-2 labelling convention mismatch**
between RIT's metadata and the m₁ ≥ m₂ convention NRSur7dq4 expects. This is cheap to test —
re-run the low-match RIT subset with χ1z and χ2z exchanged and see whether the matches jump.
If it is a convention bug, the RIT bimodality that Section IV.B interprets as code
systematics disappears. Until that test is done, I do not think any conclusion about RIT
can stand.

### M10. NR numerical error is never controlled **[VERIFIED absence]**

`paper.tex:171` claims that after the alignment optimization, *"Any residual discrepancy
remaining ... strictly reflects a combination of true numerical error in the NR simulation
and interpolation error within the surrogate itself, which we subsequently isolate and
quantify."*

Neither term is isolated or quantified anywhere in the manuscript. There is:

- no resolution study (SXS Lev-N, RIT n100/n120/n140, MAYA refinement levels are all available),
- no extrapolation-order study (SXS N = 2, 3, 4; the manuscript never states which was used),
- no comparison of polynomial extrapolation against CCE, despite Section II.A discussing both at length,
- no surrogate-internal error estimate, despite NRSur7dq4 providing one.

Without a resolution difference, a mismatch of 10⁻³ cannot be attributed to anything. The
minimum viable version of this control: for a subset of ~20 simulations per catalog,
compute the match between adjacent resolutions of the *same* simulation. That number is the
noise floor, and every claim in Section IV should be stated relative to it.

### M-mass. All conclusions are drawn at a single total mass **[VERIFIED]**

Everything uses M = 40 M⊙ (`paper.tex:340`). The authors already have the sensitivity study
on disk (`results/mass_scan_results.csv`, 13 masses × 4 pilot simulations), and it shows
the conclusions are strongly mass-dependent:

| M/M⊙ | (2,2) | (2,1) | (3,3) | (4,4) | (4,3) |
|---|---|---|---|---|---|
| 10 | 0.9835 | 0.9032 | 0.7392 | 0.8883 | 0.4449 |
| 40 | 0.9937 | **0.6508** | 0.9696 | 0.9832 | 0.6826 |
| 100 | 0.9961 | 0.6609 | 0.9863 | 0.9895 | 0.6953 |

The (2,1) median match *falls* from 0.90 to 0.63 as M goes from 10 to 40 M⊙; (4,3) moves by
0.25. The Appendix mentions the mass scan exists but no result is shown. Either present it
or state clearly that all quoted matches are M = 40 M⊙-specific and not to be read as
mass-independent statements about catalog agreement.

---

## 5. Metric definitions — two conceptual problems

### M8. "Amplitude discrepancy" is not a possible explanation for a low match **[VERIFIED against code]**

The match is normalized (`paper.tex:253`) and `compute_mode_match`
(`nrcatalogtools/waveform/matching.py:127`) calls `pycbc.filter.match`, which maximizes over
time and phase and divides by both norms. **A pure amplitude error — of any size — gives a
match of exactly 1.** Only a difference in the amplitude *profile*, i.e. in how amplitude is
distributed across the band, can reduce it.

The manuscript therefore reasons invalidly in at least four places:

- `paper.tex:413`: "residual mismatch is dominated by amplitude differences rather than phase drift"
- `paper.tex:419`: "the mismatch is driven by an amplitude discrepancy rather than phase deviation"
- `paper.tex:423`: "a slightly reduced match (0.993), indicating amplitude differences near merger"
- Fig. 5 caption: "rather than pure amplitude discrepancies"

The inference "Δφ/cycle is small, therefore the residual is amplitude" does not follow. It
should read: the residual is not *secular monotone* phase drift; it is some combination of
amplitude-profile difference and non-secular phase structure. Distinguishing those requires
plotting the time-domain amplitude ratio and phase residual after optimal alignment — the
per-simulation mode figures already exist in `figs/*_mode_matches.png`, so this is a
presentation gap, not a computation gap.

### The phase metric is far weaker than described **[VERIFIED against code]**

`compute_phase_diff_per_cycle` (`matching.py:205`) reduces to:

```python
delta_phi_nr  = abs(phi_nr[-1]  - phi_nr[0])
delta_phi_sur = abs(phi_sur[-1] - phi_sur[0])
phase_diff_per_cycle = abs(delta_phi_nr - delta_phi_sur) / n_cycles_nr
```

This is a **two-endpoint difference in total accumulated phase**. It is exactly zero for any
pair of waveforms whose phase histories differ arbitrarily in between but happen to
accumulate the same total. It cannot detect oscillatory phase error — which is precisely
the eccentric-modulation signature Section IV.C attributes to it — and the two `abs()` calls
mask a global sign/conjugation convention error.

`paper.tex:261` claims it "directly exposes these drifts". It exposes *net cycle-count
error* only. Either rename and re-scope it, or replace it with the standard diagnostic:
max/RMS of the phase residual Δφ(t) over the band after optimal (t_c, φ_c) alignment. The
`SXS:BBH:0276` case (match 0.380, Δφ/cycle 0.008) is a live demonstration that the two
metrics can be simultaneously reported and simultaneously uninformative about what went
wrong.

### Per-mode phase maximization destroys inter-mode coherence **[VERIFIED, not discussed in paper]**

Each mode's match is maximized over its own time and phase shift independently. A physical
z-rotation by ψ acts as e^{−imψ}, i.e. it is a *single* parameter shared across modes.
By maximizing per mode, the analysis grants each mode its own rotation, and is therefore
**blind to relative phase errors between modes** — which is the error that actually matters
for higher-mode parameter estimation. `paper.tex:307` notes the phase maximization "absorbs
the residual rotation about z", but does not note that it over-absorbs. This limitation
should be stated, and ideally a single-ψ joint match reported alongside.

Minor but related: `paper.tex:342` describes the pipeline as padding and PSD-weighting, but
omits that both series are **tapered** (`matching.py:178`, `tapermethod="startend"`). A
start-end taper removes real inspiral cycles and part of the ringdown; for the short RIT
waveforms (many with < 10 cycles) this is a material fraction of the signal. Document it.

---

## 6. Explicit contradictions within the manuscript

These are places where the manuscript contradicts *itself*, independent of the data.

| # | Statement A | Statement B |
|---|---|---|
| C1 | **Abstract**: "all catalogs demonstrate excellent baseline agreement, routinely achieving mismatches below 10⁻²" | **Table V**: RIT (2,2) median match 0.9231 → mismatch **7.7×10⁻²**; 10th percentile 0.494 → mismatch **0.51** |
| C2 | **Conclusions** `:601`: "(2,2) ... consistently achieving mismatches below 1% ... across all three catalogs" | Same Table V; and `:481` describes the RIT distribution as bimodal "extending below 0.5" |
| C3 | **Intro** `:171`: "we ... [implement] a comprehensive post facto optimization framework. We systematically remove these unphysical gauge degrees of freedom by maximizing ... over ... SO(3) rigid frame rotations, and BMS supertranslations" | **Section VI** `:592`: "**Future work will apply** Bondi-Metzner-Sachs (BMS) supertranslation corrections" |
| C4 | **Intro** `:171`: "Any residual discrepancy ... strictly reflects ... true numerical error ... and interpolation error within the surrogate itself, which we subsequently isolate and quantify" | Nowhere in the manuscript are these two isolated or quantified |
| C5 | **Section IV.C / Fig. 7 caption**: the q ≈ 4 hotspot indicates "the surrogate's interpolation limits", and RIT's low-q hotspots "point to code-specific systematic numerical differences" | **Section VII.A** `:647`: the mismatches are "overwhelmingly dominated by out-of-sample extrapolation errors of the NRSur7dq4 surrogate, rather than fundamental inconsistencies between the numerical relativity codes" |
| C6 | **Section IV.C** `:537`: for e < 0.005, SXS (2,2) mismatches are "below 10⁻³ to 10⁻⁴" | **Table V**, over the same quasi-circular set: SXS (2,2) median match 0.9923 → mismatch **7.7×10⁻³** |
| C7 | `:163`, `:311`: NRSur7dq4 "trained on 1528 SpEC simulations" | `:305`, Table I: "1,731 of its simulations were used as training data" |
| C8 | `:504`: "342 of the 579" are calibration simulations | `:603`: "the 242 out-of-sample simulations" (579 − 342 = 237); Fig. 6 legend: N = 329 / 242 |
| C9 | **Table III**: SXS:BBH:0001 (2,1), (3,3), (4,3) shown as "— †" (vanish by symmetry) | `:415`: "The reported matches of these modes for SXS:BBH:0001 (0.28–0.35)" — values that appear neither in the table nor in the CSV (which gives 0.533, 0.433, 0.447) |
| C10 | **Fig. 9 caption**: "demonstrating that the underlying NR codes agree well **beyond** the surrogate's strict training domain" | The figure's own axis stops at q = 4, its legend lists **one** catalog, and max(q) = 4.0000 in every dataset |
| C11 | `:624`: SEOBNRv4PHM evaluated "across the quasi-circular **and aligned-spin** parameter space" | `results_seobnrv4phm/`: categories (a) and (b) only — **zero** spinning simulations |
| C12 | **Fig. 6(b) caption**: panel separates SXS into "calibration (in-sample) versus independent testing (out-of-sample)" | The panel also plots RIT and MAYA curves, which belong to neither subset, and duplicates panel (a)'s content |
| C13 | **Fig. 3 caption**: "Scatter plots showing the noise-weighted **match** F ... the dominant (2,2) mode typically exceeds 0.95 agreement" | The figure's y-axes are **mismatch** 1−F, and the (2,2) panel shows a large RIT population at 0.1–0.8 |
| C14 | `:616`, Fig. 9 caption: SEOBNRv4PHM is "the time-domain **phenomenological** model" | SEOBNRv4PHM is an **effective-one-body** model; the paper's own `:157` lists EOB and IMRPhenom as distinct families |
| C15 | `:307`: "For all systems in categories (a)–(d), the in-plane spin components χ⊥ = 0 **by construction**" | Table I defines those categories by χ⊥ < ε_χ = 0.001, not χ⊥ = 0 |
| C16 | **Table I** cites `results/catalog_statistics.md` as its source | That file uses a spin threshold of 10⁻⁴ (not 10⁻³) and gives an SXS total of **4170**, not 4164; the SXS and MAYA rows disagree with Table I |
| C17 | `:311`: NRSur7dq4 "provides all mode coefficients up to ℓ = 4 (**excluding (5,5)**)" | (5,5) has ℓ = 5 and is already excluded by ℓ ≤ 4; the parenthetical is vacuous or misstates the model's mode content |

---

## 7. Section V (precessing) — the method is not validated

Section V presents a precessing pipeline and an SO(3) optimization but reports **no
results**. The Introduction (`:171`) nonetheless presents this machinery as something the
paper *did*. That framing must be corrected (see C3).

Beyond framing, I have specific concerns about the implementation, which the paper should
address before the pipeline is used in a follow-up:

1. **The optimizer can return a worse-than-identity answer. [VERIFIED in code]**
   `nrcatalogtools/waveform/modes.py:1120` computes `identity_mismatch` and **prints** it —
   then line 1134 sets `match = 1.0 - result.fun` from `differential_evolution` **without
   ever comparing to the identity baseline**. A maximization that can return less than a
   known feasible point is a bug. Consistent with this, the pilot CSVs record
   `match_rotated = 0.5437` for SXS:BBH:0162 (a **non-precessing** system, where the
   optimum is trivially near-identity) with β = 0.0, and `match_rotated = 0.9931` for
   SXS:BBH:0001 against per-mode matches of 0.99–0.9995. Fix: seed/polish at the identity
   and take the max.

2. **Normalization is wrong for a partial mode set. [VERIFIED in code, INFERENCE on impact]**
   In `objective_function` (`modes.py:1071`), `total_norm2_sq` is computed from the
   **unrotated** modes present in `common_modes`, while `h2_rot_matrix` mixes across the
   full −ℓ…ℓ block. Wigner rotation preserves the norm only over a *complete* ℓ-block. With
   the paper's mode set {(2,2),(2,1),(3,3),(4,4),(3,2),(4,3)} — m > 0 only — the numerator
   and denominator refer to different sets, and the "match" is not bounded or normalized
   correctly. Any missing m′ is silently filled with zeros (`modes.py:1093–1096`), so the
   rotation itself is also wrong.

3. **A φ_c–γ degeneracy is left in the search space.** The objective optimizes φ_c *and*
   the Euler angle γ, but a z-rotation acts as e^{−imγ}, exactly duplicating φ_c. The 4-D
   search therefore contains a flat direction, with `popsize=10, maxiter=50` — a small
   budget for a degenerate global search.

4. **No validation test is reported.** The standard checks are: rotate a mode set by a known
   R and recover it; verify R∘R⁻¹ = identity; verify the result against `scri`/`sxs`. The
   convention in Eq. (7), h'_{ℓm} = Σ_{m'} h_{ℓm'} D^ℓ_{m'm}(R), differs by transpose and/or
   conjugation from other common conventions, and `apply_wigner_rotation_to_mode_dict`
   (`matching.py:27`) implements yet another path. I was unable to execute that function in
   the project environment (`wigner.D(R, ell)` raised `AttributeError: 'int' object has no
   attribute 'size'` with the installed `spherical` version), so **[UNRESOLVED]** whether it
   is currently exercised at all. Please add a convention test to the test suite and cite it
   in the paper.

5. **Section V's t_target = t_peak − 4300M is presented without justification.** Why 4300M?
   Is it robust to that choice? What happens for simulations shorter than 4300M?

---

## 8. Framing and interpretation

The Introduction is admirably honest at `:169`:

> "because NRSur7dq4 is built exclusively from a suite of SXS simulations, it acts as an
> analytical proxy for the SpEC codebase. Consequently, this surrogate-mediated framework
> strictly evaluates how well other catalogs agree with the SXS baseline, rather than
> providing an independent, code-agnostic metric of absolute numerical accuracy."

This caveat then disappears. The Abstract and Conclusions speak of "cross-catalog
validation", "agreement across all three catalogs", and "the maturity and cross-consistency
of the underlying SpEC, LazEv, and MayaKranc codes". What the study measures is
d(catalog, SpEC-proxy). RIT scoring worse than SXS is the *expected* outcome of that
construction and is not evidence about LazEv. The caveat belongs in the Abstract, and the
Conclusions should be rewritten to respect it.

The title's word "Validation" overstates what a single-reference comparison can deliver.
"Comparison" would be defensible.

---

## 9. Presentation, and smaller items

- **`\del`, `\add`, `\repl`, `\prayush` tracked-change macros are still defined** (`:56–58`,
  `:91`). Remove before submission.
- **Stray `---` at the end of the Abstract** (`:136`).
- **Section VII.A "Model Dependency Analysis" is a `\subsection` inside `\section{Conclusions}`**
  (`:614`). A result that (in the authors' own words) overturns Section IV's interpretation
  cannot appear *after* the conclusions, in a subsection the conclusions never reference.
  Promote it to its own section before the Conclusions, and update the Conclusions.
- **`1%` at `:601` is unescaped, and a full sentence is missing from the compiled PDF.
  [VERIFIED]** LaTeX reads `%` as a comment. `pdftotext` on p. 16 of `paper.pdf` returns:
  *"consistently achieving mismatches below 1"* — and then stops. The remainder,
  *"...% and phase errors of < 0.1 rad/cycle at the low-eccentricity limit. This agreement
  underscores the maturity and cross-consistency of the underlying SpEC, LazEv, and
  MayaKranc numerical codes in standard binary configurations."*, does not appear in the
  paper at all. Use `1\%`. (This also means one of the Conclusions' headline sentences has
  never been read by anyone reviewing the PDF.)
- **Fig. 3 and Fig. 8 are 30-panel and 6-panel grids at full page width.** Panels are
  unreadable at print size. Select the two or three that carry the argument.
- **Fig. 6 packs two full CDF grids into one float**, with (a) and (b) sharing content.
- **Section II.A's ~1500 words on RWZ vs Ψ₄ extraction** are textbook material with no
  bearing on the analysis — the paper never uses the distinction, never states which
  extraction each catalog's data used, and never tests sensitivity to it. Either connect it
  to the results or cut it to a paragraph.
- **`f_lower` prescriptions are given twice and never reconciled**: the |m|/2 scaling at
  `:257` and `f_lower^match = max(f_lower^NR, f_lower^sur)` at `:324`. State the composition
  explicitly (the code applies `mode_f_lower` to the already-maxed value, but the paper
  should say so).
- **No upper cutoff is stated.** `compute_mode_match` defaults `f_upper=None` → Nyquist,
  so post-ringdown numerical noise enters the integral. State the choice.
- **No uncertainties anywhere.** Medians and percentiles are quoted to four decimal places
  (e.g. 0.9923) from samples of N = 49 with no bootstrap interval. For MAYA, N = 49 with
  known outliers; four significant figures is not meaningful.
- **Acknowledgments are "To be filled in"** (`:663`).

### Citations **[VERIFIED against `References.bib`]**

Several references do not support the statements they are attached to:

| Key | Actual title | Cited at | Problem |
|---|---|---|---|
| `Thornburg:2003sf` | "A Fast apparent horizon finder for three-dimensional Cartesian grids" | `:237`, for expanding the BMS slicing function in spherical harmonics | Unrelated |
| `MacFadyen:1998vz` | "Collapsars: Gamma-ray bursts and explosions in 'failed supernovae'" | `:151`, for BBH evolution accuracy | Unrelated |
| `Ruffini:2009hg` | "Electron-positron pairs in physics and astrophysics" | `:151`, same list | Unrelated |
| `Weaving:2023fji` | "Adapting the PyCBC pipeline ... for **LISA**" | `:157`, as *the* reference for PyCBC | Wrong paper (should be Usman et al. 2016 / Nitz et al.) |
| `Wette:2020air` | "SWIGLAL: Python and Octave interfaces to ... LALSuite" | `:157`, as *the* reference for LALSuite | Wrong paper |
| `Davis:1971gg`, `Chandrasekhar:1975zza` | particle infall; Schwarzschild QNMs | `:157`, in a list about PE and cosmology limits | Not relevant |

Also: **`hannam2009` (cited at `:159`) is not present in `References.bib`** (0 matches). It
survives only because `paper.bbl` is stale and still carries an entry from an older
bibliography — re-running BibTeX will produce an undefined citation. The `:157` citation
block contains 25 references for a single sentence; please prune it to those that are
actually used.

---

## 10. What I would need to see to recommend publication

**Blocking — the paper cannot be assessed until these are done:**

1. Regenerate **every** number in Tables III and V and in Sections IV.A–IV.C from one
   versioned analysis run, and state which run (commit, date). Resolve C1, C6, C7, C8, C9.
2. Purge NSNS/BHNS simulations; audit and document the provenance of the 1731-entry
   calibration list against the 1528 in Varma et al.
3. Apply an explicit validity filter (cycle count, physical `f_lower`, non-NaN) and report
   how many simulations each catalog loses.
4. Either extend the SEOBNRv4PHM comparison to RIT, MAYA, and spinning configurations —
   i.e. to the region where the effect it claims to explain actually lives — or delete
   Section VII.A's causal claims and retain it as a limited SXS-only, non-spinning
   cross-check. As written it cannot support "definitively proves".
5. Remove every reference to extrapolation "beyond the training domain" unless simulations
   with q > 4 are added.
6. Correct the amplitude/match reasoning (Section 5 above) throughout.

**Major — required for the physics to be credible:**

7. Resolution-difference study: quote the NR noise floor per catalog and state all results
   relative to it. Fix the RIT resolution mixing or justify pooling.
8. Test the RIT spin-label hypothesis (Section 4, M-fig): re-run the low-match RIT subset
   with χ1z ↔ χ2z exchanged.
9. Diagnose the in-sample failures (SXS:BBH:0276, 0223, 1145, 0200). These are known-answer
   tests; use them as the pipeline's acceptance criterion.
10. Replace or re-scope the Δφ/cycle metric; report the phase residual after optimal
    alignment.
11. Either fit the eccentricity power law properly (exponents, errors, per mode) or drop the
    claim; recompute eccentricity with a common estimator or restrict all eccentricity
    statements to within-catalog.
12. Report the mass dependence you already have on disk, or scope all results to M = 40 M⊙.
13. Fix the SO(3) optimizer (identity baseline, subset normalization, φ_c–γ degeneracy) and
    add a convention validation test — or remove Section V from this paper and publish it
    with the precessing results.
14. Move the caveat from `:169` into the Abstract, and align the Abstract/Conclusions with
    Table V.

**Minor:** items in Section 9, including the `1%` LaTeX bug, the tracked-change macros, the
missing `hannam2009` entry, the mis-citations, and Section VII.A's placement.

---

## 11. Assessment

The method is worth publishing. The surrogate-as-mediator idea genuinely does remove the
parameter-space-mismatch obstruction that has blocked direct cross-catalog comparison, and
the in-sample/out-of-sample partition is a good design — it gives the study a calibrated
null test, which most waveform-comparison papers lack.

What the manuscript does not yet do is separate the three things it is measuring: NR
truncation error, surrogate interpolation error, and pipeline error. At present the third
dominates the tails, demonstrably so — a training-set simulation returning a match of 0.38
with a phase error of 0.008 rad/cycle cannot be anything else — and the manuscript reads
those tails as physics. The largest single improvement available is to use the in-sample
subset as an acceptance gate: drive its mismatches to the ~10⁻³ level they must have by
construction, and only then interpret what remains.

I would be glad to review a revised version.
