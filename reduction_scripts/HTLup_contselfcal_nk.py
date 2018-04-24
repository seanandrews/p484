#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ../../../lperez/casa_5.1.1/casa-release-5.1.1-5.el7/bin/casa
# ../../../almadata02/lperez/casa_5.1.1/casa-release-5.1.1-5.el7/bin/casa

#######################################################################
#                       HT Lup Self-Calibration                       #
#######################################################################

'''
Universidad de Chile
Facultad de Ciencias Fisicas y Matematicas
Departamento de Astronomia

Nicolas Troncoso Kurtovic
mail: nicokurtovic at gmail.com

This script was written for CASA 5.1.1 to
self-calibrate the short and long baselines from HTLup datasets
'''

execfile('reduction_utils.py')

sys.path.append('/umi_01/nkurtovic/HTLup/analysis_scripts/')
#sys.path.append('/almadata02/nkurtovic/HTLup/analysis_scripts/')
import analysisUtils as au


#######################################################################
#                          NAMES AND PATH                             #
#######################################################################

# Do you want to skip the plots of images and interactive clean process?
skip_plots=True

# Name of the object
prefix = 'HTLup'

# Frequency of 12CO 2-1 line
rest_freq = 2.30538e11 # Hz

#

# Paths, names and lines in the data. Fill this dictionary with listobs.
# line_spws have the spws with lines that need to be flagged.
# line_freqs have the frequencies to flag. In this case is the 12CO 2-1 line
data_params = {'SB': {'vis' : '/umi_01/nkurtovic/HTLup/htlup_p484_SB.ms',
                      'name': 'SB', \
                      'field': 'HT_Lup', \
                      'line_spws': np.array([0, 4]), \
                      'line_freqs': np.array([rest_freq, rest_freq])
                     },
               'LB': {'vis' : '/umi_01/nkurtovic/HTLup/calibrated_final.ms',
                      'name' : 'LB',
                      'field': 'HT_Lupi',
                      'line_spws': np.array([3, 7]), 
                      'line_freqs': np.array([rest_freq, rest_freq]),
                      }}


# Build the path to each dataset
path_SB = data_params['SB']['vis']
path_LB = data_params['LB']['vis']


#######################################################################
#                           LINE FLAGGING                             #
#######################################################################

'''
To flag the CO line, we proceed inspecting by eye the
location in channels and spw.
Flag ~50 km/s around 12CO 2-1 line. Each channel in
these spectral windows has 0.635 km/s, so we need to
flag ~320 channels in total. (each channel is half that
speed to take the mean)
The center of the peak is around -6km/s.
'''

# Visual inspection of the spws in the SB data.
if not skip_plots:
    # Plot the amplitude of each channel, in groups of spw.
    plotms(vis=path_SB, \
           xaxis='channel', \
           yaxis='amplitude', \
           avgtime='1e8', \
           ydatacolumn='data', \
           field=data_params['SB']['field'], \
           avgscan=True, \
           avgbaseline=True, \
           iteraxis='spw', \
           restfreq=str(rest_freq))

# Numbers of the spectral windows with continuum.
cont_spws = '0~7'

'''
By visual inspection, it is detected that the line is centered in
channel ~1920 in spw 0 and 4. This correspond to a velocity of ~-6km/s
'''

# Find the channels that will be flagged in the SB data.
os.system('rm -rf '+path_SB+'.flagversions*')
SB_flagchannels = get_flagchannels(data_params['SB'], \
                                   prefix, \
                                   velocity_range=np.array([-21., 29.]))
# Flagchannels input string for SB: '0:1840~1997, 4:1840~1997'

# Average continuum. This will generate the file 'prefix+_SB_initcont.ms'
os.system('rm -rf '+prefix+'_SB_initcont.ms')
avg_cont(data_params['SB'], prefix, flagchannels=SB_flagchannels)


# Find the channels that will be flagged in the LB data.
os.system('rm -rf '+path_LB+'.flagversions*')
LB_flagchannels = get_flagchannels(data_params['LB'], \
                                   prefix, \
                                   velocity_range=np.array([-21., 29.]))
# Flagchannels input string for LB: '3:1839~1997, 7:1839~1997'

# Average continuum. This will generate the file 'prefix+_LB_initcont.ms'
os.system('rm -rf '+prefix+'_LB_initcont.ms')
avg_cont(data_params['LB'], prefix, flagchannels = LB_flagchannels)


#######################################################################
#             DEFINE MASK, FIRST IMAGE, FIND CENTROIDS                #
#######################################################################

# Image the SB ms file interactively. Inspection to define the mask
if not skip_plots:
    tclean_wrapper(vis=prefix+'_SB_initcont.ms', \
                   imagename=prefix+'_SB_initcont', \
                   scales=[0], \
                   imsize=900, \
                   interactive=True)

    tclean_wrapper(vis=prefix+'_LB_initcont.ms', \
                   imagename=prefix+'_LB_initcont', \
                   imsize=3000, \
                   scales=[0], \
                   interactive=True)

# Use this quick imaging to find centroids and positions. With fit_gaussian
# You can find the optimal positions to build the masks.

# Gaussian fit to the second source in SB data was tried, but
# the imfit could not find the best parameters, because it is unresolved.

# Define the center of the main disk mask in SB data
center_ra_SB_main = '15h45m12.847703s'
center_dec_SB_main = '-34d17m31.04081s'
center_SB_main = center_ra_SB_main + ' ' + center_dec_SB_main
# Define the center of the secondary disk mask in SB data
center_ra_SB_sec = '15h45m12.645242s'
center_dec_SB_sec = '-34d17m29.74827s'
center_SB_sec = center_ra_SB_sec + ' ' + center_dec_SB_sec
# Second disk center in LB data
center_ra_LB_sec = '15h45m12.644498s'
center_dec_LB_sec = '-34d17m29.73879s'
center_LB_sec = center_ra_LB_sec + ' ' + center_dec_LB_sec


'''
Here we define the mask for SB data
'''
# First disk semiaxis
mask_major_SB_main = '0.42arcsec'
mask_minor_SB_main = '0.48arcsec'
# Second disk semiaxis
mask_major_SB_sec = '0.30arcsec'
mask_minor_SB_sec = '0.45arcsec'
# First object Mask
mask_SB_main = 'ellipse[[%s, %s], [%s, %s], 0rad]' % (center_ra_SB_main, \
                                                      center_dec_SB_main, \
                                                      mask_major_SB_main, \
                                                      mask_minor_SB_main)
# Second object Mask
mask_SB_sec = 'ellipse[[%s, %s], [%s, %s], 0rad]' % (center_ra_SB_sec, \
                                                     center_dec_SB_sec, \
                                                     mask_major_SB_sec, \
                                                     mask_minor_SB_sec)

# Create a residual mask
res_mask_SB = 'annulus[[%s, %s], [%s, %s]]' % (center_ra_SB_main, \
                                               center_dec_SB_main, \
                                               '4arcsec', '9arcsec')
mask_SB = [mask_SB_main, mask_SB_sec]


'''
Here we define the mask for LB and combined data
'''
# First disk semiaxis
mask_major_LB_main = '0.26arcsec'
mask_minor_LB_main = '0.23arcsec'
# Second disk center in LB data
center_ra_LB_sec = '15h45m12.644498s'
center_dec_LB_sec = '-34d17m29.73879s'
center_LB_sec = center_ra_LB_sec + ' ' + center_dec_LB_sec
# Second disk semiaxis
mask_major_LB_sec = '0.12arcsec'
mask_minor_LB_sec = '0.15arcsec'

# First object Mask
mask_LB_main = 'ellipse[[%s, %s], [%s, %s], 0rad]' % (center_ra_SB_main, \
                                                      center_dec_SB_main, \
                                                      mask_major_LB_main, \
                                                      mask_minor_LB_main)
# Second object Mask
mask_LB_sec = 'ellipse[[%s, %s], [%s, %s], 0rad]' % (center_ra_LB_sec, \
                                                     center_dec_LB_sec, \
                                                     mask_major_LB_sec, \
                                                     mask_minor_LB_sec)

# Create a residual mask
res_mask_LB = 'annulus[[%s, %s], [%s, %s]]' % (center_ra_SB_main, \
                                               center_dec_SB_main, \
                                               '4arcsec', '7arcsec')
