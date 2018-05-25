import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy import convolve
import scipy.ndimage
from images import *
from interactive_plot import *
import emcee

def ellipsepath(t,params):
    r0   = params[0]
    incl = params[1]*np.pi/180.
    phi0 = params[2]*np.pi/180.
    x    = np.cos(t-phi0)
    y    = np.sin(t-phi0)/np.cos(incl)
    xp   = r0/np.sqrt(x**2+y**2)
    yp   = t*180./np.pi
    return xp,yp

def imagepath(xp,yp):
    xpp    = (xp/rmax)*image.shape[1]
    ypp    = (yp/360.)*image.shape[0]
    impath = scipy.ndimage.map_coordinates(image, np.vstack((ypp,xpp)))
    return impath

def func_widget(t,params):
    xp,yp     = ellipsepath(t,params)
    impath    = imagepath(xp,yp)
    return np.vstack((xp,yp)),np.vstack((yp,impath))

def func_mcmc(t,params):
    xp,yp     = ellipsepath(t,params)
    impath    = imagepath(xp,yp)
    impathav  = impath.sum()/len(impath)
    impathsig = (((impath-impathav)**2).sum()/len(impath))**0.5
    sigtotal = impathsig/np.sqrt(nr_of_beams)
    return -0.5*likelihoodboost*(impathav-intmodel_guess)**2/sigtotal**2

def lnprior(params):
    for ipar in range(len(params)):
        if params[ipar]<=params_lims[ipar][0] or params[ipar]>=params_lims[ipar][1]:
            return -np.inf
    return 0.0

def lnlike(params,image,rmax):
    lnlike = func_mcmc(np.linspace(0,np.pi*2,ntpath),params)
    print(params,lnlike)
    return lnlike

def lnprob(params,image,rmax):
    lp = lnprior(params)
    if not np.isfinite(lp):
        return -np.inf
    return lp + lnlike(params,image,rmax)

#-------------------------------------------------------------------------------
    
name     = 'GW_Lup'

findpeak = True         # If we wish to find a local maximum
#findpeak = False        # If we wish to find a local minimum

likelihoodboost = 2.0   # Sometimes it can be useful to make this e.g. 2.0 or 4.0 to get stronger constraint

#
# Message
#
if findpeak:
    print('Find a ring-shaped PEAK')
else:
    print('Find a ring-shaped GAP')

#
# Extract radial image from fits
#
s=raw_input('Recompute (r,phi) image (y/n)? ')
if s=='y' or s=='Y':
    nphi       = 361
    phi_offset = 0.
    filename   = name+'_script_image.fits'
    q          = continuumimage(filename,src_distance=dpc)
    q.convert_to_circular(leng=500,nphi=nphi,phi_offset=phi_offset)
    q.save_circular(name)

#
# Read the radial image in
#
a = circularimage(name)
floorvalue = 1e-3*a.circim.max()
a.circim[a.circim<floorvalue] = floorvalue

#
# The image to display in the widget
#
image = a.circim
rmax  = a.ras[-1]

#
# For the widget: define the parameter names, the ranges of the sliders and the starting values
#
parnames = ['r0 = ','incl = ','phi0 = ']
params   = [np.linspace(0,rmax,300),np.linspace(0.,90.,300),np.linspace(0.,180.,300)]
parstart = [0.55,38.,142.]

#
# A few calculations and settings
#
beam_fwhm_as   = 35e-3     # FWHM OF BEAM IN ARCSEC  *** CHECK ***
nr_of_beams    = 2*np.pi*parstart[0]/beam_fwhm_as
ntpath         = 100
intmodel_guess = 0.

