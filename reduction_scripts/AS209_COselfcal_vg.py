# CO data
sys.path.append('/home/vguzman/local/analysis_scripts/')
import analysisUtils as au
execfile('/home/vguzman/projects/Disks-Large-Program/data-reduction/reduction_scripts/reduction_utils.py')

# split data
# adding more spw in SB1, SB5 and LB to match number of spws in calibration tables.. this is needed to apply the calibration tables

# SB data
# PI: Oberg
ddir = '/home/vguzman/projects/Disks-Large-Program/data-reduction/data-as209/CO-data/'
split(vis=ddir+'uid___A002_X85c183_Xf7d.ms.split.cal',outputvis='AS209_SB1_initCO.ms',spw='4~11,15',width=[960,960,960,960,960,960,960,960,1],field='as_209',datacolumn='data') # CO in spw 15
# PI: Fedele
ddir = '/home/vguzman/projects/Disks-Large-Program/data-reduction/data-as209/2015.1.00486.S/science_goal.uid___A001_X340_X69/group.uid___A001_X340_X6a/member.uid___A001_X340_X6b/calibrated/'
split(vis=ddir+'uid___A002_Xb87877_X5849.ms.split.cal',outputvis='AS209_SB3_initCO.ms',spw='1',field = 'AS_209',datacolumn='data')
split(vis=ddir+'uid___A002_Xb8bd15_X472.ms.split.cal',outputvis='AS209_SB4_initCO.ms',spw='1',field = 'AS_209',datacolumn='data')
# PI: Andrews
ddir = '/home/vguzman/projects/Disks-Large-Program/data-reduction/data-as209/CO-data/' 
split(vis=ddir+'calibrated_final_SB_LP.ms',outputvis='AS209_SB5_initCO.ms',spw='0,1,2,3',width=[1,128,128,128],field = 'AS_209',datacolumn='data') # CO in spw 0

# LB data
# restore LB data before spectral lines were flagged
#flagmanager(vis='../data-as209/calibrated_final.ms',mode='list')
flagmanager(vis='../data-as209/calibrated_final.ms',mode='restore',versionname='before_cont_flags')
# PI: Andrews
ddir = '/home/vguzman/projects/Disks-Large-Program/data-reduction/data-as209/'  
split(vis=ddir+'calibrated_final.ms',outputvis='AS209_LB_initCO.ms',spw='0~7',width=[128,128,128,1,128,128,128,1],field = 'AS_209',datacolumn='data') # CO in spws 3,7

#splitting out the individual execution blocks
split_all_obs('AS209_LB_initCO.ms', 'AS209_LB_initCO_exec')

# Align images; get phase center from Gaussian fit of the continuum image
common_dir = 'J2000 16h49m15.29463s -014.22.09.048165' # peak of second execution of LB1 continuum (the better-quality of the high-res observations)   

shiftname = 'AS209_SB1_initCO_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis='AS209_SB1_initCO.ms', outputvis=shiftname+'.ms', field = 'as_209', phasecenter='J2000 16h49m15.29419s -14d22m09.04819s') 
fixplanets(vis = shiftname+'.ms', field = 'as_209', direction = common_dir) 

shiftname = 'AS209_SB3_initCO_shift'
os.system('rm -rf %s.ms' % shiftname)                                                                            
fixvis(vis='AS209_SB3_initCO.ms', outputvis=shiftname+'.ms', field = 'AS_209', phasecenter='ICRS 16h49m15.29282s -14d22m09.02516s')      
fixplanets(vis = shiftname+'.ms', field = 'AS_209', direction = common_dir)

shiftname = 'AS209_SB4_initCO_shift'
os.system('rm -rf %s.ms' % shiftname)                                                                             
fixvis(vis='AS209_SB4_initCO.ms', outputvis=shiftname+'.ms', field = 'AS_209', phasecenter='ICRS 16h49m15.29478s -14d22m09.07827s')      
fixplanets(vis = shiftname+'.ms', field = 'AS_209', direction = common_dir)

