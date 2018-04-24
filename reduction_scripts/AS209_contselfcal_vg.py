"""
This script was written for CASA 5.1.1

Datasets calibrated (in order of date observed):



SB1: 2013.1.00226.S/   SB_name: AS_209_SB2_contfinal.ms  
     PI: Oberg
     Observed 02 July 2014 (1 execution block)
SB2  2013.1.00226.S/   SB_name: AS_209_SB3_contfinal.ms 
     PI: Oberg 
     Observed 17 July 2014 (1 execution block)   
SB3: 2015.1.00486.S/  Xb87877
     PI. Fedele
     Observed 22 September 2016 (1 execution blocks)
     Downloaded from archive and calibrated w/ pipeline
SB4: 2015.1.00486.S/  Xb8bd15
     PI. Fedele
     Observed 26 September 2016 (1 execution blocks)
     Downloaded from archive and calibrated w/ pipeline
SB5: 2016.1.00484.L/   SB_name: AS_209_SB1_contfinal.ms 
     Observed 09 May 2017 (1 execution block)
     PI: S. Andrews
     As delivered to PI
LB1: 2016.1.00484.L/   SB_name: calibrated_final.ms
     Observed 07 September 2017 and 19 September 2017 (2 execution blocks)
     PI: S. Andrews
     As delivered to PI

"""
import os
import sys
sys.path.append('/home/vguzman/local/analysis_scripts/')
import analysisUtils as au

execfile('/home/vguzman/projects/Disks-Large-Program/data-reduction/reduction_scripts/reduction_utils.py')

skip_plots = False #if this is true, all of the plotting and inspection steps will be skipped and the script can be executed non-interactively in CASA if all relevant values have been hard-coded already 

#to fill this dictionary out, use listobs for the relevant measurement set 

prefix = 'AS209' #string that identifies the source and is at the start of the name for all output files

