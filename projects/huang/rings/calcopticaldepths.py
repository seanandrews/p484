import numpy as np
from continuumanalysis3 import Continuum
import matplotlib as mpl

sigma_sb = 5.67e-5 #erg cm^-2 s^-1 K^-4
Lsun = 3.83e33 #ergs
psi = 0.02 #grazing angle
au2cm = 1.496e13

def Tmid(r, Lstar, psi):
    r=r*au2cm
    return ((0.5*psi*Lstar*Lsun)/(4*np.pi*r**2*sigma_sb))**0.25

def calc_optical_depth(cont, Tdust, surfbrightness):
        #convert Ivals from Jy/beam to watts/ster
        # a jansky is 10^(-26) watts per square meter per hertz
        #this is all in mks units
        h = 6.62607004e-34 #m^2 kg/s
        c = 299792458 #m/s
        k = 1.38064852e-23 #m^2 kg s^-2 K^-1
        beamsize = np.pi*cont.bmin*cont.bmaj/(4*np.log(2)) #arcsec^2
        I_nu = surfbrightness*1.e-26*1/beamsize*(206264.806**2)
        B_nu = 2*h*cont.freq**3/c**2*1/(np.exp(h*cont.freq/(k*Tdust))-1)
        return -np.log(1-I_nu/B_nu)
