import numpy as np

MSname = 'combined_quick'

# get the data tables
tb.open(MSname+'.ms')
data   = np.squeeze(tb.getcol("DATA"))
flag   = np.squeeze(tb.getcol("FLAG"))
uvw    = tb.getcol("UVW")
weight = tb.getcol("WEIGHT")
spwid  = tb.getcol("DATA_DESC_ID")
tb.close()

# get frequency information
tb.open(MSname+'.ms/SPECTRAL_WINDOW')
freq = tb.getcol("CHAN_FREQ")
tb.close()

# get rid of any flagged columns
print(data.shape)
print(flag.shape)
crap   = np.any(flag, axis=0)
good   = np.squeeze([crap == False])
data   = data[:,good]
weight = weight[:,good]
uvw    = uvw[:,good]
spwid  = spwid[:,good]
print(data.shape)

# break out the spatial frequency coordinates in **lambda** units
freqlist = freq[0]
findices = lambda ispw: freqlist[ispw]
freqs = findices(spwid)
u = uvw[0,:] * freqs / 2.9979e8
v = uvw[1,:] * freqs / 2.9979e8

# Assign uniform spectral-dependence to the weights 
sp_wgt = weight

# average the polarizations
Re  = np.sum(data.real*sp_wgt, axis=0) / np.sum(sp_wgt, axis=0)
Im  = np.sum(data.imag*sp_wgt, axis=0) / np.sum(sp_wgt, axis=0)
Vis = Re + 1j*Im
Wgt = np.sum(sp_wgt, axis=0)

# output to a numpy save file
os.system('rm -rf '+MSname+'.vis.npz')
np.savez(MSname+'.vis', u=u, v=v, Vis=Vis, Wgt=Wgt)
