#!/usr/bin/env python
# -*- coding: utf-8 -*-
# /almadata02/lperez/casa_5.1.1/casa-release-5.1.1-5.el7/bin/casa

#######################################################################
#                        AS 205 Self-Calibration                      #
#######################################################################

'''
Universidad de Chile
Facultad de Ciencias Fisicas y Matematicas
Departamento de Astronomia

Nicolas Troncoso Kurtovic
mail: nicokurtovic at gmail.com

This script was written for CASA 5.1.1 to
self-calibrate the short and long baselines of AS205 datasets. This includes:
- 2 SB from archive.
- 1 SB from Large Program.
- 1 LB from Large Program.
We are naming this datasets by short-long plus a chronological number.
'''

# Execute the reduction functions
execfile('reduction_utils.py')

# Append the au functions from other directory.
sys.path.append('/umi_01/nkurtovic/HTLup/analysis_scripts/')
import analysisUtils as au


#######################################################################
#                          NAMES AND PATH                             #
#######################################################################

# Do you want to skip the plots of images and interactive clean process?
skip_plots=True

# Name of the object
prefix = 'AS205'

# Frequency of 12CO 2-1 line
rest_freq = 2.30538e11 # Hz
# Other lines that appear in SB1 and SB2
rest_freq_13CO21 = 2.20399e11 # Hz
rest_freq_C18O21 = 2.1956e11  # Hz


#

# Paths, names and lines in the data. Fill this dictionary with listobs.
# line_spws have the spws with lines that need to be flagged.
# line_freqs have the frequencies to flag. In this case is the 12CO 2-1 line

# Build the path to each dataset
path_SB1 = '/umi_01/nkurtovic/AS205/uid___A002_X3b3400_Xcd7.ms.split.cal'
path_SB2 = '/umi_01/nkurtovic/AS205/uid___A002_X3f6a86_X5da.ms.split.cal'
path_SB3 = '/umi_01/nkurtovic/AS205/as205_p484_SB.ms'
path_LB1 = '/umi_01/nkurtovic/AS205/as205_p484_LB.ms'

data_params = {'SB1': {'vis' : path_SB1,
                      'name': 'SB1', \
                      'field': 'V866 Sco', \
                       'line_spws': np.array([0, 2, 3]), \
                       'line_freqs': np.array([rest_freq, rest_freq_13CO21, rest_freq_C18O21])
                     },
               'SB2': {'vis' : path_SB2,
                      'name': 'SB2', \
                      'field': 'V866 Sco', \
                       'line_spws': np.array([0, 2, 3]), \
                       'line_freqs': np.array([rest_freq, rest_freq_13CO21, rest_freq_C18O21])
                     },
               'SB3': {'vis' : path_SB3,
                      'name': 'SB3', \
                      'field': 'AS_205', \
                       'line_spws': np.array([0, 4, 8]), \
                       'line_freqs': np.array([rest_freq, rest_freq, rest_freq])
                     },
               'LB1': {'vis' : path_LB1,
                      'name' : 'LB1',
                      'field': 'AS_205',
                      'line_spws': np.array([3]), 
                      'line_freqs': np.array([rest_freq]),
                      }}

'''
Important stuff about the datasets:
SB1: 4 spws, the CO line is in the spw0, observed in march 2012.
SB2: 4 spws, the CO line is in the spw0, observed in may 2012.
SB3: 12 spws, CO line in 0, 4 and 8. observed in may 2017.
LB1: 4 spws, CO line in spw3, observed in september 2017.
'''


#######################################################################
#                           LINE FLAGGING                             #
#######################################################################

'''
To flag the CO line, we proceed inspecting by eye the location in
channels and spw. Flag ~50 km/s around 12CO 2-1 line. Each channel in
these spectral windows has 0.635 km/s, so we need to
flag ~160 channels in total. (each channel is half that
speed to take the mean)
'''

# rest_freq_13CO21 = 2.20399e11 # Hz
# rest_freq_C18O21 = 2.1956e11  # Hz

# Visual inspection of the spws in each SB data.
if not skip_plots:
    # Plot the amplitude of each channel, in groups of spw.
    plotms(vis=path_SB1, \
           xaxis='channel', \
           yaxis='amplitude', \
           avgtime='1e8', \
           ydatacolumn='data', \
           field=data_params['SB1']['field'], \
           avgscan=True, \
           avgbaseline=True, \
           iteraxis='spw', \
           restfreq=str(rest_freq))

    plotms(vis=path_SB2, \
           xaxis='velocity', \
           yaxis='amplitude', \
           avgtime='1e8', \
           ydatacolumn='data', \
           field=data_params['SB2']['field'], \
           avgscan=True, \
           avgbaseline=True, \
           iteraxis='spw', \
           restfreq=str(rest_freq_C18O21))

    plotms(vis=path_SB3, \
           xaxis='velocity', \
           yaxis='amplitude', \
           avgtime='1e8', \
           ydatacolumn='data', \
           field=data_params['SB3']['field'], \
           avgscan=True, \
           avgbaseline=True, \
           iteraxis='spw', \
           restfreq=str(rest_freq))

    plotms(vis=path_LB1, \
           xaxis='frequency', \
           yaxis='amplitude', \
           avgtime='1e8', \
           ydatacolumn='data', \
           field=data_params['LB1']['field'], \
           avgscan=True, \
           avgbaseline=True, \
           iteraxis='spw', \
           restfreq=str(rest_freq))

'''
Position of the line depends on the SB dataset that is observed.
In SB1, the central position is aproximately in -31km/s, but
the two disks has different radial velocity, so the mid
velocity observed should be something like 36km/s.
In SB2, the central position is aproximately in -25km/s.
In SB3, the central position is aproximately in -11km/s.

This issue is only observable in the plotms, cause the get_flagchannels needs
the real velocity (~4km/s) to flag the correct channels. We continue by
flagging the known lines.
'''

# Find the channels that will be flagged in the datasets.
# Delete previous runs.
os.system('rm -rf '+path_SB1+'.flagversions*')
os.system('rm -rf '+path_SB2+'.flagversions*')
os.system('rm -rf '+path_SB3+'.flagversions*')
os.system('rm -rf '+path_LB1+'.flagversions*')

# Find
SB1_flagchannels = get_flagchannels(data_params['SB1'], \
                                    prefix, \
                                    velocity_range=np.array([-21., 29.]))
SB2_flagchannels = get_flagchannels(data_params['SB2'], \
                                    prefix, \
                                    velocity_range=np.array([-21., 29.]))
SB3_flagchannels = get_flagchannels(data_params['SB3'], \
                                    prefix, \
                                    velocity_range=np.array([-21., 29.]))
LB1_flagchannels = get_flagchannels(data_params['LB1'], \
                                    prefix, \
                                    velocity_range=np.array([-21., 29.]))
# Flagchannels input string for SB1: '0:2232~3492, 2:651~1855, 3:148~1348'
# Flagchannels input string for SB2: '0:1868~3128, 2:999~2204, 3:495~1695'
# Flagchannels input string for SB3: '0:1841~1998, 4:1841~1998, 8:1841~1998'
# Flagchannels input string for LB1: '3:1841~1998'

# Average continuum. This will generate the file 'prefix+_*B_initcont.ms'
# Delete previous run.
os.system('rm -rf '+prefix+'_SB1_initcont.*')
os.system('rm -rf '+prefix+'_SB2_initcont.*')
os.system('rm -rf '+prefix+'_SB3_initcont.*')
os.system('rm -rf '+prefix+'_LB1_initcont.*')
# Average.
avg_cont(data_params['SB1'], prefix, flagchannels=SB1_flagchannels)
avg_cont(data_params['SB2'], prefix, flagchannels=SB2_flagchannels)
avg_cont(data_params['SB3'], prefix, flagchannels=SB3_flagchannels)
avg_cont(data_params['LB1'], prefix, flagchannels=LB1_flagchannels)


#######################################################################
#                  DEFINE MASK AND FIRST IMAGE                        #
#######################################################################

# Multiscales in pixels for LB dataset.
scales_LB = [0, 11, 33, 55]    #0x, 1x, 3x, 5x


# Image the SB ms file interactively. Inspection to define the mask
if not skip_plots:
    tclean_wrapper(vis=prefix+'_SB1_initcont.ms', \
                   imagename=prefix+'_SB1_initcont', \
                   scales=[0], imsize=900, interactive=True)
    tclean_wrapper(vis=prefix+'_SB2_initcont.ms', \
                   imagename=prefix+'_SB2_initcont', \
                   scales=[0], imsize=900, interactive=True)
    tclean_wrapper(vis=prefix+'_SB3_initcont.ms', \
                   imagename=prefix+'_SB3_initcont', \
                   scales=[0], imsize=900, interactive=True)
    tclean_wrapper(vis=prefix+'_LB1_initcont.ms', \
                   imagename=prefix+'_LB1_initcont', \
                   scales=scales_LB, imsize=3000, interactive=True)


