import numpy as np
from scipy.interpolate import interp1d

def deredden(wl, Av, thresh=0.0):

    # load composite extinction curves (Alambda / AK)
    ext = np.loadtxt('ext_curves.dat')
    awl = ext[:,0]
    A1  = ext[:,1]
    A2  = ext[:,2]
    A3  = ext[:,3]

    # set thresholds for different extinction curve regimes
    Av_lo = thresh
    Av_hi = 7.75	# McClure 2009 threshold: AK = 1.0
    Av_me = 2.325	# McClure 2009 threshold: AK = 0.3
    if (Av_lo >= Av_me): Av_lo = 0.
    
    # define AV / AK factors based on regime
    if (Av >= Av_hi): AvAk, AA = 7.75, A3
    if ((Av >= Av_me) & (Av < Av_hi)): AvAk, AA = 7.75, A2
    if ((Av >= Av_lo) & (Av < Av_me)): AvAk, AA = 7.75, A2
    if (Av < Av_lo): AvAk, AA = 9.03, A1
    AK_AV = 1./AvAk

    # interpolate extinction curve onto input wavelength grid
    aint = interp1d(awl, AA, fill_value='extrapolate')
    Alambda = Av * AK_AV * aint(wl)

    return 10.**(0.4*Alambda)