mask_LB = [mask_LB_main, mask_LB_sec]
scales_LB = [0, 10, 30]


# Image non interactively
tclean_wrapper(vis=prefix+'_SB_initcont.ms', \
               imagename=prefix+'_SB_initcont', \
               scales=[0], \
               mask=mask_SB, \
               savemodel='modelcolumn', \
               threshold='1.0mJy', \
               interactive=False)

# Image non interactively
tclean_wrapper(vis=prefix+'_LB_initcont.ms', \
               imagename=prefix+'_LB_initcont', \
               scales=[0], \
               mask=mask_SB, \
               savemodel='modelcolumn', \
               threshold='0.1mJy', \
               interactive=False)


'''
In the SB data we have just two sources, both of them are unresolved. but
in the LB data we see three sources, and we can realize that the main one
in SB are in reality two disks. In order to find the centroid positions of
them we need to mask this disks sepparately.

The masks already defined will be used in the clean processes, but to find
gaussian parameters (inclination, PA, centroiding) we need to mask
more precisely. The following masks will only be used for gaussian fit, and
not for cleaning.
'''

# GAUSSIAN MASKS IN LB DATA
# Main disk position
 
center_ra_main = '15h45m12.846778s'
center_dec_main = '-34d17m31.03065s'
center_LB_main = center_ra_main + ' ' + center_dec_main
# Main disk semiaxis
mask_major_main_LB = '0.18arcsec'
mask_minor_main_LB = '0.12arcsec'
mask_PA_main_LB = str(162*np.pi/180.)+'rad'
# Third disk position
center_ra_third = '15h45m12.835023s'
center_dec_third = '-34d17m31.09386s'
center_LB_third = center_ra_third + ' ' + center_dec_third
# Third disk semiaxis
mask_major_third_LB = '0.04arcsec'
mask_minor_third_LB = '0.04arcsec'
# First object Mask
mask_main_LB = 'ellipse[[%s, %s], [%s, %s], %s]' % (center_ra_main, \
                                                    center_dec_main, \
                                                    mask_major_main_LB, \
                                                    mask_minor_main_LB, \
                                                    mask_PA_main_LB)
# Second object Mask
mask_third_LB = 'ellipse[[%s, %s], [%s, %s], 0rad]' % (center_ra_third, \
                                                       center_dec_third, \
                                                       mask_major_third_LB, \
                                                       mask_minor_third_LB)


'''
SHORT BASELINES gaussian fit
'''

# Image each observation. For SB and LB there are two of them
image_each_obs(data_params['SB'], prefix, scales=[0], mask=mask_SB)

# Fit gaussian to find the central peak in the image.
# The mask must be a string, not the mask file.

fit_gaussian(prefix+'_SB_initcont_exec0.image', \
             region=mask_SB_main)
#Peak of Gaussian component identified with imfit: ICRS 15h45m12.847769s -34d17m31.03291s
#15:45:12.847769 -34:17:31.03291
#Separation: radian = 7.86966e-08, degrees = 0.000005, arcsec = 0.016232
#Peak in J2000 coordinates: 15:45:12.84829, -034:17:31.018017
#PA of Gaussian component: 169.14 deg
#Inclination of Gaussian component: 40.39 deg
#Pixel coordinates of peak: x = 451.471 y = 445.391

fit_gaussian(prefix+'_SB_initcont_exec1.image', \
             region=mask_SB_main)
#15h45m12.847681s -34d17m31.04498s
#Peak of Gaussian component identified with imfit: ICRS 15h45m12.847681s -34d17m31.04498s
#15:45:12.847681 -34:17:31.04498
#Separation: radian = 7.86444e-08, degrees = 0.000005, arcsec = 0.016222
#Peak in J2000 coordinates: 15:45:12.84820, -034:17:31.030088
#PA of Gaussian component: 150.18 deg
#Inclination of Gaussian component: 38.75 deg
#Pixel coordinates of peak: x = 451.508 y = 444.988


fit_gaussian(prefix+'_SB_initcont.image', \
             region=mask_SB_main)
#15h45m12.847715s -34d17m31.04075s
#Peak of Gaussian component identified with imfit: ICRS 15h45m12.847715s -34d17m31.04075s
#15:45:12.847715 -34:17:31.04075
#Separation: radian = 7.85539e-08, degrees = 0.000005, arcsec = 0.016203
#Peak in J2000 coordinates: 15:45:12.84823, -034:17:31.025857
#PA of Gaussian component: 157.70 deg
#Inclination of Gaussian component: 39.08 deg
#Pixel coordinates of peak: x = 451.494 y = 445.130

# Difference between peaks is negligible in SB. We are going
# to choose the central peak of them together as the
# center

# Fit to the second source.
fit_gaussian(prefix+'_SB_initcont.image', \
             region=mask_SB_sec)
#15h45m12.645265s -34d17m29.74878s
#Peak of Gaussian component identified with imfit: ICRS 15h45m12.645265s -34d17m29.74878s
#15:45:12.645265 -34:17:29.74878
#Separation: radian = 7.8554e-08, degrees = 0.000005, arcsec = 0.016203
#Peak in J2000 coordinates: 15:45:12.64578, -034:17:29.733887
#Pixel coordinates of peak: x = 535.123 y = 488.195

'''
LONG BASELINES gaussian fit
'''
# Image each observation. For LB there are two of them. We'll check
# if there are offset positions between the peak in the central main disk
image_each_obs(data_params['LB'], prefix, scales=[0], mask=mask_LB)

fit_gaussian(prefix+'_LB_initcont_exec0.image', \
             region=mask_main_LB)
#15h45m12.846759s -34d17m31.03121s
#Peak of Gaussian component identified with imfit: ICRS 15h45m12.846759s -34d17m31.03121s
#15:45:12.846759 -34:17:31.03121
#Separation: radian = 7.86966e-08, degrees = 0.000005, arcsec = 0.016232
#Peak in J2000 coordinates: 15:45:12.84728, -034:17:31.016317
#PA of Gaussian component: 166.46 deg
#Inclination of Gaussian component: 46.24 deg
#Pixel coordinates of peak: x = 451.515 y = 445.519

fit_gaussian(prefix+'_LB_initcont_exec1.image', \
             region=mask_main_LB)
#15h45m12.846793s -34d17m31.02979s
#Peak of Gaussian component identified with imfit: ICRS 15h45m12.846793s -34d17m31.02979s
#15:45:12.846793 -34:17:31.02979
#Separation: radian = 7.86013e-08, degrees = 0.000005, arcsec = 0.016213
#Peak in J2000 coordinates: 15:45:12.84731, -034:17:31.014897
#PA of Gaussian component: 167.18 deg
#Inclination of Gaussian component: 45.82 deg
#Pixel coordinates of peak: x = 451.502 y = 445.566

# Gaussian fit to the main disk
fit_gaussian(prefix+'_LB_initcont.image', \
             region=mask_main_LB)
#15h45m12.846796s -34d17m31.03108s
#Peak of Gaussian component identified with imfit: ICRS 15h45m12.846796s -34d17m31.03108s
#15:45:12.846796 -34:17:31.03108
#Separation: radian = 7.85303e-08, degrees = 0.000004, arcsec = 0.016198
#Peak in J2000 coordinates: 15:45:12.84731, -034:17:31.016187
#PA of Gaussian component: 166.85 deg
#Inclination of Gaussian component: 48.80 deg
#Pixel coordinates of peak: x = 1515.002 y = 1455.231

# Gaussian fit to the second disk (the one that is far away)
fit_gaussian(prefix+'_LB_initcont.image', \
             region=mask_LB_sec)
#15h45m12.644503s -34d17m29.73807s
#Peak of Gaussian component identified with imfit: ICRS 15h45m12.644503s -34d17m29.73807s
#15:45:12.644503 -34:17:29.73807
#Separation: radian = 7.86014e-08, degrees = 0.000005, arcsec = 0.016213
#Peak in J2000 coordinates: 15:45:12.64502, -034:17:29.723177
#PA of Gaussian component: 69.13 deg
#Inclination of Gaussian component: 57.63 deg
#Pixel coordinates of peak: x = 2350.652 y = 1886.232

