import numpy as np
import os
import sys
import time
from scipy import stats
from scipy import special
from astropy.io import ascii
from plx_dist import plx_dist
from lt_taum import lt_taum



# I/O
ioname    = 'leftovers'
sample_id = 1
inp       = ascii.read(ioname+'.inp')


# HARD-CODED SETUPS

# stellar posterior sampling
nburn = 5000
nwalk = 10
nsamples_star = 30000
ntrials = nsamples_star + nburn

# confidence intervals
CI_levs = [84.135, 15.865, 95.45, 4.55]

# opacities
kap0 = 3.4
nu0  = 340.
bet  = 1.

# MIPS setups
sigma_mips = 0.1
mips_star_scaling = 2.8

# GAIA DR2 systematics
sys_plx = 0.1		# mas
shift_plx = 0.03 	# mas

# constants
Lsun   = 3.826e33
sigSB  = 5.67051e-5
sec_yr = 3.155815e7
G      = 6.67259e-8
Msun   = 1.989e33
hh     = 6.6260755e-27
kk     = 1.380658e-16
cc     = 2.99792548e10
parsec = 3.0857e18


# LOAD INPUT DATA

# identification
iname = inp['iname']

# parallax
parallax  = inp['varpi']
eparallax = inp['evarpi']

# host effective temperature and luminosity
sflag  = inp['sflag']		# 1 = M ul; 2 = M ll, 3 = t ul, 4 = t ll, 
                                # 9 = no data
Teff   = inp['Teff']            # if stype = 'log', then log(Teff)
eTeff  = inp['eTeff']
Lstar  = inp['Lstar']		# if stype = 'log', then log(Lstar)
eLstar = inp['eLstar']		# (at presumed distance, d_inp)
ttype  = inp['Ttype']
ltype  = inp['Ltype']

# accretion luminosity
aflag    = inp['aflag']         # 1 = Lacc ul; 2 = Lacc ll, 9 = no data 
logLacc  = inp['logLacc']	# (at presumed distance, d_inp)
elogLacc = inp['elogLacc']

# presumed distance for stellar properties
d_inp = inp['d_inp']


