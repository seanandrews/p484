import numpy as np
import os
import sys
import matplotlib.pyplot as plt
sys.path.append('/home/sandrews/mypy/')
from deproject_vis import deproject_vis

# definitions
incl = 36.2
PA = 41.8
offx = -0.2843
offy = -0.1646

incl = 39.8
PA = 36.4
offx = -0.2919
offy = -0.1735


# read in the data
adat = 'SB_quick.vis.npz'
inpf = np.load(adat)
u    = inpf['u']
v    = inpf['v']
vis = inpf['Vis']
wgt = inpf['Wgt']
vpa  = deproject_vis([u, v, vis, wgt], bins=10.+10.*np.arange(1500),
                     incl=incl, PA=PA, offx=offx, offy=offy)
vpa_rho, vpa_vis, vpa_sig = vpa

bdat = 'LB0_quick.vis.npz'
inpf = np.load(bdat)
u    = inpf['u']
v    = inpf['v']
dvis = inpf['Vis']
dwgt = inpf['Wgt']
uv   = u, v
vpb  = deproject_vis([u, v, dvis, dwgt], bins=10.+10.*np.arange(1500),
                     incl=incl, PA=PA, offx=offx, offy=offy)
vpb_rho, vpb_vis, vpb_sig = vpb

cdat = 'LB1_quick_rescaled.vis.npz'
inpf = np.load(cdat)
u    = inpf['u']
v    = inpf['v']
dvis = inpf['Vis']
dwgt = inpf['Wgt']
uv   = u, v
vpc  = deproject_vis([u, v, dvis, dwgt], bins=10.+10.*np.arange(1500),
                     incl=incl, PA=PA, offx=offx, offy=offy)
vpc_rho, vpc_vis, vpc_sig = vpc

rdat = 'combined_quick.vis.npz'
inpf = np.load(rdat)
u    = inpf['u']
v    = inpf['v']
dvis = inpf['Vis']
dwgt = inpf['Wgt']
uv   = u, v
vpr  = deproject_vis([u, v, dvis, dwgt], bins=10.+10.*np.arange(1500),
                     incl=incl, PA=PA, offx=offx, offy=offy)
vpr_rho, vpr_vis, vpr_sig = vpr




plt.axis([00, 10000, -0.01, 0.095])
plt.plot([0., 10000.], [0., 0.], '--k')
#plt.errorbar(1e-3*vpa_rho, vpa_vis.real, yerr=vpa_sig.real, 
#             fmt='or', markersize=2.8)
#plt.errorbar(1e-3*vpb_rho, 1.0*vpb_vis.real, yerr=vpb_sig.real, 
#             fmt='og', markersize=2.8)
#plt.errorbar(1e-3*vpc_rho, 1.0*vpc_vis.real, yerr=vpc_sig.real, 
#             fmt='ob', markersize=2.8)
plt.errorbar(1e-3*vpr_rho, 1.0*vpr_vis.real, yerr=vpr_sig.real,
             fmt='ok', markersize=2.8)
plt.errorbar(1e-3*vpr_rho, 1.0*vpr_vis.imag, yerr=vpr_sig.imag,
             fmt='or', markersize=2.8, alpha=0.5)

#plt.errorbar(1e-3*vpa_rho, vpa_vis.imag, yerr=vpa_sig.imag, 
#             fmt='or', markersize=2.8)
#plt.errorbar(1e-3*vpb_rho, 1.05*vpb_vis.imag, yerr=vpb_sig.imag, 
#             fmt='og', markersize=2.8)
#plt.errorbar(1e-3*vpc_rho, 1.35*vpc_vis.imag, yerr=vpc_sig.imag, 
#             fmt='ob', markersize=2.8)

plt.show()

