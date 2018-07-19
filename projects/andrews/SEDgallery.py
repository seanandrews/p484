import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from astropy.io import ascii
from starspectrum import starspectrum
from deredden import deredden

show_median = True

names = ['HTLup', 'GWLup', 'IMLup', 'HD142666', 'RULup',
         'HD143006', 'Sz129', 'MYLup', 'Sz114', 'AS205',
         'SR4', 'Elias20', 'DoAr25', 'Elias24', 'Elias27',
         'DoAr33', 'WSB52', 'WaOph6', 'AS209', 'HD163296']

labels = [r'${\rm HT \;\: Lup}$', r'${\rm GW \;\: Lup}$', 
          r'${\rm IM \;\: Lup}$', r'${\rm HD \;\: 142666}$', 
          r'${\rm RU \;\: Lup}$', r'${\rm HD \;\: 143006}$', 
          r'${\rm Sz \;\: 129}$', r'${\rm MY \;\: Lup}$', 
          r'${\rm V908 \;\: Sco}$', r'${\rm AS \;\: 205}$',
          r'${\rm SR \;\: 4}$', r'${\rm Elias \;\: 20}$', 
          r'${\rm DoAr \;\: 25}$', r'${\rm Elias \;\: 24}$', 
          r'${\rm Elias \;\: 27}$', r'${\rm DoAr \;\: 33}$', 
          r'${\rm WSB \;\: 52}$', r'${\rm WaOph \;\: 6}$', 
          r'${\rm AS \;\: 209}$', r'${\rm HD \;\: 163296}$']

dpc = np.array([154., 155., 158., 148., 159.,
                165., 161., 156., 162., 128., 
                134., 138., 138., 136., 116.,
                139., 136., 123., 131., 101.])

Teff = 10.**(np.array([3.69, 3.56, 3.63, 3.88, 3.61,
                       3.75, 3.61, 3.71, 3.50, 3.63,
                       3.61, 3.59, 3.63, 3.63, 3.59,
                       3.65, 3.57, 3.62, 3.63, 3.97]))

Lstar = 10.**(np.array([ 0.74, -0.40,  0.31,  0.96,  0.16,
                         0.58, -0.26,  0.16, -0.69,  0.33, 
                         0.07,  0.35, -0.02,  0.78, -0.04,
                         0.18, -0.15,  0.46,  0.15,  1.23]))

Av = np.array([ 1.0,  0.5,  0.9,  0.5,  0.0, 
                0.6,  0.9,  1.3,  0.3,  2.4,
                1.3, 14.0,  2.5,  8.7, 15.0,
                3.7,  5.0,  3.6,  0.5,  0.0])

xlims = [0.2, 5000.]
ylims = [-6.0, 1.8]

fig = plt.figure(figsize=(7.5, 4.5))
gs = gridspec.GridSpec(4, 5)

