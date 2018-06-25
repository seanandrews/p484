# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#%matplotlib inline
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.patches import Ellipse, Circle

from matplotlib.colors import LogNorm
from matplotlib.colors import SymLogNorm

from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy import ndimage
from scipy.optimize import curve_fit

#import matplotlib.cm as cm
from astropy.io import fits

SMALL_SIZE = 20
MEDIUM_SIZE = 25
BIGGER_SIZE = 30

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

# Define ellipse in polar coordinates where a is semi-major axis, b is 
# the semi-minor axis, and pa is the position angle. 
# x is the array containing the point on which the ellipse is defined
def PolarEllipse(xx, aa, bb, pp):
        return (aa*bb/np.sqrt((bb*np.cos(xx-pp))**2+(aa*np.sin(xx-pp))**2))


# a is the major axis, b is the minor axis        
def ErrIncl(a, da, b, db):
    return (1./a*(1.-b/a)**(-0.5)*((b/a*da)**2+db**2)**(0.5))

# Initial guess of the disk inclination and PA
pa = 133
incl = 47

pa_rad = pa*np.pi/180.
incl_rad = incl*np.pi/180.

# read fits image
image = '/Users/ai14/Papers/HD163296_ALMA_LP/data/HD163296_script_image.fits'
image_data = fits.getdata(image)
image_data = image_data[0,0,:,:]
#print(image_data.shape)

bmaj = 1.550974427826E-05*3600. # arcsec
bmin = 1.263048085901E-05*3600. # deg
bpa = 8.847134399414E+01  # deg

print('> Beam size (arcsec)',bmaj, bmin)

dimx=image_data.shape[0]
dimy=image_data.shape[1]

pixsize=0.005
xc=dimx/2+1
yc=dimy/2+1
xmin=0
xmax=dimx
ymin=0
ymax=dimx

# Make sure the axis orientation is correct (RA increasing toward east) 
fig, ax = plt.subplots(ncols=1, figsize=(20,20))
#plt.suptitle('Figure 1')
#
# Full image
#
img=ax.imshow(image_data, extent=((xmax-xc)*pixsize,(xmin-xc)*pixsize,
       (ymax-yc)*pixsize,(ymin-yc)*pixsize), cmap='magma', interpolation=None, 
        norm=SymLogNorm(linthresh=1.e-3, linscale=1.5, vmin=-1.e-5, vmax=6.e-3))
ax.set_xlim(2,-2)
ax.set_ylim(-2,2)
ax.set_xlabel('')
ax.set_ylabel('')

# set the beam ellipse
#ae=Ellipse((1, -1), width=bmin, height=bmaj, angle=bpa, color='white')
#ax.add_artist(ae)

# set colorbar
#divider = make_axes_locatable(ax)
#cax = divider.append_axes("right", size="5%", pad=0.05)
#cbar = fig.colorbar(img, cax=cax, label='')

plt.savefig('cont_single.pdf', bboxinches='tight')

plt.show()

fig, ax = plt.subplots(ncols=1, figsize=(8,8))
#plt.suptitle('Figure 1')
#
# Full image
#
img=ax.imshow(image_data, extent=((xmax-xc)*pixsize,(xmin-xc)*pixsize,
       (ymax-yc)*pixsize,(ymin-yc)*pixsize), cmap='magma', interpolation='bicubic', 
        norm=SymLogNorm(linthresh=1.e-3, linscale=1.5, vmin=6.e-4, vmax=1.2e-3))
ax.set_xlim(0.64,0.24)
ax.set_ylim(-0.5,-0.1)
ax.set_xlabel('')
ax.set_ylabel('')

# set the beam ellipse
#ae=Ellipse((1, -1), width=bmin, height=bmaj, angle=bpa, color='white')
#ax.add_artist(ae)

# set colorbar
#divider = make_axes_locatable(ax)
#cax = divider.append_axes("right", size="5%", pad=0.05)
#cbar = fig.colorbar(img, cax=cax, label='')

plt.savefig('cont_inset1.pdf', bboxinches='tight')

plt.show()

fig, ax = plt.subplots(ncols=1, figsize=(8,8))
#plt.suptitle('Figure 1')
#
# Full image
#
img=ax.imshow(image_data, extent=((xmax-xc)*pixsize,(xmin-xc)*pixsize,
       (ymax-yc)*pixsize,(ymin-yc)*pixsize), cmap='magma', interpolation='bicubic', 
       vmin=2.7e-3, vmax=5.5e-3)
