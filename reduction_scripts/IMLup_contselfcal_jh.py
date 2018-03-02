"""
This script was written for CASA 5.1.1

Datasets calibrated (in order of date observed): 
SB1: 2013.1.00226.S/im_lup_a_06_TE 
     PI: K. Oberg
     Observed 06 July 2014 (1 execution block)
     As delivered to PI
SB2: 2013.1.00226.S/im_lup_b_06_TE 
     Observed 17 July 2014 (1 execution block)
     PI: K. Oberg
     Downloaded from archive; see Huang et al. 2017 for additional comments on the reduction 
SB3: 2013.1.00694.S/IM_Lup_a_06_TC 
     PI: L.I. Cleeves
     Observed 29 January 2015 (1 execution block)
     Downloaded from archive and calibrated w/ pipeline
SB4: 2013.1.00694.S/IM_Lup_a_06_TE 
     PI: L.I. Cleeves 
     Observed 13 May 2015 (1 execution block)
     Downloaded from archive and calibrated w/ pipeline
SB5: 2013.1.00798.S/Im_Lup_a_06_TE 
     PI: C. Pinte
     Observed 9 June 2015 to 10 June 2015 (1 execution block)
     Downloaded from archive and calibrated w/ pipeline
LB1: 2016.1.00484.L/IM_Lupi_a_06_TM1 
     PI: S. Andrews
     Observed 25 September 2017 and 24 October 2017 (2 execution blocks)
     As delivered to PI

Incidentally, there are windows covering 13CS 5-4 in 2013.1.00798.S/Im_Lup_a_06_TE and 2013.1.00226.S/im_lup_a_06_TE
There's nothing obvious in either window, but if you're curious, you could consider combining them 

"""
import os

execfile('/pool/firebolt1/p484/reduction_scripts/reduction_utils.py')

skip_plots = True #if this is true, all of the plotting and inspection steps will be skipped and the script can be executed non-interactively in CASA if all relevant values have been hard-coded already 

#to fill this dictionary out, use listobs for the relevant measurement set 

prefix = 'IMLup' #string that identifies the source and is at the start of the name for all output files


#Note that if you downloaded data from the archive, your SPW numbering may differ from the SPWs in this script depending on how you split your data out!! 
data_params = {'SB1': {'vis' : '/data/astrochem1/jane/DeutChem/ImLup/deutcal/calibrated.ms',
                       'name' : 'SB1',
                       'field': 'im_lup',
                       'line_spws': np.array([11]), #SpwIDs of windows with lines that need to be flagged (this needs to be edited for each short baseline dataset)
                       'line_freqs': np.array([2.30538e11]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz)
                      }, #information about the short baseline measurement sets (SB1, SB2, SB3, etc in chronological order)
               'SB2': {'vis' : '/data/astrochem1/jane/DeutChem/ImLup/uid___A002_X86e521_X5ed.ms.split.cal',
                       'name' : 'SB2',
                       'field': 'im_lup',
                       'line_spws': np.array([]), 
                       'line_freqs': np.array([]),
                      }, 
               'SB3': {'vis' : '/data/sandrews/LP/archival/2013.1.00694.S/science_goal.uid___A001_X121_X2c7/group.uid___A001_X121_X2c8/member.uid___A001_X121_X2cb/calibrated/uid___A002_X9aa6ef_X12b7.ms.split.cal',
                       'name' : 'SB3',
                       'field': 'IM_Lup',
                       'line_spws': np.array([]), 
                       'line_freqs': np.array([]),
                      }, 
               'SB4': {'vis' : '/data/sandrews/LP/archival/2013.1.00694.S/science_goal.uid___A001_X121_X2c7/group.uid___A001_X121_X2c8/member.uid___A001_X121_X2c9/calibrated/uid___A002_Xa055bc_X1360.ms.split.cal',
                       'name' : 'SB4',
                       'field': 'IM_Lup',
                       'line_spws': np.array([]), 
                       'line_freqs': np.array([]),
                      }, 
               'SB5': {'vis' : '/data/sandrews/LP/archival/2013.1.00798.S/science_goal.uid___A001_X122_X5dc/group.uid___A001_X122_X5dd/member.uid___A001_X122_X5de/calibrated/uid___A002_Xa2ea64_Xa78.ms.split.cal',
                       'name' : 'SB5',
                       'field': 'Im_Lupi',
                       'line_spws': np.array([1]), 
                       'line_freqs': np.array([2.30538e11]),
                      }, 
               'LB1': {'vis' : '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X70/group.uid___A001_X8c5_X71/member.uid___A001_X8c5_X72/calibrated/calibrated_final.ms',
                       'name' : 'LB1',
                       'field' : 'IM_Lupi',
                       'line_spws': np.array([3,7]), #these are generally going to be the same for most of the long-baseline datasets. Some datasets only have one execution block or have strange numbering
                       'line_freqs': np.array([2.30538e11, 2.30538e11]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz) 
                      }  #information about the long baseline measurement sets
               }