#Note that if you are downloading data from the archive, your SPW numbering may differ from the SPWs in this script depending on how you split your data out!! 
data_params = {'SB1': {'vis' : '/home/vguzman/projects/Disks-Large-Program/data-reduction/data-as209/AS_209_SB2_contfinal.ms',
                       'name' : 'SB1',
                       'field': 'as_209',
                       'line_spws': np.array([]), #SpwIDs of windows with lines that need to be flagged (this needs to be edited for each short baseline dataset)
                       'line_freqs': np.array([]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz)
                      }, #information about the short baseline measurement sets (SB1, SB2, SB3, etc in chronological order)
               'SB2': {'vis' : '/home/vguzman/projects/Disks-Large-Program/data-reduction/data-as209/AS_209_SB3_contfinal.ms',
                       'name' : 'SB2',
                       'field': 'as_209',
                       'line_spws': np.array([]), 
                       'line_freqs': np.array([]), 
                      },
               'SB3': {'vis' : '/home/vguzman/projects/Disks-Large-Program/data-reduction/data-as209/2015.1.00486.S/science_goal.uid___A001_X340_X69/group.uid___A001_X340_X6a/member.uid___A001_X340_X6b/calibrated/uid___A002_Xb87877_X5849.ms.split.cal',
                       'name' : 'SB3',
                       'field': 'AS_209',
                       'line_spws': np.array([]), # continuum in spw 0. Other (4) spws in narrow (122 kHz channel) mode to get CO isotopologues lines. Will only use spw 0  
                       'line_freqs': np.array([]), 
                      },
               'SB4': {'vis' : '/home/vguzman/projects/Disks-Large-Program/data-reduction/data-as209/2015.1.00486.S/science_goal.uid___A001_X340_X69/group.uid___A001_X340_X6a/member.uid___A001_X340_X6b/calibrated/uid___A002_Xb8bd15_X472.ms.split.cal',
                       'name' : 'SB4',
                       'field': 'AS_209',
                       'line_spws': np.array([]), 
                       'line_freqs': np.array([]), 
                      },
               'SB5': {'vis' : '/home/vguzman/projects/Disks-Large-Program/data-reduction/data-as209/AS_209_SB1_contfinal.ms',
                       'name' : 'SB5',
                       'field': 'AS_209',
                       'line_spws': np.array([]), # CO line already flagged
                       'line_freqs': np.array([]), 
                       'cont_spws': None, # will include all of them
                      },
               'LB1': {'vis' : '/home/vguzman/projects/Disks-Large-Program/data-reduction/data-as209/calibrated_final.ms',
                       'name' : 'LB1',
                       'field' : 'AS_209',
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
               ydatacolumn='data', avgtime='1e8', avgscan=True, avgbaseline=True, 
               iteraxis='spw')

# Average continuum data

# CO line already flagged in Oberg's data
avg_cont(data_params['SB1'], prefix, flagchannels = '')
#Averaged continuum dataset saved to AS209_SB1_initcont.ms
avg_cont(data_params['SB2'], prefix, flagchannels = '')
#Averaged continuum dataset saved to AS209_SB2_initcont.ms

# Split spw 0 in Fedele's data
avg_cont(data_params['SB3'], prefix, contspws='0', width_array=8)
#Averaged continuum dataset saved to AS209_SB3_initcont.ms
avg_cont(data_params['SB4'], prefix, contspws='0', width_array=8)
#Averaged continuum dataset saved to AS209_SB4_initcont.ms

# CO line already flagged in Andrews's SB data
avg_cont(data_params['SB5'], prefix, flagchannels = '')
#Averaged continuum dataset saved to AS209_SB5_initcont.ms

# Flag CO line in LB data
flagchannels_string = get_flagchannels(data_params['LB1'], prefix, velocity_range = np.array([-10, 20]))
# Flagchannels input string for LB1: '3:1874~1968, 7:1874~1968'
avg_cont(data_params['LB1'], prefix, flagchannels = flagchannels_string)
#Averaged continuum dataset saved to AS209_LB1_initcont.ms


# check that amplitude vs. uvdist looks normal
# plotms(vis=prefix+'_SB1_initcont.ms', xaxis='uvdist', yaxis='amp', coloraxis='spw', avgtime='30', avgchannel='16')

"""
Quick imaging of every execution block in the measurement set using tclean. 
The threshold, scales, and mask should be adjusted for each source.
In this case, we picked our threshold, scales, and mask from previous reductions of the data. You may wish to experiment with these values when imaging. 
The threshold is ~3-4x the rms, the mask is an ellipse that covers all the emission and has roughly the same geometry, and we choose 4 to 6 scales such that the first scale is 0 (a point), and the largest is ~half the major axis of the mask.
The mask angle and the semimajor and semiminor axes should be the same for all imaging. The center is not necessarily fixed because of potential misalignments between observations. 
"""
mask_angle = 86 #position angle of mask in degrees
mask_semimajor = 1.3 #semimajor axis of mask in arcsec
mask_semiminor = 1.1 #semiminor axis of mask in arcsec

SB_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % ('16h49m15.29s', '-14.22.09.04', mask_semimajor, mask_semiminor, mask_angle)

LB_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % ('16h49m15.29s', '-14.22.09.04', mask_semimajor, mask_semiminor, mask_angle)

SB_scales = [0, 5, 10, 20]
LB_scales = [0, 5, 30, 100, 200]
"""
In this section, we are imaging every execution block to check spatial alignment 
"""

if not skip_plots:
    #images are saved in the format prefix+'_name_initcont_exec#.ms'
    image_each_obs(data_params['SB1'], prefix, mask = SB_mask, scales = SB_scales, threshold = '1.0mJy', interactive = False)
    image_each_obs(data_params['SB2'], prefix, mask = SB_mask, scales = SB_scales, threshold = '0.5mJy', interactive = False)
    image_each_obs(data_params['SB3'], prefix, mask = SB_mask, scales = SB_scales, threshold = '1.0mJy', interactive = False)
    image_each_obs(data_params['SB4'], prefix, mask = SB_mask, scales = SB_scales, threshold = '1.0mJy', interactive = False)
    image_each_obs(data_params['SB5'], prefix, mask = SB_mask, scales = SB_scales, threshold = '0.25mJy', interactive = False)

    image_each_obs(data_params['LB1'], prefix, mask = LB_mask, scales = LB_scales, threshold = '0.06mJy', interactive = False)

    """
    Since the source looks axisymmetric, we will fit a Gaussian to the disk to estimate the location of the peak in each image and record the output.
    We are also very roughly estimating the PA and inclination for checking the flux scale offsets later (these are NOT the position angles and inclinations used for analysis of the final image products.
    Here, we are using the CLEAN mask to restrict the region over which the fit is occurring, but you may wish to shrink the region even further if your disk structure is complex 
    """

    fit_gaussian(prefix+'_SB1_initcont.image', region = SB_mask)
    #Peak of Gaussian component identified with imfit: J2000 16h49m15.29419s -14d22m09.04819s

    fit_gaussian(prefix+'_SB2_initcont.image', region = SB_mask)
    #Peak of Gaussian component identified with imfit: J2000 16h49m15.29387s -14d22m09.04892s

    fit_gaussian(prefix+'_SB3_initcont.image', region = SB_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h49m15.29230s -14d22m09.02243s

    fit_gaussian(prefix+'_SB4_initcont.image', region = SB_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h49m15.29370s -14d22m09.08238s
    #Peak in J2000 coordinates: 16:49:15.29444, -014:22:09.070835

    fit_gaussian(prefix+'_SB5_initcont.image', region = SB_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h49m15.29314s -14d22m09.06113s
    #Peak in J2000 coordinates: 16:49:15.29388, -014:22:09.049585

    fit_gaussian(prefix+'_LB1_initcont_exec0.image', region = LB_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h49m15.29351s -14d22m09.04933s
    #Peak in J2000 coordinates: 16:49:15.29425, -014:22:09.037785

    fit_gaussian(prefix+'_LB1_initcont_exec1.image', region = LB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h49m15.29389s -14d22m09.05971s
    #Peak in J2000 coordinates: 16:49:15.29463, -014:22:09.048165
    #Pixel coordinates of peak: x = 1497.366 y = 1492.960
    #PA of Gaussian component: 85.41 deg
    #Inclination of Gaussian component: 34.95 deg


"""
Since the individual execution blocks appear to be slightly misaligned, 
we will be splitting out the individual execution blocks, 
shifting them so that the image peaks fall on the phase center, 
reassigning the phase centers to a common direction (for ease of concat)
and imaging to check the shift  
"""

split_all_obs(prefix+'_LB1_initcont.ms', prefix+'_LB1_initcont_exec')
#Saving observation 0 of AS209_LB1_initcont.ms to AS209_LB1_initcont_exec0.ms
#Saving observation 1 of AS209_LB1_initcont.ms to AS209_LB1_initcont_exec1.ms

common_dir = 'J2000 16h49m15.29463s -014.22.09.048165' #choose peak of second execution of LB1 to be the common direction (the better-quality of the high-res observations)   

#need to change to J2000 coordinates
mask_ra = '16h49m15.29463s'
mask_dec = '-14.22.09.048165'
common_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % (mask_ra, mask_dec, mask_semimajor, mask_semiminor, mask_angle)

shiftname = prefix+'_SB1_initcont_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_SB1_initcont.ms', outputvis=shiftname+'.ms', field = data_params['SB1']['field'], phasecenter='J2000 16h49m15.29419s -14d22m09.04819s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['SB1']['field'], direction = common_dir) #fixplanets works only with J2000, not ICRS
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = SB_scales, threshold = '1.0mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 16h49m15.29469s -14d22m09.04843s

shiftname = prefix+'_SB2_initcont_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_SB2_initcont.ms', outputvis=shiftname+'.ms', field = data_params['SB2']['field'], phasecenter='J2000 16h49m15.29387s -14d22m09.04892s')      
fixplanets(vis = shiftname+'.ms', field = data_params['SB2']['field'], direction = common_dir)
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = SB_scales, threshold = '0.5mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 16h49m15.29464s -14d22m09.04823s

shiftname = prefix+'_SB3_initcont_shift'
os.system('rm -rf %s.ms' % shiftname)                                                                            
fixvis(vis=prefix+'_SB3_initcont.ms', outputvis=shiftname+'.ms', field = data_params['SB3']['field'], phasecenter='ICRS 16h49m15.29282s -14d22m09.02516s')      
fixplanets(vis = shiftname+'.ms', field = data_params['SB3']['field'], direction = common_dir)
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = SB_scales, threshold = '1.0mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 16h49m15.29410s -14d22m09.04561s

shiftname = prefix+'_SB4_initcont_shift'
os.system('rm -rf %s.ms' % shiftname)                                                                             
fixvis(vis=prefix+'_SB4_initcont.ms', outputvis=shiftname+'.ms', field = data_params['SB4']['field'], phasecenter='ICRS 16h49m15.29478s -14d22m09.07827s')      
fixplanets(vis = shiftname+'.ms', field = data_params['SB4']['field'], direction = common_dir)
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = SB_scales, threshold = '1.0mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 16h49m15.29355s -14d22m09.05218s

shiftname = prefix+'_SB5_initcont_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_SB5_initcont.ms', outputvis=shiftname+'.ms', field = data_params['SB5']['field'], phasecenter='ICRS 16h49m15.29314s -14d22m09.06113s')      
fixplanets(vis = shiftname+'.ms', field = data_params['SB5']['field'], direction = common_dir)
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = SB_scales, threshold = '0.25mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 16h49m15.29463s -14d22m09.04812s

shiftname = prefix+'_LB1_initcont_exec0_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_LB1_initcont_exec0.ms', outputvis=shiftname+'.ms', field = data_params['LB1']['field'], phasecenter='ICRS 16h49m15.29351s -14d22m09.04933s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['LB1']['field'], direction = common_dir)
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = LB_scales, threshold = '0.06mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 16h49m15.29463s -14d22m09.04817s

shiftname = prefix+'_LB1_initcont_exec1_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_LB1_initcont_exec1.ms', outputvis=shiftname+'.ms', field = data_params['LB1']['field'], phasecenter='ICRS 16h49m15.29389s -14d22m09.05971s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['LB1']['field'], direction = common_dir)
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = LB_scales, threshold = '0.09mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 16h49m15.29463s -14d22m09.04780s


"""
After aligning the images, we want to check if the flux scales seem consistent between execution blocks (within ~5%)
First, we check the uid___xxxxx.casa_commands.log in the log directory of the data products folder (or the calibration script in the manual case) to check whether the calibrator catalog matches up with the input flux density values for the calibrators
(You should also check the plots of the calibrators in the data products to make sure that the amplitudes look consistent with the models that were inserted)
"""

#SB5
au.getALMAFlux('J1733-1304', frequency = '232.617GHz', date = '2017/05/09')
"""
Using Band 3 measurement: 2.890 +- 0.050 (age=4 days) 91.5 GHz
Using Band 7 measurement: 1.120 +- 0.060 (age=5 days) 343.5 GHz
exact value: -0.716376,  1-sigma extrema: -0.663748, -0.770949,  mean unc=0.053600
Median Monte-Carlo result for 232.617000 = 1.478989 +- 0.130852 (scaled MAD = 0.128885)
Result using spectral index of -0.716376 for 232.617000 GHz from 91.460000 GHz = 1.480716 +- 0.130852 Jy

Pipeline command:
setjy(fluxdensity=[1.4837, 0.0, 0.0, 0.0], scalebychan=True,
      vis='uid___A002_Xc02418_X29c8.ms', spix=-0.714209688596, spw='19',
      field='J1733-1304', reffreq='232.617 GHz',
      intent='CALIBRATE_FLUX#ON_SOURCE', selectdata=True, standard='manual',
      usescratch=True)

Calibration is consistent with catalog
"""

#LB1, first execution
au.getALMAFlux('J1733-1304', frequency = '232.584GHz', date = '2017/09/07')
"""
Using Band 3 measurement: 2.970 +- 0.060 (age=3 days) 91.5 GHz
Using Band 7 measurement: 1.200 +- 0.040 (age=2 days) 343.5 GHz
exact value: -0.684871,  1-sigma extrema: -0.644668, -0.725607,  mean unc=0.040470
Median Monte-Carlo result for 232.584000 = 1.569084 +- 0.088140 (scaled MAD = 0.088485)
Result using spectral index of -0.684871 for 232.584000 GHz from 91.460000 GHz = 1.567273 +- 0.088140 Jy

Pipeline command:
setjy(fluxdensity=[1.5168, 0.0, 0.0, 0.0], scalebychan=True,
      vis='uid___A002_Xc44eb5_X6da.ms', spix=-0.719950738157, spw='19',
      field='J1733-1304', reffreq='232.584 GHz',
      intent='CALIBRATE_FLUX#ON_SOURCE', selectdata=True, standard='manual',
      usescratch=True)

Calibration is consistent with catalog
"""

#LB1, second execution 
au.getALMAFlux('J1733-1304', frequency = '232.585GHz', date = '2017/09/19')

"""
Using Band 3 measurement: 3.110 +- 0.050 (age=3 days) 91.5 GHz
Using Band 7 measurement: 1.290 +- 0.050 (age=-4 days) 343.5 GHz
exact value: -0.665026,  1-sigma extrema: -0.624039, -0.706954,  mean unc=0.041457
Median Monte-Carlo result for 232.585000 = 1.672466 +- 0.107857 (scaled MAD = 0.106957)
Result using spectral index of -0.665026 for 232.585000 GHz from 91.460000 GHz = 1.671829 +- 0.107857 Jy

Pipeline command:
setjy(fluxdensity=[1.5883, 0.0, 0.0, 0.0], scalebychan=True,
      vis='uid___A002_Xc49eba_X5e5d.ms', spix=-0.719950738157, spw='19',
      field='J1733-1304', reffreq='232.585 GHz',
      intent='CALIBRATE_FLUX#ON_SOURCE', selectdata=True, standard='manual',
      usescratch=True)

difference is ~5%, so we will not worry about it.
"""

"""
Here we export averaged visibilities to npz files and then plot the deprojected visibilities to compare the amplitude scales
"""

PA = 86 #these are the rough values pulled from Gaussian fitting and used for initial deprojection. They are NOT the final values used for subsequent data analysis
incl = 35

if not skip_plots:
    for msfile in [prefix+'_SB1_initcont_shift.ms', prefix+'_SB2_initcont_shift.ms', prefix+'_SB3_initcont_shift.ms', prefix+'_SB4_initcont_shift.ms', prefix+'_SB5_initcont_shift.ms' prefix+'_LB1_initcont_exec0_shift.ms', prefix+'_LB1_initcont_exec1_shift.ms']:
        export_MS(msfile)
    
    #plot deprojected visibility profiles of all the execution blocks
    plot_deprojected([prefix+'_SB1_initcont_shift.vis.npz', prefix+'_SB2_initcont_shift.vis.npz', prefix+'_SB3_initcont_shift.vis.npz', prefix+'_SB4_initcont_shift.vis.npz', prefix+'_SB5_initcont_shift.vis.npz', prefix+'_LB1_initcont_exec0_shift.vis.npz', prefix+'_LB1_initcont_exec1_shift.vis.npz'],PA = PA, incl = incl)
    #SB3 and SB4 have slithly lower fluxes than the rest of the data
    #We use the function below to estimate the degree of the flux scale offset. We use the first execution block of SB1 for comparison.

    estimate_flux_scale(reference = prefix+'_LB1_initcont_exec0_shift.vis.npz', comparison = prefix+'_SB3_initcont_shift.vis.npz', incl = incl, PA = PA)
    #The ratio of the fluxes of ../AS209_SB3_initcont_shift.vis.npz to ../AS209_LB1_initcont_exec0_shift.vis.npz is 0.91450
    #The scaling factor for gencal is 0.956 for your comparison measurement
    #The error on the weighted mean ratio is 4.753e-04, although it's likely that the weights in the measurement sets are too off by some constant factor

    estimate_flux_scale(reference = prefix+'_LB1_initcont_exec0_shift.vis.npz', comparison = prefix+'_SB4_initcont_shift.vis.npz', incl = incl, PA = PA)
    #The ratio of the fluxes of ../AS209_SB4_initcont_shift.vis.npz to ../AS209_LB1_initcont_exec0_shift.vis.npz is 0.82057
    #The scaling factor for gencal is 0.906 for your comparison measurement
    #The error on the weighted mean ratio is 4.425e-04, although it's likely that the weights in the measurement sets are too off by some constant factor

    #We replot the deprojected visibilities with rescaled factors to check that the values make sense
    plot_deprojected([prefix+'_SB3_initcont_shift.vis.npz', prefix+'_SB4_initcont_shift.vis.npz', prefix+'_LB1_initcont_exec0_shift.vis.npz', prefix+'_LB1_initcont_exec1_shift.vis.npz'],
                 PA = PA, incl = incl, fluxscale = [1./0.91450, 1./0.82057, 1., 1.])

#now correct the flux of the discrepant dataset
rescale_flux(prefix+'_SB3_initcont_shift.ms', [0.956])
#Splitting out rescaled values into new ms: AS209_SB3_initcont_shift_rescaled.ms
rescale_flux(prefix+'_SB4_initcont_shift.ms', [0.906])
#Splitting out rescaled values into new ms: AS209_SB4_initcont_shift_rescaled.ms

"""
Start of self-calibration of the short-baseline data 
"""
#merge the short-baseline execution blocks into a single MS
SB_cont_p0 = prefix+'_SB_contp0'
os.system('rm -rf %s*' % SB_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [prefix+'_SB1_initcont_shift.ms', prefix+'_SB2_initcont_shift.ms', prefix+'_SB3_initcont_shift_rescaled.ms', prefix+'_SB4_initcont_shift_rescaled.ms', prefix+'_SB5_initcont_shift.ms'], concatvis = SB_cont_p0+'.ms', dirtol = '0.1arcsec', copypointing = False) 

#make initial image
tclean_wrapper(vis = SB_cont_p0+'.ms', imagename = SB_cont_p0, mask = common_mask, scales = SB_scales, threshold = '0.2mJy', savemodel = 'modelcolumn')

noise_annulus ="annulus[[%s, %s],['%.2farcsec', '4.25arcsec']]" % (mask_ra, mask_dec, 1.1*mask_semimajor) #annulus over which we measure the noise. The inner radius is slightly larger than the semimajor axis of the mask (to add some buffer space around the mask) and the outer radius is set so that the annulus fits inside the long-baseline image size 
estimate_SNR(SB_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#AS209_SB_contp0.image
#Beam 0.221 arcsec x 0.195 arcsec (-86.66 deg)
#Flux inside disk mask: 264.90 mJy
#Peak intensity of source: 20.63 mJy/beam
#rms: 9.26e-02 mJy/beam
#Peak SNR: 222.75

"""
We need to select one or more reference antennae for gaincal

We first look at the CASA command log (or manual calibration script) to see how the reference antennae choices were ranked (weighted toward antennae close to the center of the array and with good SNR)
Note that gaincal will sometimes choose a different reference antenna than the one specified if it deems another one to be a better choice 

SB1: DA48
SB2: DA48
SB3: DV22
SB4: DV22
SB5: DA49,DA59,DA41,DV04,DV15,DV18,DA46
First execution of LB1: DA61,DA64,DV09,DA59,DA52,DV06,DA47  
Second execution of LB1: DA49,DA59,DA41,DV04,DV15,DV18,DA46

If you want to double check whether the antenna locations are reasonable, you can use something like plotants(vis = SB_cont_p0+'.ms')

"""

SB_contspws = '0~14' #change as appropriate
SB_refant = 'DA48@A046,DV22@A011,DA41@A004'  
SB1_timerange = '2014/07/02/04:18:22~2014/07/02/04:49:28' #change timerange as appropriate
SB2_timerange = '2014/07/17/03:10:34~2014/07/17/03:40:25'
SB3_timerange = '2016/09/22/23:29:53~2016/09/23/00:18:23'
SB4_timerange = '2016/09/26/23:27:53~2016/09/27/00:16:35'
SB5_timerange = '2017/05/09/04:46:58~2017/05/09/05:21:37'

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
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB3_timerange)
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB4_timerange)
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB5_timerange)

applycal(vis=SB_cont_p0+'.ms', spw=SB_contspws, gaintable=[SB_p1], interp = 'linearPD', calwt = True)

SB_cont_p1 = prefix+'_SB_contp1'
os.system('rm -rf %s*' % SB_cont_p1)
split(vis=SB_cont_p0+'.ms', outputvis=SB_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p1+'.ms' , imagename = SB_cont_p1, mask = common_mask, scales = SB_scales, threshold = '0.1mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#AS209_SB_contp1.image
#Beam 0.226 arcsec x 0.197 arcsec (-88.69 deg)
#Flux inside disk mask: 274.62 mJy
#Peak intensity of source: 22.34 mJy/beam
#rms: 4.78e-02 mJy/beam
#Peak SNR: 467.24


#second round of phase self-cal for short baseline data
SB_p2 = prefix+'_SB.p2'
os.system('rm -rf '+SB_p2)
gaincal(vis=SB_cont_p1+'.ms' , caltable=SB_p2, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='p', solint='60s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_timerange) 
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB2_timerange)
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB3_timerange)
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB4_timerange)
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB5_timerange)