ax.set_xlim(0.2,-0.2)
ax.set_ylim(-0.2,+0.2)
ax.set_xlabel('')
ax.set_ylabel('')

# set the beam ellipse
#ae=Ellipse((1, -1), width=bmin, height=bmaj, angle=bpa, color='white')
#ax.add_artist(ae)

# set colorbar
#divider = make_axes_locatable(ax)
#cax = divider.append_axes("right", size="5%", pad=0.05)
#cbar = fig.colorbar(img, cax=cax, label='')

plt.savefig('cont_inset2.pdf', bboxinches='tight')

plt.show()
#
# plot image in cartesian coordinates
#

# Make sure the axis orientation is correct (RA increasing toward east) 
fig, axs = plt.subplots(ncols=3, figsize=(33,10))
plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9,
                wspace=0.3, hspace=None)
#plt.suptitle('Figure 1')
#
# Full image
#
img=axs[0].imshow(image_data, extent=((xmax-xc)*pixsize,(xmin-xc)*pixsize,
       (ymax-yc)*pixsize,(ymin-yc)*pixsize), cmap='magma', interpolation=None)
axs[0].set_xlim(1.2,-1.2)
axs[0].set_ylim(-1.2,1.2)
axs[0].set_xlabel(r'${\delta}$ RA (arcsec)')
axs[0].set_ylabel(r'${\delta}$ Dec (arcsec)')

# set the beam ellipse
ae=Ellipse((1, -1), width=bmin, height=bmaj, angle=bpa, color='white')
axs[0].add_artist(ae)

# set outer ring ellipse
#w3=2.
#ae=Ellipse((0, -0), width=w3, height=w3*np.cos(incl*np.pi/180.), angle=pa, color='white', fill=False)
#axs[0].add_artist(ae)

# set outer ring ellipse
#w2=1.4
#ae=Ellipse((0, -0), width=w2, height=w2*np.cos(incl*np.pi/180.), angle=pa, color='white', fill=False)
#axs[0].add_artist(ae)

# set colorbar
divider = make_axes_locatable(axs[0])
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = fig.colorbar(img, cax=cax, label='')

#
# zoom in on the tail
#
img1 = axs[1].imshow(image_data, extent=((xmax-xc)*pixsize,(xmin-xc)*pixsize,
              (ymax-yc)*pixsize,(ymin-yc)*pixsize), cmap='magma', vmin=4.e-4, 
              vmax=1.2e-3, interpolation=None)
axs[1].set_xlim(0.7,0.1)
axs[1].set_ylim(-0.65,-0.05)
axs[1].set_aspect('equal')

# set the beam ellipse
ae=Ellipse((0.65, -0.6), width=bmin, height=bmaj, angle=bpa, color='white')
axs[1].add_artist(ae)

# set colorbar
divider = make_axes_locatable(axs[1])
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = fig.colorbar(img1, cax=cax, label='')

#
# zoom in on the central regions
#
img2 = axs[2].imshow(image_data, extent=((xmax-xc)*pixsize,(xmin-xc)*pixsize,
              (ymax-yc)*pixsize,(ymin-yc)*pixsize), cmap='magma', vmin=2.7e-3, 
              vmax=5.5e-3, interpolation=None)
axs[2].set_xlim(0.2,-0.2)
axs[2].set_ylim(-0.2,0.2)
axs[2].set_aspect('equal')

# set the beam ellipse
ae=Ellipse((0.15, -0.15), width=bmin, height=bmaj, angle=bpa, color='white')
axs[2].add_artist(ae)

# set colorbar
divider = make_axes_locatable(axs[2])
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = fig.colorbar(img2, cax=cax, label=r'Flux Density (Jy beam$^{-1}$)')

plt.savefig('cont_show.pdf', bbox_inches='tight')

plt.draw()
plt.show()
#
#plot image in polar coordinates
#

# create polar grid for interpolation
dimr=1000
dr = np.sqrt((xmax-xc)**2+(ymax-yc)**2)/dimr*pixsize
rmax = pixsize*np.sqrt((xmax-xc)**2+(ymax-yc)**2)
r = np.arange(0, rmax ,dr)
print('> dr (arcsec) = ',dr)

dimtheta = 360
dtheta =2.*np.pi/dimtheta
theta = np.arange(0,2.*np.pi,dtheta)
print('> dtheta (deg)= ',dtheta*180./np.pi)

