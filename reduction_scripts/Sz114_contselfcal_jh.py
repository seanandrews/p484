"""
This script was written for CASA 5.1.1

Datasets calibrated (in order of date observed):
SB1: 2016.1.00484.L/GW_Lup_a_06_TM1  
     Observed 14 May 2017 and 17 May 2017 (2 execution blocks)
     PI: S. Andrews)
     As delivered to PI
LB1: 2016.1.00484.L/Sz_114_a_06_TM1 
     Observed 26 September 2017
     PI: S. Andrews
     As delivered to PI

"""
import os

execfile('/pool/firebolt1/p484/reduction_scripts/reduction_utils.py')

skip_plots = True #if this is true, all of the plotting and inspection steps will be skipped and the script can be executed non-interactively in CASA if all relevant values have been hard-coded already 

#to fill this dictionary out, use listobs for the relevant measurement set 

prefix = 'Sz114' #string that identifies the source and is at the start of the name for all output files

#Note that if you are downloading data from the archive, your SPW numbering may differ from the SPWs in this script depending on how you split your data out!! 
data_params = {'SB1': {'vis' : '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_Xbd4641_X1e/group.uid___A001_Xbd4641_X1f/member.uid___A001_Xbd4641_X20/calibrated/calibrated_final.ms',
                       'name' : 'SB1',
                       'field': 'Sz_114',
                       'line_spws': np.array([0,4]), #SpwIDs of windows with lines that need to be flagged (this needs to be edited for each short baseline dataset)
                       'line_freqs': np.array([2.30538e11, 2.30538e11]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz)
                      }, #information about the short baseline measurement sets (SB1, SB2, SB3, etc in chronological order)
               'LB1': {'vis' : '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X88/group.uid___A001_X8c5_X89/member.uid___A001_X8c5_X8a/calibrated/calibrated_final.ms',
                       'name' : 'LB1',
                       'field' : 'Sz_114',
                       'line_spws': np.array([3]), #these are generally going to be the same for most of the long-baseline datasets. Some datasets only have one execution block or have strange numbering
                       'line_freqs': np.array([2.30538e11]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz) 
                      }
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
    flagchannels_string = get_flagchannels(data_params[i], prefix, velocity_range = np.array([0, 10]))
    """
    Produces spectrally averaged continuum datasets
    If you only want to include a subset of the windows, you can manually pass in values for contspw and width_array, e.g.
    avg_cont(data_params[i], output_prefix, flagchannels = flagchannels_string, contspws = '0~2', width_array = [480,8,8]).
    If you don't pass in values, all of the SPWs will be split out and the widths will be computed automatically to enforce a maximum channel width of 125 MHz.
    WARNING: Only use the avg_cont function if the total bandwidth is recorded correctly in the original MS. There is sometimes a bug in CASA that records incorrect total bandwidths
    """
    # Flagchannels input string for SB1: '0:1899~1931, 4:1899~1931'
    # Averaged continuum dataset saved to Sz114_SB1_initcont.ms
    # Flagchannels input string for LB1: '3:1905~1937'
    #Averaged continuum dataset saved to Sz114_LB1_initcont.ms
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
mask_radius = 0.8 #semiminor axis of mask in arcsec

SB1_mask = 'circle[[%s,%s],%.1f arcsec]' % ('16h09m01.834s', '-39.05.12.84', mask_radius)

LB1_mask = 'circle[[%s,%s],%.1f arcsec]' % ('16h09m01.834s', '-39.05.12.84', mask_radius)

SB_scales = [0, 5, 10, 15]
LB_scales = [0, 50, 100, 150]
"""
In this section, we are imaging every execution block to check spatial alignment 
"""

if not skip_plots:
    #images are saved in the format prefix+'_name_initcont_exec#.ms'
    image_each_obs(data_params['SB1'], prefix, mask = SB1_mask, scales = SB_scales, threshold = '0.2mJy', interactive = False)
    # inspection of images do not reveal additional bright background sources 

    tclean_wrapper(vis = prefix+'_LB1_initcont.ms', imagename = prefix+'_LB1_initcont', mask = LB1_mask, scales = LB_scales, threshold = '.075mJy', interactive = False)

    """
    Since the source looks axisymmetric, we will fit a Gaussian to the disk to estimate the location of the peak in each image and record the output.
    We are also very roughly estimating the PA and inclination for checking the flux scale offsets later (these are NOT the position angles and inclinations used for analysis of the final image products.
    Here, we are using the CLEAN mask to restrict the region over which the fit is occurring, but you may wish to shrink the region even further if your disk structure is complex 
    """

    fit_gaussian(prefix+'_SB1_initcont_exec0.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h09m01.834777s -39d05m12.82564s

    fit_gaussian(prefix+'_SB1_initcont_exec1.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h09m01.833125s -39d05m12.86043s

    fit_gaussian(prefix+'_LB1_initcont.image', region = LB1_mask) 
    #Peak of Gaussian component identified with imfit: ICRS 16h09m01.833722s -39d05m12.83809s
    #Peak in J2000 coordinates: 16:09:01.83407, -039:05:12.824319
    #PA of Gaussian component: 179.30 deg
    #Inclination of Gaussian component: 4.53 deg


"""
Since the individual execution blocks appear to be slightly misaligned, 
we will be splitting out the individual execution blocks, 
shifting them so that the image peaks fall on the phase center, 
reassigning the phase centers to a common direction (for ease of concat)
and imaging to check the shift  
"""

split_all_obs(prefix+'_SB1_initcont.ms', prefix+'_SB1_initcont_exec')
#Saving observation 0 of Sz114_SB1_initcont.ms to Sz114_SB1_initcont_exec0.ms
#Saving observation 1 of Sz114_SB1_initcont.ms to Sz114_SB1_initcont_exec1.ms

common_dir = 'J2000 16h09m01.83407 -039.05.12.824319' #choose peak of LB1 to be the common direction

#need to change to J2000 coordinates
mask_ra = '16h09m01.834s'
mask_dec = '-39.05.12.824'
common_mask = 'circle[[%s,%s],%.1f arcsec]' % (mask_ra, mask_dec, mask_radius)

shiftname = prefix+'_SB1_initcont_exec0_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_SB1_initcont_exec0.ms', outputvis=shiftname+'.ms', field = data_params['SB1']['field'], phasecenter='ICRS 16h09m01.834777s -39d05m12.82564s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['SB1']['field'], direction = common_dir) #fixplanets works only with J2000, not ICRS
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = SB_scales, threshold = '0.2mJy')
#Peak of Gaussian component identified with imfit: J2000 16h09m01.834066s -39d05m12.82436s

shiftname = prefix+'_SB1_initcont_exec1_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_SB1_initcont_exec1.ms', outputvis=shiftname+'.ms', field = data_params['SB1']['field'], phasecenter='ICRS 16h09m01.833125s -39d05m12.86043s')      
fixplanets(vis = shiftname+'.ms', field = data_params['SB1']['field'], direction = common_dir)
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = SB_scales, threshold = '0.2mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 16h09m01.834074s -39d05m12.82436s

shiftname = prefix+'_LB1_initcont_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_LB1_initcont.ms', outputvis=shiftname+'.ms', field = data_params['LB1']['field'], phasecenter='ICRS 16h09m01.833722s -39d05m12.83809s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['LB1']['field'], direction = common_dir)
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = LB_scales, threshold = '0.075mJy')
fit_gaussian(shiftname+'.image', region =  common_mask)
#Peak of Gaussian component identified with imfit: J2000 16h09m01.834066s -39d05m12.82433s
#PA of Gaussian component: 166.21 deg
#Inclination of Gaussian component: 5.27 deg

