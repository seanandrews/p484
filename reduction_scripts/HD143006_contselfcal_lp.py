"""
This script was written for CASA 5.1.1

/almadata02/lperez/casa_5.1.1/casa-release-5.1.1-5.el7/bin/casa

Datasets calibrated (in order of date observed):
SB1: Project ???/??? (name HD143006_calibrated.ms)
     Observed 14 June 2016 (2 execution blocks)
     PI: K. Oberg
     As delivered to PI (data sent by J. Huang)

SB2: Project ???/??? (name HD143006_TC.ms)
     Observed 02 July 2016 (1 execution block)
     PI: K. Oberg
     As delivered to PI (data sent by J. Huang)

SB3: 2016.1.00484.L/ (name hd143006_p484_SB.ms)
     Observed 14,17,19 May 2017 (3 execution blocks)
     PI: S. Andrews
     As delivered to PI

LB1: 2016.1.00484.L/ (name hd143006_p484_LB.ms)
     Observed 26 September 2017 and 26 November 2017 (2 execution blocks)
     PI: S. Andrews
     As delivered to PI

"""
import os
sys.path.append('/almadata02/lperez/analysis_scripts/')

execfile('reduction_utils.py')

skip_plots = False #if this is true, all of the plotting and inspection steps will be skipped and the script can be executed non-interactively in CASA if all relevant values have been hard-coded already 

#to fill this dictionary out, use listobs for the relevant measurement set 

prefix = 'HD143006' #string that identifies the source and is at the start of the name for all output files

#Note that if you are downloading data from the archive, your SPW numbering may differ from the SPWs in this script depending on how you split your data out!! 

data_params = {'SB1': {'vis' : '/umi_01/lperez/hd143006/raw_data/HD143006_calibrated.ms',
                       'name' : 'SB1',
                       'field': 'HD143006',
                       'line_spws': np.array([0,9]), #SpwIDs of windows with lines that need to be flagged
                       'line_freqs': np.array([2.30538e11,2.30538e11]), #frequencies (Hz) corresponding to line_spws
                       'cont_spws': '0,1,2,9,10,11', #SpwIDs of windows with continuum
                       'width_array': [960,960,256,960,960,256], # channel averaging for continuum spws
                   },
               'SB2': {'vis' : '/umi_01/lperez/hd143006/raw_data/HD143006_TC.ms',
                       'name' : 'SB2',
                       'field': 'HD143006',
                       'line_spws': np.array([0]), 
                       'line_freqs': np.array([2.30538e11]), 
                       'cont_spws': '0,1,2',
                       'width_array': [960,960,256],
                   },
               'SB3': {'vis' : '/umi_01/lperez/hd143006/raw_data/hd143006_p484_SB.ms',
                       'name' : 'SB3',
                       'field': 'HD_143006',
                       'line_spws': np.array([0,4,8]), 
                       'line_freqs': np.array([2.30538e11,2.30538e11,2.30538e11]), 
                       'cont_spws': None,
                       'width_array': None,
                   },
               'LB1': {'vis' : '/umi_01/lperez/hd143006/raw_data/hd143006_p484_LB.ms',
                       'name' : 'LB1',
                       'field' : 'HD_143006',
                       'line_spws': np.array([3,7]), 
                       'line_freqs': np.array([2.30538e11, 2.30538e11]), 
                       'cont_spws': None,
                       'width_array': None,
                      }
               }

# need to initialize weight spectrum because earlier datasets have weight spectrum initialized 
initweights(vis = data_params['SB2']['vis'], wtmode = 'weight', dowtsp = True)
initweights(vis = data_params['LB1']['vis'], wtmode = 'weight', dowtsp = True)

# Plot each spw of each execution to see if there is some problem
if not skip_plots:
    for i in data_params.keys():
i='SB2'
plotms(vis=data_params[i]['vis'], xaxis='channel', yaxis='amplitude', field=data_params[i]['field'], ydatacolumn='data', avgtime='1e8', avgscan=True, avgbaseline=True, iteraxis='spw')

#Amplitudes of channels 0 to 200 in SPW 0 of SB2 look problematic
flagmanager(vis = data_params['SB2']['vis'], mode = 'save', versionname = 'original_flags', comment = 'Original flag states') #save flag state before flagging spectral lines
flagdata(vis=data_params['SB2']['vis'], mode='manual', spw='0:0~200', flagbackup=False, field = data_params['SB2']['field']) #flag spectral lines 


for i in data_params.keys():      
    flagchannels_string = get_flagchannels(data_params[i], prefix, velocity_range = np.array([-4, 20]))
    avg_cont(data_params[i], prefix, flagchannels = flagchannels_string, contspws = data_params[i]['cont_spws'], width_array = data_params[i]['width_array'])

# Flagchannels input string for SB1: '0:414~565, 9:414~565'
#Averaged continuum dataset saved to HD143006_SB1_initcont.ms
# Flagchannels input string for SB2: '0:414~565'
#Averaged continuum dataset saved to HD143006_SB2_initcont.ms
# Flagchannels input string for SB3: '0:1903~1978, 4:1903~1978, 8:1903~1978'
#Averaged continuum dataset saved to HD143006_SB3_initcont.ms
# Flagchannels input string for LB1: '3:1893~1968, 7:1893~1968'
#Averaged continuum dataset saved to HD143006_LB1_initcont.ms

# sample command to check that amplitude vs. uvdist looks normal
# plotms(vis=prefix+'_SB1_initcont.ms', xaxis='uvdist', yaxis='amp', coloraxis='spw', avgtime='30', avgchannel='16')


"""
Quick imaging of every execution block in the measurement set using tclean. 
The threshold, scales, and mask should be adjusted for each source.
In this case, we picked our threshold, scales, and mask from previous reductions of the data. You may wish to experiment with these values when imaging. 
The threshold is ~3-4x the rms, the mask is an ellipse that covers all the emission and has roughly the same geometry, and we choose 4 to 6 scales such that the first scale is 0 (a point), and the largest is ~half the major axis of the mask.
The mask angle and the semimajor and semiminor axes should be the same for all imaging. The center is not necessarily fixed because of potential misalignments between observations. 
"""
mask_radius = 0.8 #radius of mask in arcsec
SB_mask = 'circle[[%s, %s], %.1farcsec]' % ('15h58m36.9s', '-22.57.15.60', mask_radius)
LB_mask = 'circle[[%s, %s], %.1farcsec]' % ('15h58m36.9s', '-22.57.15.60', mask_radius)

