import numpy as np

M=np.matrix([[1, 6], [5, 2]]);

print(M)

w, v = np.linalg.eig(M)

print(w)
print(v)