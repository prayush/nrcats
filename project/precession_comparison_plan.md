# Optimization Speedup Plan: Vectorized Frequency-Domain Matching

## Phase 1: Fixing the Vectorized FFT Bug
The current implementation of `match_sphere_averaged` is extremely slow because it performs rotations and re-allocates PyCBC `TimeSeries` objects inside every step of the global optimization loop. We attempted to vectorize this by pre-computing the FFTs.

However, the current FFT vectorization has a severe bug: it incorrectly handles complex waveforms! By using PyCBC's `to_frequencyseries()` on the real and imaginary parts separately, we are only extracting the **positive frequencies**. But in gravitational-wave conventions, modes with $m > 0$ (like the dominant $(2,2)$ mode) are proportional to $e^{-im\omega t}$, which means all of their physical power lives at **negative frequencies**!
Because the vectorization silently truncates the negative frequencies, the dominant modes are effectively zeroed out, leaving only numerical noise. This is why the global optimizer converges to nonsensical values (like `0.5437` for the aligned-spin binary `0162`).

### The Solution
We must properly compute the two-sided (complex) FFT and map both positive and negative frequencies appropriately.
1. **Compute Complex FFTs**: Instead of splitting into real/imaginary parts, we will use `scipy.fft.fft` on the full complex time series.
2. **Frequency Mapping**: A complex time series $h(t)$ has a two-sided spectrum. We must evaluate the overlap integral $\int \frac{h_1(f) h_2^*(f)}{S_n(|f|)} df$ over the full domain $[-f_{max}, -f_{min}] \cup [f_{min}, f_{max}]$.
3. **Vectorized Inner Loop**: We will linearly combine the pre-computed complex spectra, apply the phase and time shifts, and compute the overlap over all frequencies using standard fast NumPy array operations.

## Phase 2: Proper Parameter Epochs for Precessing Binaries
As you rightly pointed out, even if the coordinate frames match at $t=0$, the spins themselves precess over time. The "initial time" (where parameters are extracted) may be smaller, equal to, or larger than the surrogate's native epoch of $t = -4500M$. 
For true precessing binaries, passing spins extracted at a random $t_{ref}$ directly to the surrogate can result in a physical mismatch if the surrogate and NR simulation are not synchronized to a common epoch. 

Once the FFT vectorization is fixed and validated on aligned-spin binaries, we will address this by writing a robust parameter-handling function. The detailed steps for Phase 2 will be:
1. **Extract Time-Dependent Dynamics**: We will load the full `Horizons.h5` data from the SXS simulation to get the time-series trajectories of the spins $\vec{\chi}_1(t), \vec{\chi}_2(t)$ and the orbital angular momentum $\vec{L}(t)$ and separation vector $\vec{n}(t)$.
2. **Define Common Epoch**: We select a common time before merger, such as $t_{common} = -4500M$ (the start of `NRSur7dq4`'s internal dynamics), provided the NR simulation is long enough.
3. **Evaluate Physical State**: We interpolate the NR spin vectors and orbital frame vectors at exactly $t = t_{common}$.
4. **Align to Inertial Reference Frame**: We apply a rotation to these state vectors to enforce $\vec{L}(t_{common}) \parallel \hat{z}$ and $\vec{n}(t_{common}) \parallel \hat{x}$. This rigidly maps the NR simulation into the surrogate's expected inertial reference frame at that specific epoch.
5. **Evaluate Surrogate**: We pass these rotated spins to `NRSur7dq4` with its reference epoch explicitly set to match $t_{common}$. This guarantees both models simulate identical physical states.

## User Review Required

> [!NOTE]
> Are these Phase 2 details aligned with your physical intuition for handling the precessing epoch mismatch?

## Verification Plan
### Phase 1 Verification (Vectorized FFT Fix)
- Implement the corrected two-sided complex FFT matching logic in `match_sphere_averaged`.
- Re-run `compare_one_sim_vs_surrogate.py` for three different **aligned-spin** SXS runs where precession is zero:
  1. `SXS:BBH:0001` (Non-spinning, $q=1$)
  2. `SXS:BBH:0150` (Aligned-spin, $q=1$, $chi1z=0.2, chi2z=-0.2$)
  3. `SXS:BBH:0148` (Aligned-spin)
- Verify that the optimal match values exactly reproduce (or exceed) the expected `~0.99` values.

### Phase 2 Verification (Precessing Epoch Alignment)
- Implement the `Horizons.h5` parameter extraction and frame-rotation logic to synchronize the NR and surrogate spins at $t_{common} = -4500M$.
- Re-run `compare_one_sim_vs_surrogate.py` for three different **precessing** SXS runs:
  1. `SXS:BBH:0058` (Highly precessing, $q=5$)
  2. `SXS:BBH:0165` (Precessing, $q=6$)
  3. `SXS:BBH:0053` (Precessing, $q=3$)
- Verify that the SO(3)-optimized matches for these systems improve significantly (towards `~0.99`), proving that the physical epoch mismatch has been resolved.
