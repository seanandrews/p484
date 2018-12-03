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

split(vis=data_params['SB1']['vis'],
              field = data_params['SB1']['field'],
              spw = '0~3',      
              outputvis = prefix+'_SB1_lines.ms',
              width = [1,128,128,128],
              datacolumn='data',
              intent = 'OBSERVE_TARGET#ON_SOURCE',
              keepflags = False)

#split out individual observations from long-baseline dataset 
split(vis=data_params['LB1']['vis'],
              field = '4',
              spw = '0~3',      
              outputvis = prefix+'_LB1_lines_exec0.ms',
              width = [128,128,128,1],
              timebin = '6s',
              datacolumn='data',
              intent = 'OBSERVE_TARGET#ON_SOURCE',
              keepflags = False)

split(vis=data_params['LB1']['vis'],
              field = '4',
              spw = '4~7',      
              outputvis = prefix+'_LB1_lines_exec1.ms',
              width = [128,128,128,1],
              timebin = '6s',
              datacolumn='data',
              intent = 'OBSERVE_TARGET#ON_SOURCE',
              keepflags = False)


#####rescale fluxes
rescale_flux(prefix+'_LB1_lines_exec1.ms', [0.968])

"""
Start of self-calibration of the short-baseline data 
"""
SB_CO = prefix+'_SB1_lines'
SB_contspws = '0~3' #change as appropriate
applycal(vis=SB_CO+'.ms',  spw=SB_contspws, gaintable=[prefix+'_SB.p1', prefix+'_SB.p2', prefix+'_SB.p3', prefix+'_SB.ap'], interp = 'linearPD', calwt=True, flagbackup=False)


#split out the corrected column
split(vis = SB_CO+'.ms',
      outputvis = SB_CO+'_selfcal.ms',
      datacolumn = 'corrected',
      keepflags = False)


#now we concatenate all the data together

combined_CO = prefix+'_combined_CO'
os.system('rm -rf %s*' % combined_CO)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [SB_CO+'_selfcal.ms', prefix+'_LB1_lines_exec0.ms', prefix+'_LB1_lines_exec1_rescaled.ms'], concatvis = combined_CO+'.ms' , dirtol = '0.1arcsec', copypointing = False) 


combined_contspws = '0~11'
combined_spwmap =  [0,0,0,0,4,4,4,4,8,8,8,8] #note that the tables produced by gaincal in 5.1.1 have spectral windows numbered differently if you use the combine = 'spw' option. Previously, all of the solutions would be written to spectral window 0. Now, they are written to the first window in each execution block. So, the spwmap argument has to correspond to the first window in each execution block you want to calibrate. 

applycal(vis=combined_CO+'.ms', spw=combined_contspws, spwmap = [combined_spwmap]*7, gaintable=[prefix+'_combined.p1',prefix+'_combined.p2', prefix+'_combined.p3', prefix+'_combined.p4', prefix+'_combined.p5', prefix+'_combined.p6', prefix+'_combined.ap'], interp = 'linearPD', calwt = True, applymode = 'calonly')


split(vis = combined_CO+'.ms', outputvis = 'WaOph6_CO_only.ms', datacolumn='corrected', keepflags = False, spw = '0,7,11')

CO_mscontsub = 'WaOph6_CO_only.ms.contsub'
os.system('rm -rf '+CO_mscontsub) 
fitspw = '0:0~1858;1984~3839, 1:0~1872;1998~3839, 2:0~1872;1998~3839' # channels for fitting continuum
uvcontsub(vis='WaOph6_CO_only.ms',
          spw='0~2', 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=1,
          want_cont=False) 

tclean(vis= 'WaOph6_CO_only.ms.contsub', 
       imagename = 'WaOph6_CO', 
       spw='0~2',
       specmode = 'cube',
       start='-6km/s',
       width='0.35km/s',
       nchan=65,
       restfreq='230.538GHz',
       outframe='LSRK',
       veltype='radio', 
       deconvolver = 'multiscale',
       scales = [0,10,25,75,150], 
       gain = 0.1,
       weighting='briggs', 
       robust = 1.0,
       cyclefactor = 5, 
       niter = 100000,
       imsize = 1500,
       cell = '0.01arcsec', 
       interactive = True,
       threshold = '5mJy',    
       cycleniter = 100,
       nterms = 1,
       restoringbeam = 'common') 

tclean(vis= 'WaOph6_CO_only.ms.contsub', 
       imagename = 'WaOph6_CO_midtaper', 
       spw='0~2',
       specmode = 'cube',
       start='-7km/s',
       width='0.35km/s',
       nchan=65,
       restfreq='230.538GHz',
       outframe='LSRK',
       veltype='radio', 
       deconvolver = 'multiscale',
       scales = [0,10,25,75,150], 
       gain = 0.1,
       weighting='briggs', 
       robust = 0.5,
       cyclefactor = 5, 
       niter = 100000,
       imsize = 1500,
       cell = '0.01arcsec', 
       interactive = True,
       threshold = '4mJy',    
       cycleniter = 100,
       nterms = 1,
       uvtaper = ['0.1arcsec','.03arcsec', '17deg'], 
       restoringbeam = 'common') 

immoments(imagename = 'WaOph6_CO_midtaper.image', moments = [0], includepix = [.004,20], outfile = 'WaOph6_CO_midtaper.mom0')
immoments(imagename = 'WaOph6_CO_midtaper.image', moments = [1], includepix = [.0075,20], outfile = 'WaOph6_CO_midtaper.mom1')
immoments(imagename = 'WaOph6_CO_midtaper.image', moments = [8], includepix = [.0075,20], outfile = 'WaOph6_CO_midtaper.mom8')