# Use this quick imaging to find centroids and positions. With fit_gaussian
# you can find the optimal positions to build the masks.

#########################
# LONG BASELINE MASKS
# AND FIRST IMAGE
#########################

'''
In the LB dataset we can observe two disks at a distance of 1.2arcsec
between their centers. We will mask them sepparately, and calculate the
rms with a ring around them.

The beam is elliptical, so we are going to use uvtappering to circularize
it, and then obtain a more reliable centroid, PA and inc estimations
through the gaussian fit.
'''

# Define the center of the main disk mask in LB data. First we used
# visual inspection to define centers, and then the gaussian centroid.
center_ra_LB_main  = '16h11m31.351317s'
center_dec_LB_main = '-18d38m26.24671s'
semimajor_LB_main  = '0.50arcsec'
semiminor_LB_main  = '0.60arcsec'
center_LB_main = center_ra_LB_main + ' ' + center_dec_LB_main
# Define the center of the secondary disk mask in LB data
center_ra_LB_second  = '16h11m31.294763s'
center_dec_LB_second = '-18d38m27.27550s'
semimajor_LB_second  = '0.26arcsec'
semiminor_LB_second  = '0.48arcsec'
PA_LB_second = 18.5
center_LB_second = center_ra_LB_second + ' ' + center_dec_LB_second
# Write position angle in string and in radians
str_PA_LB_second = str(PA_LB_second * (np.pi / 180))+'rad'

# First object Mask
mask_LB_main = 'ellipse[[%s, %s], [%s, %s], 0rad]' % (center_ra_LB_main, \
                                                      center_dec_LB_main, \
                                                      semimajor_LB_main, \
                                                      semiminor_LB_main)
# Second object Mask

mask_LB_second = 'ellipse[[%s, %s], [%s, %s], %s]' % (center_ra_LB_second, \
                                                      center_dec_LB_second, \
                                                      semimajor_LB_second, \
                                                      semiminor_LB_second, \
                                                      str_PA_LB_second)

# Create a residual mask
res_mask_LB = 'annulus[[%s, %s], [%s, %s]]' % (center_ra_LB_main, \
                                               center_dec_LB_main, \
                                               '1.5arcsec', '2.5arcsec')
mask_LB = [mask_LB_main, mask_LB_second]

uvtaper_LB = ['0mas', '40mas', '90deg']

#for i in ['.image', '.residual', '.pb', '.sumwt', '.psf', '.model']:
#    os.system('rm -rf '+prefix+'_LB1_initcont'+i)
# Image non interactively
tclean_wrapper(vis=prefix+'_LB1_initcont.ms', \
               imagename=prefix+'_LB1_initcont', \
               scales=scales_LB, \
               mask=mask_LB, \
               savemodel='modelcolumn', \
               threshold='0.1mJy', \
               uvtaper=uvtaper_LB, \
               interactive=False)

estimate_SNR(prefix+'_LB1_initcont.image', disk_mask = mask_LB_main, noise_mask = res_mask_LB)
# WITHOUT UVTAPER
#AS205_LB1_initcont.image
#Beam 0.032 arcsec x 0.020 arcsec (-85.30 deg)
#Flux inside disk mask: 360.29 mJy
#Peak intensity of source: 3.36 mJy/beam
#rms: 3.78e-02 mJy/beam
#Peak SNR: 89.00

# WITH UVTAPER
#AS205_LB1_initcont.image
#Beam 0.039 arcsec x 0.037 arcsec (32.78 deg)
#Flux inside disk mask: 359.48 mJy
#Peak intensity of source: 6.59 mJy/beam
#rms: 7.16e-02 mJy/beam
#Peak SNR: 92.08


#########################
# SHORT BASELINE MASKS
# AND FIRST IMAGES
#########################

# For short baselines we can use the same masks that were
# defined for LB. We are going to increase a little the size
# of the masks, but will remain in the same position.
semimajor_SB_main  = '0.55arcsec'
semiminor_SB_main  = '0.82arcsec'
# Define the center of the secondary disk mask in LB data
semimajor_SB_second  = '0.3arcsec'
semiminor_SB_second  = '0.52arcsec'

# First object Mask
mask_SB_main = 'ellipse[[%s, %s], [%s, %s], 0rad]' % (center_ra_LB_main, \
                                                      center_dec_LB_main, \
                                                      semimajor_SB_main, \
                                                      semiminor_SB_main)
# Second object Mask

mask_SB_second = 'ellipse[[%s, %s], [%s, %s], %s]' % (center_ra_LB_second, \
                                                      center_dec_LB_second, \
                                                      semimajor_SB_second, \
                                                      semiminor_SB_second, \
                                                      str_PA_LB_second)

# Create a residual mask
res_mask_SB = 'annulus[[%s, %s], [%s, %s]]' % (center_ra_LB_main, \
                                               center_dec_LB_main, \
                                               '3.0arcsec', '5.0arcsec')
mask_SB = [mask_SB_main, mask_SB_second]


# Image non interactively
tclean_wrapper(vis=prefix+'_SB1_initcont.ms', 
               imagename=prefix+'_SB1_initcont', \
               scales=[0], mask=mask_SB, savemodel='modelcolumn', \
               threshold='1.0mJy', interactive=False)
tclean_wrapper(vis=prefix+'_SB2_initcont.ms', 
               imagename=prefix+'_SB2_initcont', \
               scales=[0], mask=mask_SB, savemodel='modelcolumn', \
               threshold='1.0mJy', interactive=False)
tclean_wrapper(vis=prefix+'_SB3_initcont.ms', 
               imagename=prefix+'_SB3_initcont', \
               scales=[0], mask=mask_SB, savemodel='modelcolumn', \
               threshold='0.2mJy', interactive=False)


estimate_SNR(prefix+'_SB1_initcont.image', disk_mask = mask_LB_main, noise_mask = res_mask_LB)
estimate_SNR(prefix+'_SB2_initcont.image', disk_mask = mask_LB_main, noise_mask = res_mask_LB)
estimate_SNR(prefix+'_SB3_initcont.image', disk_mask = mask_LB_main, noise_mask = res_mask_LB)

#AS205_SB1_initcont.image
#Beam 0.781 arcsec x 0.512 arcsec (-83.41 deg)
#Flux inside disk mask: 255.79 mJy
#Peak intensity of source: 283.43 mJy/beam
#rms: 4.30e+00 mJy/beam
#Peak SNR: 65.92

#AS205_SB2_initcont.image
#Beam 0.585 arcsec x 0.528 arcsec (88.99 deg)
#Flux inside disk mask: 267.69 mJy
#Peak intensity of source: 245.11 mJy/beam
#rms: 1.39e+00 mJy/beam
#Peak SNR: 176.16

#AS205_SB3_initcont.image
#Beam 0.265 arcsec x 0.225 arcsec (87.38 deg)
#Flux inside disk mask: 357.22 mJy
#Peak intensity of source: 101.62 mJy/beam
#rms: 3.46e-01 mJy/beam
#Peak SNR: 293.80


#######################################################################
#                      FIND AND ALIGN CENTROIDS                       #
#######################################################################

'''
We calculate the centroids of each execution. For SB1, SB2 and LB1 there
is only one execution, but SB3 has 3. In case of desalignement, we
will center them to the LB position, because of the high resolution
and signal to noise.

The centroid of the main disk will be used to align.

Remember that in fit_gaussian the mask must be a string, not a mask file.
'''

#########################
# SHORT BASELINE
# GAUSSIAN FIT
#########################

# Image each execution in SB3 dataset.
image_each_obs(data_params['SB3'], prefix, \
               scales=[0], mask=mask_SB, threshold='0.1mJy')
split_all_obs(prefix+'_SB3_initcont.ms', prefix+'_SB3_initcont_exec')


# Find centroids
fit_gaussian(prefix+'_SB1_initcont.image', region=mask_SB_main)
# 16h11m31.354744s -18d38m26.09769s
# Peak of Gaussian component identified with imfit: J2000 16h11m31.354744s -18d38m26.09769s
# PA of Gaussian component: 111.93 deg
# inclination of Gaussian component: 19.18 deg
# Pixel coordinates of peak: x = 465.282 y = 410.810

fit_gaussian(prefix+'_SB2_initcont.image', region=mask_SB_main)
# 16h11m31.356286s -18d38m26.13514s
# Peak of Gaussian component identified with imfit: J2000 16h11m31.356286s -18d38m26.13514s
# PA of Gaussian component: 121.49 deg
# inclination of Gaussian component: 23.26 deg
# Pixel coordinates of peak: x = 464.552 y = 409.562

