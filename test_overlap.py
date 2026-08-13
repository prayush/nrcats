import sys
import numpy as np

sys.path.append("/home/prayush/src/nr-catalog-tools")
from nrcatalogtools.surrogate import (
    get_surrogate_model,
    generate_surrogate_modes,
    surrogate_dict_to_waveform_modes,
)
from nrcatalogtools.catalog import get_waveform
import pycbc.psd

wfm_nr = get_waveform("SXS", "SXS:BBH:0001")
sur = get_surrogate_model("NRSur7dq4")
M, q, chi1, chi2, f_lower = 40.0, 1.0, [0, 0, 0], [0, 0, 0], 20.0
sur_dict = generate_surrogate_modes(sur, q, chi1, chi2, M, 1.0, f_lower)
wfm_sur = surrogate_dict_to_waveform_modes(sur_dict, M, 1.0)
psd = pycbc.psd.aLIGOZeroDetHighPower(1000, 1.0 / 4.0, 20.0)

match, R = wfm_nr.match_sphere_averaged(wfm_sur, psd, 26.1, return_rotation=True)
print("Optimized match:", match)
