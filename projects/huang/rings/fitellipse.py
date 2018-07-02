import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as col
from scipy.optimize import minimize
import sys
sys.path.append('/pool/firebolt1/p484/projects/huang/rings')
from continuumanalysis3 import Continuum
import emcee, corner
from matplotlib.patches import Ellipse

def lnlike(ellipse_params, x, y):
    """
    Parameters
    ==========
    ellipse_params: Tuple of ellipse parameters to fit for: x0, y0, r0, cosi, par, logvar
                    x0: x-offset in arcsec (Eastward offset is positive)
                    y0: y-offset in arcsec (Northward offset is positive)
                    r0: Radius of deprojected ring (arcsec)
                    cosi: Cosine of inclination
                    par: Position angle in radians (measured east of north)
                    logvar: Logarithm of variance of orthogonal distance from true ellipse (variance in arcsec^2)
    
    x: Array of x-coordinates to fit (in arcsec)
    y: Array of y-coordinates to fit (in arcsec)    
    
    Returns
    =======
    Log-likelihood of the data given the ellipse model
    """
    x0, y0, r0, cosi, par, logvar = ellipse_params
    assert len(x)==len(y)
    a = r0
    b = r0*cosi
    theta = par-np.pi/2.
    costheta = np.cos(theta)
    sintheta = np.sin(theta)
    A = (costheta/a)**2+(sintheta/b)**2
    B = -2*costheta*sintheta/a**2+2*costheta*sintheta/b**2
    C = (sintheta/a)**2+(costheta/b)**2
 
    e0 = B**2-4*A*C #scalar
    e1 = 2*B*e0 #scalar
    e2 = 2*C*e0*(y-y0) #vector
    e3 = 4*B*C #scalar
    e4 = B**2+4*C**2+e0 #scalar
    e5 = 2*C*(B*(y-y0)-2*C*(x-x0)) #vector
    f4 = e1**2-e0*e4**2 #scalar
    f3 = 2*e1*e2-2*e0*e4*e5 #vector
    f2 = e2**2+2*e1*e3-e0*e5**2-4*e4**2*C #vector
    f1 = 2*e2*e3-8*e4*e5*C #vector
    f0 = e3**2-4*e5**2*C #vector
    sumdsq = 0 #sum of the squared orthogonal distances from the model ellipse
    #find the point p on the ellipse such that the tangent line is orthogonal to the line connecting p and the datapoint
    for i in range(len(x)):
        dmin = 1.e10
        #we get a fourth-order polynomial, but only one of the roots corresponds to the actual distance (the real root that minimizes the distance)
        roots = np.roots(np.array([f4, f3[i], f2[i], f1[i], f0[i]]))

        for dx in roots[np.where(np.isreal(roots))].astype(np.float64):
            xi = (e1*dx**2+e2[i]*dx+e3)/(e4*dx+e5[i])
            dy = (-B*dx+xi)/(2*C)
            dist = np.sqrt((x[i]-x0-dx)**2+(y[i]-y0-dy)**2)
            if dist<dmin:
                dmin = dist       
        sumdsq+=dmin**2
    n = len(x)
    inv_sigma2 = 1.0/np.exp(logvar)
    return -0.5*(inv_sigma2*sumdsq - n*np.log(inv_sigma2))

def ellipse_mle(starting_guess, xcoord, ycoord, quiet = False):
    mle = minimize(lambda *args: -lnlike(*args), starting_guess, args = (xcoord, ycoord),method = 'Nelder-Mead')
    result = mle["x"]
    if not quiet:
        print("The MLE offsets are delta_x = %.3e arcsec, delta_y = %.3e arcsec" % (result[0], result[1]))
        print("The MLE semi-major axis is r = %.3f arcsec" % (result[2],))
        print("The MLE inclination is i = %.3f degrees" %(np.arccos(result[3])*180/np.pi,))
        print("The MLE position angle is PA = %.3f degrees" % (result[4]*180/np.pi,))
        print("The MLE log-variance in the pixel offsets from the true ellipse is %.3e" % (result[5],)) 
    return result

   
def run_mcmc(nwalkers, nthreads, nsteps, initial_pos, lnprob, xcoord, ycoord):
    ndim = 6
    starting_pos = [initial_pos + 1e-4*np.random.randn(ndim) for i in range(nwalkers)]

    sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob, args=(xcoord, ycoord), threads = nthreads)
    sampler.run_mcmc(starting_pos, nsteps)

    return sampler

def plot_corner(sampler, burnin, skip):
    ndim = sampler.chain.shape[2]
    samples = sampler.chain[:, burnin::skip, :].reshape((-1, ndim))
    fig = corner.corner(samples,  labels=["x0", "y0", "r0", "cosi", "par", "logvar"], quantiles = [0.16, 0.5, 0.84], show_titles = True, title_fmt = ".4f")
    plt.show()

def make_best_ellipse(samplers, burnin, skip, imagepath):
    for sampler in samplers:
        ndim = sampler.chain.shape[2]
        samples = sampler.chain[:, burnin::skip, :].reshape((-1, ndim))
        median = np.percentile(samples, 50,axis = 0)

def sampler_results(sampler, burnin, distance):
    samples = sampler.chain[:, burnin:, :].reshape((-1, 6))
    median = np.percentile(samples, 50, axis = 0)
    sixteenth = np.percentile(samples, 16, axis = 0)
    eightyfourth = np.percentile(samples, 84, axis = 0)
    
    print("The x offset is delta_x = %.2e arcsec (+%.1e, -%.1e)"  % (median[0], eightyfourth[0]-median[0], median[0]-sixteenth[0]))
    print("The y offset is delta_y = %.2e arcsec (+%.1e, -%.1e)" % (median[1], eightyfourth[1]-median[1], median[1]-sixteenth[1]))
    print("The median semi-major axis is r = %.4f arcsec (+%.4f, -%.4f) \nor %.2f AU (+%.2f, -%.2f)" % 
          (median[2],eightyfourth[2]-median[2], median[2]-sixteenth[2],median[2]*distance,distance*(eightyfourth[1]-median[1]), distance*(median[1]-sixteenth[1])))
    print("The incl is i = %.2f deg (+%.2f, -%.2f)" %(np.arccos(median[3])*180/np.pi,(np.arccos(sixteenth[3])-np.arccos(median[3]))*180/np.pi,(np.arccos(median[3])-np.arccos(eightyfourth[3]))*180/np.pi))
    print("The median position angle is PA = %.2f deg (+%.2f, -%.2f)" % (median[4]*180/np.pi,eightyfourth[4]*180/np.pi-median[4]*180/np.pi,median[4]*180/np.pi-sixteenth[4]*180/np.pi))
    print("The median log-variance in the pixel offsets from the true ellipse is %.3e" % (median[5],)) 

def find_profile_extrema(radbins, radprofile, extrema = 'max'):    
    grad = np.gradient(radprofile)
    if extrema=='max':
        sgn_chg = np.where((np.sign(grad[:-1])!=np.sign(grad[1:])) & (np.sign(grad[:-1])>0))[0]
    else:
        sgn_chg = np.where((np.sign(grad[:-1])!=np.sign(grad[1:])) & (np.sign(grad[:-1])<0))[0]
    locs = []
    for i in sgn_chg:
        if np.abs(grad[i])>np.abs(grad[i+1]):
            locs.append(i+1)
        else:
            locs.append(i)
    return locs
        