fit_gaussian(prefix+'_SB3_initcont.image', region=mask_SB_main)
# 16h11m31.351009s -18d38m26.25311s
#Peak of Gaussian component identified with imfit: ICRS 16h11m31.351009s -18d38m26.25311s
#16:11:31.351009 -18:38:26.25311
#Separation: radian = 8.23157e-08, degrees = 0.000005, arcsec = 0.016979
#Peak in J2000 coordinates: 16:11:31.35172, -018:38:26.239466
#PA of Gaussian component: 108.65 deg
#Inclination of Gaussian component: 19.42 deg
#Pixel coordinates of peak: x = 464.318 y = 410.841

fit_gaussian(prefix+'_SB3_initcont_exec0.image', region=mask_SB_main)
# 16h11m11.351910s -18d38m26.26593s
# Peak of Gaussian component identified with imfit: ICRS 16h11m31.351910s -18d38m26.26593s
# 16:11:31.351910 -18:38:26.26593
# Separation: radian = 8.22747e-08, degrees = 0.000005, arcsec = 0.016970
# Peak in J2000 coordinates: 16:11:31.35262, -018:38:26.252286
# PA of Gaussian component: 121.01 deg
# Inclination of Gaussian component: 18.22 deg
# Pixel coordinates of peak: x = 463.891 y = 410.413

fit_gaussian(prefix+'_SB3_initcont_exec1.image', region=mask_SB_main)
#16h11m31.352010s -18d38m26.22882s
#Peak of Gaussian component identified with imfit: ICRS 16h11m31.352010s -18d38m26.22882s
#16:11:31.352010 -18:38:26.22882
#Separation: radian = 8.22747e-08, degrees = 0.000005, arcsec = 0.016970
#Peak in J2000 coordinates: 16:11:31.35272, -018:38:26.215176
#PA of Gaussian component: 100.17 deg
#Inclination of Gaussian component: 17.24 deg
#Pixel coordinates of peak: x = 463.843 y = 411.650

fit_gaussian(prefix+'_SB3_initcont_exec2.image', region=mask_SB_main)
#16h11m31.349837s -18d38m26.25763s
#Peak of Gaussian component identified with imfit: ICRS 16h11m31.349837s -18d38m26.25763s
#16:11:31.349837 -18:38:26.25763
#Separation: radian = 8.23978e-08, degrees = 0.000005, arcsec = 0.016996
#Peak in J2000 coordinates: 16:11:31.35055, -018:38:26.243986
#PA of Gaussian component: 105.04 deg
#Inclination of Gaussian component: 21.32 deg
#Pixel coordinates of peak: x = 464.873 y = 410.690

fit_gaussian(prefix+'_LB1_initcont.image', region=mask_LB_main)
#16h11m31.351310s -18d38m26.24660s
#Peak of Gaussian component identified with imfit: ICRS 16h11m31.351310s -18d38m26.24660s
#16:11:31.351310 -18:38:26.24660
#Separation: radian = 8.22747e-08, degrees = 0.000005, arcsec = 0.016970
#Peak in J2000 coordinates: 16:11:31.35202, -018:38:26.232956
#PA of Gaussian component: 110.75 deg
#Inclination of Gaussian component: 23.78 deg
#Pixel coordinates of peak: x = 1639.604 y = 1114.500

# Secondary disk
fit_gaussian(prefix+'_LB1_initcont.image', region=mask_LB_second)
#16h11m31.294774s -18d38m27.27574s
#Peak of Gaussian component identified with imfit: ICRS 16h11m31.294774s -18d38m27.27574s
#16:11:31.294774 -18:38:27.27574
#Separation: radian = 8.2111e-08, degrees = 0.000005, arcsec = 0.016937
#Peak in J2000 coordinates: 16:11:31.29548, -018:38:27.262096
#PA of Gaussian component: 108.42 deg
#Inclination of Gaussian component: 64.79 deg
#Pixel coordinates of peak: x = 1907.452 y = 771.455



'''
Peaks in J2000
SB1   16h 11m 31.35473,  -18d 38m 26.09852s
SB2   16h 11m 31.35629,  -18d 38m 26.13575s
SB3   16h 11m 31.35172,  -18d 38m 26.239466
SB3_0 16h 11m 31.35262,  -18d 38m 26.252276
SB3_1 16h 11m 31.35272,  -18d 38m 26.215186
SB3_2 16h 11m 31.35055,  -18d 38m 26.243996
LB1   16h 11m 31.35202,  -18d 38m 26.232956

There are differences up to 240mas, which is much greater than LB beam.
'''

common_dir = 'J2000 16h11m31.35202s -18d38m26.232956s'

# Create the shifted ms file of SB datasets
shiftname_SB1 = prefix+'_SB1_initcont_shift'
shiftname_SB2 = prefix+'_SB2_initcont_shift'
shiftname_SB30 = prefix+'_SB3_initcont_exec0_shift'
shiftname_SB31 = prefix+'_SB3_initcont_exec1_shift'
shiftname_SB32 = prefix+'_SB3_initcont_exec2_shift'
shiftname_LB1 = prefix+'_LB1_initcont_shift'
os.system('rm -rf %s.*' % shiftname_SB1)
os.system('rm -rf %s.*' % shiftname_SB2)
os.system('rm -rf %s.*' % shiftname_SB30)
os.system('rm -rf %s.*' % shiftname_SB31)
os.system('rm -rf %s.*' % shiftname_SB31)
os.system('rm -rf %s.*' % shiftname_LB1)

# SB1
fixvis(vis=prefix+'_SB1_initcont.ms', outputvis=shiftname_SB1+'.ms', \
       field=data_params['SB1']['field'], \
       phasecenter='J2000 16h11m31.35473s -18d38m26.09852s')
fixplanets(vis=shiftname_SB1+'.ms', \
           field=data_params['SB1']['field'], direction=common_dir)

# SB2
fixvis(vis=prefix+'_SB2_initcont.ms', outputvis=shiftname_SB2+'.ms', \
       field=data_params['SB2']['field'], \
       phasecenter='J2000 16h11m31.35629s -18d38m26.13575s')
fixplanets(vis=shiftname_SB2+'.ms', \
           field=data_params['SB2']['field'], direction=common_dir)

# SB3 exec0
fixvis(vis=prefix+'_SB3_initcont_exec0.ms', outputvis=shiftname_SB30+'.ms', \
       field=data_params['SB3']['field'], \
       phasecenter='J2000 16h11m31.35262s -18d38m26.252276s')
fixplanets(vis=shiftname_SB30+'.ms', \
           field=data_params['SB3']['field'], direction=common_dir)

# SB3 exec1
fixvis(vis=prefix+'_SB3_initcont_exec1.ms', outputvis=shiftname_SB31+'.ms', \
       field=data_params['SB3']['field'], \
       phasecenter='J2000 16h11m31.35272s -18d38m26.215186s')
fixplanets(vis=shiftname_SB31+'.ms', \
           field=data_params['SB3']['field'], direction=common_dir)

# SB3 exec2
fixvis(vis=prefix+'_SB3_initcont_exec2.ms', outputvis=shiftname_SB32+'.ms', \
       field=data_params['SB3']['field'], \
       phasecenter='J2000 16h11m31.35055s -18d38m26.243996s')
fixplanets(vis=shiftname_SB32+'.ms', \
           field=data_params['SB3']['field'], direction=common_dir)

# LB1
fixvis(vis=prefix+'_LB1_initcont.ms', outputvis=shiftname_LB1+'.ms', \
       field=data_params['LB1']['field'], \
       phasecenter=common_dir)



# New Images to check centroid
tclean_wrapper(vis=shiftname_SB1+'.ms', imagename=shiftname_SB1, \
               mask=mask_SB, scales=[0], threshold='1.0mJy')
tclean_wrapper(vis=shiftname_SB2+'.ms', imagename=shiftname_SB2, \
               mask=mask_SB, scales=[0], threshold='1.0mJy')
tclean_wrapper(vis=shiftname_SB30+'.ms', imagename=shiftname_SB30, \
               mask=mask_SB, scales=[0], threshold='0.2mJy')
tclean_wrapper(vis=shiftname_SB31+'.ms', imagename=shiftname_SB31, \
               mask=mask_SB, scales=[0], threshold='0.2mJy')
tclean_wrapper(vis=shiftname_SB32+'.ms', imagename=shiftname_SB32, \
               mask=mask_SB, scales=[0], threshold='0.2mJy')
