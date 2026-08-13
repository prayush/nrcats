# Implementation Plan: Cross-Catalog Waveform Validation Paper Enhancements

This document outlines the systematic plans and specific script additions needed to address the feedback on the paper draft.

## User Review Required
Please review the updated detailed code requirements for the scripts. Once approved, I will begin executing this plan by writing the scripts and running the tests.

---

## 1. Expanding on Figure 4 (Parameter Space Hotspots)
**Goal:** Expand on Figure 4 by detailing where the "hotspots" of mismatch occur in the $(q, \chi_{\rm eff})$ parameter space, and generate a descriptive paragraph for the main text.

**Code Requirements:**
- **Script Name:** `project/scripts/analyze_figure4_hotspots.py`
- **Dependencies:** `pandas`, `numpy`.
- **Algorithm:**
  1. Load `batch_aligned_all.csv` and filter for quasi-circular systems ($e_0 < 10^{-3}$).
  2. For each catalog, compute the 2D bin averages of the $(2,2)$ mismatch on a grid of $q$ vs $\chi_{\rm eff}$ (e.g., bin $q \in [1,4]$ and $\chi_{\rm eff} \in [-1,1]$).
  3. Identify the parameter bins with the highest average mismatch (the "hotspots") for each catalog.
  4. Print out a summary paragraph text detailing these findings (e.g., "In Figure 4, we observe that the mismatch $(1-\mathcal{F})$ increases systematically in regions of high mass ratio ($q > 3$) and high effective spin. For the RIT catalog, mismatches in this region often exceed..."). This text will be drafted to be copied directly into Section IV.B.2 of the paper.

---

## 2. Comparing with Other Models (LALSimulation)
To assess whether the discrepancies persist when using analytical phenomenological models instead of SpEC-trained surrogates, we will update the existing pipeline to support `lalsimulation` models.

**Code Requirements:**
1. Update `project/scripts/batch_aligned_catalogs.py` to accept a `--model` argument (e.g., `NRSur7dq4`, `IMRPhenomXPHM`, `SEOBNRv4PHM`).
2. Add a new module `nrcatalogtools.lalsim_interface` containing `generate_lalsim_modes(params, approximant)`. 
3. **Apples-to-Apples Length Synchronization**: To ensure an exact apples-to-apples comparison, the `generate_lalsim_modes` function will:
   - Compute the required waveform time length from the surrogate bounds.
   - Use `pycbc.waveform.get_td_waveform` with `mode_array` to generate the modes.
   - Truncate, zero-pad, and taper the LAL waveform to exactly match the length, lower frequency, and time grid of the surrogate and NR waveform.

---

## 3. Detailed Limitations of Surrogate: "Problematic" vs "Control" Script
**Goal:** Isolate and visually inspect simulations that have low eccentricity but surprisingly poor matches.

**Code Requirements:**
- **Script Name:** `project/scripts/plot_problematic_sims.py`
- **Dependencies:** `pandas`, `numpy`, `matplotlib`, `pycbc.filter`.
- **Algorithm:**
  1. **Load Data:** Read `batch_aligned_all.csv`.
  2. **Segment Space:**
     - *Problematic Group:* $e_0 < 10^{-3}$ AND $(1 - \mathcal{F}_{22}) > 3 \times 10^{-2}$.
     - *Control Group:* $e_0 < 10^{-3}$ AND $(1 - \mathcal{F}_{22}) < 10^{-3}$.
  3. **Process Each Sim:**
     - Load the NR waveform modes and generate the `NRSur7dq4` modes.
     - Maximize the match to find the optimal time shift $t_c$ and phase shift $\phi_c$.
     - **Sign Verification Phase:** To avoid visual artifacts caused by flipped sign conventions, the script will be tested strictly on known $10^{-3}$ and $10^{-2}$ mismatch cases first. The applied shift will be $h_{\rm sur}(t - t_c) e^{-i m \phi_c}$ (or equivalent depending on the optimizer output) such that the time-domain disagreement is faintly/barely visible for these cases.
  4. **Generate Plots:**
     - Create a 2-panel figure for each sim: Top panel showing time-domain $h_+(t)$ (NR vs Surrogate), bottom panel showing phase difference $\Delta \phi(t)$.
     - Save figures to `project/figs/problematic_sims/` and `project/figs/control_sims/`.

