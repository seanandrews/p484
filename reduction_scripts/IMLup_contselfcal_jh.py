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

shiftname = prefix+'_LB1_initcont_exec1_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_LB1_initcont_exec1.ms', outputvis=shiftname+'.ms', field = data_params['LB1']['field'], phasecenter= 'ICRS 15h56m09.188671s -37d56m06.54163s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['LB1']['field'], direction = common_dir)
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = LB_scales, threshold = '0.1mJy')
fit_gaussian(shiftname+'.image', region = ('15h56m09.188806s', '-37.56.06.52753', 0.2))