tclean_wrapper(vis=shiftname_LB1+'.ms', imagename=shiftname_LB1, \
               mask=mask_LB, scales=scales_LB, threshold='0.1mJy', \
               uvtaper=uvtaper_LB)

# Results
fit_gaussian(shiftname_SB1+'.image', region=mask_SB_main)
# 16h11m31.352050s -18d38m26.23157s
fit_gaussian(shiftname_SB2+'.image', region=mask_SB_main)
# 16h11m31.352055s -18d38m26.23183s
fit_gaussian(shiftname_SB30+'.image', region=mask_SB_main)
# 16h11m31.352025s -18d38m26.23260s
fit_gaussian(shiftname_SB31+'.image', region=mask_SB_main)
# 16h11m31.352011s -18d38m26.23303s
fit_gaussian(shiftname_SB32+'.image', region=mask_SB_main)
# 16h11m31.352028s -18d38m26.23280s
fit_gaussian(shiftname_LB1+'.image', region=mask_LB_main)
# 16h11m31.352018s -18d38m26.23307s

# The difference is ~1mas. We will proceed.


#######################################################################
#                           FLUX CORRECTION                           #
#######################################################################

# Redefine noise masks
res_mask_SB = 'annulus[[%s, %s], [%s, %s]]' % (center_ra_LB_main, \
                                               center_dec_LB_main, \
                                               '8.0arcsec', '11.0arcsec')

# We are going to calculate the rms in the images of the shifted
# SB3 images, and the one with less rms will be used as calibrator.
rms_exec0 = imstat(imagename=shiftname_SB30+'.image', \
                   region=res_mask_SB)['rms'][0]*10**3
rms_exec1 = imstat(imagename=shiftname_SB31+'.image', \
                   region=res_mask_SB)['rms'][0]*10**3
rms_exec2 = imstat(imagename=shiftname_SB32+'.image', \
                   region=res_mask_SB)['rms'][0]*10**3
print (rms_exec0, rms_exec1, rms_exec2)
# rms mJy of each execution
# (0.2247990773012572, 0.34920840346455695, 0.30993271493078195)

# The rough values from gaussian fitting of LB main disk will be 
# used for deprojection.
PA = 111.
incl = 24.

datasets = [shiftname_SB1+'.ms', \
            shiftname_SB2+'.ms', \
            shiftname_SB30+'.ms', \
            shiftname_SB31+'.ms', \
            shiftname_SB32+'.ms', \
            shiftname_LB1+'.ms']

# We'll check the flux of the calibrators in the SB3 data, and then
# calibrate the other observations with this measurements.

# SB3 execution 0 had J1517-2422 as a calibrator, with flux 1.948Jy.
au.getALMAFlux('J1517-2422', frequency='230.538GHz', date='2017/05/14')
#Closest Band 3 measurement: 2.420 +- 0.060 (age=+0 days) 91.5 GHz
#Closest Band 7 measurement: 1.840 +- 0.090 (age=-1 days) 343.5 GHz
#getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -1 days from 2017/05/14, with age separation of 0 days
#  2017/05/15: freqs=[103.49, 91.46, 343.48], fluxes=[2.55, 2.49, 1.84]
#Median Monte-Carlo result for 230.538000 = 2.045217 +- 0.159999 (scaled MAD = 0.157413)
#Result using spectral index of -0.234794 for 230.538 GHz from 2.420 Jy at 91.460 GHz = 1.947794 +- 0.159999 Jy
# 5% difference

# SB3 execution 1 had J1733-1304 as a calibrator, with flux 1.622Jy.
au.getALMAFlux('J1733-1304', frequency='230.537GHz', date='2017/05/17')
#Closest Band 3 measurement: 3.020 +- 0.060 (age=+0 days) 103.5 GHz
#Closest Band 7 measurement: 1.190 +- 0.060 (age=+0 days) 343.5 GHz
#getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 0 days from 2017/05/17, with age separation of 0 days
#  2017/05/17: freqs=[103.49, 343.48], fluxes=[3.02, 1.19]
#Median Monte-Carlo result for 230.537000 = 1.621264 +- 0.130647 (scaled MAD = 0.129509)
#Result using spectral index of -0.776310 for 230.537 GHz from 3.020 Jy at 103.490 GHz = 1.621711 +- 0.130647 Jy
# 1% difference

# SB3 execution 2 had J1517-2422 as a calibrator, with flux 2.113Jy.
au.getALMAFlux('J1517-2422', frequency='230.537GHz', date='2017/05/19')
#Closest Band 3 measurement: 2.550 +- 0.060 (age=+4 days) 103.5 GHz
#Closest Band 3 measurement: 2.490 +- 0.050 (age=+4 days) 91.5 GHz
#Closest Band 7 measurement: 1.750 +- 0.060 (age=+2 days) 343.5 GHz
#getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 4 days from 2017/05/19, with age separation of 0 days
#  2017/05/15: freqs=[103.49, 91.46, 343.48], fluxes=[2.55, 2.49, 1.84]
#Median Monte-Carlo result for 230.537000 = 2.048019 +- 0.160344 (scaled MAD = 0.161804)
#Result using spectral index of -0.234794 for 230.537 GHz from 2.520 Jy at 97.475 GHz = 2.058844 +- 0.160344 Jy
# 10% difference

# SB3 execution 0 has little difference between the calibrator 
# and the getALMAFlux, and also the less rms between SB3 executions,
# so we are calibrating every dataset with this observation.

if not skip_plots:
    for msfile in datasets:
        export_MS(msfile)
        #Measurement set exported to AS205_SB1_initcont_shift.vis.npz
        #Measurement set exported to AS205_SB2_initcont_shift.vis.npz
        #Measurement set exported to AS205_SB3_initcont_exec0_shift.vis.npz
        #Measurement set exported to AS205_SB3_initcont_exec1_shift.vis.npz
        #Measurement set exported to AS205_SB3_initcont_exec2_shift.vis.npz
        #Measurement set exported to AS205_LB1_initcont_shift.vis.npz

    # PLot fluxes comparing datasets with SB3exec0
    plot_deprojected([shiftname_SB30+'.vis.npz', \
                      shiftname_SB1+'.vis.npz'], PA=PA, incl=incl)
    # There is a difference between SB1 and SB30
    
    plot_deprojected([shiftname_SB30+'.vis.npz', \
                      shiftname_SB2+'.vis.npz'], PA=PA, incl=incl)
    # There is a difference between SB2 and SB30

    plot_deprojected([shiftname_SB30+'.vis.npz', \
                      shiftname_SB31+'.vis.npz'], PA=PA, incl=incl)
    # There is a difference between SB31 and SB30

    plot_deprojected([shiftname_SB30+'.vis.npz', \
                      shiftname_SB32+'.vis.npz'], PA=PA, incl=incl)
    # There is a difference in the short lambda part of this datasets

    plot_deprojected([shiftname_SB30+'.vis.npz', \
                      shiftname_LB1+'.vis.npz'], PA=PA, incl=incl)
    # Almost match

    # We calculate the difference between all executions.
    estimate_flux_scale(reference=shiftname_SB30+'.vis.npz', \
                        comparison=shiftname_SB1+'.vis.npz', \
                        incl=incl, PA=PA, uvbins=100+10*np.arange(100))
    estimate_flux_scale(reference=shiftname_SB30+'.vis.npz', \
                        comparison=shiftname_SB2+'.vis.npz', \
                        incl=incl, PA=PA, uvbins=100+10*np.arange(100))
    estimate_flux_scale(reference=shiftname_SB30+'.vis.npz', \
                        comparison=shiftname_SB31+'.vis.npz', \
                        incl=incl, PA=PA, uvbins=100+10*np.arange(100))
    estimate_flux_scale(reference=shiftname_SB30+'.vis.npz', \
                        comparison=shiftname_SB32+'.vis.npz', \
                        incl=incl, PA=PA, uvbins=100+10*np.arange(100))
    estimate_flux_scale(reference=shiftname_SB30+'.vis.npz', \
                        comparison=shiftname_LB1+'.vis.npz', \
                        incl=incl, PA=PA, uvbins=100+10*np.arange(100))

    #The ratio of the fluxes of AS205_SB1_initcont_shift.vis.npz to
    # AS205_SB3_initcont_exec0_shift.vis.npz is 1.16550
    #The scaling factor for gencal is 1.080 for your comparison measurement
    #The error on the weighted mean ratio is 5.012e-04, although it's
    # likely that the weights in the measurement sets are too off by
    # some constant factor

    #The ratio of the fluxes of AS205_SB2_initcont_shift.vis.npz to
    # AS205_SB3_initcont_exec0_shift.vis.npz is 1.06620
    #The scaling factor for gencal is 1.033 for your comparison measurement
    #The error on the weighted mean ratio is 5.244e-04, although it's
    # likely that the weights in the measurement sets are too off by
    # some constant factor

    #The ratio of the fluxes of AS205_SB3_initcont_exec1_shift.vis.npz to
    # AS205_SB3_initcont_exec0_shift.vis.npz is 1.09033
    #The scaling factor for gencal is 1.044 for your comparison measurement
    #The error on the weighted mean ratio is 2.719e-04, although it's
    # likely that the weights in the measurement sets are too off by
    # some constant factor

    #The ratio of the fluxes of AS205_SB3_initcont_exec2_shift.vis.npz to
    # AS205_SB3_initcont_exec0_shift.vis.npz is 1.08228
    #The scaling factor for gencal is 1.040 for your comparison measurement
    #The error on the weighted mean ratio is 2.368e-04, although it's
    # likely that the weights in the measurement sets are too off by
    # some constant factor

    #The ratio of the fluxes of AS205_LB1_initcont_shift.vis.npz to 
    # AS205_SB3_initcont_exec0_shift.vis.npz is 1.01869
    #The scaling factor for gencal is 1.009 for your comparison measurement
    #The error on the weighted mean ratio is 3.464e-04, although it's
    # likely that the weights in the measurement sets are too off by
    # some constant factor

    # Check the corrected differences
    plot_deprojected([shiftname_SB30+'.vis.npz', \
                      shiftname_SB1+'.vis.npz'], \
                      PA=PA, incl=incl, fluxscale=[1., 1./1.16550])
    plot_deprojected([shiftname_SB30+'.vis.npz', \
                      shiftname_SB2+'.vis.npz'], \
                      PA=PA, incl=incl, fluxscale=[1., 1./1.06620])
    plot_deprojected([shiftname_SB30+'.vis.npz', \
                      shiftname_SB31+'.vis.npz'], \
                      PA=PA, incl=incl, fluxscale=[1., 1./1.09033])
    plot_deprojected([shiftname_SB30+'.vis.npz', \
                      shiftname_SB32+'.vis.npz'], \
                      PA=PA, incl=incl, fluxscale=[1., 1./1.08228])
    plot_deprojected([shiftname_SB30+'.vis.npz', \
                      shiftname_LB1+'.vis.npz'], \
                      PA=PA, incl=incl, fluxscale=[1., 1./1.01869])

