import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colorbar import Colorbar
from matplotlib import mlab, cm
from astropy.visualization import (AsinhStretch, LogStretch, ImageNormalize)
import sys
from matplotlib.patches import Ellipse

plt.rc('font', size=9)

# constants
cc = 2.9979e10
kk = 1.381e-16

# load the CO datacube
cubefile = '/data/sandrews/LP/ingest/AS209_12CO_combined_test3.fits'
hdulist = fits.open(cubefile)
Ico = np.squeeze(hdulist[0].data)
hdr = hdulist[0].header

# parse basic cube properties
nchan = Ico.shape[0]
aoff, doff = 0.01, 0.00
beam = (np.pi/180.)**2 * np.pi * hdr['BMAJ'] * hdr['BMIN'] / (4.*np.log(2.))

# define coordinate grid
RA  = 3600. * hdr['CDELT1'] * (np.arange(hdr['NAXIS1'])-(hdr['CRPIX1']-1))
DEC = 3600. * hdr['CDELT2'] * (np.arange(hdr['NAXIS2'])-(hdr['CRPIX2']-1))
ext = (np.max(RA)-aoff, np.min(RA)-aoff, np.min(DEC)-doff, np.max(DEC)-doff)

# display properties
cm = 'viridis'
vmin, vmax = 0., 40.	# these are in Tb / K
xlims = np.array([3.5, -3.5])

# set up plot (using 54 channels; 6 across, 9 down)
fig = plt.figure(figsize=(7.5, 9.2))
gs  = gridspec.GridSpec(8, 7, width_ratios=(1, 1, 1, 1, 1, 1, 0.06),
                              height_ratios=(1, 1, 1, 1, 1, 1, 1, 1))

# loop through channels
for i in range(48):

    # select a cube plane
    j = i+1
    chanmap = np.squeeze(Ico[j,:,:])
    
    # convert intensities to brightness temperatures
    nu = hdr['CRVAL3'] + j * hdr['CDELT3']   
    Tb = (1e-23 * chanmap / beam) * cc**2 / (2.*kk*nu**2)

    # plot the channel map
    ax = fig.add_subplot(gs[np.floor_divide(i, 6), i%6])
    norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=AsinhStretch())
    im = ax.imshow(Tb, origin='lower', cmap=cm, extent=ext, aspect='auto', 
                   norm=norm)

    # plot beam
    bell = Ellipse((xlims[0]+0.15*np.diff(xlims), xlims[1]-0.15*np.diff(xlims)),
                   hdr['BMAJ']*3600., hdr['BMIN']*3600., 90.-hdr['BPA'])
    bell.set_facecolor('w')
    ax.add_artist(bell)

    # annotations
    if (i == 0):
        ax.annotate('AS 209', xy=(0.08, 0.83), xycoords='axes fraction',
                    horizontalalignment='left', color='w')
    vlsr = 1e-3*hdr['ALTRVAL'] + 1e-5*j*cc*np.abs(hdr['CDELT3'])/hdr['RESTFRQ']
    vstr = '%5.2f' % vlsr
    if (vlsr > 0): vstr = '+'+vstr
    ax.annotate(vstr, xy=(0.92, 0.08), xycoords='axes fraction',
                horizontalalignment='right', color='w', fontsize=6)
    
    ax.set_xlim(xlims)
    ax.set_ylim(-1.*xlims)
    ax.tick_params('both', length=3, direction='in', which='major',
                   colors='white')
    for xtick in ax.get_xticklabels():
        xtick.set_color('black')
    for ytick in ax.get_yticklabels():
        ytick.set_color('black')
    ax.set_xticks([2, 0, -2])
    if (i == 42):
        ax.set_xlabel('$\Delta \\alpha$ / $^{\prime\prime}$')
        ax.text(-0.30, 0.5, '$\Delta \delta$ / $^{\prime\prime}$',
                horizontalalignment='center', verticalalignment='center',
                rotation=90, transform=ax.transAxes)
    else:
        ax.set_xticklabels([])
        ax.set_yticklabels([])

# colorbar
cbax = fig.add_subplot(gs[6:8,6])
cb = Colorbar(ax=cbax, mappable=im, orientation='vertical',
              ticklocation='right', ticks=[0, 5, 10, 20, 30, 40])
#cbax.set_yticklabels(['0', '2', '5', '10', '20', '50'])
cbax.tick_params('both', length=3, direction='in', which='major',
                 colors='white')
cbax.set_ylabel('$T_b$ / K', labelpad=5)
for xtick in cbax.get_xticklabels():
    xtick.set_color('black')
for ytick in cbax.get_yticklabels():
    ytick.set_color('black')

fig.subplots_adjust(hspace=0.03, wspace=0.03)
fig.subplots_adjust(left=0.055, right=0.945, bottom=0.04, top=0.99)

fig.savefig('chanmaps_AS209.png', dpi=100)
fig.clf()