applycal(vis=SB_cont_p1+'.ms', spw=SB_contspws, gaintable=[SB_p2], interp = 'linearPD', calwt = True)

SB_cont_p2 = prefix+'_SB_contp2'
os.system('rm -rf %s*' % SB_cont_p2)
split(vis=SB_cont_p1+'.ms', outputvis=SB_cont_p2+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p2+'.ms' , imagename = SB_cont_p2, mask = common_mask, scales = SB_scales, threshold = '0.1mJy', savemodel = 'modelcolumn') 
estimate_SNR(SB_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#AS209_SB_contp2.image
#Beam 0.229 arcsec x 0.197 arcsec (-89.81 deg)
#Flux inside disk mask: 275.03 mJy
#Peak intensity of source: 22.74 mJy/beam
#rms: 4.94e-02 mJy/beam
#Peak SNR: 460.18

# SNR decreased a bit but peak intensity increased also.
# tried third round of phase self-cal but did not improve image. stop here

SB_ap = prefix+'_SB.ap'
os.system('rm -rf '+SB_ap)
#note that the solint and minsnr are larger for amp self-cal
#try solnorm = False first. If that leads to bad solutions, try solnorm = True. If that still doesn't help, then just skip amp self-cal
gaincal(vis=SB_cont_p2+'.ms' , caltable=SB_ap, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='ap', solint='inf', minsnr=3.0, minblperant=4, solnorm = False) 

if not skip_plots:
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB1_timerange) 
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB2_timerange)
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB3_timerange)
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB4_timerange)
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB5_timerange)