# Correcting discrepants datasets.
os.system('rm -rf *rescaled.*')
rescale_flux(shiftname_SB1+'.ms',  [1.080])
rescale_flux(shiftname_SB2+'.ms',  [1.033])
rescale_flux(shiftname_SB31+'.ms', [1.044])
rescale_flux(shiftname_SB32+'.ms', [1.040])
rescale_flux(shiftname_LB1+'.ms',  [1.009])
#Splitting out rescaled values into new MS: AS205_SB1_initcont_shift_rescaled.ms
#Splitting out rescaled values into new MS: AS205_SB2_initcont_shift_rescaled.ms
#Splitting out rescaled values into new MS: AS205_SB3_initcont_exec1_shift_rescaled.ms
#Splitting out rescaled values into new MS: AS205_SB3_initcont_exec2_shift_rescaled.ms
#Splitting out rescaled values into new MS: AS205_LB1_initcont_shift_rescaled.ms

export_MS(shiftname_SB1+'_rescaled.ms')
export_MS(shiftname_SB2+'_rescaled.ms')
export_MS(shiftname_SB31+'_rescaled.ms')
export_MS(shiftname_SB32+'_rescaled.ms')
export_MS(shiftname_LB1+'_rescaled.ms')
#Measurement set exported to AS205_SB1_initcont_shift_rescaled.vis.npz
#Measurement set exported to AS205_SB2_initcont_shift_rescaled.vis.npz
#Measurement set exported to AS205_SB3_initcont_exec1_shift_rescaled.vis.npz
#Measurement set exported to AS205_SB3_initcont_exec2_shift_rescaled.vis.npz
#Measurement set exported to AS205_LB1_initcont_shift_rescaled.vis.npz

shift_scaled_SB1 = 'AS205_SB1_initcont_shift_rescaled'
shift_scaled_SB2 = 'AS205_SB2_initcont_shift_rescaled'
shift_scaled_SB30 = shiftname_SB30
shift_scaled_SB31 = 'AS205_SB3_initcont_exec1_shift_rescaled'
shift_scaled_SB32 = 'AS205_SB3_initcont_exec2_shift_rescaled'
shift_scaled_LB1 = 'AS205_LB1_initcont_shift_rescaled'


if skip_plots:
    # Re-plot to see if it worked
    plot_deprojected([shift_scaled_SB30+'.vis.npz', \
                      shift_scaled_SB1+'.vis.npz'], PA=PA, incl=incl)
    # Re-plot to see if it worked
    plot_deprojected([shift_scaled_SB30+'.vis.npz', \
                      shift_scaled_SB2+'.vis.npz'], PA=PA, incl=incl)
    # Re-plot to see if it worked
    plot_deprojected([shift_scaled_SB30+'.vis.npz', \
                      shift_scaled_SB31+'.vis.npz'], PA=PA, incl=incl)
    # Re-plot to see if it worked
    plot_deprojected([shift_scaled_SB30+'.vis.npz', \
                      shift_scaled_SB32+'.vis.npz'], PA=PA, incl=incl)
    # Re-plot to see if it worked
    plot_deprojected([shift_scaled_SB30+'.vis.npz', \
                      shift_scaled_LB1+'.vis.npz'], PA=PA, incl=incl)

# Now that our datasets are shifted and calibrated, we well combine
# the SB executions.
shift_scaled_SB = 'AS205_SB_initcont_shift_scaled'

os.system('rm -rf '+shift_scaled_SB+'.*')
concat(vis=[shift_scaled_SB1+'.ms', shift_scaled_SB2+'.ms', shift_scaled_SB30+'.ms', shift_scaled_SB31+'.ms', shift_scaled_SB32+'.ms'], \
       concatvis=shift_scaled_SB+'.ms', \
       dirtol='0.1arcsec', copypointing=False, freqtol='0')


#######################################################################
#                    SB SELF-CALIBRATION PARAMETERS                   #
#######################################################################

# Robust level
robust = 0.5
# In SB the source is not well resolved. We are going to use few short
# scales. Apparently, the tclean choose to use only puntual sources, 
# but we let the freedom of choosing 1beam sources anyway.
scales_SB = [0, 9]

# We'll search for a reference antenna by inspection in plotants or
# calibration files.
#ref_SB1 = 'DV09'  # Visually selected
#ref_SB2 = 'DV09'  # Visually selected
#ref_SB3 = 'DA46'  # Highest recommended reference antenna present in all SB3
get_station_numbers(shift_scaled_SB1+'.ms', 'DV09')
get_station_numbers(shift_scaled_SB2+'.ms', 'DV09')
get_station_numbers(shift_scaled_SB30+'.ms', 'DA46')
get_station_numbers(shift_scaled_SB31+'.ms', 'DA46')
get_station_numbers(shift_scaled_SB32+'.ms', 'DA46')
#Observation ID 0: DV09@A046
#Observation ID 0: DV09@A046
#Observation ID 0: DA46@A034
#Observation ID 1: DA46@A034
#Observation ID 2: DA46@A034
ref_SB = 'DV09@A046, DA46@A034'

SB_contspws = '0~15'

# Timeranges
SB1_timerange  = '2012/03/27/00:00:01~2012/03/27/23:59:59'
SB2_timerange  = '2012/05/04/00:00:01~2012/05/04/23:59:59'
SB30_timerange = '2017/05/14/00:00:01~2017/05/14/23:59:59'
SB31_timerange = '2017/05/17/00:00:01~2017/05/17/23:59:59'
SB32_timerange = '2017/05/19/00:00:01~2017/05/19/23:59:59'
LB1_timerange  = '2017/09/29/00:00:01~2017/09/29/23:59:59'


#######################################################################
#                     PHASE SELF-CALIBRATION 0                        #
#######################################################################

# Name of the first data.
SB_p0 = prefix+'_SB_p0'

# Split the data to continue with the calibrations
os.system('rm -rf '+SB_p0+'.*')
split(vis=shift_scaled_SB+'.ms',
      outputvis=SB_p0+'.ms',
      datacolumn='data')

