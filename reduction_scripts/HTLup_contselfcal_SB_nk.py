#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ../../lperez/casa_5.1.1/casa-release-5.1.1-5.el7/bin/casa

#####################################################
# HT Lup Self-Calibration: Short Baselines          #
#####################################################

'''
Universidad de Chile
Facultad de Ciencias Fisicas y Matematicas
Departamento de Astronomia

Nicolas Troncoso Kurtovic
mail: nicokurtovic at gmail.com

This script was written for CASA 5.1.1 to
self-calibrate the short baselines HTLup dataset
'''

import numpy as np
import matplotlib.pyplot as plt
execfile('reduction_utils.py')

import sys
sys.path.append('/almadata02/nkurtovic/HTLup/analysis_scripts/')
import analysisUtils as au


#####################################################
#                 NAMES AND PATH                    #
#####################################################

# Direction of the directory where the data is
directory = ''
# Name of the dataset
# obs = 'calibrated_final.ms' # LB
obs_SB = 'htlup_p484_SB.ms' # SB
obs_LB = 'calibrated_final.ms' # LB
# Build the path
path_SB = directory + obs_SB
path_LB = directory + obs_LB

# Name of the object
prefix = 'HTLup'
field = 'HT_Lup'

skip_plots=True#False

#####################################################
#                     PARAMETERS                    #
#                 AND LINE FLAGGING                 #
#####################################################

'''
To flag the CO line, we proceed inspecting by eye the
location in channels and spw.
Flag ~50 km/s around 12CO 2-1 line. Each channel in
these spectral windows has 0.635 km/s, so we need to
flag ~320 channels in total. (each channel is half that
speed to take the mean and ALMA stuff)
The center of the peak is around -6km/s.
'''

# Frequency of 12CO 2-1 line
rest_freq = 2.30538e11
# Scales # arbitrary
scales = [0]

if not skip_plots:
    # Plot the amplitude of each channel, in groups of spw
    plotms(vis=path_SB, xaxis='channel', yaxis='amplitude', \
           avgtime='1e8', ydatacolumn='data', field=field, \
           avgscan=True, avgbaseline=True, iteraxis='spw', \
           restfreq=str(rest_freq))

# Line is centered in channel ~1920 in sectral window
# number 0 and 3.

# Numbers of the spectral windows.
cont_spws = '0~7'
# Tentative Channels and spw where to flag.
# flag_channels = '0:1760~2080, 4:1760~2080'
# Save before flagging.
#os.system('rm -rf '+path+'.flagversions/flags.before_cont_flags*')
#flagmanager(vis=path_SB, mode='save', versionname='before_cont_flags')

# Build the dictionary. path is the direction of the data, 
# and line_spws are the windows where the lines need to
# be flagged.
data_params = {'SB': {'vis' : path_SB, \
                      'name': 'SB', \
                      'field': field, \
                      'line_spws': np.array([0, 4]), \
                      'line_freqs': np.array([rest_freq, rest_freq])}}

# Find the channels that will be flagged.
SB_flagchannels = get_flagchannels(data_params['SB'], prefix,\
                                   velocity_range=np.array([-56., 44.]))

# Average continuum. This will generate the prefix+_SB_initcont.ms
avg_cont(data_params['SB'], prefix, flagchannels=SB_flagchannels)


#####################################################
#              DEFINE MASK, FIRST IMAGE             #
#####################################################


# Image the ms file interactively. Inspection to define the mask
if not skip_plots:
    tclean_wrapper(vis=prefix+'_SB_initcont.ms', \
                   imagename=prefix+'_SB_initcont', \
                   scales=[0], imsize=900, interactive=True)

# Define masks manually from the inspection
# First obj centroid in [451, 445]
xp, yp = '451', '445' # centroid
Ap, Bp = '13', '15'   # size in each axis
# Second obj in [535, 488]
xs, ys = '535', '488' # centroid
As, Bs = '7', '12'     # size in each axis
# First object Mask
mask1_SB = 'ellipse[['+xp+'pix, '+yp+'pix], ['+Ap+'pix, '+Bp+'pix], 0rad]'
# Second object Mask
mask2_SB = 'ellipse[['+xs+'pix, '+ys+'pix], ['+As+'pix, '+Bs+'pix], 0rad]'

