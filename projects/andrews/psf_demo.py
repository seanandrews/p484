import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colorbar import Colorbar
from matplotlib import mlab, cm
from astropy.visualization import (AsinhStretch, LogStretch, LinearStretch, ImageNormalize)
import sys

plt.rc('font', size=9)

# beam plotting function
def mk_beam(hdr, npts=200):
    semimajor = 0.5 * 3600. * hdr['BMAJ']
    semiminor = 0.5 * 3600. * hdr['BMIN']
    ang = np.radians(90.-hdr['BPA'])
    phi = 2.*np.pi*np.arange(npts)/(npts-1.)
    xp = semimajor*np.cos(phi)*np.cos(ang)-semiminor*np.sin(phi)*np.sin(ang)
    yp = semimajor*np.cos(phi)*np.sin(ang)+semiminor*np.sin(phi)*np.cos(ang)
    return [xp, yp]

# generalities
pdir = '/pool/asha0/SCIENCE/p484/sa_work/RULup/'
cc = 2.9979e10
kk = 1.381e-16

# image sizes
xlims = [0.5, -0.5]
ylims = [-0.5, 0.5]
aoff, doff = 3600.*-4.9074359961499946e-06, 3600.*2.3061111109563985e-5 

# color scale 
cm = 'inferno'
vmin_c = 0.
vmax_c = 70.
norm_img = ImageNormalize(vmin=vmin_c, vmax=vmax_c, stretch=AsinhStretch())
norm_psf = ImageNormalize(vmin=-0.05, vmax=1., stretch=AsinhStretch())

# image lists
sim_list = ['demo_SB', 'demo_LB1', 'demo_LB2', 
            'demo_ALL_rob05', 'demo_ALL_rob00']

# set up plot
fig = plt.figure(figsize=(7.5, 4.65))
gs  = gridspec.GridSpec(2, 6, height_ratios=(1, 1), 
                              width_ratios=(1, 1, 1, 1, 1, 0.06))
gs.update(bottom=0.075, top=0.61, wspace=0.05, hspace=0.05)

# loop through images
for i in range(len(sim_list)):

    # grab image
    hdulist = fits.open(pdir+'RULup_'+sim_list[i]+'.image.fits')
    Inu = np.squeeze(hdulist[0].data)
    hdr = hdulist[0].header

    # convert to brightness temperature
    beam = np.pi * hdr['BMAJ'] * hdr['BMIN'] / (4.*np.log(2.))
    beam *= (np.pi/180.)**2
    nu = hdr['CRVAL3']
    Tb = (1e-23 * Inu / beam) * cc**2 / (2.*kk*nu**2)

    # define coordinate grid
    RA  = 3600. * hdr['CDELT1'] * (np.arange(hdr['NAXIS1'])-(hdr['CRPIX1']-1))
    DEC = 3600. * hdr['CDELT2'] * (np.arange(hdr['NAXIS2'])-(hdr['CRPIX2']-1))
    ext = (np.max(RA)-aoff, np.min(RA)-aoff, np.min(DEC)-doff, np.max(DEC)-doff)

    # plot the image 
    ax = fig.add_subplot(gs[1,i])
    im = ax.imshow(Tb, origin='lower', cmap=cm, 
                   extent=ext, aspect='auto', norm=norm_img)

    # plot the annotations
    bx, by = mk_beam(hdr)
    ax.fill_between(bx + 0.35, by - 0.37, facecolor='w', interpolate=True)

    # figure properties
    ax.set_xlim(xlims)
    ax.set_ylim(ylims)
    ax.tick_params('both', length=3, direction='in', which='major', 
                   colors='white')
    for xtick in ax.get_xticklabels():
        xtick.set_color('black')
    for ytick in ax.get_yticklabels():
        ytick.set_color('black')
    ax.set_yticks([-0.5, 0, 0.5])
    if (i == 0):
        ax.set_xlabel('$\Delta \\alpha$ / $^{\prime\prime}$')
        ax.text(-0.30, 0.5, '$\Delta \delta$ / $^{\prime\prime}$', 
                horizontalalignment='center', verticalalignment='center', 
                rotation=90, transform=ax.transAxes)
    else:
        ax.set_xticklabels([])
        ax.set_yticklabels([])

# colorbar
cbax = fig.add_subplot(gs[1,5])
cb = Colorbar(ax=cbax, mappable=im, orientation='vertical', 
              ticklocation='right', ticks=[0, 2, 5, 10, 20, 50])
