import spherical
import numpy as np
import quaternionic

R = quaternionic.array.from_euler_angles(0.1, 0.2, 0.3)
wigner = spherical.Wigner(4)
D_full = np.zeros(wigner.Dsize, dtype=complex)
wigner.D(R, out=D_full)

ell = 2
D = np.zeros((2 * ell + 1, 2 * ell + 1), dtype=complex)
for i, m in enumerate(range(-ell, ell + 1)):
    for j, mp in enumerate(range(-ell, ell + 1)):
        D[i, j] = D_full[wigner.Dindex(ell, m, mp)]

print(D.shape)
print(D)