# Create the mask
os.system('rm -rf '+prefix+'_mask1_SB.mask')
os.system('rm -rf '+prefix+'_mask2_SB.mask')
makemask(mode='copy', inpimage=prefix+'_SB_initcont.mask', \
         inpmask=mask1_SB, output=prefix+'_mask1_SB.mask', \
         overwrite=False)
makemask(mode='copy', inpimage=prefix+'_SB_initcont.mask', \
         inpmask=mask2_SB, output=prefix+'_mask2_SB.mask', \
         overwrite=False)
mask_SB = [prefix+'_mask1_SB.mask', prefix+'_mask2_SB.mask']

# Calculate distance between sources
from numpy import sqrt
dist = sqrt((float(xp)-float(xs))**2 + (float(yp)-float(ys))**2)

# Create a residual mask
res_mask_SB = 'annulus[['+xp+'pix, '+yp+'pix], ['+str(int(dist + 30))+'pix, 400pix]]'

# Create the file of the mask
os.system('rm -rf '+prefix+'_res_mask_SB.mask')
makemask(mode='copy', inpimage=prefix+'_SB_initcont.mask', inpmask=res_mask_SB, output=prefix+'_res_mask_SB.mask', overwrite=False)


# Image non interactively
tclean_wrapper(vis=prefix+'_SB_initcont.ms', \
               imagename=prefix+'_SB_initcont', \
               mask=mask_SB, \
               scales=[0, 3, 9, 15], \
               imsize=900, \
               savemodel='modelcolumn', \
               interactive=False)

# Image each observation. For SB there are two of them
image_each_obs(data_params['SB'], prefix, scales, mask=mask_SB)

# Fit gaussian to find the central peak in the image.
# The mask must be a string, not the mask file.

fit_gaussian(prefix+'_SB_initcont_exec0.image', \
             region=mask1_SB)
#15h45m12.847765s -34d17m31.03292s
#Peak of Gaussian component identified with imfit: ICRS 15h45m12.847765s -34d17m31.03292s
#15:45:12.847765 -34:17:31.03292
#Separation: radian = 7.85539e-08, degrees = 0.000005, arcsec = 0.016203
#Peak in J2000 coordinates: 15:45:12.84828, -034:17:31.018027
#Pixel coordinates of peak: x = 451.473 y = 445.391
#PA of Gaussian component: 169.37 deg
#Inclination of Gaussian component: 40.41 deg

fit_gaussian(prefix+'_SB_initcont_exec1.image', \
             region=mask1_SB)
#15h45m12.847684s -34d17m31.04494s
#Peak of Gaussian component identified with imfit: ICRS 15h45m12.847684s -34d17m31.04494s
#15:45:12.847684 -34:17:31.04494
#Separation: radian = 7.85731e-08, degrees = 0.000005, arcsec = 0.016207
#Peak in J2000 coordinates: 15:45:12.84820, -034:17:31.030048
#Pixel coordinates of peak: x = 451.506 y = 444.990
#PA of Gaussian component: 150.29 deg
#Inclination of Gaussian component: 38.87 deg

fit_gaussian(prefix+'_SB_initcont.image', \
             region=mask1_SB)
# 15h45m12.847703s -34d17m31.04081s
# Peak of Gaussian component identified with imfit: ICRS 15h45m12.847703s -34d17m31.04081s
# 15:45:12.847703 -34:17:31.04081
# Separation: radian = 7.86013e-08, degrees = 0.000005, arcsec = 0.016213
# Peak in J2000 coordinates: 15:45:12.84822, -034:17:31.025917
# Pixel coordinates of peak: x = 451.498 y = 445.128
# PA of Gaussian component: 157.59 deg
# Inclination of Gaussian component: 39.02 deg

