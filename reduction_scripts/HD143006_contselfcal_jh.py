"""
This script was written for CASA 5.1.1

Datasets calibrated (in order of date observed):
SB1: 2015.1.00964.S/HD143006_a_06_TE 
     Observed 14 June 2016 (2 execution blocks)
     PI: K. Oberg
     As delivered to PI
SB2: 2015.1.00964.S/HD143006_a_06_TC 
     Observed 2 July 2016
     PI: K. Oberg
     Downloaded from archive and calibrated 
SB3: 2016.1.00484.L/WSB_52_a_06_TM1  
     Observed 14 May 2017, 17 May 2017, and 19 May 2017 (3 execution blocks)
     PI: S. Andrews
     As delivered to PI
LB1: 2016.1.00484.L/HD_143006_a_06_TM1 
     Observed 26 September 2017 and 26 November 2017 (2 execution blocks)
     PI: S. Andrews
     As delivered to PI

"""
import os

execfile('/pool/firebolt1/p484/reduction_scripts/reduction_utils.py')

skip_plots = True #if this is true, all of the plotting and inspection steps will be skipped and the script can be executed non-interactively in CASA if all relevant values have been hard-coded already 

#to fill this dictionary out, use listobs for the relevant measurement set 

prefix = 'HD143006' #string that identifies the source and is at the start of the name for all output files

#Note that if you are downloading data from the archive, your SPW numbering may differ from the SPWs in this script depending on how you split your data out!! 
data_params = {'SB1': {'vis' : '/data/astrochem1/jane/diskevol/uppersco/HD143006/data_1.3mm/HD143006_calibrated.ms',
                       'name' : 'SB1',
                       'field': 'HD143006',
                       'line_spws': np.array([0,9]), #SpwIDs of windows with lines that need to be flagged (this needs to be edited for each short baseline dataset)
                       'line_freqs': np.array([2.30538e11, 2.30538e11]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz)
                      },
               'SB2': {'vis' : '/data/astrochem1/jane/HD143006_TC.ms',
                       'name' : 'SB2',
                       'field': 'HD143006',
                       'line_spws': np.array([0]), 
                       'line_freqs': np.array([2.30538e11]), 
                      },
               'SB3': {'vis' : '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_Xbd4641_X1e/group.uid___A001_Xbd4641_X25/member.uid___A001_Xbd4641_X26/calibrated/calibrated_final.ms',
                       'name' : 'SB3',
                       'field': 'HD_143006',
                       'line_spws': np.array([0,4,8]), 
                       'line_freqs': np.array([2.30538e11, 2.30538e11, 2.30538e11]), 
                      }, 
               'LB1': {'vis' : '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_Xbd4641_X1a/group.uid___A001_Xbd4641_X1b/member.uid___A001_Xbd4641_X1c/calibrated/calibrated_final.ms',
                       'name' : 'LB1',
                       'field' : 'HD_143006',
                       'line_spws': np.array([3,7]), 
                       'line_freqs': np.array([2.30538e11, 2.30538e11]), 
                      }
               }

# need to initialize weight spectrum because earlier datasets have weight spectrum initialized 
initweights(vis = data_params['SB2']['vis'], wtmode = 'weight', dowtsp = True)
initweights(vis = data_params['LB1']['vis'], wtmode = 'weight', dowtsp = True)
#Amplitudes of channels 0 to 200 in SPW 0 of SB2 look problematic
flagmanager(vis = data_params['SB2']['vis'], mode = 'save', versionname = 'original_flags', comment = 'Original flag states') #save flag state before flagging spectral lines
flagdata(vis=data_params['SB2']['vis'], mode='manual', spw='0:0~200', flagbackup=False, field = data_params['SB2']['field']) #flag spectral lines 




if not skip_plots:
    """
    You can do this if you want to inspect amp vs. channel for every spectral window. This can be useful for deciding what you need to flag. 
    Alternatively, if the dataset was pipeline-calibrated, you can go to the "qa" folder in the data products package downloaded from the ALMA archive, 
    then go down a few directories until you see an "index.html" file. If you open that up in a browser, you'll see a "By Task" bar on the top. Click on that,
    go to the left bar, and click "17. hif_applycal". Here, you can find a lot of plots of the amplitude and phases of the calibrator data and the science target. 
    This can help you see whether any of the data are problematic.  
    """
    for i in data_params.keys():
        plotms(vis=data_params[i]['vis'], xaxis='channel', yaxis='amplitude', field=data_params[i]['field'], 
               ydatacolumn='data', avgtime='1e8', avgscan=True, avgbaseline=True, 
               iteraxis='spw')

#######
# Here you may wish to flag problematic data before we do spectral line flagging to form an averaged continuum. 
#
# If so, use something like 
# flagmanager(vis = msfile, mode = 'save', versionname = 'init_cal_flags', comment = 'Flag states immediately after initial calibration') 
# If you need to undo the flagging, use
# flagmanager(vis = msfile, mode = 'restore', versionname = 'init_cal_flags') #restore flagged spectral line channels 
########

SB1_flagchannels = get_flagchannels(data_params['SB1'], prefix, velocity_range = np.array([0, 15]))
avg_cont(data_params['SB1'], prefix, flagchannels = SB1_flagchannels, contspws = '0~2, 9~11', width_array = [960,960,256, 960,960,256])
#Averaged continuum dataset saved to HD143006_SB1_initcont.ms

