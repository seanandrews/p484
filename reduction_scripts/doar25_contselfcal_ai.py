"""
This script was written for CASA 5.1.1
Datasets calibrated (in order of date observed):
SB1: 2016.1.00484.L/
     ID 0: Observed 14-May-2017
     ID 1: Observed 17-May-2017
     ID 2: Observed 19-May-2017
    
LB1: 2016.1.00484.L/
     ID 0: Observed 23-Sep-2017
"""
import os

execfile('/home/shared/ALMA_data/p484_large/reduction_utils.py')

skip_plots = False #if this is true, all of the plotting and inspection steps will be skipped and the script can be executed non-interactively in CASA if all relevant values have been hard-coded already 

#to fill this dictionary out, use listobs for the relevant measurement set 

prefix = 'DOAR25' #string that identifies the source and is at the start of the name for all output files

#Note that if you are downloading data from the archive, your SPW numbering may differ from the SPWs in this script depending on how you split your data out!! 
data_params = {'SB1': {'vis' : '/home/shared/ALMA_data/p484_large/DoAr25/calibrated_msfiles/DoAr25_p484_SB.ms',
                       'name' : 'SB1',
                       'field': 'DoAr_25',
                       'line_spws': np.array([0,4,8]), #SpwIDs of windows with lines that need to be flagged (this needs to be edited for each short baseline dataset)
                       'line_freqs': np.array([2.30538e11, 2.30538e11, 2.30538e11]), #frequencies (Hz) corresponding to line_spws (12CO 2-1 line at 230.538 GHz, 13CO 2-1 line at 220.399 GHz, C18O J=2-1 line at 219.560 GHz)
                      }, #information about the short baseline measurement sets (SB1, SB2, SB3, etc in chronological order)
               'LB1': {'vis' : '/home/shared/ALMA_data/p484_large/DoAr25/calibrated_msfiles/calibrated_final_LB.ms', 
                       'name' : 'LB1',
                       'field' : 'DoAr_25',
                       'line_spws': np.array([3]), #these are generally going to be the same for most of the long-baseline datasets. Some datasets only have one execution block or have strange numbering
                       'line_freqs': np.array([2.30538e11]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz) 
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
    flagchannels_string = get_flagchannels(data_params[i], prefix, velocity_range = np.array([-30, 30]))
    """
    Produces spectrally averaged continuum datasets
    If you only want to include a subset of the windows, you can manually pass in values for contspw and width_array, e.g.
    avg_cont(data_params[i], output_prefix, flagchannels = flagchannels_string, contspws = '0~2', width_array = [480,8,8]).
    If you don't pass in values, all of the SPWs will be split out and the widths will be computed automatically to enforce a maximum channel width of 125 MHz.
    WARNING: Only use the avg_cont function if the total bandwidth is recorded correctly in the original MS. There is sometimes a bug in CASA that records incorrect total bandwidths
    """
 
    avg_cont(data_params[i], prefix, flagchannels = flagchannels_string)

    # Flagchannels input string for LB1: '3:1811~2000'
    # Flagchannels input string for SB1: '0:1809~1998, 4:1809~1998, 8:1809~1998'

# check that amplitude vs. uvdist looks normal
  plotms(vis=prefix+'_SB1_initcont.ms', xaxis='uvdist', yaxis='amp', coloraxis='spw', avgtime='30', avgchannel='16')
  plotms(vis=prefix+'_LB1_initcont.ms', xaxis='uvdist', yaxis='amp', coloraxis='spw', avgtime='30', avgchannel='16')

"""
Quick imaging of every execution block in the measurement set using tclean. 
The threshold, scales, and mask should be adjusted for each source.
In this case, we picked our threshold, scales, and mask from previous reductions of the data. You may wish to experiment with these values when imaging. 
The threshold is ~3-4x the rms, the mask is an ellipse that covers all the emission and has roughly the same geometry, and we choose 4 to 6 scales such that the first scale is 0 (a point), and the largest is ~half the major axis of the mask.
The mask angle and the semimajor and semiminor axes should be the same for all imaging. The center is not necessarily fixed because of potential misalignments between observations. 
"""
mask_angle = 100 #position angle of mask in degrees
mask_semimajor = 2.0 #semimajor axis of mask in arcsec
mask_semiminor = 1.0 #semiminor axis of mask in arcsec
mask_ra = '16h26m23.681s'
mask_dec = '-24.43.14.358'

SB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % (mask_ra, mask_dec, mask_semimajor, mask_semiminor, mask_angle)

LB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % (mask_ra, mask_dec, mask_semimajor, mask_semiminor, mask_angle)

common_mask = SB1_mask


SB_scales = [0, 7, 21, 63]
LB_scales = [0, 10, 30, 90, 270]
"""
In this section, we are imaging every execution block to check spatial alignment 
"""

if not skip_plots:
    #images are saved in the format prefix+'_name_initcont_exec#.ms'
    image_each_obs(data_params['SB1'], prefix, mask = SB1_mask, scales = SB_scales, threshold = '0.15mJy', interactive = False)
    # Exec 0: FWHM beam size: 0.27''x0.22'', rms=7.4e-5 Jy/beam
    # Exec 1: FWHM beam size: 0.26''x0.23'', rms=1.0e-4 Jy/beam
    # Exec 2: FWHM beam size: 0.29''x0.23'', rms=1.3e-4 Jy/beam
    # inspection of images does not reveal additional bright background sources 

    image_each_obs(data_params['LB1'], prefix, mask = LB1_mask, scales = LB_scales, threshold = '0.1mJy', robust=2, interactive = False)
    # Exec0: FWHM beam size: 0.055''x0.036'', rms= 7.7e-5 Jy/beam

    """
    Since the source looks axisymmetric, we will fit a Gaussian to the disk to estimate the location of the peak in each image and record the output.
    We are also very roughly estimating the PA and inclination for checking the flux scale offsets later (these are NOT the position angles and inclinations used for analysis of the final image products).
    Here, we are using the CLEAN mask to restrict the region over which the fit is occurring, but you may wish to shrink the region even further if your disk structure is complex 
    """

    fit_gaussian(prefix+'_SB1_initcont_exec0.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h26m23.681121s -24d43m14.35746s
    #Peak in J2000 coordinates: 16:26:23.68171, -024:43:14.344602
    #Pixel coordinates of peak: x = 448.583 y = 433.418
    #PA of Gaussian component: 110.28 deg
    #Inclination of Gaussian component: 64.89 deg

    fit_gaussian(prefix+'_SB1_initcont_exec1.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h26m23.679422s -24d43m14.32376s
    #Peak in J2000 coordinates: 16:26:23.68001, -024:43:14.310902
    #Pixel coordinates of peak: x = 449.354 y = 434.541
    #PA of Gaussian component: 109.99 deg
    #Inclination of Gaussian component: 64.63 deg

    fit_gaussian(prefix+'_SB1_initcont_exec2.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h26m23.679104s -24d43m14.35253s
    #Peak in J2000 coordinates: 16:26:23.67969, -024:43:14.339672
    #Pixel coordinates of peak: x = 449.499 y = 433.582
    #PA of Gaussian component: 110.15 deg
    #Inclination of Gaussian component: 63.72 deg

    fit_gaussian(prefix+'_LB1_initcont_exec0.image', region = LB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 16h26m23.680721s -24d43m14.35738s
    #Peak in J2000 coordinates: 16:26:23.68131, -024:43:14.344522
    #Pixel coordinates of peak: x = 1487.640 y = 1334.208
    #PA of Gaussian component: 110.64 deg
    #Inclination of Gaussian component: 65.74 deg


    #The shift in the position of the peak of the emission is minimal. No recentering of the ms files is required. 

"""
Now check if the flux scales are consistent between execution blocks (within ~5%)

First, check the pipeline outputs (STEP11/12, hif_setjy or hif_setmodels in the TASKS list of the qa products) to check whether the calibrator catalog matches up with the input flux density values for the calibrators.
(Also check the corresponding plots.)
        SB1, EB0: J1517-2422 = 1.944 Jy at 232.610 GHz - 14-May-2017 ## catalog flux = 1.944 (see below)
        SB1, EB1: J1733-1304 = 1.610 Jy at 232.609 GHz - 17-May-2017 ## catalog flux = 1.610 (see below)
        SB1, EB2: J1517-2422 = 2.108 Jy at 232.609 GHz - 19-May-2017 ## catalog flux = 2.054 (see below)
	LB1, EB0: J1733-1304 = 1.635 Jy at 232.583 GHz - 23-Sep-2017 ## catalog flux = 1.788 (see below)

Now can check that these inputs are matching the current calibrator catalog:
"""
au.getALMAFlux('J1517-2422', frequency = '232.610GHz', date = '2017/05/14')	# SB1, EB0
au.getALMAFlux('J1733-1304', frequency = '232.609GHz', date = '2017/05/17')	# SB1, EB1
au.getALMAFlux('J1517-2422', frequency = '232.609GHz', date = '2017/05/19')	# SB1, EB0
au.getALMAFlux('J1733-1304', frequency = '232.585GHz', date = '2017/09/23')     # LB1, EB0

"""
SB1, EB0
Closest Band 3 measurement: 2.420 +- 0.060 (age=+0 days) 91.5 GHz
Closest Band 7 measurement: 1.840 +- 0.090 (age=-1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -1 days from 2017/05/14, with age separation of 0 days
  2017/05/15: freqs=[91.46, 103.49, 343.48], fluxes=[2.49, 2.55, 1.84]
Median Monte-Carlo result for 232.610000 = 2.042253 +- 0.159757 (scaled MAD = 0.159187)
Result using spectral index of -0.234794 for 232.610 GHz from 2.420 Jy at 91.460 GHz = 1.943706 +- 0.159757 Jy

SB1, EB1
Closest Band 3 measurement: 3.020 +- 0.060 (age=+0 days) 103.5 GHz
Closest Band 7 measurement: 1.190 +- 0.060 (age=+0 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 0 days from 2017/05/17, with age separation of 0 days
  2017/05/17: freqs=[103.49, 343.48], fluxes=[3.02, 1.19]
Median Monte-Carlo result for 232.609000 = 1.611432 +- 0.129021 (scaled MAD = 0.126868)
Result using spectral index of -0.776310 for 232.609 GHz from 3.020 Jy at 103.490 GHz = 1.610486 +- 0.129021 Jy

SB1, EB2
Closest Band 3 measurement: 2.550 +- 0.060 (age=+4 days) 103.5 GHz
Closest Band 3 measurement: 2.490 +- 0.050 (age=+4 days) 91.5 GHz
Closest Band 7 measurement: 1.750 +- 0.060 (age=+2 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 4 days from 2017/05/19, with age separation of 0 days
  2017/05/15: freqs=[103.49, 91.46, 343.48], fluxes=[2.55, 2.49, 1.84]
Median Monte-Carlo result for 232.609000 = 2.045062 +- 0.161200 (scaled MAD = 0.159572)
Result using spectral index of -0.234794 for 232.609 GHz from 2.520 Jy at 97.475 GHz = 2.054524 +- 0.161200 Jy

LB1, EB0
losest Band 3 measurement: 3.110 +- 0.050 (age=+7 days) 91.5 GHz
Closest Band 7 measurement: 1.290 +- 0.050 (age=+0 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -9 days from 2017/09/23, with age separation of 0 days
  2017/10/02: freqs=[91.46, 103.49, 343.48], fluxes=[3.25, 3.07, 1.49]
Median Monte-Carlo result for 232.585000 = 1.886317 +- 0.164825 (scaled MAD = 0.166847)
Result using spectral index of -0.593201 for 232.585 GHz from 3.110 Jy at 91.460 GHz = 1.787747 +- 0.164825 Jy

"""

"""
Here we export averaged visibilities to npz files and then plot the deprojected visibilities to compare the amplitude scales
"""

split_all_obs(prefix+'_SB1_initcont.ms', prefix+'_SB1_initcont_exec')
split_all_obs(prefix+'_LB1_initcont.ms', prefix+'_LB1_initcont_exec')

PA = 110.0 #these are the rough values pulled from Gaussian fitting and used for initial deprojection. They are NOT the final values used for subsequent data analysis
incl = 65
phasecenter = au.radec2deg('16h26m23.678s -24d43m14.860s')
peakpos = au.radec2deg('16h26m23.681s -24d43m14.344s')
offsets = au.angularSeparation(peakpos[0], peakpos[1], phasecenter[0], phasecenter[1], True)

offx = 3600.*offsets[3]
offy = 3600.*offsets[2]


if not skip_plots:
    for msfile in [prefix+'_SB1_initcont_exec0.ms', prefix+'_SB1_initcont_exec1.ms', prefix+'_SB1_initcont_exec2.ms', prefix+'_LB1_initcont_exec0.ms']:
        export_MS(msfile)
    
    #plot deprojected visibility profiles of all the execution blocks. Make sure that the fluxscale parameters are set to 1
    plot_deprojected([prefix+'_SB1_initcont_exec0.vis.npz', prefix+'_SB1_initcont_exec1.vis.npz', prefix+'_SB1_initcont_exec2.vis.npz', prefix+'_LB1_initcont_exec0.vis.npz'], fluxscale=[1.00,1.00,1.00,1.00], offx = offx, offy = offy, PA = PA, incl = incl, show_err=True)
    
   # we us SB1-EC0 as reference
    estimate_flux_scale(reference = prefix+'_SB1_initcont_exec0.vis.npz', comparison = prefix+'_SB1_initcont_exec1.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
   #The ratio of the fluxes of DOAR25_SB1_initcont_exec1.vis.npz to DOAR25_SB1_initcont_exec0.vis.npz is 0.97573
   #The scaling factor for gencal is 0.988 for your comparison measurement
   #The error on the weighted mean ratio is 1.516e-03, although it's likely that the weights in the measurement sets are too off by some constant factor


    estimate_flux_scale(reference = prefix+'_SB1_initcont_exec0.vis.npz', comparison = prefix+'_SB1_initcont_exec2.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
    #The ratio of the fluxes of DOAR25_SB1_initcont_exec2.vis.npz to DOAR25_SB1_initcont_exec0.vis.npz is 1.08921
    #The scaling factor for gencal is 1.044 for your comparison measurement
    #The error on the weighted mean ratio is 1.529e-03, although it's likely that the weights in the measurement sets are too off by some constant factor

     estimate_flux_scale(reference = prefix+'_SB1_initcont_exec0.vis.npz', comparison = prefix+'_LB1_initcont_exec0.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
     #The ratio of the fluxes of DOAR25_LB1_initcont_exec0.vis.npz to DOAR25_SB1_initcont_exec0.vis.npz is 1.16167
     #The scaling factor for gencal is 1.078 for your comparison measurement
     #The error on the weighted mean ratio is 4.157e-03, although it's likely that the weights in the measurement sets are too off by some constant factor

     #We replot the deprojected visibilities with rescaled factors to check that the values make sense
     plot_deprojected([prefix+'_SB1_initcont_exec0.vis.npz', prefix+'_SB1_initcont_exec1.vis.npz', prefix+'_SB1_initcont_exec2.vis.npz', prefix+'_LB1_initcont_exec0.vis.npz'], fluxscale=[1.00, 1.0/0.97573, 1.0/1.08921, 1.0/1.16167], offx = offx, offy = offy, PA = PA, incl = incl, show_err=True)


#now correct the flux scales
rescale_flux(prefix+'_LB1_initcont_exec0.ms', [1.078])
rescale_flux(prefix+'_SB1_initcont_exec2.ms', [1.044])
rescale_flux(prefix+'_SB1_initcont_exec1.ms', [0.988])

#Splitting out rescaled values into new MS: DOAR25_LB1_initcont_exec0_rescaled.ms
#Splitting out rescaled values into new MS: DOAR25_SB1_initcont_exec2_rescaled.ms
#Splitting out rescaled values into new MS: DOAR25_SB1_initcont_exec1_rescaled.ms

# recombined SB ms files 

combined_cont_SB = prefix+'_SB1_rescaled_cont.ms'
os.system('rm -rf '+combined_cont_SB)
concat(vis =[prefix+'_SB1_initcont_exec0.ms', prefix+'_SB1_initcont_exec1_rescaled.ms', prefix+'_SB1_initcont_exec2_rescaled.ms'], concatvis=combined_cont_SB, dirtol='0.1arcsec', copypointing=False)

"""
Start of self-calibration of the short-baseline data 
"""

# make a copy of the SB data
SB_cont_p0 = prefix+'_SB_contp0'
os.system('rm -rf %s*' % SB_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
os.system('cp -r '+prefix+'_SB1_rescaled_cont.ms '+SB_cont_p0+'.ms')

#make initial image
# remove preexisting model if necessary: 
# delmod(vis=SB_cont_p0+'.ms', scr=True)
tclean_wrapper(vis = SB_cont_p0+'.ms', imagename = SB_cont_p0, mask = common_mask, scales = SB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn')

noise_annulus ="annulus[[%s, %s],['%.2farcsec', '4.25arcsec']]" % (mask_ra, mask_dec, 1.1*mask_semimajor) #annulus over which we measure the noise. The inner radius is slightly larger than the semimajor axis of the mask (to add some buffer space around the mask) and the outer radius is set so that the annulus fits inside the long-baseline image size 
estimate_SNR(SB_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#DOAR25_SB_contp0.image
#Beam 0.268 arcsec x 0.225 arcsec (87.86 deg)
#Flux inside disk mask: 230.80 mJy
#Peak intensity of source: 30.04 mJy/beam
#rms: 9.08e-02 mJy/beam
#Peak SNR: 330.89



"""
We need to select one or more reference antennae for gaincal
We first look at the CASA command log (or manual calibration script) to see how the reference antennae choices were ranked (weighted toward antennae close to the center of the array and with good SNR)
Note that gaincal will sometimes choose a different reference antenna than the one specified if it deems another one to be a better choice 
SB1, EB0: DV15, DV18, DA46, DA51
SB1, EB1: DA59, DA49, DA41, DA46
SB1, EB2: DA59, DA46, DA49, DA41
LB1, EB0: DA61, DA47, DV09, DA57
"""

SB_contspws = '0~11' #change as appropriate

#get_station_numbers(SB_cont_p0+'.ms','DA46')

SB_refant = 'DA46@A034'


# It's useful to check that the phases for the refant look good in all execution blocks in plotms. However, plotms has a tendency to crash in CASA 5.1.1, so it might be necessary to use plotms in an older version of CASA 
#plotms(vis=SB_cont_p0+'.ms', xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '0')
#plotms(vis=SB_cont_p0+'.ms', xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '1')
#plotms(vis=SB_cont_p0+'.ms', xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '2')

#first round of phase self-cal for short baseline data. Given the presence of narrow bands, we average across spectral windows. 
SB_p1 = prefix+'_SB.p1'
os.system('rm -rf '+SB_p1)
gaincal(vis=SB_cont_p0+'.ms' , caltable=SB_p1, gaintype='T', spw=SB_contspws, refant=SB_refant, combine='spw', calmode='p', solint='360s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [360s, 120s, 60s, 30s, 18s, 6s]

if not skip_plots:
    plotcal(caltable=SB_p1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', plotrange=[0,0,-180,180]) 

applycal(vis=SB_cont_p0+'.ms', spw=SB_contspws, gaintable=[SB_p1], spwmap=[0,0,0,0,4,4,4,4,8,8,8,8], interp = 'linearPD', calwt = True)

SB_cont_p1 = prefix+'_SB_contp1'
os.system('rm -rf %s*' % SB_cont_p1)
split(vis=SB_cont_p0+'.ms', outputvis=SB_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p1+'.ms' , imagename = SB_cont_p1, mask = common_mask, scales = SB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#DOAR25_SB_contp1.image
#Beam 0.269 arcsec x 0.224 arcsec (86.92 deg)
#Flux inside disk mask: 230.80 mJy
#Peak intensity of source: 31.83 mJy/beam
#rms: 3.74e-02 mJy/beam
#Peak SNR: 851.88 -> SNR increased by 157%


#second round of phase self-cal for short baseline data
SB_p2 = prefix+'_SB.p2'
os.system('rm -rf '+SB_p2)
gaincal(vis=SB_cont_p1+'.ms' , caltable=SB_p2, gaintype='T', spw=SB_contspws, refant=SB_refant, combine='spw', calmode='p', solint='120s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', plotrange=[0,0,-180,180])
    

applycal(vis=SB_cont_p1+'.ms', spw=SB_contspws, gaintable=[SB_p2], spwmap=[0,0,0,0,4,4,4,4,8,8,8,8], interp = 'linearPD', calwt = True)

SB_cont_p2 = prefix+'_SB_contp2'
os.system('rm -rf %s*' % SB_cont_p2)
split(vis=SB_cont_p1+'.ms', outputvis=SB_cont_p2+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p2+'.ms' , imagename = SB_cont_p2, mask = common_mask, scales = SB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn') 
estimate_SNR(SB_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#DOAR25_SB_contp2.image
#Beam 0.269 arcsec x 0.224 arcsec (86.92 deg)
#Flux inside disk mask: 230.82 mJy
#Peak intensity of source: 31.86 mJy/beam
#rms: 3.68e-02 mJy/beam
#Peak SNR: 865.76 -> SNR increased by 1.6 %


#third round of phase self-cal for short baseline data
SB_p3 = prefix+'_SB.p3'
os.system('rm -rf '+SB_p3)
gaincal(vis=SB_cont_p2+'.ms' , caltable=SB_p3, gaintype='T', spw=SB_contspws, refant=SB_refant, combine='spw', calmode='p', solint='30s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', plotrange=[0,0,-180,180])
   
applycal(vis=SB_cont_p2+'.ms', spw=SB_contspws, gaintable=[SB_p3], spwmap=[0,0,0,0,4,4,4,4,8,8,8,8], interp = 'linearPD', calwt = True)

SB_cont_p3 = prefix+'_SB_contp3'
os.system('rm -rf %s*' % SB_cont_p3)
split(vis=SB_cont_p2+'.ms', outputvis=SB_cont_p3+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p3+'.ms' , imagename = SB_cont_p3, mask = common_mask, scales = SB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn') 
estimate_SNR(SB_cont_p3+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#DOAR25_SB_contp3.image
#Beam 0.269 arcsec x 0.224 arcsec (86.01 deg)
#Flux inside disk mask: 230.52 mJy
#Peak intensity of source: 32.02 mJy/beam
#rms: 3.71e-02 mJy/beam
#Peak SNR: 863.95 -> SNR decreased by 0.2%  ... stopping here

#make a copy of the ms file before applyting amp calibration
mscopy = SB_cont_p3+'.ms.backup'
os.system('rm -rf '+mscopy)
os.system('cp -r '+SB_cont_p3+'.ms '+mscopy)

SB_ap = prefix+'_SB.ap'
os.system('rm -rf '+SB_ap)
#note that the solint and minsnr are larger for amp self-cal
#try solnorm = False first. If that leads to bad solutions, try solnorm = True. If that still doesn't help, then just skip amp self-cal
gaincal(vis=SB_cont_p3+'.ms' , caltable=SB_ap, gaintype='T', spw=SB_contspws, refant=SB_refant, combine='spw', calmode='ap', solint='inf', minsnr=3.0, minblperant=4, solnorm = False) 

if not skip_plots:
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', plotrange=[0,0,0,2])
    

applycal(vis=SB_cont_p3+'.ms', spw=SB_contspws, gaintable=[SB_ap], spwmap=[0,0,0,0,4,4,4,4,8,8,8,8], interp = 'linearPD', calwt = True)

SB_cont_ap = prefix+'_SB_contap'
os.system('rm -rf %s*' % SB_cont_ap)
split(vis=SB_cont_p3+'.ms', outputvis=SB_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_ap+'.ms' , imagename = SB_cont_ap, mask = common_mask, scales = SB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#DOAR25_SB_contap.image
#Beam 0.270 arcsec x 0.224 arcsec (85.65 deg)
#Flux inside disk mask: 230.25 mJy
#Peak intensity of source: 32.06 mJy/beam
#rms: 3.15e-02 mJy/beam
#Peak SNR: 1018.63 -> SNR increased by 18%


"""
Selfcalibration on the combined SB+LB data 
"""

#now we concatenate all the data together

combined_cont_p0 = prefix+'_combined_contp0'
os.system('rm -rf %s*' % combined_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [SB_cont_ap+'.ms', prefix+'_LB1_initcont_exec0_rescaled.ms'], concatvis = combined_cont_p0+'.ms', dirtol = '0.1arcsec', copypointing = False) 

tclean_wrapper(vis = combined_cont_p0+'.ms' , imagename = combined_cont_p0, mask = LB1_mask, scales = LB_scales, robust=2.0, threshold = '0.05mJy', savemodel = 'modelcolumn', interactive=False)
estimate_SNR(combined_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)

#DOAR25_combined_contp0.image
#Beam 0.064 arcsec x 0.042 arcsec (87.86 deg)
#Flux inside disk mask: 227.81 mJy
#Peak intensity of source: 2.79 mJy/beam
#rms: 4.04e-02 mJy/beam
#Peak SNR: 69.16

#get_station_numbers(prefix+'_LB1_initcont_exec0_rescaled.ms','DA61')
#Observation ID 0: DA61@A015

combined_refant = 'DA46@A034,DA61@A015'
combined_contspws = '0~15'
combined_spwmap =  [0,0,0,0,4,4,4,4,8,8,8,8,12,12,12,12] #note that the tables produced by gaincal in 5.1.1 have spectral windows numbered differently if you use the combine = 'spw' option. Previously, all of the solutions would be written to spectral window 0. Now, they are written to the first window in each execution block. So, the spwmap argument has to correspond to the first window in each execution block you want to calibrate. 

#first round of phase self-cal for combined  data
combined_p1 = prefix+'_combined.p1'
os.system('rm -rf '+combined_p1)
gaincal(vis=combined_cont_p0+'.ms' , caltable=combined_p1, gaintype='T', combine = 'spw, scan', spw=combined_contspws, field=field, refant=combined_refant, calmode='p', solint='360s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [900s, 360s, 180s, 60s, 30s, 6s]

os.system('cp -r '+combined_cont_p0+'.ms '+combined_cont_p0+'_backup.ms')

if not skip_plots:
    plotcal(caltable=combined_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', plotrange=[0,0,-180,180]) 


applycal(vis=combined_cont_p0+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p1], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p1 = prefix+'_combined_cont_p1'
os.system('rm -rf %s*' % combined_cont_p1)
split(vis=combined_cont_p0+'.ms', outputvis=combined_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p1+'.ms' , imagename = combined_cont_p1, mask = LB1_mask, scales = LB_scales, robust=2, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p1+'.image', disk_mask = LB1_mask, noise_mask = noise_annulus)
#DOAR25_combined_cont_p1.image
#Beam 0.064 arcsec x 0.042 arcsec (87.86 deg)
#Flux inside disk mask: 226.94 mJy
#Peak intensity of source: 2.81 mJy/beam
#rms: 3.89e-02 mJy/beam
#Peak SNR: 72.21 -> SNR increased by ~4%


#second round of phase self-cal on combined data
combined_p2 = prefix+'_combined.p2'
os.system('rm -rf '+combined_p2)
gaincal(vis=combined_cont_p1+'.ms' , caltable=combined_p2, gaintype='T', combine = 'spw, scan', spw=combined_contspws, field=field, refant=combined_refant, calmode='p', solint='180s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [900s, 360s, 180s, 60s, 30s, 6s]

os.system('cp -r '+combined_cont_p1+'.ms '+combined_cont_p1+'_backup.ms')

if not skip_plots:
    plotcal(caltable=combined_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', plotrange=[0,0,-180,180]) 

applycal(vis=combined_cont_p1+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p2], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p2 = prefix+'_combined_cont_p2'
os.system('rm -rf %s*' % combined_cont_p2)
split(vis=combined_cont_p1+'.ms', outputvis=combined_cont_p2+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p2+'.ms' , imagename = combined_cont_p2, mask = LB1_mask, scales = LB_scales, robust=2, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p2+'.image', disk_mask = LB1_mask, noise_mask = noise_annulus)
#DOAR25_combined_cont_p2.image
#Beam 0.064 arcsec x 0.042 arcsec (87.86 deg)
#Flux inside disk mask: 227.14 mJy
#Peak intensity of source: 2.83 mJy/beam
#rms: 3.87e-02 mJy/beam
#Peak SNR: 73.13 -> SNR increased by 1.3% 

#third round of phase self-cal on combined data
combined_p3 = prefix+'_combined.p3'
os.system('rm -rf '+combined_p3)
gaincal(vis=combined_cont_p2+'.ms' , caltable=combined_p3, gaintype='T', combine = 'spw, scan', spw=combined_contspws, field=field, refant=combined_refant, calmode='p', solint='60s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [900s, 360s, 180s, 60s, 30s, 6s]

os.system('cp -r '+combined_cont_p2+'.ms '+combined_cont_p2+'_backup.ms')

if not skip_plots:
    plotcal(caltable=combined_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', plotrange=[0,0,-180,180]) 

applycal(vis=combined_cont_p2+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p3], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p3 = prefix+'_combined_cont_p3'
os.system('rm -rf %s*' % combined_cont_p3)
split(vis=combined_cont_p2+'.ms', outputvis=combined_cont_p3+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p3+'.ms' , imagename = combined_cont_p3, mask = LB1_mask, scales = LB_scales, robust=2, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p3+'.image', disk_mask = LB1_mask, noise_mask = noise_annulus)
#DOAR25_combined_cont_p3.image
#Beam 0.064 arcsec x 0.042 arcsec (87.86 deg)
#Flux inside disk mask: 227.82 mJy
#Peak intensity of source: 2.93 mJy/beam
#rms: 3.72e-02 mJy/beam
#Peak SNR: 78.79 -> SNR increased by 7.5%


#fourth round of phase self-cal on combined data
combined_p4 = prefix+'_combined.p4'
os.system('rm -rf '+combined_p4)
gaincal(vis=combined_cont_p3+'.ms' , caltable=combined_p4, gaintype='T', combine = 'spw, scan', spw=combined_contspws, field=field, refant=combined_refant, calmode='p', solint='30s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [900s, 360s, 180s, 60s, 30s, 6s]

os.system('cp -r '+combined_cont_p3+'.ms '+combined_cont_p3+'_backup.ms')

if not skip_plots:
    plotcal(caltable=combined_p4, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', plotrange=[0,0,-180,180]) 

applycal(vis=combined_cont_p3+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p4], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p4 = prefix+'_combined_cont_p4'
os.system('rm -rf %s*' % combined_cont_p4)
split(vis=combined_cont_p3+'.ms', outputvis=combined_cont_p4+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p4+'.ms' , imagename = combined_cont_p4, mask = LB1_mask, scales = LB_scales, robust=2, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p4+'.image', disk_mask = LB1_mask, noise_mask = noise_annulus)
#DOAR25_combined_cont_p4.image
#Beam 0.064 arcsec x 0.042 arcsec (87.86 deg)
#Flux inside disk mask: 227.58 mJy
#Peak intensity of source: 2.98 mJy/beam
#rms: 3.66e-02 mJy/beam
#Peak SNR: 81.52 -> SNR increased by 3.5%

#fifth round of phase self-cal on combined data
combined_p5 = prefix+'_combined.p5'
os.system('rm -rf '+combined_p5)
gaincal(vis=combined_cont_p4+'.ms' , caltable=combined_p5, gaintype='T', combine = 'spw, scan', spw=combined_contspws, field=field, refant=combined_refant, calmode='p', solint='6s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [900s, 360s, 180s, 60s, 30s, 6s]

os.system('cp -r '+combined_cont_p4+'.ms '+combined_cont_p4+'_backup.ms')

if not skip_plots:
    plotcal(caltable=combined_p5, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', plotrange=[0,0,-180,180]) 

applycal(vis=combined_cont_p4+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p5], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p5 = prefix+'_combined_cont_p5'
os.system('rm -rf %s*' % combined_cont_p5)
split(vis=combined_cont_p4+'.ms', outputvis=combined_cont_p5+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p5+'.ms' , imagename = combined_cont_p5, mask = LB1_mask, scales = LB_scales, robust=2, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p5+'.image', disk_mask = LB1_mask, noise_mask = noise_annulus)
#DOAR25_combined_cont_p5.image
#Beam 0.064 arcsec x 0.042 arcsec (87.86 deg)
#Flux inside disk mask: 227.85 mJy
#Peak intensity of source: 3.11 mJy/beam
#rms: 3.65e-02 mJy/beam
#Peak SNR: 85.40 -> SNR increased by 4.8%


# amplitude-phase selfcal

combined_ap = prefix+'_combined.ap'
os.system('rm -rf '+combined_ap)
gaincal(vis=combined_cont_p5+'.ms' , caltable=combined_ap, gaintype='T', combine = 'spw,scan', spw=combined_contspws, refant=combined_refant, calmode='ap', solint='inf', minsnr=3.0, minblperant=4, solnorm = False)

os.system('cp -r '+combined_cont_p5+'.ms '+combined_cont_p5+'_backup.ms')

if not skip_plots:
    plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange, plotrange=[0,0,0,2]) 

applycal(vis=combined_cont_p5+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_ap], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_ap = prefix+'_combined_contap1'
os.system('rm -rf %s*' % combined_cont_ap)
split(vis=combined_cont_p5+'.ms', outputvis=combined_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_ap+'.ms' , imagename = combined_cont_ap, mask = LB1_mask, scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn', robust=2)
estimate_SNR(combined_cont_ap+'.image', disk_mask = LB1_mask, noise_mask = noise_annulus)

#DOAR25_combined_contap1.image
#Beam 0.060 arcsec x 0.036 arcsec (82.54 deg)
#Flux inside disk mask: 229.90 mJy
#Peak intensity of source: 2.69 mJy/beam
#rms: 1.37e-02 mJy/beam
#Peak SNR: 195.75 -> SNR increased 


# second round of amp/phase selfcal

combined_ap2 = prefix+'_combined.ap2'
os.system('rm -rf '+combined_ap2)
gaincal(vis=combined_cont_ap+'.ms' , caltable=combined_ap2, gaintype='T', combine = 'spw,scan', spw=combined_contspws, refant=combined_refant, calmode='ap', solint='360s', minsnr=3.0, minblperant=4, solnorm = False)

if not skip_plots:
    plotcal(caltable=combined_ap2, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange, plotrange=[0,0,0,2]) 

os.system('cp -r '+combined_cont_ap+'.ms '+combined_cont_ap+'_backup.ms')

applycal(vis=combined_cont_ap+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_ap2], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_ap2 = prefix+'_combined_contap2'
os.system('rm -rf %s*' % combined_cont_ap2)
split(vis=combined_cont_ap+'.ms', outputvis=combined_cont_ap2+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_ap2+'.ms' , imagename = combined_cont_ap2, mask = LB1_mask, scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn', robust=2)

estimate_SNR(combined_cont_ap2+'.image', disk_mask = LB1_mask, noise_mask = noise_annulus)

#DOAR25_combined_contap2.image
#Beam 0.057 arcsec x 0.034 arcsec (81.46 deg)
#Flux inside disk mask: 230.82 mJy
#Peak intensity of source: 2.46 mJy/beam
#rms: 1.32e-02 mJy/beam
#Peak SNR: 185.69

# The SNR dropped sligthly compared to the last iteration. Using the results from previous cycle as final ms file. 


os.system('cp -r '+combined_cont_ap+'_backup.ms DoAr25_cont_final.ms')

mscont = 'DoAr25_cont_final.ms'

# Make a final image with robust=0.5 cleaning deeper
cont_final = prefix+'_cont_final_r0.5'
os.system('rm -rf %s*' % cont_final)
tclean_wrapper(vis=mscont, imagename=cont_final, cellsize='0.003arcsec', imsize=[3000], mask = LB1_mask, scales = LB_scales, threshold = '0.02mJy', robust=0.5, interactive=True)
estimate_SNR(cont_final+'.image', disk_mask = LB1_mask, noise_mask = noise_annulus)
#DoAr25_cont_final_r0.5.image
#Beam 0.048 arcsec x 0.027 arcsec (79.38 deg)
#Flux inside disk mask: 227.45 mJy
#Peak intensity of source: 1.84 mJy/beam
#rms: 1.34e-02 mJy/beam
#Peak SNR: 137.41

exportfits(imagename=cont_final+'.image', fitsimage='DoAr25.fits', overwrite=True) 