SB_scales = [0, 10, 30]
LB_scales = [0, 25, 50, 75, 100]

if not skip_plots:
    #images are saved in the format prefix+'_name_initcont_exec#.ms'
    image_each_obs(data_params['SB1'], prefix, mask = SB_mask, scales = SB_scales, threshold = '0.8mJy', robust=-2, interactive = False)
    image_each_obs(data_params['SB2'], prefix, mask = SB_mask, scales = SB_scales, threshold = '0.8mJy', robust=-2, interactive = False)
    image_each_obs(data_params['SB3'], prefix, mask = SB_mask, scales = SB_scales, threshold = '0.4mJy', robust=-2, interactive = False)
    image_each_obs(data_params['LB1'], prefix, mask = LB_mask, scales = LB_scales, threshold = '0.06mJy', interactive = False)

# inspection of images does not reveal any severe alignment issues

"""
The individual execution blocks are all in alignment.  
But, before proceeding we need to align the phase centers.
Selecting the phase center from the latest observation of LB to be the reference one.
"""

au.ICRSToJ2000('15:58:36.899002 -22:57:15.61701')
#Separation: radian = 8.24252e-08, degrees = 0.000005, arcsec = 0.017001
#Out[20]: '15:58:36.89967, -022:57:15.602730'

for i in data_params.keys():      
    shift = prefix+'_'+i+'_initcont_shift.ms'
    os.system('rm -rf '+shift+'*')
    split(vis=prefix+'_'+i+'_initcont.ms', outputvis=shift, datacolumn='data')
    fixvis(vis=shift, outputvis=shift, field=data_params[i]['field'], phasecenter='J2000 15h58m36.89967s -22d57m15.602730s')


"""
Now check if the flux scales seem consistent between execution blocks (within ~5%)
"""

split_all_obs(prefix+'_SB1_initcont_shift.ms', prefix+'_SB1_initcont_exec')
split_all_obs(prefix+'_SB2_initcont_shift.ms', prefix+'_SB2_initcont_exec')
split_all_obs(prefix+'_SB3_initcont_shift.ms', prefix+'_SB3_initcont_exec')
split_all_obs(prefix+'_LB1_initcont.ms', prefix+'_LB1_initcont_exec')

"""
First, check the pipeline outputs (STEP11/12, hif_setjy or hif_setmodels in the TASKS list of the qa products) to check whether the calibrator catalog matches up with the input flux density values for the calibrators.
(Also check the corresponding plots.)

	SB1, EB0: J1517-2422 = 2.477 Jy at 232.411 GHz (2016/06/14) 5% difference
	SB1, EB1: J1517-2422 = 2.477 Jy at 232.411 GHz (2016/06/14) 5% difference
	SB2, EB0: J1517-2422 = 2.300 Jy at 232.405 GHz (2016/07/02) 2% difference
	SB3, EB0: J1517-2422 = 1.944 Jy at 232.610 GHz (2017/05/14) 5% difference
	SB3, EB1: J1733-1304 = 1.610 Jy at 232.609 GHz (2017/05/17) no difference
	SB3, EB2: J1517-2422 = 2.108 Jy at 232.609 GHz (2017/05/19) 4% difference
	LB1, EB0: J1733-1304 = 1.886 Jy at 232.584 GHz (2017/09/26) no difference
	LB1, EB1: J1427-4206 = 2.577 Jy at 232.605 GHz (2017/11/26) no difference

Now can check that these inputs are matching the current calibrator catalog:

"""
au.getALMAFlux('J1517-2422', frequency = '232.411GHz', date = '2016/06/14')     # SB1, EB0,1
au.getALMAFlux('J1517-2422', frequency = '232.405GHz', date = '2016/07/02')     # SB2, EB0
au.getALMAFlux('J1517-2422', frequency = '232.610GHz', date = '2017/05/14')     # SB3, EB0
au.getALMAFlux('J1733-1304', frequency = '232.609GHz', date = '2017/05/17')     # SB3, EB1
au.getALMAFlux('J1517-2422', frequency = '232.609GHz', date = '2017/05/19')     # SB3, EB2
au.getALMAFlux('J1733-1304', frequency = '232.584GHz', date = '2017/09/26')     # LB1, EB0
au.getALMAFlux('J1427-4206', frequency = '232.605GHz', date = '2017/11/26')     # LB1, EB1

