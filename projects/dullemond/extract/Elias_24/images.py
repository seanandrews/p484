import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
#from scipy import interpolate
from scipy import convolve
import scipy.ndimage

def get_tbright(intensity,freq,linear=True):
    cc          = 2.9979245800000e10      # Light speed             [cm/s]
    kk          = 1.3807e-16              # Bolzmann's constant     [erg/K]
    hh          = 6.6262e-27              # Planck's constant       [erg.s]
    if linear:
        tbright = intensity*(cc**2)/(2*(freq**2)*kk)
    else:
        tbright = hh*freq/(kk*np.log(2*hh*freq**3/cc**2*1./intensity+1.))
    return tbright
            
class continuumimage(object):
    def __init__(self,filename,offset_RA=None,offset_DEC=None,src_distance=None):
        #
        # Read the fits file
        # Most part taken from a script by Jane Huang
        #
        hdulist     = fits.open(filename)
        self.image_jybeam = np.nan_to_num(np.squeeze(hdulist[0].data))
        self.nx     = self.image_jybeam.shape[0]
        self.ny     = self.image_jybeam.shape[1]
        self.nn     = np.max([self.nx,self.ny])
        self.header = hdulist[0].header
        self.bmaj   = self.header['BMAJ']*3600 # in arcsec
        self.bmin   = self.header['BMIN']*3600 # in arcsec
        self.ang    = self.header['BPA']
        self.freq   = self.header['CRVAL3'] # frequency in Hz
        self.imsize = self.header['NAXIS1'] # pixels
        self.delt_ra  = self.header['CDELT1']*3600 # in arcsec
        self.delt_dec = self.header['CDELT2']*3600 # in arcsec
        if offset_RA is not None: self.offset_RA  = float(offset_RA)
        if offset_DEC is not None: self.offset_DEC = float(offset_DEC)
        #self.PA   = float(PA)
        #self.incl = float(incl)
        if src_distance is not None:
            self.src_distance = float(src_distance)
        else:
            self.src_distance = 0.
        hdulist.close()
        #
        # Convert from Jy/beam to CGS units: erg/cm^2/s/Hz/ster
        #
        au  = 1.49598e13     # Astronomical Unit       [cm]
        pc  = 3.08572e18     # Parsec                  [cm]
        self.solidangle_beam = (au/pc)**2*np.pi*self.bmaj*self.bmin/(4*np.log(2.)) # Solid angle of a Gaussian beam
        Jy          = 1e-23  # Jy in CGS units: erg/cm^2/s/Hz
        self.image  = self.image_jybeam*Jy/self.solidangle_beam # Image intensity in erg/cm^2/s/Hz/ster
        #
        # Find the central peak of the image
        #
        self.immax  = self.image.max()
        self.ix0,self.iy0 = np.where(self.image==self.immax)
        self.ix0    = self.ix0[0]
        self.iy0    = self.iy0[0]
        if np.abs(np.abs(self.delt_ra/self.delt_dec)-1.)>1e-6:
            print('Warning: delt_ra != delt_dec')

    def radial(self,angle,nl=None,leng=None):
        if leng is None:
            leng = self.nn
        if nl is None:
            nl = self.nn
        self.rp    = np.linspace(0.,leng,nl)
        self.xp    = float(self.ix0) + self.rp*np.cos(angle*np.pi/180.)
        self.yp    = float(self.iy0) + self.rp*np.sin(angle*np.pi/180.)
        self.imray = scipy.ndimage.map_coordinates(self.image, np.vstack((self.xp,self.yp)))
        self.ras   = self.rp*np.abs(self.delt_ra)

    def convert_to_circular(self,nphi=361,nr=None,leng=None,phi_offset=0.):
        if nr is None:
            nr = self.nn
        self.nr     = nr
        self.nphi   = nphi
        self.phi    = np.linspace(0,360,nphi)
        self.circim = np.zeros((nphi,nr))
        for iphi in range(nphi):
            phi = self.phi[iphi] + phi_offset
            print('Phi = {}'.format(phi))
            self.radial(phi,nl=nr,leng=leng)
            self.circim[iphi,:] = self.imray[:].copy()

    def save_circular(self,name):
        self.circim.tofile('circular_image_'+name+'.bin')
        with open('circular_image_'+name+'.info','w') as f:
            f.write('{}\n'.format(self.nr))
            f.write('{}\n'.format(self.nphi))
            f.write('{}\n'.format(self.ras.max()))
            f.write('{}\n'.format(self.src_distance))
            f.write('{}\n'.format(self.freq))

class circularimage(object):
    def __init__(self,name):
        self.read_circular(name)
        
    def read_circular(self,name):
        self.circim = np.fromfile('circular_image_'+name+'.bin', count=-1, dtype=np.float64)
        with open('circular_image_'+name+'.info','r') as f:
            self.nr = int(f.readline())
            self.nphi = int(f.readline())
            self.rasmax = float(f.readline())
            self.src_distance = float(f.readline())
            self.ras = np.linspace(0,self.rasmax,self.nr)
            self.freq = float(f.readline())
        self.phi    = np.linspace(0,360.,self.nphi)
        self.circim = self.circim.reshape((self.nphi,self.nr))

    def radial_convolve(self,gausswidth_fwhm_as):
        #
        # Convolve with a Gaussian (not quite right, but fair enough)
        #
        dx      = self.ras[1]-self.ras[0]
        nxkh    = int(2*gausswidth_fwhm_as/dx)
        nxk     = 1+2*nxkh
        rkern   = nxk*dx
        xk      = np.linspace(-rkern/2,rkern/2,nxk)
        sigma   = gausswidth_fwhm_as/2.355    # Convert from FWHM to sigma
        kernel  = np.exp(-0.5*(xk/sigma)**2)
        kernel  = kernel/kernel.sum()
        self.kernel = kernel
        self.circim_convolved = np.zeros_like(self.circim)
        for iphi in range(self.nphi):
            phi = self.phi[iphi]
            #print('Phi = {}'.format(phi))
            self.circim_convolved[iphi,:] = convolve(kernel,self.circim[iphi,:],mode='same')
        
    def find_peak(self,circim,rmin_as,rmax_as):
        cim   = circim.copy()
        ir0   = np.where(self.ras<rmin_as)[0].max()
        ir1   = np.where(self.ras>rmax_as)[0].min()
        cim[:,0:ir0]  = 0.
        cim[:,ir1:-1] = 0.
        rpeak = np.zeros_like(self.phi)
        for iphi in range(self.nphi):
            irpk = np.where(cim[iphi,:]==(cim[iphi,:]).max())[0]
            rpeak[iphi] = self.ras[irpk]
        return rpeak

    def radial_rescale(self,factor):
        assert len(factor)==self.nphi, 'Scaling factor must have nphi elements'
        self.circim_rescaled = np.zeros_like(self.circim)
        for iphi in range(self.nphi):
            ras_rescaled = self.ras*factor[iphi]
            self.circim_rescaled[iphi,:] = np.interp(ras_rescaled,self.ras,self.circim[iphi,:])
        
