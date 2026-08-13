import numpy as np
from pycbc.types import FrequencySeries
from pycbc.filter import matched_filter_core

N = 1024
df = 1.0
htilde = FrequencySeries(np.ones(N // 2 + 1, dtype=complex), delta_f=df)
stilde = FrequencySeries(np.ones(N // 2 + 1, dtype=complex), delta_f=df)
psd = FrequencySeries(np.ones(N // 2 + 1, dtype=float), delta_f=df)

snr, corr, norm = matched_filter_core(htilde, stilde, psd=psd, low_frequency_cutoff=1.0)
maxsnr = snr.abs_max_loc()[0]
match = maxsnr * norm / np.sqrt(norm**2)  # actually Sigmasq for h2 is norm^2
print("PyCBC match:", match)

# Now my way
I_f = htilde.data.conj() * stilde.data / psd.data
I_f[0] = 0  # low_frequency_cutoff=1.0
_q = np.fft.ifft(I_f, n=N)
my_match = 4 * df * N * np.max(np.abs(_q)) / norm**2
print("My match:", my_match)