SB2_flagchannels = get_flagchannels(data_params['SB2'], prefix, velocity_range = np.array([0, 15]))
avg_cont(data_params['SB2'], prefix, flagchannels = SB2_flagchannels, contspws = '0~2', width_array = [960,960,256])
#Averaged continuum dataset saved to IMLup_SB2_initcont.ms

for i in ['SB3', 'LB1']:      
    """
    Identify channels to flag based on the known velocity range of the line emission. The velocity range is based on line images from early reductions. If you are starting from scratch, 
    you can estimate the range from the plotms command above. You may wish to limit your uvrange to 0~300 or so to only view the baselines with the highest amplitudes.     
    """
    flagchannels_string = get_flagchannels(data_params[i], prefix, velocity_range = np.array([0, 15]))
    """
    Produces spectrally averaged continuum datasets
    If you only want to include a subset of the windows, you can manually pass in values for contspw and width_array, e.g.
    avg_cont(data_params[i], output_prefix, flagchannels = flagchannels_string, contspws = '0~2', width_array = [480,8,8]).
    If you don't pass in values, all of the SPWs will be split out and the widths will be computed automatically to enforce a maximum channel width of 125 MHz.
    WARNING: Only use the avg_cont function if the total bandwidth is recorded correctly in the original MS. There is sometimes a bug in CASA that records incorrect total bandwidths
    """
    # Flagchannels input string for SB3: '0:1915~1963, 4:1915~1963, 8:1915~1963'
    #Averaged continuum dataset saved to HD143006_SB3_initcont.ms
    # Flagchannels input string for LB1: '3:1905~1953, 7:1905~1953'
    #Averaged continuum dataset saved to HD143006_LB1_initcont.ms

    avg_cont(data_params[i], prefix, flagchannels = flagchannels_string)

# sample command to check that amplitude vs. uvdist looks normal
# plotms(vis=prefix+'_SB1_initcont.ms', xaxis='uvdist', yaxis='amp', coloraxis='spw', avgtime='30', avgchannel='16')

"""
Quick imaging of every execution block in the measurement set using tclean. 
The threshold, scales, and mask should be adjusted for each source.
In this case, we picked our threshold, scales, and mask from previous reductions of the data. You may wish to experiment with these values when imaging. 
The threshold is ~3-4x the rms, the mask is an ellipse that covers all the emission and has roughly the same geometry, and we choose 4 to 6 scales such that the first scale is 0 (a point), and the largest is ~half the major axis of the mask.
The mask angle and the semimajor and semiminor axes should be the same for all imaging. The center is not necessarily fixed because of potential misalignments between observations. 
"""

mask_radius = 1.3 #radius of mask in arcsec


SB1_mask = 'circle[[%s, %s], %.1farcsec]' % ('15h58m36.90s', '-22.57.15.63', mask_radius)

LB1_mask = 'circle[[%s, %s], %.1farcsec]' % ('15h58m36.90s', '-22.57.15.57', mask_radius)

SB_scales = [0, 5, 10, 20]
LB_scales = [0, 25, 50, 75, 100]
"""
In this section, we are imaging every execution block to check spatial alignment 
"""

if not skip_plots:
    #images are saved in the format prefix+'_name_initcont_exec#.ms'
    image_each_obs(data_params['SB1'], prefix, mask = SB1_mask, scales = SB_scales, threshold = '0.75mJy', interactive = False, robust = -2)

    tclean_wrapper(vis = prefix+'_SB2_initcont.ms', imagename = prefix+'_SB2_initcont', mask = SB1_mask, scales = SB_scales, threshold = '0.75mJy', interactive = False, robust = -2)

    image_each_obs(data_params['SB3'], prefix, mask = SB1_mask, scales = SB_scales, threshold = '0.4mJy', interactive =False, robust = -2)
    # inspection of images do not reveal additional bright background sources 

    image_each_obs(data_params['LB1'], prefix, mask = LB1_mask, scales = LB_scales, threshold = '0.06mJy', interactive = False)

    """
    Since the source looks axisymmetric, we will fit a Gaussian to the disk to estimate the location of the peak in each image and record the output.
    We are also very roughly estimating the PA and inclination for checking the flux scale offsets later (these are NOT the position angles and inclinations used for analysis of the final image products.
    Here, we are using the CLEAN mask to restrict the region over which the fit is occurring, but you may wish to shrink the region even further if your disk structure is complex 


    fit_gaussian(prefix+'_SB1_initcont_exec0.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 15h46m44.710036s -34d30m36.08839s

    fit_gaussian(prefix+'_SB1_initcont_exec1.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 15h46m44.708978s -34d30m36.12469s

    fit_gaussian(prefix+'_LB1_initcont_exec0.image', region = 'circle[[%s, %s], %.1farcsec]' % ('15h46m44.71s', '-34.30.36.09', 0.2)) #shrinking the fit region because of the noisiness of the image
    #Peak of Gaussian component identified with imfit: ICRS 15h46m44.710940s -34d30m36.08832s
    """
    fit_gaussian(prefix+'_LB1_initcont_exec1.image', region = 'circle[[%s, %s], %.1farcsec]' % ('15h58m36.90s', '-22.57.15.57', 0.1))
    #Peak of Gaussian component identified with imfit: ICRS 15h58m36.898560s -22d57m15.59690s
    #Peak in J2000 coordinates: 15:58:36.89923, -022:57:15.582620
    #Pixel coordinates of peak: x = 1502.034 y = 1506.704
    #PA of Gaussian component: 173.15 deg
    #Inclination of Gaussian component: 41.88 deg

    


