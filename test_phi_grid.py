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
wfm_sur = surrogate_dict_to_waveform_modes(sur_dict, M, 1.0)
psd = pycbc.psd.aLIGOZeroDetHighPower(1000, 1.0 / 4096, 20.0)

wfm_nr.match_sphere_averaged(wfm_sur, psd, 26.1)
