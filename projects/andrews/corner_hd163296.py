import numpy as np
import os
import sys
import corner

dat = np.load('hd163296_mt_test.npz')
logM = dat['logMstar']
logAGE = dat['logAGE']

posts = np.column_stack([logM, logAGE])

levs = 1.-np.exp(-0.5*(np.arange(2)+1)**2)
fig = corner.corner(posts, plot_datapoints=False, bins=30, levels=levs, 
                    range=[(-0.5, 0.5), (4.5, 8.0)], no_fill_contours=True,
                    plot_density=False, color='b', labels=['log Mstar / Msun', 
                    'log age / yr'])

print(np.percentile(logM, [50., 16., 84.]))
print(np.percentile(logAGE, [50., 16., 84.]))

#posts = np.column_stack([logM, logAGE])
#corner.corner(posts, plot_datapoints=False, bins=30, levels=levs,
#              range=[(-1.1, -0.3), (4.5, 8.0)], fig=fig,
#              plot_density=False, no_fill_contours=True, color='r')



fig.savefig('corner_hd163296.png')
fig.clf()
