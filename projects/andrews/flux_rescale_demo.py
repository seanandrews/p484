import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os
import sys
from deproject_vis import deproject_vis

# plot setup
plt.rc('font', size=8)
fig = plt.figure(figsize=(3.5, 4.2))
gs  = gridspec.GridSpec(2, 1)
ax0 = fig.add_subplot(gs[0,0])
ax1 = fig.add_subplot(gs[1,0])

# deprojection parameters (from JH script)
PA   = 41.5
incl = 38.5
offx = 0
offy = 0

# datafiles
fle = ['SB1_initcont_exec0', 'SB1_initcont_exec1', 
       'LB1_initcont_exec0', 'LB1_initcont_exec1']

# load data and create visibility profiles
all_rho = np.zeros((100, len(fle)))
all_vre = np.zeros((100, len(fle)))
all_sig = np.zeros((100, len(fle)))
for i in range(len(fle)):
    inpf = np.load('GWLup_'+fle[i]+'_shift.vis.npz')
    u, v = inpf['u'], inpf['v']
    vis  = inpf['Vis']
    wgt  = inpf['Wgt']
    uvbins = 10.+10.*np.arange(100)
    vp = deproject_vis([u, v, vis, wgt], bins=uvbins, incl=incl, PA=PA,
                       offx=offx, offy=offy)
    vp_rho, vp_vis, vp_sig = vp
    all_rho[:len(vp_rho),i] = vp_rho
    all_vre[:len(vp_rho),i] = vp_vis.real
    all_sig[:len(vp_rho),i] = vp_sig.real

# plot the misaligned visibility profiles
ax0.set_xlim([180, 520])
ax0.set_ylim([0, 34])
col = ['k', 'g', 'r', 'b']
for i in range(len(fle)):
    vp_rho = 1e-3*all_rho[:,i]
    vp_vre = 1e3*all_vre[:,i]
    vp_sig = 1e3*all_sig[:,i]
    ax0.errorbar(vp_rho[vp_rho > 0], vp_vre[vp_rho > 0], 
                 yerr=vp_sig[vp_rho > 0], fmt='o'+col[i], alpha=0.5)


ax1.set_xlim([180, 520])
ax1.set_ylim([0, 34])
col = ['k', 'g', 'r', 'b']
for i in range(len(fle)):
    vp_rho = 1e-3*all_rho[:,i]
    vp_vre = 1e3*all_vre[:,i]
    vp_sig = 1e3*all_sig[:,i]
    if (i == 3): vp_vre *= 1./0.82095
    ax1.errorbar(vp_rho[vp_rho > 0], vp_vre[vp_rho > 0], 
                 yerr=vp_sig[vp_rho > 0], fmt='o'+col[i], alpha=0.5)


ax0.annotate('2017/05/14', xy=(500, 30), xycoords='data', 
             horizontalalignment='right', color='k')
ax0.annotate('2017/05/17', xy=(500, 27), xycoords='data', 
             horizontalalignment='right', color='g')
ax0.annotate('2017/09/24', xy=(500, 24), xycoords='data', 
             horizontalalignment='right', color='r')
ax0.annotate('2017/11/04', xy=(500, 21), xycoords='data', 
             horizontalalignment='right', color='b')
ax0.annotate('pipeline', xy=(200, 5), xycoords='data', color='k',
             horizontalalignment='left', verticalalignment='top', alpha=0.7)
ax1.annotate('re-scaled (22%)', xy=(200, 5), xycoords='data', 
             color='k', horizontalalignment='left', verticalalignment='top', 
             alpha=0.7)



ax0.set_xticklabels([])
ax0.yaxis.labelpad = 8
ax1.set_xlabel('(deprojected) baseline length / k$\lambda$')
ax1.set_ylabel('real $\mathcal{V}$ / mJy')
ax1.yaxis.labelpad = 8


fig.subplots_adjust(hspace=0.0)
fig.subplots_adjust(left=0.135, right=0.865, bottom=0.09, top=0.98)
fig.savefig('flux_rescale_demo.pdf', dpi=1000)
fig.clf()
