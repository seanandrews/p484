"""
This script was written for CASA 5.1.1

Datasets calibrated (in order of date observed):
SB1: 2016.1.00484.L/Wa_Oph_6_a_06_TM1  
     Observed 09 May 2017 (1 execution block)
     PI: S. Andrews
     As delivered to PI
LB1: 2016.1.00484.L/Wa_Oph_6_a_06_TM1 
     Observed 09 September 2017 and 20 September 2017 (2 execution blocks)
     PI: S. Andrews
     As delivered to PI

"""
import os

execfile('/pool/asha0/SCIENCE/p484/sa_work/reduction_utils.py')

skip_plots = False #if this is true, all of the plotting and inspection steps will be skipped and the script can be executed non-interactively in CASA if all relevant values have been hard-coded already 

#to fill this dictionary out, use listobs for the relevant measurement set 

prefix = 'WaOph6' #string that identifies the source and is at the start of the name for all output files

#Note that if you are downloading data from the archive, your SPW numbering may differ from the SPWs in this script depending on how you split your data out!! 
data_params = {'SB1': {'vis' : '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_Xbd4641_X1e/group.uid___A001_Xbd4641_X22/member.uid___A001_Xbd4641_X23/calibrated/calibrated_final.ms',
                       'name' : 'SB1',
                       'field': 'Wa_Oph_6',
                       'line_spws': np.array([0]), #SpwIDs of windows with lines that need to be flagged (this needs to be edited for each short baseline dataset)
                       'line_freqs': np.array([2.30538e11]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz)
                      }, #information about the short baseline measurement sets (SB1, SB2, SB3, etc in chronological order)
               'LB1': {'vis' : '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X68/group.uid___A001_X8c5_X69/member.uid___A001_X8c5_X6a/calibrated/calibrated_final.ms',
                       'name' : 'LB1',
                       'field' : 'Wa_Oph_6',
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
    # Flagchannels input string for SB1: '0:1858~1984'
    # Averaged continuum dataset saved to WaOph6_SB1_initcont.ms
    # Flagchannels input string for LB1: '3:1872~1998, 7:1872~1998'
    # Averaged continuum dataset saved to WaOph6_LB1_initcont.ms
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
mask_angle = 162 #position angle of mask in degrees
mask_semimajor = 1.3 #semimajor axis of mask in arcsec
mask_semiminor = 1.0 #semiminor axis of mask in arcsec

SB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % ('16h48m45.62s', '-14.16.36.26', mask_semimajor, mask_semiminor, mask_angle)
LB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % ('16h48m45.62s', '-14.16.36.26', mask_semimajor, mask_semiminor, mask_angle)

SB_scales = [0, 5, 10, 20]
LB_scales = [0, 5, 20, 60, 120, 240]
"""
In this section, we are imaging every execution block to check spatial alignment 
"""

if not skip_plots:
    #images are saved in the format prefix+'_name_initcont_exec#.ms'
    image_each_obs(data_params['SB1'], prefix, mask = SB1_mask, scales = SB_scales, threshold = '0.15mJy', interactive = False)
    # inspection of images do not reveal additional bright background sources 

    image_each_obs(data_params['LB1'], prefix, mask = LB1_mask, scales = LB_scales, threshold = '0.06mJy', interactive = False)

    """
    Since the source looks axisymmetric, we will fit a Gaussian to the disk to estimate the location of the peak in each image and record the output.
    We are also very roughly estimating the PA and inclination for checking the flux scale offsets later (these are NOT the position angles and inclinations used for analysis of the final image products).
    Here, we are using the CLEAN mask to restrict the region over which the fit is occurring, but you may wish to shrink the region even further if your disk structure is complex 
    """
    fit_gaussian(prefix+'_SB1_initcont_exec0.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h48m45.620861s -14d16m36.27068s

    fit_gaussian(prefix+'_LB1_initcont_exec0.image', region = LB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h48m45.619925s -14d16m36.23235s

    fit_gaussian(prefix+'_LB1_initcont_exec1.image', region = LB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h48m45.621789s -14d16m36.25788s
    #PA of Gaussian component: 161.80 deg
    #Inclination of Gaussian component: 42.55 deg

"""
This is a tough case, where the 1st execution in the LB data has particularly awful phase noise.  It is not obvious that the emission is really shifted, as would be implied by the Gaussian centroid fit.  After some extensive experimentation
using various shifts, we have come to the conclusion that the apparent astrometric shift is not real (it is just noise that will be corrected in phase self-calibration).  

"""

split_all_obs(prefix+'_SB1_initcont.ms', prefix+'_SB1_initcont_exec')
split_all_obs(prefix+'_LB1_initcont.ms', prefix+'_LB1_initcont_exec')

"""
First, check the pipeline outputs (STEP11/12, hif_setjy or hif_setmodels in the TASKS list of the qa products) to check whether the calibrator catalog matches up with the input flux density values for the calibrators.
(Also check the corresponding plots.)

	SB1, EB0: J1733-1304 = 1.484 Jy at 232.617 GHz
	LB1, EB0: J1733-1304 = 1.517 Jy at 232.588 GHz
	LB1, EB1: J1733-1304 = 1.588 Jy at 232.588 GHz

Now can check that these inputs are matching the current calibrator catalog:

"""
au.getALMAFlux('J1733-1304', frequency = '232.617GHz', date = '2017/05/09')	# SB1, EB0
au.getALMAFlux('J1733-1304', frequency = '232.588GHz', date = '2017/09/09')     # LB1, EB0
au.getALMAFlux('J1733-1304', frequency = '232.586GHz', date = '2017/09/20')     # LB1, EB1

"""
Closest Band 3 measurement: 2.890 +- 0.050 (age=+4 days) 91.5 GHz
Closest Band 7 measurement: 1.120 +- 0.060 (age=+5 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 5 days from 2017/05/09, with age separation of 0 days
  2017/05/04: freqs=[91.46, 103.49, 343.48], fluxes=[2.88, 2.82, 1.12]
Median Monte-Carlo result for 232.617000 = 1.525687 +- 0.130272 (scaled MAD = 0.130513)
Result using spectral index of -0.714210 for 232.617 GHz from 2.890 Jy at 91.460 GHz = 1.483713 +- 0.130272 Jy

Closest Band 3 measurement: 2.970 +- 0.060 (age=+5 days) 91.5 GHz
Closest Band 7 measurement: 1.200 +- 0.040 (age=+4 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 16 days from 2017/09/09, with age separation of 0 days
  2017/08/24: freqs=[91.46, 343.48], fluxes=[2.8, 1.08]
Median Monte-Carlo result for 232.588000 = 1.427984 +- 0.152271 (scaled MAD = 0.147726)
Result using spectral index of -0.719951 for 232.588 GHz from 2.970 Jy at 91.460 GHz = 1.516771 +- 0.152271 Jy

Closest Band 3 measurement: 3.110 +- 0.050 (age=+4 days) 91.5 GHz
Closest Band 7 measurement: 1.290 +- 0.050 (age=-3 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -12 days from 2017/09/20, with age separation of 0 days
  2017/10/02: freqs=[91.46, 103.49, 343.48], fluxes=[3.25, 3.07, 1.49]
Median Monte-Carlo result for 232.586000 = 1.885434 +- 0.163528 (scaled MAD = 0.165476)
Result using spectral index of -0.593201 for 232.586 GHz from 3.110 Jy at 91.460 GHz = 1.787742 +- 0.163528 Jy


The input flux density for the 2nd LB execution is too low, about 11%.

"""

"""
Here we export averaged visibilities to npz files and then plot the deprojected visibilities to compare the amplitude scales
"""

PA = 162. #these are the rough values pulled from Gaussian fitting and used for initial deprojection. They are NOT the final values used for subsequent data analysis
incl = 43.
phasecenter = au.radec2deg('16:48:45.63800, -14.16.35.90000')
peakpos = au.radec2deg('16:48:45.622, -14.16.36.258')
offsets = au.angularSeparation(peakpos[0], peakpos[1], phasecenter[0], phasecenter[1], True)
"""
(0.00011858902982531175,
 -6.6666666709748433e-05,
 -9.9444444440962269e-05,
 -6.4607743064420948e-05)
"""
offx = 3600.*offsets[3]
offy = 3600.*offsets[2]


if not skip_plots:
    for msfile in [prefix+'_SB1_initcont_exec0.ms', prefix+'_LB1_initcont_exec0.ms', prefix+'_LB1_initcont_exec1.ms']:
        export_MS(msfile)
    #plot deprojected visibility profiles of all the execution blocks
    plot_deprojected([prefix+'_SB1_initcont_exec0.vis.npz', prefix+'_LB1_initcont_exec0.vis.npz', prefix+'_LB1_initcont_exec1.vis.npz'],
                     fluxscale=[1.0, 1.0, 1.00], offx = offx, offy = offy, PA = PA, incl = incl, show_err=False)

    estimate_flux_scale(reference = prefix+'_SB1_initcont_exec0.vis.npz', comparison = prefix+'_LB1_initcont_exec0.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
    # huge baseline-dependent discrepancy, tied to substantial phase noise    

    estimate_flux_scale(reference = prefix+'_SB1_initcont_exec0.vis.npz', comparison = prefix+'_LB1_initcont_exec1.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
    #The ratio of the fluxes of WaOph6_LB1_initcont_exec1.vis.npz to WaOph6_SB1_initcont_exec0.vis.npz is 0.93673
    #The scaling factor for gencal is 0.968 for your comparison measurement
    #The error on the weighted mean ratio is 4.872e-04, although it's likely that the weights in the measurement sets are too off by some constant factor

    #We replot the deprojected visibilities with rescaled factors to check that the values make sense
    plot_deprojected([prefix+'_SB1_initcont_exec0.vis.npz', prefix+'_LB1_initcont_exec0.vis.npz', prefix+'_LB1_initcont_exec1.vis.npz'],
                     fluxscale=[1.0, 1, 1/0.93673], offx = offx, offy = offy, PA = PA, incl = incl, show_err=False)

#now correct the flux scales
#rescale_flux(prefix+'_LB1_initcont_exec0.ms', [1.106])
rescale_flux(prefix+'_LB1_initcont_exec1.ms', [0.968])
#Splitting out rescaled values into new ms: WaOph6_XB1_initcont_execX_rescaled.ms
"""
For now, I am not re-scaling the 1st LB execution, even though it is clearly off.  I will try an initial iteration of phase-only self-cal and then re-examine things.

"""


"""
Start of self-calibration of the short-baseline data 
"""
#no need to merge the short-baseline execution blocks into a single MS, just copy the sole execution over
SB_cont_p0 = prefix+'_SB_contp0'
os.system('rm -rf %s*' % SB_cont_p0)
os.system('cp -r '+prefix+'_SB1_initcont_exec0.ms '+SB_cont_p0+'.ms')

#make initial image
mask_ra = '16h48m45.622s'
mask_dec = '-14.16.36.258'
common_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % (mask_ra, mask_dec, mask_semimajor, mask_semiminor, mask_angle)

tclean_wrapper(vis = SB_cont_p0+'.ms', imagename = SB_cont_p0, mask = common_mask, scales = SB_scales, threshold = '0.15mJy', savemodel = 'modelcolumn')

noise_annulus ="annulus[[%s, %s],['%.2farcsec', '4.25arcsec']]" % (mask_ra, mask_dec, 1.1*mask_semimajor) #annulus over which we measure the noise. The inner radius is slightly larger than the semimajor axis of the mask (to add some buffer space around the mask) and the outer radius is set so that the annulus fits inside the long-baseline image size 
estimate_SNR(SB_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#WaOph6_SB_contp0.image
#Beam 0.265 arcsec x 0.234 arcsec (-87.64 deg)
#Flux inside disk mask: 159.09 mJy
#Peak intensity of source: 39.60 mJy/beam
#rms: 1.62e-01 mJy/beam
#Peak SNR: 244.98


"""
We need to select one or more reference antennae for gaincal

We first look at the CASA command log (or manual calibration script) to see how the reference antennae choices were ranked (weighted toward antennae close to the center of the array and with good SNR)
Note that gaincal will sometimes choose a different reference antenna than the one specified if it deems another one to be a better choice 

SB1, EB0: DA49, DA59
LB1, EB0: DA61, DA64, DA59, DA52, DV09
LB1, EB1: DA50, DA61, DV25, DV09, DV06

for SB1, refant = 'DA49, DA59'
for all, refant = 'DA61, DV09, DA46'

"""

SB_contspws = '0~3' #change as appropriate
SB_refant = 'DA49, DA59' 
SB1_obs0_timerange = '2017/05/08/00~2017/05/10/00'
 

# It's useful to check that the phases for the refant look good in all execution blocks in plotms. However, plotms has a tendency to crash in CASA 5.1.1, so it might be necessary to use plotms in an older version of CASA 
#plotms(vis=SB_cont_p0, xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '0')
#plotms(vis=SB_cont_p0, xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '1')

#first round of phase self-cal for short baseline data
SB_p1 = prefix+'_SB.p1'
os.system('rm -rf '+SB_p1)
gaincal(vis=SB_cont_p0+'.ms' , caltable=SB_p1, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='p', solint='30s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [120s, 60s, 30s, 18s, 6s]

if not skip_plots:
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange, plotrange=[0,0,-180,180]) 

applycal(vis=SB_cont_p0+'.ms', spw=SB_contspws, gaintable=[SB_p1], interp = 'linearPD', calwt = True)

SB_cont_p1 = prefix+'_SB_contp1'
os.system('rm -rf %s*' % SB_cont_p1)
split(vis=SB_cont_p0+'.ms', outputvis=SB_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p1+'.ms' , imagename = SB_cont_p1, mask = common_mask, scales = SB_scales, threshold = '0.1mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#WaOph6_SB_contp1.image
#Beam 0.265 arcsec x 0.234 arcsec (-87.63 deg)
#Flux inside disk mask: 161.91 mJy
#Peak intensity of source: 41.11 mJy/beam
#rms: 4.93e-02 mJy/beam
#Peak SNR: 834.22


#second round of phase self-cal for short baseline data
SB_p2 = prefix+'_SB.p2'
os.system('rm -rf '+SB_p2)
gaincal(vis=SB_cont_p1+'.ms' , caltable=SB_p2, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='p', solint='18s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange, plotrange=[0,0,-180,180])

applycal(vis=SB_cont_p1+'.ms', spw=SB_contspws, gaintable=[SB_p2], interp = 'linearPD', calwt = True)

SB_cont_p2 = prefix+'_SB_contp2'
os.system('rm -rf %s*' % SB_cont_p2)
split(vis=SB_cont_p1+'.ms', outputvis=SB_cont_p2+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p2+'.ms' , imagename = SB_cont_p2, mask = common_mask, scales = SB_scales, threshold = '0.07mJy', savemodel = 'modelcolumn') 
estimate_SNR(SB_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#WaOph6_SB_contp2.image
#Beam 0.265 arcsec x 0.234 arcsec (-87.63 deg)
#Flux inside disk mask: 162.01 mJy
#Peak intensity of source: 41.24 mJy/beam
#rms: 4.17e-02 mJy/beam
#Peak SNR: 987.98


#third round of phase self-cal for short baseline data
SB_p3 = prefix+'_SB.p3'
os.system('rm -rf '+SB_p3)
gaincal(vis=SB_cont_p2+'.ms' , caltable=SB_p3, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='p', solint='int', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=SB_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange, plotrange=[0,0,-180,180])

applycal(vis=SB_cont_p2+'.ms', spw=SB_contspws, gaintable=[SB_p3], interp = 'linearPD', calwt = True)

SB_cont_p3 = prefix+'_SB_contp3'
os.system('rm -rf %s*' % SB_cont_p3)
split(vis=SB_cont_p2+'.ms', outputvis=SB_cont_p3+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p3+'.ms' , imagename = SB_cont_p3, mask = common_mask, scales = SB_scales, threshold = '0.07mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_p3+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#WaOph6_SB_contp3.image
#Beam 0.265 arcsec x 0.234 arcsec (-87.63 deg)
#Flux inside disk mask: 162.19 mJy
#Peak intensity of source: 41.43 mJy/beam
#rms: 3.96e-02 mJy/beam
#Peak SNR: 1046.38


#move on to amp self-cal for the short baseline data 
SB_ap = prefix+'_SB.ap'
os.system('rm -rf '+SB_ap)
#note that the solint and minsnr are larger for amp self-cal
#try solnorm = False first. If that leads to bad solutions, try solnorm = True. If that still doesn't help, then just skip amp self-cal
gaincal(vis=SB_cont_p3+'.ms' , caltable=SB_ap, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='ap', solint='inf', minsnr=3.0, minblperant=4, solnorm = False) 

if not skip_plots:
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange, plotrange=[0,0,0,2])

applycal(vis=SB_cont_p3+'.ms', spw=SB_contspws, gaintable=[SB_ap], interp = 'linearPD', calwt = True)

SB_cont_ap = prefix+'_SB_contap'
os.system('rm -rf %s*' % SB_cont_ap)
split(vis=SB_cont_p3+'.ms', outputvis=SB_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_ap+'.ms' , imagename = SB_cont_ap, mask = common_mask, scales = SB_scales, threshold = '0.07mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#WaOph6_SB_contap.image
#Beam 0.265 arcsec x 0.233 arcsec (-87.21 deg)
#Flux inside disk mask: 161.67 mJy
#Peak intensity of source: 41.23 mJy/beam
#rms: 2.95e-02 mJy/beam
#Peak SNR: 1399.74


#now we concatenate all the data together

combined_cont_p0 = prefix+'_combined_contp0'
os.system('rm -rf %s*' % combined_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [SB_cont_ap+'.ms', prefix+'_LB1_initcont_exec0.ms', prefix+'_LB1_initcont_exec1_rescaled.ms'], concatvis = combined_cont_p0+'.ms' , dirtol = '0.1arcsec', copypointing = False) 

tclean_wrapper(vis = combined_cont_p0+'.ms' , imagename = combined_cont_p0, mask = common_mask, scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#WaOph6_combined_contp0.image
#Beam 0.073 arcsec x 0.038 arcsec (-76.36 deg)
#Flux inside disk mask: 161.78 mJy
#Peak intensity of source: 4.96 mJy/beam
#rms: 2.51e-02 mJy/beam
#Peak SNR: 197.33

combined_refant = 'DV09@A007, DA61@A015, DV06@A027, DA49@A002, DA59@A001'
combined_contspws = '0~11'
combined_spwmap =  [0,0,0,0,4,4,4,4,8,8,8,8] #note that the tables produced by gaincal in 5.1.1 have spectral windows numbered differently if you use the combine = 'spw' option. Previously, all of the solutions would be written to spectral window 0. Now, they are written to the first window in each execution block. So, the spwmap argument has to correspond to the first window in each execution block you want to calibrate. 

LB1_obs0_timerange = '2017/09/08/00~2017/09/10/00'
LB2_obs1_timerange = '2017/09/19/00~2017/09/21/00'

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

tclean_wrapper(vis = combined_cont_p1+'.ms' , imagename = combined_cont_p1, mask = common_mask, scales = LB_scales, threshold = '0.04mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#WaOph6_combined_contp1.image
#Beam 0.073 arcsec x 0.038 arcsec (-76.36 deg)
#Flux inside disk mask: 161.86 mJy
#Peak intensity of source: 6.10 mJy/beam
#rms: 1.92e-02 mJy/beam
#Peak SNR: 318.18


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
#WaOph6_combined_contp2.image
#Beam 0.073 arcsec x 0.038 arcsec (-76.36 deg)
#Flux inside disk mask: 161.44 mJy
#Peak intensity of source: 6.66 mJy/beam
#rms: 1.61e-02 mJy/beam
#Peak SNR: 413.37


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

tclean_wrapper(vis = combined_cont_p3+'.ms' , imagename = combined_cont_p3, mask = common_mask, scales = LB_scales, threshold = '0.03mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p3+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#WaOph6_combined_contp3.image
#Beam 0.073 arcsec x 0.038 arcsec (-76.36 deg)
#Flux inside disk mask: 161.13 mJy
#Peak intensity of source: 7.05 mJy/beam
#rms: 1.49e-02 mJy/beam
#Peak SNR: 474.60


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

tclean_wrapper(vis = combined_cont_p4+'.ms' , imagename = combined_cont_p4, mask = common_mask, scales = LB_scales, threshold = '0.03mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p4+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#WaOph6_combined_contp4.image
#Beam 0.073 arcsec x 0.038 arcsec (-76.36 deg)
#Flux inside disk mask: 161.10 mJy
#Peak intensity of source: 7.48 mJy/beam
#rms: 1.36e-02 mJy/beam
#Peak SNR: 549.49


#fourth round of phase self-cal for long baseline data
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
#WaOph6_combined_contp5.image
#Beam 0.073 arcsec x 0.038 arcsec (-76.36 deg)
#Flux inside disk mask: 160.98 mJy
#Peak intensity of source: 7.66 mJy/beam
#rms: 1.35e-02 mJy/beam
#Peak SNR: 568.77


# split off and image individual executions (post self-cal)
split_all_obs(combined_cont_p5+'.ms', prefix+'_testsc_exec')
tclean_wrapper(vis = 'WaOph6_testsc_exec1.ms' , imagename = 'testsc_LB0', imsize=3000, cellsize='0.003arcsec', mask = common_mask, scales = LB_scales, threshold = '0.06mJy')
tclean_wrapper(vis = 'WaOph6_testsc_exec2.ms' , imagename = 'testsc_LB1', imsize=3000, cellsize='0.003arcsec', mask = common_mask, scales = LB_scales, threshold = '0.06mJy')

# measure centroids again
fit_gaussian('testsc_LB0.image', region = common_mask)
#Peak of Gaussian component identified with imfit: ICRS 16h48m45.621219s -14d16m36.24582s
#Peak of Gaussian component identified with imfit: ICRS 16h48m45.620823s -14d16m36.25197s

fit_gaussian('testsc_LB1.image', region = common_mask)
#Peak of Gaussian component identified with imfit: ICRS 16h48m45.620797s -14d16m36.25243s

# examine visibilities
PA = 162. #these are the rough values pulled from Gaussian fitting and used for initial deprojection. They are NOT the final values used for subsequent data analysis
incl = 43.
phasecenter = au.radec2deg('16:48:45.63800, -14.16.35.90000')
peakpos = au.radec2deg('16:48:45.621, -14.16.36.251')
offsets = au.angularSeparation(peakpos[0], peakpos[1], phasecenter[0], phasecenter[1], True)
offx = 3600.*offsets[3]
offy = 3600.*offsets[2]

for msfile in ['WaOph6_testsc_exec0.ms', 'WaOph6_testsc_exec1.ms', 'WaOph6_testsc_exec2.ms']:
    export_MS(msfile)

#plot deprojected visibility profiles of all the execution blocks
plot_deprojected(['WaOph6_testsc_exec0.vis.npz', 'WaOph6_testsc_exec1.vis.npz', 'WaOph6_testsc_exec2.vis.npz'],
                 fluxscale=[1.0, 1.0, 1.0], offx = offx, offy = offy, PA = PA, incl = incl, show_err=False)

estimate_flux_scale(reference = 'WaOph6_testsc_exec0.vis.npz', comparison = 'WaOph6_testsc_exec1.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
#The ratio of the fluxes of WaOph6_testsc_exec1.vis.npz to WaOph6_testsc_exec0.vis.npz is 0.95363
#The scaling factor for gencal is 0.977 for your comparison measurement
#The error on the weighted mean ratio is 3.413e-04, although it's likely that the weights in the measurement sets are too off by some constant factor

estimate_flux_scale(reference = 'WaOph6_testsc_exec0.vis.npz', comparison = 'WaOph6_testsc_exec2.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
#The ratio of the fluxes of WaOph6_testsc_exec2.vis.npz to WaOph6_testsc_exec0.vis.npz is 1.01630
#The scaling factor for gencal is 1.008 for your comparison measurement
#The error on the weighted mean ratio is 5.032e-04, although it's likely that the weights in the measurement sets are too off by some constant factor

"""
Ok, so this validates the original hypotheses that (a) the offsets are due to phase noise; (b) that the first execution of LB data does not need a flux re-scaling; 
and (c) that the 2nd execution of LB data needed a ~7% re-scaling.  At this point, we can just continue self-calibration.
"""


# try one more round of phase self-cal
combined_p6 = prefix+'_combined.p6'
os.system('rm -rf '+combined_p6)
gaincal(vis=combined_cont_p5+'.ms' , caltable=combined_p6, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='18s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p6, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=combined_p6, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB2_obs1_timerange, plotrange=[0,0,-180,180])

applycal(vis=combined_cont_p5+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p6], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p6 = prefix+'_combined_contp6'
os.system('rm -rf %s*' % combined_cont_p6)
split(vis=combined_cont_p5+'.ms', outputvis=combined_cont_p6+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p6+'.ms' , imagename = combined_cont_p6, mask = common_mask, scales = LB_scales, threshold = '0.025mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p6+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#WaOph6_combined_contp6.image
#Beam 0.073 arcsec x 0.038 arcsec (-76.36 deg)
#Flux inside disk mask: 161.15 mJy
#Peak intensity of source: 7.74 mJy/beam
#rms: 1.34e-02 mJy/beam
#Peak SNR: 578.61



# that's about it.  Try some amp self-cal.
combined_ap = prefix+'_combined.ap'
os.system('rm -rf '+combined_ap)
gaincal(vis=combined_cont_p6+'.ms' , caltable=combined_ap, gaintype='T', combine = 'spw,scan', spw=combined_contspws, refant=combined_refant, calmode='ap', solint='900s', minsnr=3.0, minblperant=4, solnorm = False)

if not skip_plots:
    plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange, plotrange=[0,0,0,2]) 
    plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = LB2_obs1_timerange, plotrange=[0,0,0,2])

applycal(vis=combined_cont_p6+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_ap], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_ap = prefix+'_combined_contap'
os.system('rm -rf %s*' % combined_cont_ap)
split(vis=combined_cont_p6+'.ms', outputvis=combined_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_ap+'.ms' , imagename = combined_cont_ap, mask = common_mask, scales = LB_scales, threshold = '0.02mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)

# with solnorm = False
#WaOph6_combined_contap.image
#Beam 0.070 arcsec x 0.037 arcsec (-77.58 deg)
#Flux inside disk mask: 161.30 mJy
#Peak intensity of source: 7.45 mJy/beam
#rms: 1.30e-02 mJy/beam
#Peak SNR: 575.11

# map definitely improved.

# full directory size is 32 GB.

os.system('tar cvzf /data/sandrews/ALMA_disks/final_MS/WaOph6_cont_final.ms.tgz '+combined_cont_ap+'.ms')
