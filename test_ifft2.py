import numpy as np
from pycbc.types import FrequencySeries
from pycbc.filter import matched_filter_core
import pycbc.fft

N = 1024
df = 1.0
htilde = FrequencySeries(np.ones(N // 2 + 1, dtype=complex), delta_f=df)
stilde = FrequencySeries(np.ones(N // 2 + 1, dtype=complex), delta_f=df)
psd = FrequencySeries(np.ones(N // 2 + 1, dtype=float), delta_f=df)

snr, corr, norm = matched_filter_core(htilde, stilde, psd=psd, low_frequency_cutoff=1.0)
print("PyCBC snr max:", snr.abs_max_loc()[0])

I_f = htilde.data.conj() * stilde.data / psd.data
I_f[0] = 0
_q = np.fft.ifft(I_f, n=N)
print("np.fft.ifft max:", np.max(np.abs(_q)))
print("Ratio:", snr.abs_max_loc()[0] / np.max(np.abs(_q)))
