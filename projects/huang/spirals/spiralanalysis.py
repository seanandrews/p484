import numpy as np
import sys
sys.path.append('/pool/firebolt1/p484/projects/huang/rings')
from continuumanalysis3 import Continuum
import matplotlib.pyplot as plt

import emcee, corner

def logspiral(theta, r0, b):
    return r0*np.exp(b*theta)


def archspiral(theta, a, c):
    return a+c*theta

def transform_spiral(thetavals, rvals, distance, PA, incl):
    
    xpvals = rvals*np.cos(thetavals)*np.cos(incl*np.pi/180.)/distance
    ypvals = rvals*np.sin(thetavals)/distance
    PAr = PA*np.pi/180.
    xvals = (xpvals*np.cos(-PAr)-ypvals*np.sin(-PAr))
    yvals = xpvals*np.sin(-PAr)+ypvals*np.cos(-PAr)
    return np.vstack((xvals, yvals)).T


def estimate_errors(cont, xvals, yvals, rvals):
    sigma = cont.bmaj/2.3548*cont.src_distance
    multiplier = rvals/np.sqrt(xvals**2+yvals**2)*1/cont.src_distance
    return sigma*multiplier

def lnlike(spiral_params, thetavals, rvals,sig, spiraltype = 'log'):
    inv_sigma2 = 1.0/sig**2
    if spiraltype=='log':
        modelvals = logspiral(thetavals, spiral_params[0],spiral_params[1])
    elif spiraltype=='archimedean':
        modelvals = archspiral(thetavals, spiral_params[0],spiral_params[1])
    return -0.5*(np.sum(inv_sigma2*(rvals-modelvals)**2 - np.log(inv_sigma2)))

  
def run_mcmc(nwalkers, nthreads, nsteps, initial_pos, lnprob, rvals,thetavals, errs):
    ndim = 2
    starting_pos = [initial_pos + 1e-2*np.random.randn(ndim) for i in range(nwalkers)]

    sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob, args=(thetavals, rvals, errs), threads = nthreads)
    sampler.run_mcmc(starting_pos, nsteps)
    return sampler
    
def plot_corner(sampler, burnin, skip, spiraltype = 'log'):
    ndim = sampler.chain.shape[2]
    samples = sampler.chain[:, burnin::skip, :].reshape((-1, ndim))
    if spiraltype=='log':
        fig = corner.corner(samples,  labels=["r0", "b"], quantiles = [0.16, 0.5, 0.84], show_titles = True, title_fmt = ".4f")
    elif spiraltype=='archimedean':
        fig = corner.corner(samples,  labels=["a", "c"], quantiles = [0.16, 0.5, 0.84], show_titles = True, title_fmt = ".4f")
    plt.show(block = False)
    return samples

def draw_from_posterior(flattened, ndraws):
    indices = np.random.randint(0, len(flattened)-1, ndraws)
    return flattened[indices]
    
    