#
# Spawn the widget
#
fig, axes = plt.subplots(nrows=2)
axes[0].set_xlim((0,a.ras[-1]))
axes[0].set_ylim((0,360))
axes[1].set_xlim((0,360.))
axes[1].set_ylim((1e-3*a.circim.max(),1e-1*a.circim.max()))
axd      = axes[0].imshow(np.log10(a.circim),aspect='auto',extent=[0,a.ras[-1],360,0])  # Note: due to 360,0 no origin='lower' needed
axes[0].set_xlabel(r'$r$ [arcsec]')
axes[0].set_ylabel(r'$\phi$ [degrees]')
t        = np.linspace(0,2*np.pi,ntpath)
ax1,     = axes[0].plot(np.zeros_like(t),t*180./np.pi,color='red',linewidth=2)
impath   = np.zeros_like(t)
ax2,     = axes[1].plot(t*180./np.pi,impath)
plt.xlabel(r'$\phi$ [degrees]')
plt.ylabel(r'$I_\nu [\mathrm{CGS}]$')
plt.yscale('log')
axmodel  = [ax1,ax2]
plt.show()
ipar = interactive_curve(t, func_widget, params, parnames=parnames,parstart=parstart,axmodel=axmodel,fig=fig,ax=axes[0],returnipar=True)

#
# Now extract the parameter values
#
params_start = [params[i][ipar[i]] for i in range(len(ipar))]

params_fit   = params_start

#
# Compute an estimate of the intmodel_guess (the model integral of intensity along the path)
#
xp,yp     = ellipsepath(t,params_start)
impath    = imagepath(xp,yp)
impathav  = impath.sum()/len(impath)
impathsig = (((impath-impathav)**2).sum()/len(impath))**0.5
if findpeak:
    intmodel_guess = impathav + impathsig    # For a bump
else:
    intmodel_guess = impathav - impathsig    # For a valley
if intmodel_guess<0.: intmodel_guess=0.

#
# Now guesstimate the range within which we wish to MCMC
#
r0           = params_start[0]
params_lims  = np.array([(0.8*r0,1.1*r0),(20.,50.),(0.,180.)])

#
# The half-width of the random population in each of the parameters
#
params_dran  = np.array([1e-2*params_start[0],10.,20.])
for ipar in range(len(params_start)):
    assert params_start[ipar]-params_dran[ipar]>params_lims[ipar][0] and params_start[ipar]+params_dran[ipar]<params_lims[ipar][1]

#
# Prepare the MCMC walkers
#
nwalkers       = 10
nsteps         = 500
ndump          = 250
ndim           = len(params_start)
pos            = [params_start + params_dran[:]*(2*np.random.rand(ndim)-1) for i in range(nwalkers)]
sampler        = emcee.EnsembleSampler(nwalkers, ndim, lnprob, args=([image,rmax]))

#
# Now run the MCMC chain
#
sampler.run_mcmc(pos, nsteps)
samples        = sampler.chain[:, ndump:, :].reshape((-1, ndim))

#
# Triangle plot
#
import corner
fig3 = corner.corner(samples, labels=['r0','incl','phi0'],plot_contours=False)
plt.show()
plt.savefig(name+'_cornerplot_r_incl_pa.pdf')

#
# Find the best fit parameters
#
q             = np.percentile(samples, [16, 50, 84], axis=0)
params_fit    = q[1]
#params_errneg = q[1]-q[0]
#params_errpos = q[2]-q[1]

#
# Compute the curve for this
#
tt            = np.linspace(0,np.pi*2,a.circim.shape[0])
xp,yp         = ellipsepath(tt,params_fit)

#
# Plot the resulting fit
#
fig, ax = plt.subplots(nrows=1)
ax.set_xlim((0,a.ras[-1]))
ax.set_ylim((0,360))
axd      = ax.imshow(np.log10(a.circim),aspect='auto',extent=[0,a.ras[-1],360,0])  # Note: due to 360,0 no origin='lower' needed
ax.set_xlabel(r'$r$ [arcsec]')
ax.set_ylabel(r'$\phi$ [degrees]')
ax1,     = ax.plot(xp,yp,color='red',linewidth=2)
plt.savefig(name+'_radialimage.pdf')

#
# Now rescale the radial image to deproject
#
rpeak  = xp
rpeak0 = rpeak[:].max() 
factor = rpeak / rpeak0
a.radial_rescale(factor)
floorvalue = 1e-3*a.circim.max()
a.circim_rescaled[a.circim_rescaled<floorvalue] = floorvalue