"""
COMMENT ON PREPROCESSING STEPS HERE, e.g., use of initweights to fill out weight spectrum if necessary, or an amplitude rescaling based on corrections to the calibrator catalog 
"""

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

#Flagging atmospheric lines in SB3 and SB4
flagmanager(vis=data_params['SB3']['vis'], mode='save', versionname='init_cal_flags', comment = 'Flags after initial pipeline calibration')
flagdata(vis=data_params['SB3']['vis'],mode='manual', spw='3:83~84', field = data_params['SB3']['field'])

flagmanager(vis=data_params['SB4']['vis'], mode='save', versionname='init_cal_flags', comment = 'Flags after initial pipeline calibration')
flagdata(vis=data_params['SB4']['vis'],mode='manual', spw='2:42~45,3:76~87', field = data_params['SB4']['field'])


"""
Identify channels to flag based on the known velocity range of the line emission. The velocity range is based on line images from early reductions. If you are starting from scratch, 
you can estimate the range from the plotms command above. You may wish to limit your uvrange to 0~300 or so to only view the baselines with the highest amplitudes.     
"""
SB1_flagchannels = get_flagchannels(data_params['SB1'], prefix, velocity_range = np.array([-5,15]))
# Flagchannels input string for SB1: '11:433~685'

"""
Produces spectrally averaged continuum datasets
If you only want to include a subset of the windows, you can manually pass in values for contspw and width_array, e.g.
avg_cont(data_params[i], output_prefix, flagchannels = flagchannels_string, contspws = '0~2', width_array = [480,8,8]).
If you don't pass in values, all of the SPWs will be split out and the widths will be computed automatically to enforce a maximum channel width of 125 MHz.
WARNING: Only use the avg_cont function if the total bandwidth is recorded correctly in the original MS. There is sometimes a bug in CASA that records incorrect total bandwidths
"""
avg_cont(data_params['SB1'], prefix, flagchannels = SB1_flagchannels, contspws = '8~12', width_array = [960,960,960,960,960])
#Averaged continuum dataset saved to IMLup_SB1_initcont.ms

avg_cont(data_params['SB2'], prefix, flagchannels = SB2_flagchannels, contspws = '12~17', width_array = [1920, 1920, 960,960,960,960])
#Averaged continuum dataset saved to IMLup_SB2_initcont.ms

avg_cont(data_params['SB3'], prefix, contspws = '2~3', width_array = [8,8])
#Averaged continuum dataset saved to IMLup_SB3_initcont.ms

avg_cont(data_params['SB4'], prefix, contspws = '2~3', width_array = [8,8])
#Averaged continuum dataset saved to IMLup_SB4_initcont.ms

SB5_flagchannels = get_flagchannels(data_params['SB5'], prefix, velocity_range = np.array([-5,15]))
# Flagchannels input string for SB5: '1:693~1197'
avg_cont(data_params['SB5'], prefix, flagchannels = SB5_flagchannels, contspws = '0~2', width_array = [1920,1920,8])

LB1_flagchannels = get_flagchannels(data_params['LB1'], prefix, velocity_range = np.array([-5,15]))
# Flagchannels input string for LB1: '3:1890~1953, 7:1890~1953'
avg_cont(data_params['LB1'], prefix, flagchannels = LB1_flagchannels)
#Averaged continuum dataset saved to IMLup_LB1_initcont.ms

# sample command to check that amplitude vs. uvdist looks normal
# plotms(vis=prefix+'_SB1_initcont.ms', xaxis='uvdist', yaxis='amp', coloraxis='spw', avgtime='30', avgchannel='16')

# flagging data with anomalous amplitudes in SB2
flagmanager(vis = 'IMLup_SB2_initcont.ms', mode = 'save', versionname = 'initial_averaging', comment = 'Flagging anomalous amplitudes from uvdist plot') 
flagdata(vis= 'IMLup_SB2_initcont.ms', mode='manual', antenna = 'PM03, DV14, DA47, DV15, DA64')

