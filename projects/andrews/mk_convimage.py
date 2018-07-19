import numpy as np
from astropy.convolution import convolve, convolve_fft
from astropy.convolution import Gaussian2DKernel
import os
import sys

def mk_convimage(p, nx=512, ny=512, cellsize=0.005):

    xoff = 0.		# negation implies positive shift is to the E
    yoff = 0.		# positive shift is to the N
    incl = 0.		# inclination in degrees
    PA = 0.		# PA in degrees E of N

    # define a two-dimensional grid for the image
    xp, yp = np.meshgrid(cellsize*(np.arange(nx)-0.5*nx+0.5), \
                         cellsize*(np.arange(ny)-0.5*ny+0.5))

    # define a projected, shifted radial grid
    xpp = -(xp-xoff)*np.sin(PA) + (yp-yoff)*np.cos(PA)
    ypp = -((xp-xoff)*np.cos(PA) + (yp-yoff)*np.sin(PA)) / np.cos(incl)
    r = np.sqrt( xpp**2 + ypp**2 )

    # assign a radial brightness profile to the image
    flx  = p[0]		# peak flux inside rc in mJy/beam
    rc   = p[1]
    rout = 100./140.	# radius of disk
    gam  = p[2]		# power law index inside rc
    bm   = p[3]          # beam FWHM in arcsec

    # compute a normalized surface brightness distribution (Jy/pixel)
    Ixy = np.zeros_like(r)
    Ixy[(r>0) & (r<=rout)] = flx/r[(r>0) & (r<=rout)]**gam

    # convolve that image with a Gaussian beam
    sdev_inpix = np.round(bm/2.355/cellsize)
    beam = Gaussian2DKernel(stddev=sdev_inpix)
    cIxy = convolve(Ixy, beam, boundary='extend')

    # now convert to units of Jy/beam
    cIxy /= cellsize**2 / (bm*bm/(4.*np.log(2.)))

    outpack = r, cIxy

    return outpack
