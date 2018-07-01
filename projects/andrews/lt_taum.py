import numpy as np
from scipy.stats import gaussian_kde
from emcee import EnsembleSampler
from astropy.io import ascii
from ScottiePippen.grids import model_dict
import argparse
import yaml
import sys
import os

def lt_taum(pTeff, plogLstar, grid_name='MIST', ntrials=10000, burn=0, 
            nwalkers=10):

    # set up parser
    parser = argparse.ArgumentParser(description="Given a set of MCMC samples of T, log L, use scipy.kde to approximate the density field.")
    parser.add_argument("--config", default="config.yaml", help="The config file specifying everything we need.")
    args = parser.parse_args()
    f = open(args.config)
    config = yaml.load(f)
    f.close()

    # collate the Teff, logLstar samples (presumed independent here)
    TlL_samples = np.column_stack((np.log10(pTeff), plogLstar))

    # initialize MCMC walkers
    ndim = 2
    age_low, age_high = 0.2, 20.     # in Myr
    Mstar_low, Mstar_high = 0.1, 3.  # in Msun
    p0 = np.array([np.log10(1e6*np.random.uniform(age_low, age_high, nwalkers)),
                   np.log10(np.random.uniform(Mstar_low, Mstar_high, nwalkers))]).T

    # KDE for Teff, logLstar
    samples = TlL_samples.T
    kernel = gaussian_kde(samples)

    # define the likelihood function
    def lnprob(p, grid):

        age, mass = p
        #if ((age < 0.0) or (mass < 0.0)):
        #    return -np.inf

        # smooth interpolation in H-R diagram
        temp = grid.interp_T(p)
        lL   = grid.interp_lL(p)

        # land outside the grid, you get a NaN; convert to -np.inf to sample
        if np.isnan(temp) or np.isnan(lL):
            return -np.inf

        # evaluate the KDE kernel
        lnp = kernel.logpdf([temp, lL])

        # return the log-likelihood
        return lnp

    # *** sample the {age, Mstar} posterior

    # assign the model grid
    grid = model_dict[grid_name](**config[grid_name])

    # initialize and run the EMCEE sampler
    sampler = EnsembleSampler(nwalkers, ndim, lnprob, args=[grid])
    pos, prob, state = sampler.run_mcmc(p0, ntrials)

    # flatten the resulting chain to give joint samples of {age, Mstar}
    ptauMstar = (sampler.chain[:,burn:,:]).reshape(-1, ndim)

    return ptauMstar
