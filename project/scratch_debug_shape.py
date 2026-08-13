import numpy as np
import sxs


def main():
    sim_name = "SXS:BBH:0058"
    sim = sxs.load(sim_name, auto_supersede=True, download=False)
    t_peak_dimless = sim.strain.max_norm_time()
    t_common = t_peak_dimless - 4500.0
    h = sim.horizons
    time_h = h.A.time
    print("time_h length:", len(time_h))
    idx = int(np.argmin(np.abs(time_h - t_common)))
    t_actual = time_h[idx]
    print(f"t_actual: {t_actual}")
    rh = sim.strain
    t_wfm = rh.time
    idx_wfm = int(np.argmin(np.abs(t_wfm - t_actual)))
    print(f"idx_wfm: {idx_wfm}")
    h22 = rh.data[:, rh.index(2, 2)]
    np.unwrap(np.angle(h22))

    # Is it nhat?  (values are unused; we are timing the lazy extraction itself)
    print("extracting nhat...")
    h.nhat[idx].flatten()
    print("extracting ellhat...")
    h.ellhat[idx].flatten()
    print("extracting chi_inertial...")
    h.A.chi_inertial[idx].flatten()
    h.B.chi_inertial[idx].flatten()
    print("done")


if __name__ == "__main__":
    main()