# theta increases from East to North
x_p = np.zeros(shape=(dimr*dimtheta))
y_p = np.zeros(shape=(dimr*dimtheta))
for i in range(dimr):
    for j in range(dimtheta):
        x_p[i+j*dimr] = xc-r[i]/pixsize*np.cos(theta[j])
        y_p[i+j*dimr] = yc+r[i]/pixsize*np.sin(theta[j])

# interpolate the image on the polar grid
polarimage = ndimage.map_coordinates(image_data, [x_p,y_p], order=1)

# create 2D image
polarimage2d = np.zeros(shape=(dimr,dimtheta))
for i in range(dimr):
        for j in range(dimtheta):
                polarimage2d[i][j]=polarimage[i+j*dimr]
                
# find the crest of the rings

# Define elliptic intervals to perform the search
a0h=int(1.1/dr)
b0h=int(0.8/dr)
r0h = PolarEllipse(theta, a0h, b0h, pa_rad)

a0l=int(0.8/dr)
b0l=int(0.6/dr)
r0l = PolarEllipse(theta, a0l, b0l, pa_rad)

a1h=int(0.8/dr)
b1h=int(0.6/dr)
r1h = PolarEllipse(theta, a1h, b1h, pa_rad)

a1l=int(0.50/dr)
b1l=int(0.30/dr)
r1l = PolarEllipse(theta, a1l, b1l, pa_rad)

a2h=int(0.5/dr)
b2h=int(0.3/dr)
r2h = PolarEllipse(theta, a2h, b2h, pa_rad)

a2l=int(0.13/dr)
b2l=int(0.098/dr)
r2l = PolarEllipse(theta, a2l, b2l, pa_rad)


# find the crest of each ring
rings = np.zeros(shape=(3,dimtheta), dtype=float)
for i in range(dimtheta):
    rings[0][i]=dr*(r0l[i]+np.argmax(polarimage2d[int(r0l[i]):int(r0h[i]),i]))
    rings[1][i]=dr*(r1l[i]+np.argmax(polarimage2d[int(r1l[i]):int(r1h[i]),i]))
    rings[2][i]=dr*(r2l[i]+np.argmax(polarimage2d[int(r2l[i]):int(r2h[i]),i]))
              
# fit ellipses to each ring
popt0, pcov0 = curve_fit(PolarEllipse, theta, rings[0], p0=(1.0,0.7,pa_rad))
popt1, pcov1 = curve_fit(PolarEllipse, theta, rings[1], p0=(0.7,0.5,pa_rad))
popt2, pcov2 = curve_fit(PolarEllipse, theta, rings[2], p0=(0.15,0.01,pa_rad))

print ('> ring0: a,  b,  pa_rad  =', popt0)
print ('> ring0: da, db, dpa_rad =', np.sqrt(pcov0[0][0]), np.sqrt(pcov0[1][1]), np.sqrt(pcov0[2][2]))
inclr0_rad = np.arccos(popt0[1]/popt0[0])
print ('> ring0: inclination (error) [deg] =', inclr0_rad*180./np.pi, 
       180./np.pi*ErrIncl(popt0[0],np.sqrt(pcov0[0][0]),popt0[1],np.sqrt(pcov0[1][1])) )

print ('> ring0: position angle (error) [deg] =', popt0[2]*180./np.pi, np.sqrt(pcov0[2][2])*180./np.pi)

print ('')
print ('> ring1: a, b, pa_rad =', popt1)
print ('> ring1: da, db, dpa_rad =', np.sqrt(pcov1[0][0]), np.sqrt(pcov1[1][1]), np.sqrt(pcov1[2][2]))
inclr1_rad = np.arccos(popt1[1]/popt1[0])
print ('> ring1: inclination (error) [deg] =', inclr1_rad*180./np.pi, 
           180./np.pi*ErrIncl(popt1[0],np.sqrt(pcov1[0][0]),popt1[1],np.sqrt(pcov1[1][1])))
print ('> ring1: position angle (error) [deg] =', popt1[2]*180./np.pi, np.sqrt(pcov1[2][2])*180./np.pi)

print('')
print ('> ring2: a, b, pa_rad =', popt2)
print ('> ring2: da, db, dpa_rad =', np.sqrt(pcov2[0][0]), np.sqrt(pcov2[1][1]), np.sqrt(pcov2[2][2]))
inclr2_rad = np.arccos(popt2[1]/popt2[0])
print ('> ring2: inclination (error) [deg] =', inclr2_rad*180./np.pi, 
           180./np.pi*ErrIncl(popt2[0],np.sqrt(pcov2[0][0]),popt2[1],np.sqrt(pcov2[1][1])))