"""
Reassigning to a common phase center (chose center of LB1, exec1, but this is fairly arbitrary)
"""

split_all_obs(prefix+'_SB1_initcont.ms', prefix+'_SB1_initcont_exec')
split_all_obs(prefix+'_SB2_initcont.ms', prefix+'_SB2_initcont_exec')
split_all_obs(prefix+'_SB3_initcont.ms', prefix+'_SB3_initcont_exec')
split_all_obs(prefix+'_LB1_initcont.ms', prefix+'_LB1_initcont_exec')
#Saving observation 0 of HD143006_SB1_initcont.ms to HD143006_SB1_initcont_exec0.ms
#Saving observation 1 of HD143006_SB1_initcont.ms to HD143006_SB1_initcont_exec1.ms
#Saving observation 0 of HD143006_SB2_initcont.ms to HD143006_SB1_initcont_exec0.ms
#Saving observation 0 of HD143006_SB3_initcont.ms to HD143006_SB1_initcont_exec0.ms
#Saving observation 1 of HD143006_SB3_initcont.ms to HD143006_SB1_initcont_exec1.ms
#Saving observation 2 of HD143006_SB3_initcont.ms to HD143006_SB1_initcont_exec2.ms
#Saving observation 0 of HD143006_LB1_initcont.ms to HD143006_LB1_initcont_exec0.ms
#Saving observation 1 of HD143006_LB1_initcont.ms to HD143006_LB1_initcont_exec1.ms



common_dir = 'J2000 15h58m36.89923s -022.57.15.58262' #choose peak of second execution of LB1 to be the common direction (the better-quality of the high-res observations)   

#need to change to J2000 coordinates
mask_ra = '15h58m36.89923s'
mask_dec = '-22.57.15.58262'
common_mask = 'circle[[%s, %s], %.1farcsec]' % (mask_ra, mask_dec, mask_radius)

"""
shiftname = prefix+'_SB1_initcont_exec0_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_SB1_initcont_exec0.ms', outputvis=shiftname+'.ms', field = data_params['SB1']['field'], phasecenter='ICRS 15h46m44.710036s -34d30m36.08839s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['SB1']['field'], direction = common_dir) #fixplanets works only with J2000, not ICRS
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = SB_scales, threshold = '0.25mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 15h46m44.709386s -34d30m36.07571s

shiftname = prefix+'_SB1_initcont_exec1_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_SB1_initcont_exec1.ms', outputvis=shiftname+'.ms', field = data_params['SB1']['field'], phasecenter='ICRS 15h46m44.708978s -34d30m36.12469s')      
fixplanets(vis = shiftname+'.ms', field = data_params['SB1']['field'], direction = common_dir)
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = SB_scales, threshold = '0.25mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 15h46m44.709384s -34d30m36.07577s

shiftname = prefix+'_LB1_initcont_exec0_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_LB1_initcont_exec0.ms', outputvis=shiftname+'.ms', field = data_params['LB1']['field'], phasecenter='ICRS 15h46m44.710940s -34d30m36.08832s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['LB1']['field'], direction = common_dir)
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = LB_scales, threshold = '0.09mJy')
fit_gaussian(shiftname+'.image', region =  'circle[[%s, %s], %.1farcsec]' % ('15h46m44.709s', '-34.30.36.076', 0.2))
#Peak of Gaussian component identified with imfit: J2000 15h46m44.709428s -34d30m36.07547s


shiftname = prefix+'_LB1_initcont_exec1_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_LB1_initcont_exec1.ms', outputvis=shiftname+'.ms', field = data_params['LB1']['field'], phasecenter='ICRS 15h46m44.708871s -34d30m36.09063s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['LB1']['field'], direction = common_dir)
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = LB_scales, threshold = '0.06mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 15h46m44.709382s -34d30m36.07596s
"""

"""
After aligning the images, we want to check if the flux scales seem consistent between execution blocks (within ~5%)
First, we check the uid___xxxxx.casa_commands.log in the log directory of the data products folder (or the calibration script in the manual case) to check whether the calibrator catalog matches up with the input flux density values for the calibrators
(You should also check the plots of the calibrators in the data products to make sure that the amplitudes look consistent with the models that were inserted)
"""


"""
Pipeline flux models
    SB1, both executions: J1517-2422 = 2.4808 
    SB2 was calibrated with Titan
    SB3, EB0: J1517-2422 = 1.944 Jy at 232.610 GHz
    SB3, EB1: J1733-1304 = 1.610 Jy at 232.609 GHz
    SB3, EB2: J1517-2422 = 2.108 Jy at 232.609 GHz
    LB1, EB0: J1733-1304 = 1.8864 Jy at 232.584GHz
    LB1, EB1: J1427-4206 = 2.5771 Jy at 232.605GHz
"""


