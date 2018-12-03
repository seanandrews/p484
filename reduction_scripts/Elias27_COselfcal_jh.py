"""
This script was written for CASA 5.1.1

Datasets calibrated (in order of date observed):
SB1: 2013.1.00498.L/Elias_24_a_06_TM1  
     Observed 21 July 2015 (1 execution block)
     PI: L. Perez
     Downloaded from archive and calibrated with archival scripts
LB1: 2016.1.00484.L/Elias_27_a_06_TM1 
     Observed 07 September 2017 and 3 October 2017 (2 execution blocks)
     PI: S. Andrews
     As delivered to PI

"""
import os

execfile('/pool/firebolt1/p484/reduction_scripts/reduction_utils.py')

skip_plots = False #if this is true, all of the plotting and inspection steps will be skipped and the script can be executed non-interactively in CASA if all relevant values have been hard-coded already 

#to fill this dictionary out, use listobs for the relevant measurement set 

prefix = 'Elias27' #string that identifies the source and is at the start of the name for all output files

#Note that if you are downloading data from the archive, your SPW numbering may differ from the SPWs in this script depending on how you split your data out!! 
data_params = {'SB1': {'vis' : '/data/sandrews/LP/archival/2013.1.00498.S/science_goal.uid___A001_X13a_Xeb/group.uid___A001_X13a_Xec/member.uid___A001_X13a_Xed/calibrated/uid___A002_Xa657ad_X736.ms.split.cal',
                       'name' : 'SB1',
                       'field': 'Elia_2-27',
                       'line_spws': np.array([1,5,6]), #SpwIDs of windows with lines that need to be flagged (this needs to be edited for each short baseline dataset)
                       'line_freqs': np.array([2.30538e11, 2.2039868420e11, 2.1956035410e11]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz)
                      }, #information about the short baseline measurement sets (SB1, SB2, SB3, etc in chronological order)
               'LB1': {'vis' : '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X50/group.uid___A001_X8c5_X51/member.uid___A001_X8c5_X52/calibrated/calibrated_final.ms',
                       'name' : 'LB1',
                       'field' : 'Elias_27',
                       'line_spws': np.array([3,7]), #these are generally going to be the same for most of the long-baseline datasets. Some datasets only have one execution block or have strange numbering
                       'line_freqs': np.array([2.30538e11, 2.30538e11]), #frequencies (Hz) corresponding to line_spws (in most cases this is just the 12CO 2-1 line at 230.538 GHz) 
                      }
               }


split(vis=data_params['SB1']['vis'],
              field = data_params['SB1']['field'],
              spw = '0~7',      
              outputvis = prefix+'_SB1_lines.ms',
              width = [120,1,128,60,60,960,960,128],
              datacolumn='data',
              intent = 'OBSERVE_TARGET#ON_SOURCE',
              keepflags = False)

#split out individual observations from long-baseline dataset 
split(vis=data_params['LB1']['vis'],
              field = 'Elias_27',
              spw = '0~7',      
              outputvis = prefix+'_LB1_lines.ms',
              width = [128,128,128,1,128,128,128,1],
              timebin = '6s',
              datacolumn='data',
              intent = 'OBSERVE_TARGET#ON_SOURCE',
              keepflags = False)

common_dir = 'J2000 16h26m45.022s -024.23.08.273' #choose peak of LB1 to be the common direction  

shiftname = prefix+'_SB1_lines_shift'
fixvis(vis=prefix+'_SB1_lines.ms', outputvis=shiftname+'.ms', field = data_params['SB1']['field'], phasecenter='J2000 16h26m45.021955s -24d23m08.25057s') 
fixplanets(vis = shiftname+'.ms', field = data_params['SB1']['field'], direction = common_dir) 

shiftname = prefix+'_LB1_lines_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_LB1_lines.ms', outputvis=shiftname+'.ms', field = data_params['LB1']['field'], phasecenter='ICRS 16h26m45.021309s -24d23m08.28623s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['LB1']['field'], direction = common_dir)