"""
Quick imaging of every execution block in the measurement set using tclean. 
The threshold, scales, and mask should be adjusted for each source.
In this case, we picked our threshold, scales, and mask from previous reductions of the data. You may wish to experiment with these values when imaging. 
The threshold is ~3-4x the rms, the mask is an ellipse that covers all the emission and has roughly the same geometry, and we choose 4 to 6 scales such that the first scale is 0 (a point), and the largest is ~half the major axis of the mask.
The mask angle and the semimajor and semiminor axes should be the same for all imaging. The center is not necessarily fixed because of potential misalignments between observations. 
"""
mask_angle = 145 #position angle of mask in degrees
mask_semimajor = 2.75 #semimajor axis of mask in arcsec
mask_semiminor = 1.75 #semiminor axis of mask in arcsec

SB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % ('15h56m09.20s', '-37.56.06.42', mask_semimajor, mask_semiminor, mask_angle)

LB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % ('15h46m44.71s', '-34.30.36.09', mask_semimajor, mask_semiminor, mask_angle)

SB_scales = [0, 15, 30, 45,75]
LB_scales = [0, 10, 50, 150, 300, 450]
"""
In this section, we are imaging every execution block to check spatial alignment 
"""

if not skip_plots:

    tclean_wrapper(vis = prefix+'_SB1_initcont.ms', imagename = prefix+'_SB1_initcont', mask = SB1_mask, scales = SB_scales, threshold = '1.5mJy', interactive = False)
    tclean_wrapper(vis = prefix+'_SB2_initcont.ms', imagename = prefix+'_SB2_initcont', mask = SB1_mask, scales = SB_scales, threshold = '1.5mJy', interactive = False)
    tclean_wrapper(vis = prefix+'_SB3_initcont.ms', imagename = prefix+'_SB3_initcont', mask = SB1_mask, scales = SB_scales, threshold = '2.0mJy', interactive = False)
    tclean_wrapper(vis = prefix+'_SB4_initcont.ms', imagename = prefix+'_SB4_initcont', mask = SB1_mask, scales = SB_scales, threshold = '1.0mJy', interactive = False)
    tclean_wrapper(vis = prefix+'_SB5_initcont.ms', imagename = prefix+'_SB5_initcont', mask = SB1_mask, scales = SB_scales, threshold = '1.0mJy', interactive = False)

    # inspection of images do not reveal additional bright background sources 

    image_each_obs(data_params['LB1'], prefix, mask = LB1_mask, scales = LB_scales, threshold = '0.1mJy', interactive = False)

    """
    Since the source looks centrally peaked, we will fit a Gaussian to the disk to estimate the location of the peak in each image and record the output.
    We are also very roughly estimating the PA and inclination for checking the flux scale offsets later (these are NOT the position angles and inclinations used for analysis of the final image products.
    Here, we are using the CLEAN mask to restrict the region over which the fit is occurring, but you may wish to shrink the region even further if your disk structure is complex 
    """

    fit_gaussian(prefix+'_SB1_initcont.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: J2000 15h56m09.192086s -37d56m06.44353s

    fit_gaussian(prefix+'_SB2_initcont.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: J2000 15h56m09.192004s -37d56m06.48109s

    fit_gaussian(prefix+'_SB3_initcont.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: J2000 15h56m09.193928s -37d56m06.43980s

    fit_gaussian(prefix+'_SB4_initcont.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: J2000 15h56m09.190358s -37d56m06.47500s

    fit_gaussian(prefix+'_SB5_initcont.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: J2000 15h56m09.188402s -37d56m06.50811s

    fit_gaussian(prefix+'_LB1_initcont_exec0.image', region = 'circle[[%s, %s], %.1farcsec]' % ('15h56m09.19s', '-37.56.06.53', 0.2), dooff = True) #shrinking the fit region to avoid the spiral arms
    #Peak of Gaussian component identified with imfit: ICRS 15h56m09.188385s -37d56m06.54177s
    #Peak in J2000 coordinates: 15:56:09.18880, -037:56:06.527374
    #PA of Gaussian component: 143.39 deg
    #Inclination of Gaussian component: 47.57 deg



    fit_gaussian(prefix+'_LB1_initcont_exec1.image', region = 'circle[[%s, %s], %.1farcsec]' % ('15h56m09.19s', '-37.56.06.53', 0.2), dooff = True)
    #Peak of Gaussian component identified with imfit: ICRS 15h56m09.188671s -37d56m06.54163s
    #Peak in J2000 coordinates: 15:56:09.18909, -037:56:06.527233

"""
Since the individual execution blocks appear to be slightly misaligned, 
we will be splitting out the individual execution blocks, 
shifting them so that the image peaks fall on the phase center, 
reassigning the phase centers to a common direction (for ease of concat)
and imaging to check the shift  
"""

split_all_obs(prefix+'_LB1_initcont.ms', prefix+'_LB1_initcont_exec')


common_dir = 'J2000 15h56m09.18880s -037.56.06.527374' #choose peak of first execution of LB1 to be the common direction (the better-quality of the high-res observations)  

#need to change to J2000 coordinates
mask_ra = '15h56m09.18880s'
mask_dec = '-37.56.06.527374'
common_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % (mask_ra, mask_dec, mask_semimajor, mask_semiminor, mask_angle)

shiftname = prefix+'_SB1_initcont_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_SB1_initcont.ms', outputvis=shiftname+'.ms', field = data_params['SB1']['field'], phasecenter='J2000 15h56m09.192086s -37d56m06.44353s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['SB1']['field'], direction = common_dir) #fixplanets works only with J2000, not ICRS
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = SB_scales, threshold = '1.5mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 15h56m09.188802s -37d56m06.52731s

shiftname = prefix+'_SB2_initcont_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_SB2_initcont.ms', outputvis=shiftname+'.ms', field = data_params['SB2']['field'], phasecenter='J2000 15h56m09.192004s -37d56m06.48109s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['SB2']['field'], direction = common_dir) #fixplanets works only with J2000, not ICRS
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = SB_scales, threshold = '1.5mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 15h56m09.188802s -37d56m06.52726s

shiftname = prefix+'_SB3_initcont_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_SB3_initcont.ms', outputvis=shiftname+'.ms', field = data_params['SB3']['field'], phasecenter='J2000 15h56m09.193928s -37d56m06.43980s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['SB3']['field'], direction = common_dir) #fixplanets works only with J2000, not ICRS
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = SB_scales, threshold = '2.0mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 15h56m09.188792s -37d56m06.52757s

shiftname = prefix+'_SB4_initcont_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_SB4_initcont.ms', outputvis=shiftname+'.ms', field = data_params['SB4']['field'], phasecenter='J2000 15h56m09.190358s -37d56m06.47500s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['SB4']['field'], direction = common_dir) #fixplanets works only with J2000, not ICRS
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = SB_scales, threshold = '1.0mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 15h56m09.188802s -37d56m06.52737s

shiftname = prefix+'_SB5_initcont_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_SB5_initcont.ms', outputvis=shiftname+'.ms', field = data_params['SB5']['field'], phasecenter='J2000 15h56m09.188402s -37d56m06.50811s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['SB5']['field'], direction = common_dir) #fixplanets works only with J2000, not ICRS
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = SB_scales, threshold = '1.0mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 15h56m09.188806s -37d56m06.52753s

shiftname = prefix+'_LB1_initcont_exec0_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_LB1_initcont_exec0.ms', outputvis=shiftname+'.ms', field = data_params['LB1']['field'], phasecenter='ICRS 15h56m09.188385s -37d56m06.54177s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['LB1']['field'], direction = common_dir)
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = LB_scales, threshold = '0.06mJy')
fit_gaussian(shiftname+'.image', region =  'circle[[%s, %s], %.1farcsec]' % ('15h56m09.188806s', '-37.56.06.52753', 0.2))
#Peak of Gaussian component identified with imfit: J2000 15h56m09.188823s -37d56m06.52758s

shiftname = prefix+'_LB1_initcont_exec1_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_LB1_initcont_exec1.ms', outputvis=shiftname+'.ms', field = data_params['LB1']['field'], phasecenter= 'ICRS 15h56m09.188671s -37d56m06.54163s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['LB1']['field'], direction = common_dir)
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = LB_scales, threshold = '0.1mJy')
fit_gaussian(shiftname+'.image', region = 'circle[[%s, %s], %.1farcsec]' % ('15h56m09.188806s', '-37.56.06.52753', 0.2))
#Peak of Gaussian component identified with imfit: J2000 15h56m09.188853s -37d56m06.52819s

"""
After aligning the images, we want to check if the flux scales seem consistent between execution blocks (within ~5%)
First, we check the uid___xxxxx.casa_commands.log in the log directory of the data products folder (or the calibration script in the manual case) to check whether the calibrator catalog matches up with the input flux density values for the calibrators
(You should also check the plots of the calibrators in the data products to make sure that the amplitudes look consistent with the models that were inserted)
"""

#SB1, SB2, SB3, SB4, and SB5 used Titan (Butler-JPL-Horizons 2012 model) as a flux calibrator

#LB1, first execution
au.getALMAFlux('J1517-2422', frequency = '232.581GHz', date = '2017/09/25')
"""
Closest Band 3 measurement: 2.770 +- 0.050 (age=-7 days) 103.5 GHz
Closest Band 3 measurement: 2.790 +- 0.040 (age=-7 days) 91.5 GHz
Closest Band 7 measurement: 1.770 +- 0.040 (age=+2 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -7 days from 2017/09/25, with age separation of 0 days
  2017/10/02: freqs=[103.49, 91.46, 343.48], fluxes=[2.77, 2.79, 1.92]
/data/astrochem1/jane/casa-release-5.1.1-5.el6/lib/python2.7/site-packages/matplotlib/collections.py:446: FutureWarning: elementwise comparison failed; returning scalar instead, but in the future will perform elementwise comparison
  if self._edgecolors == 'face':
Median Monte-Carlo result for 232.581000 = 2.169045 +- 0.176468 (scaled MAD = 0.173994)
Result using spectral index of -0.279723 for 232.581 GHz from 2.770 Jy at 103.490 GHz = 2.208554 +- 0.176468 Jy

Pipeline command:
setjy(fluxdensity=[2.1797, 0.0, 0.0, 0.0], scalebychan=True,
      vis='uid___A002_Xc4d618_X185.ms', spix=-0.279722838503, spw='19',
      field='J1517-2422', reffreq='TOPO 232.581GHz',
      intent='CALIBRATE_FLUX#ON_SOURCE', selectdata=True, standard='manual',
      usescratch=True)

Calibration is consistent with catalog
"""

#LB1, second execution 
au.getALMAFlux('J1427-4206', frequency = '232.589GHz', date = '2017/10/24')
"""
Closest Band 3 measurement: 4.190 +- 0.100 (age=-2 days) 91.5 GHz
Closest Band 7 measurement: 1.980 +- 0.060 (age=+3 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 3 days from 2017/10/24, with age separation of 0 days
  2017/10/21: freqs=[91.46, 103.49, 343.48], fluxes=[3.71, 3.44, 1.98]
Median Monte-Carlo result for 232.589000 = 2.371797 +- 0.116707 (scaled MAD = 0.115788)
Result using spectral index of -0.467361 for 232.589 GHz from 4.190 Jy at 91.460 GHz = 2.708729 +- 0.116707 Jy


Pipeline command:
setjy(fluxdensity=[2.7087, 0.0, 0.0, 0.0], scalebychan=True,
      vis='uid___A002_Xc5fe11_X5761.ms', spix=-0.467361059423, spw='19',
      field='J1427-4206', reffreq='TOPO 232.589GHz',
      intent='CALIBRATE_FLUX#ON_SOURCE', selectdata=True, standard='manual',
      usescratch=True)

Calibration is consistent with catalog
"""
#these are the rough values pulled from Gaussian fitting of LB1 and used for initial deprojection. They are NOT the final values used for subsequent data analysis. They are consistent with the IM Lup values estimated in Cleeves et al. 2017
PA =  144 
incl = 48

if not skip_plots:
    for msfile in [prefix+'_SB1_initcont_shift.ms', prefix+'_SB2_initcont_shift.ms',prefix+'_SB3_initcont_shift.ms',prefix+'_SB4_initcont_shift.ms',prefix+'_SB5_initcont_shift.ms', prefix+'_LB1_initcont_exec0_shift.ms', prefix+'_LB1_initcont_exec1_shift.ms']:
        export_MS(msfile)
    #Measurement set exported to IMLup_SB1_initcont_shift.vis.npz
    #Measurement set exported to IMLup_SB2_initcont_shift.vis.npz
    #Measurement set exported to IMLup_SB3_initcont_shift.vis.npz
    #Measurement set exported to IMLup_SB4_initcont_shift.vis.npz
    #Measurement set exported to IMLup_SB5_initcont_shift.vis.npz
    #Measurement set exported to IMLup_LB1_initcont_exec0_shift.vis.npz
    #Measurement set exported to IMLup_LB1_initcont_exec1_shift.vis.npz


    #plot deprojected visibility profiles of all the execution blocks
    plot_deprojected([prefix+'_SB1_initcont_shift.vis.npz', prefix+'_SB2_initcont_shift.vis.npz',prefix+'_SB3_initcont_shift.vis.npz',prefix+'_SB4_initcont_shift.vis.npz',prefix+'_SB5_initcont_shift.vis.npz', prefix+'_LB1_initcont_exec0_shift.vis.npz', prefix+'_LB1_initcont_exec1_shift.vis.npz'],
                 PA = PA, incl = incl)

    
 
    #The second execution of LB1 is noticeably lower than all the other observations
    #The other observations are reasonably similar to one another, given that they're at slightly different frequencies 

    estimate_flux_scale(reference = prefix+'_LB1_initcont_exec0_shift.vis.npz', comparison = prefix+'_LB1_initcont_exec1_shift.vis.npz', incl = incl, PA = PA, uvbins = 100+10*np.arange(100))

    #The ratio of the fluxes of IMLup_LB1_initcont_exec1_shift.vis.npz to IMLup_LB1_initcont_exec0_shift.vis.npz is 0.79486
    #The scaling factor for gencal is 0.892 for your comparison measurement
    #The error on the weighted mean ratio is 9.216e-04, although it's likely that the weights in the measurement sets are too low by a constant factor



    #We replot the deprojected visibilities with rescaled factors to check that the values make sense
    plot_deprojected([prefix+'_LB1_initcont_exec0_shift.vis.npz', prefix+'_LB1_initcont_exec1_shift.vis.npz'], PA = PA, incl = incl, fluxscale = [1, 1/.8])

#now correct the flux of the discrepant dataset
rescale_flux(prefix+'_LB1_initcont_exec1_shift.ms', [0.892])
#Splitting out rescaled values into new MS: IMLup_LB1_initcont_exec1_shift_rescaled.ms

"""
Start of self-calibration of the short-baseline data 
"""
#merge the short-baseline execution blocks into a single MS
SB_cont_p0 = prefix+'_SB_contp0'
os.system('rm -rf %s*' % SB_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [prefix+'_SB1_initcont_shift.ms', prefix+'_SB2_initcont_shift.ms',prefix+'_SB3_initcont_shift.ms',prefix+'_SB4_initcont_shift.ms',prefix+'_SB5_initcont_shift.ms'], concatvis = SB_cont_p0+'.ms', dirtol = '0.1arcsec', copypointing = False) 

#make initial image
tclean_wrapper(vis = SB_cont_p0+'.ms', imagename = SB_cont_p0, mask = common_mask, scales = SB_scales, threshold = '0.6mJy', savemodel = 'modelcolumn')

noise_annulus ="annulus[[%s, %s],['%.2farcsec', '5.75arcsec']]" % (mask_ra, mask_dec, 1.1*mask_semimajor) #annulus over which we measure the noise. The inner radius is slightly larger than the semimajor axis of the mask (to add some buffer space around the mask) and the outer radius is set so that the annulus fits inside the long-baseline image size 
estimate_SNR(SB_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#IMLup_SB_contp0.image
#Beam 0.616 arcsec x 0.409 arcsec (-82.55 deg)
#Flux inside disk mask: 246.26 mJy
#Peak intensity of source: 68.66 mJy/beam
#rms: 1.88e-01 mJy/beam
#Peak SNR: 364.40

"""
We need to select one or more reference antennae for gaincal

We first look at the CASA command log (or manual calibration script) to see how the reference antennae choices were ranked (weighted toward antennae close to the center of the array and with good SNR)
Note that gaincal will sometimes choose a different reference antenna than the one specified if it deems another one to be a better choice 

SB1: DA48 (manually calibrated) 
SB2: DA48 (manually calibrated)
SB3: DA63,DA54,DA52,DV16,DA59
SB4: DA52,DA60,DA59,DA62,DV20
SB5: DA59,DA52,DV08,DA49,DA57

First execution of LB1: DV24,DA61,DV09,DA57,DA47
Second execution of LB1: DA61,DV09,DV25,DV06,DA45


If you want to double check whether the antenna locations are reasonable, you can use something like plotants(vis = SB_cont_p0+'.ms')

"""

get_station_numbers(SB_cont_p0+'.ms', 'DA48')
#Observation ID 0: DA48@A046
#Observation ID 1: DA48@A046
#Observation ID 2: DA48@A043
get_station_numbers(SB_cont_p0+'.ms', 'DA63')
#Observation ID 1: DA63@A019
#Observation ID 2: DA63@A018
#Observation ID 3: DA63@A073
#Observation ID 4: DA63@A073

#DA59 has phases that jump up during a scan for SB4, so we'll try DA52 instead
get_station_numbers(SB_cont_p0+'.ms', 'DA52')
#Observation ID 2: DA52@A035
#Observation ID 3: DA52@A035
#Observation ID 4: DA52@A035

SB_contspws = '0~17' #change as appropriate
SB_refant = 'DA48@A046,DA63@A073, DA52@A035'
SB_obs0_timerange = '2014/07/06/00:00:01~2014/07/06/23:59:59' #change timerange as appropriate
SB_obs1_timerange = '2014/07/17/00:00:01~2014/07/17/23:59:59'
SB_obs2_timerange = '2015/01/29/00:00:01~2015/01/29/23:59:59'
SB_obs3_timerange = '2015/05/13/00:00:01~2015/05/13/23:59:59'
SB_obs4_timerange = '2015/06/09/00:00:01~2015/06/10/23:59:59'
 

# It's useful to check that the phases for the refant look good in all execution blocks in plotms. However, plotms has a tendency to crash in CASA 5.1.1, so it might be necessary to use plotms in an older version of CASA 
#plotms(vis=SB_cont_p0, xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '0')
#plotms(vis=SB_cont_p0, xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '1')

#first round of phase self-cal for short baseline data
SB_p1 = prefix+'_SB.p1'
os.system('rm -rf '+SB_p1)
gaincal(vis=SB_cont_p0+'.ms' , caltable=SB_p1, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='p', solint='60s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [120s, 60s, 30s, 18s, 6s]

if not skip_plots:
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB_obs0_timerange) 
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB_obs1_timerange)
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB_obs2_timerange)
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB_obs3_timerange)
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB_obs4_timerange)

