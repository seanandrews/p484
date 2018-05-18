"""
This script was written for CASA 5.1.1
Datasets calibrated (in order of date observed):
SB1: 2013.1.00366.S/
     Observed 04/June/2014 29/June/2014
     PI: M. Hughes
     this script uses pre-selfcalibrated SB1 data 
SB2: 2013.1.00601.S/
     Observed 05/AUg/2015 09/Aug/2015
     PI: A. Isella
     this script uses pre-selfcalibrated SB2 data
LB1: 2016.1.00484.L/
     Observed 08/Sep/2017 09/Sep/2017
     PI: S. Andrews
     As delivered to PI
"""
import os

execfile('/home/shared/ALMA_data/p484_large/reduction_utils.py')

skip_plots = False #if this is true, all of the plotting and inspection steps will be skipped and the script can be executed non-interactively in CASA if all relevant values have been hard-coded already 

#to fill this dictionary out, use listobs for the relevant measurement set 

prefix = 'HD163296' #string that identifies the source and is at the start of the name for all output files

#Note that if you are downloading data from the archive, your SPW numbering may differ from the SPWs in this script depending on how you split your data out!! 
data_params = {'SB1': {'vis' : '/home/shared/ALMA_data/p484_large/HD163296/short_baseline_msfile_from_Jane/HD_163296_SB1_contfinal.ms',
                       'name' : 'SB1',
                       'field': 'HD_163296',
                       'line_spws': '', #SpwIDs of windows with lines that need to be flagged (this needs to be edited for each short baseline dataset)
                       'line_freqs': '', #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz)
                      }, #information about the short baseline measurement sets (SB1, SB2, SB3, etc in chronological order)
               'SB2': {'vis' : '/home/shared/ALMA_data/p484_large/HD163296/short_baseline_msfile_from_Jane/HD_163296_SB2_contfinal.ms',
                       'name' : 'SB2',
                       'field': 'HD_163296',
                       'line_spws': '', #SpwIDs of windows with lines that need to be flagged (this needs to be edited for each short baseline dataset)
                       'line_freqs': '', #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz)
                      }, #information about the short baseline measurement sets (SB1, SB2, SB3, etc in chronological order)

               'LB1': {'vis' : '/home/shared/ALMA_data/p484_large/HD163296/calibrated_msfile/calibrated_final_LB.ms',
                       'name' : 'LB1',
                       'field' : 'HD_163296',
                       'line_spws': np.array([3,7]), #these are generally going to be the same for most of the long-baseline datasets. Some datasets only have one execution block or have strange numbering
                       'line_freqs': np.array([2.30538e11, 2.30538e11]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz) 
                      }
               }

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
               ydatacolumn='data', avgtime='1e8', avgscan=True, avgbaseline=True, iteraxis='spw')

#######
# Here you may wish to flag problematic data before we do spectral line flagging to form an averaged continuum. 
#
# If so, use something like 
# flagmanager(vis = msfile, mode = 'save', versionname = 'init_cal_flags', comment = 'Flag states immediately after initial calibration') 
# If you need to undo the flagging, use
# flagmanager(vis = msfile, mode = 'restore', versionname = 'init_cal_flags') #restore flagged spectral line channels 
########

"""
Identify channels to flag based on the known velocity range of the line emission. The velocity range is based on line images from early reductions. If you are starting from scratch, 
you can estimate the range from the plotms command above. You may wish to limit your uvrange to 0~300 or so to only view the baselines with the highest amplitudes.     

NOTE: CO data in the SB1 and SB2 data were already flagged. So here we process only the LB data

"""

flagchannels_string = get_flagchannels(data_params['LB1'], prefix, velocity_range = np.array([-15, 20]))
# Flagchannels input string for LB1: '3:1854~1964, 7:1854~1964'

"""
Produces spectrally averaged continuum datasets
If you only want to include a subset of the windows, you can manually pass in values for contspw and width_array, e.g.
avg_cont(data_params[i], output_prefix, flagchannels = flagchannels_string, contspws = '0~2', width_array = [480,8,8]).
If you don't pass in values, all of the SPWs will be split out and the widths will be computed automatically to enforce a maximum channel width of 125 MHz.
WARNING: Only use the avg_cont function if the total bandwidth is recorded correctly in the original MS. There is sometimes a bug in CASA that records incorrect total bandwidths
"""

avg_cont(data_params['LB1'], prefix, flagchannels = flagchannels_string)

# sample command to check that amplitude vs. uvdist looks normal
# plotms(vis=prefix+'_SB1_initcont.ms', xaxis='uvdist', yaxis='amp', coloraxis='spw', avgtime='30', avgchannel='16')

"""
Quick imaging of every execution block in the measurement set using tclean. 
The threshold, scales, and mask should be adjusted for each source.
In this case, we picked our threshold, scales, and mask from previous reductions of the data. You may wish to experiment with these values when imaging. 
The threshold is ~3-4x the rms, the mask is an ellipse that covers all the emission and has roughly the same geometry, and we choose 4 to 6 scales such that the first scale is 0 (a point), and the largest is ~half the major axis of the mask.
The mask angle and the semimajor and semiminor axes should be the same for all imaging. The center is not necessarily fixed because of potential misalignments between observations. 
"""
mask_angle = 140 #position angle of mask in degrees
mask_semimajor = 2.3 #semimajor axis of mask in arcsec
mask_semiminor = 1.6 #semiminor axis of mask in arcsec
mask_ra = '17h56m21.279s'
mask_dec = '-21.57.22.421'

SB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % (mask_ra, mask_dec, mask_semimajor, mask_semiminor, mask_angle)

LB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % (mask_ra, mask_dec, mask_semimajor, mask_semiminor, mask_angle)

SB_scales = [0, 5, 10]
LB_scales = [0, 10, 30, 90, 270]
"""
In this section, we are imaging every execution block to check spatial alignment 
"""