# Gaussian fit to the smallest (and closer to the main disk) disk
fit_gaussian(prefix+'_LB_initcont.image', \
             region=mask_third_LB)
#15h45m12.835149s -34d17m31.09333s
#Peak of Gaussian component identified with imfit: ICRS 15h45m12.835149s -34d17m31.09333s
#15:45:12.835149 -34:17:31.09333
#Separation: radian = 7.86966e-08, degrees = 0.000005, arcsec = 0.016232
#Peak in J2000 coordinates: 15:45:12.83567, -034:17:31.078437
#PA of Gaussian component: 51.66 deg
#Inclination of Gaussian component: 65.19 deg
#Pixel coordinates of peak: x = 1563.116 y = 1434.478


#######################################################################
#                        SHIFT POSITIONS IN DATA                      #
#######################################################################

'''
Two main disk, in SB and LB data, show the same position with negligible
difference in the same datasets, meaning that each observation can
be treated as just one.
By measuring the position of the second component, we can see an offset
between SB and LB of 10mas. In J2000:
SB data:  15  45  12.64578 ,  -34  17  29.733887
LB data:  15  45  12.64502 ,  -34  17  29.723177
diff:     0h  0m   0.00076s,   0d  0m   0.010710s

We can't compare the centroid of the main disks in SB and LB data,
because in SB the source is unresolved and the third source moves
the measured position.

Because of this, we choose to align the second source centroid,
using the LB data as the best solution, because here this source is
resolved and we have better quality in resolution.

In J2000, for LB data:
main: 15h45m12.84731s -34d17m31.016187s
sec:  15h45m12.64502s -34d17m29.723177s

In J2000,for SB data:
main: 15h45m12.84823s -34d17m31.025857s
sec:  15h45m12.64578s -34d17m29.733887s
'''

# Change the phase center to coincide both datasets
# with the peak in LB data. We are going to add the
# difference in dec. Even if the combination is not
# perfect, we'll let selfcalibration solved the small
# remaining differences
common_dir = 'J2000 15h45m12.84731s -34d17m31.016187s'

# Create the shifted ms file of LB
shiftname_SB = prefix+'_SB_initcont_shift'
os.system('rm -rf %s.*' % shiftname_SB)
fixvis(vis=prefix+'_SB_initcont.ms', \
       outputvis=shiftname_SB+'.ms', \
       field=data_params['SB']['field'], \
       phasecenter='J2000 15h45m12.64578s -34d17m29.733887s')
fixplanets(vis=shiftname_SB+'.ms', \
           field=data_params['SB']['field'], \
           direction='J2000 15h45m12.64502s -34d17m29.723177s')
fixvis(vis=shiftname_SB+'.ms', \
       outputvis=shiftname_SB+'.ms', \
       field=data_params['SB']['field'], \
       phasecenter='J2000 15h45m12.84731s -34d17m31.016187s')

# Image
tclean_wrapper(vis=shiftname_SB+'.ms', \
               imagename=shiftname_SB, \
               mask=mask_SB, \
               scales=[0], \
               threshold='1.5mJy')
#Gaussian fit to the second source
fit_gaussian(shiftname_SB+'.image', region=mask_SB_sec)
# Target: 15:45:12.64502, -034:17:29.723177
# Result: 15h45m12.645024s -34d17m29.72309s
#Peak of Gaussian component identified with imfit: J2000 15h45m12.645024s -34d17m29.72309s
#Pixel coordinates of peak: x = 533.562 y = 493.103

# Create the shifted ms file of LB
shiftname_LB = prefix+'_LB_initcont_shift'
os.system('rm -rf %s.*' % shiftname_LB)
fixvis(vis=prefix+'_LB_initcont.ms', \
       outputvis=shiftname_LB+'.ms', \
       field=data_params['LB']['field'], \
       phasecenter=common_dir)
# Image
tclean_wrapper(vis=shiftname_LB+'.ms', \
               imagename=shiftname_LB, \
               mask=mask_LB, \
               scales=[0], \
               threshold='0.2mJy')
#Gaussian fit to the second source
fit_gaussian(shiftname_LB+'.image', region=mask_LB_sec)
#15h45m12.645019s -34d17m29.72320s
#Peak of Gaussian component identified with imfit: J2000 15h45m12.645019s -34d17m29.72320s
#PA of Gaussian component: 69.27 deg
#Inclination of Gaussian component: 57.41 deg
#Pixel coordinates of peak: x = 2335.641 y = 1930.996

# THE DIFFERENCE NOW IS ~1mas. We will proceed with this difference.

# Split observations
split_all_obs(shiftname_LB+'.ms', shiftname_LB+'_exec')
split_all_obs(shiftname_SB+'.ms', shiftname_SB+'_exec')

#######################################################################
#                           FLUX CORRECTION                           #
#######################################################################

#listobs(shiftname_LB+'.ms')
#listobs(shiftname_SB+'.ms')

# For SB data the calibrators were J1427-4206 and J1517-2422. The fluxes
# were 1.803Jy and 2.108Jy nominally.

au.getALMAFlux('J1427-4206', frequency='232.605GHz', date='2017/05/14')
'''
Closest Band 3 measurement: 3.130 +- 0.080 (age=+0 days) 91.5 GHz
Closest Band 7 measurement: 1.450 +- 0.080 (age=-1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -1 days from 2017/05/14, with age separation of 0 days
  2017/05/15: freqs=[103.49, 91.46, 343.48], fluxes=[3.09, 3.16, 1.45]
Median Monte-Carlo result for 232.605000 = 1.860478 +- 0.162262 (scaled MAD = 0.160392)
Result using spectral index of -0.591033 for 232.605 GHz from 3.130 Jy at 91.460 GHz = 1.802796 +- 0.162262 Jy
Calibration is consistent with catalog (3% difference)
'''

au.getALMAFlux('J1517-2422', frequency='232.604GHz', date='2017/05/17')
'''
Closest Band 3 measurement: 2.550 +- 0.060 (age=+2 days) 103.5 GHz
Closest Band 3 measurement: 2.490 +- 0.050 (age=+2 days) 91.5 GHz
Closest Band 7 measurement: 1.750 +- 0.060 (age=+0 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 2 days from 2017/05/17, with age separation of 0 days
  2017/05/15: freqs=[103.49, 91.46, 343.48], fluxes=[2.55, 2.49, 1.84]
Median Monte-Carlo result for 232.604000 = 2.047153 +- 0.159726 (scaled MAD = 0.159300)
Result using spectral index of -0.234794 for 232.604 GHz from 2.520 Jy at 97.475 GHz = 2.054534 +- 0.159726 Jy
Calibration is consistent with catalog (3% difference)
'''

# For LB data the calibrators were J1517-2422 and J1427-4206 .The fluxes
# were 1.803Jy and 2.108Jy nominally.
au.getALMAFlux('J1517-2422', frequency='232.581GHz', date='2017/09/24')
'''
Closest Band 3 measurement: 3.300 +- 0.330 (age=+7 days) 103.5 GHz
Closest Band 3 measurement: 3.200 +- 0.280 (age=+7 days) 91.5 GHz
Closest Band 7 measurement: 1.770 +- 0.040 (age=+1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -8 days from 2017/09/24, with age separation of 0 days
  2017/10/02: freqs=[91.46, 103.49, 343.48], fluxes=[2.79, 2.77, 1.92]
Median Monte-Carlo result for 232.581000 = 2.172913 +- 0.178773 (scaled MAD = 0.177553)
Result using spectral index of -0.279723 for 232.581 GHz from 3.250 Jy at 97.475 GHz = 2.548223 +- 0.178773 Jy
'''

au.getALMAFlux('J1427-4206', frequency='232.589GHz', date='2017/09/24')
'''
Closest Band 3 measurement: 3.210 +- 0.100 (age=-4 days) 91.5 GHz
Closest Band 7 measurement: 1.380 +- 0.050 (age=+1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -27 days from 2017/09/24, with age separation of 0 days
  2017/10/21: freqs=[91.46, 103.49, 343.48], fluxes=[3.71, 3.44, 1.98]
Median Monte-Carlo result for 232.589000 = 2.373690 +- 0.116957 (scaled MAD = 0.115420)
Result using spectral index of -0.467361 for 232.589 GHz from 3.210 Jy at 91.460 GHz = 2.075183 +- 0.116957 Jy
'''