---

## 4. Estimating SNR Limits for Next-Gen Detectors
**Goal:** Determine the critical signal-to-noise ratio ($\rho_{\rm crit}$) at which the observed inter-catalog mismatches lead to distinguishable parameter estimation biases.

**Code Requirements:**
- **Script Name:** `project/scripts/estimate_snr_limits.py`
- **Dependencies:** `pandas`, `numpy`.
- **Algorithm:**
  1. Load `batch_aligned_all.csv` and filter for quasi-circular systems ($e_0 < 10^{-3}$).
  2. Extract the $(2,2)$ mode mismatch array for each catalog (SXS, RIT, MAYA).
  3. Compute the median and 90th percentile mismatch for each catalog.
  4. Use the Lindblom indistinguishability criterion: $1 - \mathcal{F} = \frac{D}{2 \rho_{\rm crit}^2}$, where $D$ is the effective number of intrinsic parameters (we will use $D=4$ representing $M_c$, $q$, $\chi_1$, $\chi_2$).
  5. Invert the formula to compute $\rho_{\rm crit} = \sqrt{\frac{D}{2 (1 - \mathcal{F})}}$ for the median and 90th percentile mismatches of each catalog.
  6. Print the resulting critical SNRs. The script will output a short text summary intended for direct inclusion in the paper's discussion section, contrasting these $\rho_{\rm crit}$ values (e.g., $\rho \sim 45$) against expected Cosmic Explorer SNRs ($\rho > 100$).

---

## 5. Sub-dominant Modes and Biases in Tests of GR
**Goal:** Estimate how inter-catalog mode differences bias tests of GR.

**Code Requirements:**
- **Script Name:** `project/scripts/estimate_gr_bias.py`
- **Dependencies:** `numpy`, `pycbc.filter`, `scipy.integrate`.
- **Algorithm:**
  1. We will numerically compute the waveform derivative $\partial_j h$ with respect to a parameter $\theta_j$ using finite differences of the surrogate model around a target binary.
  2. The Fisher matrix $\Gamma_{ij} = \langle \partial_i h | \partial_j h \rangle$ will be computed using the `pycbc.filter.match` noise-weighted inner product function.
  3. We will compute the systematic bias vector $\Delta_i = \langle \delta h | \partial_i h \rangle$, where $\delta h = h_{\rm SXS} - h_{\rm RIT}$ (the waveform difference across catalogs).
  4. The absolute parameter bias is $\Delta \theta^i = \sum_j (\Gamma^{-1})^{ij} \Delta_j$.
  5. The script will output a table comparing the bias $\Delta \theta^i$ against the statistical uncertainty $\sigma_i = \sqrt{(\Gamma^{-1})^{ii}}$ for key parameters, allowing us to quantify the exact GR test bias.

---

## 6. Parameter-space boundary safety
**Goal:** Show how waveforms diverge at boundaries (like $q=4$ or high spins).

**Code Requirements:**
- **Script Name:** `project/scripts/plot_boundary_mismatches.py`
- **Dependencies:** `pandas`, `matplotlib.pyplot`.
- **Algorithm:**
  1. Read `batch_aligned_all.csv`.
  2. Create a 1x3 grid of subplots (for SXS, RIT, MAYA).
  3. Scatter plot Mismatch $(1 - \mathcal{F}_{22})$ on the X-axis vs initial eccentricity $e_0$ (log scale) on the Y-axis.
  4. Color the scatter points by mass ratio $q$ with a shared colorbar.

---

## 7. Identifying Where Codes Disagree Most
**Goal:** Visualize the parameter distribution of the "problematic" simulations.

**Code Requirements:**
- **Script Name:** `project/scripts/plot_disagreement_corner.py`
- **Dependencies:** `pandas`, `matplotlib.pyplot`, `seaborn`, `numpy`.
- **Algorithm:**
  1. Filter the CSV for "problematic" systems: $e_0 < 10^{-3}$ and $(1 - \mathcal{F}_{22}) > 10^{-2}$.
  2. Compute `log_mismatch = np.log10(1 - match_22)`.
  3. Use `seaborn.PairGrid` to create a scatter matrix (corner plot) for the parameters: `q`, `chi_eff`, `spin1z`, `spin2z`.
  4. Color the points continuously using `log_mismatch` mapped to `matplotlib.cm.viridis`, highlighting parameter regions (high spin, high q) where disagreement peaks.
  5. Save to `project/figs/disagreement_corner_log.png`.

