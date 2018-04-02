"""
This script was written for CASA 5.1.1

Datasets calibrated (in order of date observed):



SB1: 2013.1.00226.S/   SB_name: AS_209_SB2_contfinal.ms  
     PI: Oberg
     Observed 02 July 2014 (1 execution block)
SB2  2013.1.00226.S/   SB_name: AS_209_SB3_contfinal.ms 
     PI: Oberg 
     Observed 17 July 2014 (1 execution block)       may need to make 2 SB for this SB dataset
SB3: 2015.1.00486.S/
     PI. Fedele
     Observed   2015 (2 execution blocks)
     Downloaded from archive and calibrated w/ pipeline
SB4: 2016.1.00484.L/   SB_name: AS_209_SB1_contfinal.ms 
     Observed 09 May 2017 (1 execution block)
     PI: S. Andrews
     As delivered to PI
LB1: 2016.1.00484.L/   SB_name: calibrated_final.ms
     Observed 07 September 2017 and 20 September 2017 (2 execution blocks)
     PI: S. Andrews
     As delivered to PI

"""
import os

execfile('/home/vguzman/projects/Disks-Large-Program/data-as209/reduction_scripts/reduction_utils.py')

skip_plots = False #if this is true, all of the plotting and inspection steps will be skipped and the script can be executed non-interactively in CASA if all relevant values have been hard-coded already 

#to fill this dictionary out, use listobs for the relevant measurement set 

prefix = 'AS209' #string that identifies the source and is at the start of the name for all output files

