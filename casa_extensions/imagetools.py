#this needs to be executed in Python, not CASA
import numpy as np
from skimage.measure import find_contours, moments, EllipseModel, grid_points_in_poly
import matplotlib.pyplot as plt

import pwkit.environments.casa.util as util
ia = util.tools.image()
#always good to double check with what you get interactively. This is to enforce consistency
def getcentroid(filename, box):
    ia.open(filename)
    imgdataraw = ia.getregion()
    headerlist = ia.summary()
    ia.close()

    x0,x1,y0,y1 = box
    imgdata = np.squeeze(imgdataraw) #in units of Jy/beam

    xpix = imgdata.shape[0] #confirmed that imgdata is x,y
    ypix = imgdata.shape[1]

    xcen, ycen = headerlist['refpix'][0], headerlist['refpix'][1]
    RA0, DEC0 = headerlist['refval'][0], headerlist['refval'][1]
    deltaRA, deltaDEC = headerlist['incr'][0], headerlist['incr'][1]

    bminor = headerlist['restoringbeam']['minor']['value']
    bmajor = headerlist['restoringbeam']['major']['value']
    ang = headerlist['restoringbeam']['positionangle']['value']

    beamsize = np.pi*bminor*bmajor/(4*np.log(2)) #in arcsec^2

    print "The beam shape is %.3f, %.3f, %.3f" % (bmajor, bminor, ang)

    cellsize = headerlist['incr'][1]*206265 #in arcsec
    
    print "The image size is %d pixels" % imgdata.shape[0]


    #background calculations
    bg1 = imgdata[50:xpix-50 ,50:150]
    bg2 = imgdata[50:xpix - 50, ypix - 150:ypix - 50]
    bgmean = 0.5*(np.mean(bg1)+np.mean(bg2))

    rms = np.sqrt(np.sum((bg1-bgmean)**2+(bg2-bgmean)**2)/(float(bg1.size)+float(bg2.size)))
    print "The image rms is %.3e" % rms

    #m = moments(image = imgdata[xpix/2-75:xpix/2+75,ypix/2-75:ypix/2+75], order = 1)

    #print "The image centroid is (%.3f, %.3f)" % (xpix/2-75+m[0,1]/m[0,0], ypix/2-75+m[1,0]/m[0,0])

    m = moments(image = imgdata[x0:x1,y0:y1], order = 1)

    print "The image centroid is (%.3f, %.3f)" % (x0+m[0,1]/m[0,0], y0+m[1,0]/m[0,0])
    centroidRA = (RA0+deltaRA*(x0+m[0,1]/m[0,0]-xcen))*180/np.pi*1/15.
    centroidDEC = (DEC0+deltaDEC*(y0+m[1,0]/m[0,0]-ycen))*180/np.pi
    ra = np.zeros(3)
    ra[0] = int(centroidRA)
    ra[1] = np.abs(int((centroidRA - ra[0])*60))
    ra[2] = (np.abs(centroidRA)-np.abs(ra[0])-ra[1]/60.)*3600
    dec = np.zeros(3)
    dec[0] = int(centroidDEC)
    dec[1] = np.abs(int((centroidDEC - dec[0])*60))
    dec[2] = (np.abs(centroidDEC)-np.abs(dec[0])-dec[1]/60.)*3600
    print "The coordinates are RA %d:%d:%.3f, DEC %d:%d:%.3f" % (ra[0], ra[1], ra[2], dec[0], dec[1], dec[2])

#getcentroid('/pool/firebolt1/LPscratch/HD_163296_new/HD_163296_LB_initcontinuum_LBonly.image', [750,1250,760,1240]) 
#getcentroid('/pool/firebolt1/LPscratch/HD_163296/HD_163296_SB2_ap1continuum.image', [170,330,170,330]) 