"""
After aligning the images, we want to check if the flux scales seem consistent between execution blocks (within ~5%)
First, we check the uid___xxxxx.casa_commands.log in the log directory of the data products folder (or the calibration script in the manual case) to check whether the calibrator catalog matches up with the input flux density values for the calibrators
(You should also check the plots of the calibrators in the data products to make sure that the amplitudes look consistent with the models that were inserted)
"""
#SB1, first execution
au.getALMAFlux('J1427-4206', frequency = '232.605GHz', date = '2017/05/14')

"""
Closest Band 3 measurement: 3.130 +- 0.080 (age=+0 days) 91.5 GHz
Closest Band 7 measurement: 1.450 +- 0.080 (age=-1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -1 days from 2017/05/14, with age separation of 0 days
  2017/05/15: freqs=[103.49, 91.46, 343.48], fluxes=[3.09, 3.16, 1.45]
Median Monte-Carlo result for 232.605000 = 1.864723 +- 0.160560 (scaled MAD = 0.161309)
Result using spectral index of -0.591033 for 232.605 GHz from 3.130 Jy at 91.460 GHz = 1.802796 +- 0.160560 Jy

Pipeline command: 
setjy(fluxdensity=[1.8028, 0.0, 0.0, 0.0], scalebychan=True,
      vis='uid___A002_Xc04da7_Xea.ms', spix=-0.591033389226, spw='19',
      field='J1427-4206', reffreq='232.605 GHz',
      intent='CALIBRATE_FLUX#ON_SOURCE', selectdata=True, standard='manual',
      usescratch=True)

Calibration is consistent with catalog
"""