au.getALMAFlux('J1517-2422', frequency = '230.530GHz', date = '2016/06/14')
au.getALMAFlux('J1517-2422', frequency = '232.610GHz', date = '2017/05/14')	# SB1, EB0
au.getALMAFlux('J1733-1304', frequency = '232.609GHz', date = '2017/05/17')     # SB1, EB1
au.getALMAFlux('J1517-2422', frequency = '232.609GHz', date = '2017/05/19')     # SB1, EB2
au.getALMAFlux('J1733-1304', frequency = '232.584GHz', date = '2017/09/26')     #LB1, EB0
au.getALMAFlux('J1427-4206', frequency = '232.584GHz', date = '2017/11/26')     #LB1, EB1


"""
SB1 (both executions)
Closest Band 3 measurement: 2.910 +- 0.110 (age=-2 days) 103.5 GHz
Closest Band 3 measurement: 2.790 +- 0.100 (age=-2 days) 91.5 GHz
Closest Band 7 measurement: 2.190 +- 0.130 (age=+5 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -5 days from 2016/06/14, with age separation of 0 days
  2016/06/19: freqs=[103.49, 91.46, 337.46], fluxes=[2.95, 2.84, 2.09]
/data/astrochem1/jane/casa-release-5.1.1-5.el6/lib/python2.7/site-packages/matplotlib/collections.py:446: FutureWarning: elementwise comparison failed; returning scalar instead, but in the future will perform elementwise comparison
  if self._edgecolors == 'face':
Median Monte-Carlo result for 230.530000 = 2.356563 +- 0.195613 (scaled MAD = 0.193102)
Result using spectral index of -0.225942 for 230.530 GHz from 2.910 Jy at 103.490 GHz = 2.428309 +- 0.195613 Jy


SB3, EB0:
Closest Band 3 measurement: 2.420 +- 0.060 (age=+0 days) 91.5 GHz
Closest Band 7 measurement: 1.840 +- 0.090 (age=-1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -1 days from 2017/05/14, with age separation of 0 days
  2017/05/15: freqs=[103.49, 91.46, 343.48], fluxes=[2.55, 2.49, 1.84]
Median Monte-Carlo result for 232.610000 = 2.043380 +- 0.159244 (scaled MAD = 0.157684)
Result using spectral index of -0.234794 for 232.610 GHz from 2.420 Jy at 91.460 GHz = 1.943706 +- 0.159244 Jy

SB3, EB1:
Closest Band 3 measurement: 3.020 +- 0.060 (age=+0 days) 103.5 GHz
Closest Band 7 measurement: 1.190 +- 0.060 (age=+0 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 0 days from 2017/05/17, with age separation of 0 days
  2017/05/17: freqs=[103.49, 343.48], fluxes=[3.02, 1.19]
Median Monte-Carlo result for 232.609000 = 1.610663 +- 0.129086 (scaled MAD = 0.126920)
Result using spectral index of -0.776310 for 232.609 GHz from 3.020 Jy at 103.490 GHz = 1.610486 +- 0.129086 Jy

SB3, EB2:
Closest Band 3 measurement: 2.550 +- 0.060 (age=+4 days) 103.5 GHz
Closest Band 3 measurement: 2.490 +- 0.050 (age=+4 days) 91.5 GHz
Closest Band 7 measurement: 1.750 +- 0.060 (age=+2 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 4 days from 2017/05/19, with age separation of 0 days
  2017/05/15: freqs=[103.49, 91.46, 343.48], fluxes=[2.55, 2.49, 1.84]
Median Monte-Carlo result for 232.609000 = 2.040585 +- 0.161160 (scaled MAD = 0.157430)
Result using spectral index of -0.234794 for 232.609 GHz from 2.520 Jy at 97.475 GHz = 2.054524 +- 0.161160 Jy

LB1, EB0
Closest Band 3 measurement: 3.070 +- 0.080 (age=-6 days) 103.5 GHz
Closest Band 3 measurement: 3.250 +- 0.090 (age=-6 days) 91.5 GHz
Closest Band 7 measurement: 1.290 +- 0.050 (age=+3 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -6 days from 2017/09/26, with age separation of 0 days
  2017/10/02: freqs=[103.49, 91.46, 343.48], fluxes=[3.07, 3.25, 1.49]
Median Monte-Carlo result for 232.584000 = 1.886107 +- 0.162175 (scaled MAD = 0.161563)
Result using spectral index of -0.593201 for 232.584 GHz from 3.070 Jy at 103.490 GHz = 1.898980 +- 0.162175 Jy
  Out[156]: 
{'ageDifference': 9.0,
 'fluxDensity': 1.898980410812134,
 'fluxDensityUncertainty': 0.16217529776215703,
 'meanAge': -6.0,
 'monteCarloFluxDensity': 1.8861065974358149,
 'spectralIndex': -0.5932012954549899,
 'spectralIndexAgeOldest': -6,
 'spectralIndexAgeSeparation': 0,
 'spectralIndexAgeYoungest': -6,
 'spectralIndexNPairs': 1,
 'spectralIndexUncertainty': 0.033328174157397271}

LB1, EB1
au.getALMAFlux('J1427-4206', date = '2017/11/26', frequency = '232.584GHz')
Closest Band 3 measurement: 4.430 +- 0.080 (age=+1 days) 91.5 GHz
Closest Band 7 measurement: 2.060 +- 0.070 (age=+3 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 3 days from 2017/11/26, with age separation of 0 days
  2017/11/23: freqs=[91.46, 343.48], fluxes=[4.44, 2.06]
Median Monte-Carlo result for 232.584000 = 2.585165 +- 0.149040 (scaled MAD = 0.149264)
Result using spectral index of -0.580360 for 232.584 GHz from 4.430 Jy at 91.460 GHz = 2.577244 +- 0.149040 Jy
  Out[157]: 
{'ageDifference': 2.0,
 'fluxDensity': 2.5772438170147502,
 'fluxDensityUncertainty': 0.14904034347703818,
 'meanAge': 1.0,
 'monteCarloFluxDensity': 2.5851648253966402,
 'spectralIndex': -0.58036020757522699,
 'spectralIndexAgeOldest': 3,
 'spectralIndexAgeSeparation': 0,
 'spectralIndexAgeYoungest': 3,
 'spectralIndexNPairs': 1,
 'spectralIndexUncertainty': 0.039958971258299378}
"""