"""
Results are:

SB1, EB0,1
Closest Band 3 measurement: 2.910 +- 0.110 (age=-2 days) 103.5 GHz
Closest Band 3 measurement: 2.790 +- 0.100 (age=-2 days) 91.5 GHz
Closest Band 7 measurement: 2.190 +- 0.130 (age=+5 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -5 days from 2016/06/14, with age separation of 0 days
  2016/06/19: freqs=[103.49, 91.46, 337.46], fluxes=[2.95, 2.84, 2.09]
Median Monte-Carlo result for 232.411000 = 2.362163 +- 0.193603 (scaled MAD = 0.191896)
Result using spectral index of -0.225942 for 232.411 GHz from 2.850 Jy at 97.475 GHz = 2.341977 +- 0.193603 Jy

SB2, EB0
Closest Band 3 measurement: 3.130 +- 0.050 (age=+1 days) 103.5 GHz
Closest Band 3 measurement: 2.960 +- 0.050 (age=+1 days) 91.5 GHz
Closest Band 7 measurement: 2.050 +- 0.080 (age=+1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 1 days from 2016/07/02, with age separation of 0 days
  2016/07/01: freqs=[103.49, 91.46, 343.48], fluxes=[3.13, 2.96, 2.05]
Median Monte-Carlo result for 232.405000 = 2.355061 +- 0.147604 (scaled MAD = 0.145188)
Result using spectral index of -0.293392 for 232.405 GHz from 3.045 Jy at 97.475 GHz = 2.359801 +- 0.147604 Jy

SB3, EB0
Closest Band 3 measurement: 2.420 +- 0.060 (age=+0 days) 91.5 GHz
Closest Band 7 measurement: 1.840 +- 0.090 (age=-1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -1 days from 2017/05/14, with age separation of 0 days
  2017/05/15: freqs=[103.49, 91.46, 343.48], fluxes=[2.55, 2.49, 1.84]
Median Monte-Carlo result for 232.610000 = 2.039790 +- 0.160329 (scaled MAD = 0.157137)
Result using spectral index of -0.234794 for 232.610 GHz from 2.420 Jy at 91.460 GHz = 1.943706 +- 0.160329 Jy

SB3, EB1
Closest Band 3 measurement: 3.020 +- 0.060 (age=+0 days) 103.5 GHz
Closest Band 7 measurement: 1.190 +- 0.060 (age=+0 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 0 days from 2017/05/17, with age separation of 0 days
  2017/05/17: freqs=[103.49, 343.48], fluxes=[3.02, 1.19]
Median Monte-Carlo result for 232.609000 = 1.612333 +- 0.128501 (scaled MAD = 0.128638)
Result using spectral index of -0.776310 for 232.609 GHz from 3.020 Jy at 103.490 GHz = 1.610486 +- 0.128501 Jy

SB3, EB2
Closest Band 3 measurement: 2.550 +- 0.060 (age=+4 days) 103.5 GHz
Closest Band 3 measurement: 2.490 +- 0.050 (age=+4 days) 91.5 GHz
Closest Band 7 measurement: 1.750 +- 0.060 (age=+2 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 4 days from 2017/05/19, with age separation of 0 days
  2017/05/15: freqs=[103.49, 91.46, 343.48], fluxes=[2.55, 2.49, 1.84]
Median Monte-Carlo result for 232.609000 = 2.043097 +- 0.158878 (scaled MAD = 0.159456)
Result using spectral index of -0.234794 for 232.609 GHz from 2.520 Jy at 97.475 GHz = 2.054524 +- 0.158878 Jy

LB1, EB0
Closest Band 3 measurement: 3.070 +- 0.080 (age=-6 days) 103.5 GHz
Closest Band 3 measurement: 3.250 +- 0.090 (age=-6 days) 91.5 GHz
Closest Band 7 measurement: 1.290 +- 0.050 (age=+3 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -6 days from 2017/09/26, with age separation of 0 days
  2017/10/02: freqs=[103.49, 91.46, 343.48], fluxes=[3.07, 3.25, 1.49]
Median Monte-Carlo result for 232.584000 = 1.882780 +- 0.163177 (scaled MAD = 0.162419)
Result using spectral index of -0.593201 for 232.584 GHz from 3.160 Jy at 97.475 GHz = 1.886440 +- 0.163177 Jy

LB1, EB1
Closest Band 3 measurement: 4.430 +- 0.080 (age=+1 days) 91.5 GHz
Closest Band 7 measurement: 2.060 +- 0.070 (age=+3 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 3 days from 2017/11/26, with age separation of 0 days
  2017/11/23: freqs=[91.46, 343.48], fluxes=[4.44, 2.06]
Median Monte-Carlo result for 232.605000 = 2.582799 +- 0.148594 (scaled MAD = 0.149213)
Result using spectral index of -0.580360 for 232.605 GHz from 4.430 Jy at 91.460 GHz = 2.577109 +- 0.148594 Jy

Conclusion: Differences are less than 5% between ALMA calibrator catalog and what was input as fluxes for the amplitude calibrators in each of the observations. 
"""
"""
As a final check, we will compare the amplitude calibration by deprojecting the visibilities by a rough estimate of the inclination, PA of the disk
"""

PA = 80. #these are the rough values 
incl = 10.
phasecenter = au.radec2deg('15:58:36.899002, -22.57.15.61701')
peakpos = au.radec2deg('15:58:36.899, -22.57.15.596')
offsets = au.angularSeparation(peakpos[0], peakpos[1], phasecenter[0], phasecenter[1], True)
"""
(5.83611615863498e-06,
 -8.3333585986838343e-09,
 5.8361111139729223e-06,
 -7.6734897198442044e-09)
"""

offx = 3600.*offsets[3]
offy = 3600.*offsets[2]

# SB1 and SB2 have only spws close to 231GHz, while SB3 has spws close to 231 and 245 GHz, so to make a fair comparison, we will split only the spws in SB3 with frequencies close to 231GHz
split(vis=prefix+'_SB3_initcont_exec0.ms',outputvis=prefix+'_SB3_initcont_exec0_spw01.ms', spw='0,1',datacolumn='data')
split(vis=prefix+'_SB3_initcont_exec1.ms',outputvis=prefix+'_SB3_initcont_exec1_spw01.ms', spw='0,1',datacolumn='data')
split(vis=prefix+'_SB3_initcont_exec2.ms',outputvis=prefix+'_SB3_initcont_exec2_spw01.ms', spw='0,1',datacolumn='data')