# Clean for selfcalibration
tclean_wrapper(vis=SB_p0+'.ms', \
               imagename=SB_p0, \
               mask=mask_SB, \
               scales=scales_SB, \
               robust=robust, \
               threshold='0.2mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(SB_p0+'.image', \
             disk_mask = mask_SB_main, \
             noise_mask = res_mask_SB)
#AS205_SB_p0.image
#Beam 0.268 arcsec x 0.228 arcsec (86.44 deg)
#Flux inside disk mask: 346.66 mJy
#Peak intensity of source: 97.39 mJy/beam
#rms: 1.69e-01 mJy/beam
#Peak SNR: 576.63

# RMS in mJy
rms_SB_p0 = imstat(imagename=SB_p0+'.image', region=res_mask_SB)['rms'][0]*10**3

# Gaincal for self-calibration
os.system('rm -rf '+SB_p0+'.cal')
gaincal(vis=SB_p0+'.ms',
        caltable=SB_p0+'.cal',
        gaintype='T',
        spw=SB_contspws,
        refant = ref_SB,
        solint='120s',
        calmode='p',
        minsnr=1.5,
        minblperant=4)

'''
None solutions were flagged
'''

if not skip_plots:
    # Plot the first phase calibration
    plotcal(caltable=SB_p0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB1_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=SB_p0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB2_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=SB_p0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB30_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=SB_p0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB31_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=SB_p0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB32_timerange,
            markersize=5, fontsize=10.0, showgui=True)

# Apply calibration
applycal(vis=SB_p0+'.ms', spw=SB_contspws, 
         gaintable=[SB_p0+'.cal'], interp='linearPD', calwt=True)


#######################################################################
#                     PHASE SELF-CALIBRATION 1                        #
#######################################################################

# Name of the data.
SB_p1 = prefix+'_SB_p1'

# Split the data to continue with the calibrations
os.system('rm -rf '+SB_p1+'.*')
split(vis=SB_p0+'.ms',
      outputvis=SB_p1+'.ms',
      datacolumn='corrected')

# Clean for selfcalibration. 2*rms_SB_p0>0.2mJy, so we keep 
# the 0.2 as threshold
tclean_wrapper(vis=SB_p1+'.ms', \
               imagename=SB_p1, \
               mask=mask_SB, \
               scales=scales_SB, \
               robust=robust, \
               threshold='0.2mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(SB_p1+'.image', \
             disk_mask = mask_SB_main, \
             noise_mask = res_mask_SB)
#AS205_SB_p1.image
#Beam 0.270 arcsec x 0.228 arcsec (84.95 deg)
#Flux inside disk mask: 352.65 mJy
#Peak intensity of source: 103.14 mJy/beam
#rms: 5.90e-02 mJy/beam
#Peak SNR: 1749.40

# RMS in mJy
rms_SB_p1 = imstat(imagename=SB_p1+'.image', region=res_mask_SB)['rms'][0]*10**3

# Gaincal self-calibration
os.system('rm -rf '+SB_p1+'.cal')
gaincal(vis=SB_p1+'.ms',
        caltable=SB_p1+'.cal',
        gaintype='T',
        spw=SB_contspws,
        refant = ref_SB,
        solint='60s',
        calmode='p',
        minsnr=1.5,
        minblperant=4)

'''
None solutions were flagged
'''

if not skip_plots:
    # Plot phase calibration
    plotcal(caltable=SB_p1+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB1_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=SB_p1+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB2_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=SB_p1+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB30_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=SB_p1+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB31_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=SB_p1+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB32_timerange,
            markersize=5, fontsize=10.0, showgui=True)

# Apply calibration
applycal(vis=SB_p1+'.ms', spw=SB_contspws, 
         gaintable=[SB_p1+'.cal'], interp='linearPD', calwt=True)


#######################################################################
#                        AMP SELF-CALIBRATION 0                       #
#######################################################################

# Name of the data.
SB_a0 = prefix+'_SB_a0'

# Split the data to continue with the calibrations
os.system('rm -rf '+SB_a0+'.*')
split(vis=SB_p1+'.ms',
      outputvis=SB_a0+'.ms',
      datacolumn='corrected')

# Clean for selfcalibration.  The high signal to noise encourage us
# to push the limit to the 1.5rms level.
tclean_wrapper(vis=SB_a0+'.ms', \
               imagename=SB_a0, \
               mask=mask_SB, \
               scales=scales_SB, \
               robust=robust, \
               threshold=str(1.5*rms_SB_p1)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(SB_a0+'.image', \
             disk_mask = mask_SB_main, \
             noise_mask = res_mask_SB)
#AS205_SB_a0.image
#Beam 0.270 arcsec x 0.228 arcsec (84.79 deg)
#Flux inside disk mask: 352.93 mJy
#Peak intensity of source: 103.18 mJy/beam
#rms: 5.83e-02 mJy/beam
#Peak SNR: 1770.71


'''
The decrease is almost 2%. It was tried another round of phase self-cal
with a gaincal of 30s, but the results got worse.
There were a decrease in SNR because of an increase in rms.
It was tried with 1*rms and 2*rms threshold, but the 30s gaincal always
decreased the snr.

#AS205_SB_a0.image
#Beam 0.270 arcsec x 0.228 arcsec (83.98 deg)
#Flux inside disk mask: 353.41 mJy
#Peak intensity of source: 104.39 mJy/beam
#rms: 5.92e-02 mJy/beam
#Peak SNR: 1762.12

We stop the phase cal here, and start the amp calibration.
'''

# RMS in mJy
rms_SB_a0 = imstat(imagename=SB_a0+'.image', region=res_mask_SB)['rms'][0]*10**3

# First self-calibration
os.system('rm -rf '+SB_a0+'.cal')
gaincal(vis=SB_a0+'.ms',
        caltable=SB_a0+'.cal',
        gaintype='T',
        spw=SB_contspws,
        refant = ref_SB,
        solint='inf',
        calmode='ap',
        minsnr=3.0,
        minblperant=4, 
        solnorm=False)

'''
None solutions were flagged
'''

if not skip_plots:
    # Plot the first phase calibration
    plotcal(caltable=SB_a0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -5, 5], timerange=SB1_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=SB_a0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -5, 5], timerange=SB2_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=SB_a0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -5, 5], timerange=SB30_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=SB_a0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -5, 5], timerange=SB31_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=SB_a0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -5, 5], timerange=SB32_timerange,
            markersize=5, fontsize=10.0, showgui=True)

# Apply calibration
applycal(vis=SB_a0+'.ms', spw=SB_contspws, 
         gaintable=[SB_a0+'.cal'], interp='linearPD', calwt=True)


#######################################################################
#                          FINAL SB IMAGE                             #
#######################################################################

# Name of the first data.
SB_ap = prefix+'_SB_ap'

# Split the data to continue with the calibrations
os.system('rm -rf '+SB_ap+'.*')
split(vis=SB_a0+'.ms',
      outputvis=SB_ap+'.ms',
      datacolumn='corrected')