"""
Here we export averaged visibilities to npz files and then plot the deprojected visibilities to compare the amplitude scales
"""

#HD143006 is asymmetric, but comparing the radially averaged profiles will still provide an indication of the flux scale offsets 
PA = 0 
incl = 0

if not skip_plots:
    for msfile in [prefix+'_SB1_initcont_exec0.ms', prefix+'_SB1_initcont_exec1.ms', prefix+'_SB2_initcont_exec0.ms', prefix+'_SB3_initcont_exec0.ms', prefix+'_SB3_initcont_exec1.ms',prefix+'_SB3_initcont_exec2.ms', prefix+'_LB1_initcont_exec0.ms', prefix+'_LB1_initcont_exec1.ms']:
        export_MS(msfile)
    #plot deprojected visibility profiles of all the execution blocks


    plot_deprojected([prefix+'_SB1_initcont_exec0.vis.npz', prefix+'_SB1_initcont_exec1.vis.npz', prefix+'_SB2_initcont_exec0.vis.npz', prefix+'_SB3_initcont_exec0.vis.npz', 
         prefix+'_SB3_initcont_exec1.vis.npz', prefix+'_SB3_initcont_exec2.vis.npz'], PA = PA, incl = incl)

    #there seems to be small amounts of scatter between the different observations. We don't know which one is "correct," but we want the fluxes to be consistent, so we rescale to the observation that is roughly in the middle (SB3, EB1)

    estimate_flux_scale(reference = prefix+'_SB3_initcont_exec1.vis.npz', comparison = prefix+'_SB1_initcont_exec0.vis.npz', incl = incl, PA = PA)
    #The ratio of the fluxes of HD143006_SB1_initcont_exec0.vis.npz to HD143006_SB3_initcont_exec1.vis.npz is 1.01850
    #The scaling factor for gencal is 1.009 for your comparison measurement
    #The error on the weighted mean ratio is 1.892e-03, although it's likely that the weights in the measurement sets are too off by some constant factor


    estimate_flux_scale(reference = prefix+'_SB3_initcont_exec1.vis.npz', comparison = prefix+'_SB1_initcont_exec1.vis.npz', incl = incl, PA = PA)
    #The ratio of the fluxes of HD143006_SB1_initcont_exec1.vis.npz to HD143006_SB3_initcont_exec1.vis.npz is 0.95363
    #The scaling factor for gencal is 0.977 for your comparison measurement
    #The error on the weighted mean ratio is 1.778e-03, although it's likely that the weights in the measurement sets are too off by some constant factor


    estimate_flux_scale(reference = prefix+'_SB3_initcont_exec1.vis.npz', comparison = prefix+'_SB2_initcont_exec0.vis.npz', incl = incl, PA = PA)
    #The ratio of the fluxes of HD143006_SB2_initcont_exec0.vis.npz to HD143006_SB3_initcont_exec1.vis.npz is 0.90750
    #The scaling factor for gencal is 0.953 for your comparison measurement
    #The error on the weighted mean ratio is 1.594e-03, although it's likely that the weights in the measurement sets are too off by some constant factor

    estimate_flux_scale(reference = prefix+'_SB3_initcont_exec1.vis.npz', comparison = prefix+'_SB3_initcont_exec0.vis.npz', incl = incl, PA = PA)
    #The ratio of the fluxes of HD143006_SB3_initcont_exec0.vis.npz to HD143006_SB3_initcont_exec1.vis.npz is 0.91948
    #The scaling factor for gencal is 0.959 for your comparison measurement
    #The error on the weighted mean ratio is 1.743e-03, although it's likely that the weights in the measurement sets are off by some constant factor

    estimate_flux_scale(reference = prefix+'_SB3_initcont_exec1.vis.npz', comparison = prefix+'_SB3_initcont_exec2.vis.npz', incl = incl, PA = PA)

    #The ratio of the fluxes of HD143006_SB3_initcont_exec2.vis.npz to HD143006_SB3_initcont_exec1.vis.npz is 1.06962
    #The scaling factor for gencal is 1.034 for your comparison measurement
    #The error on the weighted mean ratio is 1.757e-03, although it's likely that the weights in the measurement sets are off by some constant factor

    estimate_flux_scale(reference = prefix+'_SB3_initcont_exec1.vis.npz', comparison = prefix+'_LB1_initcont_exec0.vis.npz', incl = incl, PA = PA)
    #looks like the offset is due to phase de-correlation rather than a fluxcal issue 

    estimate_flux_scale(reference = prefix+'_SB3_initcont_exec1.vis.npz', comparison = prefix+'_LB1_initcont_exec1.vis.npz', incl = incl, PA = PA)
    #The ratio of the fluxes of HD143006_LB1_initcont_exec1.vis.npz to HD143006_SB3_initcont_exec1.vis.npz is 0.86208
    #The scaling factor for gencal is 0.928 for your comparison measurement
    #The error on the weighted mean ratio is 2.021e-03, although it's likely that the weights in the measurement sets are off by some constant factor

    plot_deprojected([prefix+'_SB2_initcont_exec0.vis.npz', prefix+'_SB3_initcont_exec1.vis.npz'], PA = PA, incl = incl, fluxscale = [1/0.89,1])


    #We replot the deprojected visibilities with rescaled factors to check that the values make sense
    plot_deprojected([prefix+'_SB1_initcont_exec0.vis.npz', prefix+'_SB1_initcont_exec1.vis.npz', prefix+'_SB2_initcont_exec0.vis.npz', prefix+'_SB3_initcont_exec0.vis.npz', 
         prefix+'_SB3_initcont_exec1.vis.npz', prefix+'_SB3_initcont_exec2.vis.npz', prefix+'_LB1_initcont_exec0.vis.npz',prefix+'_LB1_initcont_exec1.vis.npz'], 
         PA = PA, incl = incl, fluxscale = [1, 1/0.94, 1/0.89, 1/0.92, 1, 1/1.07, 1, 1/0.86])