"""
Start of self-calibration of the short-baseline data 
"""
SB_CO = prefix+'_SB1_lines_shift'
SB_contspws = '0~7' #change as appropriate
applycal(vis=SB_CO+'.ms',  spw=SB_contspws, gaintable=[prefix+'_SB.p1', prefix+'_SB.p2',prefix+'_SB.ap'], interp = 'linearPD', calwt=True, flagbackup=False)

#split out the corrected column
split(vis = SB_CO+'.ms',
      outputvis = SB_CO+'_selfcal.ms',
      datacolumn = 'corrected',
      keepflags = False)


combined_CO = prefix+'_combined_CO'
os.system('rm -rf %s*' % combined_CO)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [SB_CO+'_selfcal.ms', prefix+'_LB1_lines_shift.ms'], concatvis = combined_CO+'.ms' , dirtol = '0.1arcsec', copypointing = False) 


combined_contspws = '0~15'
combined_spwmap =  [0,0,0,0,0,0,0,0,8,8,8,8,12,12,12,12] #note that the tables produced by gaincal in 5.1.1 have spectral windows numbered differently if you use the combine = 'spw' option. Previously, all of the solutions would be written to spectral window 0. Now, they are written to the first window in each execution block. So, the spwmap argument has to correspond to the first window in each execution block you want to calibrate. 

applycal(vis=combined_CO+'.ms', spw=combined_contspws, spwmap = [combined_spwmap]*5, gaintable=[prefix+'_combined.p1',prefix+'_combined.p2', prefix+'_combined.p3', prefix+'_combined.p4',prefix+'_combined.ap'], interp = 'linearPD', calwt = True, applymode = 'calonly')


split(vis = combined_CO+'.ms', outputvis = 'Elias27_CO_only.ms', datacolumn='corrected', keepflags = False, spw = '1,11,15')

flagdata(vis='Elias27_CO_only.ms', mode='manual', spw='0', flagbackup=False, field='0', scan='32', antenna='DA46')

CO_mscontsub = 'Elias27_CO_only.ms.contsub'
os.system('rm -rf '+CO_mscontsub) 
fitspw = '0:0~167;215~1920, 1:0~1880;1950~3839, 2:0~1880;1950~3839' # channels for fitting continuum
uvcontsub(vis='Elias27_CO_only.ms',
          spw='0~2', 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=1,
          want_cont=False) 

tclean(vis='Elias27_CO_only.ms.contsub', imagename='Elias27_COtaper',specmode = 'cube',imsize=2000, deconvolver = 'multiscale',  
      start='-6km/s',width='0.35km/s',nchan=50,  
      outframe='LSRK', veltype='radio', restfreq='230.538GHz',
      cell='0.01arcsec', scales = [0,10,50,100,200,300], gain=0.1,
      weighting='briggs', robust=0.5,threshold = '5mJy', niter = 50000, uvtaper = ['.1arcsec', '0.07arcsec', '-35deg'], 
      interactive=True, nterms = 1, restoringbeam = 'common') 

immoments(imagename = 'Elias27_COtaper.image', moments = [0], includepix = [.005,20], outfile = 'Elias27_COtaper.mom0')
immoments(imagename = 'Elias27_COtaper.image', moments = [1], includepix = [.0075,20], outfile = 'Elias27_COtaper.mom1')
immoments(imagename = 'Elias27_COtaper.image', moments = [8], includepix = [.0075,20], outfile = 'Elias27_COtaper.mom8')

tclean(vis='Elias27_CO_only.ms.contsub', imagename='Elias27_COclipped',specmode = 'cube',imsize=2000, deconvolver = 'multiscale',  
      start='-6km/s',width='0.35km/s',nchan=50,  
      outframe='LSRK', veltype='radio', restfreq='230.538GHz',
      cell='0.01arcsec', scales = [0,10,50,100,200,300], gain=0.1,
      weighting='briggs', robust=0.5,threshold = '15mJy', niter = 50000, uvtaper = ['.1arcsec', '0.07arcsec', '-35deg'], uvrange = '>20klambda',
      interactive=True, nterms = 1, restoringbeam = 'common') 