print ('> ring2: position angle (error) [deg] =', popt2[2]*180./np.pi, np.sqrt(pcov2[2][2])*180./np.pi)

# Update value of the disk inclination and position angle
incl_rad = (inclr0_rad+inclr1_rad)/2.
pa_rad = (popt0[2]+popt1[2])/2.

print('')         
print(' ## Deprojecting using incl (deg) =',incl_rad*180./np.pi)
print(' ## Deprojecting using pa (deg)   =',pa_rad*180./np.pi)           
           

# plot image 
fig, ax = plt.subplots(figsize=(10,10))
#plt.suptitle('Figure 2')
img = ax.imshow(polarimage2d, cmap='magma', extent=(0, 360, rmax, 0), 
                    aspect='auto', interpolation=None)
plt.ylim(0,np.sqrt(2))
plt.xlim(0, 360)
plt.ylabel(r'${\delta}$ r (arcsec)')
plt.xlabel('theta')

plt.plot(theta*180./np.pi,rings[0], color='white')
plt.plot(theta*180./np.pi,PolarEllipse(theta, *popt0), color='blue')

plt.plot(theta*180./np.pi,rings[1], color='white')
plt.plot(theta*180./np.pi,PolarEllipse(theta, *popt1), color='blue')

plt.plot(theta*180./np.pi,rings[2], color='white')
plt.plot(theta*180./np.pi,PolarEllipse(theta, *popt2), color='blue')


#plt.plot(theta*180./np.pi,r2l*dr, color='grey')
#plt.plot(theta*180./np.pi,r2h*dr, color='grey')
#
#plt.plot(theta*180./np.pi,r1l*dr, color='grey')
#plt.plot(theta*180./np.pi,r1h*dr, color='grey')
#
#plt.plot(theta*180./np.pi,r0l*dr, color='grey')
#plt.plot(theta*180./np.pi,r0h*dr, color='grey')

divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = fig.colorbar(img, cax=cax, label=r'Flux Density (Jy beam$^{-1}$)')

plt.savefig('cont_polar.pdf', bbox_inches='tight')

plt.show()


#
# Plot deprojected images
#

# rotate cartesian image so that the major axis of the disk is aligned with the 
#x-axis, and deproject for the disk inclination


rot = pa_rad*180./np.pi-90.
image_data_rot = ndimage.interpolation.rotate(image_data, rot, reshape=False) 
 
fig, ax = plt.subplots(figsize=(10,10))
#plt.suptitle('Figure 3')
img = ax.imshow(image_data_rot, extent=((xmax-xc)*pixsize,(xmin-xc)*pixsize,
               (ymax-yc)*pixsize/np.cos(incl_rad),(ymin-yc)*pixsize/np.cos(incl_rad)), 
                cmap='magma')


plt.xlim(1.2,-1.2)
plt.ylim(-1.2,1.2)
plt.xlabel(r'${\delta}$ RA (arcsec)')
plt.ylabel(r'${\delta}$ Dec (arcsec)')
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = fig.colorbar(img, cax=cax, label=r'Flux Density (Jy beam$^{-1}$)')
#sincl='incl='+str(incl_rad*180./np.pi)
#spa='pa='+str(pa_rad*180./np.pi)
#ax.text(1, 1, sincl, color='white', fontsize=15)
#ax.text(1, 0.85, spa, color='white', fontsize=15)

# set the beam ellipse
ae=Circle(xy=(0.0, 0.0), radius=popt0[0], color='white', fill=False)
ax.add_artist(ae)

ae=Circle(xy=(0.0, 0.0), radius=popt1[0], color='white', fill=False)
ax.add_artist(ae)

ae=Circle(xy=(0.0, 0.0), radius=popt2[0], color='white', fill=False)
ax.add_artist(ae)

plt.savefig('cont_circular.pdf', bbox_inches='tight')

plt.show()

#
#plot image in polar coordinates
#

# create polar grid for interpolation
#dimr=300
#dr = np.sqrt((xmax-xc)**2+(ymax-yc)**2)/dimr*pixsize
#rmax = pixsize*np.sqrt((xmax-xc)**2+(ymax-yc)**2)
#r = np.arange(0, rmax ,dr)
#print(rmax)

#dimtheta = 260
#dtheta =2.*np.pi/dimtheta
#theta = np.arange(0.,2.*np.pi,dtheta)