cbax.set_yticklabels(['0', '2', '5', '10', '20', '50'])
cbax.tick_params('both', length=3, direction='in', which='major',
                 colors='white')
cbax.set_ylabel('$T_b$ / K', labelpad=7)
for xtick in cbax.get_xticklabels():
    xtick.set_color('black')
for ytick in cbax.get_yticklabels():
    ytick.set_color('black')


# loop through PSFs
psflbls = ['robust=0.5', 'robust=0.5', 'robust=0.5', 'robust=0.5', 'robust=0.0']
for i in range(len(sim_list)):

    # grab psf image
    hdulist = fits.open(pdir+'RULup_'+sim_list[i]+'.psf.fits')
    psf = np.squeeze(hdulist[0].data)
    hdr = hdulist[0].header

    # define coordinate grid
    RA  = 3600. * hdr['CDELT1'] * (np.arange(hdr['NAXIS1'])-(hdr['CRPIX1']-1))
    DEC = 3600. * hdr['CDELT2'] * (np.arange(hdr['NAXIS2'])-(hdr['CRPIX2']-1))
    ext = (np.max(RA), np.min(RA), np.min(DEC), np.max(DEC))

    # plot the image 
    ax = fig.add_subplot(gs[0,i])
    im = ax.imshow(psf, origin='lower', cmap='plasma',
                   extent=ext, aspect='auto', norm=norm_psf)

    # annotations
    ax.annotate(psflbls[i], xy=(0.06, 0.86), xycoords='axes fraction',
                horizontalalignment='left', color='w')

    # figure properties
    ax.set_xlim([0.5, -0.5])
    ax.set_ylim([-0.5, 0.5])
    ax.tick_params('both', length=3, direction='in', which='major',
                   colors='white')
    for xtick in ax.get_xticklabels():
        xtick.set_color('black')
    for ytick in ax.get_yticklabels():
        ytick.set_color('black')
    ax.set_yticks([-0.5, 0, 0.5])
    ax.set_xticklabels([])
    ax.set_yticklabels([])

# colorbar
cbax = fig.add_subplot(gs[0,5])
cb = Colorbar(ax=cbax, mappable=im, orientation='vertical',
              ticklocation='right', ticks=[0, 0.1, 0.2, 0.5, 1])
cbax.tick_params('both', length=3, direction='in', which='major',
                 colors='white')
cbax.set_ylabel('PSF (norm.)')
for xtick in cbax.get_xticklabels():
    xtick.set_color('black')
for ytick in cbax.get_yticklabels():
    ytick.set_color('black')



gs1 = gridspec.GridSpec(1, 6, width_ratios=(1, 1, 1, 1, 1, 0.06))
gs1.update(bottom=0.715, top=0.98, wspace=0.05)

# loop through (u,v) coverage
uvsets = ['sb', 'lb1', 'lb2', 'all', 'all']
uvlbls = ['C40-5', 'C40-8/9', 'C40-8', 'all', 'all']

for i in range(len(uvsets)):

    # load u,v data
    inpf = np.load(pdir+'rulup_demo_'+uvsets[i]+'.vis.npz')
    uu   = inpf['u'] * 2.9979e5 / 232.6e9
    vv   = inpf['v'] * 2.9979e5 / 232.6e9
    spw  = inpf['spw']
    u = np.concatenate((uu[spw == 0], uu[spw == 8], uu[spw == 12]))
    v = np.concatenate((vv[spw == 0], vv[spw == 8], vv[spw == 12]))

    # plot the (u,v) tracks
    ax = fig.add_subplot(gs1[0,i])
    ax.plot(u, v, '.k', markersize=0.2, rasterized=True)

    # annotations
    ax.annotate(uvlbls[i], xy=(0.06, 0.86), xycoords='axes fraction',
                horizontalalignment='left', color='k')

    # figure properties
    ax.set_xlim([15.46, -15.46])
    ax.set_ylim([-16, 16])
    ax.tick_params('both', length=3, direction='in', which='major')
    if (i == 0):
        ax.set_xlabel('$u$ / km')
        ax.text(-0.30, 0.5, '$v$ / km',
                horizontalalignment='center', verticalalignment='center',
                rotation=90, transform=ax.transAxes)
    else:
        ax.set_xticklabels([])
        ax.set_yticklabels([])
    

fig.subplots_adjust(left=0.06, right=0.94)
fig.savefig('psf_demo.pdf', dpi=1000)
fig.clf()
