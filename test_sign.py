import sys
import numpy as np

sys.path.append("/home/prayush/src/nr-catalog-tools")
from nrcatalogtools.surrogate import (
    load_nrsur7dq4,
    generate_surrogate_modes,
    surrogate_dict_to_waveform_modes,
)
from nrcatalogtools import load_catalog
import pycbc.psd

wfm_nr = load_catalog("SXS").get("SXS:BBH:0001")
wfm_nr.LM = np.array([[2, 2]])
M, q, chi1, chi2, f_lower = 40.0, 1.0, [0, 0, 0], [0, 0, 0], 20.0
sur_dict, _ = generate_surrogate_modes(
    {
        "mass1": 20,
        "mass2": 20,
        "spin1x": 0,
        "spin1y": 0,
        "spin1z": 0,
        "spin2x": 0,
        "spin2y": 0,
        "spin2z": 0,
        "f_lower": 19.83,
    },
    M,
    1.0,
)
wfm_sur = surrogate_dict_to_waveform_modes(sur_dict, M, 1.0)
wfm_sur.LM = np.array([[2, 2]])
psd = pycbc.psd.aLIGOZeroDetHighPower(1000, 1.0 / 4096, 20.0)

# Hack _complex_to_frequencyseries in wfm_nr and wfm_sur
old_method = wfm_nr._complex_to_frequencyseries


def new_method(self, mode_ts, delta_f):
    from pycbc.types import TimeSeries

    ts_real = TimeSeries(mode_ts.data.real, delta_t=mode_ts.delta_t)
    ts_imag = TimeSeries(mode_ts.data.imag, delta_t=mode_ts.delta_t)
    fs_real = ts_real.to_frequencyseries(delta_f=delta_f)
    fs_imag = ts_imag.to_frequencyseries(delta_f=delta_f)
    fs_complex = fs_real.copy()
    fs_complex.data = fs_real.data - 1j * fs_imag.data  # CONJUGATE!
    return fs_complex


import types

wfm_nr._complex_to_frequencyseries = types.MethodType(new_method, wfm_nr)
wfm_sur._complex_to_frequencyseries = types.MethodType(new_method, wfm_sur)

match = wfm_nr.match_sphere_averaged(wfm_sur, psd, 26.1)
print("My (2,2) match with minus sign:", match)