if not skip_plots:
    #images are saved in the format prefix+'_name_initcont_exec#.ms'
    os.system('cp -r '+data_params['SB1']['vis']+' '+prefix+'_'+data_params['SB1']['name']+'_initcont.ms')
    image_each_obs(data_params['SB1'], prefix, mask = SB1_mask, scales = SB_scales, threshold = '0.15mJy', interactive = False)
    # inspection of images do not reveal additional bright background sources
    # there is however some phase noise in exec 1, 2, and 3
    
    os.system('cp -r '+data_params['SB2']['vis']+' '+prefix+'_'+data_params['SB2']['name']+'_initcont.ms')
    image_each_obs(data_params['SB2'], prefix, mask = SB1_mask, scales = SB_scales, threshold = '0.15mJy', interactive = False)
    # the rms noise in exec2 is 4X higher than in exec0 and 1

    image_each_obs(data_params['LB1'], prefix, mask = LB1_mask, scales = LB_scales, threshold = '0.1mJy', interactive = False)

    ### I AM HERE

    """
    Since the source looks axisymmetric, we will fit a Gaussian to the disk to estimate the location of the peak in each image and record the output.
    We are also very roughly estimating the PA and inclination for checking the flux scale offsets later (these are NOT the position angles and inclinations used for analysis of the final image products).
    Here, we are using the CLEAN mask to restrict the region over which the fit is occurring, but you may wish to shrink the region even further if your disk structure is complex 
    """
    
    fit_gaussian(prefix+'_LB1_initcont_exec0.image', region = LB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 17h56m21.278739s -21d57m22.57056s
    #Peak in J2000 coordinates: 17:56:21.27927, -021:57:22.563477
    #Pixel coordinates of peak: x = 1493.279 y = 1497.624
    #PA of Gaussian component: 131.93 deg
    #Inclination of Gaussian component: 46.95 deg

    fit_gaussian(prefix+'_LB1_initcont_exec1.image', region = LB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 17h56m21.278566s -21d57m22.58505s
    #Peak in J2000 coordinates: 17:56:21.27910, -021:57:22.577967
    #Pixel coordinates of peak: x = 1494.080 y = 1492.796
    #PA of Gaussian component: 125.60 deg
    #Inclination of Gaussian component: 43.75 deg

    fit_gaussian(prefix+'_SB1_initcont_exec0.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: J2000 17h56m21.278128s -21d57m22.42001s
    #Pixel coordinates of peak: x = 450.756 y = 450.516
    #PA of Gaussian component: 131.31 deg
    #Inclination of Gaussian component: 43.16 deg

    fit_gaussian(prefix+'_SB1_initcont_exec1.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: J2000 17h56m21.278108s -21d57m22.42058s
    #Pixel coordinates of peak: x = 450.765 y = 450.497
    #PA of Gaussian component: 131.09 deg
    #Inclination of Gaussian component: 43.62 deg

    fit_gaussian(prefix+'_SB1_initcont_exec2.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: J2000 17h56m21.278135s -21d57m22.42078s
    #Pixel coordinates of peak: x = 450.753 y = 450.491
    #PA of Gaussian component: 129.63 deg
    #Inclination of Gaussian component: 43.75 deg

    fit_gaussian(prefix+'_SB1_initcont_exec3.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: J2000 17h56m21.278139s -21d57m22.42057s
    #Pixel coordinates of peak: x = 450.751 y = 450.498
    #PA of Gaussian component: 130.20 deg
    #Inclination of Gaussian component: 43.99 deg

    fit_gaussian(prefix+'_SB1_initcont_exec4.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: J2000 17h56m21.278093s -21d57m22.42119s
    #Pixel coordinates of peak: x = 450.772 y = 450.477
    #PA of Gaussian component: 130.60 deg
    #Inclination of Gaussian component: 43.33 deg

    fit_gaussian(prefix+'_SB2_initcont_exec0.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: J2000 17h56m21.278090s -21d57m22.42614s
    #Pixel coordinates of peak: x = 450.463 y = 451.840
    #PA of Gaussian component: 124.47 deg
    #Inclination of Gaussian component: 45.12 deg

    fit_gaussian(prefix+'_SB2_initcont_exec1.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: J2000 17h56m21.278112s -21d57m22.42584s
    #Pixel coordinates of peak: x = 450.453 y = 451.850
    #PA of Gaussian component: 126.40 deg
    #Inclination of Gaussian component: 44.70 deg

    fit_gaussian(prefix+'_SB2_initcont_exec2.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: J2000 17h56m21.278015s -21d57m22.42165s
    #Pixel coordinates of peak: x = 450.498 y = 451.989
    #PA of Gaussian component: 130.83 deg
    #Inclination of Gaussian component: 47.09 deg


"""
Since the LB and SB blocks appear to be misaligned, we will shif them so that the 
image peaks fall on the phase center.
"""

common_dir = 'J2000 17h56m21.27927s -021.57.22.563477'  # we choose the peak of the first execution of LB1 to be the common direction.
 
mask_ra = '17h56m21.27927s'
mask_dec = '-021.57.22.563477'
common_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % (mask_ra, mask_dec, mask_semimajor, mask_semiminor, mask_angle)

# need to change to J2000 coordinates
shiftname = prefix+'_LB1_initcont_shift'
os.system('rm -rf '+shiftname+'.*')
fixvis(vis=prefix+'_LB1_initcont.ms', outputvis=shiftname+'.ms', field=data_params['LB1']['field'], phasecenter='J2000 17h56m21.27910s -021d57m22.577967s') # get phase center from gaussian fit
fixplanets(vis=shiftname+'.ms', field=data_params['LB1']['field'], direction=common_dir)
tclean_wrapper(vis=shiftname+'.ms', imagename=shiftname, mask=common_mask, scales=LB_scales, threshold='0.1mJy')
fit_gaussian(shiftname+'.image', region = common_mask)

shiftname = prefix+'_SB1_initcont_shift'
os.system('rm -rf '+shiftname+'.*')
fixvis(vis=prefix+'_SB1_initcont.ms', outputvis=shiftname+'.ms', field=data_params['SB1']['field'], phasecenter='J2000 17h56m21.278128s -21d57m22.42001') # get phase center from gaussian fit (using exec0)
fixplanets(vis=shiftname+'.ms', field=data_params['SB1']['field'], direction=common_dir)
tclean_wrapper(vis=shiftname+'.ms', imagename=shiftname, mask=common_mask, scales=SB_scales, threshold='0.1mJy')
fit_gaussian(shiftname+'.image', region = common_mask)

shiftname = prefix+'_SB2_initcont_shift'
os.system('rm -rf '+shiftname+'.*')
fixvis(vis=prefix+'_SB2_initcont.ms', outputvis=shiftname+'.ms', field=data_params['SB2']['field'], phasecenter='J2000 17h56m21.278112s -21d57m22.42584s') # get phase center from gaussian fit (using exec1)
fixplanets(vis=shiftname+'.ms', field=data_params['SB2']['field'], direction=common_dir)
tclean_wrapper(vis=shiftname+'.ms', imagename=shiftname, mask=common_mask, scales=SB_scales, threshold='0.1mJy')
fit_gaussian(shiftname+'.image', region = common_mask)



"""
After aligning the images, we want to check if the flux scales are consistent between execution blocks (within ~5%). 

"""

# We split out the individual execution blocks 

split_all_obs(prefix+'_SB2_initcont_shift.ms', prefix+'_SB2_initcont_shift_exec')
split_all_obs(prefix+'_SB1_initcont_shift.ms', prefix+'_SB1_initcont_shift_exec')
split_all_obs(prefix+'_LB1_initcont_shift.ms', prefix+'_LB1_initcont_shift_exec')


"""
First, check the pipeline outputs (STEP11/12, hif_setjy or hif_setmodels in the TASKS list of the qa products) to check whether the calibrator catalog matches up with the input flux density values for the calibrators.
(Also check the corresponding plots.)
        SB1, EB0 (4/June/2014  - X4bb):  J1733-130, 1.3087 Jy at 230.54926096GHz
	SB1, EB1 (14/June/2014 - X17c0): J1733-130, 1.21984 Jy at 230.54926096GHz
        SB1, EB2 (16/June/2014 - X3e97): J1733-130, 1.21984 Jy at 230.54926096GHz
        SB1, EB3 (17/June/2014 - X125c): J1733-130, 1.21984 Jy at 230.54926096GHz
        SB1, EB4 (29/June/2014 - X28dd): J1733-130, 1.27219 Jy at 230.539783959GHz

        SB2, EB0 (5/Aug/2015 - X14f5): Ceres was used to derive the flux of J1733-130, 1.98954 Jy at 230.525GHz
        SB2, EB1 (8/Aug/2015 - Xce2): Ceres was used to derive the flux of J1733-130, 2.02316 Jy at 230.525GHz
        SB2, EB2 (9/Aug/2015 - Xd6c): Titan was used ot derive the flux of 1733-130, 1.93651 Jy at 230.525GHz

        LB1, EB0 (08/Sep/2017 - X538): J1924-2914, 3.446 Jy at 232.538 GHz 
	LB1, EB1 (08/Sep/2017 - X83a): J1733-130, 1.517 Jy at 232.538 GHz

Now can check that these inputs are matching the current calibrator catalog:
"""
# SB1, EB0
au.getALMAFlux('J1733-130', frequency = '230.54926096Hz', date = '2014/06/04')	

"""
Closest Band 3 measurement: 2.330 +- 0.120 (age=-1 days) 103.5 GHz
Closest Band 3 measurement: 2.330 +- 0.120 (age=-1 days) 91.5 GHz
Closest Band 7 measurement: 0.990 +- 0.050 (age=+1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 21 days from 2014/06/04, with age separation of 0 days
  2014/05/14: freqs=[91.46, 103.49, 343.48], fluxes=[2.29, 2.21, 1.12]
Median Monte-Carlo result for 230.549261 = 1.397147 +- 0.182050 (scaled MAD = 0.180338)
Result using spectral index of -0.546326 for 230.549 GHz from 2.330 Jy at 97.475 GHz = 1.455796 +- 0.182050 Jy

*** The difference between the flux adopted in the pipeline and that in the catalog is 11%

"""

#SB1, EB1
au.getALMAFlux('J1733-130', frequency = '230.54926096Hz', date = '2014/06/14')	
"""
Closest Band 3 measurement: 2.300 +- 0.110 (age=+7 days) 103.5 GHz
Closest Band 3 measurement: 2.330 +- 0.100 (age=+7 days) 91.5 GHz
Closest Band 7 measurement: 0.990 +- 0.050 (age=+11 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -24 days from 2014/06/14, with age separation of 0 days
  2014/07/08: freqs=[91.46, 103.49, 343.48], fluxes=[2.21, 2.17, 0.91]
Median Monte-Carlo result for 230.549261 = 1.206416 +- 0.170484 (scaled MAD = 0.168484)
Result using spectral index of -0.686483 for 230.549 GHz from 2.315 Jy at 97.475 GHz = 1.282021 +- 0.170484 Jy

Calibration is consistent with the catalog

"""

#SB1, EB2
au.getALMAFlux('J1733-130', frequency = '230.54926096Hz', date = '2014/06/16')	
"""
Closest Band 3 measurement: 2.300 +- 0.110 (age=+9 days) 103.5 GHz
Closest Band 3 measurement: 2.330 +- 0.100 (age=+9 days) 91.5 GHz
Closest Band 7 measurement: 0.940 +- 0.080 (age=-13 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -22 days from 2014/06/16, with age separation of 0 days
  2014/07/08: freqs=[91.46, 103.49, 343.48], fluxes=[2.21, 2.17, 0.91]
Median Monte-Carlo result for 230.549261 = 1.210347 +- 0.170805 (scaled MAD = 0.166890)
Result using spectral index of -0.686483 for 230.549 GHz from 2.315 Jy at 97.475 GHz = 1.282021 +- 0.170805 Jy

Calibration is consisten with the catalog

"""

#SB1, EB3
au.getALMAFlux('J1733-130', frequency = '230.54926096Hz', date = '2014/06/17')	
"""
Closest Band 3 measurement: 2.300 +- 0.110 (age=+10 days) 103.5 GHz
Closest Band 3 measurement: 2.330 +- 0.100 (age=+10 days) 91.5 GHz
Closest Band 7 measurement: 0.940 +- 0.080 (age=-12 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -21 days from 2014/06/17, with age separation of 0 days
  2014/07/08: freqs=[91.46, 103.49, 343.48], fluxes=[2.21, 2.17, 0.91]
Median Monte-Carlo result for 230.549261 = 1.205014 +- 0.170391 (scaled MAD = 0.169001)
Result using spectral index of -0.686483 for 230.549 GHz from 2.315 Jy at 97.475 GHz = 1.282021 +- 0.170391 Jy

Calibration is consistent with the catalog

"""

#SB1, EB4
au.getALMAFlux('J1733-130', frequency = '230.54926096Hz', date = '2014/06/29')
"""
Closest Band 3 measurement: 2.430 +- 0.040 (age=+2 days) 91.5 GHz
Closest Band 7 measurement: 0.940 +- 0.080 (age=+0 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -9 days from 2014/06/29, with age separation of 0 days
  2014/07/08: freqs=[91.46, 103.49, 343.48], fluxes=[2.21, 2.17, 0.91]
Median Monte-Carlo result for 230.549261 = 1.208227 +- 0.170971 (scaled MAD = 0.171680)
Result using spectral index of -0.686483 for 230.549 GHz from 2.430 Jy at 91.460 GHz = 1.288134 +- 0.170971 Jy

Calibration is consistent with the catalog

"""

#SB2, EB0
au.getALMAFlux('J1733-130', frequency = '230.54926096Hz', date = '2015/08/05')
"""
Closest Band 3 measurement: 3.090 +- 0.110 (age=-2 days) 103.5 GHz
Closest Band 3 measurement: 3.080 +- 0.100 (age=-2 days) 91.5 GHz
Closest Band 7 measurement: 1.390 +- 0.090 (age=+0 days) 349.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -11 days from 2015/08/05, with age separation of 0 days
  2015/08/16: freqs=[103.49, 91.46, 349.49], fluxes=[2.92, 2.9, 1.4]
Median Monte-Carlo result for 230.549261 = 1.849774 +- 0.201949 (scaled MAD = 0.202516)
Result using spectral index of -0.524203 for 230.549 GHz from 3.085 Jy at 97.475 GHz = 1.964586 +- 0.201949 Jy

Calibration consistent with the catalog
"""

#SB2, EB1
au.getALMAFlux('J1733-130', frequency = '230.54926096Hz', date = '2015/08/08')
"""
Closest Band 3 measurement: 3.090 +- 0.110 (age=+1 days) 103.5 GHz
Closest Band 3 measurement: 3.080 +- 0.100 (age=+1 days) 91.5 GHz
Closest Band 7 measurement: 1.390 +- 0.090 (age=+3 days) 349.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -8 days from 2015/08/08, with age separation of 0 days
  2015/08/16: freqs=[103.49, 91.46, 349.49], fluxes=[2.92, 2.9, 1.4]
Median Monte-Carlo result for 230.549261 = 1.845194 +- 0.202016 (scaled MAD = 0.200036)
Result using spectral index of -0.524203 for 230.549 GHz from 3.085 Jy at 97.475 GHz = 1.964586 +- 0.202016 Jy

Calibration consistent with the catalog
"""

#SB2, EB2
au.getALMAFlux('J1733-130', frequency = '230.54926096Hz', date = '2015/08/09')
"""
Closest Band 3 measurement: 3.090 +- 0.110 (age=+2 days) 103.5 GHz
Closest Band 3 measurement: 3.080 +- 0.100 (age=+2 days) 91.5 GHz
Closest Band 7 measurement: 1.390 +- 0.090 (age=+4 days) 349.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -7 days from 2015/08/09, with age separation of 0 days
  2015/08/16: freqs=[103.49, 91.46, 349.49], fluxes=[2.92, 2.9, 1.4]
Median Monte-Carlo result for 230.549261 = 1.848432 +- 0.202791 (scaled MAD = 0.201533)
Result using spectral index of -0.524203 for 230.549 GHz from 3.085 Jy at 97.475 GHz = 1.964586 +- 0.202791 Jy

Calibration consistent with the catalog
"""

#LB1, EB0
au.getALMAFlux('J1924-2914', frequency = '232.538GHz', date = '2017/09/08')
"""
Closest Band 3 measurement: 5.650 +- 0.250 (age=-1 days) 103.5 GHz
Closest Band 3 measurement: 5.690 +- 0.200 (age=-1 days) 91.5 GHz
Closest Band 7 measurement: 2.590 +- 0.130 (age=-1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -1 days from 2017/09/08, with age separation of 0 days
  2017/09/09: freqs=[103.49, 91.46, 343.48], fluxes=[5.65, 5.69, 2.59]
Median Monte-Carlo result for 232.538000 = 3.302591 +- 0.270656 (scaled MAD = 0.271816)
Result using spectral index of -0.609631 for 232.538 GHz from 5.670 Jy at 97.475 GHz = 3.337228 +- 0.270656 Jy

Calibration consistent with the catalog
"""

#LB1, EB1
au.getALMAFlux('J1733-130', frequency = '232.538GHz', date = '2017/09/08')
"""
Closest Band 3 measurement: 2.970 +- 0.060 (age=+4 days) 91.5 GHz
Closest Band 7 measurement: 1.200 +- 0.040 (age=+3 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 15 days from 2017/09/08, with age separation of 0 days
  2017/08/24: freqs=[91.46, 343.48], fluxes=[2.8, 1.08]
Median Monte-Carlo result for 232.538000 = 1.432669 +- 0.152127 (scaled MAD = 0.152390)
Result using spectral index of -0.719951 for 232.538 GHz from 2.970 Jy at 91.460 GHz = 1.517006 +- 0.152127 Jy

Calibration consistent with the catalog
"""



"""
Here we export averaged visibilities to npz files and then plot the deprojected visibilities to compare the amplitude scales
"""

PA = 130.0 #these are the rough values pulled from Gaussian fitting and used for initial deprojection. They are NOT the final values used for subsequent data analysis
incl = 43.0

if not skip_plots:
    for msfile in [prefix+'_SB1_initcont_shift_exec0.ms', prefix+'_SB1_initcont_shift_exec1.ms',prefix+'_SB1_initcont_shift_exec2.ms', prefix+'_SB1_initcont_shift_exec3.ms', prefix+'_SB1_initcont_shift_exec4.ms', prefix+'_SB2_initcont_shift_exec0.ms', prefix+'_SB2_initcont_shift_exec1.ms',prefix+'_SB2_initcont_shift_exec2.ms',  prefix+'_LB1_initcont_shift_exec0.ms', prefix+'_LB1_initcont_shift_exec1.ms']:
        export_MS(msfile)

    #plot deprojected visibility profiles of all the execution blocks
    plot_deprojected([prefix+'_SB1_initcont_shift_exec0.vis.npz', prefix+'_SB1_initcont_shift_exec1.vis.npz', prefix+'_SB1_initcont_shift_exec2.vis.npz', prefix+'_SB1_initcont_shift_exec3.vis.npz',prefix+'_SB1_initcont_shift_exec4.vis.npz', prefix+'_SB2_initcont_shift_exec0.vis.npz', prefix+'_SB2_initcont_shift_exec1.vis.npz', prefix+'_SB2_initcont_shift_exec2.vis.npz', prefix+'_LB1_initcont_shift_exec0.vis.npz', prefix+'_LB1_initcont_shift_exec1.vis.npz'], fluxscale=[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0], PA = PA, incl = incl, show_err=False)
    
    plot_deprojected([prefix+'_SB1_initcont_shift_exec0.vis.npz', prefix+'_SB1_initcont_shift_exec1.vis.npz', prefix+'_SB1_initcont_shift_exec2.vis.npz', prefix+'_SB1_initcont_shift_exec3.vis.npz',prefix+'_SB1_initcont_shift_exec4.vis.npz'], fluxscale=[1.0,1.0,1.0,1.0,1.0], PA = PA, incl = incl, show_err=False)
    
    plot_deprojected([prefix+'_SB1_initcont_shift_exec0.vis.npz', prefix+'_SB2_initcont_shift_exec0.vis.npz', prefix+'_SB2_initcont_shift_exec1.vis.npz', prefix+'_SB2_initcont_shift_exec2.vis.npz'], fluxscale=[1.0,1.0,1.0,1.0], PA = PA, incl = incl, show_err=False)

    plot_deprojected([prefix+'_SB1_initcont_shift_exec0.vis.npz', prefix+'_LB1_initcont_shift_exec0.vis.npz', prefix+'_LB1_initcont_shift_exec1.vis.npz'], fluxscale=[1.0,1.0,1.0], PA = PA, incl = incl, show_err=False)
   
    # SB1 execution blocks have consistent fluxes
    # SB2 execution blocks have higher fluxes compared to SB1, despite the frequency be very similar
    # LB1, EB1 has lower flux than SB1 blocks

    estimate_flux_scale(reference = prefix+'_SB1_initcont_shift_exec0.vis.npz', comparison = prefix+'_SB2_initcont_shift_exec0.vis.npz', incl = incl, PA = PA)
    #The ratio of the fluxes of HD163296_SB2_initcont_shift_exec0.vis.npz to HD163296_SB1_initcont_shift_exec0.vis.npz is 1.10598
    #The scaling factor for gencal is 1.052 for your comparison measurement
    #The error on the weighted mean ratio is 3.271e-04, although it's likely that the weights in the measurement sets are too off by some constant factor

    estimate_flux_scale(reference = prefix+'_SB1_initcont_shift_exec0.vis.npz', comparison = prefix+'_SB2_initcont_shift_exec1.vis.npz', incl = incl, PA = PA)
    #The ratio of the fluxes of HD163296_SB2_initcont_shift_exec1.vis.npz to HD163296_SB1_initcont_shift_exec0.vis.npz is 1.10879
    #The scaling factor for gencal is 1.053 for your comparison measurement
    #The error on the weighted mean ratio is 2.414e-04, although it's likely that the weights in the measurement sets are too off by some constant factor

    estimate_flux_scale(reference = prefix+'_SB1_initcont_shift_exec0.vis.npz', comparison = prefix+'_SB2_initcont_shift_exec2.vis.npz', incl = incl, PA = PA)
    #The ratio of the fluxes of HD163296_SB2_initcont_shift_exec2.vis.npz to HD163296_SB1_initcont_shift_exec0.vis.npz is 1.10673
#The scaling factor for gencal is 1.052 for your comparison measurement
#The error on the weighted mean ratio is 7.195e-04, although it's likely that the weights in the measurement sets are too off by some constant factor

    plot_deprojected([prefix+'_SB1_initcont_shift_exec0.vis.npz', prefix+'_SB2_initcont_shift_exec0.vis.npz', prefix+'_SB2_initcont_shift_exec1.vis.npz', prefix+'_SB2_initcont_shift_exec2.vis.npz'], fluxscale=[1.0,1.0/1.10598,1.0/1.10879,1.0/1.10673], PA = PA, incl = incl, show_err=False)


    estimate_flux_scale(reference = prefix+'_SB1_initcont_shift_exec0.vis.npz', comparison = prefix+'_LB1_initcont_shift_exec1.vis.npz', incl = incl, PA = PA)
    #The ratio of the fluxes of HD163296_LB1_initcont_shift_exec1.vis.npz to HD163296_SB1_initcont_shift_exec0.vis.npz is 0.92406
    #The scaling factor for gencal is 0.961 for your comparison measurement
    #The error on the weighted mean ratio is 1.797e-04, although it's likely that the weights in the measurement sets are too off by some constant factor

    estimate_flux_scale(reference = prefix+'_SB1_initcont_shift_exec0.vis.npz', comparison = prefix+'_LB1_initcont_shift_exec0.vis.npz', incl = incl, PA = PA)
    #The ratio of the fluxes of HD163296_LB1_initcont_shift_exec0.vis.npz to HD163296_SB1_initcont_shift_exec0.vis.npz is 1.03809
    #The scaling factor for gencal is 1.019 for your comparison measurement
    #The error on the weighted mean ratio is 2.304e-04, although it's likely that the weights in the measurement sets are too off by some constant factor

    plot_deprojected([prefix+'_SB1_initcont_shift_exec0.vis.npz', prefix+'_LB1_initcont_shift_exec0.vis.npz', prefix+'_LB1_initcont_shift_exec1.vis.npz'], fluxscale=[1.0,1.0/1.03809,1.0/0.92406], PA = PA, incl = incl, show_err=False)

#now correct the flux scales
rescale_flux(prefix+'_SB2_initcont_shift_exec0.ms', [1.052])
rescale_flux(prefix+'_SB2_initcont_shift_exec1.ms', [1.053])
rescale_flux(prefix+'_SB2_initcont_shift_exec2.ms', [1.052])
rescale_flux(prefix+'_LB1_initcont_shift_exec1.ms', [0.961])

#Splitting out rescaled values into new MS: HD163296_SB2_initcont_shift_exec0_rescaled.ms
#Splitting out rescaled values into new MS: HD163296_SB2_initcont_shift_exec1_rescaled.ms
#Splitting out rescaled values into new MS: HD163296_SB2_initcont_shift_exec2_rescaled.ms
#Splitting out rescaled values into new MS: HD163296_LB1_initcont_shift_exec1_rescaled.ms


"""
Since SB data were already selfcalibrated we proceed selfcalibrating the combined detaset. 
"""

#merge all data in a single MS
comb_cont_p0 = prefix+'_comb_contp0'
os.system('rm -rf %s*' % comb_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [prefix+'_SB1_initcont_shift_exec0.ms', prefix+'_SB1_initcont_shift_exec1.ms', prefix+'_SB1_initcont_shift_exec2.ms', prefix+'_SB1_initcont_shift_exec3.ms',prefix+'_SB1_initcont_shift_exec4.ms', prefix+'_SB2_initcont_shift_exec0_rescaled.ms', prefix+'_SB2_initcont_shift_exec1_rescaled.ms', prefix+'_SB2_initcont_shift_exec2_rescaled.ms',prefix+'_LB1_initcont_shift_exec0.ms',prefix+'_LB1_initcont_shift_exec1_rescaled.ms' ], concatvis = comb_cont_p0+'.ms', dirtol = '0.1arcsec', copypointing = False) 

#make initial image
tclean_wrapper(vis=comb_cont_p0+'.ms', imagename = comb_cont_p0, mask=common_mask, scales=LB_scales, threshold = '0.10mJy', savemodel = 'modelcolumn', imsize=2000, cellsize='0.005arcsec', robust=-0.5)


noise_annulus ="annulus[[%s, %s],['%.2farcsec', '4.25arcsec']]" % (mask_ra, mask_dec, 1.3*mask_semimajor) #annulus over which we measure the noise. The inner radius is slightly larger than the semimajor axis of the mask (to add some buffer space around the mask) and the outer radius is set so that the annulus fits inside the long-baseline image size 
estimate_SNR(comb_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD163296_comb_contp0.image
#Beam 0.071 arcsec x 0.058 arcsec (80.27 deg)
#Flux inside disk mask: 716.19 mJy
#Peak intensity of source: 7.45 mJy/beam
#rms: 3.70e-02 mJy/beam
#Peak SNR: 201.35


""" 
We need to select  one or more reference antennas for gaincal

SB1, EB0 (manually calibrated): DA63
SB1, EB1 (manually calibrated): DA48
SB1, EB2 (manually calibrated): DA48
SB1, EB3 (manually calibrated): DA48
SB1, EB4 (manually calibrated): DA48

SB2, EB0 (manually calibrated): DA55
SB2, EB1 (manually calibrated): DA55
SB2, EB2 (manually calibrated): DA55

LB1, EB0: DA64, DA61, DA59, DA52, DV09
LB1, EB1: DA64, DA61, DV09, DA52, DA59

"""
get_station_numbers(comb_cont_p0+'.ms', 'DA63')
#Observation ID 0: DA63@A019

get_station_numbers(comb_cont_p0+'.ms', 'DA48')
#Observation ID 1: DA48@A046
#Observation ID 2: DA48@A046
#Observation ID 3: DA48@A046
#Observation ID 4: DA48@A046

get_station_numbers(comb_cont_p0+'.ms', 'DA55')
#Observation ID 5: DA55@A060
#Observation ID 6: DA55@A060
#Observation ID 7: DA55@A060

get_station_numbers(comb_cont_p0+'.ms', 'DA64')
#Observation ID 8: DA64@A065
#Observation ID 9: DA64@A065


comb_contspws = '0~23' #use all the windows
comb_refant = 'DA63@A019,DA48@A046,DA55@A060,DA64@A065'

comb_ex0_timerange = '2014/06/04/00:00:01~2014/06/04/23:59:59'
comb_ex1_timerange = '2014/06/14/00:00:01~2014/06/14/23:59:59'
comb_ex2_timerange = '2014/06/16/00:00:01~2014/06/16/23:59:59'
comb_ex3_timerange = '2014/06/17/00:00:01~2014/06/17/23:59:59'
comb_ex4_timerange = '2014/06/29/00:00:01~2014/06/29/23:59:59'
comb_ex5_timerange = '2015/08/05/00:00:01~2015/08/05/23:59:59'
comb_ex6_timerange = '2015/08/08/00:00:01~2015/08/08/23:59:59'
comb_ex7_timerange = '2015/08/09/00:00:01~2015/08/09/23:59:59'
comb_ex8_timerange = '2017/09/08/00:00:01~2017/09/09/23:59:59'
comb_ex9_timerange = '2017/09/08/00:00:01~2017/09/09/23:59:59'


# It's useful to check that the phases for the refant look good in all execution blocks in plotms. However, plotms has a tendency to crash in CASA 5.1.1, so it might be necessary to use plotms in an older version of CASA 
#plotms(vis=SB_cont_p0+'.ms', xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '0')
#plotms(vis=SB_cont_p0+'.ms', xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '1')

#first round of phase self-cal for short baseline data
comb_p1 = prefix+'_comb.p1'
os.system('rm -rf '+comb_p1)
gaincal(vis=comb_cont_p0+'.ms' , caltable=comb_p1, gaintype='T', combine='scans,spw', spw=comb_contspws, refant=comb_refant, calmode='p', solint='360s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [360s, 120s, 60s, 30s, 18s, 6s]

if not skip_plots:
    plotcal(caltable=comb_p1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex0_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=comb_p1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex1_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex2_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex3_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex4_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex5_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex6_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex7_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex8_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex9_timerange, plotrange=[0,0,-180,180])

os.system('rm -rf '+comb_cont_p0+'.backup.ms')
os.system('cp -r '+comb_cont_p0+'.ms '+comb_cont_p0+'.backup.ms')
comb_spwmap = [0,0,2,2,4,4,6,6,8,8,10,10,12,12,14,14,16,16,16,16,20,20,20,20]
applycal(vis=comb_cont_p0+'.ms', spw=comb_contspws, spwmap=comb_spwmap, gaintable=[comb_p1], interp = 'linearPD', calwt = True)

comb_cont_p1 = prefix+'_comb_contp1'
os.system('rm -rf %s*' % comb_cont_p1)
split(vis=comb_cont_p0+'.ms', outputvis=comb_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis=comb_cont_p1+'.ms', imagename = comb_cont_p1, mask=common_mask, scales=LB_scales, threshold = '0.10mJy', savemodel = 'modelcolumn', imsize=2000, cellsize='0.005arcsec', robust=-0.5)
estimate_SNR(comb_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD163296_comb_contp1.image
#Beam 0.049 arcsec x 0.038 arcsec (82.14 deg)
#Flux inside disk mask: 714.28 mJy
#Peak intensity of source: 3.91 mJy/beam
#rms: 2.66e-02 mJy/beam
#Peak SNR: 147.30


#second round of phase self-cal for short baseline data
comb_p2 = prefix+'_comb.p2'
os.system('rm -rf '+comb_p2)
gaincal(vis=comb_cont_p1+'.ms' , caltable=comb_p2, gaintype='T', combine='scans,spw', spw=comb_contspws, refant=comb_refant, calmode='p', solint='120s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [360s, 120s, 60s, 30s, 18s, 6s]

if not skip_plots:
    plotcal(caltable=comb_p2, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex0_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=comb_p2, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex1_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p2, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex2_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p2, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex3_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p2, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex4_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p2, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex5_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p2, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex6_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p2, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex7_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p2, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex8_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p2, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex9_timerange, plotrange=[0,0,-180,180])

os.system('rm -rf '+comb_cont_p1+'.backup.ms')
os.system('cp -r '+comb_cont_p1+'.ms '+comb_cont_p1+'.backup.ms')
comb_spwmap = [0,0,2,2,4,4,6,6,8,8,10,10,12,12,14,14,16,16,16,16,20,20,20,20]
applycal(vis=comb_cont_p1+'.ms', spw=comb_contspws, spwmap=comb_spwmap, gaintable=[comb_p2], interp = 'linearPD', calwt = True, applymode='calonly')

comb_cont_p2 = prefix+'_comb_contp2'
os.system('rm -rf %s*' % comb_cont_p2)
split(vis=comb_cont_p1+'.ms', outputvis=comb_cont_p2+'.ms', datacolumn='corrected')

tclean_wrapper(vis=comb_cont_p2+'.ms', imagename = comb_cont_p2, mask=common_mask, scales=LB_scales, threshold = '0.10mJy', savemodel = 'modelcolumn', imsize=2000, cellsize='0.005arcsec', robust=-0.5)
estimate_SNR(comb_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)

#HD163296_comb_contp2.image
#Beam 0.049 arcsec x 0.038 arcsec (82.14 deg)
#Flux inside disk mask: 714.29 mJy
#Peak intensity of source: 4.06 mJy/beam
#rms: 2.54e-02 mJy/beam
#Peak SNR: 159.80 -> SNR increase by 8%

#third round of phase self-cal for short baseline data
comb_p3 = prefix+'_comb.p3'
os.system('rm -rf '+comb_p3)
gaincal(vis=comb_cont_p2+'.ms' , caltable=comb_p3, gaintype='T', combine='scans,spw', spw=comb_contspws, refant=comb_refant, calmode='p', solint='60s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [360s, 120s, 60s, 30s, 18s, 6s]

if not skip_plots:
    plotcal(caltable=comb_p3, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex0_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=comb_p3, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex1_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p3, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex2_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p3, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex3_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p3, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex4_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p3, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex5_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p3, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex6_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p3, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex7_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p3, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex8_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p3, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex9_timerange, plotrange=[0,0,-180,180])

os.system('rm -rf '+comb_cont_p2+'.backup.ms')
os.system('cp -r '+comb_cont_p2+'.ms '+comb_cont_p2+'.backup.ms')
comb_spwmap = [0,0,2,2,4,4,6,6,8,8,10,10,12,12,14,14,16,16,16,16,20,20,20,20]
applycal(vis=comb_cont_p2+'.ms', spw=comb_contspws, spwmap=comb_spwmap, gaintable=[comb_p3], interp = 'linearPD', calwt = True, applymode='calonly')

comb_cont_p3 = prefix+'_comb_contp3'
os.system('rm -rf %s*' % comb_cont_p3)
split(vis=comb_cont_p2+'.ms', outputvis=comb_cont_p3+'.ms', datacolumn='corrected')

tclean_wrapper(vis=comb_cont_p3+'.ms', imagename = comb_cont_p3, mask=common_mask, scales=LB_scales, threshold = '0.10mJy', savemodel = 'modelcolumn', imsize=2000, cellsize='0.005arcsec', robust=-0.5)
estimate_SNR(comb_cont_p3+'.image', disk_mask = common_mask, noise_mask = noise_annulus)

#HD163296_comb_contp3.image
#Beam 0.049 arcsec x 0.038 arcsec (82.14 deg)
#Flux inside disk mask: 714.29 mJy
#Peak intensity of source: 4.18 mJy/beam
#rms: 2.47e-02 mJy/beam
#Peak SNR: 169.40 -> SNR increased by 6%

#fourth round of phase self-cal for short baseline data
comb_p4 = prefix+'_comb.p4'
os.system('rm -rf '+comb_p4)
gaincal(vis=comb_cont_p3+'.ms' , caltable=comb_p4, gaintype='T', combine='scans,spw', spw=comb_contspws, refant=comb_refant, calmode='p', solint='30s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [360s, 120s, 60s, 30s, 18s, 6s]

if not skip_plots:
    plotcal(caltable=comb_p4, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex0_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=comb_p4, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex1_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p4, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex2_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p4, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex3_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p4, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex4_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p4, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex5_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p4, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex6_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p4, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex7_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p4, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex8_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p4, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex9_timerange, plotrange=[0,0,-180,180])

os.system('rm -rf '+comb_cont_p3+'.backup.ms')
os.system('cp -r '+comb_cont_p3+'.ms '+comb_cont_p3+'.backup.ms')
comb_spwmap = [0,0,2,2,4,4,6,6,8,8,10,10,12,12,14,14,16,16,16,16,20,20,20,20]
applycal(vis=comb_cont_p3+'.ms', spw=comb_contspws, spwmap=comb_spwmap, gaintable=[comb_p4], interp = 'linearPD', calwt = True, applymode='calonly')

comb_cont_p4 = prefix+'_comb_contp4'
os.system('rm -rf %s*' % comb_cont_p4)
split(vis=comb_cont_p3+'.ms', outputvis=comb_cont_p4+'.ms', datacolumn='corrected')

tclean_wrapper(vis=comb_cont_p4+'.ms', imagename = comb_cont_p4, mask=common_mask, scales=LB_scales, threshold = '0.10mJy', savemodel = 'modelcolumn', imsize=2000, cellsize='0.005arcsec', robust=-0.5)
estimate_SNR(comb_cont_p4+'.image', disk_mask = common_mask, noise_mask = noise_annulus)

#HD163296_comb_contp4.image
#Beam 0.049 arcsec x 0.038 arcsec (82.14 deg)
#Flux inside disk mask: 714.30 mJy
#Peak intensity of source: 4.33 mJy/beam
#rms: 2.45e-02 mJy/beam
#Peak SNR: 177.01 -> SNR increased by 5%


#fifth round of phase self-cal for short baseline data
comb_p5 = prefix+'_comb.p5'
os.system('rm -rf '+comb_p5)
gaincal(vis=comb_cont_p4+'.ms' , caltable=comb_p5, gaintype='T', combine='scans,spw', spw=comb_contspws, refant=comb_refant, calmode='p', solint='18s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [360s, 120s, 60s, 30s, 18s, 6s]

if not skip_plots:
    plotcal(caltable=comb_p5, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex0_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=comb_p5, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex1_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p5, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex2_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p5, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex3_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p5, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex4_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p5, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex5_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p5, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex6_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p5, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex7_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p5, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex8_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_p5, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex9_timerange, plotrange=[0,0,-180,180])

os.system('rm -rf '+comb_cont_p4+'.backup.ms')
os.system('cp -r '+comb_cont_p4+'.ms '+comb_cont_p4+'.backup.ms')
comb_spwmap = [0,0,2,2,4,4,6,6,8,8,10,10,12,12,14,14,16,16,16,16,20,20,20,20]
applycal(vis=comb_cont_p4+'.ms', spw=comb_contspws, spwmap=comb_spwmap, gaintable=[comb_p5], interp = 'linearPD', calwt = True, applymode='calonly')

comb_cont_p5 = prefix+'_comb_contp5'
os.system('rm -rf %s*' % comb_cont_p5)
split(vis=comb_cont_p4+'.ms', outputvis=comb_cont_p5+'.ms', datacolumn='corrected')

tclean_wrapper(vis=comb_cont_p5+'.ms', imagename = comb_cont_p5, mask=common_mask, scales=LB_scales, threshold = '0.10mJy', savemodel = 'modelcolumn', imsize=2000, cellsize='0.005arcsec', robust=-0.5)
estimate_SNR(comb_cont_p5+'.image', disk_mask = common_mask, noise_mask = noise_annulus)

#HD163296_comb_contp5.image
#Beam 0.049 arcsec x 0.038 arcsec (82.14 deg)
#Flux inside disk mask: 714.34 mJy
#Peak intensity of source: 4.41 mJy/beam
#rms: 2.44e-02 mJy/beam
#Peak SNR: 180.20 -> SNR increased by 2% -- we stop phase-only selfcal here

# Proceeding with amplitude self-cal


os.system('rm -rf '+comb_cont_p5+'.ms')
os.system('cp -r '+comb_cont_p5+'.backup.ms '+comb_cont_p5+'.ms ')

comb_ap1 = prefix+'_comb.ap1'
os.system('rm -rf '+comb_ap1)
gaincal(vis=comb_cont_p5+'.ms' , caltable=comb_ap1, gaintype='T', combine = 'spw,scan', spw=comb_contspws, refant=comb_refant, calmode='ap', solint='inf', minsnr=3.0, minblperant=4, solnorm = False)

"""
if not skip_plots:
    plotcal(caltable=comb_ap1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex0_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=comb_ap1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex1_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_ap1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex2_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_ap1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex3_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_ap1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex4_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_ap1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex5_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_ap1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex6_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_ap1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex7_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_ap1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex8_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=comb_ap1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = comb_ex9_timerange, plotrange=[0,0,-180,180])
"""

#os.system('rm -rf '+comb_cont_p5+'.backup.ms')
#os.system('cp -r '+comb_cont_p5+'.ms '+comb_cont_p5+'.backup.ms')
comb_spwmap = [0,0,2,2,4,4,6,6,8,8,10,10,12,12,14,14,16,16,16,16,20,20,20,20]
applycal(vis=comb_cont_p5+'.ms', spw=comb_contspws, spwmap=comb_spwmap, gaintable=[comb_ap1], interp = 'linearPD', calwt = True, applymode='calonly')

comb_cont_ap1 = prefix+'_comb_contap1'
os.system('rm -rf %s*' % comb_cont_ap1)
split(vis=comb_cont_p5+'.ms', outputvis=comb_cont_ap1+'.ms', datacolumn='corrected')

tclean_wrapper(vis=comb_cont_ap1+'.ms', imagename = comb_cont_ap1, mask=common_mask, scales=LB_scales, threshold = '0.10mJy', savemodel = 'modelcolumn', imsize=2000, cellsize='0.005arcsec', robust=-0.5)
estimate_SNR(comb_cont_ap1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)

#HD163296_comb_contap1.image
#Beam 0.048 arcsec x 0.037 arcsec (81.31 deg)
#Flux inside disk mask: 714.84 mJy
#Peak intensity of source: 4.21 mJy/beam
#rms: 2.34e-02 mJy/beam
#Peak SNR: 180.26

# shorter solint do not provide any improvement in the SNR

os.system('cp -r '+comb_cont_ap1+'.ms HD163296_cont_final.ms')

# Make final image with robust 0
image = field+'_comb_cont_ap1_r0'
os.system('rm -rf '+image+'.*')
tclean(vis='HD163296_cont_final.ms', 
      imagename=image, 
      specmode='mfs', 
      gridder='standard',
      deconvolver='multiscale',
      scales = [0, 10, 30, 60, 120, 240, 480], #0, 1, 3, 6, 12, 24, 48 x the beam
      smallscalebias=0.7, 
      weighting='briggs', 
      robust=0.0,
      gain=0.1,
      calcpsf=False, # !!! Set to true if running for the first time
      calcres=False, # !!! Set to true if running for the first time
      imsize=2000,
      cell='0.005arcsec',
      threshold='0.017mJy', 
      niter=100000,
      cycleniter=5000,
      interactive=False,
      usemask='user',
      mask=common_mask)

### I AM HERE

exportfits(imagename=image+'.image', fitsimage='HD163296_script_image.fits', overwrite=True) 




