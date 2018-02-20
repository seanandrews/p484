import numpy as np
import matplotlib.pyplot as plt
from deproject_vis import deproject_vis

# files to compare
files = ['SB_quick', 'LB0_quick', 'LB1_quick']

# manual re-scalings to check flux calibration
rescl = [1.0, 1.0, 1.0]

# geometric parameters 
incl = 30.
PA   = 52.
offx = 0.118
offy = -0.386

# bin centers (use only linear scale for now)
uvbins = 10.+10.*np.arange(100)

# colors
cols = ['r', 'g', 'b']

# loop through files and plot the deprojected profiles
minvis = np.zeros((len(files)))
maxvis = np.zeros((len(files)))
for i in range(len(files)):

    # read in the data
    inpf = np.load(files[i]+'.vis.npz')
    u    = inpf['u']
    v    = inpf['v']
    vis  = rescl[i]*inpf['Vis']
    wgt  = inpf['Wgt']

    # deproject the visibilities and do the annular averaging
    vp   = deproject_vis([u, v, vis, wgt], bins=uvbins, incl=incl, PA=PA, 
                         offx=offx, offy=offy)
    vp_rho, vp_vis, vp_sig = vp

    # calculate min, max of deprojected, averaged reals (for visualization)
    minvis[i] = np.min(vp_vis.real)
    maxvis[i] = np.max(vp_vis.real)

    # plot the profile
    plt.plot(1e-3*vp_rho, vp_vis.real, 'o'+cols[i], markersize=2.8)

# plot adjustments
allmaxvis = np.max(maxvis)
allminvis = np.min(minvis)
if ((allminvis < 0) or (allminvis-0.1*allmaxvis < 0)):
    plt.axis([0, 1000, allminvis-0.1*allmaxvis, 1.1*allmaxvis])
else: plt.axis([0, 1000, 0., 1.1*allmaxvis])
plt.plot([0, 1000], [0, 0], '--k')
plt.xlabel('deprojected baseline length [klambda]')
plt.ylabel('average real [Jy]')
plt.show()