#SB2, second execution
au.getALMAFlux('J1517-2422', frequency = '232.604GHz', date = '2017/05/17')
"""
Closest Band 3 measurement: 2.550 +- 0.060 (age=+2 days) 103.5 GHz
Closest Band 3 measurement: 2.490 +- 0.050 (age=+2 days) 91.5 GHz
Closest Band 7 measurement: 1.750 +- 0.060 (age=+0 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 2 days from 2017/05/17, with age separation of 0 days
  2017/05/15: freqs=[103.49, 91.46, 343.48], fluxes=[2.55, 2.49, 1.84]
Median Monte-Carlo result for 232.604000 = 2.042757 +- 0.161330 (scaled MAD = 0.159156)
Result using spectral index of -0.234794 for 232.604 GHz from 2.550 Jy at 103.490 GHz = 2.108428 +- 0.161330 Jy

Pipeline command:
setjy(fluxdensity=[2.1084, 0.0, 0.0, 0.0], scalebychan=True,
      vis='uid___A002_Xc067f7_Xa6d.ms', spix=-0.234793698802, spw='19',
      field='J1517-2422', reffreq='232.604 GHz',
      intent='CALIBRATE_FLUX#ON_SOURCE', selectdata=True, standard='manual',
      usescratch=True)

Calibration is consistent with catalog
"""

#LB1, first execution
au.getALMAFlux('J1733-1304', frequency = '232.528GHz', date = '2017/09/26')
"""
Closest Band 3 measurement: 3.070 +- 0.080 (age=-6 days) 103.5 GHz
Closest Band 3 measurement: 3.250 +- 0.090 (age=-6 days) 91.5 GHz
Closest Band 7 measurement: 1.290 +- 0.050 (age=+3 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -6 days from 2017/09/26, with age separation of 0 days
  2017/10/02: freqs=[103.49, 91.46, 343.48], fluxes=[3.07, 3.25, 1.49]
Median Monte-Carlo result for 232.528000 = 1.882544 +- 0.163158 (scaled MAD = 0.162947)
Result using spectral index of -0.593201 for 232.528 GHz from 3.070 Jy at 103.490 GHz = 1.899252 +- 0.163158 Jy
Out[140]: 
{'ageDifference': 9.0,
 'fluxDensity': 1.8992516882067969,
 'fluxDensityUncertainty': 0.16315791795600348,
 'meanAge': -6.0,
 'monteCarloFluxDensity': 1.8825435168956126,
 'spectralIndex': -0.59320129564531798,
 'spectralIndexAgeOldest': -6,
 'spectralIndexAgeSeparation': 0,
 'spectralIndexAgeYoungest': -6,
 'spectralIndexNPairs': 1,
 'spectralIndexUncertainty': 0.033328174142712823}

Consistent with pipeline log
"""


"""
Here we export averaged visibilities to npz files and then plot the deprojected visibilities to compare the amplitude scales
"""


PA = 180 #these are the rough values pulled from Gaussian fitting and used for initial deprojection. They are NOT the final values used for subsequent data analysis
incl = 4

