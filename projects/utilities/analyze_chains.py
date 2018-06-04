import numpy as np
import matplotlib.pyplot as plt

# function to compare autocorrelations
def gelman_rubin(chain):
    ssq = np.var(chain, axis=1, ddof=1)
    W = np.mean(ssq, axis=0)
    thetab = np.mean(chain, axis=1)
    thetabb = np.mean(thetab, axis=0)
    m = chain.shape[0]
    n = chain.shape[1]
    B = n / (m - 1) * np.sum((thetabb - thetab)**2, axis=0)
    var_theta = (n - 1) / n * W + 1 / n * B
    Rhat = np.sqrt(var_theta / W)
    return Rhat

# make a plot to track Gelman-Rubin statistic with iteration

# this presumes you load your walkers from 'emcee' somehow into an array called
# chain.  If the following dimensionality doesn't make sense, something's wrong
# this thing called "chain" is the same thing as 'sampler.chain' you 
# would get using emcee is you ran:
# sampler = emcee.EnsembleSampler(nwalk, ndim, lnprob)
# for some lnprob objective function.
nwalk, niter, ndim = chain.shape[0], chain.shape[1], chain.shape[2]

# define the steps where you want to calculate autocorrelations (e.g. is for 
# every 100 posterior samples)
nsamples_per_point = 100
xmin = 100
step_sampling = np.arange(xmin, niter, nsamples_per_point)

# make a plot of rhat versus accumulated samples
fig = plt.figure(figsize=(5.5, 5))
plt.axis([0, niter, 1.0, 2.0])
for idim in range(ndim-2):
    rhat = [gelman_rubin(chain[:, :steps, idim]) for steps in step_sampling]
    plt.plot(step_sampling, rhat)
plt.plot([0, niter], [1.1, 1.1], '--k')
fig.savefig('analyze_chains.png')
fig.clf()

# so the goal is that this plot shows *all* the curves consistently below 
# a value of 1.1.  If that's *not true*, your chains are not converged.  But, 
# if that *is true*, it does not necessarily mean the chains are converged 
# although it would need to be pathological if that's a problem).  

# There are other tests one could do, but I feel like this is a pretty 
# straightforward necessary (if not sufficient) one.