#
# Plot the rescaled image
#
fig, ax = plt.subplots(nrows=1)
ax.set_xlim((0,a.ras[-1]))
ax.set_ylim((0,360))
axd      = ax.imshow(np.log10(a.circim_rescaled),aspect='auto',extent=[0,a.ras[-1],360,0])
plt.xlabel(r'$r$ [arcsec] (rescaled)')
plt.ylabel(r'$\phi$ [degrees]')
plt.savefig(name+'_radialimage_deproj.pdf')

# Now average over phi
a.circim_average = a.circim_rescaled.sum(axis=0)/a.nphi
a.circim_average[a.circim_average<=0.] = 1e-90

# Convert to T_bright (linear and full version)
tbright_linear = get_tbright(a.circim_average,a.freq,linear=True)
tbright_full   = get_tbright(a.circim_average,a.freq,linear=False)

# Now find rms
a.circim_rms = np.zeros_like(a.circim_average)
for ir in range(a.nr):
    a.circim_rms[ir] = np.sqrt(((a.circim_rescaled[:,ir]-a.circim_average[ir])**2).sum()/a.nphi)
a.circim_rms = a.circim_rms/a.circim_average
a.circim_rms[a.circim_rms>1e3] = 0.
a.circim_rms_tbright = a.circim_rms*tbright_linear

# Now compute the error
nbeams    = 2*np.pi*a.ras/beam_fwhm_as
nbeams[nbeams<1.0] = 1.0
a.circim_error_tbright = a.circim_rms_tbright / np.sqrt(nbeams)

# Write the linear brightness temperature
au  = 1.49598e13     # Astronomical Unit       [cm]
with open(name+'_radial_tbright_linear.txt','w') as f:
    f.write('# r[au]  T_bright_linear [K]   Variance [K]   Error [K]\n')
    for ir in range(a.nr):
        f.write('{0:e} {1:e} {2:e} {3:e}\n'.format(a.ras[ir]*a.src_distance,tbright_linear[ir],a.circim_rms_tbright[ir],a.circim_error_tbright[ir]))

# Write the non-linear brightness temperature (w/o error, since this is non-linear)
with open(name+'_radial_tbright.txt','w') as f:
    f.write('# r[au]  T_bright_nonlin [K]\n')
    for ir in range(a.nr):
        f.write('{0:e} {1:e}\n'.format(a.ras[ir]*a.src_distance,tbright_full[ir]))

# Plot
plt.figure()
plt.plot(a.ras*a.src_distance,tbright_linear,'k-')
plt.fill_between(a.ras*a.src_distance,tbright_linear-a.circim_rms_tbright,tbright_linear+a.circim_rms_tbright,color='beige')
plt.fill_between(a.ras*a.src_distance,tbright_linear-a.circim_error_tbright,tbright_linear+a.circim_error_tbright,color='coral')
plt.xlabel(r'$r$ [au]')
plt.ylabel(r'$T_{\mathrm{bight,lin}}$ [K]')
plt.xlim(xmin=0,xmax=140)
plt.ylim(ymin=1e-1,ymax=1e1)
plt.yscale('log')
plt.savefig(name+'_radial_tbright_logscale.pdf')
plt.show()

plt.figure()
plt.plot(a.ras*a.src_distance,tbright_linear,'k-')
plt.fill_between(a.ras*a.src_distance,tbright_linear-a.circim_rms_tbright,tbright_linear+a.circim_rms_tbright,color='beige')
plt.fill_between(a.ras*a.src_distance,tbright_linear-a.circim_error_tbright,tbright_linear+a.circim_error_tbright,color='coral')
plt.xlabel(r'$r$ [au]')
plt.ylabel(r'$T_{\mathrm{bight,lin}}$ [K]')
plt.xlim(xmin=0,xmax=140)
plt.ylim(ymin=0,ymax=1e1)
plt.savefig(name+'_radial_tbright_linscale.pdf')
plt.show()