## theta increases from East to North
x_p = np.zeros(shape=(dimr*dimtheta))
y_p = np.zeros(shape=(dimr*dimtheta))
for i in range(dimr):
    for j in range(dimtheta):
        x_p[i+j*dimr] = xc+r[i]/pixsize*np.sin(theta[j])*np.cos(incl_rad)
        y_p[i+j*dimr] = yc-r[i]/pixsize*np.cos(theta[j])
        
# interpolate the image on the polar grid
polarimage_rot = ndimage.map_coordinates(image_data_rot, [x_p,y_p], order=1)

# create 2D image
polarimage2d_rot = np.zeros(shape=(dimr,dimtheta))
for i in range(dimr):
        for j in range(dimtheta):
                polarimage2d_rot[i][j]=polarimage_rot[i+j*dimr]
                
               
# plot image 
fig, axs = plt.subplots(ncols=2, figsize=(22,10))
plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9,
                wspace=0.3, hspace=None)
#plt.suptitle('Figure 4')

#img = axs[0].imshow(polarimage2d_rot, cmap='magma', extent=(0, 360, rmax, 0), 
#                  interpolation='bicubic', aspect='auto', 
#                  norm=LogNorm(vmin=1.e-4, vmax=1.e-2))
polarimage2d_t = np.transpose(polarimage2d_rot)
img = axs[0].imshow(polarimage2d_t, cmap='magma', extent=(0, rmax, 0, 360), 
                  interpolation=None, aspect='auto', 
                  norm=LogNorm(vmin=1.e-4, vmax=1.e-2))

axs[0].set_xlim(0,1.2)
axs[0].set_ylim(0, 360)
axs[0].set_xlabel(r'${\delta}$ r (arcsec)')
axs[0].set_ylabel(r'$\theta$ (deg)')
axs[0].plot([popt0[0],popt0[0]],[0,360], color='white', lw=1)
axs[0].plot([popt1[0],popt1[0]],[0,360], color='white', lw=1)
axs[0].plot([popt2[0],popt2[0]],[0,360], color='white', lw=1)
divider = make_axes_locatable(axs[0])
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = fig.colorbar(img, cax=cax, label='')


img = axs[1].imshow(polarimage2d_t*r, cmap='magma', extent=(0, rmax, 0, 360), 
                  interpolation=None, aspect='auto',  
                  norm=LogNorm(vmin=1.e-4, vmax=np.max(polarimage2d_t*r)))
axs[1].set_xlim(0,1.2)
axs[1].set_ylim(0, 360)
axs[1].set_xlabel(r'${\delta}$ r (arcsec)')
axs[1].set_ylabel(r'')
axs[1].plot([popt0[0],popt0[0]],[0,360], color='white', lw=1)
axs[1].plot([popt1[0],popt1[0]],[0,360], color='white', lw=1)
axs[1].plot([popt2[0],popt2[0]],[0,360], color='white', lw=1)
divider = make_axes_locatable(axs[1])
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = fig.colorbar(img, cax=cax, label=r'(Jy beam$^{-1}$)')

plt.savefig('cont_circular_polar.pdf', bbox_inches='tight')

plt.show()

#
# plot radial profile
#
rpmean = np.mean(polarimage2d_rot, axis=1)
rpvar  = np.std(polarimage2d_rot, axis=1)
fig, ax = plt.subplots(figsize=(10,10))
ax.set_yscale('linear')
#plt.title('Figure5')
plt.errorbar(r,rpmean/rpmean.max(), yerr=rpvar/rpmean.max())
plt.xlabel('radius (arcsec)')
plt.ylabel('Normalized intensity')
ax.set_ylim(0,1.1)
ax.set_xlim(0,1.2)

#plt.semilogy(r, rpmean, label='mean')
#plt.xlabel('radius(arcsec)')
#plt.xlim(0,1.2)
#plt.ylim()
plt.savefig('cont_radial_profile.pdf', bbox_inches='tight')
plt.show()




# plot image of I-I_mean
fig, axs = plt.subplots(ncols=2, figsize=(22,10))
plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9,
                wspace=0.3, hspace=None)

#plt.title('Figure 6')

#img = axs[0].imshow(polarimage2d_rot, cmap='magma', extent=(0, 360, rmax, 0), 
#                  interpolation='bicubic', aspect='auto', 
#                  norm=LogNorm(vmin=1.e-4, vmax=1.e-2))
polarimage2d_t = np.transpose(polarimage2d_rot)
img = axs[0].imshow((polarimage2d_t-rpmean)/rpmean, cmap='magma', extent=(0, rmax, 0, 360), 
                  interpolation=None, aspect='auto', vmin=-2, vmax=2)