shiftname = 'AS209_SB5_initCO_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis='AS209_SB5_initCO.ms', outputvis=shiftname+'.ms', field = 'AS_209', phasecenter='ICRS 16h49m15.29314s -14d22m09.06113s')      
fixplanets(vis = shiftname+'.ms', field = 'AS_209', direction = common_dir)

shiftname = 'AS209_LB_initCO_exec0_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis='AS209_LB_initCO_exec0.ms', outputvis=shiftname+'.ms', field = 'AS_209', phasecenter='ICRS 16h49m15.29351s -14d22m09.04933s') 
fixplanets(vis = shiftname+'.ms', field = 'AS_209', direction = common_dir)

shiftname = 'AS209_LB_initCO_exec1_shift'
os.system('rm -rf %s.ms' % shiftname)
fixvis(vis='AS209_LB_initCO_exec1.ms', outputvis=shiftname+'.ms', field = 'AS_209', phasecenter='ICRS 16h49m15.29389s -14d22m09.05971s')
fixplanets(vis = shiftname+'.ms', field = 'AS_209', direction = common_dir)

##########################################################################################################################################

# concat different SB datasets
os.system("rm -rf AS209_SB_CO_selfcal.ms")
concat(vis = ['AS209_SB1_initCO_shift.ms', 'AS209_SB3_initCO_shift.ms', 'AS209_SB4_initCO_shift.ms', 'AS209_SB5_initCO_shift.ms'], concatvis = 'AS209_SB_CO_selfcal.ms', dirtol = '0.1arcsec', copypointing = False)
# 0~14 spws 
# CO data in:
# SB1: spw 8
# SB3: spw 9
# SB4: spw 10
# SB5: spw 11

flagmanager(vis='AS209_SB_CO_selfcal.ms',mode='save',versionname='beforeSelfCal') 
#flagmanager(vis='AS209_SB_CO_selfcal.ms',mode='restore',versionname='beforeSelfCal') 

listcal(vis='../AS209_SB_contp2.ms',caltable='../AS209_SB.p1')
plotcal(caltable='../AS209_SB.p1', xaxis = 'time', yaxis = 'phase',subplot=441,iteration='spw') 
# aply self-cal to SB CO data
# caltables have spws 0~14
# SB1: spws 0,1,2 (spw1 @ 230GHz)
# SB3: spw 9  (@ 232GHz)
# SB4: spw 10 (@ 232GHz)
# SB5: spws 11,12,13,14 (spw11 @ 230GHz)
applycal(vis='AS209_SB_CO_selfcal.ms', spw='8~11', spwmap=[[1,9,10,11]]*3,gaintable=['../AS209_SB.p1','../AS209_SB.p2','../AS209_SB.ap'], interp = ['linearPD']*3, applymode = 'calonly', calwt = True)

##########################################################################################################################################

# combine SB and LB datasets
os.system("rm -rf AS209_CO_combined_selfcal.ms")
concat(vis = ['AS209_SB_CO_selfcal.ms', 'AS209_LB_initCO_exec0_shift.ms', 'AS209_LB_initCO_exec1_shift.ms'], concatvis = 'AS209_CO_combined_selfcal.ms' , dirtol = '0.1arcsec', copypointing = False) 
flagmanager(vis='AS209_CO_combined_selfcal.ms',mode='save',versionname='beforeSelfCal') 
#flagmanager(vis='AS209_CO_combined_selfcal.ms',mode='restore',versionname='beforeSelfCal') 
# 0~22 spws
# CO data in:
# SB1: spw 8
# SB3: spw 9
# SB4: spw 10
# SB5: spw 11
# LB exec0: 18
# LB exec1: 22

plotcal(caltable='../AS209_combined.p2', xaxis = 'time', yaxis = 'phase',subplot=441,iteration='spw') 
# aply self-cal to combined SB+LB CO data
# caltables have spws 0, 3, 9, 10, 11, 15, 19
# SB1: spws 0
# SB3: spw 9
# SB4: spw 10
# SB5: spws 11
# LB0:  spws 15
# LB1:  spws 19

