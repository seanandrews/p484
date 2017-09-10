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
from casa import quanta as qa

def LSRKvel_to_chan(msfile, field, spw, restfreq, LSRKvelocity):
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
    tb.open(msfile+"/FIELD")
    fieldnames = tb.getcol("NAME")
    tb.close()
    nchan = len(chanfreqs)
    ms.open(msfile)
    lsrkfreqs = ms.cvelfreqs(spwids = [spw], fieldids = np.where(fieldnames==field)[0][0], mode = 'channel', nchan = nchan, start = 0, outframe = 'LSRK')
    chanvelocities = (restfreq-lsrkfreqs)/restfreq*cc/1.e3 #converted to LSRK velocities in km/s
    if type(LSRKvelocity)==np.ndarray:
        outchans = np.zeros_like(LSRKvelocity)
        for i in range(len(LSRKvelocity)):
            outchans[i] = np.argmin(np.abs(chanvelocities - LSRKvelocity[i]))
        return outchans
    else:
        return np.argmin(np.abs(chanvelocities - LSRKvelocity))


def getobstimes(caltable):
    """
    Converts observation times from measurement set to a format that can be read by plotcal
    
    """
    tb.open(caltable+"/OBSERVATION")
    start,end = tb.getcol("TIME_RANGE")
    outputtimes = []
    for i in range(len(start)):
        
        starttime = qa.quantity(start[i], 's')
        convertedstarttime = str(qa.time(starttime, form = 'ymd')[0])
        endtime = qa.quantity(end[i],'s')
        convertedendtime = str(qa.time(endtime, form = 'ymd')[0])
        outputtimes.append(convertedstarttime+'~'+convertedendtime)
    return outputtimes