# The rough values from gaussian fitting of LB main disk will be 
# used for deprojection.
PA = 166.
incl = 47.

if not skip_plots:
    for msfile in [shiftname_LB+'.ms', shiftname_SB+'.ms',shiftname_LB+'_exec0.ms', shiftname_LB+'_exec1.ms', shiftname_SB+'_exec0.ms', shiftname_SB+'_exec1.ms']:
        export_MS(msfile)
#Measurement set exported to HTLup_LB_initcont_shift.vis.npz
#Measurement set exported to HTLup_SB_initcont_shift.vis.npz
#Measurement set exported to HTLup_LB_initcont_shift_exec0.vis.npz
#Measurement set exported to HTLup_LB_initcont_shift_exec1.vis.npz
#Measurement set exported to HTLup_SB_initcont_shift_exec0.vis.npz
#Measurement set exported to HTLup_SB_initcont_shift_exec1.vis.npz

    # PLot fluxes comparing both SB executions
    plot_deprojected([shiftname_SB+'_exec0.vis.npz', shiftname_SB+'_exec1.vis.npz'], PA=PA, incl=incl)
    # There is a difference in the middle of the deprojected baseline length
    # of the SB data, however the initial and final part are consistent
    # From the calibrators we now that there shouldn't be so much difference,
    # so We'll leave the rest to the self-calibration.

    # Plot fluxes comparing both LB executions
    plot_deprojected([shiftname_LB+'_exec0.vis.npz', shiftname_LB+'_exec1.vis.npz'], PA=PA, incl=incl)
    # There is a difference between executions.
    estimate_flux_scale(reference=shiftname_LB+'_exec0.vis.npz', \
                        comparison=shiftname_LB+'_exec1.vis.npz', \
                        incl=incl, PA=PA, uvbins=100+10*np.arange(100))
    # The ratio of the fluxes of HTLup_LB_initcont_shift_exec1.vis.npz to HTLup_LB_initcont_shift_exec0.vis.npz is 0.91735
    # The scaling factor for gencal is 0.958 for your comparison measurement
    # The error on the weighted mean ratio is 6.628e-04, although it's likely that the weights in the measurement sets are too off by some constant factor
    plot_deprojected([shiftname_LB+'_exec0.vis.npz', shiftname_LB+'_exec1.vis.npz'], PA=PA, incl=incl, fluxscale=[1., 1/.91])

    # We are going to correct both LB executions with SB data.
    plot_deprojected([shiftname_SB+'.vis.npz', shiftname_LB+'_exec0.vis.npz'], PA=PA, incl=incl)
    # 
    plot_deprojected([shiftname_SB+'.vis.npz', shiftname_LB+'_exec1.vis.npz'], PA=PA, incl=incl)
    # There is a difference between executions.
    estimate_flux_scale(reference=shiftname_SB+'.vis.npz', \
                        comparison=shiftname_LB+'_exec0.vis.npz', \
                        incl=incl, PA=PA, uvbins=100+10*np.arange(100))
#The ratio of the fluxes of HTLup_LB_initcont_shift_exec0.vis.npz to HTLup_SB_initcont_shift.vis.npz is 0.95028
#The scaling factor for gencal is 0.975 for your comparison measurement
#The error on the weighted mean ratio is 5.863e-04, although it's likely that the weights in the measurement sets are too off by some constant factor

    # There is a difference between executions.
    estimate_flux_scale(reference=shiftname_SB+'.vis.npz', \
                        comparison=shiftname_LB+'_exec1.vis.npz', \
                        incl=incl, PA=PA, uvbins=100+10*np.arange(100))
#The ratio of the fluxes of HTLup_LB_initcont_shift_exec1.vis.npz to HTLup_SB_initcont_shift.vis.npz is 0.86829
#The scaling factor for gencal is 0.932 for your comparison measurement
#The error on the weighted mean ratio is 5.683e-04, although it's likely that the weights in the measurement sets are too off by some constant factor


# The discrepant dataset is LB_exec1. Correct discrepant dataset
os.system('rm -rf *rescaled.*')
rescale_flux(shiftname_LB+'_exec0.ms', [0.975])
rescale_flux(shiftname_LB+'_exec1.ms', [0.932])
export_MS(shiftname_LB+'_exec0_rescaled.ms')
export_MS(shiftname_LB+'_exec1_rescaled.ms')

if skip_plots:
    # Re-plot to see if it worked
    plot_deprojected([shiftname_SB+'.vis.npz', shiftname_LB+'_exec0_rescaled.vis.npz'], PA=PA, incl=incl)
    # Re-plot to see if it worked
    plot_deprojected([shiftname_SB+'.vis.npz', shiftname_LB+'_exec1_rescaled.vis.npz'], PA=PA, incl=incl)

# REMEMBER TO COMBINE BOTH LB EXECUTIONS WHEN SELF-CALIBRATING.


#######################################################################
#                    SB SELF-CALIBRATION PARAMETERS                   #
#######################################################################

# Robust level
robust = 0.5
# This reference antenna will be used for SB and combined data.
SB_refant = 'DA61'
# In SB the source is not well resolved. We are not using different scales.
scales_SB = [0]

# Calculate residual of the noise in the previous imaging.
estimate_SNR(imagename=shiftname_SB+'.image', disk_mask=mask1_SB, noise_mask=res_mask_SB)
#HTLup_SB_initcont_shift.image
#Beam 0.273 arcsec x 0.229 arcsec (-83.71 deg)
#Flux inside disk mask: 73.14 mJy
#Peak intensity of source: 50.57 mJy/beam
#rms: 1.29e-01 mJy/beam
#Peak SNR: 391.31

#######################################################################
#                     PHASE SELF-CALIBRATION 0                        #
#######################################################################

# Name of the first data.
SB_cont_p0 = prefix+'_SB_contp0'

# Split the data to continue with the calibrations
os.system('rm -rf '+SB_cont_p0+'.*')
split(vis=shiftname_SB+'.ms',
      outputvis=SB_cont_p0+'.ms',
      datacolumn='data')

