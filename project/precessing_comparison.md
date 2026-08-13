# Pipeline walkthrough: precessing SXS simulation vs NRSur7dq4

This document describes the full computation performed by
`project/scripts/compare_one_sim_vs_surrogate.py` → `nrcatalogtools/comparisons.py`
when run on a precessing SXS binary.  For precessing systems the SO(3)-optimized
match is enabled automatically; the standard path is therefore the full path described
here.

---

## Step 1 — Load catalog and waveform

```python
cat = load_catalog("SXS")
wfm = cat.get(sim_name)
```

`wfm` is a `WaveformModes` object wrapping the SXS `rhOverM` strain data in
**dimensionless NR units** (modes $h_{\ell m}(t) \cdot r / M$, where $t$ is in
units of $M_\text{total}$).  No physical scaling happens at this point.

---

## Step 2 — Parameter and precession detection

```python
params = cat.get_parameters(sim_name, total_mass=M)
```

For SXS the code reads the `reference_time` epoch (not `relaxation_time`):

```python
Momega = |reference_orbital_frequency|   # M Ω_orb, dimensionless NR units
f_lower = Momega / π / (M_total · MTSUN_SI)   # [Hz]
spin1   = reference_dimensionless_spin1   # 3-vector, inertial frame, heavier body
spin2   = reference_dimensionless_spin2   # 3-vector, inertial frame, lighter body
```

The `reference_orbital_frequency` magnitude is $M \Omega_\text{orb}$ at the SXS
reference epoch.  Dividing by $\pi$ gives the (2,2) GW frequency:

$$f_\text{lower} = \frac{M\Omega_\text{orb}}{\pi \cdot M_\text{sec}} = \frac{\Omega_\text{orb}}{\pi} \;\text{[Hz]}$$

So `f_lower` returned by `get_parameters` is the **(2,2) GW frequency** at the
reference epoch, not the orbital frequency.

**Precession detection and rotate auto-enable** (`comparisons.py:110-116`):

```python
chi1_perp = sqrt(spin1x² + spin1y²)
chi2_perp = sqrt(spin2x² + spin2y²)
is_precessing = chi1_perp > 1e-4 or chi2_perp > 1e-4
if is_precessing and not rotate:
    rotate = True   # SO(3)-optimized match enabled automatically
```

---

## Step 3 — Epoch-aligned surrogate modes (Phase 2)

`generate_surrogate_modes` is called with `catalog=cat` and `sim_name=sim_name`
**unconditionally** — the epoch-aligned spin extraction (Phase 2) runs for all
precessing SXS binaries regardless of the `rotate` flag.

### 3a. Detect the surrogate's training window start

```python
sur = load_nrsur7dq4()
_sur_t_start_M = abs(sur._sur_dimless.t_0)   # ≈ 4300 M for NRSur7dq4
```

This reads the surrogate's actual earliest training time from its internal
metadata so that the code adapts automatically if a different surrogate model
is loaded.

### 3b. Epoch-aligned spin extraction (`_epoch_align_spins`)

The function:

1. **Finds the reference time** at `t_target = t_peak − _sur_t_start_M`, clamped
   to the available horizon-data range.  For NRSur7dq4 this puts the epoch at
   approximately the start of the NR simulation (the surrogate's training window
   starts ~4300 M before merger).

2. **Identifies the heavier body.**  The SXS labeling (A, B) does not guarantee
   A is the heavier black hole, so the code checks masses at the reference epoch:

   ```python
   mA = h.A.mass[idx_h]
   mB = h.B.mass[idx_h]
   # chi_primary → spin of heavier body (chiA in gwsurrogate)
   # chi_secondary → spin of lighter body (chiB in gwsurrogate)
   ```

3. **Constructs the coprecessing frame** from horizon positions via central
   differences:

   $$\hat{n} = \frac{\vec{r}_\text{heavier} - \vec{r}_\text{lighter}}{|\vec{r}_\text{heavier} - \vec{r}_\text{lighter}|}$$

   $$\hat{L} = \frac{\vec{r}_\text{sep} \times \dot{\vec{r}}_\text{sep}}{|\vec{r}_\text{sep} \times \dot{\vec{r}}_\text{sep}|}$$

   $$\hat{\lambda} = \hat{L} \times \hat{n}$$

   This is the right-handed frame $(\ \hat{n},\; \hat{\lambda},\; \hat{L}\ )$,
   matching gwsurrogate's documented convention:
   $\chi_x = \chi \cdot \hat{n}$,
   $\chi_y = \chi \cdot (\hat{L} \times \hat{n})$,
   $\chi_z = \chi \cdot \hat{L}$.