#flux offsets for SB1 and SB2 from SB3 are within what one would expect based on the slight frequency difference
#now correct the flux of the discrepant datasets
rescale_flux(prefix+'_SB3_initcont_exec0.ms', [0.959])
#Splitting out rescaled values into new MS: HD143006_SB3_initcont_exec0_rescaled.ms
rescale_flux(prefix+'_SB3_initcont_exec2.ms', [1.034])
#Splitting out rescaled values into new MS: HD143006_SB3_initcont_exec2_rescaled.ms
rescale_flux(prefix+'_LB1_initcont_exec1.ms', [0.928])


"""
Start of self-calibration of the short-baseline data 
"""
#merge the short-baseline execution blocks into a single MS
SB_cont_p0 = prefix+'_SB_contp0'
os.system('rm -rf %s*' % SB_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [prefix+'_SB1_initcont_exec0.ms', prefix+'_SB1_initcont_exec1.ms', prefix+'_SB2_initcont_exec0.ms',  prefix+'_SB3_initcont_exec0_rescaled.ms',  prefix+'_SB3_initcont_exec1.ms',  prefix+'_SB3_initcont_exec2_rescaled.ms'], concatvis = SB_cont_p0+'.ms', dirtol = '0.1arcsec', copypointing = False) 

#make initial image
tclean_wrapper(vis = SB_cont_p0+'.ms', imagename = SB_cont_p0, mask = common_mask, scales = SB_scales, threshold = '0.1mJy', savemodel = 'modelcolumn')

noise_annulus ="annulus[[%s, %s],['%.2farcsec', '4.25arcsec']]" % (mask_ra, mask_dec, 1.1*mask_radius) #annulus over which we measure the noise. The inner radius is slightly larger than the semimajor axis of the mask (to add some buffer space around the mask) and the outer radius is set so that the annulus fits inside the long-baseline image size 
estimate_SNR(SB_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_SB_contp0.image
#Beam 0.289 arcsec x 0.245 arcsec (-89.21 deg)
#Flux inside disk mask: 60.39 mJy
#Peak intensity of source: 7.76 mJy/beam
#rms: 4.15e-02 mJy/beam
#Peak SNR: 186.97


"""
We need to select one or more reference antennae for gaincal

We first look at the CASA command log (or manual calibration script) to see how the reference antennae choices were ranked (weighted toward antennae close to the center of the array and with good SNR)
Note that gaincal will sometimes choose a different reference antenna than the one specified if it deems another one to be a better choice 

SB1: DA41,DA49,DV16,DA61,DV19
SB2: DV16
SB3, EB0: DV15, DV18, DA46, DA51, DV23
SB3, EB1: DA59, DA49, DA41, DA46, DA51
SB3, EB2: DA59, DA46, DA49, DA41, DA51
LB1, EB0: DA61,DA47,DV24,DA57,DV09
LB1, EB1: DV20,DV08,DV04,DV06,DA63

If you want to double check whether the antenna locations are reasonable, you can use something like plotants(vis = SB_cont_p0+'.ms')

"""

get_station_numbers(SB_cont_p0+'.ms', 'DV16')
#Observation ID 0: DV16@A036
#Observation ID 1: DV16@A036
#Observation ID 2: DV16@A036
#Observation ID 3: DV16@A103
#Observation ID 4: DV16@A103
#Observation ID 5: DV16@A103
get_station_numbers(SB_cont_p0+'.ms', 'DA49')
#Observation ID 0: DA49@A002
#Observation ID 1: DA49@A002
#Observation ID 2: DA49@A002
#Observation ID 4: DA49@A002
#Observation ID 5: DA49@A002
get_station_numbers(SB_cont_p0+'.ms', 'DA46')
#Observation ID 2: DA46@A034
#Observation ID 3: DA46@A034
#Observation ID 4: DA46@A034
#Observation ID 5: DA46@A034
get_station_numbers(SB_cont_p0+'.ms', 'DV15')
#Observation ID 0: DV15@A048
#Observation ID 1: DV15@A048
#Observation ID 2: DV15@A048
#Observation ID 3: DV15@A006
#Observation ID 5: DV15@A006
get_station_numbers(SB_cont_p0+'.ms', 'DV18')
#Observation ID 1: DV18@A009
#Observation ID 2: DV18@A009
#Observation ID 3: DV18@A009
#Observation ID 4: DV18@A009
#Observation ID 5: DV18@A009





SB_contspws = '0~20' #change as appropriate
SB_refant = 'DV16@A036, DV18@A009, DA46@A034' 
SB1_timerange = '2016/06/13~2016/06/15'
SB2_timerange = '2016/07/01/00~2016/07/03/00'
SB3_obs0_timerange = '2017/05/13/00~2017/05/15/00'
SB3_obs1_timerange = '2017/05/15/00~2017/05/18/00'
SB3_obs2_timerange = '2017/05/18/00~2017/05/20/00'
 

# It's useful to check that the phases for the refant look good in all execution blocks in plotms. However, plotms has a tendency to crash in CASA 5.1.1, so it might be necessary to use plotms in an older version of CASA 
#plotms(vis=SB_cont_p0, xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '0')
#plotms(vis=SB_cont_p0, xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '1')

#first round of phase self-cal for short baseline data
SB_p1 = prefix+'_SB.p1'
os.system('rm -rf '+SB_p1)
gaincal(vis=SB_cont_p0+'.ms' , caltable=SB_p1, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='p', solint='120s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [120s, 60s, 30s, 18s, 6s]

if not skip_plots:
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_timerange) 
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB2_timerange)  
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB3_obs0_timerange)
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB3_obs1_timerange)
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB3_obs2_timerange)