axs[0].set_xlim(0,1.2)
axs[0].set_ylim(0, 360)
axs[0].set_xlabel(r'${\delta}$ r (arcsec)')
axs[0].set_ylabel(r'${\theta}$ (deg)')
axs[0].plot([popt0[0],popt0[0]],[0,360], color='white', lw=1)
axs[0].plot([popt1[0],popt1[0]],[0,360], color='white', lw=1)
axs[0].plot([popt2[0],popt2[0]],[0,360], color='white', lw=1)
divider = make_axes_locatable(axs[0])
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = fig.colorbar(img, cax=cax, label=r'')


img = axs[1].imshow((polarimage2d_t-rpmean)/rpmean, cmap='magma', extent=(0, rmax, 0, 360), 
                  interpolation=None, aspect='auto', vmin=-0.5, vmax=0.5)

axs[1].set_xlim(0,1.2)
axs[1].set_ylim(0, 360)
axs[1].set_xlabel(r'${\delta}$ r (arcsec)')
axs[1].set_ylabel('')
axs[1].plot([popt0[0],popt0[0]],[0,360], color='white', lw=1)
axs[1].plot([popt1[0],popt1[0]],[0,360], color='white', lw=1)
axs[1].plot([popt2[0],popt2[0]],[0,360], color='white', lw=1)
divider = make_axes_locatable(axs[1])
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = fig.colorbar(img, cax=cax, label=r'')

plt.savefig('cont_dev.pdf', bbox_inches='tight')
plt.show()


# calcualte the image of the residual (Image(x,y)-Mean_Image(x,y))
mean_data_rot = np.empty([dimx,dimy])
#mean_data_rot = image_data_rot

print('incl_rad=',incl_rad)
for i in range(int(xc-5),int(xc+5)):
        for j in range(int(yc-5),int(yc+5)):
                
                tt = np.arctan2((j-yc),(i-xc))    
                if (tt<0): 
                    tt=2.*np.pi+tt
                 
                rr=0.
                
                if ((i-xc)==0):
                        rr = np.fabs(j-yc)*pixsize*np.cos(incl_rad)
                elif ((j-yc)==0):
                        rr = np.fabs(i-xc)*pixsize
                else: 
                    rr = PolarEllipse(tt,np.fabs(i-xc)*pixsize, np.fabs(j-yc)*pixsize*np.cos(incl_rad), 0.)                
#                
#                if (rr<0 or rr>rmax):
#                        print('## Error: rr out of bound',rr,i,j)

                rr =  np.sqrt((i-xc)**2+(j-yc)**2)*pixsize
                mean_data_rot[i][j]=np.interp(rr,r,rpmean)
                print(i-xc, j-yc ,tt, rr, np.fabs(j-yc)*pixsize*np.cos(incl_rad))



fig, ax = plt.subplots(figsize=(10,10))
plt.suptitle('Figure 8')
#img = ax.imshow(mean_data_rot, extent=((xmax-xc)*pixsize,(xmin-xc)*pixsize,
#               (ymax-yc)*pixsize/np.cos(incl_rad),(ymin-yc)*pixsize/np.cos(incl_rad)), 
#                cmap='magma')

img = ax.imshow(mean_data_rot, extent=((xmax-xc)*pixsize,(xmin-xc)*pixsize,
               (ymax-yc)*pixsize,(ymin-yc)*pixsize), 
                cmap='magma')

plt.xlim(1.2,-1.2)
plt.ylim(-1.2,1.2)
plt.xlabel(r'${\delta}$ RA (arcsec)')
plt.ylabel(r'${\delta}$ Dec (arcsec)')
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = fig.colorbar(img, cax=cax, label=r'Flux Density (Jy beam$^{-1}$)')
#sincl='incl='+str(incl_rad*180./np.pi)
#spa='pa='+str(pa_rad*180./np.pi)
#ax.text(1, 1, sincl, color='white', fontsize=15)
#ax.text(1, 0.85, spa, color='white', fontsize=15)

# set the beam ellipse
ae=Circle(xy=(0.0, 0.0), radius=popt0[0], color='white', fill=False)
ax.add_artist(ae)

ae=Circle(xy=(0.0, 0.0), radius=popt1[0], color='white', fill=False)
ax.add_artist(ae)

ae=Circle(xy=(0.0, 0.0), radius=popt2[0], color='white', fill=False)
ax.add_artist(ae)

plt.show()