4. **Rotates the inertial-frame spins** into the coprecessing frame:

   $$R = \begin{pmatrix} \hat{n} \\ \hat{\lambda} \\ \hat{L} \end{pmatrix}
   \quad\Rightarrow\quad
   \vec{\chi}_\text{cop} = R\,\vec{\chi}_\text{inertial}$$

5. **Computes `f_ref_dimless`** as the dimensionless (2,2) GW frequency at the
   reference epoch:

   $$f_\text{ref} = \frac{|\dot\phi_{22}|}{2\pi} \quad \text{[cycles/M, dimensionless]}$$

   where $\dot\phi_{22}$ is estimated by a central difference on the unwrapped
   (2,2) mode phase.

### 3c. The surrogate call

```python
t_sur, h_sur, _ = sur(q, chiA_cop, chiB_cop,
                      ellMax=4, dt=dt_dimless,
                      f_low=0, f_ref=f_ref_dimless)
```

- `f_low=0` — full waveform from $t \approx -4300\,M$; no truncation.
- `f_ref=f_ref_dimless` — the epoch at which the coprecessing-frame spins are
  defined.  The surrogate backward-evolves the spins from this epoch to its
  own start.
- `dt=\Delta t_\text{sec} / M_\text{sec}` — dimensionless time step.

