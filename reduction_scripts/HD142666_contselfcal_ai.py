"""
This script was written for CASA 5.1.1
Datasets calibrated (in order of date observed):
SB1: 2013.1.00498.S/
     Observed 21/Jul/2015 
     PI: L. Perez
     As delivered to PI
LB1: 2016.1.00484.L/
     Observed 25/Sep/2017 9/Nov/2017
     PI: S. Andrews
     As delivered to PI
"""
import os

execfile('/home/shared/ALMA_data/p484_large/reduction_utils.py')

skip_plots = False #if this is true, all of the plotting and inspection steps will be skipped and the script can be executed non-interactively in CASA if all relevant values have been hard-coded already 

#to fill this dictionary out, use listobs for the relevant measurement set 

prefix = 'HD142666' #string that identifies the source and is at the start of the name for all output files

#Note that if you are downloading data from the archive, your SPW numbering may differ from the SPWs in this script depending on how you split your data out!! 
data_params = {'SB1': {'vis' : '/home/shared/ALMA_data/p484_large/hd142666/calibrated_msfiles/calibrated_final_SB.ms',
                       'name' : 'SB1',
                       'field': 'HD_142666',
                       'line_spws': np.array([1,5]), #SpwIDs of windows with lines that need to be flagged (this needs to be edited for each short baseline dataset)
                       'line_freqs': np.array([2.30538e11, 2.20399e11]), #frequencies (Hz) corresponding to line_spws (12CO 2-1 line at 230.538 GHz, 13CO 2-1 line at 220.399 GHz, C18O J=2-1 line at 219.560 GHz)
                      }, #information about the short baseline measurement sets (SB1, SB2, SB3, etc in chronological order)
               'LB1': {'vis' : '/home/shared/ALMA_data/p484_large/hd142666/calibrated_msfiles/calibrated_final_LB.ms', 
                       'name' : 'LB1',
                       'field' : 'HD_142666',
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
    flagchannels_string = get_flagchannels(data_params[i], prefix, velocity_range = np.array([-25, 25]))
    """
    Produces spectrally averaged continuum datasets
    If you only want to include a subset of the windows, you can manually pass in values for contspw and width_array, e.g.
    avg_cont(data_params[i], output_prefix, flagchannels = flagchannels_string, contspws = '0~2', width_array = [480,8,8]).
    If you don't pass in values, all of the SPWs will be split out and the widths will be computed automatically to enforce a maximum channel width of 125 MHz.
    WARNING: Only use the avg_cont function if the total bandwidth is recorded correctly in the original MS. There is sometimes a bug in CASA that records incorrect total bandwidths
    """

    # Flagchannels input string for SB1: '1:112~270, 5:22~98'
    # Averaged continuum dataset saved to HD142666_SB1_initcont.ms
    # Flagchannels input string for LB1: '3:1827~1984, 7:1827~1984'
    # Averaged continuum dataset saved to HD142666_LB1_initcont.ms
 
    avg_cont(data_params[i], prefix, flagchannels = flagchannels_string)

# sample command to check that amplitude vs. uvdist looks normal
  plotms(vis=prefix+'_SB1_initcont.ms', xaxis='uvdist', yaxis='amp', coloraxis='spw', avgtime='30', avgchannel='16')
  plotms(vis=prefix+'_LB1_initcont.ms', xaxis='uvdist', yaxis='amp', coloraxis='spw', avgtime='30', avgchannel='16')

"""
Quick imaging of every execution block in the measurement set using tclean. 
The threshold, scales, and mask should be adjusted for each source.
In this case, we picked our threshold, scales, and mask from previous reductions of the data. You may wish to experiment with these values when imaging. 
The threshold is ~3-4x the rms, the mask is an ellipse that covers all the emission and has roughly the same geometry, and we choose 4 to 6 scales such that the first scale is 0 (a point), and the largest is ~half the major axis of the mask.
The mask angle and the semimajor and semiminor axes should be the same for all imaging. The center is not necessarily fixed because of potential misalignments between observations. 
"""
mask_angle = 170 #position angle of mask in degrees
mask_semimajor = 1.0 #semimajor axis of mask in arcsec
mask_semiminor = 0.6 #semiminor axis of mask in arcsec
mask_ra = '15h56m40.001s'
mask_dec = '-22.01.40.38'

SB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % (mask_ra, mask_dec, mask_semimajor, mask_semiminor, mask_angle)

LB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % (mask_ra, mask_dec, mask_semimajor, mask_semiminor, mask_angle)

common_mask = LB1_mask


SB_scales = [0, 7, 21, 63]
LB_scales = [0, 10, 30, 90, 270]
"""
In this section, we are imaging every execution block to check spatial alignment 
"""

if not skip_plots:
    #images are saved in the format prefix+'_name_initcont_exec#.ms'
    image_each_obs(data_params['SB1'], prefix, mask = SB1_mask, scales = SB_scales, threshold = '0.15mJy', interactive = False)
    # inspection of images does not reveal additional bright background sources 

    image_each_obs(data_params['LB1'], prefix, mask = LB1_mask, scales = LB_scales, threshold = '0.06mJy', interactive = False)

    """
    Since the source looks axisymmetric, we will fit a Gaussian to the disk to estimate the location of the peak in each image and record the output.
    We are also very roughly estimating the PA and inclination for checking the flux scale offsets later (these are NOT the position angles and inclinations used for analysis of the final image products).
    Here, we are using the CLEAN mask to restrict the region over which the fit is occurring, but you may wish to shrink the region even further if your disk structure is complex 
    """

    fit_gaussian(prefix+'_SB1_initcont_exec0.image', region = SB1_mask)
   #Peak of Gaussian component identified with imfit: J2000 15h56m40.005495s -22d01m40.38903s
   #Pixel coordinates of peak: x = 450.900 y = 447.628
   #PA of Gaussian component: 161.36 deg
   #Inclination of Gaussian component: 58.70 deg



    fit_gaussian(prefix+'_LB1_initcont_exec0.image', region = LB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 15h56m40.004913s -22d01m40.39761s
    #Peak in J2000 coordinates: 15:56:40.00560, -022:01:40.383238
    #Pixel coordinates of peak: x = 1515.136 y = 1508.941
    #PA of Gaussian component: 162.24 deg
    #Inclination of Gaussian component: 61.55 deg

    
    fit_gaussian(prefix+'_LB1_initcont_exec1.image', region = LB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 15h56m40.005235s -22d01m40.39733s
    #Peak in J2000 coordinates: 15:56:40.00592, -022:01:40.382958
    #Pixel coordinates of peak: x = 1513.165 y = 1509.981
    #PA of Gaussian component: 163.27 deg
    #Inclination of Gaussian component: 61.95 deg


"""
SB and LB images are perhaps shifted by about 8mas in dec. This is a small fraction of the beam that 
should be corrected during selfcal. 
Now check if the flux scales seem consistent between execution blocks (within ~5%)
"""

split_all_obs(prefix+'_SB1_initcont.ms', prefix+'_SB1_initcont_exec')
split_all_obs(prefix+'_LB1_initcont.ms', prefix+'_LB1_initcont_exec')


"""
Phase centers of the three executions:
SB1, EB0:
Name                RA               Decl           Epoch   
HD_142666           15:56:40.007438 -22.01.40.31786 J2000   

LB1, EB0:
 Name                RA               Decl           Epoch  
 HD_142666           15:56:40.008179 -22.01.40.42444 ICRS  

LB1, EB1:
Name                RA               Decl           Epoch 
HD_142666           15:56:40.008076 -22.01.40.42728 ICRS  

We need to shift the phase centers to the same coordinates

"""
shiftname=prefix+'_SB1_initcont_exec0_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_SB1_initcont_exec0.ms', outputvis=shiftname+'.ms', datacolumn='data', phasecenter='ICRS 15h56m40.008179s -22d01m40.42444s') 
tclean_wrapper(vis=shiftname+'.ms', imagename=shiftname, mask=common_mask, scales=SB_scales, threshold='0.25mJy')
fit_gaussian(shiftname+'.image', region=common_mask)
#Peak of Gaussian component identified with imfit: ICRS 15h56m40.004813s -22d01m40.40341s
#Peak in J2000 coordinates: 15:56:40.00550, -022:01:40.389038
#Pixel coordinates of peak: x = 451.560 y = 450.701
#PA of Gaussian component: 161.36 deg
#Inclination of Gaussian component: 58.71 deg


"""
First, check the pipeline outputs (STEP11/12, hif_setjy or hif_setmodels in the TASKS list of the qa products) to check whether the calibrator catalog matches up with the input flux density values for the calibrators.
(Also check the corresponding plots.)
        SB1, EB0: Titan observed during the track and used to derive the flux scale of J1517-2422 (1.740 Jy at 219.246GHz)
        LB1, EB0: J1517-2422 = 2.18 Jy at 232.585 GHz - 25/Sep/2017
	LB1, EB1: J1427-4206 = 2.36 Jy at 232.599 GHz - 09/Nov/2017
Now can check that these inputs are matching the current calibrator catalog:
"""
au.getALMAFlux('J1517-2422', frequency = '219.246GHz', date = '2015/07/21')	# SB1, EB0

au.getALMAFlux('J1517-2422', frequency = '232.585GHz', date = '2017/09/25')     # LB1, EB0
au.getALMAFlux('J1427-4206', frequency = '232.599GHz', date = '2017/11/09')     # LB1, EB1

"""
SB1, EB0
Closest Band 3 measurement: 2.030 +- 0.040 (age=+2 days) 103.5 GHz
Closest Band 3 measurement: 2.010 +- 0.040 (age=+2 days) 91.5 GHz
Closest Band 7 measurement: 1.430 +- 0.100 (age=+5 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -6 days from 2015/07/21, with age separation of 0 days
  2015/07/27: freqs=[103.49, 91.46, 343.48], fluxes=[2.11, 2.1, 1.58]
Median Monte-Carlo result for 219.246000 = 1.756356 +- 0.150602 (scaled MAD = 0.150200)
Result using spectral index of -0.219743 for 219.246 GHz from 2.020 Jy at 97.475 GHz = 1.690415 +- 0.150602 Jy

** the flux measurement based on Titan in not in the catalog. The flux from the catalog differs from that used in the 
pipeline by only 1%. 


LB1, EB0:
losest Band 3 measurement: 2.770 +- 0.050 (age=-7 days) 103.5 GHz
Closest Band 3 measurement: 2.790 +- 0.040 (age=-7 days) 91.5 GHz
Closest Band 7 measurement: 1.770 +- 0.040 (age=+2 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -7 days from 2017/09/25, with age separation of 0 days
  2017/10/02: freqs=[103.49, 91.46, 343.48], fluxes=[2.77, 2.79, 1.92]
Median Monte-Carlo result for 232.585000 = 2.171127 +- 0.178947 (scaled MAD = 0.177753)
Result using spectral index of -0.279723 for 232.585 GHz from 2.780 Jy at 97.475 GHz = 2.179700 +- 0.178947 Jy


LB1, EB1:
Closest Band 3 measurement: 4.010 +- 0.110 (age=+2 days) 103.5 GHz
Closest Band 3 measurement: 4.290 +- 0.120 (age=+2 days) 91.5 GHz
Closest Band 7 measurement: 1.960 +- 0.050 (age=-1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 8 days from 2017/11/09, with age separation of 0 days
  2017/11/01: freqs=[91.46, 103.49, 343.48], fluxes=[4.19, 4.05, 1.92]
Median Monte-Carlo result for 232.599000 = 2.439934 +- 0.142507 (scaled MAD = 0.140998)
Result using spectral index of -0.595755 for 232.599 GHz from 4.150 Jy at 97.475 GHz = 2.471854 +- 0.142507 Jy


"""

"""
Here we export averaged visibilities to npz files and then plot the deprojected visibilities to compare the amplitude scales
"""





PA = 161.0 #these are the rough values pulled from Gaussian fitting and used for initial deprojection. They are NOT the final values used for subsequent data analysis
incl = 60.0
phasecenter = au.radec2deg('15:56:40.007438, -22:01:40.31786')
peakpos = au.radec2deg('15:56:40.005, -022:01:40.387')
offsets = au.angularSeparation(peakpos[0], peakpos[1], phasecenter[0], phasecenter[1], True)

offx = 3600.*offsets[3]
offy = 3600.*offsets[2]


if not skip_plots:
    for msfile in [prefix+'_SB1_initcont_exec0_shift.ms', prefix+'_LB1_initcont_exec0.ms', prefix+'_LB1_initcont_exec1.ms']:
        export_MS(msfile)
    #plot deprojected visibility profiles of all the execution blocks. Make sure that the fluxscale parameters are set to 1
    plot_deprojected([prefix+'_SB1_initcont_exec0_shift.vis.npz', prefix+'_LB1_initcont_exec0.vis.npz', prefix+'_LB1_initcont_exec1.vis.npz'], fluxscale=[1.00,1.00,1.00], offx = offx, offy = offy, PA = PA, incl = incl, show_err=False)
    
   
    estimate_flux_scale(reference = prefix+'_SB1_initcont_exec0_shift.vis.npz', comparison = prefix+'_LB1_initcont_exec0.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
    #The ratio of the fluxes of HD142666_LB1_initcont_exec0.vis.npz to HD142666_SB1_initcont_exec0_shift.vis.npz is 1.17725
    #The scaling factor for gencal is 1.085 for your comparison measurement
    #The error on the weighted mean ratio is 9.718e-04, although it's likely that the weights in the measurement sets are too off by some constant factor

    estimate_flux_scale(reference = prefix+'_SB1_initcont_exec0_shift.vis.npz', comparison = prefix+'_LB1_initcont_exec1.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
    #The ratio of the fluxes of HD142666_LB1_initcont_exec1.vis.npz to HD142666_SB1_initcont_exec0_shift.vis.npz is 0.93345
    #The scaling factor for gencal is 0.966 for your comparison measurement
    #The error on the weighted mean ratio is 1.069e-03, although it's likely that the weights in the measurement sets are too off by some constant factor

    #We replot the deprojected visibilities with rescaled factors to check that the values make sense
    plot_deprojected([prefix+'_SB1_initcont_exec0_shift.vis.npz',prefix+'_LB1_initcont_exec0.vis.npz', prefix+'_LB1_initcont_exec1.vis.npz'],
                     fluxscale=[1, 1/1.17725, 1/0.93345], offx = offx, offy = offy, PA = PA, incl = incl, show_err=False)

#now correct the flux scales
rescale_flux(prefix+'_LB1_initcont_exec0.ms', [1.085])
rescale_flux(prefix+'_LB1_initcont_exec1.ms', [0.966])
#Splitting out rescaled values into new MS: HD142666_LB1_initcont_exec0_rescaled.ms
#Splitting out rescaled values into new MS: HD142666_LB1_initcont_exec1_rescaled.ms


#OPTIONAL: check that the rescaling was successfull
export_MS('HD142666_LB1_initcont_exec0_rescaled.ms')
export_MS('HD142666_LB1_initcont_exec1_rescaled.ms')
plot_deprojected([prefix+'_SB1_initcont_exec0_shift.vis.npz', prefix+'_LB1_initcont_exec0_rescaled.vis.npz', prefix+'_LB1_initcont_exec1_rescaled.vis.npz'],
                     fluxscale=[1, 1, 1], offx = offx, offy = offy, PA = PA, incl = incl, show_err=True)

"""
Start of self-calibration of the short-baseline data 
"""

# make a copy of the SB data
SB_cont_p0 = prefix+'_SB_contp0'
os.system('rm -rf %s*' % SB_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
os.system('cp -r '+prefix+'_SB1_initcont_exec0_shift.ms '+SB_cont_p0+'.ms')

#make initial image
# remove preexisting model if necessary: 
# delmod(vis=SB_cont_p0+'.ms', scr=True)
tclean_wrapper(vis = SB_cont_p0+'.ms', imagename = SB_cont_p0, mask = common_mask, scales = SB_scales, threshold = '0.10mJy', savemodel = 'modelcolumn')

noise_annulus ="annulus[[%s, %s],['%.2farcsec', '4.25arcsec']]" % (mask_ra, mask_dec, 1.1*mask_semimajor) #annulus over which we measure the noise. The inner radius is slightly larger than the semimajor axis of the mask (to add some buffer space around the mask) and the outer radius is set so that the annulus fits inside the long-baseline image size 
estimate_SNR(SB_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD142666_SB_contp0.image
#Beam 0.234 arcsec x 0.195 arcsec (60.13 deg)
#Flux inside disk mask: 117.57 mJy
#Peak intensity of source: 34.47 mJy/beam
#rms: 2.19e-01 mJy/beam
#Peak SNR: 157.69



"""
We need to select one or more reference antennae for gaincal
We first look at the CASA command log (or manual calibration script) to see how the reference antennae choices were ranked (weighted toward antennae close to the center of the array and with good SNR)
Note that gaincal will sometimes choose a different reference antenna than the one specified if it deems another one to be a better choice 
SB1, EB0: DV09, DV08, DV06, DV04
LB1, EB0: DV24, DA61, DV09, DA47
LB1, EB1: DA56, DV24, DA45, DV06

"""

SB_contspws = '0~7' #change as appropriate

#get_station_numbers('HD142666_SB_contp0.ms','DV09')
#get_station_numbers('HD142666_SB_contp0.ms','DV08')
SB_refant = 'DV09@A007, DV08@A008' 


# It's useful to check that the phases for the refant look good in all execution blocks in plotms. However, plotms has a tendency to crash in CASA 5.1.1, so it might be necessary to use plotms in an older version of CASA 
#plotms(vis=SB_cont_p0+'.ms', xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '0')
#plotms(vis=SB_cont_p0+'.ms', xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '1')

#first round of phase self-cal for short baseline data. Given the presence of narrow bands, we average across spectral windows. 
SB_p1 = prefix+'_SB.p1'
os.system('rm -rf '+SB_p1)
gaincal(vis=SB_cont_p0+'.ms' , caltable=SB_p1, gaintype='T', spw=SB_contspws, refant=SB_refant, combine='spw', calmode='p', solint='360s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [120s, 60s, 30s, 18s, 6s]

if not skip_plots:
    plotcal(caltable=SB_p1, xaxis='time', yaxis='phase', subplot=441, iteration='antenna', plotrange=[0,0,-180,180]) 

applycal(vis=SB_cont_p0+'.ms', spw=SB_contspws, gaintable=[SB_p1], spwmap=[0,0,0,0,0,0,0,0], interp = 'linearPD', calwt = True)

SB_cont_p1 = prefix+'_SB_contp1'
os.system('rm -rf %s*' % SB_cont_p1)
split(vis=SB_cont_p0+'.ms', outputvis=SB_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p1+'.ms' , imagename = SB_cont_p1, mask = common_mask, scales = SB_scales, threshold = '0.1mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD142666_SB_contp1.image
#Beam 0.235 arcsec x 0.196 arcsec (60.21 deg)
#Flux inside disk mask: 120.24 mJy
#Peak intensity of source: 37.87 mJy/beam
#rms: 7.97e-02 mJy/beam
#Peak SNR: 474.95

#second round of phase self-cal for short baseline data
SB_p2 = prefix+'_SB.p2'
os.system('rm -rf '+SB_p2)
gaincal(vis=SB_cont_p1+'.ms' , caltable=SB_p2, gaintype='T', spw=SB_contspws, refant=SB_refant, combine='spw', calmode='p', solint='120s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', plotrange=[0,0,-180,180])
    

applycal(vis=SB_cont_p1+'.ms', spw=SB_contspws, gaintable=[SB_p2], spwmap=[0,0,0,0,0,0,0,0], interp = 'linearPD', calwt = True)

SB_cont_p2 = prefix+'_SB_contp2'
os.system('rm -rf %s*' % SB_cont_p2)
split(vis=SB_cont_p1+'.ms', outputvis=SB_cont_p2+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p2+'.ms' , imagename = SB_cont_p2, mask = common_mask, scales = SB_scales, threshold = '0.1mJy', savemodel = 'modelcolumn') 
estimate_SNR(SB_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD142666_SB_contp2.image
#Beam 0.235 arcsec x 0.196 arcsec (60.21 deg)
#Flux inside disk mask: 120.17 mJy
#Peak intensity of source: 37.91 mJy/beam
#rms: 7.81e-02 mJy/beam
#Peak SNR: 485.28


#third round of phase self-cal for short baseline data
SB_p3 = prefix+'_SB.p3'
os.system('rm -rf '+SB_p3)
gaincal(vis=SB_cont_p2+'.ms' , caltable=SB_p3, gaintype='T', spw=SB_contspws, refant=SB_refant, combine='spw', calmode='p', solint='30s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', plotrange=[0,0,-180,180])
   
applycal(vis=SB_cont_p2+'.ms', spw=SB_contspws, gaintable=[SB_p3], spwmap=[0,0,0,0,0,0,0,0], interp = 'linearPD', calwt = True)

SB_cont_p3 = prefix+'_SB_contp3'
os.system('rm -rf %s*' % SB_cont_p3)
split(vis=SB_cont_p2+'.ms', outputvis=SB_cont_p3+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p3+'.ms' , imagename = SB_cont_p3, mask = common_mask, scales = SB_scales, threshold = '0.1mJy', savemodel = 'modelcolumn') 
estimate_SNR(SB_cont_p3+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD142666_SB_contp3.image
#Beam 0.237 arcsec x 0.198 arcsec (57.85 deg)
#Flux inside disk mask: 120.52 mJy
#Peak intensity of source: 39.24 mJy/beam
#rms: 7.57e-02 mJy/beam
#Peak SNR: 518.43

# RMS keeps improving. 

#fourth round of phase self-cal for short baseline data
SB_p4 = prefix+'_SB.p4'
os.system('rm -rf '+SB_p4)
gaincal(vis=SB_cont_p3+'.ms' , caltable=SB_p4, gaintype='T', spw=SB_contspws, refant=SB_refant, combine='spw', calmode='p', solint='12s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=SB_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', plotrange=[0,0,-180,180])
   
applycal(vis=SB_cont_p3+'.ms', spw=SB_contspws, gaintable=[SB_p4], spwmap=[0,0,0,0,0,0,0,0], interp = 'linearPD', calwt = True)

SB_cont_p4 = prefix+'_SB_contp4'
os.system('rm -rf %s*' % SB_cont_p4)
split(vis=SB_cont_p3+'.ms', outputvis=SB_cont_p4+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p4+'.ms' , imagename = SB_cont_p4, mask = common_mask, scales = SB_scales, threshold = '0.1mJy', savemodel = 'modelcolumn') 
estimate_SNR(SB_cont_p4+'.image', disk_mask = common_mask, noise_mask = noise_annulus)


#HD142666_SB_contp4.image
#Beam 0.244 arcsec x 0.207 arcsec (42.41 deg)
#Flux inside disk mask: 121.08 mJy
#Peak intensity of source: 42.45 mJy/beam
#rms: 7.80e-02 mJy/beam
#Peak SNR: 544.01

# SNR increases due to the increase in beam size. rms noise is worse. We proceed using the results of the previous iteration. 
delmod(vis=SB_cont_p3+'.ms')



SB_ap = prefix+'_SB.ap'
os.system('rm -rf '+SB_ap)
#note that the solint and minsnr are larger for amp self-cal
#try solnorm = False first. If that leads to bad solutions, try solnorm = True. If that still doesn't help, then just skip amp self-cal
gaincal(vis=SB_cont_p3+'.ms' , caltable=SB_ap, gaintype='T', spw=SB_contspws, refant=SB_refant, combine='spw', calmode='ap', solint='inf', minsnr=3.0, minblperant=4, solnorm = False) 

if not skip_plots:
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', plotrange=[0,0,0,2])
    

applycal(vis=SB_cont_p3+'.ms', spw=SB_contspws, gaintable=[SB_ap], spwmap=[0,0,0,0,0,0,0,0], interp = 'linearPD', calwt = True)

SB_cont_ap = prefix+'_SB_contap'
os.system('rm -rf %s*' % SB_cont_ap)
split(vis=SB_cont_p2+'.ms', outputvis=SB_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_ap+'.ms' , imagename = SB_cont_ap, mask = common_mask, scales = SB_scales, threshold = '0.1mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD142666_SB_contap.image
#Beam 0.236 arcsec x 0.198 arcsec (58.00 deg)
#Flux inside disk mask: 120.65 mJy
#Peak intensity of source: 39.14 mJy/beam
#rms: 7.42e-02 mJy/beam
#Peak SNR: 527.69

# the image has improved compared to the phase-only self cal version


#now we concatenate all the data together

combined_cont_p0 = prefix+'_combined_contp0'
os.system('rm -rf %s*' % combined_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [SB_cont_ap+'.ms', prefix+'_LB1_initcont_exec0_rescaled.ms', prefix+'_LB1_initcont_exec1_rescaled.ms'], concatvis = combined_cont_p0+'.ms' , dirtol = '0.1arcsec', copypointing = False) 

# note that we are slighlty tapering the longest baselines to improve the shape of the PSF
tclean_wrapper(vis = combined_cont_p0+'.ms' , imagename = combined_cont_p0, mask = common_mask, scales = LB_scales, threshold = '0.08mJy', savemodel = 'modelcolumn', interactive=False)
estimate_SNR(combined_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)

#HD142666_combined_contp0.image
#Beam 0.033 arcsec x 0.023 arcsec (64.59 deg)
#Flux inside disk mask: 119.29 mJy
#Peak intensity of source: 1.23 mJy/beam
#rms: 1.28e-02 mJy/beam
#Peak SNR: 95.94

combined_refant = '' #DV09, DV24, DA56'
combined_contspws = '0~15'
combined_spwmap =  [0,0,0,0,0,0,0,0,8,8,8,8,12,12,12,12] #note that the tables produced by gaincal in 5.1.1 have spectral windows numbered differently if you use the combine = 'spw' option. Previously, all of the solutions would be written to spectral window 0. Now, they are written to the first window in each execution block. So, the spwmap argument has to correspond to the first window in each execution block you want to calibrate. 

LB1_obs0_timerange = '2017/09/24/00~2017/09/26/00'
LB2_obs1_timerange = '2017/11/08/00~2017/11/10/00'

#first round of phase self-cal for long baseline data
combined_p1 = prefix+'_combined.p1'
os.system('rm -rf '+combined_p1)
gaincal(vis=combined_cont_p0+'.ms' , caltable=combined_p1, gaintype='T', combine = 'spw, scan', spw=combined_contspws, field=field, refant=combined_refant, calmode='p', solint='360s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [900s, 360s, 180s, 60s, 30s, 6s]

if not skip_plots:
    plotcal(caltable=combined_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=combined_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB2_obs1_timerange, plotrange=[0,0,-180,180])

applycal(vis=combined_cont_p0+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p1], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p1 = prefix+'_combined_contp1'
os.system('rm -rf %s*' % combined_cont_p1)
split(vis=combined_cont_p0+'.ms', outputvis=combined_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p1+'.ms' , imagename = combined_cont_p1, mask = common_mask, scales = LB_scales, threshold = '0.08mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD142666_combined_contp1.image
#Beam 0.033 arcsec x 0.023 arcsec (64.59 deg)
#Flux inside disk mask: 118.82 mJy
#Peak intensity of source: 1.19 mJy/beam
#rms: 1.30e-02 mJy/beam
#Peak SNR: 91.75

#### ---------------------------
#### The first run of selfcal always leads to a worse image. 
#### I tried tapering, chaging robust, changing refant, changing the threashold in cleaning, chaning solint, but that did not work. 
#### Have you encountered any similar problem with other disks? 
#### ------------------------------------------------------




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

