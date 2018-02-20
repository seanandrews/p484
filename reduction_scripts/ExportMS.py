"""
This function should produce a numpy save file of the spectrally averaged (and 
polarization-averaged) input MS.  The 'filename' parameter should end in '.ms'.

Just place:

execfile('ExportMS.py')

at the top of your CASA script and run with

ExportMS(filename)

"""
import numpy as np

def ExportMS(filename):

    # strip off the '.ms'
    MS_filename = filename.replace('.ms', '')

    # get information about spectral windows
    ms.open(MS_filename+'.ms')
    spwInfo = ms.getspectralwindowinfo()
    ms.close()
    nspw = len(spwInfo)
    chanlist = [(spwInfo[str(i)])['NumChan'] for i in range(nspw)]

    # spectral averaging (1 channel per SPW)
    os.system('rm -rf '+MS_filename+'_spavg.ms*')
    split(vis=MS_filename+'.ms', width=chanlist, datacolumn='data',
          outputvis=MS_filename+'_spavg.ms')

    # get the data tables
    tb.open(MS_filename+'_spavg.ms')
    data   = np.squeeze(tb.getcol("DATA"))
    flag   = np.squeeze(tb.getcol("FLAG"))
    uvw    = tb.getcol("UVW")
    weight = tb.getcol("WEIGHT")
    spwid  = tb.getcol("DATA_DESC_ID")
    tb.close()

    # get frequency information
    tb.open(MS_filename+'_spavg.ms/SPECTRAL_WINDOW')
    freq = tb.getcol("CHAN_FREQ")
    tb.close()

    # get rid of any flagged columns
    crap   = np.any(flag, axis=0)
    good   = np.squeeze([crap == False])
    data   = data[:,good]
    weight = weight[:,good]
    uvw    = uvw[:,good]
    spwid  = spwid[good]

    # break out the spatial frequency coordinates in **lambda** units
    freqlist = freq[0]
    findices = lambda ispw: freqlist[ispw]
    freqs = findices(spwid)
    u = uvw[0,:] * freqs / 2.9979e8
    v = uvw[1,:] * freqs / 2.9979e8

    # average the polarizations
    Re  = np.sum(data.real*weight, axis=0) / np.sum(weight, axis=0)
    Im  = np.sum(data.imag*weight, axis=0) / np.sum(weight, axis=0)
    Vis = Re + 1j*Im
    Wgt = np.sum(weight, axis=0)

    # output to a numpy save file
    os.system('rm -rf '+MS_filename+'.vis.npz')
    np.savez(MS_filename+'.vis', u=u, v=v, Vis=Vis, Wgt=Wgt)
