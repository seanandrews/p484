"""
This script was written for CASA 5.1.1

Datasets calibrated (in order of date observed): 
SB1: 2013.1.00226.S/im_lup_a_06_TE 
     PI: K. Oberg
     Observed 06 July 2014 (1 execution block)
     As delivered to PI
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

execfile('/pool/firebolt1/p484/reduction_scripts/reduction_utils.py')

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

split(vis=data_params['SB1']['vis'],
              field = data_params['SB1']['field'],
              spw = '8~12',      
              outputvis = prefix+'_SB1_lines.ms',
              width = [960,960,960,1,3840],
              datacolumn='data',
              intent = 'OBSERVE_TARGET#ON_SOURCE',
              keepflags = False)


split(vis=data_params['SB5']['vis'],
              field = data_params['SB5']['field'],
              spw = '0~2',      
              outputvis = prefix+'_SB5_lines.ms',
              width = [1920,1,128],
              datacolumn='data',
              intent = 'OBSERVE_TARGET#ON_SOURCE',
              keepflags = False)

#split out individual observations from long-baseline dataset 
split(vis=data_params['LB1']['vis'],
              field = '3',
              spw = '0~3',      
              outputvis = prefix+'_LB1_lines_exec0.ms',
              width = [128,128,128,1],
              timebin = '6s',
              datacolumn='data',
              intent = 'OBSERVE_TARGET#ON_SOURCE',
              keepflags = False)

split(vis=data_params['LB1']['vis'],
              field = '5',
              spw = '4~7',      
              outputvis = prefix+'_LB1_lines_exec1.ms',
              width = [128,128,128,1],
              timebin = '6s',
              datacolumn='data',
              intent = 'OBSERVE_TARGET#ON_SOURCE',
              keepflags = False)



common_dir = 'J2000 15h56m09.18880s -037.56.06.527374' #choose peak of first execution of LB1 to be the common direction (the better-quality of the high-res observations)  


shiftname = prefix+'_SB1_lines_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_SB1_lines.ms', outputvis=shiftname+'.ms', field = data_params['SB1']['field'], phasecenter='J2000 15h56m09.192086s -37d56m06.44353s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['SB1']['field'], direction = common_dir) #fixplanets works only with J2000, not ICRS

shiftname = prefix+'_SB5_lines_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_SB5_lines.ms', outputvis=shiftname+'.ms', field = data_params['SB5']['field'], phasecenter='J2000 15h56m09.188402s -37d56m06.50811s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['SB5']['field'], direction = common_dir) #fixplanets works only with J2000, not ICRS

shiftname = prefix+'_LB1_lines_exec0_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_LB1_lines_exec0.ms', outputvis=shiftname+'.ms', field = data_params['LB1']['field'], phasecenter='ICRS 15h56m09.188385s -37d56m06.54177s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['LB1']['field'], direction = common_dir)

shiftname = prefix+'_LB1_lines_exec1_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis=prefix+'_LB1_lines_exec1.ms', outputvis=shiftname+'.ms', field = data_params['LB1']['field'], phasecenter= 'ICRS 15h56m09.188671s -37d56m06.54163s') #get phasecenter from Gaussian fit      
fixplanets(vis = shiftname+'.ms', field = data_params['LB1']['field'], direction = common_dir)


#now correct the flux of the discrepant dataset
rescale_flux(prefix+'_LB1_lines_exec1_shift.ms', [0.892])
#Splitting out rescaled values into new MS: IMLup_LB1_lines_exec1_shift_rescaled.ms

"""
Start of self-calibration of the short-baseline data 
"""
#merge the short-baseline execution blocks into a single MS (the continuum MS for SB2, SB3, and SB4 are included to get the SPW numbering right for applycal)
SB_CO = prefix+'_SB_CO'
os.system('rm -rf %s*' % SB_CO)
#pay attention here and make sure you're selecting the shifted (and potentially rescaled) measurement sets
concat(vis = [prefix+'_SB1_lines_shift.ms',  prefix+'_SB2_initcont_shift.ms',prefix+'_SB3_initcont_shift.ms',prefix+'_SB4_initcont_shift.ms', prefix+'_SB5_lines_shift.ms'], concatvis = SB_CO+'.ms', dirtol = '0.1arcsec', copypointing = False) 

SB_contspws = '0~17' #change as appropriate
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
concat(vis = [SB_CO+'_selfcal.ms', prefix+'_LB1_lines_exec0_shift.ms', prefix+'_LB1_lines_exec1_shift_rescaled.ms'], concatvis = combined_CO+'.ms' , dirtol = '0.1arcsec', copypointing = False) 

combined_contspws = '0~25'
combined_spwmap =  [0,0,0,0,0,5,5,5,5,5,5,11,11,13,13,15,15,15,18,18,18,18,22,22,22,22] #note that the tables produced by gaincal in 5.1.1 have spectral windows numbered differently if you use the combine = 'spw' option. Previously, all of the solutions would be written to spectral window 0. Now, they are written to the first window in each execution block. So, the spwmap argument has to correspond to the first window in each execution block you want to calibrate. 

applycal(vis=combined_CO+'.ms', spw=combined_contspws, spwmap = [combined_spwmap]*6, gaintable=[prefix+'_combined.p1',prefix+'_combined.p2', prefix+'_combined.p3', prefix+'_combined.p4', prefix+'_combined.p5', prefix+'_combined.ap'], interp = 'linearPD', calwt = True, applymode = 'calonly')

split(vis = combined_CO+'.ms', outputvis = 'IMLup_CO_only.ms', datacolumn='corrected', keepflags = False, spw = '3, 16, 21, 25')

CO_mscontsub = 'IMLup_CO_only.ms.contsub'
os.system('rm -rf '+CO_mscontsub) 
fitspw = '0:0~432;686~939, 1:0~692;1198~1919, 2:0~1889;1954~3839, 3:0~1889;1954~3839' # channels for fitting continuum
uvcontsub(vis='IMLup_CO_only.ms',
          spw='0~3', 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=1,
          want_cont=False) 


split(vis = 'IMLup_CO_only.ms.contsub', outputvis  = 'IMLup_CO_LBonly.ms.contsub', spw = '2,3', datacolumn = 'data') 

split(vis = 'IMLup_CO_only.ms.contsub', outputvis  = 'IMLup_CO_SBonly.ms.contsub', spw = '0,1', datacolumn = 'data') 

CO_cvel = 'IMLup_CO.ms.contsub.cvel'

os.system('rm -rf '+ CO_cvel)
mstransform(vis = 'IMLup_CO_only.ms.contsub', outputvis = CO_cvel,  keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='-5.0km/s',width='0.35km/s',nchan=50, outframe='LSRK', veltype='radio', restfreq='230.538GHz')

LB_cvel = 'IMLup_CO_LBonly.ms.contsub.cvel'

os.system('rm -rf '+ LB_cvel)
mstransform(vis = 'IMLup_CO_LBonly.ms.contsub', outputvis = LB_cvel,  keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='-5.0km/s',width='0.35km/s',nchan=50, outframe='LSRK', veltype='radio', restfreq='230.538GHz')



SB_cvel = 'IMLup_CO_SBonly.ms.contsub.cvel'

os.system('rm -rf '+ SB_cvel)
mstransform(vis = 'IMLup_CO_SBonly.ms.contsub', outputvis = SB_cvel,  keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='-5.0km/s',width='0.35km/s',nchan=50, outframe='LSRK', veltype='radio', restfreq='230.538GHz')

tclean(vis=SB_cvel, imagename='IMLup_COlowres',specmode = 'cube',imsize=500, deconvolver = 'multiscale',  
      start='-5km/s',width='0.35km/s',nchan=50,  
      outframe='LSRK', veltype='radio', restfreq='230.538GHz',
      cell='0.05arcsec', scales = [0,10,20,30], gain=0.1,
      weighting='briggs', robust=0.5,threshold = '10.0mJy', niter = 100000,  
      interactive=True, nterms = 1, restoringbeam = 'common') 

immoments(imagename = 'IMLup_COlowres.image', moments = [0], includepix = [.003,20], outfile = 'IMLup_COlowres.mom0')

tclean(vis=['IMLup_CO_SBonly.ms.contsub.cvel','IMLup_CO_LBonly.ms.contsub.cvel'], imagename='IMLup_COhires',specmode = 'cube',imsize=1500, deconvolver = 'multiscale',  
      start='-5km/s',width='0.35km/s',nchan=50,  
      outframe='LSRK', veltype='radio', restfreq='230.538GHz',
      cell='0.01arcsec', scales = [0,10,50,100,200,300], gain=0.1,
      weighting='briggs', robust=0.5,threshold = '6.0mJy', niter = 100000, uvtaper = '0.05arcsec', 
      interactive=True, nterms = 1, restoringbeam = 'common') 

immoments(imagename = 'IMLup_COhires.image', moments = [0], includepix = [.004,20], outfile = 'IMLup_COhhires.mom0')

immoments(imagename = 'IMLup_COhires.image', moments = [1], includepix = [.006,20], outfile = 'IMLup_COhhires.mom1')

immoments(imagename = 'IMLup_COhires.image', moments = [8], includepix = [.004,20], outfile = 'IMLup_COhhires.mom8')

tclean(vis=['IMLup_CO_SBonly.ms.contsub.cvel','IMLup_CO_LBonly.ms.contsub.cvel'], imagename='IMLup_COmidtaper',specmode = 'cube',imsize=2000, deconvolver = 'multiscale',  
      start='-5km/s',width='0.35km/s',nchan=50,  
      outframe='LSRK', veltype='radio', restfreq='230.538GHz',
      cell='0.01arcsec', scales = [0,10,50,100,200,300], gain=0.1,
      weighting='briggs', robust=0,threshold = '10.0mJy', niter = 50000, uvtaper = '0.1arcsec', 
      interactive=True, nterms = 1, restoringbeam = 'common') 

immoments(imagename = 'IMLup_COmidtaper.image', moments = [0], includepix = [.004,20], outfile = 'IMLup_COmidtaper.mom0')
immoments(imagename = 'IMLup_COmidtaper.image', moments = [1], includepix = [.01,20], outfile = 'IMLup_COmidtaper.mom1')
