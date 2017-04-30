try:
    import numpy as np
except:
    print 'ERROR'
    print ' Numpy cannot be imported '
    print ' To use the python module of RADMC-3D you need to install Numpy'


from radmc3dPy.natconst import *
try:
    import matplotlib.pylab as plb
except:
    print ' WARNING'
    print ' matploblib.pylab cannot be imported ' 
    print ' To used the visualization functionality of the python module of RADMC-3D you need to install matplotlib'
    print ' Without matplotlib you can use the python module to set up a model but you will not be able to plot things or'
    print ' display images'

import radmc3dPy.analyze as analyze
import sys

# ============================================================================================================================
#
# ============================================================================================================================
def getModelDesc():
    """Returns the brief description of the model.
    """

    return "Gaussian blobs"
           

# ============================================================================================================================
#
# ============================================================================================================================
def getDefaultParams():
    """Function to provide default parameter values of the model.

    Returns a list whose elements are also lists with three elements:
    1) parameter name, 2) parameter value, 3) parameter description
    All three elements should be strings. The string of the parameter
    value will be directly written out to the parameter file if requested,
    and the value of the string expression will be evaluated and be put
    to radmc3dData.ppar. The third element contains the description of the
    parameter which will be written in the comment field of the line when
    a parameter file is written. 
    """

    defpar = {}

    defpar = [ 
    ['levelMaxLimit', '4', ' Highest refinement level in octree AMR'],
    ['crd_sys', "'car'", '  Coordinate system used (car/cyl)'],
    ['grid_style', '1', '  0 - Regular grid, 1 - Octree AMR, 10 - Layered/nested grid (not yet supported)'],
    ['xres_nlev', '3', 'Number of refinement levels'],
    ['xres_nspan', '3', 'Number of the original grid cells to refine'],
    ['xres_nstep', '3', 'Number of grid cells to create in a refinement level'],
    ['nx', '[10]', 'Number of grid points in the first dimension'],
    ['xbound', '[-100.*au, 100.*au]', 'Number of radial grid points'],
    ['ny', '[10]', 'Number of grid points in the first dimension'],
    ['ybound', '[-100.*au, 100*au]', 'Number of radial grid points'],
    ['nz', '[10]', 'Number of grid points in the first dimension'],
    ['zbound', '[-100.*au, 100.*au]', 'Number of radial grid points'],
    ['blob_xc', '[-30.*au, 30.*au]', 'X coordinate of the blob centers'],
    ['blob_yc', '[0.*au, 0.*au]', 'Y coordinate of the blob centers'],
    ['blob_zc', '[0.*au, 0.*au]', 'Z coordinate of the blob centers'],
    ['blob_fwhm', '[10.*au, 10.*au]', 'FWHM of the 3D gaussian in the X coordinate'], 
    ['blob_rho0', '[1e-10, 1e-10]', 'Central density of the blobs'],
    ['bgdens', '1e-20', 'Central density of the blobs'],
    ['dusttogas', '0.01', ' Dust-to-gas mass ratio'],
    ['nsample', '30', ' Number of randomly sampled points within a grid cell (used for AMR refinement)']]


    return defpar

# ============================================================================================================================
#
# ============================================================================================================================
def getGasDensity(x=None, y=None, z=None, grid=None, ppar=None):
    """Calculates the gas density 
    
    Parameters
    ----------
    x    : ndarray
           Coordinate of the cell centers in the first dimension
    
    y    : ndarray
           Coordinate of the cell centers in the second dimension
    
    y    : ndarray
           Coordinate of the cell centers in the third dimension
    
    grid : radmc3dGrid
           An instance of the radmc3dGrid class containing the spatial and frequency/wavelength grid
    
    ppar : dictionary
           A dictionary containing all parameters of the model
    
    Returns
    -------
    Returns the volume density in g/cm^3
    """

    if grid is not None:
        x = grid.x
        y = grid.y
        z = grid.z

    rho = np.zeros(x.shape[0], dtype=np.float64)
    for i in range(len(ppar['blob_xc'])):
        d   = np.sqrt((x - ppar['blob_xc'][i])**2 + (y - ppar['blob_yc'][i])**2 + (z - ppar['blob_zc'][i])**2)
        rho += ppar['blob_rho0'][i] * np.exp(-0.5 * d**2 / ppar['blob_fwhm'][i]**2)

    rho = rho.clip(ppar['bgdens'])
    return rho
