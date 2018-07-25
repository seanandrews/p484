import numpy as np
import os
import sys
import time
from datetime import date, timedelta

cals = ['J1427-4206', 'J1517-2422', 'J1617-5848', 'J1733-1304']

# set up dates and indexing
d1, d2 = date(2017, 5, 1), date(2017, 12, 31) 
delta = d2 - d1    

# loop
for j in range(len(cals)):

    os.system('rm -rf '+cals[j]+'.fluxes.dat')

    for i in range(delta.days + 1):

        # compute a date
        d = d1 + timedelta(i)

        # measure the 240 GHz flux density for that date and calibrator
        fetch = au.getALMAFlux(cals[0], frequency='238.74GHz', 
                               date=d.strftime("20%y/%m/%d"))
        Fnu, eFnu  = fetch['fluxDensity'], fetch['fluxDensityUncertainty']

        # prepare for output
        if (i < 10): ix = str(i) + '    '
        if ((i >= 10) & (i < 100)): ix = str(i) + '   '
        if (i >= 100): ix = str(i) + '  '
        fstr = '%7.4f  %7.4f' % (Fnu, eFnu)

        # write to file
        f = open(cals[j]+'.fluxes.dat', 'a')
        f.write(ix + str(d.year) + '  ' + str(d.month) + '  ' + str(d.day) + 
                '  ' + fstr)
        f.write('\n')
        f.close()
