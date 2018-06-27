import numpy as np
import os
import sys
import time
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from astropy.io import ascii
from scipy.interpolate import interp1d

ndim = 6

# plot layout
xinch = 7.5
yinch = 6.5
dhspace, dwspace = 0.25, 0.25
lbound, rbound, bbound, tbound = 0.08, 0.92, 0.08, 0.99
fig = plt.figure(figsize=(xinch, yinch))
gs = gridspec.GridSpec(2, 2)

# plot ranges for each parameter
Llims = [-1.0, 1.5]     # log Lstar / Lsun
Tlims = [3.75, 3.5]      # log Teff / K
Mlims = [-0.5, 0.4]     # log Mstar / Msun
Alims = [5., 7.5]	

# HRD
ntest = 15000
data_logT = np.random.normal(3.97, 0.03, ntest)
data_logL = np.random.normal(1.23, 0.30, ntest)


# HRD
ax = fig.add_subplot(gs[0,0])


# overplot models
top_dir = '/pool/asha0/SCIENCE/Lupus_sizes/analysis/'
iso_dir = top_dir+'MIST_isochrones/MIST_v1.1_vvcrit0.4_full_isos/'
iso_file = iso_dir+'MIST_v1.1_feh_p0.00_afe_p0.0_vvcrit0.4_full.iso'
iso_dat = ascii.read(iso_file)
iso_AGE = iso_dat['col2']
iso_M = iso_dat['col4']
iso_L = iso_dat['col9']
iso_T = iso_dat['col14']
ax.plot(iso_T[iso_AGE == 5.6], iso_L[iso_AGE == 5.6], 'r')

mt_dir = top_dir+'../SP/ScottiePippen/data/MIST/'
mt_file = mt_dir+'MIST_v1.0_feh_p0.00_afe_p0.0_vvcrit0.4_EEPS/00070M.track.eep'
mt_dat = ascii.read(mt_file)
mt_AGE = np.log10(mt_dat['col1'])
mt_M = mt_dat['col2']
mt_L = mt_dat['col7']
mt_T = mt_dat['col12']
ax.plot(mt_T[mt_AGE <= 7.5], mt_L[mt_AGE <= 7.5], 'r')

ax.plot(data_logT, data_logL, '.k')

ax.set_ylim(Llims)
ax.set_xlim(Tlims)


# load some data
mt_dir = top_dir+'../SP/ScottiePippen/data/MIST/MIST_v1.0_feh_p0.00_afe_p0.0_vvcrit0.4_EEPS/'
mt_files = ascii.read(mt_dir+'filenames.txt')
files = mt_files['files']

mt_logM = np.zeros((343, len(files)))
mt_logL = np.zeros((343, len(files)))
mt_logT = np.zeros((343, len(files)))
for im in range(len(files)):
    filename = mt_dir+files[im]
    mt_dat = ascii.read(filename)
    mt_age  = np.log10(mt_dat['col1'])
    inp_logM = np.log10((mt_dat['col2'])[mt_age <= 8.0])
    inp_logL = (mt_dat['col7'])[mt_age <= 8.0]
    inp_logT = (mt_dat['col12'])[mt_age <= 8.0]
    mt_logM[:len(inp_logL),im] = inp_logM
    mt_logL[:len(inp_logL),im] = inp_logL
    mt_logT[:len(inp_logL),im] = inp_logT

iso_dir = top_dir+'MIST_isochrones/MIST_v1.1_vvcrit0.4_full_isos/'
iso_file = iso_dir+'MIST_v1.1_feh_p0.00_afe_p0.0_vvcrit0.4_full.iso'
iso_dat = ascii.read(iso_file)
init_AGE = iso_dat['col2']
ok = (init_AGE <= 7.5)
iso_AGE = (iso_dat['col2'])[ok]
iso_M = (iso_dat['col4'])[ok]
iso_L = (iso_dat['col9'])[ok]
iso_T = (iso_dat['col14'])[ok]
ages = np.unique(iso_AGE)


# loop through a collection of datapoints
axbot = fig.add_subplot(gs[1,0])
axtop = fig.add_subplot(gs[0,1])
axcor = fig.add_subplot(gs[1,1])

agestar  = np.zeros(ntest)
massstar = np.zeros(ntest)

t0 = time.time()
for i in range(ntest):
    # mass as function of temperature at the given luminosity
    interp_M = []
    interp_T = []
    for im in range(len(files)):

        # check and see if the mass track surrounds the input log L value
        ok = (np.max(mt_logL[:,im]) >= data_logL[i]) & \
             (np.min(mt_logL[:,im]) <= data_logL[i])

        if (ok == True):
            ltint = interp1d(mt_logL[:,im], mt_logT[:,im])
            temp = ltint(data_logL[i])
            interp_T = np.append(interp_T, temp)
            interp_M = np.append(interp_M, mt_logM[0,im])

    axbot.plot(interp_T, interp_M)

    mtint = interp1d(interp_T, interp_M, fill_value='extrapolate')
    massstar[i] = mtint(data_logT[i])


    # age as function of luminosity at the given temperature
    interp_age = []
    interp_L = []
    for ia in range(len(ages)):
        il_logL = (iso_L)[iso_AGE == ages[ia]]
        il_logT = (iso_T)[iso_AGE == ages[ia]]

        # check and see if the isochrone surrounds the input log T value
        ok = (np.max(il_logT) >= data_logT[i]) & \
             (np.min(il_logT) <= data_logT[i])

        if (ok == True):
            ilint = interp1d(il_logT, il_logL)
            lum = ilint(data_logT[i])
            interp_L = np.append(interp_L, lum)
            interp_age = np.append(interp_age, ages[ia])

    # plotting stuff for each parameter
    axtop.plot(interp_age, interp_L)

    ageint = interp1d(interp_L, interp_age, fill_value='extrapolate')
    agestar[i] = ageint(data_logL[i])



axcor.plot(agestar, massstar, '.k')

axbot.set_ylim(Mlims)
axbot.set_xlim(Tlims)
axtop.set_ylim(Llims)
axtop.set_xlim(Alims)
axcor.set_xlim(Alims)
axcor.set_ylim(Mlims)

tf = time.time()
print(tf-t0)

os.system('rm -rf hd163296_mt_test.npz')
np.savez('hd163296_mt_test.npz', logT=data_logT, logL=data_logL, 
         logMstar=massstar, logAGE=agestar)

# plot appearances
fig.subplots_adjust(left=lbound, right=rbound, bottom=bbound, top=tbound)
fig.subplots_adjust(hspace=dhspace, wspace=dwspace)
fig.savefig('hd163296_hrd_inferences.pdf',dpi=1000)
fig.clf()
