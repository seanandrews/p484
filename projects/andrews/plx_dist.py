import numpy as np
import os
import sys

def plx_dist(varpi, evarpi, nsamples=1e5, lopc=0.001, hipc=3000., 
             ddpc=0.1, prior_type='flat'):

    # convert to arcseconds
    varpi  *= 1e-3
    evarpi *= 1e-3

    # discretized distance grid in pc
    dgrid = np.linspace(lopc, hipc, num=np.round((hipc-lopc)/ddpc))

    # discretized likelihood
    L_d = 1./(np.sqrt(2.*np.pi) * evarpi) * \
          np.exp(-1/(2.*evarpi**2) * (varpi - 1./dgrid)**2)

    # define some options for the prior function
    def pi_d(d, prior_type='flat'):
        return 1.0

    # define the discretized posterior: p(d | varpi, evarpi) = L_d * pi*d
    pdist = L_d * pi_d(dgrid)
    pdist /= np.sum(pdist)

    # randomly draw posterior samples from that discretized posterior pdf
    dists = np.random.choice(dgrid, nsamples, p=pdist)

    return dists
