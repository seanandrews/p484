"""
This script was written for CASA 5.1.1

Datasets calibrated (in order of date observed):
SB1: 2016.1.00484.L/DoAr_33_a_06_TM1  
     Observed 14 May 2017, 17 May 2017, and 19 May 2017 (3 execution blocks)
     PI: S. Andrews
     As delivered to PI
LB1: 2016.1.00484.L/DoAr_33_a_06_TM1 
     Observed 17 September 2017 and 10 October 2017 (2 execution blocks)
     PI: S. Andrews
     As delivered to PI

"""
import os

execfile('/pool/asha0/SCIENCE/p484/sa_work/reduction_utils.py')

skip_plots = False #if this is true, all of the plotting and inspection steps will be skipped and the script can be executed non-interactively in CASA if all relevant values have been hard-coded already 

#to fill this dictionary out, use listobs for the relevant measurement set 

prefix = 'DoAr33' #string that identifies the source and is at the start of the name for all output files

#Note that if you are downloading data from the archive, your SPW numbering may differ from the SPWs in this script depending on how you split your data out!! 
data_params = {'SB1': {'vis' : '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_Xbd4641_X1e/group.uid___A001_Xbd4641_X25/member.uid___A001_Xbd4641_X26/calibrated/calibrated_final.ms',
                       'name' : 'SB1',
                       'field': 'DoAr_33',
                       'line_spws': np.array([0,4,8]), #SpwIDs of windows with lines that need to be flagged (this needs to be edited for each short baseline dataset)
                       'line_freqs': np.array([2.30538e11, 2.30538e11, 2.30538e11]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz)
                      }, #information about the short baseline measurement sets (SB1, SB2, SB3, etc in chronological order)
               'LB1': {'vis' : '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X6c/group.uid___A001_X8c5_X6d/member.uid___A001_X8c5_X6e/calibrated/calibrated_final.ms',
                       'name' : 'LB1',
                       'field' : 'DoAr_33',
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
    # Flagchannels input string for SB1: '0:1855~1981, 4:1855~1981, 8:1855~1981'
    #Averaged continuum dataset saved to DoAr33_SB1_initcont.ms
    # Flagchannels input string for LB1: '3:1858~1984, 7:1858~1984'
    #Averaged continuum dataset saved to DoAr33_LB1_initcont.ms
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
mask_angle = 79 #position angle of mask in degrees
mask_semimajor = 0.7 #semimajor axis of mask in arcsec
mask_semiminor = 0.5 #semiminor axis of mask in arcsec

SB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % ('16h27m39.00s', '-23.58.19.17', mask_semimajor, mask_semiminor, mask_angle)
LB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % ('16h27m39.00s', '-23.58.19.17', mask_semimajor, mask_semiminor, mask_angle)

SB_scales = [0, 5, 10]
LB_scales = [0, 5, 20, 60, 100]
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
    #Peak of Gaussian component identified with imfit: ICRS 16h27m39.004011s -23d58m19.18060s

    fit_gaussian(prefix+'_SB1_initcont_exec1.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h27m39.002327s -23d58m19.16920s

    fit_gaussian(prefix+'_SB1_initcont_exec2.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h27m39.001418s -23d58m19.17451s

    fit_gaussian(prefix+'_LB1_initcont_exec0.image', region = LB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h27m39.003185s -23d58m19.18790s

    fit_gaussian(prefix+'_LB1_initcont_exec1.image', region = LB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h27m39.003036s -23d58m19.18899s
    #PA of Gaussian component: 83.14 deg
    #Inclination of Gaussian component: 42.62 deg

"""
Note that there are two other point sources in the SB maps, located about 5" almost due E (about 0.5 mJy), and a little more than 7" to the SW (about 0.3 mJy).  Both of these fall outside 
the default LB image size.
"""

"""
The individual execution blocks are all in rough alignment.  The small (~10-15 mas) shifts between SB executions are not a source of concern: those maps are much lower SNR and will re-orient during self-calibration.
Now check if the flux scales seem consistent between execution blocks (within ~5%)
"""

split_all_obs(prefix+'_SB1_initcont.ms', prefix+'_SB1_initcont_exec')
split_all_obs(prefix+'_LB1_initcont.ms', prefix+'_LB1_initcont_exec')


"""
First, check the pipeline outputs (STEP11/12, hif_setjy or hif_setmodels in the TASKS list of the qa products) to check whether the calibrator catalog matches up with the input flux density values for the calibrators.
(Also check the corresponding plots.)

	SB1, EB0: J1517-2422 = 1.944 Jy at 232.610 GHz
	SB1, EB1: J1733-1304 = 1.610 Jy at 232.609 GHz
	SB1, EB2: J1517-2422 = 2.108 Jy at 232.609 GHz
	LB1, EB0: J1733-1304 = 1.788 Jy at 232.582 GHz
	LB1, EB1: J1733-1304 = 1.910 Jy at 232.587 GHz

Now can check that these inputs are matching the current calibrator catalog:

"""
au.getALMAFlux('J1517-2422', frequency = '232.610GHz', date = '2017/05/14')	# SB1, EB0
au.getALMAFlux('J1733-1304', frequency = '232.609GHz', date = '2017/05/17')     # SB1, EB1
au.getALMAFlux('J1517-2422', frequency = '232.609GHz', date = '2017/05/19')     # SB1, EB2
au.getALMAFlux('J1733-1304', frequency = '232.582GHz', date = '2017/09/17')     # LB1, EB0
au.getALMAFlux('J1733-1304', frequency = '232.587GHz', date = '2017/10/10')     # LB1, EB1

"""
SB1, EB0:
Closest Band 3 measurement: 2.420 +- 0.060 (age=+0 days) 91.5 GHz
Closest Band 7 measurement: 1.840 +- 0.090 (age=-1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -1 days from 2017/05/14, with age separation of 0 days
  2017/05/15: freqs=[103.49, 91.46, 343.48], fluxes=[2.55, 2.49, 1.84]
Median Monte-Carlo result for 232.610000 = 2.043380 +- 0.159244 (scaled MAD = 0.157684)
Result using spectral index of -0.234794 for 232.610 GHz from 2.420 Jy at 91.460 GHz = 1.943706 +- 0.159244 Jy

SB1, EB1:
Closest Band 3 measurement: 3.020 +- 0.060 (age=+0 days) 103.5 GHz
Closest Band 7 measurement: 1.190 +- 0.060 (age=+0 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 0 days from 2017/05/17, with age separation of 0 days
  2017/05/17: freqs=[103.49, 343.48], fluxes=[3.02, 1.19]
Median Monte-Carlo result for 232.609000 = 1.610663 +- 0.129086 (scaled MAD = 0.126920)
Result using spectral index of -0.776310 for 232.609 GHz from 3.020 Jy at 103.490 GHz = 1.610486 +- 0.129086 Jy

SB1, EB2:
Closest Band 3 measurement: 2.550 +- 0.060 (age=+4 days) 103.5 GHz
Closest Band 3 measurement: 2.490 +- 0.050 (age=+4 days) 91.5 GHz
Closest Band 7 measurement: 1.750 +- 0.060 (age=+2 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 4 days from 2017/05/19, with age separation of 0 days
  2017/05/15: freqs=[103.49, 91.46, 343.48], fluxes=[2.55, 2.49, 1.84]
Median Monte-Carlo result for 232.609000 = 2.040585 +- 0.161160 (scaled MAD = 0.157430)
Result using spectral index of -0.234794 for 232.609 GHz from 2.520 Jy at 97.475 GHz = 2.054524 +- 0.161160 Jy

LB1, EB0:
Closest Band 3 measurement: 3.110 +- 0.050 (age=+1 days) 91.5 GHz
Closest Band 7 measurement: 1.290 +- 0.050 (age=-6 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -15 days from 2017/09/17, with age separation of 0 days
  2017/10/02: freqs=[91.46, 103.49, 343.48], fluxes=[3.25, 3.07, 1.49]
Median Monte-Carlo result for 232.582000 = 1.882789 +- 0.163850 (scaled MAD = 0.163139)
Result using spectral index of -0.593201 for 232.582 GHz from 3.110 Jy at 91.460 GHz = 1.787760 +- 0.163850 Jy

LB1, EB1:
Closest Band 3 measurement: 3.080 +- 0.070 (age=+0 days) 103.5 GHz
Closest Band 3 measurement: 3.270 +- 0.070 (age=+0 days) 91.5 GHz
Closest Band 7 measurement: 1.490 +- 0.080 (age=+8 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 8 days from 2017/10/10, with age separation of 0 days
  2017/10/02: freqs=[91.46, 103.49, 343.48], fluxes=[3.25, 3.07, 1.49]
Median Monte-Carlo result for 232.587000 = 1.882821 +- 0.163775 (scaled MAD = 0.163777)
Result using spectral index of -0.593201 for 232.587 GHz from 3.175 Jy at 97.475 GHz = 1.895380 +- 0.163775 Jy

"""

"""
The input calibrator flux densities are all consistent with the catalog.  The input for SB1, EB2 is 3% lower than the catalog, but that's ok.
"""

"""
Here we export averaged visibilities to npz files and then plot the deprojected visibilities to compare the amplitude scales
"""

PA = 83.0 #these are the rough values pulled from Gaussian fitting and used for initial deprojection. They are NOT the final values used for subsequent data analysis
incl = 42.0
phasecenter = au.radec2deg('16:27:39.01000, -23.58.18.70000')
peakpos = au.radec2deg('16:27:39.003, -23.58.19.189')
offsets = au.angularSeparation(peakpos[0], peakpos[1], phasecenter[0], phasecenter[1], True)
"""
(0.00013842313427259945,
 -2.9166666650528839e-05,
 -0.00013583333333078469,
 -2.6650884759747529e-05)
"""
offx = 3600.*offsets[3]
offy = 3600.*offsets[2]


if not skip_plots:
    for msfile in [prefix+'_SB1_initcont_exec0.ms', prefix+'_SB1_initcont_exec1.ms', prefix+'_SB1_initcont_exec2.ms', prefix+'_LB1_initcont_exec0.ms', prefix+'_LB1_initcont_exec1.ms']:
        export_MS(msfile)
    #plot deprojected visibility profiles of all the execution blocks
    plot_deprojected([prefix+'_SB1_initcont_exec0.vis.npz', prefix+'_SB1_initcont_exec1.vis.npz', prefix+'_SB1_initcont_exec2.vis.npz', prefix+'_LB1_initcont_exec0.vis.npz', prefix+'_LB1_initcont_exec1.vis.npz'],
                     fluxscale=[1.00,1.00,1.00,1.00,1.00], offx = offx, offy = offy, PA = PA, incl = incl, show_err=False)

    estimate_flux_scale(reference = prefix+'_SB1_initcont_exec1.vis.npz', comparison = prefix+'_SB1_initcont_exec0.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
    #The ratio of the fluxes of DoAr33_SB1_initcont_exec0.vis.npz to DoAr33_SB1_initcont_exec1.vis.npz is 0.94679
    #The scaling factor for gencal is 0.973 for your comparison measurement
    #The error on the weighted mean ratio is 1.536e-03, although it's likely that the weights in the measurement sets are too off by some constant factor

    estimate_flux_scale(reference = prefix+'_SB1_initcont_exec1.vis.npz', comparison = prefix+'_SB1_initcont_exec2.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
    #The ratio of the fluxes of DoAr33_SB1_initcont_exec2.vis.npz to DoAr33_SB1_initcont_exec1.vis.npz is 0.98616
    #The scaling factor for gencal is 0.993 for your comparison measurement
    #The error on the weighted mean ratio is 1.464e-03, although it's likely that the weights in the measurement sets are too off by some constant factor

    estimate_flux_scale(reference = prefix+'_SB1_initcont_exec1.vis.npz', comparison = prefix+'_LB1_initcont_exec0.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
    #The ratio of the fluxes of DoAr33_LB1_initcont_exec0.vis.npz to DoAr33_SB1_initcont_exec1.vis.npz is 1.03436
    #The scaling factor for gencal is 1.017 for your comparison measurement
    #The error on the weighted mean ratio is 1.927e-03, although it's likely that the weights in the measurement sets are too off by some constant factor

    estimate_flux_scale(reference = prefix+'_SB1_initcont_exec1.vis.npz', comparison = prefix+'_LB1_initcont_exec1.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
    #The ratio of the fluxes of DoAr33_LB1_initcont_exec1.vis.npz to DoAr33_SB1_initcont_exec1.vis.npz is 0.94415
    #The scaling factor for gencal is 0.972 for your comparison measurement
    #The error on the weighted mean ratio is 2.421e-03, although it's likely that the weights in the measurement sets are too off by some constant factor

    #We replot the deprojected visibilities with rescaled factors to check that the values make sense
    plot_deprojected([prefix+'_SB1_initcont_exec0.vis.npz', prefix+'_SB1_initcont_exec1.vis.npz', prefix+'_SB1_initcont_exec2.vis.npz', prefix+'_LB1_initcont_exec0.vis.npz', prefix+'_LB1_initcont_exec1.vis.npz'],
                     fluxscale=[1/0.925, 1.00, 1.00, 1.00, 1/0.94], offx = offx, offy = offy, PA = PA, incl = incl, show_err=False)

#now correct the flux scales
rescale_flux(prefix+'_SB1_initcont_exec0.ms', [0.961])
rescale_flux(prefix+'_LB1_initcont_exec1.ms', [0.970])
#Splitting out rescaled values into new ms: DoAr33_XB1_initcont_execX_rescaled.ms

"""
Start of self-calibration of the short-baseline data 
"""
#merge the short-baseline execution blocks into a single MS
SB_cont_p0 = prefix+'_SB_contp0'
os.system('rm -rf %s*' % SB_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [prefix+'_SB1_initcont_exec0_rescaled.ms', prefix+'_SB1_initcont_exec1.ms', prefix+'_SB1_initcont_exec2.ms'], concatvis = SB_cont_p0+'.ms', dirtol = '0.1arcsec', copypointing = False) 

#make initial image
mask_semimajor = 0.70 #semimajor axis of mask in arcsec
mask_semiminor = 0.52 #semiminor axis of mask in arcsec
mask_angle = 83 #position angle of mask in degrees
mask_ra = '16h27m39.003s'
mask_dec = '-23.58.19.189'

common_mask = ['ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % (mask_ra, mask_dec, mask_semimajor, mask_semiminor, mask_angle), 
               'circle[[16h27m39.363s, -23d58m19.017s], 0.4arcsec]', 'circle[[16h27m38.845s, -23d58m26.047s], 0.4arcsec]']			# these circles deal with the flanking point sources
disk_mask = common_mask[0]

tclean_wrapper(vis = SB_cont_p0+'.ms', imagename = SB_cont_p0, mask = common_mask, scales = SB_scales, threshold = '0.15mJy', savemodel = 'modelcolumn')

noise_annulus ="annulus[[%s, %s],['%.2farcsec', '4.25arcsec']]" % (mask_ra, mask_dec, 1.1*mask_semimajor) #annulus over which we measure the noise. The inner radius is slightly larger than the semimajor axis of the mask (to add some buffer space around the mask) and the outer radius is set so that the annulus fits inside the long-baseline image size 
estimate_SNR(SB_cont_p0+'.image', disk_mask = disk_mask, noise_mask = noise_annulus)
#DoAr33_SB_contp0.image
#Beam 0.268 arcsec x 0.225 arcsec (87.06 deg)
#Flux inside disk mask: 34.60 mJy
#Peak intensity of source: 20.90 mJy/beam
#rms: 5.56e-02 mJy/beam
#Peak SNR: 375.78

"""
We need to select one or more reference antennae for gaincal

We first look at the CASA command log (or manual calibration script) to see how the reference antennae choices were ranked (weighted toward antennae close to the center of the array and with good SNR)
Note that gaincal will sometimes choose a different reference antenna than the one specified if it deems another one to be a better choice 

SB1, EB0: DV15, DV18, DA46, DA51, DV23
SB1, EB1: DA59, DA49, DA41, DA46, DA51
SB1, EB2: DA59, DA46, DA49, DA41, DA51
LB1, EB0: DA61, DA64, DA59, DA52, DV09
LB1, EB1: DA50, DA61, DV25, DV09, DV06

for SB1, refant = 'DA46, DA51'
***for all, refant = 'DA61, DV09, DA46'

"""

SB_contspws = '0~11' #change as appropriate
SB_refant = 'DA46, DA51' 
SB1_obs0_timerange = '2017/05/13/00~2017/05/15/00'
SB1_obs1_timerange = '2017/05/15/00~2017/05/18/00'
SB1_obs2_timerange = '2017/05/18/00~2017/05/20/00'
 

# It's useful to check that the phases for the refant look good in all execution blocks in plotms. However, plotms has a tendency to crash in CASA 5.1.1, so it might be necessary to use plotms in an older version of CASA 
#plotms(vis=SB_cont_p0, xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '0')
#plotms(vis=SB_cont_p0, xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '1')

#first round of phase self-cal for short baseline data
SB_p1 = prefix+'_SB.p1'
os.system('rm -rf '+SB_p1)
gaincal(vis=SB_cont_p0+'.ms' , caltable=SB_p1, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='p', solint='30s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [120s, 60s, 30s, 18s, 6s]

if not skip_plots:
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs1_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs2_timerange, plotrange=[0,0,-180,180])

applycal(vis=SB_cont_p0+'.ms', spw=SB_contspws, gaintable=[SB_p1], interp = 'linearPD', calwt = True)

SB_cont_p1 = prefix+'_SB_contp1'
os.system('rm -rf %s*' % SB_cont_p1)
split(vis=SB_cont_p0+'.ms', outputvis=SB_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p1+'.ms' , imagename = SB_cont_p1, mask = common_mask, scales = SB_scales, threshold = '0.1mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_p1+'.image', disk_mask = disk_mask, noise_mask = noise_annulus)
#DoAr33_SB_contp1.image
#Beam 0.269 arcsec x 0.225 arcsec (87.01 deg)
#Flux inside disk mask: 35.01 mJy
#Peak intensity of source: 22.50 mJy/beam
#rms: 3.13e-02 mJy/beam
#Peak SNR: 719.01


#second round of phase self-cal for short baseline data
SB_p2 = prefix+'_SB.p2'
os.system('rm -rf '+SB_p2)
gaincal(vis=SB_cont_p1+'.ms' , caltable=SB_p2, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='p', solint='18s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs1_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs2_timerange, plotrange=[0,0,-180,180])

applycal(vis=SB_cont_p1+'.ms', spw=SB_contspws, gaintable=[SB_p2], interp = 'linearPD', calwt = True)

SB_cont_p2 = prefix+'_SB_contp2'
os.system('rm -rf %s*' % SB_cont_p2)
split(vis=SB_cont_p1+'.ms', outputvis=SB_cont_p2+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p2+'.ms' , imagename = SB_cont_p2, mask = common_mask, scales = SB_scales, threshold = '0.07mJy', savemodel = 'modelcolumn') 
estimate_SNR(SB_cont_p2+'.image', disk_mask = disk_mask, noise_mask = noise_annulus)
#DoAr33_SB_contp2.image
#Beam 0.269 arcsec x 0.225 arcsec (86.67 deg)
#Flux inside disk mask: 35.06 mJy
#Peak intensity of source: 22.67 mJy/beam
#rms: 3.12e-02 mJy/beam
#Peak SNR: 725.99


#improvement over previous round of phase self-cal is marginal, so we move on to amp self-cal for the short baseline data 
SB_ap = prefix+'_SB.ap'
os.system('rm -rf '+SB_ap)
#note that the solint and minsnr are larger for amp self-cal
#try solnorm = False first. If that leads to bad solutions, try solnorm = True. If that still doesn't help, then just skip amp self-cal
gaincal(vis=SB_cont_p2+'.ms' , caltable=SB_ap, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='ap', solint='inf', minsnr=3.0, minblperant=4, solnorm = False) 

if not skip_plots:
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange, plotrange=[0,0,0,2])
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB1_obs1_timerange, plotrange=[0,0,0,2])
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB1_obs2_timerange, plotrange=[0,0,0,2])

applycal(vis=SB_cont_p2+'.ms', spw=SB_contspws, gaintable=[SB_ap], interp = 'linearPD', calwt = True)

SB_cont_ap = prefix+'_SB_contap'
os.system('rm -rf %s*' % SB_cont_ap)
split(vis=SB_cont_p2+'.ms', outputvis=SB_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_ap+'.ms' , imagename = SB_cont_ap, mask = common_mask, scales = SB_scales, threshold = '0.07mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_ap+'.image', disk_mask = disk_mask, noise_mask = noise_annulus)
#DoAr33_SB_contap.image
#Beam 0.270 arcsec x 0.224 arcsec (86.50 deg)
#Flux inside disk mask: 35.09 mJy
#Peak intensity of source: 22.62 mJy/beam
#rms: 2.88e-02 mJy/beam
#Peak SNR: 786.18


#now we concatenate all the data together

combined_cont_p0 = prefix+'_combined_contp0'
os.system('rm -rf %s*' % combined_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [SB_cont_ap+'.ms', prefix+'_LB1_initcont_exec0.ms', prefix+'_LB1_initcont_exec1_rescaled.ms'], concatvis = combined_cont_p0+'.ms' , dirtol = '0.1arcsec', copypointing = False) 

tclean_wrapper(vis = combined_cont_p0+'.ms' , imagename = combined_cont_p0, mask = common_mask, imsize=5600, scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn')	# increased imsize to get those point sources
estimate_SNR(combined_cont_p0+'.image', disk_mask = disk_mask, noise_mask = noise_annulus)
#DoAr33_combined_contp0.image
#Beam 0.043 arcsec x 0.024 arcsec (79.86 deg)
#Flux inside disk mask: 35.08 mJy
#Peak intensity of source: 1.78 mJy/beam
#rms: 1.42e-02 mJy/beam
#Peak SNR: 125.61


combined_refant = 'DA61@A015, DV25@A087, DA46@A034, DA51@A124'
combined_contspws = '0~19'
combined_spwmap =  [0,0,0,0,4,4,4,4,8,8,8,8,12,12,12,12,16,16,16,16] #note that the tables produced by gaincal in 5.1.1 have spectral windows numbered differently if you use the combine = 'spw' option. Previously, all of the solutions would be written to spectral window 0. Now, they are written to the first window in each execution block. So, the spwmap argument has to correspond to the first window in each execution block you want to calibrate. 

LB1_obs0_timerange = '2017/09/16/00~2017/09/19/00'
LB2_obs1_timerange = '2017/10/09/00~2017/10/11/00'

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

tclean_wrapper(vis = combined_cont_p1+'.ms' , imagename = combined_cont_p1, mask = common_mask, imsize=5600, scales = LB_scales, threshold = '0.04mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p1+'.image', disk_mask = disk_mask, noise_mask = noise_annulus)
#DoAr33_combined_contp1.image
#Beam 0.043 arcsec x 0.024 arcsec (79.86 deg)
#Flux inside disk mask: 34.96 mJy
#Peak intensity of source: 1.78 mJy/beam
#rms: 1.42e-02 mJy/beam
#Peak SNR: 124.84


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

tclean_wrapper(vis = combined_cont_p2+'.ms' , imagename = combined_cont_p2, mask = common_mask, imsize=5600, scales = LB_scales, threshold = '0.04mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p2+'.image', disk_mask = disk_mask, noise_mask = noise_annulus)
#DoAr33_combined_contp2.image
#Beam 0.043 arcsec x 0.024 arcsec (79.86 deg)
#Flux inside disk mask: 34.87 mJy
#Peak intensity of source: 1.82 mJy/beam
#rms: 1.41e-02 mJy/beam
#Peak SNR: 128.67

# improvement in SNR is small, but map quality is enhanced.


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

tclean_wrapper(vis = combined_cont_p3+'.ms' , imagename = combined_cont_p3, mask = common_mask, imsize=5600, scales = LB_scales, threshold = '0.04mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p3+'.image', disk_mask = disk_mask, noise_mask = noise_annulus)
#DoAr33_combined_contp3.image
#Beam 0.043 arcsec x 0.024 arcsec (79.86 deg)
#Flux inside disk mask: 34.72 mJy
#Peak intensity of source: 1.84 mJy/beam
#rms: 1.41e-02 mJy/beam
#Peak SNR: 130.60

# no improvement.  try amp self-cal


combined_ap = prefix+'_combined.ap'
os.system('rm -rf '+combined_ap)
gaincal(vis=combined_cont_p3+'.ms' , caltable=combined_ap, gaintype='T', combine = 'spw,scan', spw=combined_contspws, refant=combined_refant, calmode='ap', solint='900s', minsnr=3.0, minblperant=4, solnorm = False)

if not skip_plots:
    plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange, plotrange=[0,0,0,2]) 
    plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = LB2_obs1_timerange, plotrange=[0,0,0,2])

applycal(vis=combined_cont_p3+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_ap], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_ap = prefix+'_combined_contap'
os.system('rm -rf %s*' % combined_cont_ap)
split(vis=combined_cont_p3+'.ms', outputvis=combined_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_ap+'.ms' , imagename = combined_cont_ap, mask = common_mask, imsize=5600, scales = LB_scales, threshold = '0.03mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_ap+'.image', disk_mask = disk_mask, noise_mask = noise_annulus)

# with solnorm = False
#DoAr33_combined_contap.image
#Beam 0.043 arcsec x 0.024 arcsec (79.34 deg)
#Flux inside disk mask: 35.12 mJy
#Peak intensity of source: 1.74 mJy/beam
#rms: 1.37e-02 mJy/beam
#Peak SNR: 126.62

# both cases improve the RMS, but decrease the peak SNR.  However, the maps look better.  Will do the solnorm = False.


# try a map with robust = 0
tclean_wrapper(vis = combined_cont_ap+'.ms' , imagename = combined_cont_ap+'_rob0', mask = disk_mask, scales = LB_scales, robust=0.0, threshold = '0.03mJy')
