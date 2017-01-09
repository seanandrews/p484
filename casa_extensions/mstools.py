"""
Useful (hopefully) helper functions during data reduction
Obviously the writing is still in progress

It's quite possible that some of this functionality already exists in CASA natively, but CASA is a deep mystery, so...

Tested in CASA version 4.4.0, should probably work from 4.2 to 4.7
"""

import numpy as np
import constants as const
from casa import table as tb
from casa import ms

def LSRKvel_to_chan(msfile, spw, restfreq, LSRKvelocity):
    """
    Identifies the channel(s) corresponding to input LSRK velocities. 
    Useful for choosing which channels to split out or flag if a line is expected to be present

    Parameters:
    msfile: Name of measurement set (string)
    spw: Spectral window number (int)
    restfreq: Rest frequency in Hz (float)
    LSRKvelocity: input velocity in LSRK frame in km/s (float or array of floats)

    Returns: 
    Channel number most closely corresponding to input LSRK velocity 
    """
    tb.open(msfile+"/SPECTRAL_WINDOW")
    chanfreqs = tb.getcol("CHAN_FREQ", startrow = 0, nrow = 1)
    tb.close()
    nchan = len(chanfreqs)
    ms.open(msfile)
    lsrkfreqs = ms.cvelfreqs(spwids = [spw], mode = 'channel', nchan = nchan, start = 0, outframe = 'LSRK')
    chanvelocities = (restfreq-lsrkfreqs)/restfreq*const.cc/1.e3 #converted to LSRK velocities in km/s
    if type(LSRKvelocity)==np.ndarray:
        outchans = np.zeros_like(LSRKvelocity)
        for i in range(len(LSRKvelocity)):
            outchans[i] = np.argmin(np.abs(chanvelocities - LSRKvelocity[i]))
        return outchans
    else:
        return np.argmin(np.abs(chanvelocities - LSRKvelocity))