if not skip_plots:
    for msfile in [prefix+'_SB1_initcont_exec0_shift.ms', prefix+'_SB1_initcont_exec1_shift.ms', prefix+'_LB1_initcont_shift.ms']:
        export_MS(msfile)
    #Measurement set exported to Sz114_SB1_initcont_exec0_shift.vis.npz
    #Measurement set exported to Sz114_SB1_initcont_exec1_shift.vis.npz
    #Measurement set exported to Sz114_LB1_initcont_shift.vis.npz

    #plot deprojected visibility profiles of all the execution blocks
    plot_deprojected([prefix+'_SB1_initcont_exec0_shift.vis.npz', prefix+'_SB1_initcont_exec1_shift.vis.npz', prefix+'_LB1_initcont_shift.vis.npz'],
                 PA = PA, incl = incl)
    #the executions are fairly close to one another, although LB1 is slightly higher than the other two

    #comparing LB1 to exec0 of SB1 (the higher S/N of the two)
    estimate_flux_scale(reference = prefix+'_SB1_initcont_exec0_shift.vis.npz', comparison = prefix+'_LB1_initcont_shift.vis.npz', incl = incl, PA = PA)

    #The ratio of the fluxes of Sz114_LB1_initcont_shift.vis.npz to Sz114_SB1_initcont_exec0_shift.vis.npz is 1.08375
    #The scaling factor for gencal is 1.041 for your comparison measurement
    #The error on the weighted mean ratio is 1.820e-03, although it's likely that the weights in the measurement sets are too off by some constant factor



    #We replot the deprojected visibilities with rescaled factors to check that the values make sense
    plot_deprojected([prefix+'_SB1_initcont_exec0_shift.vis.npz', prefix+'_SB1_initcont_exec1_shift.vis.npz', prefix+'_LB1_initcont_shift.vis.npz', ],
                 PA = PA, incl = incl, fluxscale = [1., 1., 1/1.08375])

#now correct the flux of the discrepant dataset
rescale_flux(prefix+'_LB1_initcont_shift.ms', [1.041])
#Splitting out rescaled values into new ms: Sz114_LB1_initcont_exec1_shift_rescaled.ms

"""
Start of self-calibration of the short-baseline data 
"""
#merge the short-baseline execution blocks into a single MS
SB_cont_p0 = prefix+'_SB_contp0'
os.system('rm -rf %s*' % SB_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [prefix+'_SB1_initcont_exec0_shift.ms', prefix+'_SB1_initcont_exec1_shift.ms'], concatvis = SB_cont_p0+'.ms', dirtol = '0.1arcsec', copypointing = False) 

#make initial image
tclean_wrapper(vis = SB_cont_p0+'.ms', imagename = SB_cont_p0, mask = common_mask, scales = SB_scales, threshold = '0.15mJy', savemodel = 'modelcolumn')

noise_annulus ="annulus[[%s, %s],['%.2farcsec', '4.25arcsec']]" % (mask_ra, mask_dec, 1.1*mask_radius) #annulus over which we measure the noise. The inner radius is slightly larger than the semimajor axis of the mask (to add some buffer space around the mask) and the outer radius is set so that the annulus fits inside the long-baseline image size 
estimate_SNR(SB_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Sz114_SB_contp0.image
#Beam 0.281 arcsec x 0.231 arcsec (-81.75 deg)
#Flux inside disk mask: 48.72 mJy
#Peak intensity of source: 19.07 mJy/beam
#rms: 4.88e-02 mJy/beam
#Peak SNR: 390.71


"""
We need to select one or more reference antennae for gaincal

We first look at the CASA command log (or manual calibration script) to see how the reference antennae choices were ranked (weighted toward antennae close to the center of the array and with good SNR)
Note that gaincal will sometimes choose a different reference antenna than the one specified if it deems another one to be a better choice 

First execution of SB1: DA49,DA59,DV18,DV15,DA46
Second execution of SB2: DA49,DA59,DV18,DV15,DA46
First execution of LB1: DV24,DA61,DA57,DA47,DV09

If you want to double check whether the antenna locations are reasonable, you can use something like plotants(vis = SB_cont_p0+'.ms')

"""

SB_contspws = '0~7' #change as appropriate
get_station_numbers(SB_cont_p0+'.ms', 'DV18')
#Observation ID 0: DV18@A009
#Observation ID 1: DV18@A009

SB_refant = 'DV18@A009' #DA49 and DA59 have a couple SPWs flagged in observation 0
SB1_obs0_timerange = '2017/05/14/00:00:01~2017/05/14/23:59:59' #change timerange as appropriate
SB1_obs1_timerange = '2017/05/17/00:00:01~2017/05/17/23:59:59'
 

# It's useful to check that the phases for the refant look good in all execution blocks in plotms. However, plotms has a tendency to crash in CASA 5.1.1, so it might be necessary to use plotms in an older version of CASA 
#plotms(vis=SB_cont_p0, xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '0')
#plotms(vis=SB_cont_p0, xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '1')

#first round of phase self-cal for short baseline data
SB_p1 = prefix+'_SB.p1'
os.system('rm -rf '+SB_p1)
gaincal(vis=SB_cont_p0+'.ms' , caltable=SB_p1, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='p', solint='30s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [120s, 60s, 30s, 18s, 6s]

if not skip_plots:
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange) 
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs1_timerange)