If the surrogate raises an `omega_ref too small` error (NR waveform starts below
the surrogate's minimum frequency), the code re-extracts the spin vectors at the
clipped `f_ref` by calling `_epoch_align_spins` a second time with
`f_ref_target=f_ref_clipped`.  This keeps the spin epoch consistent with the
actual reference frequency used.

### 3d. Physical-unit scaling and epoch assignment

$$h^\text{phys}_{\ell m}(t) = h^\text{NR}_{\ell m}(t) \cdot
\underbrace{\frac{GM_\text{total}/c^2}{D_L}}_{\texttt{amp\_scale}}$$

at reference distance $D_L = 1\,\text{Mpc}$.  The time axis is shifted so
$t = 0$ is at the peak of $|h_{22}|$:

```python
peak_idx = argmax(|h_sur[(2,2)]|)
epoch = t_physical[0] - t_physical[peak_idx]
```

Both the NR waveform (loaded in step 1) and the surrogate `TimeSeries` objects
share this convention, so their absolute time stamps are directly comparable in
subsequent steps.

---

## Step 4 — PSD

```python
psd = from_string(psd_name, length_f, delta_f, low_freq_cutoff=f_lower_mode)
```

A `pycbc` analytic PSD (default: `aLIGOZeroDetHighPower`) is built freshly per
mode at the matching frequency resolution $\Delta f = 1 / (N_\text{FFT} \Delta t)$.

---

## Step 5 — Per-mode noise-weighted match

For each $(l, m) \in$ `NR_MODES`:

**a. Get NR mode and take real part**

```python
h_nr_complex = wfm.get_mode(l, m, total_mass=M, distance=1, delta_t_seconds=δt)
h_nr     = h_nr_complex.real()    # h+ = Re(h_lm)
h_sur_lm = h_sur[(l,m)].real()
```

Only $h_+$ is used.  `pycbc.filter.match` maximises over an overall phase
$e^{i\phi}$, so using $\text{Re}(h_{\ell m})$ is equivalent to using the full
complex mode: the phase maximisation recovers the missing $\pi/2$ freedom.

**b. Mode-specific frequency cutoff**

```python
f_lower_mode = f_lower_match * |m| / 2
```

where `f_lower_match = max(f_lower_NR, f_lower_surrogate)` is the (2,2) GW
frequency at the start of the shorter waveform.  For mode $(l, m)$:

| mode | $f_\text{mode}$ |
|------|-----------------|
| (2,2) | $f_{22}$ |
| (2,1) | $f_{22}/2$ |
| (3,3) | $3\,f_{22}/2$ |
| (4,4) | $2\,f_{22}$ |

**c. Intersect time windows, taper, pad**

Both waveforms are sliced to the common window
$[max(t^\text{start}_{NR}, t^\text{start}_{sur}),\;
   min(t^\text{end}_{NR},   t^\text{end}_{sur})]$,
tapered with a Tukey window ($\alpha=0.2$, i.e. 10% on each end),
then zero-padded to the next power of two.

**d. Noise-weighted match**

$$\mathcal{F}(h_\text{NR}, h_\text{sur}) =
\max_{\Delta t,\,\phi}
\frac{\langle h_\text{NR},\, h_\text{sur} \rangle_{\Delta t}}
{\sqrt{\langle h_\text{NR}, h_\text{NR}\rangle
       \langle h_\text{sur}, h_\text{sur}\rangle}}$$

where

$$\langle a, b \rangle = 4\,\text{Re}\!\int_{f_\text{low}}^{f_\text{Nyq}}
\frac{\tilde{a}^*(f)\,\tilde{b}(f)}{S_n(f)}\,df$$

The inner product uses the chosen analytic PSD.  Maximisation over $\Delta t$ is
performed via the FFT cross-correlation; maximisation over $\phi$ is handled by
`pycbc.filter.match` returning the complex SNR magnitude.

---

## Step 5b — SO(3)-optimized match (auto-enabled for precessing systems)

Because per-mode matches are computed in the NR simulation's fixed inertial frame,
any residual misalignment between that frame and the surrogate's output frame will
suppress the individual-mode values.  For precessing systems the SO(3) optimisation
finds the rotation $\hat{R} \in \text{SO}(3)$ that maximises the
sphere-averaged noise-weighted overlap:

```python
mm_rot, R_opt = wfm.match_sphere_averaged(
    h_sur,
    psd=psd_rot,
    f_lower=f_lower_match,
    delta_t=delta_t,
    return_rotation=True,
    total_mass=total_mass,
    distance=DISTANCE,
)
alpha, beta, gamma = R_opt.to_euler_angles
```

Concretely, the optimisation solves:

$$\hat{R} = \arg\max_{R \in \text{SO}(3)}
\sum_{(l,m) \in \text{modes}}
\mathcal{F}\!\left(h^\text{NR}_{lm},\;\sum_{m'} D^{(l)}_{mm'}(R)\,h^\text{sur}_{lm'}\right)$$

where $D^{(l)}_{mm'}(R)$ is the Wigner D-matrix.  The Euler angles
$(\alpha, \beta, \gamma)$ of $\hat{R}$ describe the remaining frame mismatch
between the NR simulation and the surrogate output.  For a perfect comparison
with perfectly aligned spins, $\hat{R}$ should be close to the identity; a large
$\beta$ (nutation) indicates residual orbital-plane precession not captured by
the epoch-aligned spin extraction.

---

## Step 6 — Phase drift metric

```python
phi_nr  = unwrap(angle(h_nr_complex))   # complex mode, common window
phi_sur = unwrap(angle(h_sur[(l,m)]))

ΔΦ_NR  = |phi_nr[-1]  - phi_nr[0]|
ΔΦ_sur = |phi_sur[-1] - phi_sur[0]|

N_cycles = ΔΦ_NR / (2π)
phase_diff_per_cycle = |ΔΦ_NR − ΔΦ_sur| / N_cycles   [rad/cycle]
```

This measures the mismatch in total accumulated GW phase (cycle-count error) over
the common time window, normalised per cycle.  Taking differences within each
waveform removes any constant initial-phase offset, so the result is independent of
coalescence-phase convention.

The metric is complementary to the match: the match is optimistic about time
alignment (it maximises over $\Delta t$), while the phase drift uses the absolute
time alignment (both waveforms referenced to $t = 0$ at peak amplitude).  A large
phase drift with a high match indicates the waveforms are frequency-accurate but
start at slightly different absolute times.

---

## Output

| Column | Description |
|--------|-------------|
| `match` | Noise-weighted $\mathcal{F}$ per mode, maximised over $\Delta t$ and $\phi$ |
| `match_rotated` | $\mathcal{F}$ after SO(3) frame optimisation (precessing systems) |
| `R_alpha, R_beta, R_gamma` | Euler angles of the optimal frame rotation |
| `phase_diff_per_cycle` | Cycle-count error (rad/cycle) at fixed time alignment |
| `n_cycles` | Total NR cycles in the common window |
| `f_lower_mode` | Low-frequency cutoff used for this mode (Hz) |