# ============================================================================================================================
#
# ============================================================================================================================
def getDustDensity(x=None, y=None, z=None, grid=None, ppar=None):
    """Calculates the dust density distribution. 
   
    Parameters
    ----------
    x    : ndarray
           Coordinate of the cell centers in the first dimension
    
    y    : ndarray
           Coordinate of the cell centers in the second dimension
    
    y    : ndarray
           Coordinate of the cell centers in the third dimension

    grid : radmc3dGrid
           An instance of the radmc3dGrid class containing the spatial and frequency/wavelength grid
    
    ppar : dictionary
           A dictionary containing all parameters of the model
    
    Returns
    -------
    Returns the volume density in g/cm^3
    """

    rhogas = getGasDensity(x=x, y=y, z=z, grid=grid, ppar=ppar)

    rho    = np.array(rhogas) * ppar['dusttogas']
    if ppar.has_key('ngs'):
        if ppar['ngs']>1:
            ngs = ppar['ngs']
            #
            # WARNING!!!!!!
            # At the moment I assume that the multiple dust population differ from each other only in 
            # grain size but not in bulk density thus when I calculate the abundances / mass fractions 
            # they are independent of the grains bulk density since abundances/mass fractions are normalized
            # to the total mass. Thus I use 1g/cm^3 for all grain sizes.
            # TODO: Add the possibility to handle multiple dust species with different bulk densities and 
            # with multiple grain sizes.
            #
            gdens = np.zeros(ngs, dtype=float) + 1.0
            gs = ppar['gsmin'] * (ppar['gsmax']/ppar['gsmin']) ** (np.arange(ppar['ngs'], dtype=np.float64) / (float(ppar['ngs'])-1.))
            gmass = 4./3.*np.pi*gs**3. * gdens
            gsfact = gmass * gs**(ppar['gsdist_powex']+1)
            gsfact = gsfact / gsfact.sum()
        else:
            gsfact = [1.0]
            ngs    = 1
    elif ppar.has_key('mfrac'):
        ngs    = len(ppar['mfrac'])
        gsfact = ppar['mfrac'] / ppar['mfrac'].sum()
    
    else:
        ngs = 1
        gsfact = [1.0]
 
    rho_old = np.array(rho)

    if grid is not None:
        # Regular grids
        if grid.grid_style == 0:
            rho = np.zeros([grid.nx, grid.ny, grid.nz, ngs], dtype=np.float64)
            for igs in range(ngs):
                rho[:,:,:,igs] = rho_old[:,:,:] * gsfact[igs]
        elif grid.grid_style == 1:
            rho = np.zeros([grid.nCell, ngs], dtype=np.float64)
            for igs in range(ngs):
                rho[:,igs] = rho_old * gsfact[igs]
    else:
        ncell = x.shape[0]
        rho = np.zeros([ncell, ngs], dtype=np.float64)
        for igs in range(ngs):
            rho[:,igs] = rho_old * gsfact[igs]


    return rho

def decisionFunction(x=None, y=None, z=None, dx=None, dy=None, dz=None, model=None, ppar=None, **kwargs):
    """
    Example function to be used as decision function for resolving cells in tree building. It calculates the gas density
    at a random sample of coordinates within a given cell than take the ratio of the max/min density. If it is larger
    than a certain threshold value it will return True (i.e. the cell should be resolved) if the density variation is less
    than the threshold it returns False (i.e. the cell should not be resolved)

    Parameters
    ----------
    x       : ndarray
              Cell centre coordinates of the cells in the first dimension
    
    y       : ndarray
              Cell centre coordinates of the cells in the second dimension
    
    z       : ndarray
              Cell centre coordinates of the cells in the third dimension
    
    dx      : ndarray
              Half size of the cells in the first dimension
    
    dy      : ndarray
              Half size of the cells in the second dimension
    
    dz      : ndarray
              Half size of the cells in the third dimension
    
    model   : object
              A radmc3dPy model (must contain a getGasDensity() function) 

    ppar    : dictionary
              All parameters of the problem (from the problem_params.inp file). It is not used here, but must be present 
              for compatibility reasons.
    
    **kwargs: dictionary
              Parameters used to decide whether the cell should be resolved. It should contain the following keywords; 'nsample', 
              which sets the number of random points the gas desity is sampled at within the cell and 'threshold' that
              sets the threshold value for max(gasdens)/min(gasdens) above which the cell should be resolved.
    """

    ncell   = x.shape[0]
    rho     = np.zeros([ncell, kwargs['nsample']], dtype=np.float64)

    for isample in range(kwargs['nsample']):
        xoffset  = (np.random.random_sample(ncell)-0.5)*dx*4.0
        yoffset  = (np.random.random_sample(ncell)-0.5)*dy*4.0
        zoffset  = (np.random.random_sample(ncell)-0.5)*dz*4.0
        rho[:,isample] = model.getGasDensity(x+xoffset, y+yoffset, z+zoffset, ppar=ppar)
    
    rho_max = rho.max(axis=1)
    rho_min = rho.min(axis=1)
    jj      = ((rho_max-rho_min)/rho_max>ppar['threshold'])
    
    decision = np.zeros(ncell, dtype=bool)
    if True in jj:
        decision[jj] = True

    return decision


