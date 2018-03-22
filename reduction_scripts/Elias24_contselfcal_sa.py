"""
This script was written for CASA 5.1.1

Datasets calibrated (in order of date observed):
SB1: 2013.1.00498.L/Elias_24_a_06_TM1  
     Observed 21 July 2015 (1 execution block)
     PI: L. Perez
     As delivered to PI
LB1: 2016.1.00484.L/Elias_24_a_06_TM1 
     Observed 25 September 2017 and 3 October 2017 (2 execution blocks)
     PI: S. Andrews
     As delivered to PI

"""
import os

execfile('/pool/asha0/SCIENCE/p484/reduction_scripts/reduction_utils.py')

skip_plots = False #if this is true, all of the plotting and inspection steps will be skipped and the script can be executed non-interactively in CASA if all relevant values have been hard-coded already 

#to fill this dictionary out, use listobs for the relevant measurement set 

prefix = 'Elias24' #string that identifies the source and is at the start of the name for all output files

#Note that if you are downloading data from the archive, your SPW numbering may differ from the SPWs in this script depending on how you split your data out!! 
data_params = {'SB1': {'vis' : '/data/sandrews/LP/archival/2013.1.00498.S/science_goal.uid___A001_X13a_Xeb/group.uid___A001_X13a_Xec/member.uid___A001_X13a_Xed/calibrated/uid___A002_Xa657ad_X736.ms.split.cal',
                       'name' : 'SB1',
                       'field': 'Elias_24',
                       'line_spws': np.array([1,5,6]), #SpwIDs of windows with lines that need to be flagged (this needs to be edited for each short baseline dataset)
                       'line_freqs': np.array([2.30538e11, 2.2039868420e11, 2.1956035410e11]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz)
                      }, #information about the short baseline measurement sets (SB1, SB2, SB3, etc in chronological order)
               'LB1': {'vis' : '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X4c/group.uid___A001_X8c5_X4d/member.uid___A001_X8c5_X4e/calibrated/calibrated_final.ms',
                       'name' : 'LB1',
                       'field' : 'Elias_24',
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
    flagchannels_string = get_flagchannels(data_params[i], prefix, velocity_range = np.array([-15, 25]))
    """
    Produces spectrally averaged continuum datasets
    If you only want to include a subset of the windows, you can manually pass in values for contspw and width_array, e.g.
    avg_cont(data_params[i], output_prefix, flagchannels = flagchannels_string, contspws = '0~2', width_array = [480,8,8]).
    If you don't pass in values, all of the SPWs will be split out and the widths will be computed automatically to enforce a maximum channel width of 125 MHz.
    WARNING: Only use the avg_cont function if the total bandwidth is recorded correctly in the original MS. There is sometimes a bug in CASA that records incorrect total bandwidths
    """
    # Flagchannels input string for SB1: '0:1856~1982, 4:1856~1982, 8:1856~1982'
    # Averaged continuum dataset saved to Elias20_SB1_initcont.ms
    # Flagchannels input string for LB1: '3:1858~1984, 7:1858~1984'
    # Averaged continuum dataset saved to Elias20_LB1_initcont.ms
    avg_cont(data_params[i], prefix, flagchannels = flagchannels_string)

# sample command to check that amplitude vs. uvdist looks normal
# plotms(vis=prefix+'_SB1_initcont.ms', xaxis='uvdist', yaxis='amp', coloraxis='spw', avgtime='30', avgchannel='16')

# Some additional flagging
flagmanager(vis='Elias24_SB1_initcont.ms', mode='save', versionname='init_cal_flags', comment='Flag states immediately after initial calibration')
flagdata(vis='Elias24_SB1_initcont.ms', mode='manual', spw='3~4,6', flagbackup=False, field=data_params['SB1']['field'], timerange='2015/07/21/22:45:00~2015/07/21/23:10:00', antenna='DA41')
flagdata(vis='Elias24_SB1_initcont.ms', mode='manual', spw='1,3,5', flagbackup=False, field=data_params['SB1']['field'], scan='30', antenna='DA46')
flagdata(vis='Elias24_SB1_initcont.ms', mode='manual', spw='3,4,6', flagbackup=False, field=data_params['SB1']['field'], scan='30,35', antenna='DA59')
flagdata(vis='Elias24_SB1_initcont.ms', mode='manual', spw='3,4', flagbackup=False, field=data_params['SB1']['field'], scan='30', antenna='DV08')
flagdata(vis='Elias24_SB1_initcont.ms', mode='manual', spw='3', flagbackup=False, field=data_params['SB1']['field'], scan='30,35', antenna='DV18')


"""
Quick imaging of every execution block in the measurement set using tclean. 
The threshold, scales, and mask should be adjusted for each source.
In this case, we picked our threshold, scales, and mask from previous reductions of the data. You may wish to experiment with these values when imaging. 
The threshold is ~3-4x the rms, the mask is an ellipse that covers all the emission and has roughly the same geometry, and we choose 4 to 6 scales such that the first scale is 0 (a point), and the largest is ~half the major axis of the mask.
The mask angle and the semimajor and semiminor axes should be the same for all imaging. The center is not necessarily fixed because of potential misalignments between observations. 
"""
mask_angle = 52 #position angle of mask in degrees
mask_semimajor = 1.6 #semimajor axis of mask in arcsec
mask_semiminor = 1.4 #semiminor axis of mask in arcsec

SB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % ('16h26m24.08s', '-24.16.13.89', mask_semimajor, mask_semiminor, mask_angle)
LB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % ('16h26m24.08s', '-24.16.13.89', mask_semimajor, mask_semiminor, mask_angle)

SB_scales = [0, 5, 10, 25]
LB_scales = [0, 5, 20, 60, 180]
"""
In this section, we are imaging every execution block to check spatial alignment 
"""

if not skip_plots:
    #images are saved in the format prefix+'_name_initcont_exec#.ms'
    image_each_obs(data_params['SB1'], prefix, mask = SB1_mask, scales = SB_scales, threshold = '0.2mJy', interactive = False)
    # inspection of images do not reveal additional bright background sources 

    image_each_obs(data_params['LB1'], prefix, mask = LB1_mask, scales = LB_scales, threshold = '0.1mJy', interactive = False)

    """
    Since the source looks axisymmetric, we will fit a Gaussian to the disk to estimate the location of the peak in each image and record the output.
    We are also very roughly estimating the PA and inclination for checking the flux scale offsets later (these are NOT the position angles and inclinations used for analysis of the final image products).
    Here, we are using the CLEAN mask to restrict the region over which the fit is occurring, but you may wish to shrink the region even further if your disk structure is complex 
    """
    fit_gaussian(prefix+'_SB1_initcont_exec0.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: J2000 16h26m24.078792s -24d16m13.84764s
    #PA of Gaussian component: 51.52 deg
    #Inclination of Gaussian component: 27.37 deg

    fit_gaussian(prefix+'_LB1_initcont_exec0.image', region = 'circle[[1465pix,1371pix], 0.4arcsec]')
    #Peak of Gaussian component identified with imfit: ICRS 16h26m24.077753s -24d16m13.88292s
    #PA of Gaussian component: 46.63 deg
    #Inclination of Gaussian component: 30.39 deg

    fit_gaussian(prefix+'_LB1_initcont_exec1.image', region = 'circle[[1465pix,1371pix], 0.4arcsec]')
    #Peak of Gaussian component identified with imfit: ICRS 16h26m24.078146s -24d16m13.88695s
    #PA of Gaussian component: 43.57 deg
    #Inclination of Gaussian component: 30.34 deg

"""
The individual execution blocks are all in alignment.  But, we first need to align the phase centers.
"""
SB_shift = prefix+'_SB1_initcont_shift.ms'
os.system('rm -rf '+SB_shift+'*')
split(vis=prefix+'_SB1_initcont.ms', outputvis=SB_shift, datacolumn='data')
fixvis(vis=SB_shift, outputvis=SB_shift, field=data_params['SB1']['field'], phasecenter='ICRS 16h26m24.070000s -24d16m13.50000s')


"""
Now check if the flux scales seem consistent between execution blocks (within ~5%)
"""

split_all_obs(prefix+'_SB1_initcont_shift.ms', prefix+'_SB1_initcont_exec')
split_all_obs(prefix+'_LB1_initcont.ms', prefix+'_LB1_initcont_exec')

"""
First, check the pipeline outputs (STEP11/12, hif_setjy or hif_setmodels in the TASKS list of the qa products) to check whether the calibrator catalog matches up with the input flux density values for the calibrators.
(Also check the corresponding plots.)

	SB1, EB0: Titan      = 1.278 Jy at 232.350 GHz
	LB1, EB0: J1733-1304 = 1.899 Jy at 232.583 GHz
	LB1, EB1: J1733-1304 = 1.899 Jy at 232.585 GHz

Now can check that these inputs are matching the current calibrator catalog:

"""
au.planetFlux('Titan',date='2015/07/21', frequency=232.350e9, bandwidth=15.625e6)
au.getALMAFlux('J1733-1304', frequency = '232.583GHz', date = '2017/09/25')     # LB1, EB0
au.getALMAFlux('J1733-1304', frequency = '232.585GHz', date = '2017/10/03')     # LB1, EB1

"""
SB1, EB0:
 'fluxDensity': 1.2188372993124337,
 'frequency': [232342187500.00003, 232357812500.00003],
 'majorAxis': 0.75214452165990309,
 'meanFrequency': 232350000000.00003,
 'minorAxis': 0.7521445216599031,
 'positionAngle': 2.171899999999998}

LB1, EB0:
Closest Band 3 measurement: 3.070 +- 0.080 (age=-7 days) 103.5 GHz
Closest Band 3 measurement: 3.250 +- 0.090 (age=-7 days) 91.5 GHz
Closest Band 7 measurement: 1.290 +- 0.050 (age=+2 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -7 days from 2017/09/25, with age separation of 0 days
  2017/10/02: freqs=[103.49, 91.46, 343.48], fluxes=[3.07, 3.25, 1.49]
Median Monte-Carlo result for 232.583000 = 1.882610 +- 0.162177 (scaled MAD = 0.157987)
Result using spectral index of -0.593201 for 232.583 GHz from 3.160 Jy at 97.475 GHz = 1.886444 +- 0.162177 Jy

LB1, EB1:
Closest Band 3 measurement: 3.070 +- 0.080 (age=+1 days) 103.5 GHz
Closest Band 3 measurement: 3.250 +- 0.090 (age=+1 days) 91.5 GHz
Closest Band 7 measurement: 1.490 +- 0.080 (age=+1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 1 days from 2017/10/03, with age separation of 0 days
  2017/10/02: freqs=[103.49, 91.46, 343.48], fluxes=[3.07, 3.25, 1.49]
Median Monte-Carlo result for 232.585000 = 1.886613 +- 0.164340 (scaled MAD = 0.161956)
Result using spectral index of -0.593201 for 232.585 GHz from 3.160 Jy at 97.475 GHz = 1.886435 +- 0.164340 Jy
"""

"""
The input calibrator flux densities are consistent with the catalog.  The Titan flux density seems messed up.  

"""

"""
Here we export averaged visibilities to npz files and then plot the deprojected visibilities to compare the amplitude scales
"""

PA = 45. #these are the rough values pulled from Gaussian fitting and used for initial deprojection. They are NOT the final values used for subsequent data analysis
incl = 30.
phasecenter = au.radec2deg('16:26:24.07000, -24.16.13.50000')
peakpos = au.radec2deg('16:26:24.078, -24.16.13.883')
offsets = au.angularSeparation(peakpos[0], peakpos[1], phasecenter[0], phasecenter[1], True)
"""
(0.00011064346380163252,
 3.333333332942978e-05,
 -0.00010638888888830412,
 3.038717497363008e-05)
"""
offx = 3600.*offsets[3]
offy = 3600.*offsets[2]


if not skip_plots:
    for msfile in [prefix+'_SB1_initcont_exec0.ms', prefix+'_LB1_initcont_exec0.ms', prefix+'_LB1_initcont_exec1.ms']:
        export_MS(msfile)
    #plot deprojected visibility profiles of all the execution blocks
    plot_deprojected([prefix+'_SB1_initcont_exec0.vis.npz', prefix+'_LB1_initcont_exec0.vis.npz', prefix+'_LB1_initcont_exec1.vis.npz'],
                     fluxscale=[1.0, 1.0, 1.0], offx = offx, offy = offy, PA = PA, incl = incl, show_err=False)

    estimate_flux_scale(reference = prefix+'_LB1_initcont_exec0.vis.npz', comparison = prefix+'_SB1_initcont_exec0.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
    #The ratio of the fluxes of Elias24_SB1_initcont_exec0.vis.npz to Elias24_LB1_initcont_exec0.vis.npz is 0.83890
    #The scaling factor for gencal is 0.916 for your comparison measurement
    #The error on the weighted mean ratio is 5.333e-04, although it's likely that the weights in the measurement sets are too off by some constant factor

    estimate_flux_scale(reference = prefix+'_LB1_initcont_exec0.vis.npz', comparison = prefix+'_LB1_initcont_exec1.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
    #The ratio of the fluxes of Elias24_LB1_initcont_exec1.vis.npz to Elias24_LB1_initcont_exec0.vis.npz is 0.95667
    #The scaling factor for gencal is 0.978 for your comparison measurement
    #The error on the weighted mean ratio is 5.647e-04, although it's likely that the weights in the measurement sets are too off by some constant factor

    #We replot the deprojected visibilities with rescaled factors to check that the values make sense
    plot_deprojected([prefix+'_SB1_initcont_exec0.vis.npz', prefix+'_LB1_initcont_exec0.vis.npz', prefix+'_LB1_initcont_exec1.vis.npz'],
                     fluxscale=[1/0.839, 1.0, 1.0], offx = offx, offy = offy, PA = PA, incl = incl, show_err=False)

"""
The SB1 data seems low compared to the LB executions, but its likely caused by phase noise.  After 2 iterations of phase-only self-calibration, we find excellent agreement in the flux scales.  So, no re-scaling is needed.
"""

"""
Start of self-calibration of the short-baseline data 
"""
#merge the short-baseline execution blocks into a single MS
SB_cont_p0 = prefix+'_SB_contp0'
os.system('rm -rf %s*' % SB_cont_p0)
os.system('cp -r '+prefix+'_SB1_initcont_exec0.ms '+SB_cont_p0+'.ms')

#make initial image
mask_angle = 45. #position angle of mask in degrees
mask_ra = '16h26m24.078s'
mask_dec = '-24.16.13.883'
common_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % (mask_ra, mask_dec, mask_semimajor, mask_semiminor, mask_angle)

tclean_wrapper(vis = SB_cont_p0+'.ms', imagename = SB_cont_p0, mask = common_mask, scales = SB_scales, threshold = '0.15mJy', savemodel = 'modelcolumn')

noise_annulus ="annulus[[%s, %s],['%.2farcsec', '4.25arcsec']]" % (mask_ra, mask_dec, 1.1*mask_semimajor) #annulus over which we measure the noise. The inner radius is slightly larger than the semimajor axis of the mask (to add some buffer space around the mask) and the outer radius is set so that the annulus fits inside the long-baseline image size 
estimate_SNR(SB_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Elias24_SB_contp0.image
#Beam 0.234 arcsec x 0.194 arcsec (62.68 deg)
#Flux inside disk mask: 346.55 mJy
#Peak intensity of source: 39.54 mJy/beam
#rms: 1.29e-01 mJy/beam
#Peak SNR: 307.27


"""
We need to select one or more reference antennae for gaincal

We first look at the CASA command log (or manual calibration script) to see how the reference antennae choices were ranked (weighted toward antennae close to the center of the array and with good SNR)
Note that gaincal will sometimes choose a different reference antenna than the one specified if it deems another one to be a better choice 

for SB1, refant = 'DA46, DA51'
for all, refant = 'DA61, DV09, DA46'

"""

SB_contspws = '0~7' #change as appropriate
SB_refant = 'DV09, DV08, DV06' 
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
#Elias24_SB_contp1.image
#Beam 0.234 arcsec x 0.194 arcsec (62.33 deg)
#Flux inside disk mask: 360.15 mJy
#Peak intensity of source: 43.23 mJy/beam
#rms: 5.87e-02 mJy/beam
#Peak SNR: 736.83


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

tclean_wrapper(vis = SB_cont_p2+'.ms' , imagename = SB_cont_p2, mask = common_mask, scales = SB_scales, threshold = '0.1mJy', savemodel = 'modelcolumn') 
estimate_SNR(SB_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Elias24_SB_contp2.image
#Beam 0.235 arcsec x 0.194 arcsec (62.35 deg)
#Flux inside disk mask: 360.78 mJy
#Peak intensity of source: 43.93 mJy/beam
#rms: 5.76e-02 mJy/beam
#Peak SNR: 762.80


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
split(vis=SB_cont_p2+'.ms', outputvis=SB_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_ap+'.ms' , imagename = SB_cont_ap, mask = common_mask, scales = SB_scales, threshold = '0.07mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Elias24_SB_contap.image
#Beam 0.232 arcsec x 0.192 arcsec (62.90 deg)
#Flux inside disk mask: 360.31 mJy
#Peak intensity of source: 43.16 mJy/beam
#rms: 4.73e-02 mJy/beam
#Peak SNR: 911.65


#now we concatenate all the data together

combined_cont_p0 = prefix+'_combined_contp0'
os.system('rm -rf %s*' % combined_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [SB_cont_ap+'.ms', prefix+'_LB1_initcont_exec0.ms', prefix+'_LB1_initcont_exec1.ms'], concatvis = combined_cont_p0+'.ms' , dirtol = '0.1arcsec', copypointing = False) 

tclean_wrapper(vis = combined_cont_p0+'.ms' , imagename = combined_cont_p0, mask = common_mask, scales = LB_scales, threshold = '0.10mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Elias24_combined_contp0.image
#Beam 0.045 arcsec x 0.030 arcsec (86.49 deg)
#Flux inside disk mask: 367.59 mJy
#Peak intensity of source: 4.67 mJy/beam
#rms: 1.83e-02 mJy/beam
#Peak SNR: 255.28

get_station_numbers(combined_cont_p0+'.ms', 'DA61')
get_station_numbers(combined_cont_p0+'.ms', 'DV24')


combined_refant = 'DV24@A090, DA61@A015, DV09@A007, DV08@A008, DV06@A014'
combined_contspws = '0~15'
combined_spwmap =  [0,0,0,0,0,0,0,0,8,8,8,8,12,12,12,12] #note that the tables produced by gaincal in 5.1.1 have spectral windows numbered differently if you use the combine = 'spw' option. Previously, all of the solutions would be written to spectral window 0. Now, they are written to the first window in each execution block. So, the spwmap argument has to correspond to the first window in each execution block you want to calibrate. 

LB1_obs0_timerange = '2017/09/24/00~2017/09/26/00'
LB2_obs1_timerange = '2017/10/02/00~2017/10/05/00'

#first round of phase self-cal for long baseline data
combined_p1 = prefix+'_combined.p1'
os.system('rm -rf '+combined_p1)
gaincal(vis=combined_cont_p0+'.ms' , caltable=combined_p1, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='900s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [900s, 360s, 180s, 60s, 30s, 6s]

if not skip_plots:
    plotcal(caltable=combined_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=combined_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB2_obs1_timerange, plotrange=[0,0,-180,180])

applycal(vis=combined_cont_p0+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p1], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p1 = prefix+'_combined_contp1'
os.system('rm -rf %s*' % combined_cont_p1)
split(vis=combined_cont_p0+'.ms', outputvis=combined_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p1+'.ms' , imagename = combined_cont_p1, mask = common_mask, scales = LB_scales, threshold = '0.10mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Elias24_combined_contp1.image
#Beam 0.045 arcsec x 0.030 arcsec (86.49 deg)
#Flux inside disk mask: 367.09 mJy
#Peak intensity of source: 4.58 mJy/beam
#rms: 1.81e-02 mJy/beam
#Peak SNR: 253.03

# SNR change minimal, but map improvements.  Continue.


#second round of phase self-cal for long baseline data
combined_p2 = prefix+'_combined.p2'
os.system('rm -rf '+combined_p2)
gaincal(vis=combined_cont_p1+'.ms' , caltable=combined_p2, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='360s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=combined_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB2_obs1_timerange, plotrange=[0,0,-180,180])

applycal(vis=combined_cont_p1+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p2], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p2 = prefix+'_combined_contp2'
os.system('rm -rf %s*' % combined_cont_p2)
split(vis=combined_cont_p1+'.ms', outputvis=combined_cont_p2+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p2+'.ms' , imagename = combined_cont_p2, mask = common_mask, scales = LB_scales, threshold = '0.04mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Elias24_combined_contp2.image
#Beam 0.045 arcsec x 0.030 arcsec (86.49 deg)
#Flux inside disk mask: 367.30 mJy
#Peak intensity of source: 4.63 mJy/beam
#rms: 1.72e-02 mJy/beam
#Peak SNR: 269.92

# still smoothing out map ripples.  Try one more.


#third round of phase self-cal for long baseline data
combined_p3 = prefix+'_combined.p3'
os.system('rm -rf '+combined_p3)
gaincal(vis=combined_cont_p2+'.ms' , caltable=combined_p3, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='180s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=combined_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB2_obs1_timerange, plotrange=[0,0,-180,180])

applycal(vis=combined_cont_p2+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p3], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p3 = prefix+'_combined_contp3'
os.system('rm -rf %s*' % combined_cont_p3)
split(vis=combined_cont_p2+'.ms', outputvis=combined_cont_p3+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p3+'.ms' , imagename = combined_cont_p3, mask = common_mask, scales = LB_scales, threshold = '0.04mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p3+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Elias24_combined_contp3.image
#Beam 0.045 arcsec x 0.030 arcsec (86.49 deg)
#Flux inside disk mask: 367.44 mJy
#Peak intensity of source: 4.70 mJy/beam
#rms: 1.70e-02 mJy/beam
#Peak SNR: 276.39

# starting to see improvements

#fourth round of phase self-cal for long baseline data
combined_p4 = prefix+'_combined.p4'
os.system('rm -rf '+combined_p4)
gaincal(vis=combined_cont_p3+'.ms' , caltable=combined_p4, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='60s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p4, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=combined_p4, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB2_obs1_timerange, plotrange=[0,0,-180,180])

applycal(vis=combined_cont_p3+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p4], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p4 = prefix+'_combined_contp4'
os.system('rm -rf %s*' % combined_cont_p4)
split(vis=combined_cont_p3+'.ms', outputvis=combined_cont_p4+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p4+'.ms' , imagename = combined_cont_p4, mask = common_mask, scales = LB_scales, threshold = '0.04mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p4+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Elias24_combined_contp4.image
#Beam 0.045 arcsec x 0.030 arcsec (86.49 deg)
#Flux inside disk mask: 367.61 mJy
#Peak intensity of source: 4.88 mJy/beam
#rms: 1.69e-02 mJy/beam
#Peak SNR: 288.42

# now seeing some improvements 

#fifth round of phase self-cal for long baseline data
combined_p5 = prefix+'_combined.p5'
os.system('rm -rf '+combined_p5)
gaincal(vis=combined_cont_p4+'.ms' , caltable=combined_p5, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='30s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p5, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=combined_p5, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB2_obs1_timerange, plotrange=[0,0,-180,180])

applycal(vis=combined_cont_p4+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p5], interp = 'linearPD', calwt = True, applymode = 'calonly')


combined_cont_p5 = prefix+'_combined_contp5'
os.system('rm -rf %s*' % combined_cont_p5)
split(vis=combined_cont_p4+'.ms', outputvis=combined_cont_p5+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p5+'.ms' , imagename = combined_cont_p5, mask = common_mask, scales = LB_scales, threshold = '0.03mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p5+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Elias24_combined_contp5.image
#Beam 0.045 arcsec x 0.030 arcsec (86.49 deg)
#Flux inside disk mask: 367.67 mJy
#Peak intensity of source: 4.95 mJy/beam
#rms: 1.67e-02 mJy/beam
#Peak SNR: 295.82

# that's about it.  Try some amp self-cal.


combined_ap = prefix+'_combined.ap'
os.system('rm -rf '+combined_ap)
gaincal(vis=combined_cont_p5+'.ms' , caltable=combined_ap, gaintype='T', combine = 'spw,scan', spw=combined_contspws, refant=combined_refant, calmode='ap', solint='900s', minsnr=3.0, minblperant=4, solnorm = False)

if not skip_plots:
    plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange, plotrange=[0,0,0,2]) 
    plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = LB2_obs1_timerange, plotrange=[0,0,0,2])

applycal(vis=combined_cont_p5+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_ap], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_ap = prefix+'_combined_contap'
os.system('rm -rf %s*' % combined_cont_ap)
split(vis=combined_cont_p5+'.ms', outputvis=combined_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_ap+'.ms' , imagename = combined_cont_ap, mask = common_mask, scales = LB_scales, threshold = '0.025mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)

# with solnorm = False
#Elias24_combined_contap.image
#Beam 0.041 arcsec x 0.028 arcsec (84.09 deg)
#Flux inside disk mask: 369.28 mJy
#Peak intensity of source: 4.35 mJy/beam
#rms: 1.49e-02 mJy/beam
#Peak SNR: 290.99

# map definitely improved.

# full directory size is 26 GB.

os.system('tar cvzf /data/sandrews/ALMA_disks/final_MS/Elias24_cont_final.ms.tgz '+combined_cont_ap+'.ms')


tclean_wrapper(vis = combined_cont_ap+'.ms' , imagename = combined_cont_ap+'_rob0', mask = common_mask, scales = LB_scales, robust = 0.0, threshold = '0.025mJy', savemodel = 'none')