applycal(vis=SB_cont_p0+'.ms', spw=SB_contspws, gaintable=[SB_p1], interp = 'linearPD', calwt = True)

SB_cont_p1 = prefix+'_SB_contp1'
os.system('rm -rf %s*' % SB_cont_p1)
split(vis=SB_cont_p0+'.ms', outputvis=SB_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p1+'.ms' , imagename = SB_cont_p1, mask = common_mask, scales = SB_scales, threshold = '0.09mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Sz114_SB_contp1.image
#Beam 0.281 arcsec x 0.231 arcsec (-81.75 deg)
#Flux inside disk mask: 49.96 mJy
#Peak intensity of source: 20.76 mJy/beam
#rms: 3.22e-02 mJy/beam
#Peak SNR: 645.11



#second round of phase self-cal for short baseline data
SB_p2 = prefix+'_SB.p2'
os.system('rm -rf '+SB_p2)
gaincal(vis=SB_cont_p1+'.ms' , caltable=SB_p2, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='p', solint='18s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange) 
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs1_timerange)

applycal(vis=SB_cont_p1+'.ms', spw=SB_contspws, gaintable=[SB_p2], interp = 'linearPD', calwt = True)

SB_cont_p2 = prefix+'_SB_contp2'
os.system('rm -rf %s*' % SB_cont_p2)
split(vis=SB_cont_p1+'.ms', outputvis=SB_cont_p2+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p2+'.ms' , imagename = SB_cont_p2, mask = common_mask, scales = SB_scales, threshold = '0.09mJy', savemodel = 'modelcolumn') 
estimate_SNR(SB_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Sz114_SB_contp2.image
#Beam 0.281 arcsec x 0.231 arcsec (-81.69 deg)
#Flux inside disk mask: 50.01 mJy
#Peak intensity of source: 20.95 mJy/beam
#rms: 3.23e-02 mJy/beam
#Peak SNR: 649.14


#improvement over previous round of phase self-cal is marginal, so we move on to amp self-cal for the short baseline data 
SB_ap = prefix+'_SB.ap'
os.system('rm -rf '+SB_ap)
#note that the solint and minsnr are larger for amp self-cal
#try solnorm = False first. If that leads to bad solutions, try solnorm = True. If that still doesn't help, then just skip amp self-cal
gaincal(vis=SB_cont_p2+'.ms' , caltable=SB_ap, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='ap', solint='inf', minsnr=3.0, minblperant=4, solnorm = False) 

if not skip_plots:
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange) 
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange)

applycal(vis=SB_cont_p2+'.ms', spw=SB_contspws, gaintable=[SB_ap], interp = 'linearPD', calwt = True)