for i in range(len(names)):

    # set up the plot
    ax = fig.add_subplot(gs[np.floor_divide(i,5),i%5])
    ax.set_xlim(xlims)
    ax.set_xscale('log')
    ax.set_ylim(ylims)

    # load the spectrum data
    sed  = ascii.read('SEDs/'+names[i]+'.SED.txt')
    wl   = sed['col1']
    nu   = 2.9979e14 / wl
    Fnu  = sed['col2']
    eFnu = np.sqrt(sed['col3']**2 + (sed['col4']*Fnu)**2)

    # convert to SED units (in log luminosity density)
    Lnu  = 1e-23 * 4. * np.pi * (dpc[i] * 3.0857e18)**2 * nu * Fnu / 3.826e33
    Lnu *= deredden(wl, Av[i], thresh=1.0)
    eLnu = 1e-23 * 4. * np.pi * (dpc[i] * 3.0857e18)**2 * nu * eFnu / 3.826e33
    SED  = np.log10(Lnu)
    eSEDlo = SED - np.log10(Lnu - eLnu)
    eSEDhi = np.log10(Lnu + eLnu) - SED

    # overplot the (properly extincted) stellar spectrum
    swl, sFnu = starspectrum(Teff[i], Lstar[i], dpc=dpc[i])
    snu  = 2.9979e14 / swl
    sLnu = 1e-23*4.*np.pi*(dpc[i]*3.0857e18)**2*snu*sFnu/3.826e33
    sSED = np.log10(sLnu)
    ax.plot(swl, sSED, 'r', linewidth=0.8, alpha=0.5)

    # if you want to show median SED, do so
    if (show_median == True):
        ribas = ascii.read('SEDs/ribas_median.SED.txt')
        rwl, rlo, rmed, rhi = ribas['col1'], ribas['col2'], ribas['col3'], \
                              ribas['col4']
        rnu = 2.9979e14 / rwl
        FtargJ = Fnu[wl == 1.235] * deredden([1.235], Av[i], thresh=1.0)
        Flo, Fhi = rlo * FtargJ[0], rhi * FtargJ[0]
        Llo = 1e-23*4.*np.pi*(dpc[i] * 3.0857e18)**2 * rnu * Flo / 3.826e33
        Lhi = 1e-23*4.*np.pi*(dpc[i] * 3.0857e18)**2 * rnu * Fhi / 3.826e33
        SEDlo, SEDhi = np.log10(Llo), np.log10(Lhi)
        ax.fill_between(rwl, SEDlo, SEDhi, facecolor='green', interpolate=True)

    # if an IRS or ISO spectrum is available, plot it
    if (os.path.isfile('SEDs/'+names[i]+'.IRS.txt') == True):
        irs = ascii.read('SEDs/'+names[i]+'.IRS.txt')
        iwl, iFnu  = irs['col2'], irs['col3']
        inu  = 2.9979e14 / iwl
        iLnu = 1e-23 *4.*np.pi*(dpc[i] * 3.0857e18)**2*inu*iFnu / 3.826e33
        iLnu *= deredden(iwl, Av[i], thresh=1.0)
        iSED = np.log10(iLnu)
        ax.plot(iwl, iSED, 'gray')
#    if (os.path.isfile('SEDs/'+names[i]+'.ISO.txt') == True):
#        iso = ascii.read('SEDs/'+names[i]+'.ISO.txt')
#        iwl, iFnu  = iso['lambda'], iso['Flux']
#        inu  = 2.9979e14 / iwl
#        iLnu = 1e-23 *4.*np.pi*(dpc[i] * 3.0857e18)**2*inu*iFnu / 3.826e33
#        iLnu *= deredden(iwl, Av[i], thresh=1.0)
#        iSED = np.log10(iLnu)
#        ax.plot(iwl, iSED, 'gray')

    # plot the SED with associated errorbars
    ax.errorbar(wl, SED, yerr=[eSEDlo, eSEDhi], fmt='ok', markersize=1.5,
                capsize=0)

    # plot formatting
    ax.tick_params('both', length=2, which='major')
    ax.tick_params('both', which='major', labelsize=6)
    ax.annotate(labels[i], xy=(0.92, 0.83), xycoords='axes fraction',
                size=7, horizontalalignment='right', color='k')
    if (i == 15):
        ax.set_xlabel(r'$\lambda$'+' / '+r'$\mu{\rm m}$', fontsize=7)
        ax.xaxis.set_label_coords(0.5, -0.18)
        ax.set_xticklabels([' ', ' ', '1', '10', '100', '1000'])
        ax.set_ylabel(r'${\rm log}$'+' '+r'$L_\nu$'+' / '+r'$L_\odot$', 
                      fontsize=7)
    else:
        ax.set_xticklabels([])
        ax.set_yticklabels([])

fig.subplots_adjust(wspace=0.0, hspace=0.0)
fig.subplots_adjust(left=0.05, right=0.95, bottom=0.06, top=0.99)
fig.savefig('SEDgallery.pdf')
fig.clf()
