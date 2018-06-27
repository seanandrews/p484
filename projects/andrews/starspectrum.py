import numpy as np
import sys
from scipy.interpolate import interp1d

def starspectrum(teff, lstar, dpc=1., type='Nextgen', grid=False, Jy=True):

    # unit conversions
    lstar = 3.826e33 * lstar
    dcm = dpc * 3.0857e18

    # HARD-CODE
    logg = 4.0

    # calculate other physical parameters
    rstar = np.sqrt(lstar / (4.*np.pi*5.67051e-5*teff**4.))

    # load spectrum grid
    sgrid = np.load('nextgen_grid.npz')
    wl, spec = sgrid['wl'], sgrid['spec']
    tgrid, ggrid = sgrid['tgrid'], sgrid['ggrid']

    # interpolate in Teff
    ispec = np.zeros((len(ggrid), len(wl)))
    for i in range(len(wl)):
        for j in range(len(ggrid)):
            tint = interp1d(tgrid, spec[:,j,i])
            ispec[j, i] = tint(teff)

    # interpolate in log g
    fspec = np.zeros(len(wl))
    for i in range(len(wl)):
        gint = interp1d(ggrid, ispec[:,i])
        fspec[i] = gint(logg)
 
    # scale model spectrum to appropriate luminosity
    Fnu = fspec * (rstar / dcm)**2
    if (Jy == True): Fnu = 1e23 * Fnu

    return 1e-3*wl, Fnu 
