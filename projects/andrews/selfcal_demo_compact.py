import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colorbar import Colorbar
from matplotlib import mlab, cm
from astropy.visualization import (AsinhStretch, PowerStretch, LogStretch, ImageNormalize)
import sys

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

# image sizes
xlims = [4., -4.]
ylims = [-4., 4.]
aoff, doff = 3600.*-4.9074359961499946e-06, 3600.*2.3061111109563985e-5 

# color scale for compact observations
cm = 'inferno'
vmin_c = -0.065
vmax_c = 30.
norm = ImageNormalize(vmin=vmin_c, vmax=vmax_c, stretch=LogStretch())

# image lists
sim_list = ['SB_contp0', 'SB_contp1', 'SB_contp2', 'SB_contap']
notes = [r'${\rm initial}$'+' '+r'${\rm (compact}$'+' '+r'${\rm only)}$',
         r'${\rm phase}$'+' '+r'${\rm self}$'+'-'+r'${\rm cal}$'+' '+r'${\rm (30s)}$',
         r'${\rm phase}$'+' '+r'${\rm self}$'+'-'+r'${\rm cal}$'+' '+r'${\rm (18s)}$',
         r'${\rm amp}$'+' '+r'${\rm self}$'+'-'+r'${\rm cal}$'+' '+r'${\rm (scan)}$',
         ' ']


# set up plot
fig = plt.figure(figsize=(7.5, 1.9))
gs  = gridspec.GridSpec(1, 5, width_ratios=(1, 1, 1, 1, 0.07))

# loop through images
for i in range(len(sim_list)):

    # grab image
    hdulist = fits.open(pdir+'RULup_'+sim_list[i]+'.image.fits')
    hdr = hdulist[0].header

    # define coordinate grid
    RA  = 3600. * hdr['CDELT1'] * (np.arange(hdr['NAXIS1'])-(hdr['CRPIX1']-1))
    DEC = 3600. * hdr['CDELT2'] * (np.arange(hdr['NAXIS2'])-(hdr['CRPIX2']-1))
    ext = (np.max(RA)-aoff, np.min(RA)-aoff, np.min(DEC)-doff, np.max(DEC)-doff)

    # plot the image 
    ax = fig.add_subplot(gs[0,i])
    im = ax.imshow(1e3*np.squeeze(hdulist[0].data), origin='lower', cmap=cm, 
                   extent=ext, aspect='auto', norm=norm)

    # plot the annotations
    bx, by = mk_beam(hdr)
    ax.fill_between(bx + 3., by - 3., facecolor='w', interpolate=True)
    ax.annotate(notes[i], xy=(0.06, 0.87), xycoords='axes fraction', 
                size=8, horizontalalignment='left', color='w')

    # figure properties
    ax.set_xlim(xlims)
    ax.set_ylim(ylims)
    ax.tick_params('both', length=3, direction='in', which='major', 
                   colors='white', labelsize=7)
    for xtick in ax.get_xticklabels():
        xtick.set_color('black')
    for ytick in ax.get_yticklabels():
        ytick.set_color('black')
    ax.set_yticks([-4, -2, 0, 2, 4])
    if (i == 0):
        ax.set_xlabel(r'$\Delta \alpha$'+' / '+r'$^{\prime\prime}$', fontsize=8)
        ax.set_ylabel(r'$\Delta \delta$'+' / '+r'$^{\prime\prime}$', fontsize=8)
    else:
        ax.set_xticklabels([])
        ax.set_yticklabels([])

# colorbar
cbax = fig.add_subplot(gs[0,4])
cb = Colorbar(ax=cbax, mappable=im, orientation='vertical', 
              ticklocation='right', ticks=[0, 0.3, 1, 3, 10, 30])
cbax.set_yticklabels(['0.0','0.3','1', '3', '10', '30'])
cbax.tick_params('both', length=3, direction='in', which='major',
                 colors='white', labelsize=7)
cbax.set_ylabel(r'$I_\nu$'+' / '+r'${\rm mJy}$'+' '+r'${\rm beam}^{-1}$', 
                fontsize=8)
for xtick in cbax.get_xticklabels():
    xtick.set_color('black')
for ytick in cbax.get_yticklabels():
    ytick.set_color('black')


fig.subplots_adjust(wspace=0.05)
fig.subplots_adjust(left=0.055, right=0.945, bottom=0.16, top=0.98)
fig.savefig('selfcal_demo_compact.pdf')
fig.clf()