if not skip_plots:
    for msfile in [prefix+'_SB1_initcont_exec0.ms', prefix+'_SB1_initcont_exec1.ms', prefix+'_SB2_initcont_exec0.ms', prefix+'_SB3_initcont_exec0_spw01.ms', prefix+'_SB3_initcont_exec1_spw01.ms', prefix+'_SB3_initcont_exec2_spw01.ms', prefix+'_LB1_initcont_exec0.ms', prefix+'_LB1_initcont_exec1.ms']:
    export_MS(msfile)

    #plot deprojected visibility profiles of all the execution blocks
    plot_deprojected([prefix+'_SB1_initcont_exec0.vis.npz', prefix+'_SB1_initcont_exec1.vis.npz', prefix+'_SB2_initcont_exec0.vis.npz', prefix+'_SB3_initcont_exec0_spw01.vis.npz', prefix+'_SB3_initcont_exec1_spw01.vis.npz', prefix+'_SB3_initcont_exec2_spw01.vis.npz', prefix+'_LB1_initcont_exec0.vis.npz', prefix+'_LB1_initcont_exec1.vis.npz'], fluxscale=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], offx = offx, offy = offy, PA = PA, incl = incl, show_err=False)

    estimate_flux_scale(reference = prefix+'_LB1_initcont_exec0.vis.npz', comparison = prefix+'_LB1_initcont_exec1.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
#The ratio of the fluxes of HD143006_LB1_initcont_exec1.vis.npz to HD143006_LB1_initcont_exec0.vis.npz is 0.76910
#The scaling factor for gencal is 0.877 for your comparison measurement
#The error on the weighted mean ratio is 2.341e-03, although it's likely that the weights in the measurement sets are too off by some constant factor
    estimate_flux_scale(reference = prefix+'_SB3_initcont_exec0_spw01.vis.npz', comparison = prefix+'_SB1_initcont_exec0.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
#The ratio of the fluxes of HD143006_SB1_initcont_exec0.vis.npz to HD143006_SB3_initcont_exec0_spw01.vis.npz is 1.12843
#The scaling factor for gencal is 1.062 for your comparison measurement
#The error on the weighted mean ratio is 2.122e-03, although it's likely that the weights in the measurement sets are too off by some constant factor
    estimate_flux_scale(reference = prefix+'_SB3_initcont_exec0_spw01.vis.npz', comparison = prefix+'_SB1_initcont_exec1.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
#The ratio of the fluxes of HD143006_SB1_initcont_exec1.vis.npz to HD143006_SB3_initcont_exec0_spw01.vis.npz is 1.04710
#The scaling factor for gencal is 1.023 for your comparison measurement
#The error on the weighted mean ratio is 1.992e-03, although it's likely that the weights in the measurement sets are too off by some constant factor
    estimate_flux_scale(reference = prefix+'_SB3_initcont_exec0_spw01.vis.npz', comparison = prefix+'_SB2_initcont_exec0.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
#The ratio of the fluxes of HD143006_SB2_initcont_exec0.vis.npz to HD143006_SB3_initcont_exec0_spw01.vis.npz is 1.00313
#The scaling factor for gencal is 1.002 for your comparison measurement
#The error on the weighted mean ratio is 1.776e-03, although it's likely that the weights in the measurement sets are too off by some constant factor
    estimate_flux_scale(reference = prefix+'_SB3_initcont_exec0_spw01.vis.npz', comparison = prefix+'_SB3_initcont_exec1_spw01.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
#The ratio of the fluxes of HD143006_SB3_initcont_exec1.vis.npz to HD143006_SB3_initcont_exec0.vis.npz is 1.07657
#The scaling factor for gencal is 1.038 for your comparison measurement
#The error on the weighted mean ratio is 2.049e-03, although it's likely that the weights in the measurement sets are too off by some constant factor
    estimate_flux_scale(reference = prefix+'_SB3_initcont_exec0.vis.npz', comparison = prefix+'_SB3_initcont_exec2.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
#The ratio of the fluxes of HD143006_SB3_initcont_exec2.vis.npz to HD143006_SB3_initcont_exec0.vis.npz is 1.15169
#The scaling factor for gencal is 1.073 for your comparison measurement
#The error on the weighted mean ratio is 1.744e-03, although it's likely that the weights in the measurement sets are too off by some constant factor
    estimate_flux_scale(reference = prefix+'_SB3_initcont_exec0.vis.npz', comparison = prefix+'_LB1_initcont_exec0.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
#The ratio of the fluxes of HD143006_LB1_initcont_exec0.vis.npz to HD143006_SB3_initcont_exec0.vis.npz is 1.16634
#The scaling factor for gencal is 1.080 for your comparison measurement
#The error on the weighted mean ratio is 3.199e-03, although it's likely that the weights in the measurement sets are too off by some constant factor
    estimate_flux_scale(reference = prefix+'_SB3_initcont_exec0.vis.npz', comparison = prefix+'_LB1_initcont_exec1.vis.npz', offx = offx, offy = offy, incl = incl, PA = PA)
#The ratio of the fluxes of HD143006_LB1_initcont_exec1.vis.npz to HD143006_SB3_initcont_exec0.vis.npz is 0.92359
#The scaling factor for gencal is 0.961 for your comparison measurement
#The error on the weighted mean ratio is 1.957e-03, although it's likely that the weights in the measurement sets are too off by some constant factor

    #We replot the deprojected visibilities with rescaled factors to check that the values make sense
    plot_deprojected([prefix+'_SB1_initcont_exec0.vis.npz', prefix+'_SB1_initcont_exec1.vis.npz', prefix+'_SB2_initcont_exec0.vis.npz', prefix+'_SB3_initcont_exec0.vis.npz', prefix+'_SB3_initcont_exec1.vis.npz', prefix+'_SB3_initcont_exec2.vis.npz', prefix+'_LB1_initcont_exec0.vis.npz', prefix+'_LB1_initcont_exec1.vis.npz'], fluxscale=[1.0/1.09932, 1.0/1.02237, 1.0/0.97805, 1.0, 1.0/1.07657, 1.0/1.15169, 1.0/1.16634, 1.0/0.92359], offx = offx, offy = offy, PA = PA, incl = incl, show_err=False)


""" 
We have chosen the SB observations from our program (SB3) to be the reference for the amplitude scale. In particular, of the 3 executions we will select the one with lowest RMS (E0 from SB3), to avoid phase noise.

Considering only the SB executions, flux ratios are offset at most by 15%
SB3 E0 to SB1 E0 1.12843 231GHz
SB3 E0 to SB1 E1 1.04710 231GHz
SB3 E0 to SB2 E0 1.00313 231GHz
SB3 E0 to SB3 E1 1.07657 239GHz
SB3 E0 to SB3 E2 1.15169 239GHz
Considering the LB and SB executions, flux ratios are offset by +/- 15%
SB3 E0 to LB1 E0 1.16634 239GHz
SB3 E0 to LB1 E1 0.92359 239GHz
"""

# Rescaling datasets
os.system('rm -rf *rescaled.*')
rescale_flux(prefix+'_SB1_initcont_exec0.ms', [1.062])
rescale_flux(prefix+'_SB1_initcont_exec1.ms', [1.023])
rescale_flux(prefix+'_SB2_initcont_exec0.ms', [1.002])
rescale_flux(prefix+'_SB3_initcont_exec1.ms', [1.038])
rescale_flux(prefix+'_SB3_initcont_exec2.ms', [1.073])
rescale_flux(prefix+'_LB1_initcont_exec0.ms', [1.080])
rescale_flux(prefix+'_LB1_initcont_exec1.ms', [0.961])

# Export again to npz and deproject to see if rescaling worked
if not skip_plots:
    for msfile in [prefix+'_SB1_initcont_exec0_rescaled.ms', prefix+'_SB1_initcont_exec1_rescaled.ms', prefix+'_SB2_initcont_exec0_rescaled.ms', prefix+'_SB3_initcont_exec1_rescaled.ms', prefix+'_SB3_initcont_exec2_rescaled.ms', prefix+'_LB1_initcont_exec0_rescaled.ms', prefix+'_LB1_initcont_exec1_rescaled.ms']:
    export_MS(msfile)

    #plot deprojected visibility profiles of all the execution blocks
    plot_deprojected([prefix+'_SB1_initcont_exec0_rescaled.vis.npz', prefix+'_SB1_initcont_exec1_rescaled.vis.npz', prefix+'_SB2_initcont_exec0_rescaled.vis.npz', prefix+'_SB3_initcont_exec0.vis.npz', prefix+'_SB3_initcont_exec1_rescaled.vis.npz', prefix+'_SB3_initcont_exec2_rescaled.vis.npz', prefix+'_LB1_initcont_exec0_rescaled.vis.npz', prefix+'_LB1_initcont_exec1_rescaled.vis.npz'], fluxscale=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], offx = offx, offy = offy, PA = PA, incl = incl, show_err=False)


"""
Start of self-calibration of the short-baseline data 
"""
#merge the short-baseline execution blocks into a single MS
SB_cont_p0 = prefix+'_SB_contp0'
os.system('rm -rf %s*' % SB_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [prefix+'_SB1_initcont_exec0_rescaled.ms', 
prefix+'_SB1_initcont_exec1_rescaled.ms', 
prefix+'_SB2_initcont_exec0_rescaled.ms', 
prefix+'_SB3_initcont_exec0.ms', 
prefix+'_SB3_initcont_exec1_rescaled.ms', 
prefix+'_SB3_initcont_exec2_rescaled.ms'], 
concatvis = SB_cont_p0+'.ms' , dirtol = '0.1arcsec', copypointing = False) 

#make initial image
mask_ra = '15h58m36.9s'
mask_dec = '-22.57.15.60'
mask_radius = 0.9
common_mask = 'circle[[%s, %s], %.1farcsec]' % (mask_ra, mask_dec, mask_radius)
SB_scales = [0,10,30] # no larger scales were needed to describe the data

tclean_wrapper(vis = SB_cont_p0+'.ms', imagename = SB_cont_p0, mask = common_mask, scales = SB_scales, threshold = '0.04mJy', savemodel = 'modelcolumn')


noise_annulus ="annulus[[%s, %s],['%.2farcsec', '4.25arcsec']]" % (mask_ra, mask_dec, 1.1*mask_radius) #annulus over which we measure the noise. The inner radius is slightly larger than the semimajor axis of the mask (to add some buffer space around the mask) and the outer radius is set so that the annulus fits inside the long-baseline image size 
estimate_SNR(SB_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_SB_contp0.image
#Beam 0.287 arcsec x 0.244 arcsec (-89.21 deg)
#Flux inside disk mask: 56.47 mJy
#Peak intensity of source: 7.19 mJy/beam
#rms: 3.95e-02 mJy/beam
#Peak SNR: 182.01


"""
We need to select one or more reference antennae for gaincal

We first look at the CASA command log (or manual calibration script) to see how the reference antennae choices were ranked (weighted toward antennae close to the center of the array and with good SNR)
Note that gaincal will sometimes choose a different reference antenna than the one specified if it deems another one to be a better choice 

get_station_numbers(SB_cont_p0+'.ms', 'DA49')

for SB1, refant = 'DA41, DA49'
for SB2, refant = 'DV16@A036'
for SB3, refant = 'DA46, DA51'
for all, refant = 'DA41@A004,DA49@A002,DV16@A036,DA46@A034,DA51@A023'

"""

SB_contspws = '0~20'
SB_refant = 'DA41@A004,DA49@A002,DV16@A036,DA46@A034,DA51@A023'
SB1_obs0_timerange = '2016/06/14/00~2016/06/15/00'
SB1_obs2_timerange = '2016/07/02/00~2016/07/03/00'
SB1_obs3_timerange = '2017/05/14/00~2017/05/15/00'
SB1_obs4_timerange = '2017/05/17/00~2017/05/18/00'
SB1_obs5_timerange = '2017/05/18/00~2017/05/20/00'

# It's useful to check that the phases for the refant look good in all execution blocks in plotms. However, plotms has a tendency to crash in CASA 5.1.1, so it might be necessary to use plotms in an older version of CASA 
#plotms(vis=SB_cont_p0+'.ms', xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '0')
#plotms(vis=SB_cont_p0+'.ms', xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '1')
#plotms(vis=SB_cont_p0+'.ms', xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '2')
#plotms(vis=SB_cont_p0+'.ms', xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '3')
#plotms(vis=SB_cont_p0+'.ms', xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '4')
#plotms(vis=SB_cont_p0+'.ms', xaxis='time', yaxis='phase', ydatacolumn='data', avgtime='30', avgbaseline=True, antenna = SB_refant, observation = '5')

#first round of phase self-cal for short baseline data
SB_p1 = prefix+'_SB.p1'
os.system('rm -rf '+SB_p1)
gaincal(vis=SB_cont_p0+'.ms' , caltable=SB_p1, gaintype='T', spw=SB_contspws, refant=SB_refant, calmode='p', solint='120s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [120s, 60s, 30s, 18s, 6s]

"""
Lots of solutions flagged when we obtain one solution per spw,
even at this large time interval.
"""

if not skip_plots:
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs2_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs3_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs4_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=SB_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs5_timerange, plotrange=[0,0,-180,180]) 

applycal(vis=SB_cont_p0+'.ms', spw=SB_contspws, gaintable=[SB_p1], interp = 'linearPD', calwt = True)

SB_cont_p1 = prefix+'_SB_contp1'
os.system('rm -rf %s*' % SB_cont_p1)
split(vis=SB_cont_p0+'.ms', outputvis=SB_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p1+'.ms' , imagename = SB_cont_p1, mask = common_mask, scales = SB_scales, threshold = '0.035mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_SB_contp1.image
#Beam 0.288 arcsec x 0.244 arcsec (-89.17 deg)
#Flux inside disk mask: 57.88 mJy
#Peak intensity of source: 7.94 mJy/beam
#rms: 2.33e-02 mJy/beam
#Peak SNR: 340.09

#second round of phase self-cal for short baseline data
# will combine spws for this round
SB_p2 = prefix+'_SB.p2'
os.system('rm -rf '+SB_p2)
gaincal(vis=SB_cont_p1+'.ms' , caltable=SB_p2, gaintype='T', spw=SB_contspws, combine='spw', refant=SB_refant, calmode='p', solint='30s', minsnr=1.5, minblperant=4)

if not skip_plots:
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs2_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs3_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs4_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=SB_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = SB1_obs5_timerange, plotrange=[0,0,-180,180]) 

SB_spwmap=[0,0,0,3,3,3,6,6,6,9,9,9,9,13,13,13,13,17,17,17,17]
applycal(vis=SB_cont_p1+'.ms', spw=SB_contspws, gaintable=[SB_p2], spwmap=SB_spwmap, interp = 'linearPD', calwt = True)

SB_cont_p2 = prefix+'_SB_contp2'
os.system('rm -rf %s*' % SB_cont_p2)
split(vis=SB_cont_p1+'.ms', outputvis=SB_cont_p2+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_p2+'.ms' , imagename = SB_cont_p2, mask = common_mask, scales = SB_scales, threshold = '0.035mJy', savemodel = 'modelcolumn') 
estimate_SNR(SB_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_SB_contp2.image
#Beam 0.288 arcsec x 0.244 arcsec (-89.94 deg)
#Flux inside disk mask: 57.96 mJy
#Peak intensity of source: 8.10 mJy/beam
#rms: 2.33e-02 mJy/beam
#Peak SNR: 347.37

#improvement over previous round of phase self-cal is marginal, so we move on to amp self-cal for the short baseline data 
SB_ap = prefix+'_SB.ap'
os.system('rm -rf '+SB_ap)
gaincal(vis=SB_cont_p2+'.ms' , caltable=SB_ap, gaintype='T', spw=SB_contspws, combine='scan', refant=SB_refant, calmode='ap', solint='inf', minsnr=3.0, minblperant=4, solnorm = False) 

"""
6 of 40 solutions flagged due to SNR < 3 in spw=6 at 2016/07/02/05:29:10.2
5 of 39 solutions flagged due to SNR < 3 in spw=7 at 2016/07/02/05:29:10.5
"""

if not skip_plots:
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=111, timerange = SB1_obs0_timerange, plotrange=[0,0,0,2])
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=111, timerange = SB1_obs2_timerange, plotrange=[0,0,0,2])
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=111, timerange = SB1_obs3_timerange, plotrange=[0,0,0,2])
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=111, timerange = SB1_obs4_timerange, plotrange=[0,0,0,2])
    plotcal(caltable=SB_ap, xaxis = 'time', yaxis = 'amp',subplot=111, timerange = SB1_obs5_timerange, plotrange=[0,0,0,2])

applycal(vis=SB_cont_p2+'.ms', spw=SB_contspws, gaintable=[SB_ap], interp = 'linearPD', calwt = True)

SB_cont_ap = prefix+'_SB_contap'
os.system('rm -rf %s*' % SB_cont_ap)
split(vis=SB_cont_p2+'.ms', outputvis=SB_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_ap+'.ms' , imagename = SB_cont_ap, mask = common_mask, scales = SB_scales, threshold = '0.023mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_SB_contap.image
#Beam 0.284 arcsec x 0.243 arcsec (-89.89 deg)
#Flux inside disk mask: 58.15 mJy
#Peak intensity of source: 7.98 mJy/beam
#rms: 2.24e-02 mJy/beam
#Peak SNR: 355.96

# improvement is marginal, but map looks better, will consider another round of amp selfcal with one solution per scan
SB_ap1 = prefix+'_SB.ap'
os.system('rm -rf '+SB_ap1)
gaincal(vis=SB_cont_ap+'.ms' , caltable=SB_ap1, gaintype='T', spw=SB_contspws, combine='spw', refant=SB_refant, calmode='ap', solint='inf', minsnr=3.0, minblperant=4, solnorm = False) 

if not skip_plots:
    plotcal(caltable=SB_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB1_obs0_timerange, plotrange=[0,0,0,2])
    plotcal(caltable=SB_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB1_obs2_timerange, plotrange=[0,0,0,2])
    plotcal(caltable=SB_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB1_obs3_timerange, plotrange=[0,0,0,2])
    plotcal(caltable=SB_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB1_obs4_timerange, plotrange=[0,0,0,2])
    plotcal(caltable=SB_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = SB1_obs5_timerange, plotrange=[0,0,0,2])

applycal(vis=SB_cont_ap+'.ms', spw=SB_contspws, gaintable=[SB_ap1], spwmap=SB_spwmap, interp = 'linearPD', calwt = True)

SB_cont_ap1 = prefix+'_SB_contap1'
os.system('rm -rf %s*' % SB_cont_ap1)
split(vis=SB_cont_ap+'.ms', outputvis=SB_cont_ap1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = SB_cont_ap1+'.ms' , imagename = SB_cont_ap1, mask = common_mask, scales = SB_scales, threshold = '0.022mJy', savemodel = 'modelcolumn')
estimate_SNR(SB_cont_ap1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_SB_contap1.image
#Beam 0.283 arcsec x 0.242 arcsec (89.88 deg)
#Flux inside disk mask: 58.24 mJy
#Peak intensity of source: 7.96 mJy/beam
#rms: 2.22e-02 mJy/beam
#Peak SNR: 358.76


#now we concatenate all the data together
combined_cont_p0 = prefix+'_combined_contp0'
os.system('rm -rf %s*' % combined_cont_p0)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [SB_cont_ap+'.ms', prefix+'_LB1_initcont_exec0_rescaled.ms', prefix+'_LB1_initcont_exec1_rescaled.ms'], concatvis = combined_cont_p0+'.ms' , dirtol = '0.1arcsec', copypointing = False) 

# Redefining center of mask
mask_ra = '15h58m36.899s'
mask_dec = '-22.57.15.583'
mask_radius = 0.7
common_mask = 'circle[[%s, %s], %.1farcsec]' % (mask_ra, mask_dec, mask_radius)
noise_annulus ="annulus[[%s, %s],['%.2farcsec', '4.25arcsec']]" % (mask_ra, mask_dec, 1.1*mask_radius) 

LB_scales = [0,17,52,87,170] # for beamsize 52mas, pixel size 3mas

# First image
tclean_wrapper(vis = combined_cont_p0+'.ms' , imagename = combined_cont_p0, mask = common_mask, scales = LB_scales, threshold = '0.02mJy', savemodel = 'modelcolumn', robust=0.5)
estimate_SNR(combined_cont_p0+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_combined_contp0.image
#Beam 0.052 arcsec x 0.037 arcsec (86.45 deg)
#Flux inside disk mask: 57.79 mJy
#Peak intensity of source: 0.60 mJy/beam
#rms: 1.29e-02 mJy/beam
#Peak SNR: 46.52

"""
We need to select one or more reference antennae for gaincal

We first look at the CASA command log (or manual calibration script) to see how the reference antennae choices were ranked (weighted toward antennae close to the center of the array and with good SNR)
Note that gaincal will sometimes choose a different reference antenna than the one specified if it deems another one to be a better choice 

get_station_numbers(combined_cont_p0+'.ms', 'DA49')

for SB1, refant = 'DA41, DA49'
for SB2, refant = 'DV16@A036'
for SB3, refant = 'DA46, DA51'
for all SBs, refant = 'DA41@A004,DA49@A002,DV16@A036,DA46@A034,DA51@A023'
for LB1, exec0 refant = DA61@A015, DA47@A074
for LB1, exec1 refant = DV20@A072, DV08@A042
for all combined: refant = 'DA61@A015, DA47@A074, DV20@A072, DV08@A042, DA41@A004,DA49@A002,DV16@A036,DA46@A034,DA51@A023'
"""

combined_contspws = '0~28' 
combined_refant = 'DV16@A036,DA41@A004,DA49@A002,DA46@A034,DA51@A023,DA61@A015,DA47@A074,DV20@A072,DV08@A042'

combined_obs6_timerange = '2017/09/26/00~2017/09/27/00'
combined_obs7_timerange = '2017/11/26/00~2017/11/27/00'
combined_spwmap =  [0,0,0, 3,3,3, 6,6,6, 9,9,9,9, 13,13,13,13, 17,17,17,17, 21,21,21,21, 25,25,25,25]

#first round of phase self-cal for long baseline data
combined_p1 = prefix+'_combined.p1'
os.system('rm -rf '+combined_p1)
gaincal(vis=combined_cont_p0+'.ms' , caltable=combined_p1, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='900s', minsnr=1.5, minblperant=4) #choose self-cal intervals from [900s, 360s, 180s, 60s, 30s, 6s]

"""
5 of 41 solutions flagged due to SNR < 1.5 in spw=21 at 2017/09/26/22:55:42.2
4 of 41 solutions flagged due to SNR < 1.5 in spw=21 at 2017/09/26/23:11:45.9
2 of 44 solutions flagged due to SNR < 1.5 in spw=25 at 2017/11/26/14:10:01.0
2 of 44 solutions flagged due to SNR < 1.5 in spw=25 at 2017/11/26/14:26:03.3
"""

if not skip_plots:
    plotcal(caltable=combined_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = combined_obs6_timerange, plotrange=[0,0,-180,180]) 
    plotcal(caltable=combined_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = combined_obs7_timerange, plotrange=[0,0,-180,180]) 

applycal(vis=combined_cont_p0+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p1], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p1 = prefix+'_combined_contp1'
os.system('rm -rf %s*' % combined_cont_p1)
split(vis=combined_cont_p0+'.ms', outputvis=combined_cont_p1+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p1+'.ms' , imagename = combined_cont_p1, mask = common_mask, scales = LB_scales, threshold = '0.019mJy', savemodel = 'modelcolumn', robust=0.5)
estimate_SNR(combined_cont_p1+'.image', disk_mask = common_mask, noise_mask = noise_annulus)

#HD143006_combined_contp1.image
#Beam 0.052 arcsec x 0.037 arcsec (86.45 deg)
#Flux inside disk mask: 57.79 mJy
#Peak intensity of source: 0.61 mJy/beam
#rms: 1.27e-02 mJy/beam
#Peak SNR: 47.87

# SNR change minimal, but map improvements.  Continue.
#second round of phase self-cal for long baseline data
combined_p2 = prefix+'_combined.p2'
os.system('rm -rf '+combined_p2)
gaincal(vis=combined_cont_p1+'.ms' , caltable=combined_p2, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='360s', minsnr=1.5, minblperant=4)
"""
4 of 41 solutions flagged due to SNR < 1.5 in spw=21 at 2017/09/26/22:55:42.2
1 of 41 solutions flagged due to SNR < 1.5 in spw=21 at 2017/09/26/23:05:17.7
3 of 41 solutions flagged due to SNR < 1.5 in spw=21 at 2017/09/26/23:09:11.0
1 of 41 solutions flagged due to SNR < 1.5 in spw=21 at 2017/09/26/23:29:48.0
1 of 41 solutions flagged due to SNR < 1.5 in spw=21 at 2017/09/26/23:33:55.4
11 of 41 solutions flagged due to SNR < 1.5 in spw=21 at 2017/09/26/23:36:34.8
5 of 41 solutions flagged due to SNR < 1.5 in spw=21 at 2017/09/26/23:50:31.5
2 of 44 solutions flagged due to SNR < 1.5 in spw=25 at 2017/11/26/14:10:01.0
5 of 44 solutions flagged due to SNR < 1.5 in spw=25 at 2017/11/26/14:16:51.3
2 of 44 solutions flagged due to SNR < 1.5 in spw=25 at 2017/11/26/14:23:33.1
6 of 44 solutions flagged due to SNR < 1.5 in spw=25 at 2017/11/26/14:30:12.3
11 of 43 solutions flagged due to SNR < 1.5 in spw=25 at 2017/11/26/14:37:10.0
1 of 44 solutions flagged due to SNR < 1.5 in spw=25 at 2017/11/26/14:50:06.0
1 of 44 solutions flagged due to SNR < 1.5 in spw=25 at 2017/11/26/14:53:05.9
"""

if not skip_plots:
    plotcal(caltable=combined_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = combined_obs6_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=combined_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = combined_obs7_timerange, plotrange=[0,0,-180,180])

applycal(vis=combined_cont_p1+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p2], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p2 = prefix+'_combined_contp2'
os.system('rm -rf %s*' % combined_cont_p2)
split(vis=combined_cont_p1+'.ms', outputvis=combined_cont_p2+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p2+'.ms' , imagename = combined_cont_p2, mask = common_mask, scales = LB_scales, threshold = '0.019mJy', savemodel = 'modelcolumn', robust=0.5)
estimate_SNR(combined_cont_p2+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_combined_contp2.image
#Beam 0.052 arcsec x 0.037 arcsec (86.45 deg)
#Flux inside disk mask: 57.77 mJy
#Peak intensity of source: 0.63 mJy/beam
#rms: 1.27e-02 mJy/beam
#Peak SNR: 49.33

#third round of phase self-cal for long baseline data
combined_p3 = prefix+'_combined.p3'
os.system('rm -rf '+combined_p3)
gaincal(vis=combined_cont_p2+'.ms' , caltable=combined_p3, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='180s', minsnr=1.5, minblperant=4)
"""
Many solutions flagged
"""

if not skip_plots:
    plotcal(caltable=combined_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = combined_obs6_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=combined_p3, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = combined_obs7_timerange, plotrange=[0,0,-180,180])

applycal(vis=combined_cont_p2+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p3], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p3 = prefix+'_combined_contp3'
os.system('rm -rf %s*' % combined_cont_p3)
split(vis=combined_cont_p2+'.ms', outputvis=combined_cont_p3+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p3+'.ms' , imagename = combined_cont_p3, mask = common_mask, scales = LB_scales, threshold = '0.019mJy', savemodel = 'modelcolumn', robust=0.5)
estimate_SNR(combined_cont_p3+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_combined_contp3.image
#Beam 0.052 arcsec x 0.037 arcsec (86.45 deg)
#Flux inside disk mask: 57.76 mJy
#Peak intensity of source: 0.66 mJy/beam
#rms: 1.26e-02 mJy/beam
#Peak SNR: 52.21

#fourth round of phase self-cal for long baseline data
combined_p4 = prefix+'_combined.p4'
os.system('rm -rf '+combined_p4)
gaincal(vis=combined_cont_p3+'.ms' , caltable=combined_p4, gaintype='T', combine = 'spw, scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='60s', minsnr=1.5, minblperant=4)
"""
Many more solutions flagged
"""

if not skip_plots:
    plotcal(caltable=combined_p4, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = combined_obs6_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=combined_p4, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = combined_obs7_timerange, plotrange=[0,0,-180,180])

applycal(vis=combined_cont_p3+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p4], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p4 = prefix+'_combined_contp4'
os.system('rm -rf %s*' % combined_cont_p4)
split(vis=combined_cont_p3+'.ms', outputvis=combined_cont_p4+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p4+'.ms' , imagename = combined_cont_p4, mask = common_mask, scales = LB_scales, threshold = '0.019mJy', savemodel = 'modelcolumn', robust=0.5)
estimate_SNR(combined_cont_p4+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_combined_contp4.image
#Beam 0.052 arcsec x 0.037 arcsec (86.45 deg)
#Flux inside disk mask: 57.82 mJy
#Peak intensity of source: 0.69 mJy/beam
#rms: 1.25e-02 mJy/beam
#Peak SNR: 54.93

#fifth round of phase self-cal for long baseline data
combined_p5 = prefix+'_combined.p5'
os.system('rm -rf '+combined_p5)
gaincal(vis=combined_cont_p4+'.ms' , caltable=combined_p5, gaintype='T', combine = 'spw,scan', spw=combined_contspws, refant=combined_refant, calmode='p', solint='30s', minsnr=1.5, minblperant=4)
"""
Many more solutions flagged
"""

if not skip_plots:
    plotcal(caltable=combined_p5, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = combined_obs6_timerange, plotrange=[0,0,-180,180])
    plotcal(caltable=combined_p5, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = combined_obs7_timerange, plotrange=[0,0,-180,180])

applycal(vis=combined_cont_p4+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_p5], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_p5 = prefix+'_combined_contp5'
os.system('rm -rf %s*' % combined_cont_p5)
split(vis=combined_cont_p4+'.ms', outputvis=combined_cont_p5+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_p5+'.ms' , imagename = combined_cont_p5, mask = common_mask, scales = LB_scales, threshold = '0.013mJy', savemodel = 'modelcolumn', robust=0.5)
estimate_SNR(combined_cont_p5+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_combined_contp5.image
#Beam 0.052 arcsec x 0.037 arcsec (86.45 deg)
#Flux inside disk mask: 58.07 mJy
#Peak intensity of source: 0.70 mJy/beam
#rms: 1.25e-02 mJy/beam
#Peak SNR: 55.94

# that's about it. Try amp self-cal.
combined_ap = prefix+'_combined.ap'
os.system('rm -rf '+combined_ap)
gaincal(vis=combined_cont_p5+'.ms' , caltable=combined_ap, gaintype='T', combine = 'spw,scan', spw=combined_contspws, refant=combined_refant, calmode='ap', solint='900s', minsnr=3.5, minblperant=4, solnorm = False)

"""
16 of 41 solutions flagged due to SNR < 3 in spw=21 at 2017/09/26/22:55:42.2
18 of 41 solutions flagged due to SNR < 3 in spw=21 at 2017/09/26/23:11:46.0
2 of 41 solutions flagged due to SNR < 3 in spw=21 at 2017/09/26/23:47:20.8
7 of 44 solutions flagged due to SNR < 3 in spw=25 at 2017/11/26/14:10:01.0
8 of 44 solutions flagged due to SNR < 3 in spw=25 at 2017/11/26/14:26:03.1
"""

if not skip_plots:
    plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = combined_obs6_timerange, plotrange=[0,0,0,2]) 
    plotcal(caltable=combined_ap, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = combined_obs7_timerange, plotrange=[0,0,0,2])

applycal(vis=combined_cont_p5+'.ms', spw=combined_contspws, spwmap = combined_spwmap, gaintable=[combined_ap], interp = 'linearPD', calwt = True, applymode = 'calonly')

combined_cont_ap = prefix+'_combined_contap'
os.system('rm -rf %s*' % combined_cont_ap)
split(vis=combined_cont_p5+'.ms', outputvis=combined_cont_ap+'.ms', datacolumn='corrected')

tclean_wrapper(vis = combined_cont_ap+'.ms' , imagename = combined_cont_ap, mask = common_mask, scales = LB_scales, threshold = '0.012mJy', savemodel = 'modelcolumn', robust=0.5)
estimate_SNR(combined_cont_ap+'.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_combined_contap.image
#Beam 0.047 arcsec x 0.032 arcsec (83.66 deg)
#Flux inside disk mask: 58.23 mJy
#Peak intensity of source: 0.57 mJy/beam
#rms: 1.16e-02 mJy/beam
#Peak SNR: 49.11

tclean_wrapper(vis = combined_cont_ap+'.ms' , imagename = combined_cont_ap+'_rob0.8', mask = common_mask, scales = LB_scales, threshold = '0.011mJy', savemodel = 'modelcolumn', robust=0.8)
estimate_SNR(combined_cont_ap+'_rob0.8.image', disk_mask = common_mask, noise_mask = noise_annulus)
#HD143006_combined_contap_rob0.8.image
#Beam 0.053 arcsec x 0.036 arcsec (84.02 deg)
#Flux inside disk mask: 58.19 mJy
#Peak intensity of source: 0.67 mJy/beam
#rms: 1.07e-02 mJy/beam
#Peak SNR: 63.10


# For a similar beam size, there is a 4% reduction of peak flux while the noise in the map reduced by 17%, so will keep amplitude selfcalibration.

#Export fits file and final calibrated ms file
exportfits(imagename=combined_cont_ap+'_rob0.8.image',fitsimage=prefix+'_script_image.fits',overwrite=True)

final_ms =  prefix+'_cont_final.ms'
os.system('rm -rf %s*' % final_ms)
split(vis=combined_cont_ap+'.ms', outputvis=final_ms, datacolumn='data')
