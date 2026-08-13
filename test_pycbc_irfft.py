import pycbc.types
import numpy as np

N = 100
arr = np.ones(N // 2 + 1, dtype=complex)
fs = pycbc.types.FrequencySeries(arr, delta_f=1.0)
ts = fs.to_timeseries()
print(ts.dtype)