#Note that if you are downloading data from the archive, your SPW numbering may differ from the SPWs in this script depending on how you split your data out!! 
data_params = {'SB1': {'vis' : '/home/vguzman/projects/Disks-Large-Program/data-as209/data/AS_209_SB2_contfinal.ms',
                       'name' : 'SB1',
                       'field': 'as_209',
                       'line_spws': np.array([]), #SpwIDs of windows with lines that need to be flagged (this needs to be edited for each short baseline dataset)
                       'line_freqs': np.array([]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz)
                      }, #information about the short baseline measurement sets (SB1, SB2, SB3, etc in chronological order)
               'SB2': {'vis' : '/home/vguzman/projects/Disks-Large-Program/data-as209/data/AS_209_SB3_contfinal.ms',
                       'name' : 'SB2',
                       'field': 'as_209',
                       'line_spws': np.array([]), 
                       'line_freqs': np.array([]), 
                      },
               'SB3': {'vis' : '/home/vguzman/projects/Disks-Large-Program/data-as209/data/FEDELE',
                       'name' : 'SB3',
                       'field': 'as_209',
                       'line_spws': np.array([0,4]), 
                       'line_freqs': np.array([2.30538e11, 2.30538e11]), 
                      },
               'SB4': {'vis' : '/home/vguzman/projects/Disks-Large-Program/data-as209/data/AS_209_SB1_contfinal.ms',
                       'name' : 'SB4',
                       'field': 'as_209',
                       'line_spws': np.array([]), 
                       'line_freqs': np.array([]), 
                      },
               'LB1': {'vis' : '/home/vguzman/projects/Disks-Large-Program/data-as209/data/calibrated_contfinal.ms',
                       'name' : 'LB1',
                       'field' : 'as_209',
                       'line_spws': np.array([3,7]), #these are generally going to be the same for most of the long-baseline datasets. Some datasets only have one execution block or have strange numbering
                       'line_freqs': np.array([2.30538e11, 2.30538e11]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz) 
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
    flagchannels_string = get_flagchannels(data_params[i], prefix, velocity_range = np.array([-5, 10]))
    """
    Produces spectrally averaged continuum datasets
    If you only want to include a subset of the windows, you can manually pass in values for contspw and width_array, e.g.
    avg_cont(data_params[i], output_prefix, flagchannels = flagchannels_string, contspws = '0~2', width_array = [480,8,8]).
    If you don't pass in values, all of the SPWs will be split out and the widths will be computed automatically to enforce a maximum channel width of 125 MHz.
    WARNING: Only use the avg_cont function if the total bandwidth is recorded correctly in the original MS. There is sometimes a bug in CASA that records incorrect total bandwidths
    """

    # Flagchannels input string for SB1: '0:1890~1937, 4:1890~1937'
    # Averaged continuum dataset saved to GWLup_SB1_initcont.ms
    # Flagchannels input string for LB1: '3:1890~1937, 7:1890~1937'
    # Averaged continuum dataset saved to GWLup_LB1_initcont.ms
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
mask_angle = 42 #position angle of mask in degrees
mask_semimajor = 1.3 #semimajor axis of mask in arcsec
mask_semiminor = 1.1 #semiminor axis of mask in arcsec

SB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % ('15h46m44.71s', '-34.30.36.09', mask_semimajor, mask_semiminor, mask_angle)

LB1_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % ('15h46m44.71s', '-34.30.36.09', mask_semimajor, mask_semiminor, mask_angle)

SB_scales = [0, 5, 10, 20]
LB_scales = [0, 5, 30, 100, 200]
"""
In this section, we are imaging every execution block to check spatial alignment 
"""

if not skip_plots:
    #images are saved in the format prefix+'_name_initcont_exec#.ms'
    image_each_obs(data_params['SB1'], prefix, mask = SB1_mask, scales = SB_scales, threshold = '0.25mJy', interactive = False)
    # inspection of images do not reveal additional bright background sources 

    image_each_obs(data_params['LB1'], prefix, mask = LB1_mask, scales = LB_scales, threshold = '0.06mJy', interactive = False)

    """
    Since the source looks axisymmetric, we will fit a Gaussian to the disk to estimate the location of the peak in each image and record the output.
    We are also very roughly estimating the PA and inclination for checking the flux scale offsets later (these are NOT the position angles and inclinations used for analysis of the final image products.
    Here, we are using the CLEAN mask to restrict the region over which the fit is occurring, but you may wish to shrink the region even further if your disk structure is complex 
    """

    fit_gaussian(prefix+'_SB1_initcont_exec0.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 15h46m44.710036s -34d30m36.08839s

    fit_gaussian(prefix+'_SB1_initcont_exec1.image', region = SB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 15h46m44.708978s -34d30m36.12469s

    fit_gaussian(prefix+'_LB1_initcont_exec0.image', region = 'circle[[%s, %s], %.1farcsec]' % ('15h46m44.71s', '-34.30.36.09', 0.2)) #shrinking the fit region because of the noisiness of the image
    #Peak of Gaussian component identified with imfit: ICRS 15h46m44.710940s -34d30m36.08832s

    fit_gaussian(prefix+'_LB1_initcont_exec1.image', region = LB1_mask)
    #Peak of Gaussian component identified with imfit: ICRS 15h46m44.708871s -34d30m36.09063s
    #Peak in J2000 coordinates: 15:46:44.70938, -034:30:36.075805
    #Pixel coordinates of peak: x = 1579.879 y = 1444.676
    #PA of Gaussian component: 41.42 deg
    #Inclination of Gaussian component: 38.55 deg


"""
Since the individual execution blocks appear to be slightly misaligned, 
we will be splitting out the individual execution blocks, 
shifting them so that the image peaks fall on the phase center, 
reassigning the phase centers to a common direction (for ease of concat)
and imaging to check the shift  
"""

split_all_obs(prefix+'_SB1_initcont.ms', prefix+'_SB1_initcont_exec')
split_all_obs(prefix+'_LB1_initcont.ms', prefix+'_LB1_initcont_exec')
#Saving observation 0 of GWLup_SB1_initcont.ms to GWLup_SB1_initcont_exec0.ms
#Saving observation 1 of GWLup_SB1_initcont.ms to GWLup_SB1_initcont_exec1.ms
#Saving observation 0 of GWLup_LB1_initcont.ms to GWLup_LB1_initcont_exec0.ms
#Saving observation 1 of GWLup_LB1_initcont.ms to GWLup_LB1_initcont_exec1.ms


common_dir = 'J2000 15h46m44.70938s -034.30.36.075805' #choose peak of second execution of LB1 to be the common direction (the better-quality of the high-res observations)   

#need to change to J2000 coordinates
mask_ra = '15h46m44.709s'
mask_dec = '-34.30.36.076'
common_mask = 'ellipse[[%s, %s], [%.1farcsec, %.1farcsec], %.1fdeg]' % (mask_ra, mask_dec, mask_semimajor, mask_semiminor, mask_angle)

shiftname = prefix+'_SB1_initcont_exec0_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_SB1_initcont_exec0.ms', outputvis=shiftname+'.ms', field = data_params['SB1']['field'], phasecenter='ICRS 15h46m44.710036s -34d30m36.08839s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['SB1']['field'], direction = common_dir) #fixplanets works only with J2000, not ICRS
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = SB_scales, threshold = '0.25mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 15h46m44.709386s -34d30m36.07571s

shiftname = prefix+'_SB1_initcont_exec1_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_SB1_initcont_exec1.ms', outputvis=shiftname+'.ms', field = data_params['SB1']['field'], phasecenter='ICRS 15h46m44.708978s -34d30m36.12469s')      
fixplanets(vis = shiftname+'.ms', field = data_params['SB1']['field'], direction = common_dir)
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = SB_scales, threshold = '0.25mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 15h46m44.709384s -34d30m36.07577s

shiftname = prefix+'_LB1_initcont_exec0_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_LB1_initcont_exec0.ms', outputvis=shiftname+'.ms', field = data_params['LB1']['field'], phasecenter='ICRS 15h46m44.710940s -34d30m36.08832s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['LB1']['field'], direction = common_dir)
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = LB_scales, threshold = '0.09mJy')
fit_gaussian(shiftname+'.image', region =  'circle[[%s, %s], %.1farcsec]' % ('15h46m44.709s', '-34.30.36.076', 0.2))
#Peak of Gaussian component identified with imfit: J2000 15h46m44.709428s -34d30m36.07547s


shiftname = prefix+'_LB1_initcont_exec1_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_LB1_initcont_exec1.ms', outputvis=shiftname+'.ms', field = data_params['LB1']['field'], phasecenter='ICRS 15h46m44.708871s -34d30m36.09063s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['LB1']['field'], direction = common_dir)
tclean_wrapper(vis = shiftname+'.ms', imagename = shiftname, mask = common_mask, scales = LB_scales, threshold = '0.06mJy')
fit_gaussian(shiftname+'.image', region = common_mask)
#Peak of Gaussian component identified with imfit: J2000 15h46m44.709382s -34d30m36.07596s

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
au.getALMAFlux('J1733-1304', frequency = '232.582GHz', date = '2017/09/24')
"""
Closest Band 3 measurement: 3.070 +- 0.080 (age=-8 days) 103.5 GHz
Closest Band 3 measurement: 3.250 +- 0.090 (age=-8 days) 91.5 GHz
Closest Band 7 measurement: 1.290 +- 0.050 (age=+1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -8 days from 2017/09/24, with age separation of 0 days
  2017/10/02: freqs=[103.49, 91.46, 343.48], fluxes=[3.07, 3.25, 1.49]
Median Monte-Carlo result for 232.582000 = 1.880897 +- 0.163642 (scaled MAD = 0.158946)
Result using spectral index of -0.593201 for 232.582 GHz from 3.070 Jy at 103.490 GHz = 1.898990 +- 0.163642 Jy

Pipeline command:
setjy(fluxdensity=[1.8865, 0.0, 0.0, 0.0], scalebychan=True,
      vis='uid___A002_Xc4c2da_X57b8.ms', spix=-0.593201295645, spw='19',
      field='J1733-1304', reffreq='TOPO 232.582GHz',
      intent='CALIBRATE_FLUX#ON_SOURCE', selectdata=True, standard='manual',
      usescratch=True)

Calibration is consistent with catalog
"""

#LB1, second execution 
au.getALMAFlux('J1427-4206', frequency = '232.594GHz', date = '2017/11/04')
"""
Closest Band 3 measurement: 4.050 +- 0.080 (age=+3 days) 103.5 GHz
Closest Band 3 measurement: 4.190 +- 0.070 (age=+3 days) 91.5 GHz
Closest Band 7 measurement: 1.920 +- 0.070 (age=+3 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 3 days from 2017/11/04, with age separation of 0 days
  2017/11/01: freqs=[103.49, 91.46, 343.48], fluxes=[4.05, 4.19, 1.92]
/data/astrochem1/jane/casa-release-5.1.1-5.el6/lib/python2.7/site-packages/matplotlib/collections.py:446: FutureWarning: elementwise comparison failed; returning scalar instead, but in the future will perform elementwise comparison
  if self._edgecolors == 'face':
Median Monte-Carlo result for 232.594000 = 2.443185 +- 0.143395 (scaled MAD = 0.144217)
Result using spectral index of -0.595755 for 232.594 GHz from 4.050 Jy at 103.490 GHz = 2.499931 +- 0.143395 Jy

Pipeline command:
setjy(fluxdensity=[2.3604, 0.0, 0.0, 0.0], scalebychan=True,
      vis='uid___A002_Xc66ce1_X3ea6.ms', spix=-0.648802376678, spw='19',
      field='J1427-4206', reffreq='TOPO 232.594GHz',
      intent='CALIBRATE_FLUX#ON_SOURCE', selectdata=True, standard='manual',
      usescratch=True)

Catalog results are different from the pipeline results because 11/07 measurements were added to the catalog after the original calibration
"""

"""
Here we export averaged visibilities to npz files and then plot the deprojected visibilities to compare the amplitude scales
"""


PA = 41.5 #these are the rough values pulled from Gaussian fitting and used for initial deprojection. They are NOT the final values used for subsequent data analysis
incl = 38.5

if not skip_plots:
    for msfile in [prefix+'_SB1_initcont_exec0_shift.ms', prefix+'_SB1_initcont_exec1_shift.ms', prefix+'_LB1_initcont_exec0_shift.ms', prefix+'_LB1_initcont_exec1_shift.ms']:
        export_MS(msfile)
    #plot deprojected visibility profiles of all the execution blocks
    plot_deprojected([prefix+'_SB1_initcont_exec0_shift.vis.npz', prefix+'_SB1_initcont_exec1_shift.vis.npz', prefix+'_LB1_initcont_exec0_shift.vis.npz', prefix+'_LB1_initcont_exec1_shift.vis.npz'],
                 PA = PA, incl = incl)
    #There's clearly a large discrepancy between the second execution of LB1 and everything else. We use the function below to estimate the degree of the flux scale offset. We use the first execution block of SB1 for comparison, although choosing any of the three similar ones would be fine 

    estimate_flux_scale(reference = prefix+'_SB1_initcont_exec0_shift.vis.npz', comparison = prefix+'_LB1_initcont_exec1_shift.vis.npz', incl = incl, PA = PA)
    #The ratio of the fluxes of GWLup_LB1_initcont_exec1_shift.vis.npz to GWLup_SB1_initcont_exec0_shift.vis.npz is 0.82095
    #The scaling factor for gencal is 0.906 for your comparison measurement
    #The error on the weighted mean ratio is 1.781e-03, although it's likely that the weights in the measurement sets are off by a constant factor


    #We replot the deprojected visibilities with rescaled factors to check that the values make sense
    plot_deprojected([prefix+'_SB1_initcont_exec0_shift.vis.npz', prefix+'_SB1_initcont_exec1_shift.vis.npz', prefix+'_LB1_initcont_exec0_shift.vis.npz', prefix+'_LB1_initcont_exec1_shift.vis.npz'],
                 PA = PA, incl = incl, fluxscale = [1., 1., 1., 1/0.82095])

#now correct the flux of the discrepant dataset
rescale_flux(prefix+'_LB1_initcont_exec1_shift.ms', [0.906])
#Splitting out rescaled values into new ms: GWLup_LB1_initcont_exec1_shift_rescaled.ms

"""
Start of self-calibration of the short-baseline data 
"""
#merge the short-baseline execution blocks into a single MS
SB_cont_p0 = prefix+'_SB_contp0'
os.system('rm -rf %s*' % SB_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [prefix+'_SB1_initcont_exec0_shift.ms', prefix+'_SB1_initcont_exec1_shift.ms'], concatvis = SB_cont_p0+'.ms', dirtol = '0.1arcsec', copypointing = False) 

#make initial image
tclean_wrapper(vis = SB_cont_p0+'.ms', imagename = SB_cont_p0, mask = common_mask, scales = SB_scales, threshold = '0.2mJy', savemodel = 'modelcolumn')

noise_annulus ="annulus[[%s, %s],['%.2farcsec', '4.25arcsec']]" % (mask_ra, mask_dec, 1.1*mask_semimajor) #annulus over which we measure the noise. The inner radius is slightly larger than the semimajor axis of the mask (to add some buffer space around the mask) and the outer radius is set so that the annulus fits inside the long-baseline image size 
estimate_SNR(SB_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#GWLup_SB_contp0.image
#Beam 0.274 arcsec x 0.229 arcsec (-83.62 deg)
#Flux inside disk mask: 86.60 mJy
#Peak intensity of source: 20.76 mJy/beam
#rms: 6.75e-02 mJy/beam
#Peak SNR: 307.49


"""
We need to select one or more reference antennae for gaincal

We first look at the CASA command log (or manual calibration script) to see how the reference antennae choices were ranked (weighted toward antennae close to the center of the array and with good SNR)
Note that gaincal will sometimes choose a different reference antenna than the one specified if it deems another one to be a better choice 

First execution of SB1: DA49,DA59,DV18,DV15,DA46
Second execution of SB2: DA49,DA59,DV18,DV15,DA46
First execution of LB1: DV24,DA61,DV09,DA57,DV25
Second execution of LB1: DA57,DA45,DV24,DV09,DV25

DA49 and DA59 have a couple SPWs flagged in the first observation of SB1, so we use DV18 for SB1
DV24 and DA61 don't have data for the second execution of LB1
DV09 is present and fairly central for the two long-baseline observations. It is present in the short-baseline executions, but not really close to the center. 

If you want to double check whether the antenna locations are reasonable, you can use something like plotants(vis = SB_cont_p0+'.ms')

"""

SB_contspws = '0~7' #change as appropriate
SB_refant = 'DV18' #DA49 and DA59 have a couple SPWs flagged in observation 0
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

tclean_wrapper(vis = SB_cont_p1+'.ms' , imagename = SB_cont_p1, mask = common_mask, scales = SB_scales, threshold = '0.1mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#GWLup_SB_contp1.image
#Beam 0.274 arcsec x 0.229 arcsec (-83.62 deg)
#Flux inside disk mask: 88.98 mJy
#Peak intensity of source: 22.10 mJy/beam
#rms: 3.26e-02 mJy/beam
#Peak SNR: 678.15


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

#after the first round of self-cal, emission at ~7sigma shows up several arcsec to the northwest, so we modify the clean mask to encompass it 
tclean_wrapper(vis = SB_cont_p2+'.ms' , imagename = SB_cont_p2, mask = [common_mask, 'circle[[15h46m44.796s, -34d30m33.59s],0.4arcsec]'], scales = SB_scales, threshold = '0.06mJy', savemodel = 'modelcolumn') 
estimate_SNR(SB_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#GWLup_SB_contp2.image
#Beam 0.273 arcsec x 0.230 arcsec (-83.66 deg)
#Flux inside disk mask: 89.24 mJy
#Peak intensity of source: 22.29 mJy/beam
#rms: 3.23e-02 mJy/beam
#Peak SNR: 689.66

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

tclean_wrapper(vis = SB_cont_ap+'.ms' , imagename = SB_cont_ap, mask = [common_mask, 'circle[[15h46m44.796s, -34d30m33.59s],0.4arcsec]'], scales = SB_scales, threshold = '0.06mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#GWLup_SB_contap.image
#Beam 0.274 arcsec x 0.229 arcsec (-83.46 deg)
#Flux inside disk mask: 88.49 mJy
#Peak intensity of source: 22.27 mJy/beam
#rms: 3.04e-02 mJy/beam
#Peak SNR: 731.34


#now we concatenate all the data together

combined_cont_p0 = prefix+'_combined_contp0'
os.system('rm -rf %s*' % combined_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [SB_cont_ap+'.ms', prefix+'_LB1_initcont_exec0_shift.ms', prefix+'_LB1_initcont_exec1_shift_rescaled.ms'], concatvis = combined_cont_p0+'.ms' , dirtol = '0.1arcsec', copypointing = False) 

tclean_wrapper(vis = combined_cont_p0+'.ms' , imagename = combined_cont_p0, mask = [common_mask, 'circle[[15h46m44.796s, -34d30m33.59s],0.4arcsec]'], scales = LB_scales, threshold = '0.05mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#GWLup_combined_contp0.image
#Beam 0.035 arcsec x 0.026 arcsec (-89.67 deg)
#Flux inside disk mask: 88.86 mJy
#Peak intensity of source: 1.76 mJy/beam
#rms: 1.52e-02 mJy/beam
#Peak SNR: 116.30

combined_refant = 'DV09, DV18'
combined_contspws = '0~15'
combined_spwmap =  [0,0,0,0,4,4,4,4,8,8,8,8,12,12,12,12] #note that the tables produced by gaincal in 5.1.1 have spectral windows numbered differently if you use the combine = 'spw' option. Previously, all of the solutions would be written to spectral window 0. Now, they are written to the first window in each execution block. So, the spwmap argument has to correspond to the first window in each execution block you want to calibrate. 

LB1_obs0_timerange = '2017/09/24/00:00:01~2017/09/25/23:59:59'
LB2_obs0_timerange = '2017/11/04/00:00:01~2017/11/04/23:59:59'

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

tclean_wrapper(vis = combined_cont_p1+'.ms' , imagename = combined_cont_p1, mask = [common_mask, 'circle[[15h46m44.796s, -34d30m33.59s],0.4arcsec]'], scales = LB_scales, threshold = '0.045mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#GWLup_combined_contp1.image
#Beam 0.035 arcsec x 0.026 arcsec (-89.67 deg)
#Flux inside disk mask: 89.12 mJy
#Peak intensity of source: 1.90 mJy/beam
#rms: 1.48e-02 mJy/beam
#Peak SNR: 128.42



#second round of phase self-cal for long baseline data
combined_p2 = prefix+'_combined.p2'
os.system('rm -rf '+combined_p2)
gaincal(vis=combined_cont_p1+'.ms' , caltable=combined_p2, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='360s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 
    plotcal(caltable=combined_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs1_timerange)

applycal(vis=combined_cont_p1+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p2], interp = 'linearPD', calwt = True, applymode = 'calonly')


combined_cont_p2 = prefix+'_combined_contp2'
os.system('rm -rf %s*' % combined_cont_p2)
split(vis=combined_cont_p1+'.ms', outputvis=combined_cont_p2+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p2+'.ms' , imagename = combined_cont_p2, mask = [common_mask, 'circle[[15h46m44.796s, -34d30m33.59s],0.4arcsec]'], scales = LB_scales, threshold = '0.045mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#GWLup_combined_contp2.image
#Beam 0.035 arcsec x 0.026 arcsec (-89.67 deg)
#Flux inside disk mask: 89.23 mJy
#Peak intensity of source: 1.95 mJy/beam
#rms: 1.48e-02 mJy/beam
#Peak SNR: 131.94


#third round of phase self-cal for long-baseline data 
combined_p3 = prefix+'_combined.p3'
os.system('rm -rf '+combined_p3)
gaincal(vis=combined_cont_p2+'.ms' , caltable=combined_p3, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='180s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 
    plotcal(caltable=combined_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs1_timerange)

applycal(vis=combined_cont_p2+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p3], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p3 = prefix+'_combined_contp3'
os.system('rm -rf %s*' % combined_cont_p3)
split(vis=combined_cont_p2+'.ms', outputvis=combined_cont_p3+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p3+'.ms' , imagename = combined_cont_p3, mask = [common_mask, 'circle[[15h46m44.796s, -34d30m33.59s],0.4arcsec]'], scales = LB_scales, threshold = '0.045mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p3+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#GWLup_combined_contp3.image
#Beam 0.035 arcsec x 0.026 arcsec (-89.67 deg)
#Flux inside disk mask: 88.71 mJy
#Peak intensity of source: 2.06 mJy/beam
#rms: 1.47e-02 mJy/beam
#Peak SNR: 140.14


#fourth round of phase self-cal for long-baseline data 
combined_p4 = prefix+'_combined.p4'
os.system('rm -rf '+combined_p4)
gaincal(vis=combined_cont_p3+'.ms' , caltable=combined_p4, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='60s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p4, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 
    plotcal(caltable=combined_p4, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs1_timerange)

applycal(vis=combined_cont_p3+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p4], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p4 = prefix+'_combined_contp4'
os.system('rm -rf %s*' % combined_cont_p4)
split(vis=combined_cont_p3+'.ms', outputvis=combined_cont_p4+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p4+'.ms' , imagename = combined_cont_p4, mask = [common_mask, 'circle[[15h46m44.796s, -34d30m33.59s],0.4arcsec]'], scales = LB_scales, threshold = '0.045mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p4+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#GWLup_combined_contp4.image
#Beam 0.035 arcsec x 0.026 arcsec (-89.67 deg)
#Flux inside disk mask: 88.77 mJy
#Peak intensity of source: 2.25 mJy/beam
#rms: 1.46e-02 mJy/beam
#Peak SNR: 153.70

#fifth round of phase self-cal for long-baseline data 

combined_p5 = prefix+'_combined.p5'
os.system('rm -rf '+combined_p5)
gaincal(vis=combined_cont_p4+'.ms' , caltable=combined_p5, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='30s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=combined_p5, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 
    plotcal(caltable=combined_p5, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = LB1_obs1_timerange)

applycal(vis=combined_cont_p4+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p5], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p5 = prefix+'_combined_contp5'
os.system('rm -rf %s*' % combined_cont_p5)
split(vis=combined_cont_p4+'.ms', outputvis=combined_cont_p5+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p5+'.ms' , imagename = combined_cont_p5, mask = [common_mask, 'circle[[15h46m44.796s, -34d30m33.59s],0.4arcsec]'], scales = LB_scales, threshold = '0.045mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_p5+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#GWLup_combined_contp5.image
#Beam 0.035 arcsec x 0.026 arcsec (-89.67 deg)
#Flux inside disk mask: 88.66 mJy
#Peak intensity of source: 2.36 mJy/beam
#rms: 1.46e-02 mJy/beam
#Peak SNR: 161.19


#additional phase self-cal and amp self-cal appears to make things worse for GW Lup
#uncomment the lines below if you wish to perform amp self-cal for your source specifically
"""

combined_ap = prefix+'_combined.ap'
os.system('rm -rf '+combined_ap)
gaincal(vis=combined_cont_p5+'.ms' , caltable=combined_ap, gaintype='T', combine = 'spw,scan', spw=combined_contspws, refant=combined_refant, calmode='ap', solint='900s', minsnr=3.0, minblperant=4, solnorm = False)

if not skip_plots:
    plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = LB1_obs0_timerange) 
    plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = LB1_obs1_timerange)

applycal(vis=combined_cont_p5+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_ap], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_ap = prefix+'_combined_contap'
os.system('rm -rf %s*' % combined_cont_ap)
split(vis=combined_cont_p5+'.ms', outputvis=combined_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_ap+'.ms' , imagename = combined_cont_ap, mask = [common_mask, 'circle[[15h46m44.796s, -34d30m33.59s],0.4arcsec]'], scales = LB_scales, threshold = '0.045mJy', savemodel = 'modelcolumn')
estimate_SNR(combined_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
"""