applycal(vis=SB_cont_p0+'.ms', spw=SB_contspws, gaintable=[SB_p1], interp = 'linearPD', calwt = True)

SB_cont_p1 = prefix+'_SB_contp1'
os.system('rm -rf %s*' % SB_cont_p1)
split(vis=SB_cont_p0+'.ms', outputvis=SB_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p1+'.ms' , imagename = SB_cont_p1, mask = common_mask, scales = SB_scales, threshold = '0.07mJy', interactive = False, savemodel = 'modelcolumn')
estimate_SNR(SB_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_SB_contp1.image
#Beam 0.289 arcsec x 0.245 arcsec (-89.09 deg)
#Flux inside disk mask: 61.57 mJy
#Peak intensity of source: 8.55 mJy/beam
#rms: 2.51e-02 mJy/beam
#Peak SNR: 341.31

#now we concatenate all the data together

combined_cont_p0 = prefix+'_combined_contp0'
os.system('rm -rf %s*' % combined_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [SB_cont_p1+'.ms', prefix+'_LB1_initcont_exec0.ms', prefix+'_LB1_initcont_exec1_rescaled.ms'], concatvis = combined_cont_p0+'.ms' , dirtol = '0.1arcsec', copypointing = False) 

tclean_wrapper(vis = combined_cont_p0+'.ms' , imagename = combined_cont_p0, mask = common_mask, scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_combined_contp0.image
#Beam 0.054 arcsec x 0.039 arcsec (87.44 deg)
#Flux inside disk mask: 64.87 mJy
#Peak intensity of source: 0.70 mJy/beam
#rms: 1.50e-02 mJy/beam
#Peak SNR: 46.75

get_station_numbers(combined_cont_p0+'.ms', 'DA61')
#Observation ID 0: DA61@A006
#Observation ID 1: DA61@A006
#Observation ID 2: DA61@A006
#Observation ID 3: DA61@A015
#Observation ID 4: DA61@A015
#Observation ID 5: DA61@A015
#Observation ID 6: DA61@A015
#Observation ID 7: DA61@A089

get_station_numbers(combined_cont_p0+'.ms', 'DV20')
#Observation ID 2: DV20@A013
#Observation ID 3: DV20@A093
#Observation ID 5: DV20@A093
#Observation ID 6: DV20@A093
#Observation ID 7: DV20@A072


combined_refant = 'DV16@A036, DV18@A009, DA46@A034, DA61@A015, DV20@A072'
combined_contspws = '0~28'
combined_spwmap =  [0,0,0,3,3,3,6,6,6,9,9,9,9,13,13,13,13,17,17,17,17,21,21,21,21,25,25,25,25] #note that the tables produced by gaincal in 5.1.1 have spectral windows numbered differently if you use the combine = 'spw' option. Previously, all of the solutions would be written to spectral window 0. Now, they are written to the first window in each execution block. So, the spwmap argument has to correspond to the first window in each execution block you want to calibrate. 

LB1_obs0_timerange = '2017/09/26/00:00:01~2017/09/26/23:59:59'
LB2_obs0_timerange = '2017/11/26/00:00:01~2017/11/26/23:59:59'

#first round of phase self-cal for long baseline data
combined_p1 = prefix+'_combined.p1'
os.system('rm -rf '+combined_p1)
gaincal(vis=combined_cont_p0+'.ms' , caltable=combined_p1, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='360s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [900s, 360s, 180s, 60s, 30s, 6s]

if not skip_plots:
    plotcal(caltable=combined_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 
    plotcal(caltable=combined_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB2_obs0_timerange)

applycal(vis=combined_cont_p0+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p1], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p1 = prefix+'_combined_contp1'
os.system('rm -rf %s*' % combined_cont_p1)
split(vis=combined_cont_p0+'.ms', outputvis=combined_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p1+'.ms' , imagename = combined_cont_p1, mask = common_mask, scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_combined_contp1.image
#Beam 0.053 arcsec x 0.038 arcsec (86.81 deg)
#Flux inside disk mask: 64.68 mJy
#Peak intensity of source: 0.67 mJy/beam
#rms: 1.41e-02 mJy/beam
#Peak SNR: 47.36


#second round of phase self-cal for long baseline data
combined_p2 = prefix+'_combined.p2'
os.system('rm -rf '+combined_p2)
gaincal(vis=combined_cont_p1+'.ms' , caltable=combined_p2, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='180s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 
    plotcal(caltable=combined_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs1_timerange)

applycal(vis=combined_cont_p1+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p2], interp = 'linearPD', calwt = True, applymode = 'calonly')


combined_cont_p2 = prefix+'_combined_contp2'
os.system('rm -rf %s*' % combined_cont_p2)
split(vis=combined_cont_p1+'.ms', outputvis=combined_cont_p2+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p2+'.ms' , imagename = combined_cont_p2, mask = common_mask, scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_combined_contp2.image
#Beam 0.053 arcsec x 0.038 arcsec (86.81 deg)
#Flux inside disk mask: 64.26 mJy
#Peak intensity of source: 0.71 mJy/beam
#rms: 1.40e-02 mJy/beam
#Peak SNR: 50.46


#third round of phase self-cal for long-baseline data 
combined_p3 = prefix+'_combined.p3'
os.system('rm -rf '+combined_p3)
gaincal(vis=combined_cont_p2+'.ms' , caltable=combined_p3, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='60s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 
    plotcal(caltable=combined_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs1_timerange)

applycal(vis=combined_cont_p2+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p3], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p3 = prefix+'_combined_contp3'
os.system('rm -rf %s*' % combined_cont_p3)
split(vis=combined_cont_p2+'.ms', outputvis=combined_cont_p3+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p3+'.ms' , imagename = combined_cont_p3, mask = common_mask, scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p3+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_combined_contp3.image
#Beam 0.053 arcsec x 0.038 arcsec (86.81 deg)
#Flux inside disk mask: 63.92 mJy
#Peak intensity of source: 0.76 mJy/beam
#rms: 1.39e-02 mJy/beam
#Peak SNR: 54.73



#fourth round of phase self-cal for long-baseline data 
combined_p4 = prefix+'_combined.p4'
os.system('rm -rf '+combined_p4)
gaincal(vis=combined_cont_p3+'.ms' , caltable=combined_p4, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='30s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p4, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 
    plotcal(caltable=combined_p4, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs1_timerange)

applycal(vis=combined_cont_p3+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p4], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p4 = prefix+'_combined_contp4'
os.system('rm -rf %s*' % combined_cont_p4)
split(vis=combined_cont_p3+'.ms', outputvis=combined_cont_p4+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p4+'.ms' , imagename = combined_cont_p4, mask =common_mask, scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p4+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_combined_contp4.image
#Beam 0.053 arcsec x 0.038 arcsec (86.81 deg)
#Flux inside disk mask: 63.42 mJy
#Peak intensity of source: 0.80 mJy/beam
#rms: 1.40e-02 mJy/beam
#Peak SNR: 56.91



#additional phase self-cal and amp self-cal appears to make things worse 
#uncomment the lines below if you wish to perform amp self-cal for your source specifically
"""

combined_ap = prefix+'_combined.ap'
os.system('rm -rf '+combined_ap)
gaincal(vis=combined_cont_p4+'.ms' , caltable=combined_ap, gaintype='T', combine = 'spw,scan', spw=combined_contspws, refant=combined_refant, calmode='ap', solint='900s', minsnr=3.0, minblperant=4, solnorm = True)

if not skip_plots:
    plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 
    plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = LB1_obs1_timerange)

applycal(vis=combined_cont_p4+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_ap], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_ap = prefix+'_combined_contap'
os.system('rm -rf %s*' % combined_cont_ap)
split(vis=combined_cont_p4+'.ms', outputvis=combined_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_ap+'.ms' , imagename = combined_cont_ap, mask =common_mask, scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
"""

split_all_obs(combined_cont_p4+'.ms', combined_cont_p4+'_exec')

plot_deprojected(['HD143006_combined_contp4_exec6.vis.npz', 'HD143006_LB1_initcont_exec0.vis.npz', 'HD143006_SB3_initcont_exec1.vis.npz'], PA = PA, incl = incl)

estimate_flux_scale(reference = prefix+'_SB3_initcont_exec1.vis.npz', comparison = 'HD143006_combined_contp4_exec6.vis.npz', incl = incl, PA = PA)


export_MS(combined_cont_p4+'_exec6.ms')