# MAIN LOOP
#os.system('rm -rf datafiles/'+ioname+'.summary.dat')
for i in range(len(iname)):	#len(iname)):

    # INITIAL BOOK-KEEPING
    # record source names
    iname_str = '%11s  ' % iname[i]
    print(iname[i])

    # store the number of disk-related posterior samples
    nsamples = 50000
 
    # CALCULATE DISTANCES AND RE-SCALE TO PHYSICAL COORDINATES
    pdist = plx_dist(parallax[i]+shift_plx, np.sqrt(eparallax[i]**2+sys_plx**2), nsamples=nsamples)
    CI_dist  = np.percentile(pdist, CI_levs)
    kde_dist = stats.gaussian_kde(pdist)
    ndisc = np.round((CI_dist[0] - CI_dist[1]) / 0.1)
    x_dist   = np.linspace(CI_dist[1], CI_dist[0], ndisc)
    pk_dist  = x_dist[np.argmax(kde_dist.evaluate(x_dist))]

    # record strings for output
    plx_str  = '%6.3f  %6.3f  ' % (parallax[i], eparallax[i])
    dist_str = '%5.1f  %5.1f  %5.1f  ' % \
               (pk_dist, CI_dist[0]-pk_dist, pk_dist-CI_dist[1])

    # CALCULATE STELLAR HOST PROPERTIES
    sflag_str = '%1i  ' % (sflag[i])
    if (sflag[i] != 9):
        # compute Teff and log(Teff)
        if (ttype[i] == 0):
            pTeff = np.random.normal(Teff[i], eTeff[i], nsamples)
            plogTeff = np.log10(pTeff)
        else:
            plogTeff = np.random.normal(Teff[i], eTeff[i], nsamples)
            pTeff = 10.**(plogTeff)
        CI_logTeff  = np.percentile(plogTeff, CI_levs)
        kde_logTeff = stats.gaussian_kde(plogTeff)
        ndisc = np.round((CI_logTeff[0] - CI_logTeff[1]) / 0.001)
        x_logTeff   = np.linspace(CI_logTeff[1], CI_logTeff[0], ndisc)
        pk_logTeff  = x_logTeff[np.argmax(kde_logTeff.evaluate(x_logTeff))]

        # compute Lstar and log(Lstar)
        if (ltype[i] == 0):
            plogLstar = np.random.normal(np.log10(Lstar[i]), eLstar[i] / \
                        Lstar[i] / np.log(10), nsamples) + \
                        2.*np.log10(pdist / d_inp[i])
            pLstar = 10.**(plogLstar)
        else:
            plogLstar = np.random.normal(Lstar[i], eLstar[i], nsamples) + \
                        2.*np.log10(pdist / d_inp[i])
            pLstar = 10.**(plogLstar)
        CI_logLstar  = np.percentile(plogLstar, CI_levs)
        kde_logLstar = stats.gaussian_kde(plogLstar)
        ndisc = np.round((CI_logLstar[0] - CI_logLstar[1]) / 0.01)
        x_logLstar   = np.linspace(CI_logLstar[1], CI_logLstar[0], ndisc)
        pk_logLstar  = x_logLstar[np.argmax(kde_logLstar.evaluate(x_logLstar))]

        # compute a restricted set of {age, Mstar} posterior samples
        ptauMstar = lt_taum(pTeff[:ntrials], plogLstar[:ntrials], 
                            grid_name='MIST', ntrials=ntrials, burn=nburn, 
                            nwalkers=nwalk)
        plogAGE      = ptauMstar[:,0]	
        plogMstar    = ptauMstar[:,1]	
        CI_logAGE    = np.percentile(plogAGE, CI_levs)
        kde_logAGE   = stats.gaussian_kde(plogAGE)
        ndisc = np.round((CI_logAGE[0] - CI_logAGE[1]) / 0.01)
        x_logAGE     = np.linspace(CI_logAGE[1], CI_logAGE[0], ndisc)
        pk_logAGE    = x_logAGE[np.argmax(kde_logAGE.evaluate(x_logAGE))]
        CI_logMstar  = np.percentile(plogMstar, CI_levs)
        kde_logMstar = stats.gaussian_kde(plogMstar)
        ndisc = np.round((CI_logMstar[0] - CI_logMstar[1]) / 0.01)
        x_logMstar   = np.linspace(CI_logMstar[1], CI_logMstar[0], ndisc)
        pk_logMstar  = x_logMstar[np.argmax(kde_logMstar.evaluate(x_logMstar))]

        # record strings for output
        Teff_str = '%5.3f  %5.3f  %5.3f  ' % (pk_logTeff, 
                   CI_logTeff[0]-pk_logTeff, pk_logTeff-CI_logTeff[1])
        if (pk_logLstar < 0.0):
            Lstar_str = '%5.2f  %4.2f  %4.2f  ' % (pk_logLstar, 
                        CI_logLstar[0]-pk_logLstar, pk_logLstar-CI_logLstar[1])
        else: Lstar_str = ' %4.2f  %4.2f  %4.2f  ' % (pk_logLstar,
                        CI_logLstar[0]-pk_logLstar, pk_logLstar-CI_logLstar[1])
        AGE_str = '%4.2f  %4.2f  %4.2f  ' % (pk_logAGE, CI_logAGE[0]-pk_logAGE,
                  pk_logAGE-CI_logAGE[1])
        if ((sflag[i] != 4) & (sflag[i] != 3)): limAGE_str = '   0  '
        if (sflag[i] == 3):
            limAGE_str = '%4.2f  ' % CI_logAGE[2]
        if (sflag[i] == 4):
            limAGE_str = '%4.2f  ' % CI_logAGE[3]
        if (pk_logMstar < 0.0):
            Mstar_str = '%5.2f  %4.2f  %4.2f  ' % (pk_logMstar,
                        CI_logMstar[0]-pk_logMstar, pk_logMstar-CI_logMstar[1])
        else: Mstar_str = ' %4.2f  %4.2f  %4.2f  ' % (pk_logMstar,
                        CI_logMstar[0]-pk_logMstar, pk_logMstar-CI_logMstar[1])
        if (sflag[i] == 1): 
            if (CI_logMstar[2] < 0.0):
                limMstar_str = '%5.2f  ' % CI_logMstar[2]
            else: limMstar_str = ' %4.2f  ' % CI_logMstar[2]
        if (sflag[i] == 2): 
            if (CI_logMstar[3] < 0.0):
                limMstar_str = '%5.2f  ' % CI_logMstar[3]
            else: limMstar_str = ' %4.2f  ' % CI_logMstar[3]
        if ((sflag[i] != 1) & (sflag[i] != 2)): limMstar_str = '    0  '
       
        # compute accretion rate (logMdot)
        if (aflag[i] != 9):
            # compute Lacc posterior draws
            if (aflag[i] == 0):       # Lacc measurement
                Lacc = 10.**np.random.normal(logLacc[i], elogLacc[i], nsamples)
            if (aflag[i] == 1):       # Lacc upper limit
                rL = np.linspace(-4, 1, num=1e4)
                disc_L = special.erfc((rL-logLacc[i]) / elogLacc[i])
                prob_L = disc_L / np.sum(disc_L)
                Lacc = 10.**np.random.choice(rL, nsamples, p=prob_L)
            pLacc = Lacc * (pdist / d_inp[i])**2

            # calculate stellar radii
            Rstar = np.sqrt(pLstar*Lsun / (4.*np.pi*sigSB*pTeff**4.))

            # draw stellar masses from posteriors
            pMstar = 10.**(plogMstar[np.random.random_integers(0, 
                                     len(plogMstar)-1, size=nsamples)])

            # calculate logMdot 
            Mdot = 1.25 * Rstar * pLacc * Lsun / (G * pMstar * Msun)
            plogMdot = np.log10(Mdot * sec_yr / Msun)

            # there are different scenarios for the logMdot inference:
            # if aflag = 1, Mdot is an upper limit
            # if aflag = 0, but sflag = 1, Mdot is a *lower* limit
            # if aflag = 0, but sflag = 2, Mdot is an *upper* limit
            CI_logMdot  = np.percentile(plogMdot, CI_levs)
            kde_logMdot = stats.gaussian_kde(plogMdot)
            ndisc = np.round((CI_logMdot[0] - CI_logMdot[1]) / 0.01)
            x_logMdot   = np.linspace(CI_logMdot[1], CI_logMdot[0], ndisc)
            pk_logMdot  = x_logMdot[np.argmax(kde_logMdot.evaluate(x_logMdot))]

            # record strings for output
            if (pk_logMdot <= -10.0):
                Mdot_str = '%6.2f  %4.2f  %4.2f  ' % (pk_logMdot, 
                           CI_logMdot[0]-pk_logMdot, pk_logMdot-CI_logMdot[1])
            else:
                Mdot_str = ' %5.2f  %4.2f  %4.2f  ' % (pk_logMdot, 
                           CI_logMdot[0]-pk_logMdot, pk_logMdot-CI_logMdot[1])
            if ((aflag[i] == 1) or ((aflag[i] == 0) & (sflag[i] == 2))):
                if (CI_logMdot[2] <= -10.0):
                    limMdot_str = '  1  %6.2f  ' % CI_logMdot[2]
                else: limMdot_str = '  1   %5.2f  ' % CI_logMdot[2]
            if ((aflag[i] == 0) & (sflag[i] == 1)):
                if (CI_logMdot[3] <= -10.0):
                    limMdot_str = '  2  %6.2f  ' % CI_logMdot[3]
                else: limMdot_str = '  2   %5.2f  ' % CI_logMdot[3]
            if ((aflag[i] == 0) & (sflag[i] != 1) & (sflag[i] != 2)):
                limMdot_str = '  0       0  '

        else: 
            Mdot_str    = '     0     0     0  '
            limMdot_str = '  9       0  '

    else:
        Teff_str     = '    0      0      0  '
        Lstar_str    = '    0     0     0  '
        Mstar_str    = '    0     0     0  '
        limMstar_str = '    0  '
        AGE_str      = '   0     0     0  '
        limAGE_str   = '   0  '
        Mdot_str     = '     0     0     0  '
        limMdot_str  = '  0       0  '


    # OUTPUTS

    # write out the posterior summary table file
    f = open(ioname+'.summary.dat', 'a')
    f.write(iname_str + sflag_str +
            plx_str + dist_str + Teff_str + Lstar_str + Mstar_str +
            limMstar_str + AGE_str + limAGE_str + Mdot_str + limMdot_str)
    f.write('\n')
    f.close()

    # save the posterior draws for everything together
    os.system('rm -rf posteriors/'+iname[i]+'.uberpost.npz')
    if ((sflag[i] != 9) & (aflag[i] != 9)):
        np.savez('posteriors/'+iname[i]+'.uberpost.npz', d=pdist, logTeff=plogTeff, logLstar=plogLstar, logAGE=plogAGE, logMstar=plogMstar, logMdot=plogMdot)
    if ((sflag[i] != 9) & (aflag[i] == 9)):
        np.savez('posteriors/'+iname[i]+'.uberpost.npz', d=pdist, logTeff=plogTeff, logLstar=plogLstar, logAGE=plogAGE, logMstar=plogMstar)
    if (sflag[i] == 9):
        np.savez('posteriors/'+iname[i]+'.uberpost.npz', d=pdist) 
