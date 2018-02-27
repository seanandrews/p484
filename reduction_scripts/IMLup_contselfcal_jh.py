"""
This script was written for CASA 5.1.1

Datasets calibrated (in order of date observed): 
SB1: 2013.1.00226.S/im_lup_a_06_TE 
     PI: K. Oberg
     Observed 06 July 2014 (1 execution block)
     As delivered to PI
SB2: 2013.1.00226.S/im_lup_b_06_TE 
     Observed 17 July 2014 (1 execution block)
     PI: K. Oberg
     Downloaded from archive; see Huang et al. 2017 for additional comments on the reduction 
SB3: 2013.1.00694.S/IM_Lup_a_06_TC 
     PI: L.I. Cleeves
     Observed 29 January 2015 (1 execution block)
     Downloaded from archive and calibrated w/ pipeline
SB4: 2013.1.00694.S/IM_Lup_a_06_TE 
     PI: L.I. Cleeves 
     Observed 13 May 2015 (1 execution block)
     Downloaded from archive and calibrated w/ pipeline
SB5: 2013.1.00798.S/Im_Lup_a_06_TE 
     PI: C. Pinte
     Observed 9 June 2015 to 10 June 2015 (1 execution block)
     Downloaded from archive and calibrated w/ pipeline
LB1: 2016.1.00484.L/IM_Lupi_a_06_TM1 
     PI: S. Andrews
     Observed 25 September 2017 and 24 October 2017 (2 execution blocks)
     As delivered to PI

Incidentally, there are windows covering 13CS 5-4 in 2013.1.00798.S/Im_Lup_a_06_TE and 2013.1.00226.S/im_lup_a_06_TE
There's nothing obvious in either window, but if you're curious, you could consider combining them 

"""
import os

execfile('/pool/firebolt1/LPscratch/newscripts/reduction_utils.py')

skip_plots = True #if this is true, all of the plotting and inspection steps will be skipped and the script can be executed non-interactively in CASA if all relevant values have been hard-coded already 

#to fill this dictionary out, use listobs for the relevant measurement set 

prefix = 'IMLup' #string that identifies the source and is at the start of the name for all output files


#Note that if you downloaded data from the archive, your SPW numbering may differ from the SPWs in this script depending on how you split your data out!! 
data_params = {'SB1': {'vis' : '/data/astrochem1/jane/DeutChem/ImLup/deutcal/calibrated.ms',
                       'name' : 'SB1',
                       'field': 'im_lup',
                       'line_spws': np.array([11]), #SpwIDs of windows with lines that need to be flagged (this needs to be edited for each short baseline dataset)
                       'line_freqs': np.array([2.30538e11]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz)
                      }, #information about the short baseline measurement sets (SB1, SB2, SB3, etc in chronological order)
               'SB2': {'vis' : '/data/astrochem1/jane/DeutChem/ImLup/uid___A002_X86e521_X5ed.ms.split.cal',
                       'name' : 'SB2',
                       'field': 'im_lup',
                       'line_spws': np.array([]), 
                       'line_freqs': np.array([]),
                      }, 
               'SB3': {'vis' : '/data/sandrews/LP/archival/2013.1.00694.S/science_goal.uid___A001_X121_X2c7/group.uid___A001_X121_X2c8/member.uid___A001_X121_X2cb/calibrated/uid___A002_X9aa6ef_X12b7.ms.split.cal',
                       'name' : 'SB3',
                       'field': 'IM_Lup',
                       'line_spws': np.array([]), 
                       'line_freqs': np.array([]),
                      }, 
               'SB4': {'vis' : '/data/sandrews/LP/archival/2013.1.00694.S/science_goal.uid___A001_X121_X2c7/group.uid___A001_X121_X2c8/member.uid___A001_X121_X2c9/calibrated/uid___A002_Xa055bc_X1360.ms.split.cal',
                       'name' : 'SB4',
                       'field': 'IM_Lup',
                       'line_spws': np.array([]), 
                       'line_freqs': np.array([]),
                      }, 
               'SB5': {'vis' : '/data/sandrews/LP/archival/2013.1.00798.S/science_goal.uid___A001_X122_X5dc/group.uid___A001_X122_X5dd/member.uid___A001_X122_X5de/calibrated/uid___A002_Xa2ea64_Xa78.ms.split.cal',
                       'name' : 'SB5',
                       'field': 'Im_Lupi',
                       'line_spws': np.array([1]), 
                       'line_freqs': np.array([2.30538e11]),
                      }, 
               'LB1': {'vis' : '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X70/group.uid___A001_X8c5_X71/member.uid___A001_X8c5_X72/calibrated/calibrated_final.ms',
                       'name' : 'LB1',
                       'field' : 'IM_Lupi',
                       'line_spws': np.array([3,7]), #these are generally going to be the same for most of the long-baseline datasets. Some datasets only have one execution block or have strange numbering
                       'line_freqs': np.array([2.30538e11, 2.30538e11]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz) 
                      }  #information about the long baseline measurement sets
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

"""
Identify channels to flag based on the known velocity range of the line emission. The velocity range is based on line images from early reductions. If you are starting from scratch, 
you can estimate the range from the plotms command above. You may wish to limit your uvrange to 0~300 or so to only view the baselines with the highest amplitudes.     
"""
SB1_flagchannels = get_flagchannels(data_params['SB1'], prefix, velocity_range = np.array([-5,15]))
"""
Produces spectrally averaged continuum datasets
If you only want to include a subset of the windows, you can manually pass in values for contspw and width_array, e.g.
avg_cont(data_params[i], output_prefix, flagchannels = flagchannels_string, contspws = '0~2', width_array = [480,8,8]).
If you don't pass in values, all of the SPWs will be split out and the widths will be computed automatically to enforce a maximum channel width of 125 MHz.
WARNING: Only use the avg_cont function if the total bandwidth is recorded correctly in the original MS. There is sometimes a bug in CASA that records incorrect total bandwidths
"""
avg_cont(data_params[i], prefix, flagchannels = SB1_flagchannels, contspws = '8~12', width_array = [960,960,960,960,960])

SB2_flagchannels = get_flagchannels(data_params['SB2'], prefix, velocity_range = np.array([-5,15]))
avg_cont(data_params[i], prefix, flagchannels = flagchannels_string, contspws = '8~12', width_array = [1920, 1920, 960,960,960,960])

SB3_flagchannels = get_flagchannels(data_params['SB2'], prefix, velocity_range = np.array([-5,15]))
avg_cont(data_params[i], prefix, flagchannels = flagchannels_string, contspws = '2~3', width_array = [8,8])

SB3_flagchannels = get_flagchannels(data_params['SB3'], prefix, velocity_range = np.array([-5,15]))
avg_cont(data_params[i], prefix, flagchannels = flagchannels_string, contspws = '2~3', width_array = [8,8])

SB5_flagchannels = get_flagchannels(data_params['SB5'], prefix, velocity_range = np.array([-5,15]))
avg_cont(data_params[i], prefix, flagchannels = flagchannels_string, contspws = '0~2', width_array = [1920,1920,8])

# sample command to check that amplitude vs. uvdist looks normal
# plotms(vis=prefix+'_SB1_initcont.ms', xaxis='uvdist', yaxis='amp', coloraxis='spw', avgtime='30', avgchannel='16')
