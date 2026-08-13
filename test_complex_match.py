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
wfm_sur = surrogate_dict_to_waveform_modes(sur_dict)

h1 = wfm_nr.get_mode(2, 2, to_pycbc=True)
h2 = wfm_sur.get_mode(2, 2, to_pycbc=True)
print("NR max real:", np.max(h1.data.real), " max imag:", np.max(h1.data.imag))
print("Sur max real:", np.max(h2.data.real), " max imag:", np.max(h2.data.imag))

# Let's compute pycbc match on REAL part
from pycbc.filter import match as pycbc_match

psd = pycbc.psd.aLIGOZeroDetHighPower(1000, 1.0 / 4096, 20.0)
m, _ = pycbc_match(h1.real(), h2.real(), psd=psd, low_frequency_cutoff=26.1)
print("PyCBC Real match:", m)

m_imag, _ = pycbc_match(h1.imag(), h2.imag(), psd=psd, low_frequency_cutoff=26.1)
print("PyCBC Imag match:", m_imag)

m_cross1, _ = pycbc_match(h1.real(), h2.imag(), psd=psd, low_frequency_cutoff=26.1)
print("PyCBC Real vs Sur Imag match:", m_cross1)

m_cross2, _ = pycbc_match(h1.imag(), h2.real(), psd=psd, low_frequency_cutoff=26.1)
print("PyCBC Imag vs Sur Real match:", m_cross2)
