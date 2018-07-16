"""
Script for displaying continuum images, deprojecting, and azimuthally averaging
This script is written for Python 3.6 (but should work in Python 2.7) 
"""

import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from matplotlib.patches import Ellipse
from scipy.ndimage.interpolation import shift
import copy
import matplotlib as mpl
import matplotlib.colors as col
import yaml
from skimage import transform, measure
from scipy import ndimage


class Continuum:
    def __init__(self, filename, offsetx, offsety, PA, incl, src_distance):
        """
        filename: fits file name
        offsetx: offset from phase center in x-direction in arcsec (positive is eastward). Note that the phase center occurs at pixelimsize/2+1 
        offsety: offset from phase center in y-directino in arcsec (positive is northward)
        PA: position angle, defined as angle that semimajor axis makes with north (deg)
        incl: inclination angle in degrees (0 is face-on, 90 is edge on)
        src_distance: source distance in pc
        """
        hdulist = fits.open(filename)
        #we assume here that the image is square
        self.image = np.squeeze(hdulist[0].data).astype(np.float64) #stored as (y,x)
        assert self.image.shape[0]==self.image.shape[1]
        #self.image = np.nan_to_num(np.squeeze(hdulist[0].data))
        #self.image[np.where(np.abs(self.image)>1.e6)]=0
        self.header = hdulist[0].header
        self.bmaj = self.header['BMAJ']*3600 #major axis of synthesized beam in arcsec
        self.bmin = self.header['BMIN']*3600 #minor axis of synthesized beam in arcsec
        self.bpa = self.header['BPA'] #position angle of synthesized beam in degrees
        self.freq = self.header['CRVAL3'] #continuum frequency in Hz
        self.imsize = self.header['NAXIS1']#image size along one dimension in pixels
        self.delt_x = self.header['CDELT1']*3600 #size of pixel in x direction in arcsec (this is negative because RA is positive going left)
        self.delt_y =self.header['CDELT2']*3600 #size of pixel in y direction in arcsec
        hdulist.close()


        self.offsetx = float(offsetx)
        self.offsety = float(offsety)
        self.PA = float(PA)
        self.incl = float(incl)
        self.src_distance = float(src_distance)

        RAcosDEC = self.delt_x*(np.arange(self.imsize)-(self.header['CRPIX1']-1.0))-self.offsetx #For an even number of pixels, the phase center corresponds to pixel = imsize/2+1

        DEC = self.delt_y*(np.arange(self.imsize)-(self.header['CRPIX2']-1.0))-self.offsety

        # Define a coordinate system based on the geometry

        self.xx, self.yy = np.meshgrid(RAcosDEC, DEC) # indexing is y,x 
        inclr = np.radians(self.incl)
        PAr = np.radians(self.PA)

        self.x_prime = (self.xx*np.cos(PAr) - self.yy*np.sin(PAr)) / np.cos(inclr) #this does the rotation so that the major axis of the disk image is aligned with the y-axis
        self.y_prime = (self.xx*np.sin(PAr) + self.yy*np.cos(PAr))

        # convert into polar coordinates (in physical dimensions)
        self.r = self.src_distance * np.sqrt(self.x_prime**2 + self.y_prime**2) #in pc
        self.theta = np.degrees(np.arctan2(self.y_prime, self.x_prime)) #90 deg corresponds to the major axis, angles increase in the clockwise direction when viewing the image (because of the orientation of the horizontal axis)

    def get_TB(self, Ivals):
        #convert Ivals from Jy/beam to watts/ster
        # a jansky is 10^(-26) watts per square meter per hertz
        #this is all in mks units
        h = 6.62607004e-34 #m^2 kg/s
        c = 299792458 #m/s
        k = 1.38064852e-23 #m^2 kg s^-2 K^-1
        beamsize = np.pi*self.bmin*self.bmaj/(4*np.log(2)) #arcsec^2
        B_nu = Ivals*1.e-26*1/beamsize*(206264.806**2)
        return h*self.freq/(k*np.log(2*h*self.freq**3/c**2*1/B_nu+1.))

    def radialprofile(self,radialbins,yaxis = 'intensity', theta_exclusion = np.array([]), high_incl = False): 
        """
        Parameters
        ==========
        """
        rbins = radialbins
        rwidth = (rbins[1]-rbins[0])

        radial_profile = np.zeros( len(rbins) )
        rad_prof_scatter = np.zeros_like(radial_profile)

        for i in range(len(rbins)):
            annulus_thetas = self.theta[(self.r>=(rbins[i]-0.5*rwidth)) & (self.r<(rbins[i]+0.5*rwidth))]
            #for azimuthal asymmetries
            if len(theta_exclusion)==2:
                  annulus_intensities = self.image[(self.r>=(radialbins[i]-0.5*rwidth)) & (self.r<(radialbins[i]+0.5*rwidth))&((self.theta<=theta_exclusion[0]) | (self.theta>=theta_exclusion[1]))]
            #for high inclination disks 
            elif high_incl:
                annulus_intensities = self.image[(self.r>=(rbins[i]-0.5*rwidth)) & (self.r<(rbins[i]+0.5*rwidth))&(np.abs(self.theta)<=110)&(np.abs(self.theta)>=70)]
            else:
                annulus_intensities = self.image[(self.r>=(rbins[i]-0.5*rwidth)) & (self.r<(rbins[i]+0.5*rwidth))]

            radial_profile[i] = np.average(annulus_intensities)
            rad_prof_scatter[i] = np.std(annulus_intensities)

        if yaxis == 'temperature': #return brightness temperature (K)
            return self.get_TB(radial_profile)
        elif yaxis == 'intensity': #return intensity profile (mJy/beam)
            return radial_profile, rad_prof_scatter

    def azunwrap(self,radialbins, tbins = -179.+2*np.arange(180), yaxis = 'intensity', theta_exclusion = np.array([])): 
        """
        Parameters
        ==========
        """
        rbins = np.copy(radialbins)
        rwidth = (rbins[1]-rbins[0])
        twidth = np.abs((tbins[1]-tbins[0]))

        # create a binned (r, theta) "map" 
        rtmap = np.zeros( (len(tbins), len(rbins)) )
        radial_profile = np.zeros( len(rbins) )
        rad_prof_scatter = np.zeros_like(radial_profile)

        for i in range(len(rbins)):
            annulus_thetas = self.theta[(self.r>=(rbins[i]-0.5*rwidth)) & (self.r<(rbins[i]+0.5*rwidth))]
            if len(theta_exclusion)==2:
                annulus_intensities = self.image[(self.r>=(radialbins[i]-0.5*rwidth)) & (self.r<(radialbins[i]+0.5*rwidth))&((self.theta<=theta_exclusion[0]) | (self.theta>=theta_exclusion[1]))]
            else:
                annulus_intensities = self.image[(self.r>=(rbins[i]-0.5*rwidth)) & (self.r<(rbins[i]+0.5*rwidth))]

            radial_profile[i] = np.average(annulus_intensities)
            rad_prof_scatter[i] = np.std(annulus_intensities)
            if len(theta_exclusion)==2:
                annulus_intensities = self.image[(self.r>=(rbins[i]-0.5*rwidth)) & (self.r<(rbins[i]+0.5*rwidth))]
            for j in range(len(tbins)):
                wedge = annulus_intensities[(annulus_thetas>=(tbins[j]-0.5*twidth)) & (annulus_thetas<(tbins[j]+0.5*twidth))]
                if len(wedge) > 0:
                    rtmap[j, i] = np.average(wedge)
                else: 
                    rtmap[j, i] = -1e10
        
        # "fix" the inner disk where there's too few azimuthal bins (linear interpolation)
        for i in range(len(rbins)):
            tslice = rtmap[:, i]
            if np.any(tslice <= -1e5):
                xslc = tbins[tslice >= -1e5]
                yslc = tslice[tslice >= -1e5]
                #we need the interpolating values to make at least a full 360 so that we can get the whole circle
                xslc_extended = np.pad(xslc, 1, mode = 'wrap')
                xslc_extended[0]-=360.
                xslc_extended[-1]+=360
                yslc_extended = np.pad(yslc, 1, mode = 'wrap')

                rzfunc = interp1d(xslc_extended, yslc_extended, bounds_error=True)
                fix_slice = rzfunc(tbins)
                rtmap[:, i] = fix_slice

        if yaxis == 'temperature': #return brightness temperature (K)
            return self.get_TB(radial_profile), rtmap
        elif yaxis == 'intensity': #return intensity profile (mJy/beam)
            return radial_profile, rad_prof_scatter, rtmap
        else:
            return rtmap

    def plot_cont_intensity(self, ax, size, cmap ='magma', vmin =None, vmax = None, alpha = False, gamma = 1.0, contours=False, labels_off = False, show_beam = True, norm = None):
        """Plots continuum image"""        
        
        imshifted = shift(self.image, np.array([-self.offsety/self.delt_y+0.5,-self.offsetx/self.delt_x+0.5]))

        imgdata = imshifted*1000 #convert to mJy/beam if this is an intensity image

        size_pix = size/np.abs(self.delt_x) #size of zoomed-in image in pixels

        padding = int(0.5*(self.imsize-size_pix))

        std =np.std(imgdata[int(0.2*padding):padding, int(0.2*padding):padding])
        n = np.arange(4,26)
        levels = std*np.append([4,8],2**n)
        
        zoomimgdata = imgdata[padding:self.imsize - padding, padding:self.imsize - padding]
        
        zoomimgdata = np.fliplr(zoomimgdata) #since reversing the x-axis later will flip the image around, we have to flip it back
        if show_beam:
            self.beam_plot(0.4*size,-0.4*size,ax,flip =  True)

        if not vmin:
            vmin = 0
        if not vmax:
            vmax = np.max(zoomimgdata)

        if norm:
            finalimage = ax.imshow(zoomimgdata,origin='lower',cmap=cmap,norm = norm,  interpolation='None', extent=[-size/2., size/2., -size/2., size/2.])
        else:
            finalimage = ax.imshow(zoomimgdata,origin='lower',cmap=cmap,vmin = vmin, vmax=vmax, interpolation='None', extent=[-size/2., size/2., -size/2., size/2.])
        if contours: 
            cont = ax.contour(zoomimgdata,levels,linestyles='solid',colors='white', extent=[-size/2., size/2., -size/2., size/2.], linewidths = .5)
        ax.xaxis.tick_top()
        
        if labels_off:
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            ticks = np.arange(-np.floor(size)/2., np.floor(size)/2+0.5, 2)
            ax.set_xticks(ticks)

            plt.setp(ax.get_xticklabels(), size=12)
            ax.yaxis.set_label_coords(-.12,0.5)
            ax.set_yticks(ticks)

            plt.setp(ax.get_yticklabels(), size=12)


        plt.gca().invert_xaxis() #since RA increases right to left 
        return finalimage

    def beam_plot(self, x, y, ax, flip = False, color = 'white'):
        """Retrieves parameters for drawing the synthesized beam"""
        beam = Ellipse(xy=(x, y), width=self.bmin, height=self.bmaj, angle=self.bpa, facecolor=color, edgecolor = color)
        if flip:
            #this option is for if the axes are labeled with the RA and DEC, since the image gets flipped around
            beam = Ellipse(xy=(x, y), width=self.bmin, height=self.bmaj, angle=-self.bpa, facecolor=color, edgecolor = color)
        ax.add_artist(beam) 
        
    def circularize(self):
        shifted = ndimage.shift(self.image.T, (-self.offsetx/self.delt_x+0.5,-self.offsety/self.delt_y+0.5))
        rotated = transform.rotate(shifted, 180-self.PA) #ccw
        rescaled = transform.rescale(rotated, (1/np.cos(self.incl*np.pi/180.),1), preserve_range = False)
        return rescaled

    def extract_ring_old(self,rmin,rmax,tbins = -179.5+np.arange(360), twidth = 1, extract_type = 'max', return_rvals = False): 
        """
        Extracts pixels corresponding to local maxima 

        Parameters
        ==========
        rmin: Inner radius of annulus over which local maxima/minima are being identified
        rmax: Outer radius of annulus over which local maxima/minima are being identified
        tbins: Array denoting the centers of the azimuthal bins in which the local max/min is being identified(in degrees)
        twidth: Width (in degrees) of each azimuthal search bin (should be less than or equal to the separation between the bin centers)
        extract_type: 'max' yields local maxima, 'min' yields local minima

        Returns
        ======
        xcoord, ycoord: Arrays of coordinates (in arcsec) of the pixels correponding to the local maxima/minima
        """
        
        xcoord = []
        ycoord = []
        rvals = []
        assert twidth<=np.min(np.abs(np.diff(tbins)))
        annulus_intensities = self.image[(self.r>rmin) & (self.r<rmax)]
        annulus_thetas = self.theta[(self.r>rmin) & (self.r<rmax)]
        for j in range(len(tbins)):
            wedge = annulus_intensities[(annulus_thetas>=(tbins[j]-0.5*twidth)) & (annulus_thetas<(tbins[j]+0.5*twidth))]
            if len(wedge) > 0.:
                if extract_type=='max':
                    index = np.where(wedge==np.max(wedge))[0][0]
                elif extract_type=='min':
                    index = np.where(wedge==np.min(wedge))[0][0]
                xcoord.append(self.xx[(self.r>rmin) & (self.r<rmax)][(annulus_thetas>=(tbins[j]-0.5*twidth)) & (annulus_thetas<(tbins[j]+0.5*twidth))][index])
                ycoord.append(self.yy[(self.r>rmin) & (self.r<rmax)][(annulus_thetas>=(tbins[j]-0.5*twidth)) & (annulus_thetas<(tbins[j]+0.5*twidth))][index])
                if return_rvals:
                     rvals.append(self.r[(self.r>rmin) & (self.r<rmax)][(annulus_thetas>=(tbins[j]-0.5*twidth)) & (annulus_thetas<(tbins[j]+0.5*twidth))][index])
        if return_rvals:
            return np.array(xcoord)+self.offsetx, np.array(ycoord)+self.offsety, np.array(rvals)
             

        else:
            return np.array(xcoord)+self.offsetx, np.array(ycoord)+self.offsety

    def extract_ring(self,rmin,rmax,tbins = -179.5+np.arange(360), extract_type = 'max'): 
        """
        Extracts pixels corresponding to local maxima 

        Parameters
        ==========
        rmin: Inner radius of annulus over which local maxima/minima are being identified
        rmax: Outer radius of annulus over which local maxima/minima are being identified
        tbins: Array denoting the centers of the azimuthal bins in which the local max/min is being identified(in degrees)
        twidth: Width (in degrees) of each azimuthal search bin (should be less than or equal to the separation between the bin centers)
        extract_type: 'max' yields local maxima, 'min' yields local minima

        Returns
        ======
        xcoord, ycoord: Arrays of coordinates (in arcsec) of the pixels correponding to the local maxima/minima
        """
        xcoord = []
        ycoord = []


        xdiff = self.x_prime[0,0]-self.x_prime[1,0]
        ydiff = self.y_prime[0,0]-self.y_prime[0,1]
        tbins=tbins*np.pi/180.
        for j in range(len(tbins)):
            xpstart = rmin*np.cos(tbins[j])/self.src_distance*np.cos(self.incl*np.pi/180.)
            ypstart = rmin*np.sin(tbins[j])/self.src_distance

            PAr = self.PA*np.pi/180.
            xstart = np.int((xpstart*np.cos(-PAr)-ypstart*np.sin(-PAr)+self.offsetx)/self.delt_x+self.imsize/2)
            ystart = np.int((xpstart*np.sin(-PAr)+ypstart*np.cos(-PAr)+self.offsety)/self.delt_y+self.imsize/2)

        
            xpend = rmax*np.cos(tbins[j])/self.src_distance*np.cos(self.incl*np.pi/180.)
            ypend = rmax*np.sin(tbins[j])/self.src_distance
            xend = np.int((xpend*np.cos(-PAr)-ypend*np.sin(-PAr)+self.offsetx)/self.delt_x+self.imsize/2)
            yend = np.int((xpend*np.sin(-PAr)+ypend*np.cos(-PAr)+self.offsety)/self.delt_y+self.imsize/2)
            profile = measure.profile_line(self.image, (ystart,xstart), (yend, xend), order= 0)
            if extract_type=='max':
                index = np.where(profile==np.max(profile))[0][0]
            elif extract_type=='min':
                index = np.where(profile==np.min(profile))[0][0]
            if index!=0 and index!=len(profile)-1:
                loc = np.where(self.image[(self.r>rmin) & (self.r<rmax)]==profile[index])


                xcoord.append(self.xx[(self.r>rmin) & (self.r<rmax)][loc[0][0]])
                ycoord.append(self.yy[(self.r>rmin) & (self.r<rmax)][loc[0][0]])
            
        return np.array(xcoord)+self.offsetx, np.array(ycoord)+self.offsety

    def plot_extracted_ring(self,cont,xcoords, ycoords, gamma, size, cmap = 'magma'):
        f = plt.figure(figsize=(7,7))
        LBmap = plt.subplot(111, aspect = 'equal', adjustable = 'box')
        self.plot_cont_intensity(LBmap, size, cmap = cmap, vmin = 2.e-2, norm = col.PowerNorm(gamma = gamma))
        plt.scatter(xcoords-self.offsetx, ycoords-self.offsety, s = 1, color = 'white')
        return LBmap

    def plotbeamprofile(self, x,y, height, ax):
        bmin = self.bmin*self.src_distance
        sigma = bmin/(2*np.sqrt(2*np.log(2.)))
        xvals = np.linspace(x-2.5*bmin, x+2.5*bmin)
        ax.plot(xvals, y+height*np.exp(-(xvals-x)**2/(2*sigma**2)), color = 'gray')
                    