---

## 8. Interpolation Error vs Inter-code Differences
**Goal:** Compare in-sample vs out-of-sample SXS matches.

**Code Requirements:**
- **Script Name:** `project/scripts/plot_insample_vs_outsample.py`
- **Dependencies:** `pandas`, `numpy`, `matplotlib.pyplot`.
- **Algorithm:**
  1. Read `batch_aligned_all.csv`, filter for `catalog == 'SXS'` and `eccentricity < 1e-3`.
  2. Split into `df_in` (`nrsur7dq4_calibration == True`) and `df_out` (`False`).
  3. Create a figure with 3 horizontal subplots for modes $(2,2)$, $(3,3)$, and $(4,4)$.
  4. For each mode, compute the mismatches $1 - \mathcal{F}_{\ell m}$. Drop any NaNs.
  5. Use `np.sort` and empirical counts (`np.arange(1, len+1)/len`) to plot the Cumulative Distribution Function (CDF) of the mismatches. Set a log scale on the X-axis.
  6. Plot `df_in` as a solid line and `df_out` as a dashed line. Save figure.

---

## 9. Initial Data Formulations and Long-term Phase Accumulation
**Goal:** Quantify differing phase drifts between XCTS (SXS) and Bowen-York (RIT) initial data.

**Code Requirements:**
- **Script Name:** `project/scripts/plot_phase_accumulation_drift.py`
- **Dependencies:** `nrcatalogtools`, `numpy`, `matplotlib.pyplot`, `scipy.signal`.
- **Algorithm:**
  1. Automatically select 3-5 matched pairs of SXS and RIT simulations with highly similar physical parameters (e.g., near-equal masses, zero spin).
  2. Load the time-domain $(2,2)$ mode from both catalogs. Time-align at $t=0$ (peak amplitude), and phase-align at an early reference time $t_{\rm ref}$.
  3. Compute the unwrapped phase $\phi(t)$ for both waveforms.
  4. Compute the phase difference $\Delta \phi(t) = \phi_{\rm SXS}(t) - \phi_{\rm RIT}(t)$.
  5. Apply a Savitzky-Golay filter (`scipy.signal.savgol_filter`) to smooth numerical noise, then use `np.gradient` to compute the phase derivative $d(\Delta \phi)/dt$.
  6. Plot $d(\Delta \phi)/dt$ vs time to visualize whether RIT exhibits larger initial oscillatory transients (junk radiation settling) or a distinct secular drift slope compared to SXS.

---

## 10. Extraction of Higher Harmonics (RWZ vs $\Psi_4$)
**Goal:** Assess if $\Psi_4$ integration drift systematically affects higher modes in RIT/MAYA compared to SXS CCE/RWZ.

**Code Requirements:**
- **Script Name:** `project/scripts/compare_higher_harmonic_variance.py`
- **Dependencies:** `pandas`, `scipy.stats`.
- **Algorithm:**
  1. Load `batch_aligned_all.csv` and filter for quasi-circular systems ($e_0 < 10^{-3}$).
  2. Extract the mismatches for the $(2,2)$, $(3,3)$, and $(4,4)$ modes separated by catalog (SXS, RIT, MAYA).
  3. To account for intrinsic mode-scaling of phase errors, compute the $m$-normalized mismatches: $\Delta_{(l,m)} = (1 - \mathcal{F}_{\ell m}) / m^2$.
  4. Compute descriptive statistics (median, variance, 90th percentile) for $\Delta_{(l,m)}$.
  5. Perform a Levene's test (`scipy.stats.levene`) to evaluate if the variance of the normalized $(4,4)$ mismatch in RIT/MAYA is statistically significantly larger than in SXS.
  6. Print a formatted statistical summary to stdout, suitable for direct inclusion in the paper draft.