applycal(vis=SB_cont_p0+'.ms', spw=SB_contspws, gaintable=[SB_p1], interp = 'linearPD', calwt = True)

SB_cont_p1 = prefix+'_SB_contp1'
os.system('rm -rf %s*' % SB_cont_p1)
split(vis=SB_cont_p0+'.ms', outputvis=SB_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p1+'.ms' , imagename = SB_cont_p1, mask = common_mask, scales = SB_scales, threshold = '0.15mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#IMLup_SB_contp1.image
#Beam 0.615 arcsec x 0.410 arcsec (-82.50 deg)
#Flux inside disk mask: 253.06 mJy
#Peak intensity of source: 72.62 mJy/beam
#rms: 5.42e-02 mJy/beam
#Peak SNR: 1339.53



#second round of phase self-cal for short baseline data
SB_p2 = prefix+'_SB.p2'
os.system('rm -rf '+SB_p2)
gaincal(vis=SB_cont_p1+'.ms' , caltable=SB_p2, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='p', solint='30s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB_obs0_timerange) 
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB_obs1_timerange)
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB_obs2_timerange)
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB_obs3_timerange)
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB_obs4_timerange)

applycal(vis=SB_cont_p1+'.ms', spw=SB_contspws, gaintable=[SB_p2], interp = 'linearPD', calwt = True)

