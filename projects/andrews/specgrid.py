import numpy as np
import os
import sys

# set paths
dir_nextgen = '/pool/asha1/HOLD/nextgen/'

# make an appropriate spectral grid
tgrid = np.loadtxt(dir_nextgen+'TEMP_GRID.dat')
ggrid = np.loadtxt(dir_nextgen+'GRAV_GRID.dat')
nwl = 1221
tname = np.array([str(np.int(np.floor(i/100))) for i in tgrid])
for i in range(len(tgrid)):
    if (tgrid[i] < 10000.): tname[i] = '0'+tname[i]
gname = np.array([str(i) for i in ggrid])
spec = np.zeros((len(tgrid), len(ggrid), nwl))

for i in range(len(tgrid)):
    for j in range(len(ggrid)):
        infile = dir_nextgen+'Fnu/NG_'+tname[i]+'_'+gname[j]+'_00.dat'
        wl, cf = np.loadtxt(infile, usecols=(0, 2), unpack=True)
        spec[i, j, :] = cf

np.savez('nextgen_grid.npz', wl=wl, spec=spec, tgrid=tgrid, ggrid=ggrid)     
    