# Clean for imaging
tclean_wrapper(vis=SB_ap+'.ms', \
               imagename=SB_ap, \
               mask=mask_SB, \
               scales=scales_SB, \
               robust=robust, \
               threshold=str(1.*rms_SB_a0)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(SB_ap+'.image', \
             disk_mask = mask_SB_main, \
             noise_mask = res_mask_SB)
#AS205_SB_ap.image
#Beam 0.270 arcsec x 0.227 arcsec (84.89 deg)
#Flux inside disk mask: 353.81 mJy
#Peak intensity of source: 102.50 mJy/beam
#rms: 3.10e-02 mJy/beam
#Peak SNR: 3310.36

# RMS in mJy
rms_SB_ap = imstat(imagename=SB_ap+'.image', region=res_mask_SB)['rms'][0]*10**3


#######################################################################
#                         COMBINE SB AND LB                           #
#######################################################################

# Name
combined_p0 = prefix+'_combined_p0'

# Combined file. Includes the calibrated SB, and the shifted and
# rescaled execution of LB.
os.system('rm -rf '+combined_p0+'.*')
concat(vis=[SB_ap+'.ms', shift_scaled_LB1+'.ms'], concatvis=combined_p0+'.ms', dirtol='0.1arcsec', copypointing=False)


#######################################################################
#                      COMBINED PHASE SELF-CAL 0                      #
#######################################################################

# Robust level
robust = 0.5
# Combined parameters
combined_contspw = '0~19'
combined_spwmap = [0, 0, 0, 0, \
                   4, 4, 4, 4, \
                   8, 8, 8, 8, \
                   12, 12, 12, 12, \
                   16, 16, 16, 16]
# The beam is roughly 11 pixels.
combined_scales = [0, 11, 33, 55]
# I had to use imsize=4000 in order to get the calculation of rms,
# because of the secondary source.
combined_imsize = 3000
# Reference antenna. By visual inspection, DA61 seems like a good candidate
# for LB1 and SB3. We don't have any antenna present in all data. 
# 
#get_station_numbers(combined_p0+'.ms', 'DA61')
get_station_numbers(path_LB1, 'DA61')
#Observation ID 0: DA61@A015
combined_refant = 'DA61@A015, '+ref_SB

# Clean for selfcalibration
tclean_wrapper(vis=combined_p0+'.ms', \
               imagename=combined_p0, \
               imsize=combined_imsize, \
               mask=mask_LB, \
               scales=combined_scales, \
               robust=robust, \
               threshold='0.1mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(combined_p0+'.image', \
             disk_mask=mask_LB_main, noise_mask=res_mask_LB)
#AS205_combined_p0.image
#Beam 0.039 arcsec x 0.025 arcsec (-81.58 deg)
#Flux inside disk mask: 374.69 mJy
#Peak intensity of source: 4.89 mJy/beam
#rms: 2.90e-02 mJy/beam
#Peak SNR: 168.75

# RMS in mJy
rms_LB_p0 = imstat(imagename=combined_p0+'.image', \
                   region=res_mask_LB)['rms'][0]*10**3

# Phase self-calibration
os.system('rm -rf '+combined_p0+'.cal')
gaincal(vis=combined_p0+'.ms',
        caltable=combined_p0+'.cal',
        combine= 'spw, scan',
        gaintype='T',
        spw=combined_contspw,
        refant = combined_refant,
        solint='360s',
        calmode='p',
        minsnr=1.5,
        minblperant=4)

'''
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/22:44:08.8
3 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/22:48:01.7
3 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/22:54:51.2
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/22:58:15.9
4 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:01:38.6
2 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:08:28.0
4 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:22:10.5
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:27:23.4
2 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:31:56.7
'''

if not skip_plots:
    # Plot the first phase calibration
    plotcal(caltable=combined_p0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB1_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_p0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB2_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_p0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB30_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_p0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB31_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_p0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB32_timerange,
            markersize=5, fontsize=10.0, showgui=True)

# Apply calibration
applycal(vis=combined_p0+'.ms', 
         spw=combined_contspw, 
         spwmap=combined_spwmap, 
         gaintable=[combined_p0+'.cal'], 
         interp='linearPD', 
         calwt=True, 
         applymode='calonly')


#######################################################################
#                      COMBINED PHASE SELF-CAL 1                      #
#######################################################################

# Name of the first data.
combined_p1 = prefix+'_combined_p1'

# Split the data to continue with the calibrations
os.system('rm -rf '+combined_p1+'.*')
split(vis=combined_p0+'.ms',
      outputvis=combined_p1+'.ms',
      datacolumn='corrected')

# Clean for selfcalibration
tclean_wrapper(vis=combined_p1+'.ms', \
               imagename=combined_p1, \
               imsize=combined_imsize, \
               mask=mask_LB, \
               scales=combined_scales, \
               robust=robust, \
               threshold=str(2*rms_LB_p0)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(combined_p1+'.image', \
             disk_mask=mask_LB_main, noise_mask=res_mask_LB)
#AS205_combined_p1.image
#Beam 0.039 arcsec x 0.025 arcsec (-81.58 deg)
#Flux inside disk mask: 363.44 mJy
#Peak intensity of source: 5.71 mJy/beam
#rms: 1.96e-02 mJy/beam
#Peak SNR: 291.45

# RMS in mJy
rms_LB_p1 = imstat(imagename=combined_p1+'.image', \
                   region=res_mask_LB)['rms'][0]*10**3

# Phase self-calibration
os.system('rm -rf '+combined_p1+'.cal')
gaincal(vis=combined_p1+'.ms',
        caltable=combined_p1+'.cal',
        combine= 'spw, scan',
        gaintype='T',
        spw=combined_contspw,
        refant = combined_refant,
        solint='180s',
        calmode='p',
        minsnr=1.5,
        minblperant=4)

'''
4 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/22:38:30.4
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/22:40:30.1
2 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/22:42:27.0
4 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/22:50:45.5
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/22:54:42.1
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:01:19.9
2 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:03:00.5
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:06:57.1
3 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:15:14.0
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:17:13.2
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:19:10.6
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:21:10.7
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:25:48.2
3 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:27:28.4
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:29:28.3
4 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:31:24.9
2 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:32:37.8
'''

if not skip_plots:
    # Plot the first phase calibration
    plotcal(caltable=combined_p1+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB1_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_p1+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB2_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_p1+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB30_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_p1+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB31_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_p1+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB32_timerange,
            markersize=5, fontsize=10.0, showgui=True)

# Apply calibration
applycal(vis=combined_p1+'.ms', 
         spw=combined_contspw, 
         spwmap=combined_spwmap, 
         gaintable=[combined_p1+'.cal'], 
         interp='linearPD', calwt=True, applymode='calonly')


#######################################################################
#                      COMBINED PHASE SELF-CAL 2                      #
#######################################################################

# Name of the first data.
combined_p2 = prefix+'_combined_p2'

# Split the data to continue with the calibrations
os.system('rm -rf '+combined_p2+'.*')
split(vis=combined_p1+'.ms',
      outputvis=combined_p2+'.ms',
      datacolumn='corrected')

# Clean for selfcalibration
tclean_wrapper(vis=combined_p2+'.ms', \
               imagename=combined_p2, \
               imsize=combined_imsize, \
               mask=mask_LB, \
               scales=combined_scales, \
               robust=robust, \
               threshold=str(2*rms_LB_p1)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(combined_p2+'.image', \
             disk_mask=mask_LB_main, noise_mask=res_mask_LB)
#AS205_combined_p2.image
#Beam 0.039 arcsec x 0.025 arcsec (-81.58 deg)
#Flux inside disk mask: 358.54 mJy
#Peak intensity of source: 6.13 mJy/beam
#rms: 1.80e-02 mJy/beam
#Peak SNR: 341.17

# RMS in mJy
rms_LB_p2 = imstat(imagename=combined_p2+'.image', \
                   region=res_mask_LB)['rms'][0]*10**3

# Phase self-calibration
os.system('rm -rf '+combined_p2+'.cal')
gaincal(vis=combined_p2+'.ms',
        caltable=combined_p2+'.cal',
        combine= 'spw, scan',
        gaintype='T',
        spw=combined_contspw,
        refant = combined_refant,
        solint='60s',
        calmode='p',
        minsnr=1.5,
        minblperant=4)

'''
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/22:35:37.5
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/22:36:50.4
2 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/22:38:12.2
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/22:39:34.1
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/22:42:17.9
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/22:45:15.1
2 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/22:47:52.6
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/22:50:27.3
2 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/22:55:54.9
2 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:00:07.6
3 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:01:20.4
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:05:26.0
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:08:09.8
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:12:21.2
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:16:17.7
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:21:58.4
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:24:35.5
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:25:48.3
2 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:28:32.1
2 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:29:54.0
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:31:15.9
1 of 43 solutions flagged due to SNR < 1.5 in spw=16 at 2017/09/29/23:32:37.8
'''

if not skip_plots:
    # Plot the first phase calibration
    plotcal(caltable=combined_p2+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB1_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_p2+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB2_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_p2+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB30_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_p2+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB31_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_p2+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB32_timerange,
            markersize=5, fontsize=10.0, showgui=True)

# Apply calibration
applycal(vis=combined_p2+'.ms', 
         spw=combined_contspw, 
         spwmap=combined_spwmap, 
         gaintable=[combined_p2+'.cal'], 
         interp='linearPD', calwt=True, applymode='calonly')


#######################################################################
#                      COMBINED PHASE SELF-CAL 3                      #
#######################################################################

# Name of the first data.
combined_p3 = prefix+'_combined_p3'

# Split the data to continue with the calibrations
os.system('rm -rf '+combined_p3+'.*')
split(vis=combined_p2+'.ms',
      outputvis=combined_p3+'.ms',
      datacolumn='corrected')

# Clean for selfcalibration. We push it to 1.5rms level
tclean_wrapper(vis=combined_p3+'.ms', \
               imagename=combined_p3, \
               imsize=combined_imsize, \
               mask=mask_LB, \
               scales=combined_scales, \
               robust=robust, \
               threshold=str(1.5*rms_LB_p2)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(combined_p3+'.image', \
             disk_mask=mask_LB_main, noise_mask=res_mask_LB)
#AS205_combined_p3.image
#Beam 0.039 arcsec x 0.025 arcsec (-81.58 deg)
#Flux inside disk mask: 356.45 mJy
#Peak intensity of source: 6.45 mJy/beam
#rms: 1.78e-02 mJy/beam
#Peak SNR: 362.7

# RMS in mJy
rms_LB_p3 = imstat(imagename=combined_p3+'.image', \
                   region=res_mask_LB)['rms'][0]*10**3

# Phase self-calibration
os.system('rm -rf '+combined_p3+'.cal')
gaincal(vis=combined_p3+'.ms',
        caltable=combined_p3+'.cal',
        combine= 'spw, scan',
        gaintype='T',
        spw=combined_contspw,
        refant = combined_refant,
        solint='30s',
        calmode='p',
        minsnr=1.5,
        minblperant=4)

'''

'''

if not skip_plots:
    # Plot the first phase calibration
    plotcal(caltable=combined_p3+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB1_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_p3+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB2_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_p3+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB30_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_p3+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB31_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_p3+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, -180, 180], timerange=SB32_timerange,
            markersize=5, fontsize=10.0, showgui=True)

# Apply calibration
applycal(vis=combined_p3+'.ms', 
         spw=combined_contspw, 
         spwmap=combined_spwmap, 
         gaintable=[combined_p3+'.cal'], 
         interp='linearPD', calwt=True, applymode='calonly')


#######################################################################
#                       COMBINED AMP SELF-CAL 0                       #
#######################################################################

# Name of the first data.
combined_a0 = prefix+'_combined_a0'

# Split the data to continue with the calibrations
os.system('rm -rf '+combined_a0+'.*')
split(vis=combined_p3+'.ms',
      outputvis=combined_a0+'.ms',
      datacolumn='corrected')

# Clean for selfcalibration. we push to 1.5rms level.
tclean_wrapper(vis=combined_a0+'.ms', \
               imagename=combined_a0, \
               imsize=combined_imsize, \
               mask=mask_LB, \
               scales=combined_scales, \
               robust=robust, \
               threshold=str(1.5*rms_LB_p3)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(combined_a0+'.image', \
             disk_mask=mask_LB_main, noise_mask=res_mask_LB)
#AS205_combined_a0.image
#Beam 0.039 arcsec x 0.025 arcsec (-81.58 deg)
#Flux inside disk mask: 356.56 mJy
#Peak intensity of source: 6.61 mJy/beam
#rms: 1.78e-02 mJy/beam
#Peak SNR: 371.72

# RMS in mJy
rms_LB_a0 = imstat(imagename=combined_a0+'.image', \
                   region=res_mask_LB)['rms'][0]*10**3

'''
We proceed to amp calibration
'''

# First amp-calibration
os.system('rm -rf '+combined_a0+'.cal')
gaincal(vis=combined_a0+'.ms',
        caltable=combined_a0+'.cal',
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
7 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/22:48:01.7
4 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/22:54:51.2
1 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/22:58:16.0
7 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/23:01:38.6
6 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/23:08:28.0
3 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/23:22:10.5
2 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/23:31:56.7
'''

if not skip_plots:
    # Plot the first phase calibration
    plotcal(caltable=combined_a0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, 0, 0], timerange=SB1_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_a0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, 0, 0], timerange=SB2_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_a0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, 0, 0], timerange=SB30_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_a0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, 0, 0], timerange=SB31_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_a0+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, 0, 0], timerange=SB32_timerange,
            markersize=5, fontsize=10.0, showgui=True)

# Apply calibration
applycal(vis=combined_a0+'.ms', 
         spw=combined_contspw, 
         spwmap=combined_spwmap, 
         gaintable=[combined_a0+'.cal'], 
         interp='linearPD', calwt=True, applymode='calonly')


#######################################################################
#                       COMBINED AMP SELF-CAL 1                       #
#######################################################################

# Name of the first data.
combined_a1 = prefix+'_combined_a1'

# Split the data to continue with the calibrations
os.system('rm -rf '+combined_a1+'.*')
split(vis=combined_a0+'.ms',
      outputvis=combined_a1+'.ms',
      datacolumn='corrected')

# Clean for selfcalibration
tclean_wrapper(vis=combined_a1+'.ms', \
               imagename=combined_a1, \
               imsize=combined_imsize, \
               mask=mask_LB, \
               scales=combined_scales, \
               robust=robust, \
               threshold=str(1.5*rms_LB_a0)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(combined_a1+'.image', \
             disk_mask=mask_LB_main, noise_mask=res_mask_LB)
#AS205_combined_a1.image
#Beam 0.039 arcsec x 0.025 arcsec (-83.55 deg)
#Flux inside disk mask: 357.24 mJy
#Peak intensity of source: 6.32 mJy/beam
#rms: 1.64e-02 mJy/beam
#Peak SNR: 384.05

# RMS in mJy
rms_LB_a1 = imstat(imagename=combined_a1+'.image', \
                   region=res_mask_LB)['rms'][0]*10**3

'''
We proceed to amp calibration
'''

# First amp-calibration
os.system('rm -rf '+combined_a1+'.cal')
gaincal(vis=combined_a1+'.ms',
        caltable=combined_a1+'.cal',
        refant=combined_refant,
        combine='spw, scan', 
        solint='180',
        calmode='ap',
        gaintype='T',
        spw=combined_contspw,
        minsnr=3.0,
        minblperant=4, 
        solnorm=False)

'''
1 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/22:36:50.3
7 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/22:38:30.4
1 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/22:40:30.1
5 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/22:42:27.0
1 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/22:44:28.0
7 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/22:50:45.5
4 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/22:54:42.1
2 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/22:56:42.4
1 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/23:01:20.2
5 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/23:03:00.5
1 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/23:06:57.1
3 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/23:08:57.4
1 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/23:13:33.7
6 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/23:15:14.0
1 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/23:17:13.4
3 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/23:19:10.6
1 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/23:21:10.7
1 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/23:25:48.4
5 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/23:27:28.4
2 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/23:29:28.3
3 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/23:31:24.9
2 of 43 solutions flagged due to SNR < 3 in spw=16 at 2017/09/29/23:32:37.8
'''

if not skip_plots:
    # Plot the first phase calibration
    plotcal(caltable=combined_a1+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, 0, 0], timerange=SB1_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_a1+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, 0, 0], timerange=SB2_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_a1+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, 0, 0], timerange=SB30_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_a1+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, 0, 0], timerange=SB31_timerange,
            markersize=5, fontsize=10.0, showgui=True)
    plotcal(caltable=combined_a1+'.cal', \
            xaxis='time', yaxis='phase', subplot=221, iteration='antenna', \
            plotrange=[0, 0, 0, 0], timerange=SB32_timerange,
            markersize=5, fontsize=10.0, showgui=True)

# Apply calibration
applycal(vis=combined_a1+'.ms', 
         spw=combined_contspw, spwmap=combined_spwmap, 
         gaintable=[combined_a1+'.cal'], 
         interp='linearPD', calwt=True, applymode='calonly')


#######################################################################
#                         COMBINED FINAL IMAGE                        #
#######################################################################

im_robust = -0.5

# Name of the first data.
combined_ap = prefix+'_combined_ap'

# Split the data to continue with the calibrations
os.system('rm -rf '+combined_ap+'_'+str(im_robust)+'.*')
split(vis=combined_a1+'.ms',
      outputvis=combined_ap+'_'+str(im_robust)+'.ms',
      datacolumn='corrected')

# Clean for selfcalibration
tclean_wrapper(vis=combined_ap+'.ms', \
               imagename=combined_ap+'_'+str(im_robust), \
               imsize=combined_imsize, \
               mask=mask_LB, \
               scales=combined_scales, \
               robust=im_robust, \
               threshold=str(2*rms_LB_a1)+'mJy', \
               savemodel='modelcolumn', \
               interactive=False)

# Check the values from the clean
estimate_SNR(combined_ap+'_'+str(im_robust)+'.image', \
             disk_mask = mask_LB_main, \
             noise_mask = res_mask_LB)

# ROBUST 0.5
#AS205_combined_ap_0.5.image
#Beam 0.038 arcsec x 0.025 arcsec (-84.63 deg)
#Flux inside disk mask: 358.01 mJy
#Peak intensity of source: 6.15 mJy/beam
#rms: 1.61e-02 mJy/beam
#Peak SNR: 381.28

# ROBUST 0.0
#AS205_combined_ap_0.0.image
#Beam 0.031 arcsec x 0.019 arcsec (89.18 deg)
#Flux inside disk mask: 357.03 mJy
#Peak intensity of source: 4.45 mJy/beam
#rms: 1.93e-02 mJy/beam
#Peak SNR: 230.53

# ROBUST -0.5
#AS205_combined_ap_-0.5.image
#Beam 0.029 arcsec x 0.016 arcsec (84.51 deg)
#Flux inside disk mask: 356.11 mJy
#Peak intensity of source: 3.60 mJy/beam
#rms: 2.64e-02 mJy/beam
#Peak SNR: 136.41

exportfits(imagename=combined_ap+'_0.5.image', \
           fitsimage=prefix+'_combined_selfcal_ap.fits', \
           history=False, overwrite=True)