SB_cont_p2 = prefix+'_SB_contp2'
os.system('rm -rf %s*' % SB_cont_p2)
split(vis=SB_cont_p1+'.ms', outputvis=SB_cont_p2+'.ms', datacolumn='corrected')


tclean_wrapper(vis = SB_cont_p2+'.ms' , imagename = SB_cont_p2, mask = common_mask, scales = SB_scales, threshold = '0.15mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)

#IMLup_SB_contp2.image
#Beam 0.615 arcsec x 0.410 arcsec (-82.53 deg)
#Flux inside disk mask: 253.30 mJy
#Peak intensity of source: 72.94 mJy/beam
#rms: 5.38e-02 mJy/beam
#Peak SNR: 1356.49

SB_p3 = prefix+'_SB.p3'
os.system('rm -rf '+SB_p3)
gaincal(vis=SB_cont_p2+'.ms' , caltable=SB_p3, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='p', solint='18s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=SB_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB_obs0_timerange) 
    plotcal(caltable=SB_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB_obs1_timerange)
    plotcal(caltable=SB_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB_obs2_timerange)
    plotcal(caltable=SB_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB_obs3_timerange)
    plotcal(caltable=SB_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB_obs4_timerange)

applycal(vis=SB_cont_p2+'.ms', spw=SB_contspws, gaintable=[SB_p3], interp = 'linearPD', calwt = True)


SB_cont_p3 = prefix+'_SB_contp3'
os.system('rm -rf %s*' % SB_cont_p3)
split(vis=SB_cont_p2+'.ms', outputvis=SB_cont_p3+'.ms', datacolumn='corrected')


tclean_wrapper(vis = SB_cont_p3+'.ms' , imagename = SB_cont_p3, mask = common_mask, scales = SB_scales, threshold = '0.15mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_p3+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#IMLup_SB_contp3.image
#Beam 0.615 arcsec x 0.410 arcsec (-82.53 deg)
#Flux inside disk mask: 253.53 mJy
#Peak intensity of source: 73.14 mJy/beam
#rms: 5.37e-02 mJy/beam
#Peak SNR: 1362.31

#improvement over previous round of phase self-cal is marginal, so we move on to amp self-cal for the short baseline data 
SB_ap = prefix+'_SB.ap'
os.system('rm -rf '+SB_ap)
#note that the solint and minsnr are larger for amp self-cal
#try solnorm = False first. If that leads to bad solutions, try solnorm = True. If that still doesn't help, then just skip amp self-cal
gaincal(vis=SB_cont_p3+'.ms' , caltable=SB_ap, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='ap', solint='inf', minsnr=3.0, minblperant=4, solnorm = False) 

if not skip_plots:
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB_obs0_timerange) 
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB_obs1_timerange)
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB_obs2_timerange)
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB_obs3_timerange)
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB_obs4_timerange)