# Difference between peaks is negligible. We are going
# to choose the central peak of them together as the
# center
center_ra = '15h45m12.847703s'
center_dec = '-34d17m31.04081s'
center_SB = center_ra + ' ' + center_dec


#####################################################
#               SB SELF-CALIBRATION 0               #
#####################################################

# Split the data to continue with the calibrations
os.system('rm -rf '+prefix+'_SB_selfcal_0.ms*')
split(vis=prefix+'_SB_initcont.ms',
      outputvis=prefix+'_SB_selfcal_0.ms',
      datacolumn='data')

# Robust level
robust = 0.5

# Calculate residual of the noise in the
# previous imaging.
residual_1 = imstat(imagename=prefix+'_SB_initcont.image', mask=prefix+'_res_mask_SB.mask')
rms = residual_1['rms'][0]  #rms in Jy
# 0.00012656644618971375 Jy
# 0.12656644618971375

# First Clean for selfcalibration
tclean_wrapper(vis=prefix+'_SB_selfcal_0.ms', \
               imagename=prefix+'_SB_1first', \
               mask=mask_SB, \
               scales=scales, \
               robust=robust, \
               threshold=str(2*rms*10**3)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
stats_first = imstat(imagename=prefix+'_SB_1first.image')
residual_1 = imstat(imagename=prefix+'_SB_1first.image', mask=prefix+'_res_mask_SB.mask')
max_1 = stats_first['max'][0]
res_rms_1 = residual_1['rms'][0]   # 20.7 microJy
snr_1 = stats_first['max'][0] / residual_1['rms'][0]

# max (0.046605717390775681 with robust 0.0)
# 0.050779607146978378
# rms of noise mJy (0.13635040640142518 with 0.0)
# 0.12659586070594712
# snr
# 401.115856899363

# First self-calibration
os.system('rm -rf '+prefix+'_phase_1.cal')
gaincal(vis=prefix+'_SB_selfcal_0.ms',
        caltable=prefix+'_phase_1.cal',
        field='0',
        solint='inf',
        calmode='p',
        gaintype='T',
        combine='scan',
        spw=cont_spws,
        minsnr=1.5,
        minblperant=4)
# combine scan only when solint is larger than scan lenght

'''
None solutions were flagged
'''

if not skip_plots:
    # Plot the first phase calibration
    plotcal(caltable=prefix+'_phase_1.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/14/00~2017/05/15/00',
            markersize=5,
            fontsize=10.0,
            figfile=prefix+'_phase_1a.png',
            showgui=True)

    plotcal(caltable=prefix+'_phase_1.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/16/00~2017/05/18/00',
            markersize=5,
            fontsize=10.0,
            figfile=prefix+'_phase_1b.png',
            showgui=True)

# Apply calibration
applycal(vis=prefix+'_SB_selfcal_0.ms',
         field='0',
         gaintable=[prefix+'_phase_1.cal'],
         spwmap=[0]*8,
         interp='linearPD',
         calwt=True,
         applymode='calonly')

# Split the data to continue with the calibrations
os.system('rm -rf '+prefix+'_SB_selfcal_1.ms')
split(vis=prefix+'_SB_selfcal_0.ms',
      outputvis=prefix+'_SB_selfcal_1.ms',
      datacolumn='corrected')

#####################################################
#                 Self-Calibration 2                #
#####################################################

# Second Clean for selfcalibration
tclean_wrapper(vis=prefix+'_SB_selfcal_1.ms', \
               imagename=prefix+'_SB_2second', \
               mask=mask_SB, \
               scales=scales, \
               robust=robust, \
               threshold=str(1.5*res_rms_1*10**3)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
stats_second = imstat(imagename=prefix+'_SB_2second.image')
residual_2 = imstat(imagename=prefix+'_SB_2second.image', mask=prefix+'_res_mask_SB.mask')
max_2 = stats_second['max'][0]
res_rms_2 = residual_2['rms'][0]
snr_2 = stats_second['max'][0] / residual_2['rms'][0]

# max / increase 1.0078139999077107
# 0.051176398992538452
# rms of noise Jy / decrease 0.96579355840203462
# 0.00012226546679016499
# snr / increase 1.0435087199951938
# 418.56789440282961


# First self-calibration
os.system('rm -rf '+prefix+'_phase_2.cal')
gaincal(vis=prefix+'_SB_selfcal_1.ms',
        caltable=prefix+'_phase_2.cal',
        field='0',
        solint='120',
        calmode='p',
        gaintype='T',
        combine='scan',
        spw=cont_spws,
        minsnr=1.5,
        minblperant=4)
# combine scan only when solint is larger than scan lenght

'''
None solutions were flagged
'''

if not skip_plots:
    # Plot the first phase calibration
    plotcal(caltable=prefix+'_phase_2.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/14/00~2017/05/15/00',
            markersize=5,
            fontsize=10.0,
            figfile=prefix+'_phase_2a.png',
            showgui=True)

    plotcal(caltable=prefix+'_phase_2.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/16/00~2017/05/18/00',
            markersize=5,
            fontsize=10.0,
            figfile=prefix+'_phase_2b.png',
            showgui=True)

# Apply calibration
applycal(vis=prefix+'_SB_selfcal_1.ms',
         field='0',
         gaintable=[prefix+'_phase_2.cal'],
         spwmap=[0]*8,
         interp='linearPD',
         calwt=True,
         applymode='calonly')

# Split the data to continue with the calibrations
os.system('rm -rf '+prefix+'_SB_selfcal_2.ms')
split(vis=prefix+'_SB_selfcal_1.ms',
      outputvis=prefix+'_SB_selfcal_2.ms',
      datacolumn='corrected')


#####################################################
#                 Self-Calibration 3                #
#####################################################


# Third Clean for selfcalibration
tclean_wrapper(vis=prefix+'_SB_selfcal_2.ms', \
               imagename=prefix+'_SB_3third', \
               mask=mask_SB, \
               scales=scales, \
               robust=robust, \
               threshold=str(1.5*res_rms_2*10**3)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
stats_third = imstat(imagename=prefix+'_SB_3third.image')
residual_3 = imstat(imagename=prefix+'_SB_3third.image', mask=prefix+'_res_mask_SB.mask')
max_3 = stats_third['max'][0]
res_rms_3 = residual_3['rms'][0]
snr_3 = stats_third['max'][0] / residual_3['rms'][0]

# max / increase 1.0078139999077107
# 0.051176398992538452
# rms of noise Jy / decrease 0.96579355840203462
# 0.00012226546679016499
# snr / increase 1.0435087199951938
# 418.56789440282961


# First self-calibration
os.system('rm -rf '+prefix+'_phase_2.cal')
gaincal(vis=prefix+'_SB_selfcal_1.ms',
        caltable=prefix+'_phase_2.cal',
        field='0',
        solint='180',
        calmode='p',
        gaintype='T',
        combine='scan',
        spw=cont_spws,
        minsnr=1.5,
        minblperant=4)
# combine scan only when solint is larger than scan lenght

'''
None solutions were flagged
'''

if not skip_plots:
    # Plot the first phase calibration
    plotcal(caltable=prefix+'_phase_2.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/14/00~2017/05/15/00',
            markersize=5,
            fontsize=10.0,
            figfile=prefix+'_phase_2a.png',
            showgui=True)

    plotcal(caltable=prefix+'_phase_2.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/16/00~2017/05/18/00',
            markersize=5,
            fontsize=10.0,
            figfile=prefix+'_phase_2b.png',
            showgui=True)

# Apply calibration
applycal(vis=prefix+'_SB_selfcal_1.ms',
         field='0',
         gaintable=[prefix+'_phase_2.cal'],
         spwmap=[0]*8,
         interp='linearPD',
         calwt=True)#,
#         applymode='calonly')

# Split the data to continue with the calibrations
os.system('rm -rf '+prefix+'_SB_selfcal_2.ms')
split(vis=prefix+'_SB_selfcal_1.ms',
      outputvis=prefix+'_SB_selfcal_2.ms',
      datacolumn='corrected')


#####################################################
#                 Self-Calibration 3                #
#####################################################












