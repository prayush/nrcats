import numpy as np
import sxs


def test_extract_spins():
    sim_name = "SXS:BBH:0058"
    print("Loading simulation...")
    # Get waveform to find peak time
    # We will simulate what we'd do inside the surrogate generator
    sim = sxs.load(sim_name, auto_supersede=True)

    rh = sim.strain
    t_peak = rh.max_norm_time()
    print(f"Peak time: {t_peak}")

    t_common = t_peak - 4500.0
    print(f"Target common time: {t_common}")

    h = sim.horizons
    time = h.A.time
    idx = (np.abs(time - t_common)).argmin()
    t_actual = time[idx]
    print(f"Closest Horizons time: {t_actual} (error: {t_actual - t_common})")

    # We need the frequency at this time
    # From waveform, find frequency at t_actual
    t_wfm = rh.time
    idx_wfm = (np.abs(t_wfm - t_actual)).argmin()

    # Get phase of (2,2) mode
    h22 = rh.data[:, rh.index(2, 2)]
    phase22 = np.unwrap(np.angle(h22))

    # Simple finite difference for frequency
    dt_wfm = t_wfm[idx_wfm + 1] - t_wfm[idx_wfm - 1]
    omega22 = (phase22[idx_wfm + 1] - phase22[idx_wfm - 1]) / dt_wfm
    f_gw_dimless = np.abs(omega22) / (2 * np.pi)
    print(f"GW Frequency (dimless) at t_actual: {f_gw_dimless}")

    # Extract frame vectors
    nhat = h.nhat[idx]
    ellhat = h.ellhat[idx]

    # Ensure they are normalized
    nhat = nhat / np.linalg.norm(nhat)
    ellhat = ellhat / np.linalg.norm(ellhat)

    # Gram-Schmidt to make strictly orthogonal (they should be, but just in case)
    ellhat = ellhat - np.dot(ellhat, nhat) * nhat
    ellhat = ellhat / np.linalg.norm(ellhat)

    lambdahat = np.cross(ellhat, nhat)

    # Note: NRSur7dq4 uses a frame where Z is along L (ellhat) and X is along the separation vector (nhat)
    # OR X is along the separation vector from lighter to heavier BH?
    # gwsurrogate documentation says: "X-axis along separation vector from black hole 2 to black hole 1"
    # In SXS, nhat is defined as x_A - x_B. Wait, is A the heavier or lighter?
    # In SXS, A is usually the heavier (if q >= 1). So x_1 - x_2.
    # We will assume X = nhat, Y = lambdahat, Z = ellhat.

    rot_matrix = np.array([nhat, lambdahat, ellhat])
    print("Rotation matrix rows (X, Y, Z):")
    print(rot_matrix)

    chiA_inertial = h.A.chi_inertial[idx]
    chiB_inertial = h.B.chi_inertial[idx]

    chiA_copr = rot_matrix @ chiA_inertial
    chiB_copr = rot_matrix @ chiB_inertial

    print("Original chiA:", chiA_inertial)
    print("Coprecessing chiA:", chiA_copr)
    print("Original chiB:", chiB_inertial)
    print("Coprecessing chiB:", chiB_copr)


if __name__ == "__main__":
    test_extract_spins()
