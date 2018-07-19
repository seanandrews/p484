import numpy as np
import matplotlib.pyplot as plt
from mk_convimage import mk_convimage

pars = np.array([3.0e-3, 0.5, 0.75, 0.3])
pars = np.array([4.0e-3, 0.5, 0.75, 0.25])
rad, img = mk_convimage(pars, nx=300, ny=300)
print(np.max(img))

pars[3] = 0.045
rad, img = mk_convimage(pars, nx=300, ny=300)
print(np.max(img))
plt.loglog(rad, img, '.b')


plt.show()


