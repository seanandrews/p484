import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colorbar import Colorbar
from matplotlib import mlab, cm
from astropy.visualization import (AsinhStretch, LinearStretch, ImageNormalize)
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

# image sizes
xlims = [0.5, -0.5]
ylims = [-0.5, 0.5]
aoff, doff = -0.045, -0.13

# generalities
cc = 2.9979e10
kk = 1.381e-16

# color scale for compact observations
cm = 'inferno'
norm = ImageNormalize(vmin=0, vmax=35, stretch=AsinhStretch())
normc = ImageNormalize(vmin=0, vmax=5, stretch=AsinhStretch())

# image lists
sim_list = ['HTLup_SB_initcont_exec0', 'HTLup_SB_initcont_exec1', 
            'HTLup_LB_initcont_exec0', 'HTLup_LB_initcont_exec1']
notes = ['SB0', 'SB1', 'LB0', 'LB1']

# set up plot
fig = plt.figure(figsize=(7.5, 3.7))
gs  = gridspec.GridSpec(2, 5, width_ratios=(1, 1, 1, 1, 0.06), 
                              height_ratios=(1, 1))
                              

# loop through images
for i in range(len(sim_list)):

    # grab image
    hdulist = fits.open(sim_list[i]+'.fits')
    Inu = np.squeeze(hdulist[0].data)
    hdr = hdulist[0].header
    if (i == 0): ra0, dec0 = hdr['CRVAL1'], hdr['CRVAL2']
    pc_aoff = (hdr['CRVAL1'] - ra0)*np.cos(np.radians(dec0))
    pc_doff = hdr['CRVAL2'] - dec0

    # convert to brightness temperature
    beam = np.pi * hdr['BMAJ'] * hdr['BMIN'] / (4.*np.log(2.))
    beam *= (np.pi/180.)**2
    nu = hdr['CRVAL3']
    Tb = (1e-23 * Inu / beam) * cc**2 / (2.*kk*nu**2)

    # define coordinate grid
    RA  = 3600. * hdr['CDELT1'] * (np.arange(hdr['NAXIS1'])-(hdr['CRPIX1']-1))
    DEC = 3600. * hdr['CDELT2'] * (np.arange(hdr['NAXIS2'])-(hdr['CRPIX2']-1))
    ext = (np.max(RA)-aoff-pc_aoff, np.min(RA)-aoff-pc_aoff, 
           np.min(DEC)-doff-pc_doff, np.max(DEC)-doff-pc_doff)

    # plot the image 
    ax0 = fig.add_subplot(gs[0,i])
    img = ax0.imshow(Tb, origin='lower', cmap=cm, 
                    extent=ext, aspect='auto', norm=norm)
    ax0.plot([0.], [0.], '+g')

    # plot the annotations
    bx, by = mk_beam(hdr)
    ax0.fill_between(bx + 0.33, by - 0.35, facecolor='w', interpolate=True)
    ax0.annotate(notes[i], xy=(0.06, 0.87), xycoords='axes fraction', 
                horizontalalignment='left', color='w')

    # figure properties
    ax0.set_xlim(xlims)
    ax0.set_ylim(ylims)
    ax0.tick_params('both', length=3, direction='in', which='major', 
                   colors='white')
    for xtick in ax0.get_xticklabels():
        xtick.set_color('black')
    for ytick in ax0.get_yticklabels():
        ytick.set_color('black')
    ax0.set_xticks([0.4, 0.2, 0.0, -0.2, -0.4])

    if (i != 0):
        ax0.set_xticklabels([])
        ax0.set_yticklabels([])


    # plot the image 
    ax1 = fig.add_subplot(gs[1,i])
    imgc = ax1.imshow(Tb, origin='lower', cmap=cm,
                    extent=ext, aspect='auto', norm=normc)
    cx, cy = -2.505, 1.285
    ax1.plot([cx], [cy], '+g')

    # plot the annotations
    bx, by = mk_beam(hdr)
    ax1.fill_between(bx+cx+0.33, by+cy-0.35, facecolor='w', interpolate=True)
    ax1.annotate(notes[i], xy=(0.06, 0.87), xycoords='axes fraction',
                horizontalalignment='left', color='w')

    # figure properties
    ax1.set_xlim([cx+0.5, cx-0.5])
    ax1.set_ylim([cy-0.5, cy+0.5])
    ax1.tick_params('both', length=3, direction='in', which='major',
                   colors='white')
    for xtick in ax1.get_xticklabels():
        xtick.set_color('black')
    for ytick in ax1.get_yticklabels():
        ytick.set_color('black')
    ax1.set_xticks([-2.2,-2.4,-2.6,-2.8,-3.0])
    if (i == 0):
        ax1.set_xlabel('$\Delta \\alpha$ / $^{\prime\prime}$')
        ax1.set_ylabel('$\Delta \delta$ / $^{\prime\prime}$') 
    else:
        ax1.set_xticklabels([])
        ax1.set_yticklabels([])




# colorbars
cbax = fig.add_subplot(gs[0,4])
cb = Colorbar(ax=cbax, mappable=img, orientation='vertical',
              ticklocation='right')	#, ticks=[0, 0.3, 1, 3, 10, 30])
#cbax.set_yticklabels(['0.0','0.3','1', '3', '10', '30'])
cbax.tick_params('both', length=3, direction='in', which='major',
                 colors='white')
cbax.set_ylabel('$T_b$ / K')
for xtick in cbax.get_xticklabels():
    xtick.set_color('black')
for ytick in cbax.get_yticklabels():
    ytick.set_color('black')

cbax = fig.add_subplot(gs[1,4])
cb = Colorbar(ax=cbax, mappable=imgc, orientation='vertical',
              ticklocation='right')     #, ticks=[0, 0.3, 1, 3, 10, 30])
#cbax.set_yticklabels(['0.0','0.3','1', '3', '10', '30'])
cbax.tick_params('both', length=3, direction='in', which='major',
                 colors='white')
cbax.set_ylabel('$T_b$ / K')
for xtick in cbax.get_xticklabels():
    xtick.set_color('black')
for ytick in cbax.get_yticklabels():
    ytick.set_color('black')


fig.subplots_adjust(hspace=0.14, wspace=0.05)
fig.subplots_adjust(left=0.06, right=0.94, bottom=0.10, top=0.99)
fig.savefig('astrom_demo.pdf', dpi=1000)
fig.clf()
