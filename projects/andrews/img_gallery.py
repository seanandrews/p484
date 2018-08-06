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

# generalities
pdir = '/data/sandrews/ALMA_disks/final_images/'
jdir = '/data/sandrews/ALMA_disks/jane_supplementary_images/'
hdir = 'test'
cc = 2.9979e10
kk = 1.381e-16

fdir = [pdir, jdir, jdir, hdir,
        pdir, hdir, jdir, pdir,
        jdir, pdir, jdir, hdir,
        pdir, jdir, jdir, jdir,
        hdir, jdir, jdir, hdir]

names = ['HTLup', 'GWLup', 'IMLup', 'RULup', 
         'Sz114', 'Sz129', 'MYLup', 'HD142666', 
         'HD143006', 'AS205', 'SR4', 'Elias20', 
         'DoAr25', 'Elias24', 'Elias27', 'DoAr33', 
         'WSB52', 'WaOph6', 'AS209', 'HD163296']

labels = ['HT Lup', 'GW Lup', 'IM Lup', 'RULup', 
          'Sz 114', 'Sz 129', 'MY Lup', 'HD 142666', 
          'HD 143006', 'AS 205', 'SR 4', 'Elias 20', 
          'DoAr 25', 'Elias 24', 'Elias 27', 'DoAr 33', 
          'WSB 52', 'WaOph 6', 'AS 209', 'HD 163296']

dpc = [154., 155., 158., 159., 
       162., 161., 156., 148., 
       165., 128., 134., 138., 
       138., 136., 116., 139., 
       136., 123., 121., 101.]

aoffs = [0., 0., 0., -0.02,
         0., 0., -0.06, 0.01,
         0., 0., -0.06, -0.06,
         0.02, 0.10, 0., 0.,
         -0.12, -0.25, 0.01, -0.02]

doffs = [0., 0., 0., 0.08302,
         0., 0., 0.088659, 0.02,
         0.02, 0., -0.51, -0.49,
         -0.49, -0.38, 0., 0.,
         -0.43, -0.36, 0., 0.]

xlims = np.array([[0.5, -0.5], [1., -1.], [1.5, -1.5], [0.5, -0.5],
                  [0.5, -0.5], [0.7, -0.7], [0.6, -0.6], [0.5, -0.5],
                  [0.7, -0.7], [0.6, -0.6], [0.5, -0.5], [0.5, -0.5],
                  [1.2, -1.2], [1.3, -1.3], [1.7, -1.7], [0.5, -0.5],
                  [0.5, -0.5], [1., -1.], [1.2, -1.2], [1.3, -1.3]])

ylims = [[-1., 1.], [-1., 1.], [-1., 1.], [-1., 1.],
         [-1., 1.], [-1., 1.], [-1., 1.], [-1., 1.],
         [-1., 1.], [-1., 1.], [-1., 1.], [-1., 1.],
         [-1., 1.], [-1., 1.], [-1., 1.], [-1., 1.],
         [-1., 1.], [-1., 1.], [-1., 1.], [-1., 1.]]

vmins = [0., 0., 0., 0.,
         0., 0., 0., 0.,
         0., 0., 0., 0.,
         0., 0., 0., 0.,
         0., 0., 0., 0.]

vmaxs = [6., 1., 1., 4.,
         3., 4., 3., 4.,
         2., 7., 5., 5.,
         3., 5., 2., 4.,
         8., 5., 5., 5.]

vmaxs = [50., 50., 50., 50.,
         50., 50., 50., 50.,
         50., 50., 50., 50.,
         50., 50., 50., 50.,
         50., 50., 50., 50.]

vmaxs = [80., 20., 15., 75.,
         30., 30., 50., 50.,
         15., 60., 50., 50.,
         50., 50., 20., 70.,
         100., 35., 35., 70.]

# color scale 
cm = 'inferno'

# set up plot
fig = plt.figure(figsize=(7.5, 9.4))
gs  = gridspec.GridSpec(5, 4, width_ratios=(1, 1, 1, 1), 
                              height_ratios=(1, 1, 1, 1, 1))

# loop through images
for i in range(len(names)):

    # grab image, header
    if (fdir[i] == pdir): suff = 'script' 
    if (fdir[i] == jdir): suff = 'taper'
    if (fdir[i] == hdir): suff = 'hires'
    hdulist = fits.open(pdir+names[i]+'_'+suff+'_image.fits')
    Inu = np.squeeze(hdulist[0].data)
    hdr = hdulist[0].header

    # convert to brightness temperature
    beam = np.pi * hdr['BMAJ'] * hdr['BMIN'] / (4.*np.log(2.))
    beam *= (np.pi/180.)**2
    nu = hdr['CRVAL3']
    Tb = (1e-23 * Inu / beam) * cc**2 / (2.*kk*nu**2)
    print(names[i], nu, 3.6e6*hdr['BMAJ'], 3.6e6*hdr['BMIN'], hdr['BPA'])

    # define coordinate grid
    RA  = 3600. * hdr['CDELT1'] * (np.arange(hdr['NAXIS1'])-(hdr['CRPIX1']-1))
    DEC = 3600. * hdr['CDELT2'] * (np.arange(hdr['NAXIS2'])-(hdr['CRPIX2']-1))
    ext = (np.max(RA)-aoffs[i], np.min(RA)-aoffs[i], 
           np.min(DEC)-doffs[i], np.max(DEC)-doffs[i])

    # plot the image 
    ax = fig.add_subplot(gs[np.floor_divide(i, 4), i%4])
    norm = ImageNormalize(vmin=vmins[i], vmax=vmaxs[i], stretch=AsinhStretch())
    im = ax.imshow(Tb, origin='lower', cmap=cm, 
                   extent=ext, aspect='equal', norm=norm)

    # plot beam
    beam = Ellipse(((xlims[i])[0] + 0.1*np.diff(xlims[i]), 
                    (xlims[i])[1] - 0.1*np.diff(xlims[i])), 
                   hdr['BMAJ']*3600., hdr['BMIN']*3600., 90.-hdr['BPA'])
    beam.set_facecolor('w')
    ax.add_artist(beam)

    # plot the annotations
    ax.annotate(labels[i], xy=(0.06, 0.87), xycoords='axes fraction', 
                horizontalalignment='left', color='w')
    dr = 10.
    ax.plot([(xlims[i])[1] - 0.1*np.diff(xlims[i]), dr / dpc[i] + \
             (xlims[i])[1] - 0.1*np.diff(xlims[i])], 
            [(xlims[i])[1] - 0.1*np.diff(xlims[i]), 
             (xlims[i])[1] - 0.1*np.diff(xlims[i])], '-w')
    if (i == 0):
        ax.annotate('10 au', xy=(0.5*dr / dpc[i] + \
                    (xlims[i])[1] - 0.1*np.diff(xlims[i]), 
                    0.04 + (xlims[i])[1] - 0.1*np.diff(xlims[i])), 
                    xycoords='data', horizontalalignment='center', color='w', 
                    fontsize=7.5)

    # figure properties
    ax.set_xlim(xlims[i])
    ax.set_ylim(-1.*xlims[i])
    ax.set_xticklabels([])
    ax.set_yticklabels([])

fig.subplots_adjust(hspace=0.03, wspace=0.03)
fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)
fig.savefig('img_gallery.pdf', dpi=1000)
fig.clf()