applycal(vis='AS209_CO_combined_selfcal.ms', spw='0~22', spwmap=[[0,0,0,0,0,0,0,0,0,9,10,11,11,11,11,15,15,15,15,19,19,19,19]]*4, gaintable=['../AS209_combined.p1','../AS209_combined.p2','../AS209_combined.p3','../AS209_combined.p4'], interp = ['linearPD']*4, calwt = True, applymode = 'calonly')

##########################################################################################################################################
# Fit and remove continuum 

# SB only
os.system('rm -rf AS209_SB_CO_selfcal.ms.contsub')     
uvcontsub(vis='AS209_SB_CO_selfcal.ms',spw='8~11',fitorder=0,fitspw='8:400~900,9:120~350,10:120~350,11:1850~2000',solint='int',excludechans=True)
# Check 
plotms(vis='AS209_SB_CO_selfcal.ms.constub', xaxis='channel', yaxis='amp', averagedata=T,avgtime='1.e8', avgbaseline=True, avgscan=True)

# SB+LB combined
os.system('rm -rf AS209_CO_combined_selfcal.ms.contsub')     
uvcontsub(vis='AS209_CO_combined_selfcal.ms',spw='8~11,18,22',fitorder=0,fitspw='8:400~900,9:120~350,10:120~350,11:1850~2000,18:1850~2000,22:1850~2000',solint='int',excludechans=True)
# Check 
plotms(vis='AS209_CO_combined_selfcal.ms.constub', xaxis='channel', yaxis='amp', averagedata=T,avgtime='1.e8', avgbaseline=True, avgscan=True)

# regrid velocity axis
#mstransform(vis = 'AS209_CO_combined_selfcal.ms.contsub', outputvis = 'AS209_CO_combined_selfcal.ms.contsub.cvel',  keepflags = False,datacolumn = 'data', regridms = True,mode='velocity',start='-4km/s',width='0.35km/s',nchan=60, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')
# this step actualy messes up everything! for some reason it reverts the channels for half of the spectral windows (cdelt is negative instead or positive, or the other around)

##########################################################################################################################################
# clean images

uvtaper = []

start = '-4km/s'
width = '0.35km/s'
nchan = 60
COfreq = '230.53800GHz'

##############

# SB+LB combined
imagename = 'AS209_12CO_combined_test3'
os.system('rm -rf cleaning/'+imagename+'.*')
tclean(vis= 'AS209_CO_combined_selfcal.ms.contsub', 
       imagename = 'cleaning/'+imagename, 
       spw='0~5',
       specmode = 'cube',
       start=start,
       width=width,
       nchan=nchan,
       restfreq=COfreq,
       outframe='LSRK',
       veltype='radio', 
       deconvolver = 'multiscale',
       scales = [0,10,25,75,150,250], 
       gain = 0.1,
       weighting='briggs', 
       robust = 1.0,
       cyclefactor = 5, 
       niter = 100000,
       imsize = 1500,
       cell = '0.01arcsec', 
       interactive = True,
       threshold = '3mJy',    
       cycleniter = 100,
       nterms = 1,
       restoringbeam = 'common') 
# rms = 0.77mJy
immoments(axis = "spec",imagename='cleaning/AS209_12CO_combined_test3.image',moments=[0],outfile ='cleaning/AS209_12CO_combined_test3.mom0',chans='3~52')
immoments(axis = "spec",imagename='cleaning/AS209_12CO_combined_test3.image',moments=[0],outfile ='cleaning/AS209_12CO_combined_test3.mom0.clipped',chans='3~52', includepix = [.002,10]) # clip 3xrms
#immoments(axis = "spec",imagename='cleaning/AS209_12CO_combined_test3.image',moments=[1],outfile ='cleaning/AS209_12CO_combined_test3.mom1',chans='3~52')

exportfits(imagename='cleaning/AS209_12CO_combined_test3.mom0',fitsimage='cleaning/AS209_12CO_combined_test3_mom0.fits')
exportfits(imagename='cleaning/AS209_12CO_combined_test3.mom0.clipped',fitsimage='cleaning/AS209_12CO_combined_test3_mom0_clipped.fits')