SB_cont_ap = prefix+'_SB_contap'
os.system('rm -rf %s*' % SB_cont_ap)
split(vis=SB_cont_p2+'.ms', outputvis=SB_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_ap+'.ms' , imagename = SB_cont_ap, mask = common_mask, scales = SB_scales, threshold = '0.09mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Sz114_SB_contap.image
#Beam 0.283 arcsec x 0.232 arcsec (-81.55 deg)
#Flux inside disk mask: 49.26 mJy
#Peak intensity of source: 20.95 mJy/beam
#rms: 3.02e-02 mJy/beam
#Peak SNR: 693.05



#now we concatenate all the data together

combined_cont_p0 = prefix+'_combined_contp0'
os.system('rm -rf %s*' % combined_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [SB_cont_ap+'.ms', prefix+'_LB1_initcont_shift_rescaled.ms'], concatvis = combined_cont_p0+'.ms' , dirtol = '0.1arcsec', copypointing = False) 

tclean_wrapper(vis = combined_cont_p0+'.ms' , imagename = combined_cont_p0, mask = common_mask, scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Sz114_combined_contp0.image
#Beam 0.067 arcsec x 0.028 arcsec (-88.04 deg)
#Flux inside disk mask: 49.64 mJy
#Peak intensity of source: 3.31 mJy/beam
#rms: 1.90e-02 mJy/beam
#Peak SNR: 173.76

get_station_numbers(combined_cont_p0+'.ms', 'DV24')
#Observation ID 0: DV24@A077
#Observation ID 1: DV24@A077
#Observation ID 2: DV24@A090

#we want to choose DV24 for the long-baseline refant

combined_refant = 'DV24@A090, DV18@A009'
combined_contspws = '0~11'
combined_spwmap =  [0,0,0,0,4,4,4,4,8,8,8,8] #note that the tables produced by gaincal in 5.1.1 have spectral windows numbered differently if you use the combine = 'spw' option. Previously, all of the solutions would be written to spectral window 0. Now, they are written to the first window in each execution block. So, the spwmap argument has to correspond to the first window in each execution block you want to calibrate. 

LB1_obs0_timerange = '2017/09/26/00:00:01~2017/09/26/23:59:59'

#first round of phase self-cal for long baseline data
combined_p1 = prefix+'_combined.p1'
os.system('rm -rf '+combined_p1)
gaincal(vis=combined_cont_p0+'.ms' , caltable=combined_p1, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='360s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [900s, 360s, 180s, 60s, 30s, 6s]

if not skip_plots:
    plotcal(caltable=combined_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 

applycal(vis=combined_cont_p0+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p1], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p1 = prefix+'_combined_contp1'
os.system('rm -rf %s*' % combined_cont_p1)
split(vis=combined_cont_p0+'.ms', outputvis=combined_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p1+'.ms' , imagename = combined_cont_p1, mask = common_mask, scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Sz114_combined_contp1.image
#Beam 0.067 arcsec x 0.028 arcsec (-88.04 deg)
#Flux inside disk mask: 49.24 mJy
#Peak intensity of source: 3.33 mJy/beam
#rms: 1.89e-02 mJy/beam
#Peak SNR: 175.54




#second round of phase self-cal for long baseline data
combined_p2 = prefix+'_combined.p2'
os.system('rm -rf '+combined_p2)
gaincal(vis=combined_cont_p1+'.ms' , caltable=combined_p2, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='180s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 

applycal(vis=combined_cont_p1+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p2], interp = 'linearPD', calwt = True, applymode = 'calonly')


combined_cont_p2 = prefix+'_combined_contp2'
os.system('rm -rf %s*' % combined_cont_p2)
split(vis=combined_cont_p1+'.ms', outputvis=combined_cont_p2+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p2+'.ms' , imagename = combined_cont_p2, mask =common_mask, scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#Sz114_combined_contp2.image
#Beam 0.067 arcsec x 0.028 arcsec (-88.04 deg)
#Flux inside disk mask: 49.27 mJy
#Peak intensity of source: 3.36 mJy/beam
#rms: 1.89e-02 mJy/beam
#Peak SNR: 178.15


#additional phase self-cal and amp self-cal appears to make things worse for GW Lup
#uncomment the lines below if you wish to perform amp self-cal for your source specifically

"""
combined_ap = prefix+'_combined.ap'
os.system('rm -rf '+combined_ap)
gaincal(vis=combined_cont_p2+'.ms' , caltable=combined_ap, gaintype='T', combine = 'spw,scan', spw=combined_contspws, refant=combined_refant, calmode='ap', solint='900s', minsnr=3.0, minblperant=4, solnorm = False)

if not skip_plots:
    plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 

applycal(vis=combined_cont_p2+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_ap], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_ap = prefix+'_combined_contap'
os.system('rm -rf %s*' % combined_cont_ap)
split(vis=combined_cont_p2+'.ms', outputvis=combined_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_ap+'.ms' , imagename = combined_cont_ap, mask =common_mask, scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
"""