# First Clean for selfcalibration
tclean_wrapper(vis=SB_cont_p0+'.ms', \
               imagename=SB_cont_p0, \
               mask=mask_SB, \
               scales=scales_SB, \
               robust=robust, \
               threshold='0.2mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(SB_cont_p0+'.image', disk_mask = mask_SB_main, noise_mask = res_mask_SB)
#HTLup_SB_contp0.image
#Beam 0.273 arcsec x 0.229 arcsec (-83.72 deg)
#Flux inside disk mask: 73.70 mJy
#Peak intensity of source: 51.03 mJy/beam
#rms: 1.28e-01 mJy/beam
#Peak SNR: 399.70

# RMS in mJy
rms_SB_p0 = imstat(imagename=SB_cont_p0+'.image', region=res_mask_SB)['rms'][0]*10**3

# First self-calibration
os.system('rm -rf '+SB_cont_p0+'_p0.cal')
gaincal(vis=SB_cont_p0+'.ms',
        caltable=SB_cont_p0+'.cal',
        gaintype='T',
        spw=cont_spws,
        refant = SB_refant,
        solint='60s',
        calmode='p',
        minsnr=1.5,
        minblperant=4)

'''
None solutions were flagged
'''

if not skip_plots:
    # Plot the first phase calibration
    plotcal(caltable=SB_cont_p0+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/14/00~2017/05/15/00',
            markersize=5,
            fontsize=10.0,
            figfile=SB_cont_p0+'_cal_0.png',
            showgui=True)

    plotcal(caltable=SB_cont_p0+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/16/00~2017/05/18/00',
            markersize=5,
            fontsize=10.0,
            figfile=SB_cont_p0+'_cal_1.png',
            showgui=True)

# Apply calibration
applycal(vis=SB_cont_p0+'.ms',
         spw=cont_spws, 
         gaintable=[SB_cont_p0+'.cal'],
         interp='linearPD',
         calwt=True)


#######################################################################
#                     PHASE SELF-CALIBRATION 1                        #
#######################################################################

# Name of the data.
SB_cont_p1 = prefix+'_SB_contp1'

# Split the data to continue with the calibrations
os.system('rm -rf '+SB_cont_p1+'.*')
split(vis=SB_cont_p0+'.ms',
      outputvis=SB_cont_p1+'.ms',
      datacolumn='corrected')

# Clean for selfcalibration. 0.2 is lower than 2*rms_SB_p0.
tclean_wrapper(vis=SB_cont_p1+'.ms', \
               imagename=SB_cont_p1, \
               mask=mask_SB, \
               scales=scales_SB, \
               robust=robust, \
               threshold='0.2mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(SB_cont_p1+'.image', disk_mask = mask_SB_main, noise_mask = res_mask_SB)
#HTLup_SB_contp1.image
#Beam 0.273 arcsec x 0.229 arcsec (-83.72 deg)
#Flux inside disk mask: 76.04 mJy
#Peak intensity of source: 56.12 mJy/beam
#rms: 3.86e-02 mJy/beam
#Peak SNR: 1453.15

# RMS in mJy
rms_SB_p1 = imstat(imagename=SB_cont_p1+'.image', region=res_mask_SB)['rms'][0]*10**3


# Gaincal - self-calibration
os.system('rm -rf '+SB_cont_p1+'.cal')
gaincal(vis=SB_cont_p1+'.ms',
        caltable=SB_cont_p1+'.cal',
        gaintype='T',
        spw=cont_spws,
        refant = SB_refant,
        solint='30s',
        calmode='p',
        minsnr=1.5,
        minblperant=4)

'''
None solutions were flagged
'''

if not skip_plots:
    # Plot the first phase calibration
    plotcal(caltable=SB_cont_p1+'_p1.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/14/00~2017/05/15/00',
            markersize=5,
            fontsize=10.0,
            figfile=SB_cont_p1+'_cal_0.png',
            showgui=True)

    plotcal(caltable=SB_cont_p1+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/16/00~2017/05/18/00',
            markersize=5,
            fontsize=10.0,
            figfile=SB_cont_p1+'_cal_1.png',
            showgui=True)

# Apply calibration
applycal(vis=SB_cont_p1+'.ms',
         spw=cont_spws, 
         gaintable=[SB_cont_p1+'.cal'],
         interp='linearPD',
         calwt=True)


#######################################################################
#                       PHASE SELF-CALIBRATION 2                      #
#######################################################################

# Name of the data.
SB_cont_p2 = prefix+'_SB_contp2'

# Split the data to continue with the calibrations
os.system('rm -rf '+SB_cont_p2+'.*')
split(vis=SB_cont_p1+'.ms',
      outputvis=SB_cont_p2+'.ms',
      datacolumn='corrected')

# Clean for selfcalibration
tclean_wrapper(vis=SB_cont_p2+'.ms', \
               imagename=SB_cont_p2, \
               mask=mask_SB, \
               scales=scales_SB, \
               robust=robust, \
               threshold=str(2*rms_SB_p1)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(SB_cont_p2+'.image', disk_mask = mask_SB_main, noise_mask = res_mask_SB)
#HTLup_SB_contp2.image
#Beam 0.273 arcsec x 0.229 arcsec (-83.72 deg)
#Flux inside disk mask: 76.14 mJy
#Peak intensity of source: 56.91 mJy/beam
#rms: 3.72e-02 mJy/beam
#Peak SNR: 1529.13

# RMS in mJy
rms_SB_p2 = imstat(imagename=SB_cont_p2+'.image', region=res_mask_SB)['rms'][0]*10**3

# Third self-calibration
os.system('rm -rf '+SB_cont_p2+'.cal')
gaincal(vis=SB_cont_p2+'.ms',
        caltable=SB_cont_p2+'.cal',
        gaintype='T',
        spw=cont_spws,
        refant = SB_refant,
        solint='18s',
        calmode='p',
        minsnr=1.5,
        minblperant=4)

'''
None solutions were flagged
'''

if not skip_plots:
    # Plot the first phase calibration
    plotcal(caltable=SB_cont_p2+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/14/00~2017/05/15/00',
            markersize=5,
            fontsize=10.0,
            figfile=SB_cont_p2+'_cal_0.png',
            showgui=True)

    plotcal(caltable=SB_cont_p2+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/16/00~2017/05/18/00',
            markersize=5,
            fontsize=10.0,
            figfile=SB_cont_p2+'_cal_1.png',
            showgui=True)

# Apply calibration
applycal(vis=SB_cont_p2+'.ms',
         spw=cont_spws, 
         gaintable=[SB_cont_p2+'.cal'],
         interp='linearPD',
         calwt=True)


#######################################################################
#                       AMP SELF-CALIBRATION 0                        #
#######################################################################

# As you will see, the phase calibration shows no more improvement.
# Here we start the amp calibration
# Name of the data.
SB_cont_a0 = prefix+'_SB_conta0'

# Split the data to continue with the calibrations
os.system('rm -rf '+SB_cont_a0+'.*')
split(vis=SB_cont_p2+'.ms',
      outputvis=SB_cont_a0+'.ms',
      datacolumn='corrected')

# Clean for selfcalibration. We push to 1.5rms
tclean_wrapper(vis=SB_cont_a0+'.ms', \
               imagename=SB_cont_a0, \
               mask=mask_SB, \
               scales=scales_SB, \
               robust=robust, \
               threshold=str(1.5*rms_SB_p2)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(SB_cont_a0+'.image', disk_mask = mask_SB_main, noise_mask = res_mask_SB)
#HTLup_SB_conta0.image
#Beam 0.273 arcsec x 0.229 arcsec (-83.72 deg)
#Flux inside disk mask: 76.24 mJy
#Peak intensity of source: 57.24 mJy/beam
#rms: 3.74e-02 mJy/beam
#Peak SNR: 1531.67

# RMS in mJy
rms_SB_a0 = imstat(imagename=SB_cont_a0+'.image', region=res_mask_SB)['rms'][0]*10**3


# I stopped here the phase cal. Improvement of snr
# is marginal. We start the amp calibration.

# First amp-calibration
os.system('rm -rf '+SB_cont_a0+'.cal')
gaincal(vis=SB_cont_a0+'.ms',
        caltable=SB_cont_a0+'.cal',
        refant=SB_refant,
        solint='inf',
        calmode='ap',
        gaintype='T',
        spw=cont_spws,
        minsnr=3.0,
        minblperant=4, 
        solnorm=False)


if not skip_plots:
    # Plot the first phase calibration
    plotcal(caltable=SB_cont_a0+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            timerange='2017/05/14/00~2017/05/15/00',
            figfile=SB_cont_a0+'_cal_0.png',
            showgui=True)

    plotcal(caltable=prefix+'_a1.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            plotrange=[0, 0, 0, 0],
            iteration='antenna',
            timerange='2017/05/16/00~2017/05/18/00',
            figfile=SB_cont_a0+'_cal_1.png',
            showgui=True)

# Apply calibration
applycal(vis=SB_cont_a0+'.ms',
         gaintable=[SB_cont_a0+'.cal'],
         spw=cont_spws, 
         interp='linearPD',
         calwt=True)


# Split the data to continue with the calibrations
os.system('rm -rf '+prefix+'_SB_selfcal_ap.ms')
split(vis=SB_cont_a0+'.ms',
      outputvis=prefix+'_SB_selfcal_ap.ms',
      datacolumn='corrected')


#######################################################################
#                            FINAL SB IMAGE                           #
#######################################################################

# Image
tclean_wrapper(vis=prefix+'_SB_selfcal_ap.ms', \
               imagename=prefix+'_SB_contap', \
               mask=mask_SB, \
               scales=scales_SB, \
               robust=robust, \
               threshold=str(1.5*rms_SB_a0)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(prefix+'_SB_contap.image', disk_mask = mask_SB_main, noise_mask = res_mask_SB)
#HTLup_SB_contap.image
#Beam 0.273 arcsec x 0.228 arcsec (-83.56 deg)
#Flux inside disk mask: 76.25 mJy
#Peak intensity of source: 57.17 mJy/beam
#rms: 2.94e-02 mJy/beam
#Peak SNR: 1944.31


#######################################################################
#                         COMBINE SB AND LB                           #
#######################################################################

# Name
combined_cont_p0 = prefix+'_combined_p0'

# Combined file. Includes the calibrated SB, and the two shifted and
# rescaled executions of LB.
os.system('rm -rf '+combined_cont_p0+'.*')
concat(vis=[prefix+'_SB_selfcal_ap.ms', shiftname_LB+'_exec0_rescaled.ms', shiftname_LB+'_exec1_rescaled.ms' ], concatvis=combined_cont_p0+'.ms', dirtol='0.1arcsec', copypointing=False)


#######################################################################
#                         COMBINE SB AND LB                           #
#######################################################################

# Robust level
robust = 0.5
# Combined parameters
combined_contspw = '0~15'
combined_spwmap = [0, 0, 0, 0, 4, 4, 4, 4, 8, 8, 8, 8, 12, 12, 12, 12]
# The beam is roughly 11 pixels.
combined_scales = [0, 11, 33, 55]
# I had to use imsize=4000 in order to get the calculation of rms,
# because of the secondary source.
combined_imsize = 4000
# Reference antenna. By visual inspection, DA61 seems like a good candidate
# for SB and LB. We check if it is in all executions and in the same station.
get_station_numbers(combined_cont_p0+'.ms', 'DA61')
#Observation ID 0: DA61@A015
#Observation ID 1: DA61@A015
#Observation ID 2: DA61@A015
#Observation ID 3: DA61@A015
combined_refant = 'DA61'

# Clean for selfcalibration
tclean_wrapper(vis=combined_cont_p0+'.ms', \
               imagename=combined_cont_p0, \
               imsize=combined_imsize, \
               mask=mask_LB, \
               scales=combined_scales, \
               robust=robust, \
               threshold='0.1mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(combined_cont_p0+'.image', disk_mask = mask_LB_main, noise_mask = res_mask_LB)
#HTLup_combined_p0.image
#Beam 0.038 arcsec x 0.033 arcsec (69.45 deg)
#Flux inside disk mask: 77.26 mJy
#Peak intensity of source: 7.01 mJy/beam
#rms: 1.69e-02 mJy/beam
#Peak SNR: 415.83

# RMS in mJy
rms_com_p0 = imstat(imagename=combined_cont_p0+'.image', region=res_mask_LB)['rms'][0]*10**3

# Phase self-calibration
os.system('rm -rf '+combined_cont_p0+'.cal')
gaincal(vis=combined_cont_p0+'.ms',
        caltable=combined_cont_p0+'.cal',
        combine= 'spw, scan',
        gaintype='T',
        spw=combined_contspw,
        refant = combined_refant,
        solint='360s',
        calmode='p',
        minsnr=1.5,
        minblperant=4)

'''
2 of 39 solutions flagged due to SNR < 1.5 in spw=8 at 2017/09/24/18:03:05.3
3 of 39 solutions flagged due to SNR < 1.5 in spw=8 at 2017/09/24/18:09:42.7
1 of 39 solutions flagged due to SNR < 1.5 in spw=8 at 2017/09/24/18:12:38.8
1 of 39 solutions flagged due to SNR < 1.5 in spw=8 at 2017/09/24/18:19:14.0
3 of 39 solutions flagged due to SNR < 1.5 in spw=8 at 2017/09/24/18:22:23.9
4 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/19:33:25.5
2 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/19:40:01.6
1 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/19:43:31.6
2 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/19:46:48.0
1 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/19:53:41.0
2 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/20:00:34.9
1 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/20:05:00.1
3 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/20:07:29.9
1 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/20:11:02.2
'''

if not skip_plots:
    # Plot the first phase calibration
    plotcal(caltable=combined_cont_p0+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/14/00~2017/05/15/00',
            markersize=5,
            fontsize=10.0,
            figfile=combined_cont_p0+'a.png',
            showgui=True)

    plotcal(caltable=combined_cont_p0+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/16/00~2017/05/18/00',
            markersize=5,
            fontsize=10.0,
            figfile=combined_cont_p0+'b.png',
            showgui=True)

    plotcal(caltable=combined_cont_p0+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/09/24/00~2017/09/25/00',
            markersize=5,
            fontsize=10.0,
            figfile=combined_cont_p0+'c.png',
            showgui=True)

# Apply calibration
applycal(vis=combined_cont_p0+'.ms', 
         spw=combined_contspw, 
         spwmap=combined_spwmap, 
         gaintable=[combined_cont_p0+'.cal'], 
         interp='linearPD', 
         calwt=True, 
         applymode='calonly')


#######################################################################
#                     COMBINED PHASE-SELFCAL 1                        #
#######################################################################

# Name
combined_cont_p1 = prefix+'_combined_p1'

# Split the data to continue with the calibrations
os.system('rm -rf '+combined_cont_p1+'.ms')
split(vis=combined_cont_p0+'.ms',
      outputvis=combined_cont_p1+'.ms',
      datacolumn='corrected')


# First Clean for selfcalibration
tclean_wrapper(vis=combined_cont_p1+'.ms', \
               imagename=combined_cont_p1, \
               imsize=combined_imsize, \
               mask=mask_LB, \
               scales=combined_scales, \
               robust=robust, \
               threshold=str(2*rms_com_p0)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(combined_cont_p1+'.image', disk_mask = mask_LB_main, noise_mask = res_mask_LB)
#HTLup_combined_p1.image
#Beam 0.038 arcsec x 0.033 arcsec (69.45 deg)
#Flux inside disk mask: 76.59 mJy
#Peak intensity of source: 7.24 mJy/beam
#rms: 1.60e-02 mJy/beam
#Peak SNR: 454.10

# RMS in mJy
rms_com_p1 = imstat(imagename=combined_cont_p1+'.image', region=res_mask_LB)['rms'][0]*10**3

# Phase self-calibration
os.system('rm -rf '+combined_cont_p1+'.cal')
gaincal(vis=combined_cont_p1+'.ms',
        caltable=combined_cont_p1+'.cal',
        combine= 'spw, scan',
        gaintype='T',
        spw=combined_contspw,
        refant = combined_refant,
        solint='180s',
        calmode='p',
        minsnr=1.5,
        minblperant=4)

'''
1 of 39 solutions flagged due to SNR < 1.5 in spw=8 at 2017/09/24/17:52:10.4
2 of 39 solutions flagged due to SNR < 1.5 in spw=8 at 2017/09/24/17:53:48.1
2 of 39 solutions flagged due to SNR < 1.5 in spw=8 at 2017/09/24/17:57:38.4
2 of 39 solutions flagged due to SNR < 1.5 in spw=8 at 2017/09/24/18:11:29.4
2 of 39 solutions flagged due to SNR < 1.5 in spw=8 at 2017/09/24/18:16:59.6
2 of 39 solutions flagged due to SNR < 1.5 in spw=8 at 2017/09/24/18:20:53.8
1 of 39 solutions flagged due to SNR < 1.5 in spw=8 at 2017/09/24/18:31:11.8
1 of 39 solutions flagged due to SNR < 1.5 in spw=8 at 2017/09/24/18:33:06.4
1 of 39 solutions flagged due to SNR < 1.5 in spw=8 at 2017/09/24/18:35:14.1
2 of 39 solutions flagged due to SNR < 1.5 in spw=8 at 2017/09/24/18:36:55.5
3 of 39 solutions flagged due to SNR < 1.5 in spw=8 at 2017/09/24/18:47:59.6
2 of 39 solutions flagged due to SNR < 1.5 in spw=8 at 2017/09/24/18:52:07.7
2 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/19:30:33.3
1 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/19:34:30.4
6 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/19:42:51.2
1 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/19:44:41.6
1 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/19:46:39.9
1 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/19:55:07.3
1 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/20:01:07.2
1 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/20:05:42.2
1 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/20:07:21.8
1 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/20:09:21.4
2 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/20:11:17.8
1 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/20:19:31.8
1 of 39 solutions flagged due to SNR < 1.5 in spw=12 at 2017/09/24/20:23:25.8
'''

if not skip_plots:
    # Plot the phase calibration
    plotcal(caltable=combined_cont_p1+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/14/00~2017/05/15/00',
            markersize=5,
            fontsize=10.0,
            figfile=combined_cont_p1+'a.png',
            showgui=True)

    plotcal(caltable=combined_cont_p1+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/16/00~2017/05/18/00',
            markersize=5,
            fontsize=10.0,
            figfile=combined_cont_p1+'b.png',
            showgui=True)

    plotcal(caltable=combined_cont_p1+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/09/24/00~2017/09/25/00',
            markersize=5,
            fontsize=10.0,
            figfile=combined_cont_p1+'c.png',
            showgui=True)

# Apply calibration
applycal(vis=combined_cont_p1+'.ms', 
         spw=combined_contspw, 
         spwmap=combined_spwmap, 
         gaintable=[combined_cont_p1+'.cal'], 
         interp='linearPD', 
         calwt=True, 
         applymode='calonly')



#######################################################################
#                     COMBINED PHASE-SELFCAL 2                        #
#######################################################################

# Name
combined_cont_p2 = prefix+'_combined_p2'

# Split the data to continue with the calibrations
os.system('rm -rf '+combined_cont_p2+'.ms')
split(vis=combined_cont_p1+'.ms',
      outputvis=combined_cont_p2+'.ms',
      datacolumn='corrected')


# First Clean for selfcalibration
tclean_wrapper(vis=combined_cont_p2+'.ms', \
               imagename=combined_cont_p2, \
               imsize=combined_imsize, \
               mask=mask_LB, \
               scales=combined_scales, \
               robust=robust, \
               threshold=str(2*rms_com_p1)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(combined_cont_p2+'.image', disk_mask = mask_LB_main, noise_mask = res_mask_LB)
#HTLup_combined_p2.image
#Beam 0.038 arcsec x 0.033 arcsec (69.45 deg)
#Flux inside disk mask: 76.62 mJy
#Peak intensity of source: 7.49 mJy/beam
#rms: 1.52e-02 mJy/beam
#Peak SNR: 493.23

# RMS in mJy
rms_com_p2 = imstat(imagename=combined_cont_p2+'.image', region=res_mask_LB)['rms'][0]*10**3

# Third self-calibration
os.system('rm -rf '+combined_cont_p2+'.cal')
gaincal(vis=combined_cont_p2+'.ms',
        caltable=combined_cont_p2+'.cal',
        combine= 'spw, scan',
        gaintype='T',
        spw=combined_contspw,
        refant = combined_refant,
        solint='60s',
        calmode='p',
        minsnr=1.5,
        minblperant=4)

'''
Too much flags
'''

if not skip_plots:
    # Plot the phase calibration
    plotcal(caltable=combined_cont_p2+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/14/00~2017/05/15/00',
            markersize=5,
            fontsize=10.0,
            figfile=combined_cont_p2+'a.png',
            showgui=True)

    plotcal(caltable=combined_cont_p2+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/16/00~2017/05/18/00',
            markersize=5,
            fontsize=10.0,
            figfile=combined_cont_p2+'b.png',
            showgui=True)

    plotcal(caltable=combined_cont_p2+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/09/24/00~2017/09/25/00',
            markersize=5,
            fontsize=10.0,
            figfile=combined_cont_p2+'c.png',
            showgui=True)

# Apply calibration
applycal(vis=combined_cont_p2+'.ms', 
         spw=combined_contspw, 
         spwmap=combined_spwmap, 
         gaintable=[combined_cont_p2+'.cal'], 
         interp='linearPD', 
         calwt=True, 
         applymode='calonly')


#######################################################################
#                     COMBINED PHASE-SELFCAL 3                        #
#######################################################################

# Name
combined_cont_p3 = prefix+'_combined_p3'

# Split the data to continue with the calibrations
os.system('rm -rf '+combined_cont_p3+'.ms')
split(vis=combined_cont_p2+'.ms',
      outputvis=combined_cont_p3+'.ms',
      datacolumn='corrected')


# Clean for selfcalibration
tclean_wrapper(vis=combined_cont_p3+'.ms', \
               imagename=combined_cont_p3, \
               imsize=combined_imsize, \
               mask=mask_LB, \
               scales=combined_scales, \
               robust=robust, \
               threshold=str(2*rms_com_p2)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(combined_cont_p3+'.image', disk_mask = mask_LB_main, noise_mask = res_mask_LB)
#HTLup_combined_p3.image
#Beam 0.038 arcsec x 0.033 arcsec (69.45 deg)
#Flux inside disk mask: 76.31 mJy
#Peak intensity of source: 8.00 mJy/beam
#rms: 1.41e-02 mJy/beam
#Peak SNR: 568.22

# RMS in mJy
rms_com_p3 = imstat(imagename=combined_cont_p3+'.image', region=res_mask_LB)['rms'][0]*10**3

# Phase self-calibration
os.system('rm -rf '+combined_cont_p3+'.cal')
gaincal(vis=combined_cont_p3+'.ms',
        caltable=combined_cont_p3+'.cal',
        combine= 'spw, scan',
        gaintype='T',
        spw=combined_contspw,
        refant = combined_refant,
        solint='30s',
        calmode='p',
        minsnr=1.5,
        minblperant=4)

'''
Too many flags to write them here. They are in spw8 and spw12
'''

if not skip_plots:
    # Plot the phase calibration
    plotcal(caltable=combined_cont_p3+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/14/00~2017/05/15/00',
            markersize=5,
            fontsize=10.0,
            figfile=combined_cont_p3+'a.png',
            showgui=True)

    plotcal(caltable=combined_cont_p3+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/05/16/00~2017/05/18/00',
            markersize=5,
            fontsize=10.0,
            figfile=combined_cont_p3+'b.png',
            showgui=True)

    plotcal(caltable=combined_cont_p3+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            iteration='antenna',
            plotrange=[0, 0, -180, 180],
            timerange='2017/09/24/00~2017/09/25/00',
            markersize=5,
            fontsize=10.0,
            figfile=combined_cont_p3+'c.png',
            showgui=True)

# Apply calibration
applycal(vis=combined_cont_p3+'.ms', 
         spw=combined_contspw, 
         spwmap=combined_spwmap, 
         gaintable=[combined_cont_p3+'.cal'], 
         interp='linearPD', 
         calwt=True, 
         applymode='calonly')

#######################################################################
#                        COMBINED AMP-SELFCAL 0                       #
#######################################################################

# Name
combined_cont_a0 = prefix+'_combined_a0'

# Split the data to continue with the calibrations
os.system('rm -rf '+combined_cont_a0+'.ms')
split(vis=combined_cont_p3+'.ms',
      outputvis=combined_cont_a0+'.ms',
      datacolumn='corrected')


# Clean for selfcalibration. We push for 1.5rms.
tclean_wrapper(vis=combined_cont_a0+'.ms', \
               imagename=combined_cont_a0, \
               imsize=combined_imsize, \
               mask=mask_LB, \
               scales=combined_scales, \
               robust=robust, \
               threshold=str(1.5*rms_com_p3)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(combined_cont_a0+'.image', disk_mask = mask_LB_main, noise_mask = res_mask_LB)
#HTLup_combined_a0.image
#Beam 0.038 arcsec x 0.033 arcsec (69.45 deg)
#Flux inside disk mask: 76.44 mJy
#Peak intensity of source: 8.27 mJy/beam
#rms: 1.41e-02 mJy/beam
#Peak SNR: 587.77

# The increase is only 3 percent, and we are getting a lot of flags
# The decrease in the rms is very low, and only the peak is increasing
# its intensity.
# We stopped the phase calibration here.

# RMS in mJy
rms_com_a0 = imstat(imagename=combined_cont_a0+'.image', region=res_mask_LB)['rms'][0]*10**3


# First amp-calibration
os.system('rm -rf '+combined_cont_a0+'.cal')
gaincal(vis=combined_cont_a0+'.ms',
        caltable=combined_cont_a0+'.cal',
        refant=combined_refant,
        combine='spw, scan', 
        solint='360',
        calmode='ap',
        gaintype='T',
        spw=combined_contspw,
        minsnr=3.0,
        minblperant=4, 
        solnorm=False)

'''
2 of 39 solutions flagged due to SNR < 3 in spw=8 at 2017/09/24/18:03:05.3
2 of 39 solutions flagged due to SNR < 3 in spw=8 at 2017/09/24/18:09:42.7
1 of 39 solutions flagged due to SNR < 3 in spw=8 at 2017/09/24/18:12:38.6
2 of 39 solutions flagged due to SNR < 3 in spw=8 at 2017/09/24/18:22:23.9
1 of 39 solutions flagged due to SNR < 3 in spw=8 at 2017/09/24/18:29:10.7
7 of 39 solutions flagged due to SNR < 3 in spw=12 at 2017/09/24/19:33:25.5
1 of 39 solutions flagged due to SNR < 3 in spw=12 at 2017/09/24/19:36:01.5
4 of 39 solutions flagged due to SNR < 3 in spw=12 at 2017/09/24/19:40:01.6
1 of 39 solutions flagged due to SNR < 3 in spw=12 at 2017/09/24/19:43:31.6
2 of 39 solutions flagged due to SNR < 3 in spw=12 at 2017/09/24/19:46:48.0
2 of 39 solutions flagged due to SNR < 3 in spw=12 at 2017/09/24/19:53:41.1
2 of 39 solutions flagged due to SNR < 3 in spw=12 at 2017/09/24/20:00:34.9
1 of 39 solutions flagged due to SNR < 3 in spw=12 at 2017/09/24/20:04:46.6
10 of 39 solutions flagged due to SNR < 3 in spw=12 at 2017/09/24/20:07:29.9
1 of 39 solutions flagged due to SNR < 3 in spw=12 at 2017/09/24/20:14:16.2
1 of 39 solutions flagged due to SNR < 3 in spw=12 at 2017/09/24/20:19:24.4
'''


if not skip_plots:
    # Plot the first phase calibration
    plotcal(caltable=combined_cont_a0+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            plotrange=[0, 0, 0, 0],
            iteration='antenna',
            timerange='2017/05/14/00~2017/05/15/00',
            figfile=combined_cont_a0+'_a.png',
            showgui=True)

    plotcal(caltable=combined_cont_a0+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            plotrange=[0, 0, 0, 0],
            iteration='antenna',
            timerange='2017/05/16/00~2017/05/18/00',
            figfile=combined_cont_a0+'_b.png',
            showgui=True)

    plotcal(caltable=combined_cont_a0+'.cal',
            xaxis='time',
            yaxis='amp',
            subplot=221,
            plotrange=[0, 0, 0, 0],
            iteration='antenna',
            timerange='2017/09/24/00~2017/09/25/00',
            figfile=combined_cont_a0+'_c.png',
            showgui=True)

# Apply calibration
applycal(vis=combined_cont_a0+'.ms',
         gaintable=[combined_cont_a0+'.cal'],
         spw=combined_contspw, 
         spwmap=combined_spwmap, 
         interp='linearPD',
         calwt=True, 
         applymode='calonly')



#######################################################################
#                      COMBINED AMP-SELFCAL 1                         #
#######################################################################

# Name
combined_cont_a1 = prefix+'_combined_a1'

# Split the data to continue with the calibrations
os.system('rm -rf '+combined_cont_a1+'.*')
split(vis=combined_cont_a0+'.ms',
      outputvis=combined_cont_a1+'.ms',
      datacolumn='corrected')


# Clean for selfcalibration
tclean_wrapper(vis=combined_cont_a1+'.ms', \
               imagename=combined_cont_a1, \
               imsize=combined_imsize, \
               mask=mask_LB, \
               scales=combined_scales, \
               robust=robust, \
               threshold=str(2.*rms_com_a0)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(combined_cont_a1+'.image', disk_mask = mask_LB_main, noise_mask = res_mask_LB)
#HTLup_combined_a1.image
#Beam 0.038 arcsec x 0.033 arcsec (61.46 deg)
#Flux inside disk mask: 76.71 mJy
#Peak intensity of source: 8.28 mJy/beam
#rms: 1.41e-02 mJy/beam
#Peak SNR: 586.95

# RMS in mJy
rms_com_a1 = imstat(imagename=combined_cont_a1+'.image', region=res_mask_LB)['rms'][0]*10**3

# First amp-calibration
os.system('rm -rf '+combined_cont_a1+'.cal')
gaincal(vis=combined_cont_a1+'.ms',
        caltable=combined_cont_a1+'.cal',
        refant=combined_refant,
        combine='spw, scan', 
        solint='180s',
        calmode='ap',
        gaintype='T',
        spw=combined_contspw,
        minsnr=3.0,
        minblperant=4, 
        solnorm=False)

'''
Too much flags
'''


if not skip_plots:
    # Plot the first phase calibration
    plotcal(caltable=combined_cont_a1+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            plotrange=[0, 0, 0, 0],
            iteration='antenna',
            timerange='2017/05/14/00~2017/05/15/00',
            figfile=combined_cont_a1+'_a.png',
            showgui=True)

    plotcal(caltable=combined_cont_a1+'.cal',
            xaxis='time',
            yaxis='phase',
            subplot=221,
            plotrange=[0, 0, 0, 0],
            iteration='antenna',
            timerange='2017/05/16/00~2017/05/18/00',
            figfile=combined_cont_a1+'_b.png',
            showgui=True)

    plotcal(caltable=combined_cont_a1+'.cal',
            xaxis='time',
            yaxis='amp',
            subplot=221,
            plotrange=[0, 0, 0, 0],
            iteration='antenna',
            timerange='2017/09/24/00~2017/09/25/00',
            figfile=combined_cont_a1+'_c.png',
            showgui=True)

# Apply calibration
applycal(vis=combined_cont_a1+'.ms',
         gaintable=[combined_cont_a1+'.cal'],
         spw=combined_contspw, 
         spwmap=combined_spwmap, 
         interp='linearPD',
         calwt=True, 
         applymode='calonly')


#######################################################################
#                              FINAL IMAGE                            #
#######################################################################

robust = 0.5

finalms = prefix+'_combined_selfcal_ap'

# Split the data, in the final ms file.
os.system('rm -rf '+finalms+'.ms')
split(vis=combined_cont_a1+'.ms',
      outputvis=finalms+'.ms',
      datacolumn='corrected')

# First Clean for selfcalibration
tclean_wrapper(vis=finalms+'.ms', \
               imagename=finalms+'_'+str(robust), \
               imsize=combined_imsize, \
               mask=mask_LB, \
               scales=combined_scales, \
               robust=robust, \
               threshold=str(2*rms_com_a1)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(finalms+'_'+str(robust)+'.image', disk_mask = mask_LB_main, noise_mask = res_mask_LB)

# RMS in mJy
rms_com_ap = imstat(imagename=finalms+'_'+str(robust)+'.image', region=res_mask_LB)['rms'][0]*10**3


# ROBUST 0.5
#HTLup_combined_selfcal_ap_0.5.image
#Beam 0.037 arcsec x 0.033 arcsec (59.46 deg)
#Flux inside disk mask: 76.70 mJy
#Peak intensity of source: 8.03 mJy/beam
#rms: 1.38e-02 mJy/beam
#Peak SNR: 583.06

'''
There is a decrease in SNR with the last selfcal, which may be due to
antenna flagging. we proceed with only the first amp calibration
to generate the final image.
'''


robust = 0.5

finalms = prefix+'_combined_selfcal_ap'

# Split the data, in the final ms file.
os.system('rm -rf '+finalms+'.ms')
split(vis=combined_cont_a0+'.ms',
      outputvis=finalms+'.ms',
      datacolumn='corrected')

# First Clean for selfcalibration
tclean_wrapper(vis=finalms+'.ms', \
               imagename=finalms+'_'+str(robust), \
               imsize=combined_imsize, \
               mask=mask_LB, \
               scales=combined_scales, \
               robust=robust, \
               threshold=str(2*rms_com_a0)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(finalms+'_'+str(robust)+'.image', disk_mask = mask_LB_main, noise_mask = res_mask_LB)

# RMS in mJy
rms_com_ap = imstat(imagename=finalms+'_'+str(robust)+'.image', region=res_mask_LB)['rms'][0]*10**3


# ROBUST 0.5
#HTLup_combined_selfcal_ap_0.5.image
#Beam 0.038 arcsec x 0.033 arcsec (61.46 deg)
#Flux inside disk mask: 76.67 mJy
#Peak intensity of source: 8.25 mJy/beam
#rms: 1.41e-02 mJy/beam
#Peak SNR: 585.28


exportfits(imagename=finalms+'_0.5.image', \
           fitsimage=prefix+'_combined_selfcal_ap.fits', \
           history=False, overwrite=True)