applycal(vis=SB_cont_p2+'.ms', spw=SB_contspws, gaintable=[SB_ap], interp = 'linearPD', calwt = True)

SB_cont_ap = prefix+'_SB_contap'
os.system('rm -rf %s*' % SB_cont_ap)
split(vis=SB_cont_p2+'.ms', outputvis=SB_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_ap+'.ms' , imagename = SB_cont_ap, mask = common_mask, scales = SB_scales, threshold = '0.1mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#AS209_SB_contap.image
#Beam 0.226 arcsec x 0.192 arcsec (88.82 deg)
#Flux inside disk mask: 272.76 mJy
#Peak intensity of source: 21.96 mJy/beam
#rms: 2.71e-02 mJy/beam
#Peak SNR: 811.33


#now we concatenate all the data together

combined_cont_p0 = prefix+'_combined_contp0'
os.system('rm -rf %s*' % combined_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [SB_cont_ap+'.ms', prefix+'_LB1_initcont_exec0_shift.ms', prefix+'_LB1_initcont_exec1_shift_rescaled.ms'], concatvis = combined_cont_p0+'.ms' , dirtol = '0.1arcsec', copypointing = False) 

tclean_wrapper(vis = combined_cont_p0+'.ms' , imagename = combined_cont_p0, mask = common_mask, scales = LB_scales, threshold = '0.06mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#AS209_combined_contp0.image
#Beam 0.056 arcsec x 0.039 arcsec (-86.46 deg)
#Flux inside disk mask: 267.58 mJy
#Peak intensity of source: 2.32 mJy/beam
#rms: 1.30e-02 mJy/beam
#Peak SNR: 177.60

combined_refant = 'DA61@A015,DA48@A046,DV22@A017,DA41@A004'
combined_contspws = '0~22'
combined_spwmap =  [0, 0, 0, 3, 3, 3, 3, 3, 3, 9, 10, 11, 11, 11, 11, 15, 15, 15, 15, 19, 19, 19, 19] #note that the tables produced by gaincal in 5.1.1 have spectral windows numbered differently if you use the combine = 'spw' option. Previously, all of the solutions would be written to spectral window 0. Now, they are written to the first window in each execution block. So, the spwmap argument has to correspond to the first window in each execution block you want to calibrate. 

LB1_obs0_timerange = '2017/09/07/00:41:29~2017/09/07/01:38:36'
LB2_obs0_timerange = '2017/09/19/23:35:28~2017/09/20/00:32:41'

#first round of phase self-cal for long baseline data
combined_p1 = prefix+'_combined.p1'
os.system('rm -rf '+combined_p1)
gaincal(vis=combined_cont_p0+'.ms' , caltable=combined_p1, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='900s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [900s, 360s, 180s, 60s, 30s, 6s]

if not skip_plots:
    plotcal(caltable=combined_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 
    plotcal(caltable=combined_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB2_obs0_timerange)

applycal(vis=combined_cont_p0+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p1], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p1 = prefix+'_combined_contp1'
os.system('rm -rf %s*' % combined_cont_p1)
split(vis=combined_cont_p0+'.ms', outputvis=combined_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p1+'.ms' , imagename = combined_cont_p1, mask = common_mask, scales = LB_scales, threshold = '0.06mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#AS209_combined_contp1.image
#Beam 0.056 arcsec x 0.039 arcsec (-86.46 deg)
#Flux inside disk mask: 267.46 mJy
#Peak intensity of source: 2.39 mJy/beam
#rms: 1.23e-02 mJy/beam
#Peak SNR: 195.15


#second round of phase self-cal for long baseline data
combined_p2 = prefix+'_combined.p2'
os.system('rm -rf '+combined_p2)
gaincal(vis=combined_cont_p1+'.ms' , caltable=combined_p2, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='360s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 
    plotcal(caltable=combined_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs1_timerange)

applycal(vis=combined_cont_p1+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p2], interp = 'linearPD', calwt = True, applymode = 'calonly')


combined_cont_p2 = prefix+'_combined_contp2'
os.system('rm -rf %s*' % combined_cont_p2)
split(vis=combined_cont_p1+'.ms', outputvis=combined_cont_p2+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p2+'.ms' , imagename = combined_cont_p2, mask = common_mask, scales = LB_scales, threshold = '0.06mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#AS209_combined_contp2.image
#Beam 0.056 arcsec x 0.039 arcsec (-86.46 deg)
#Flux inside disk mask: 267.69 mJy
#Peak intensity of source: 2.42 mJy/beam
#rms: 1.20e-02 mJy/beam
#Peak SNR: 200.95


#third round of phase self-cal for long-baseline data 
combined_p3 = prefix+'_combined.p3'
os.system('rm -rf '+combined_p3)
gaincal(vis=combined_cont_p2+'.ms' , caltable=combined_p3, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='180s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 
    plotcal(caltable=combined_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs1_timerange)

applycal(vis=combined_cont_p2+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p3], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p3 = prefix+'_combined_contp3'
os.system('rm -rf %s*' % combined_cont_p3)
split(vis=combined_cont_p2+'.ms', outputvis=combined_cont_p3+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p3+'.ms' , imagename = combined_cont_p3, mask = common_mask, scales = LB_scales, threshold = '0.06mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p3+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#AS209_combined_contp3.image
#Beam 0.056 arcsec x 0.039 arcsec (-86.46 deg)
#Flux inside disk mask: 267.53 mJy
#Peak intensity of source: 2.44 mJy/beam
#rms: 1.19e-02 mJy/beam
#Peak SNR: 204.72


#fourth round of phase self-cal for long-baseline data 
combined_p4 = prefix+'_combined.p4'
os.system('rm -rf '+combined_p4)
gaincal(vis=combined_cont_p3+'.ms' , caltable=combined_p4, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='60s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p4, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 
    plotcal(caltable=combined_p4, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs1_timerange)

applycal(vis=combined_cont_p3+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p4], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p4 = prefix+'_combined_contp4'
os.system('rm -rf %s*' % combined_cont_p4)
split(vis=combined_cont_p3+'.ms', outputvis=combined_cont_p4+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p4+'.ms' , imagename = combined_cont_p4, mask = common_mask, scales = LB_scales, threshold = '0.06mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p4+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#AS209_combined_contp4.image
#Beam 0.056 arcsec x 0.039 arcsec (-86.46 deg)
#Flux inside disk mask: 267.51 mJy
#Peak intensity of source: 2.52 mJy/beam
#rms: 1.18e-02 mJy/beam
#Peak SNR: 212.96


#fifth round of phase self-cal for long-baseline data 

combined_p5 = prefix+'_combined.p5'
os.system('rm -rf '+combined_p5)
gaincal(vis=combined_cont_p4+'.ms' , caltable=combined_p5, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='60s', minsnr=1.5, minblperant=4)
# too many solutions lost with solint=30

if not skip_plots:
    plotcal(caltable=combined_p5, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 
    plotcal(caltable=combined_p5, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs1_timerange)

applycal(vis=combined_cont_p4+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p5], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p5 = prefix+'_combined_contp5'
os.system('rm -rf %s*' % combined_cont_p5)
split(vis=combined_cont_p4+'.ms', outputvis=combined_cont_p5+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p5+'.ms' , imagename = combined_cont_p5, mask = common_mask, scales = LB_scales, threshold = '0.06mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p5+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#AS209_combined_contp5.image
#Beam 0.056 arcsec x 0.039 arcsec (-86.46 deg)
#Flux inside disk mask: 267.74 mJy
#Peak intensity of source: 2.52 mJy/beam
#rms: 1.18e-02 mJy/beam
#Peak SNR: 213.28

# no improvement. Stop at fourth phase selfcal and try amp self-cal
# amp self-cal does not improve image.

'''
combined_ap = prefix+'_combined.ap'
os.system('rm -rf '+combined_ap)
gaincal(vis=combined_cont_p4+'.ms' , caltable=combined_ap, gaintype='T', combine = 'spw,scan', spw=combined_contspws, refant=combined_refant, calmode='ap', solint='900s', minsnr=3.0, minblperant=4, solnorm = False)

plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 

applycal(vis=combined_cont_p4+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_ap], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_ap = prefix+'_combined_contap'
os.system('rm -rf %s*' % combined_cont_ap)
split(vis=combined_cont_p4+'.ms', outputvis=combined_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_ap+'.ms' , imagename = combined_cont_ap, mask = common_mask, scales = LB_scales, threshold = '0.06mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#AS209_combined_contap.image
#Beam 0.055 arcsec x 0.037 arcsec (89.88 deg)
#Flux inside disk mask: 267.95 mJy
#Peak intensity of source: 2.24 mJy/beam
#rms: 1.07e-02 mJy/beam
#Peak SNR: 208.14

# Does not improve image. 
'''

# Clean image with robust=0 and save image to FITS 
tclean_wrapper(vis = combined_cont_p4+'.ms' , imagename = combined_cont_p4+'_rob0', mask = common_mask, scales = LB_scales, robust=0.0, threshold = '0.06mJy')

exportfits(imagename=combined_cont_p4+'_rob0.image',fitsimage='AS209_script_image.fits')
