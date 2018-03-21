"""
This script was written for CASA 5.1.1
Datasets calibrated (in order of date observed):
SB1: 2016.1.00484.L/
     Observed 14/May/2017 17/May/2017
     PI: S. Andrews
     As delivered to PI
LB1: 2016.1.00484.L/
     Observed 24/Sep/2017 25/Nov/2017
     PI: S. Andrews
     As delivered to PI
"""
import os

execfile('/home/shared/ALMA_data/p484_large/reduction_utils.py')

skip_plots = False #if this is true, all of the plotting and inspection steps will be skipped and the script can be executed non-interactively in CASA if all relevant values have been hard-coded already 

#to fill this dictionary out, use listobs for the relevant measurement set 

prefix = 'MYLup' #string that identifies the source and is at the start of the name for all output files

#Note that if you are downloading data from the archive, your SPW numbering may differ from the SPWs in this script depending on how you split your data out!! 
data_params = {'SB1': {'vis' : '/home/shared/ALMA_data/p484_large/mylup/calibrated_msfiles/calibrated_final_SB.ms',
                       'name' : 'SB1',
                       'field': 'MY_Lup',
                       'line_spws': np.array([0,4]), #SpwIDs of windows with lines that need to be flagged (this needs to be edited for each short baseline dataset)
                       'line_freqs': np.array([2.30538e11, 2.30538e11]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz)
                      }, #information about the short baseline measurement sets (SB1, SB2, SB3, etc in chronological order)
               'LB1': {'vis' : '/home/shared/ALMA_data/p484_large/mylup/calibrated_msfiles/calibrated_final_LB.ms', 
                       'name' : 'LB1',
                       'field' : 'MY_Lupi',
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
    flagchannels_string = get_flagchannels(data_params[i], prefix, velocity_range = np.array([-5, 15]))
    """
    Produces spectrally averaged continuum datasets
    If you only want to include a subset of the windows, you can manually pass in values for contspw and width_array, e.g.
    avg_cont(data_params[i], output_prefix, flagchannels = flagchannels_string, contspws = '0~2', width_array = [480,8,8]).
    If you don't pass in values, all of the SPWs will be split out and the widths will be computed automatically to enforce a maximum channel width of 125 MHz.
    WARNING: Only use the avg_cont function if the total bandwidth is recorded correctly in the original MS. There is sometimes a bug in CASA that records incorrect total bandwidths
    """
    # Flagchannels input string for SB1: '0:1889~1952, 4:1889~1952'
    # Averaged continuum dataset saved to MYLup_SB1_initcont.ms
    # Flagchannels input string for LB1: '3:1890~1953, 7:1890~1953'
    # Averaged continuum dataset saved to MYLup_LB1_initcont.ms
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
mask_angle = 59 #position angle of mask in degrees
mask_semimajor = 1.0 #semimajor axis of mask in arcsec
mask_semiminor = 0.6 #semiminor axis of mask in arcsec
mask_ra = '16h00m44.50s'
mask_dec = '-41.55.31.34'

SB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % (mask_ra, mask_dec, mask_semimajor, mask_semiminor, mask_angle)

LB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % (mask_ra, mask_dec, mask_semimajor, mask_semiminor, mask_angle)

common_mask = LB1_mask


SB_scales = [0, 5, 10]
LB_scales = [0, 10, 30, 90, 270]
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
    #Peak of Gaussian component identified with imfit: ICRS 16h00m44.502359s -41d55m31.32430s
    #Peak in J2000 coordinates: 16:00:44.50267, -041:55:31.310122
    #Pixel coordinates of peak: x = 452.196 y = 452.446
    #PA of Gaussian component: 58.76 deg
    #Inclination of Gaussian component: 73.05 deg

    fit_gaussian(prefix+'_SB1_initcont_exec1.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h00m44.498646s -41d55m31.34984s
    #Peak in J2000 coordinates: 16:00:44.49896, -041:55:31.335661
    #Pixel coordinates of peak: x = 453.577 y = 451.594
    #PA of Gaussian component: 59.05 deg
    #Inclination of Gaussian component: 68.43 deg

    fit_gaussian(prefix+'_LB1_initcont_exec0.image', region = LB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h00m44.500993s -41d55m31.33852s
    #Peak in J2000 coordinates: 16:00:44.50131, -041:55:31.324341
    #Pixel coordinates of peak: x = 1525.649 y = 1522.513
    #PA of Gaussian component: 58.89 deg
    #Inclination of Gaussian component: 73.24 deg
    
    fit_gaussian(prefix+'_LB1_initcont_exec1.image', region = LB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h00m44.501227s -41d55m31.34468s
    #Peak in J2000 coordinates: 16:00:44.50154, -041:55:31.330502
    #Pixel coordinates of peak: x = 1524.138 y = 1521.749
    #PA of Gaussian component: 59.07 deg
    #Inclination of Gaussian component: 73.37 deg


"""
The individual execution blocks are all in alignment.  Now check if the flux scales seem consistent between execution blocks (within ~5%)
"""

split_all_obs(prefix+'_SB1_initcont.ms', prefix+'_SB1_initcont_exec')
split_all_obs(prefix+'_LB1_initcont.ms', prefix+'_LB1_initcont_exec')

"""
First, check the pipeline outputs (STEP11/12, hif_setjy or hif_setmodels in the TASKS list of the qa products) to check whether the calibrator catalog matches up with the input flux density values for the calibrators.
(Also check the corresponding plots.)
        SB1, EB0: J1427-4206 = 1.803 Jy at 232.605 GHz - 14/May/2017
	SB1, EB1: J1517-2422 = 2.108 Jy at 232.604 GHz - 17/May/2017
        LB1, EB0: J1617-5848 = 0.5812 Jy at 232.585 GHz - 24/Sep/2017
	LB1, EB1: J1617-5848 = 0.4843 Jy at 232.599 GHz - 25/Nov/2017
Now can check that these inputs are matching the current calibrator catalog:
"""
au.getALMAFlux('J1427-4206', frequency = '232.605GHz', date = '2017/05/14')	# SB1, EB0
au.getALMAFlux('J1517-2422', frequency = '232.604GHz', date = '2017/05/17')     # SB1, EB1
au.getALMAFlux('J1617-5848', frequency = '232.585GHz', date = '2017/09/24')     # LB1, EB0
au.getALMAFlux('J1617-5848', frequency = '232.599GHz', date = '2017/11/25')     # LB1, EB1

"""
SB1, EB0:
Closest Band 3 measurement: 3.130 +- 0.080 (age=+0 days) 91.5 GHz
Closest Band 7 measurement: 1.450 +- 0.080 (age=-1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -1 days from 2017/05/14, with age separation of 0 days
  2017/05/15: freqs=[103.49, 91.46, 343.48], fluxes=[3.09, 3.16, 1.45]
Median Monte-Carlo result for 232.605000 = 1.861600 +- 0.162910 (scaled MAD = 0.157547)
Result using spectral index of -0.591033 for 232.605 GHz from 3.130 Jy at 91.460 GHz = 1.802796 +- 0.162910 Jy

SB1, EB1:
losest Band 3 measurement: 2.550 +- 0.060 (age=+2 days) 103.5 GHz
Closest Band 3 measurement: 2.490 +- 0.050 (age=+2 days) 91.5 GHz
Closest Band 7 measurement: 1.750 +- 0.060 (age=+0 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 2 days from 2017/05/17, with age separation of 0 days
  2017/05/15: freqs=[103.49, 91.46, 343.48], fluxes=[2.55, 2.49, 1.84]
Median Monte-Carlo result for 232.604000 = 2.039469 +- 0.158096 (scaled MAD = 0.159334)
Result using spectral index of -0.234794 for 232.604 GHz from 2.520 Jy at 97.475 GHz = 2.054534 +- 0.158096 Jy

LB1, EB0:
Closest Band 3 measurement: 1.120 +- 0.070 (age=+7 days) 103.5 GHz
Closest Band 3 measurement: 1.160 +- 0.060 (age=+7 days) 91.5 GHz
Closest Band 7 measurement: 0.360 +- 0.030 (age=+1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -8 days from 2017/09/24, with age separation of 0 days
  2017/10/02: freqs=[91.46, 103.49, 343.48], fluxes=[1.11, 1.03, 0.4]
Median Monte-Carlo result for 232.585000 = 0.544032 +- 0.088701 (scaled MAD = 0.086554)
Result using spectral index of -0.774750 for 232.585 GHz from 1.140 Jy at 97.475 GHz = 0.581153 +- 0.088701 Jy

LB1, EB1:
Closest Band 3 measurement: 1.130 +- 0.030 (age=+2 days) 91.5 GHz
Closest Band 7 measurement: 0.340 +- 0.030 (age=+2 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 2 days from 2017/11/25, with age separation of 0 days
  2017/11/23: freqs=[91.46, 343.48], fluxes=[1.13, 0.34]
Median Monte-Carlo result for 232.599000 = 0.483957 +- 0.071850 (scaled MAD = 0.070817)
Result using spectral index of -0.907650 for 232.599 GHz from 1.130 Jy at 91.460 GHz = 0.484327 +- 0.071850 Jy

"""

"""
Here we export averaged visibilities to npz files and then plot the deprojected visibilities to compare the amplitude scales
"""

PA = 59.0 #these are the rough values pulled from Gaussian fitting and used for initial deprojection. They are NOT the final values used for subsequent data analysis
incl = 73.0
phasecenter = au.radec2deg('16:00:44.510, -041:55:31.413')
peakpos = au.radec2deg('16:00:44.50131, -041:55:31.324341')
offsets = au.angularSeparation(peakpos[0], peakpos[1], phasecenter[0], phasecenter[1], True)

"""
3.6500054808989134e-05, -3.6208333394866967e-05, 2.46275000038053e-05, -2.6939566521118778e-05
"""
offx = 3600.*offsets[3]
offy = 3600.*offsets[2]


if not skip_plots:
    for msfile in [prefix+'_SB1_initcont_exec0.ms', prefix+'_SB1_initcont_exec1.ms', prefix+'_LB1_initcont_exec0.ms', prefix+'_LB1_initcont_exec1.ms']:
        export_MS(msfile)
    #plot deprojected visibility profiles of all the execution blocks
    plot_deprojected([prefix+'_SB1_initcont_exec0.vis.npz', prefix+'_SB1_initcont_exec1.vis.npz', prefix+'_LB1_initcont_exec0.vis.npz', prefix+'_LB1_initcont_exec1.vis.npz'], fluxscale=[1.00,1.00,0.9,1.15], offx = offx, offy = offy, PA = PA, incl = incl, show_err=False)
    
    # LB1-EB0 and LB1-EB1 differs by ~30%, while SB1-EB0 and SB1-EB1 agrees and have fluxes in between those of the long baselines obs. 
    # So, we use the short baseline tracks as references. 

    estimate_flux_scale(reference = prefix+'_SB1_initcont_exec0.vis.npz', comparison = prefix+'_SB1_initcont_exec1.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
    #The ratio of the fluxes of MYLup_SB1_initcont_exec1.vis.npz to MYLup_SB1_initcont_exec0.vis.npz is 1.00868
    #The scaling factor for gencal is 1.004 for your comparison measurement
    #The error on the weighted mean ratio is 8.125e-04, although it's likely that the weights in the measurement sets are too off by some constant factor

    estimate_flux_scale(reference = prefix+'_LB1_initcont_exec0.vis.npz', comparison = prefix+'_LB1_initcont_exec1.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
   #The ratio of the fluxes of MYLup_LB1_initcont_exec1.vis.npz to MYLup_LB1_initcont_exec0.vis.npz is 0.74844
   #The scaling factor for gencal is 0.865 for your comparison measurement
   #The error on the weighted mean ratio is 8.064e-04, although it's likely that the weights in the measurement sets are too off by some constant factor

    estimate_flux_scale(reference = prefix+'_SB1_initcont_exec0.vis.npz', comparison = prefix+'_LB1_initcont_exec0.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
    #The ratio of the fluxes of MYLup_LB1_initcont_exec0.vis.npz to MYLup_SB1_initcont_exec0.vis.npz is 1.10652
    #The scaling factor for gencal is 1.052 for your comparison measurement
    #The error on the weighted mean ratio is 1.359e-03, although it's likely that the weights in the measurement sets are too off by some constant factor

    estimate_flux_scale(reference = prefix+'_SB1_initcont_exec0.vis.npz', comparison = prefix+'_LB1_initcont_exec1.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
    #The ratio of the fluxes of MYLup_LB1_initcont_exec1.vis.npz to MYLup_SB1_initcont_exec0.vis.npz is 0.83530
    #The scaling factor for gencal is 0.914 for your comparison measurement
    #The error on the weighted mean ratio is 8.194e-04, although it's likely that the weights in the measurement sets are too off by some constant factor


    #We replot the deprojected visibilities with rescaled factors to check that the values make sense
    plot_deprojected([prefix+'_SB1_initcont_exec0.vis.npz', prefix+'_SB1_initcont_exec1.vis.npz', prefix+'_LB1_initcont_exec0.vis.npz', prefix+'_LB1_initcont_exec1.vis.npz'],
                     fluxscale=[1, 1, 1/1.10652, 1/0.83530], offx = offx, offy = offy, PA = PA, incl = incl, show_err=False)

#now correct the flux scales
rescale_flux(prefix+'_LB1_initcont_exec0.ms', [1.052])
rescale_flux(prefix+'_LB1_initcont_exec1.ms', [0.914])
#Splitting out rescaled values into new MS: MYLup_LB1_initcont_exec0_rescaled.ms
#Splitting out rescaled values into new MS: MYLup_LB1_initcont_exec1_rescaled.ms

#OPTIONAL: check that the rescaling was successfull
export_MS('MYLup_LB1_initcont_exec0_rescaled.ms')
export_MS('MYLup_LB1_initcont_exec1_rescaled.ms')
plot_deprojected([prefix+'_SB1_initcont_exec0.vis.npz', prefix+'_SB1_initcont_exec1.vis.npz', prefix+'_LB1_initcont_exec0_rescaled.vis.npz', prefix+'_LB1_initcont_exec1_rescaled.vis.npz'],
                     fluxscale=[1, 1, 1, 1], offx = offx, offy = offy, PA = PA, incl = incl, show_err=True)

"""
Start of self-calibration of the short-baseline data 
"""
#merge the short-baseline execution blocks into a single MS
SB_cont_p0 = prefix+'_SB_contp0'
os.system('rm -rf %s*' % SB_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [prefix+'_SB1_initcont_exec0.ms', prefix+'_SB1_initcont_exec1.ms'], concatvis = SB_cont_p0+'.ms', dirtol = '0.1arcsec', copypointing = False) 

#make initial image
tclean_wrapper(vis = SB_cont_p0+'.ms', imagename = SB_cont_p0, mask = common_mask, scales = SB_scales, threshold = '0.15mJy', savemodel = 'modelcolumn')

noise_annulus ="annulus[[%s, %s],['%.2farcsec', '4.25arcsec']]" % (mask_ra, mask_dec, 1.1*mask_semimajor) #annulus over which we measure the noise. The inner radius is slightly larger than the semimajor axis of the mask (to add some buffer space around the mask) and the outer radius is set so that the annulus fits inside the long-baseline image size 
estimate_SNR(SB_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#MYLup_SB_contp0.image
#Beam 0.276 arcsec x 0.235 arcsec (-78.60 deg)
#Flux inside disk mask: 76.81 mJy
#Peak intensity of source: 24.94 mJy/beam
#rms: 8.04e-02 mJy/beam
#Peak SNR: 310.10

"""
We need to select one or more reference antennae for gaincal
We first look at the CASA command log (or manual calibration script) to see how the reference antennae choices were ranked (weighted toward antennae close to the center of the array and with good SNR)
Note that gaincal will sometimes choose a different reference antenna than the one specified if it deems another one to be a better choice 
SB1, EB0: DA49, DA59, DV18, DV15, DA46, DA51, DV23, DA61
SB1, EB1: DA59, DA49, DA41, DA51, DV18, DV23, DA46, DA61
LB1, EB0: DV24, DV09, DV20, DA61, DV25, DA57, DV14, PM02
LB1, EB1: DV08, DV20, DV06, DV24, DA63, DV09, DA52, DA54
for SB1, refant = 'DA46, DA51'
for all, refant = 'DA61, DV09'
"""

SB_contspws = '0~7' #change as appropriate

#get_station_numbers('MYLup_SB_contp0.ms','DA49')
#get_station_numbers('MYLup_SB_contp0.ms','DA59')
SB_refant = 'DA49@A002, DA59@A001' 

SB1_obs0_timerange = '2017/05/14/00~2017/05/15/00'
SB1_obs1_timerange = '2017/05/15/00~2017/05/19/00'


# It's useful to check that the phases for the refant look good in all execution blocks in plotms. However, plotms has a tendency to crash in CASA 5.1.1, so it might be necessary to use plotms in an older version of CASA 
#plotms(vis=SB_cont_p0+'.ms', xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '0')
#plotms(vis=SB_cont_p0+'.ms', xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '1')

#first round of phase self-cal for short baseline data
SB_p1 = prefix+'_SB.p1'
os.system('rm -rf '+SB_p1)
gaincal(vis=SB_cont_p0+'.ms' , caltable=SB_p1, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='p', solint='60s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [120s, 60s, 30s, 18s, 6s]

if not skip_plots:
    plotcal(caltable=SB_p1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = SB1_obs0_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=SB_p1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', timerange = SB1_obs1_timerange, plotrange=[0,0,-180,180])
    

applycal(vis=SB_cont_p0+'.ms', spw=SB_contspws, gaintable=[SB_p1], interp = 'linearPD', calwt = True)

SB_cont_p1 = prefix+'_SB_contp1'
os.system('rm -rf %s*' % SB_cont_p1)
split(vis=SB_cont_p0+'.ms', outputvis=SB_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p1+'.ms' , imagename = SB_cont_p1, mask = common_mask, scales = SB_scales, threshold = '0.1mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#MYLup_SB_contp1.image
#Beam 0.276 arcsec x 0.235 arcsec (-78.60 deg)
#Flux inside disk mask: 77.66 mJy
#Peak intensity of source: 26.47 mJy/beam
#rms: 3.74e-02 mJy/beam
#Peak SNR: 708.21



#second round of phase self-cal for short baseline data
SB_p2 = prefix+'_SB.p2'
os.system('rm -rf '+SB_p2)
gaincal(vis=SB_cont_p1+'.ms' , caltable=SB_p2, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='p', solint='30s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs1_timerange, plotrange=[0,0,-180,180])
   

applycal(vis=SB_cont_p1+'.ms', spw=SB_contspws, gaintable=[SB_p2], interp = 'linearPD', calwt = True)

SB_cont_p2 = prefix+'_SB_contp2'
os.system('rm -rf %s*' % SB_cont_p2)
split(vis=SB_cont_p1+'.ms', outputvis=SB_cont_p2+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p2+'.ms' , imagename = SB_cont_p2, mask = common_mask, scales = SB_scales, threshold = '0.07mJy', savemodel = 'modelcolumn') 
estimate_SNR(SB_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
MYLup_SB_contp2.image
#Beam 0.276 arcsec x 0.235 arcsec (-79.15 deg)
#Flux inside disk mask: 77.78 mJy
#Peak intensity of source: 26.83 mJy/beam
#rms: 3.72e-02 mJy/beam
#Peak SNR: 720.36

#third round of phase self-cal for short baseline data
SB_p3 = prefix+'_SB.p3'
os.system('rm -rf '+SB_p3)
gaincal(vis=SB_cont_p2+'.ms' , caltable=SB_p3, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='p', solint='18s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs1_timerange, plotrange=[0,0,-180,180])
   

applycal(vis=SB_cont_p2+'.ms', spw=SB_contspws, gaintable=[SB_p3], interp = 'linearPD', calwt = True)

SB_cont_p3 = prefix+'_SB_contp3'
os.system('rm -rf %s*' % SB_cont_p3)
split(vis=SB_cont_p2+'.ms', outputvis=SB_cont_p3+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p3+'.ms' , imagename = SB_cont_p3, mask = common_mask, scales = SB_scales, threshold = '0.07mJy', savemodel = 'modelcolumn') 
estimate_SNR(SB_cont_p3+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#MYLup_SB_contp3.image
#Beam 0.278 arcsec x 0.237 arcsec (-82.02 deg)
#Flux inside disk mask: 77.92 mJy
#Peak intensity of source: 27.28 mJy/beam
#rms: 3.81e-02 mJy/beam
#Peak SNR: 716.93

#noise rms and SNR ratio is worse compared to the previous cycle. Proceeding using results from cycle 2

SB_ap = prefix+'_SB.ap'
os.system('rm -rf '+SB_ap)
#note that the solint and minsnr are larger for amp self-cal
#try solnorm = False first. If that leads to bad solutions, try solnorm = True. If that still doesn't help, then just skip amp self-cal
gaincal(vis=SB_cont_p2+'.ms' , caltable=SB_ap, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='ap', solint='inf', minsnr=3.0, minblperant=4, solnorm = False) 

if not skip_plots:
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange, plotrange=[0,0,0,2])
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB1_obs1_timerange, plotrange=[0,0,0,2])
    

applycal(vis=SB_cont_p2+'.ms', spw=SB_contspws, gaintable=[SB_ap], interp = 'linearPD', calwt = True)

SB_cont_ap = prefix+'_SB_contap'
os.system('rm -rf %s*' % SB_cont_ap)
split(vis=SB_cont_p2+'.ms', outputvis=SB_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_ap+'.ms' , imagename = SB_cont_ap, mask = common_mask, scales = SB_scales, threshold = '0.07mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#MYLup_SB_contap.image
#Beam 0.279 arcsec x 0.236 arcsec (-81.50 deg)
#Flux inside disk mask: 77.48 mJy
#Peak intensity of source: 27.15 mJy/beam
#rms: 3.33e-02 mJy/beam
#Peak SNR: 815.27

# Make a test image with higher angular resolution
#tclean_wrapper(vis = SB_cont_ap+'.ms' , imagename = SB_cont_ap+'rn2', mask = common_mask, scales = SB_scales, threshold = '0.07mJy', savemodel = 'modelcolumn', robust=-2)

#now we concatenate all the data together

combined_cont_p0 = prefix+'_combined_contp0'
os.system('rm -rf %s*' % combined_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [SB_cont_ap+'.ms', prefix+'_LB1_initcont_exec0_rescaled.ms', prefix+'_LB1_initcont_exec1_rescaled.ms'], concatvis = combined_cont_p0+'.ms' , dirtol = '0.1arcsec', copypointing = False) 

tclean_wrapper(vis = combined_cont_p0+'.ms' , imagename = combined_cont_p0, mask = common_mask, scales = LB_scales, threshold = '0.10mJy', savemodel = 'modelcolumn', uvtaper=['0.04arcsec'], interactive=True)
estimate_SNR(combined_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#MYLup_combined_contp0.image
#Beam 0.072 arcsec x 0.057 arcsec (74.79 deg)
#Flux inside disk mask: 78.06 mJy
#Peak intensity of source: 3.36 mJy/beam
#rms: 1.51e-02 mJy/beam
#Peak SNR: 222.69



combined_refant = 'DA49@A002, DA59@A001, DV24@A090, DV08@A042'
combined_contspws = '0~15'
combined_spwmap =  [0,0,0,0,4,4,4,4,8,8,8,8,12,12,12,12] #note that the tables produced by gaincal in 5.1.1 have spectral windows numbered differently if you use the combine = 'spw' option. Previously, all of the solutions would be written to spectral window 0. Now, they are written to the first window in each execution block. So, the spwmap argument has to correspond to the first window in each execution block you want to calibrate. 

LB1_obs0_timerange = '2017/09/23/00~2017/09/25/00'
LB2_obs1_timerange = '2017/11/24/00~2017/11/27/00'

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

tclean_wrapper(vis = combined_cont_p1+'.ms' , imagename = combined_cont_p1, uvtaper=['0.04arcsec'], mask = common_mask, scales = LB_scales, threshold = '0.10mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)

#MYLup_combined_contp1.image
#Beam 0.072 arcsec x 0.057 arcsec (74.79 deg)
#Flux inside disk mask: 78.01 mJy
#Peak intensity of source: 3.32 mJy/beam
#rms: 1.51e-02 mJy/beam
#Peak SNR: 220.43


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

tclean_wrapper(vis = combined_cont_p2+'.ms' , imagename = combined_cont_p2, mask = common_mask, scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn', uvtaper=['0.04arcsec'])
estimate_SNR(combined_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#MYLup_combined_contp2.image
#Beam 0.072 arcsec x 0.057 arcsec (74.79 deg)
#Flux inside disk mask: 78.11 mJy
#Peak intensity of source: 3.35 mJy/beam
#rms: 1.46e-02 mJy/beam
#Peak SNR: 229.79

# SNR change is small, but map quality improved some.  Will attempt another round


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

tclean_wrapper(vis = combined_cont_p3+'.ms' , imagename = combined_cont_p3, mask = common_mask, scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn', uvtaper=['0.04arcsec'])
estimate_SNR(combined_cont_p3+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#MYLup_combined_contp3.image
#Beam 0.072 arcsec x 0.057 arcsec (74.79 deg)
#Flux inside disk mask: 78.09 mJy
#Peak intensity of source: 3.42 mJy/beam
#rms: 1.39e-02 mJy/beam
#Peak SNR: 246.18

 
# continued improvement (in both map quality and SNR)


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

tclean_wrapper(vis = combined_cont_p4+'.ms' , imagename = combined_cont_p4, mask = common_mask, scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn', uvtaper=['0.04arcsec'])
estimate_SNR(combined_cont_p4+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#MYLup_combined_contp4.image
#Beam 0.072 arcsec x 0.057 arcsec (74.79 deg)
#Flux inside disk mask: 78.05 mJy
#Peak intensity of source: 3.54 mJy/beam
#rms: 1.37e-02 mJy/beam
#Peak SNR: 259.09

# marginal improvement (in both map quality and SNR, and not just peak SNR). Proceeding with amplitude self-cal

# Note that the use of solint interval longer than the scan length does not lead to any improvement in the image quality.
combined_ap = prefix+'_combined.ap'
os.system('rm -rf '+combined_ap)
gaincal(vis=combined_cont_p4+'.ms' , caltable=combined_ap, gaintype='T', combine = 'spw', spw=combined_contspws, refant=combined_refant, calmode='ap', solint='inf', minsnr=3.0, minblperant=4, solnorm = False)

if not skip_plots:
    plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange, plotrange=[0,0,0,2]) 
    plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = LB2_obs1_timerange, plotrange=[0,0,0,2])

applycal(vis=combined_cont_p4+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_ap], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_ap = prefix+'_combined_contap'
os.system('rm -rf %s*' % combined_cont_ap)
split(vis=combined_cont_p4+'.ms', outputvis=combined_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_ap+'.ms' , imagename = combined_cont_ap, mask = common_mask, scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn', uvtaper=['0.04arcsec'])
estimate_SNR(combined_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)

#MYLup_combined_contap.image
#Beam 0.071 arcsec x 0.057 arcsec (74.85 deg)
#Flux inside disk mask: 78.83 mJy
#Peak intensity of source: 3.37 mJy/beam
#rms: 1.30e-02 mJy/beam
#Peak SNR: 258.93

# no real improvement in peak SNR metric.  But map is slightly improved. 

# make image with no uv tapering and deeper clean
imagename = prefix+'_combined_contap_nouvtap'
os.system('rm -rf '+imagename+'.*')
tclean_wrapper(vis = combined_cont_ap+'.ms' , imagename = imagename, mask = common_mask, scales = LB_scales, threshold = '0.03mJy', savemodel = 'modelcolumn', interactive=True)
estimate_SNR(imagename+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#MYLup_combined_contap_nouvtap.image
#Beam 0.050 arcsec x 0.033 arcsec (74.87 deg)
#Flux inside disk mask: 79.24 mJy
#Peak intensity of source: 1.63 mJy/beam
#rms: 1.27e-02 mJy/beam
#Peak SNR: 127.90

exportfits(imagename=imagename+'.image', fitsimage='MYLup.fits', overwrite=True) 

os.system('cp -r '+combined_cont_ap+'.ms MYLup_cont_final.ms')

