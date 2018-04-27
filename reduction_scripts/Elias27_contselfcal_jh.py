"""
This script was written for CASA 5.1.1

Datasets calibrated (in order of date observed):
SB1: 2013.1.00498.L/Elias_24_a_06_TM1  
     Observed 21 July 2015 (1 execution block)
     PI: L. Perez
     Downloaded from archive and calibrated with archival scripts
LB1: 2016.1.00484.L/Elias_27_a_06_TM1 
     Observed 07 September 2017 and 3 October 2017 (2 execution blocks)
     PI: S. Andrews
     As delivered to PI

"""
import os

execfile('/pool/firebolt1/p484/reduction_scripts/reduction_utils.py')

skip_plots = False #if this is true, all of the plotting and inspection steps will be skipped and the script can be executed non-interactively in CASA if all relevant values have been hard-coded already 

#to fill this dictionary out, use listobs for the relevant measurement set 

prefix = 'Elias27' #string that identifies the source and is at the start of the name for all output files

#Note that if you are downloading data from the archive, your SPW numbering may differ from the SPWs in this script depending on how you split your data out!! 
data_params = {'SB1': {'vis' : '/data/sandrews/LP/archival/2013.1.00498.S/science_goal.uid___A001_X13a_Xeb/group.uid___A001_X13a_Xec/member.uid___A001_X13a_Xed/calibrated/uid___A002_Xa657ad_X736.ms.split.cal',
                       'name' : 'SB1',
                       'field': 'Elia_2-27',
                       'line_spws': np.array([1,5,6]), #SpwIDs of windows with lines that need to be flagged (this needs to be edited for each short baseline dataset)
                       'line_freqs': np.array([2.30538e11, 2.2039868420e11, 2.1956035410e11]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz)
                      }, #information about the short baseline measurement sets (SB1, SB2, SB3, etc in chronological order)
               'LB1': {'vis' : '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X50/group.uid___A001_X8c5_X51/member.uid___A001_X8c5_X52/calibrated/calibrated_final.ms',
                       'name' : 'LB1',
                       'field' : 'Elias_27',
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

for i in data_params.keys():      
    """
    Identify channels to flag based on the known velocity range of the line emission. The velocity range is based on line images from early reductions. If you are starting from scratch, 
    you can estimate the range from the plotms command above. You may wish to limit your uvrange to 0~300 or so to only view the baselines with the highest amplitudes.     
    """
    flagchannels_string = get_flagchannels(data_params[i], prefix, velocity_range = np.array([-5, 10]))
    """
    Produces spectrally averaged continuum datasets
    If you only want to include a subset of the windows, you can manually pass in values for contspw and width_array, e.g.
    avg_cont(data_params[i], output_prefix, flagchannels = flagchannels_string, contspws = '0~2', width_array = [480,8,8]).
    If you don't pass in values, all of the SPWs will be split out and the widths will be computed automatically to enforce a maximum channel width of 125 MHz.
    WARNING: Only use the avg_cont function if the total bandwidth is recorded correctly in the original MS. There is sometimes a bug in CASA that records incorrect total bandwidths
    """
    # Flagchannels input string for SB1: '1:167~215, 5:49~72, 6:806~829'
    #Averaged continuum dataset saved to Elias27_SB1_initcont.ms
    # Flagchannels input string for LB1: '3:1890~1937, 7:1890~1937'
    #Averaged continuum dataset saved to Elias27_LB1_initcont.ms
    avg_cont(data_params[i], prefix, flagchannels = flagchannels_string)

# sample command to check that amplitude vs. uvdist looks normal
# plotms(vis=prefix+'_SB1_initcont.ms', xaxis='uvdist', yaxis='amp', coloraxis='spw', avgtime='30', avgchannel='16')

flagdata(vis  = "/data/sandrews/LP/archival/2013.1.00498.S/science_goal.uid___A001_X13a_Xeb/group.uid___A001_X13a_Xec/member.uid___A001_X13a_Xed/calibrated/uid___A002_Xa657ad_X736.ms.split.cal", spw = '1:167~215, 5:49~72, 6:806~829', field = 'Elia_2-27')

# Some additional flagging
flagmanager(vis=prefix+'_SB1_initcont.ms', mode='save', versionname='init_cal_flags', comment='Flag states immediately after initial calibration')
flagdata(vis=prefix+'_SB1_initcont.ms', mode='manual', spw='1,3,5', flagbackup=False, field=data_params['SB1']['field'], scan='32', antenna='DA46')
flagdata(vis=prefix+'_SB1_initcont.ms', mode='manual', spw='3,4,6', flagbackup=False, field=data_params['SB1']['field'], scan='18,32,37', antenna='DA59')
flagdata(vis=prefix+'_SB1_initcont.ms', mode='manual', spw='3,4', flagbackup=False, field=data_params['SB1']['field'], scan='13,18', antenna='DV06')
flagdata(vis=prefix+'_SB1_initcont.ms', mode='manual', spw='3,4', flagbackup=False, field=data_params['SB1']['field'], scan='32', antenna='DV08')
flagdata(vis=prefix+'_SB1_initcont.ms', mode='manual', spw='3', flagbackup=False, field=data_params['SB1']['field'], scan='32,37', antenna='DV18')


"""
Quick imaging of every execution block in the measurement set using tclean. 
The threshold, scales, and mask should be adjusted for each source.
In this case, we picked our threshold, scales, and mask from previous reductions of the data. You may wish to experiment with these values when imaging. 
The threshold is ~3-4x the rms, the mask is an ellipse that covers all the emission and has roughly the same geometry, and we choose 4 to 6 scales such that the first scale is 0 (a point), and the largest is ~half the major axis of the mask.
The mask angle and the semimajor and semiminor axes should be the same for all imaging. The center is not necessarily fixed because of potential misalignments between observations. 
"""
mask_angle = 118 #position angle of mask in degrees
mask_semimajor = 2.5 #semimajor axis of mask in arcsec
mask_semiminor = 1.5 #semiminor axis of mask in arcsec

SB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % ('16h26m45.027s', '-24.23.08.28', mask_semimajor, mask_semiminor, mask_angle)
LB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % ('16h26m45.027s', '-24.23.08.28', mask_semimajor, mask_semiminor, mask_angle)

SB_scales = [0, 5, 10, 25, 50]
LB_scales = [0, 10, 30, 100, 200]
"""
In this section, we are imaging every execution block to check spatial alignment 
"""

if not skip_plots:
    #images are saved in the format prefix+'_name_initcont_exec#.ms'
    image_each_obs(data_params['SB1'], prefix, mask = SB1_mask, scales = SB_scales, threshold = '0.2mJy', interactive = False)
    # inspection of images do not reveal additional bright background sources 

    image_each_obs(data_params['LB1'], prefix, mask = LB1_mask, scales = LB_scales, threshold = '0.08mJy', interactive = False)

    """
    Since the source looks axisymmetric, we will fit a Gaussian to the disk to estimate the location of the peak in each image and record the output.
    We are also very roughly estimating the PA and inclination for checking the flux scale offsets later (these are NOT the position angles and inclinations used for analysis of the final image products).
    Here, we are using the CLEAN mask to restrict the region over which the fit is occurring, but you may wish to shrink the region even further if your disk structure is complex 
    """
    fit_gaussian(prefix+'_SB1_initcont_exec0.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: J2000 16h26m45.021955s -24d23m08.25057s
    #PA of Gaussian component: 121.00 deg
    #Inclination of Gaussian component: 49.72 deg
    #Pixel coordinates of peak: x = 451.368 y = 433.301

    fit_gaussian(prefix+'_LB1_initcont_exec0.image', region = 'circle[[%s, %s], %.1farcsec]' % ('16h26m45.027s', '-24.23.08.28', 0.3),  dooff = True)
    #Peak of Gaussian component identified with imfit: ICRS 16h26m45.021236s -24d23m08.28546s
    #Peak in J2000 coordinates: 16:26:45.02183, -024:23:08.272621 
    #PA of Gaussian component: 120.58 deg
    #Inclination of Gaussian component: 56.86 deg
    #Pixel coordinates of peak: x = 1517.141 y = 1321.512


    fit_gaussian(prefix+'_LB1_initcont_exec1.image', region = 'circle[[%s, %s], %.1farcsec]' % ('16h26m45.027s', '-24.23.08.28', 0.3),  dooff = True)
    #Peak of Gaussian component identified with imfit: ICRS 16h26m45.021274s -24d23m08.28782s
    #Peak in J2000 coordinates: 16:26:45.02187, -024:23:08.274981
    #PA of Gaussian component: 121.02 deg
    #Inclination of Gaussian component: 59.04 deg
    #Pixel coordinates of peak: x = 1516.969 y = 1320.727



common_dir = 'J2000 16h26m45.022s -024.23.08.273' #choose peak of LB1 to be the common direction    

#need to change to J2000 coordinates
mask_ra = '16h26m45.022s'
mask_dec = '-024.23.08.2733'
common_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % (mask_ra, mask_dec, mask_semimajor, mask_semiminor, mask_angle)

shiftname = prefix+'_SB1_initcont_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_SB1_initcont.ms', outputvis=shiftname+'.ms', field = data_params['SB1']['field'], phasecenter='J2000 16h26m45.021955s -24d23m08.25057s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['SB1']['field'], direction = common_dir) #fixplanets works only with J2000, not ICRS
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = SB_scales, threshold = '0.2mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 16h26m45.021997s -24d23m08.27297s

shiftname = prefix+'_LB1_initcont_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_LB1_initcont.ms', outputvis=shiftname+'.ms', field = data_params['LB1']['field'], phasecenter='ICRS 16h26m45.021309s -24d23m08.28623s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['LB1']['field'], direction = common_dir)
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = LB_scales, threshold = '0.06mJy')
fit_gaussian(shiftname+'.image', region =   'circle[[%s, %s], %.1farcsec]' % (mask_ra, mask_dec, 0.3))
#Peak of Gaussian component identified with imfit: J2000 16h26m45.021965s -24d23m08.27374s
#PA of Gaussian component: 120.04 deg
#Inclination of Gaussian component: 45.94 deg
#Pixel coordinates of peak: x = 1500.160 y = 1499.752

"""
Now check if the flux scales seem consistent between execution blocks (within ~5%)
"""

split_all_obs(prefix+'_LB1_initcont_shift.ms', prefix+'_LB1_initcont_shift_exec')

"""
First, check the pipeline outputs (STEP11/12, hif_setjy or hif_setmodels in the TASKS list of the qa products) to check whether the calibrator catalog matches up with the input flux density values for the calibrators.
(Also check the corresponding plots.)

	SB1, EB0: Titan      = 1.278 Jy at 232.350 GHz
	LB1, EB0: J1517-2422 = 2.918 Jy at 232.583 GHz
	LB1, EB1: J1517-2422 = 2.209 Jy at 232.585 GHz

Now can check that these inputs are matching the current calibrator catalog:

"""
au.planetFlux('Titan',date='2015/07/21', frequency=232.350e9, bandwidth=15.625e6)
au.getALMAFlux('J1517-2422', frequency = '232.582GHz', date = '2017/09/07')     # LB1, EB0
au.getALMAFlux('J1517-2422', frequency = '232.585GHz', date = '2017/10/03')     # LB1, EB1

"""
SB1, EB0:
 'fluxDensity': 1.2188372993124337,
 'frequency': [232342187500.00003, 232357812500.00003],
 'majorAxis': 0.75214452165990309,
 'meanFrequency': 232350000000.00003,
 'minorAxis': 0.7521445216599031,
 'positionAngle': 2.171899999999998}

Closest Band 3 measurement: 3.690 +- 0.070 (age=+3 days) 91.5 GHz
Closest Band 7 measurement: 2.370 +- 0.050 (age=+2 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 18 days from 2017/09/07, with age separation of 0 days
  2017/08/20: freqs=[91.46, 343.48], fluxes=[3.78, 2.71]
Median Monte-Carlo result for 232.582000 = 2.993229 +- 0.255810 (scaled MAD = 0.255278)
Result using spectral index of -0.251488 for 232.582 GHz from 3.690 Jy at 91.460 GHz = 2.918012 +- 0.255810 Jy

Closest Band 3 measurement: 2.770 +- 0.050 (age=+1 days) 103.5 GHz
Closest Band 3 measurement: 2.790 +- 0.040 (age=+1 days) 91.5 GHz
Closest Band 7 measurement: 1.920 +- 0.100 (age=+1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 1 days from 2017/10/03, with age separation of 0 days
  2017/10/02: freqs=[103.49, 91.46, 343.48], fluxes=[2.77, 2.79, 1.92]
Median Monte-Carlo result for 232.585000 = 2.173269 +- 0.178465 (scaled MAD = 0.180271)
Result using spectral index of -0.279723 for 232.585 GHz from 2.770 Jy at 103.490 GHz = 2.208543 +- 0.178465 Jy

"""

"""
The input calibrator flux densities are consistent with the catalog.  The Titan flux density seems off. 

"""

"""
Here we export averaged visibilities to npz files and then plot the deprojected visibilities to compare the amplitude scales
"""

PA = 121. #these are the rough values pulled from Gaussian fitting and used for initial deprojection. They are NOT the final values used for subsequent data analysis
incl = 57.



if not skip_plots:
    for msfile in [prefix+'_SB1_initcont_shift.ms', prefix+'_LB1_initcont_shift_exec0.ms', prefix+'_LB1_initcont_shift_exec1.ms']:
        export_MS(msfile)
    #plot deprojected visibility profiles of all the execution blocks
    plot_deprojected([prefix+'_SB1_initcont_shift.vis.npz', prefix+'_LB1_initcont_shift_exec0.vis.npz', prefix+'_LB1_initcont_shift_exec1.vis.npz'],
                     fluxscale=[1.0, 1.0, 1.0], PA = PA, incl = incl, show_err=False)

    estimate_flux_scale(reference = prefix+'_SB1_initcont_shift.vis.npz', comparison = prefix+'_LB1_initcont_shift_exec0.vis.npz', incl = incl, PA = PA)
    #The ratio of the fluxes of Elias27_LB1_initcont_shift_exec0.vis.npz to Elias27_SB1_initcont_shift.vis.npz is 1.15508
    #The scaling factor for gencal is 1.075 for your comparison measurement
    #The error on the weighted mean ratio is 8.590e-04, although it's likely that the weights in the measurement sets are off by some constant factor


    estimate_flux_scale(reference = prefix+'_LB1_initcont_shift_exec0.vis.npz', comparison = prefix+'_LB1_initcont_shift_exec1.vis.npz', incl = incl, PA = PA)
    #The ratio of the fluxes of Elias27_LB1_initcont_shift_exec1.vis.npz to Elias27_LB1_initcont_shift_exec0.vis.npz is 0.94992
    #The scaling factor for gencal is 0.975 for your comparison measurement
    #The error on the weighted mean ratio is 7.326e-04, although it's likely that the weights in the measurement sets are off by some constant factor

"""
Given the amount of scatter in the flux ratios as a function of uv distance, it seems likely that the discrepancy is due to phase-noise
"""

"""
Start of self-calibration of the short-baseline data 
"""
SB_cont_p0 = prefix+'_SB_contp0'
os.system('rm -rf %s' % (SB_cont_p0+'.ms',))
os.system('cp -r %s %s' % (prefix+'_SB1_initcont_shift.ms', SB_cont_p0+'.ms'))

tclean_wrapper(vis = SB_cont_p0+'.ms', imagename = SB_cont_p0, mask = common_mask, scales = SB_scales, threshold = '0.2mJy', savemodel = 'modelcolumn')

noise_annulus ="annulus[[%s, %s],['%.2farcsec', '4.25arcsec']]" % (mask_ra, mask_dec, 1.1*mask_semimajor) #annulus over which we measure the noise. The inner radius is slightly larger than the semimajor axis of the mask (to add some buffer space around the mask) and the outer radius is set so that the annulus fits inside the long-baseline image size 
estimate_SNR(SB_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Elias27_SB_contp0.image
#Beam 0.233 arcsec x 0.194 arcsec (62.94 deg)
#Flux inside disk mask: 299.04 mJy
#Peak intensity of source: 23.99 mJy/beam
#rms: 8.38e-02 mJy/beam
#Peak SNR: 286.10



"""
We need to select one or more reference antennae for gaincal

We first look at the CASA command log (or manual calibration script) to see how the reference antennae choices were ranked (weighted toward antennae close to the center of the array and with good SNR)
Note that gaincal will sometimes choose a different reference antenna than the one specified if it deems another one to be a better choice 

for SB1, refant = 'DV09, DV08, DV06' 
LB1, exec0 = 'DA61,DA64,DA59,DV09,DA52'
LB1, exec1 = 'DA50,DV24,DA61,DV25,DV09'

"""
get_station_numbers(SB_cont_p0+'.ms', 'DV09')
#Observation ID 0: DV09@A007


SB_contspws = '0~7' #change as appropriate
SB_refant = 'DV09@A007' 
SB1_obs0_timerange = '2015/07/20/00~2015/07/22/00'
 

# It's useful to check that the phases for the refant look good in all execution blocks in plotms. However, plotms has a tendency to crash in CASA 5.1.1, so it might be necessary to use plotms in an older version of CASA 
#plotms(vis=SB_cont_p0, xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '0')
#plotms(vis=SB_cont_p0, xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '1')

#first round of phase self-cal for short baseline data
SB_p1 = prefix+'_SB.p1'
os.system('rm -rf '+SB_p1)
gaincal(vis=SB_cont_p0+'.ms' , caltable=SB_p1, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='p', solint='120s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [120s, 60s, 30s, 18s, 6s]

if not skip_plots:
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange, plotrange=[0,0,-180,180]) 

applycal(vis=SB_cont_p0+'.ms', spw=SB_contspws, gaintable=[SB_p1], interp = 'linearPD', calwt = True)

SB_cont_p1 = prefix+'_SB_contp1'
os.system('rm -rf %s*' % SB_cont_p1)
split(vis=SB_cont_p0+'.ms', outputvis=SB_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p1+'.ms' , imagename = SB_cont_p1, mask = common_mask, scales = SB_scales, threshold = '0.15mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Elias27_SB_contp1.image
#Beam 0.233 arcsec x 0.194 arcsec (62.59 deg)
#Flux inside disk mask: 310.31 mJy
#Peak intensity of source: 26.44 mJy/beam
#rms: 5.61e-02 mJy/beam
#Peak SNR: 471.18



#second round of phase self-cal for short baseline data
SB_p2 = prefix+'_SB.p2'
os.system('rm -rf '+SB_p2)
gaincal(vis=SB_cont_p1+'.ms' , caltable=SB_p2, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='p', solint='60s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange, plotrange=[0,0,-180,180])

applycal(vis=SB_cont_p1+'.ms', spw=SB_contspws, gaintable=[SB_p2], interp = 'linearPD', calwt = True)

SB_cont_p2 = prefix+'_SB_contp2'
os.system('rm -rf %s*' % SB_cont_p2)
split(vis=SB_cont_p1+'.ms', outputvis=SB_cont_p2+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p2+'.ms' , imagename = SB_cont_p2, mask = common_mask, scales = SB_scales, threshold = '0.15mJy', savemodel = 'modelcolumn') 
estimate_SNR(SB_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Elias27_SB_contp2.image
#Beam 0.234 arcsec x 0.196 arcsec (62.94 deg)
#Flux inside disk mask: 310.55 mJy
#Peak intensity of source: 27.27 mJy/beam
#rms: 5.58e-02 mJy/beam
#Peak SNR: 488.54



#improvement over previous round of phase self-cal is marginal, so we move on to amp self-cal for the short baseline data 
SB_ap = prefix+'_SB.ap'
os.system('rm -rf '+SB_ap)
#note that the solint and minsnr are larger for amp self-cal
#try solnorm = False first. If that leads to bad solutions, try solnorm = True. If that still doesn't help, then just skip amp self-cal
gaincal(vis=SB_cont_p2+'.ms' , caltable=SB_ap, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='ap', solint='inf', minsnr=3.0, minblperant=4, solnorm = False) 

if not skip_plots:
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange, plotrange=[0,0,0,2])

applycal(vis=SB_cont_p2+'.ms', spw=SB_contspws, gaintable=[SB_ap], interp = 'linearPD', calwt = True)

SB_cont_ap = prefix+'_SB_contap'
os.system('rm -rf %s*' % SB_cont_ap)
split(vis=SB_cont_p2+'.ms', outputvis=SB_cont_ap+'.ms', datacolumn='corrected', keepflags = False)

tclean_wrapper(vis = SB_cont_ap+'.ms' , imagename = SB_cont_ap, mask = common_mask, scales = SB_scales, threshold = '0.12mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Elias27_SB_contap.image
#Beam 0.233 arcsec x 0.196 arcsec (63.57 deg)
#Flux inside disk mask: 306.69 mJy
#Peak intensity of source: 27.00 mJy/beam
#rms: 4.57e-02 mJy/beam
#Peak SNR: 591.08



#now we concatenate all the data together

combined_cont_p0 = prefix+'_combined_contp0'
os.system('rm -rf %s*' % combined_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [SB_cont_ap+'.ms', prefix+'_LB1_initcont_shift.ms'], concatvis = combined_cont_p0+'.ms' , dirtol = '0.1arcsec', copypointing = False) 

tclean_wrapper(vis = combined_cont_p0+'.ms' , imagename = combined_cont_p0, mask = common_mask, scales = LB_scales, threshold = '0.05mJy', imsize = 4000, uvtaper = '.03arcsec', savemodel = 'modelcolumn')
noise_annulus ="annulus[[%s, %s],['%.2farcsec', '5arcsec']]" % (mask_ra, mask_dec, 1.1*mask_semimajor)
estimate_SNR(combined_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Beam 0.053 arcsec x 0.041 arcsec (73.57 deg)
#Flux inside disk mask: 330.57 mJy
#Peak intensity of source: 4.43 mJy/beam
#rms: 1.58e-02 mJy/beam
#Peak SNR: 280.14

get_station_numbers(combined_cont_p0+'.ms', 'DA61')
#Observation ID 1: DA61@A015
#Observation ID 2: DA61@A015

get_station_numbers(combined_cont_p0+'.ms', 'DA50')
#Observation ID 0: DA50@A064
#Observation ID 1: DA50@A108
#Observation ID 2: DA50@A108



combined_refant = 'DV09@A007, DA61@A015,DA50@A108'
combined_contspws = '0~15'
combined_spwmap =  [0,0,0,0,0,0,0,0,8,8,8,8,12,12,12,12] #note that the tables produced by gaincal in 5.1.1 have spectral windows numbered differently if you use the combine = 'spw' option. Previously, all of the solutions would be written to spectral window 0. Now, they are written to the first window in each execution block. So, the spwmap argument has to correspond to the first window in each execution block you want to calibrate. 

LB1_obs0_timerange = '2017/09/07/00~2017/09/08/00'
LB2_obs1_timerange = '2017/10/02/00~2017/10/05/00'

#first round of phase self-cal for long baseline data
combined_p1 = prefix+'_combined.p1'
os.system('rm -rf '+combined_p1)
gaincal(vis=combined_cont_p0+'.ms' , caltable=combined_p1, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='360s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [900s, 360s, 180s, 60s, 30s, 6s]

if not skip_plots:
    plotcal(caltable=combined_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=combined_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB2_obs1_timerange, plotrange=[0,0,-180,180])

applycal(vis=combined_cont_p0+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p1], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p1 = prefix+'_combined_contp1'
os.system('rm -rf %s*' % combined_cont_p1)
split(vis=combined_cont_p0+'.ms', outputvis=combined_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p1+'.ms' , imagename = combined_cont_p1, mask = common_mask, scales = LB_scales, threshold = '0.05mJy', imsize = 4000, uvtaper = '.03arcsec', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Elias27_combined_contp1.image
#Beam 0.053 arcsec x 0.041 arcsec (73.57 deg)
#Flux inside disk mask: 330.74 mJy
#Peak intensity of source: 4.46 mJy/beam
#rms: 1.55e-02 mJy/beam
#Peak SNR: 286.95

#second round of phase self-cal for long baseline data
combined_p2 = prefix+'_combined.p2'
os.system('rm -rf '+combined_p2)
gaincal(vis=combined_cont_p1+'.ms' , caltable=combined_p2, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='180s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=combined_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB2_obs1_timerange, plotrange=[0,0,-180,180])

applycal(vis=combined_cont_p1+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p2], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p2 = prefix+'_combined_contp2'
os.system('rm -rf %s*' % combined_cont_p2)
split(vis=combined_cont_p1+'.ms', outputvis=combined_cont_p2+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p2+'.ms' , imagename = combined_cont_p2, mask = common_mask, scales = LB_scales, threshold = '0.05mJy',  imsize = 4000, uvtaper = '.03arcsec',savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Elias27_combined_contp2.image
#Beam 0.053 arcsec x 0.041 arcsec (73.57 deg)
#Flux inside disk mask: 330.89 mJy
#Peak intensity of source: 4.53 mJy/beam
#rms: 1.55e-02 mJy/beam
#Peak SNR: 293.27


#third round of phase self-cal for long baseline data
combined_p3 = prefix+'_combined.p3'
os.system('rm -rf '+combined_p3)
gaincal(vis=combined_cont_p2+'.ms' , caltable=combined_p3, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='60s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=combined_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB2_obs1_timerange, plotrange=[0,0,-180,180])

applycal(vis=combined_cont_p2+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p3], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p3 = prefix+'_combined_contp3'
os.system('rm -rf %s*' % combined_cont_p3)
split(vis=combined_cont_p2+'.ms', outputvis=combined_cont_p3+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p3+'.ms' , imagename = combined_cont_p3, mask = common_mask, scales = LB_scales, threshold = '0.05mJy',  imsize = 4000, uvtaper = '.03arcsec', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p3+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Elias27_combined_contp3.image
#Beam 0.053 arcsec x 0.041 arcsec (73.57 deg)
#Flux inside disk mask: 330.87 mJy
#Peak intensity of source: 4.66 mJy/beam
#rms: 1.54e-02 mJy/beam
#Peak SNR: 303.14


#fourth round of phase self-cal for long baseline data
combined_p4 = prefix+'_combined.p4'
os.system('rm -rf '+combined_p4)
gaincal(vis=combined_cont_p3+'.ms' , caltable=combined_p4, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='30s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p4, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=combined_p4, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB2_obs1_timerange, plotrange=[0,0,-180,180])

applycal(vis=combined_cont_p3+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p4], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p4 = prefix+'_combined_contp4'
os.system('rm -rf %s*' % combined_cont_p4)
split(vis=combined_cont_p3+'.ms', outputvis=combined_cont_p4+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p4+'.ms' , imagename = combined_cont_p4, mask = common_mask, scales = LB_scales, threshold = '0.05mJy',  imsize = 4000, uvtaper = '.03arcsec', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p4+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Elias27_combined_contp4.image
#Beam 0.053 arcsec x 0.041 arcsec (73.57 deg)
#Flux inside disk mask: 331.03 mJy
#Peak intensity of source: 4.74 mJy/beam
#rms: 1.54e-02 mJy/beam
#Peak SNR: 308.03


combined_ap = prefix+'_combined.ap'
os.system('rm -rf '+combined_ap)
gaincal(vis=combined_cont_p4+'.ms' , caltable=combined_ap, gaintype='T', combine = 'spw,scan', spw=combined_contspws, refant=combined_refant, calmode='ap', solint='900s', minsnr=3.0, minblperant=4, solnorm = False)

if not skip_plots:
    plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange, plotrange=[0,0,0,2]) 
    plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = LB2_obs1_timerange, plotrange=[0,0,0,2])

applycal(vis=combined_cont_p4+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_ap], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_ap = prefix+'_combined_contap'
os.system('rm -rf %s*' % combined_cont_ap)
split(vis=combined_cont_p4+'.ms', outputvis=combined_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_ap+'.ms' , imagename = combined_cont_ap, mask = common_mask, scales = LB_scales,  threshold = '0.05mJy',  imsize = 4000, uvtaper = '.03arcsec',savemodel = 'modelcolumn')
estimate_SNR(combined_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)

#Elias27_combined_contap.image
#Beam 0.054 arcsec x 0.041 arcsec (73.62 deg)
#Flux inside disk mask: 329.29 mJy
#Peak intensity of source: 4.64 mJy/beam
#rms: 1.41e-02 mJy/beam
#Peak SNR: 329.72

os.system('tar cvzf /data/sandrews/ALMA_disks/final_MS/Elias27_cont_final.ms.tgz '+combined_cont_ap+'.ms')