applycal(vis=SB_cont_p3+'.ms', spw=SB_contspws, gaintable=[SB_ap], interp = 'linearPD', calwt = True)

SB_cont_ap = prefix+'_SB_contap'
os.system('rm -rf %s*' % SB_cont_ap)
split(vis=SB_cont_p3+'.ms', outputvis=SB_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_ap+'.ms' , imagename = SB_cont_ap, mask = common_mask, scales = SB_scales, threshold = '0.15mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#IMLup_SB_contap.image
#Beam 0.614 arcsec x 0.413 arcsec (-82.51 deg)
#Flux inside disk mask: 252.49 mJy
#Peak intensity of source: 73.72 mJy/beam
#rms: 3.81e-02 mJy/beam
#Peak SNR: 1935.89

#now we concatenate all the data together

combined_cont_p0 = prefix+'_combined_contp0'
os.system('rm -rf %s*' % combined_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [SB_cont_ap+'.ms', prefix+'_LB1_initcont_exec0_shift.ms', prefix+'_LB1_initcont_exec1_shift_rescaled.ms'], concatvis = combined_cont_p0+'.ms' , dirtol = '0.1arcsec', copypointing = False) 

tclean_wrapper(vis = combined_cont_p0+'.ms' , imagename = combined_cont_p0, mask = common_mask, scales = LB_scales, threshold = '0.06mJy', imsize = 4000, savemodel = 'modelcolumn')

estimate_SNR(combined_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#IMLup_combined_contp0.image
#Beam 0.033 arcsec x 0.026 arcsec (47.52 deg)
#Flux inside disk mask: 254.24 mJy
#Peak intensity of source: 3.45 mJy/beam
#rms: 1.43e-02 mJy/beam
#Peak SNR: 241.88

#checking station numbers for potential long-baseline observation refants
get_station_numbers(combined_cont_p0+'.ms', 'DA61')
#Observation ID 1: DA61@A075
#Observation ID 2: DA61@A075
#Observation ID 3: DA61@A075
#Observation ID 4: DA61@A075
#Observation ID 5: DA61@A015
#Observation ID 6: DA61@A015

combined_refant = 'DA61@A015, DA48@A046,DA63@A073, DA52@A035'
combined_contspws = '0~24'
combined_spwmap =  [0,0,0,0,0,5,5,5,5,5,5,11,11,13,13,15,15,15,18,18,18,18,22,22,22,22] #note that the tables produced by gaincal in 5.1.1 have spectral windows numbered differently if you use the combine = 'spw' option. Previously, all of the solutions would be written to spectral window 0. Now, they are written to the first window in each execution block. So, the spwmap argument has to correspond to the first window in each execution block you want to calibrate. 

LB1_obs0_timerange = '2017/09/25/00:00:01~2017/09/25/23:59:59'
LB2_obs0_timerange = '2017/10/24/00:00:01~2017/10/24/23:59:59'

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

tclean_wrapper(vis = combined_cont_p1+'.ms' , imagename = combined_cont_p1, mask = common_mask, scales = LB_scales, threshold = '0.06mJy', imsize = 4000, savemodel = 'modelcolumn')

estimate_SNR(combined_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)

