"""
This script is written for CASA 4.5.3
Note that the imaging algorithms were rewritten significantly between CASA 4.5.3 and CASA 4.7.2 

Datasets calibrated: 
2016.1.00484.L/GW_Lup_a_06_TM1  (PI: Andrews)
"""

field = 'MY_Lup'

##################################################################
##################################################################
## short baseline data
##################################################################
##################################################################

SB1 = 'calibrated_final.ms' #replace as appropriate
SB1refant = 'DA49'
tag = 'SB1'

#split out all the data from the given field
SB1_field = field+'_'+tag+'.ms'
print SB1_field #just to double check for yourself that the name is actually ok
os.system('rm -rf ' + SB1_field + '*')
split2(vis=SB1,
       field = field,    
       outputvis=SB1_field,
       datacolumn='data')

"""
This portion covers self-calibration and imaging of the continuum of the short baseline data
"""
# initial inspection of data before splitting out and averaging the continuum

plotms(vis = SB1_field, xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')


# spws 0 and 4 contains the CO 2-1 line, while the other six are continuum SPWs
contspws = '0~7'
flagmanager(vis=SB1_field,mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
flagchannels='0:1850~2000, 4:1850~2000' 

flagdata(vis=SB1_field,mode='manual', spw=flagchannels, flagbackup=False, field = field)

# Average the channels within spws
SB1_initcont = field+'_'+tag+'_initcont.ms'
print SB1_initcont #just to double check for yourself that the name is actually ok
os.system('rm -rf ' + SB1_initcont + '*')
split2(vis=SB1_field,
       field = field,
       spw=contspws,      
       outputvis=SB1_initcont,
       width=[480,8,8,8, 480, 8, 8, 8], # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
       datacolumn='data')


# Restore flagged line channels
flagmanager(vis=SB1_field,mode='restore',
            versionname='before_cont_flags')

# Check that amplitude vs. uvdist looks normal
plotms(vis=SB1_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30', avgscan = True)

# Inspect individual antennae. We do this step here rather than before splitting because plotms will load the averaged continuum much faster 

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '0',
       coloraxis = 'spw', iteraxis = 'antenna')


plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '1',
       coloraxis = 'spw', iteraxis = 'antenna')

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '0', 
       coloraxis = 'spw', iteraxis = 'antenna') 

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '1', 
       coloraxis = 'spw', iteraxis = 'antenna') 

# check individual execution blocks
SB1_EB1_initcontimage_dirty = field+'_'+tag+'_EB1_initcontinuum_dirty'
os.system('rm -rf '+SB1_EB1_initcontimage_dirty+'.*')
clean(vis=SB1_initcont, 
      imagename=SB1_EB1_initcontimage_dirty, 
      observation = '0', 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      robust=0.5,
      imsize=500,
      cell='0.03arcsec', 
      interactive=False, 
      niter = 0)

SB1_EB2_initcontimage_dirty = field+'_'+tag+'_EB2_initcontinuum_dirty'
os.system('rm -rf '+SB1_EB2_initcontimage_dirty+'.*')
clean(vis=SB1_initcont, 
      imagename=SB1_EB2_initcontimage_dirty, 
      observation = '1', 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      robust=0.5,
      imsize=500,
      cell='0.03arcsec', 
      interactive=False, 
      niter = 0)

# Initial clean
SB1_initcontimage = field+'_'+tag+'_initcontinuum'
os.system('rm -rf '+SB1_initcontimage+'.*')
clean(vis=SB1_initcont, 
      imagename=SB1_initcontimage, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 20, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[252pix,253pix],0.9arcsec]',
      interactive=True)

# cleaned for 1 cycle (100 iterations)
# peak: 24.3 mJy/beam
# rms: 68 microJy/beam

# First phase-self-cal
SB1_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB1_p1)
gaincal(vis=SB1_initcont, caltable=SB1_p1, gaintype='T', combine = 'spw', 
        spw=contspws, refant=SB1refant, calmode='p', 
        solint='20s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2017/05/14/00:00:01~2017/05/14/11:59:59')

plotcal(caltable=SB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2017/05/17/00:00:01~2017/05/17/11:59:59')

applycal(vis=SB1_initcont, spw=contspws, spwmap = 8*[0], gaintable=[SB1_p1], calwt=T, flagbackup=F)

SB1_contms_p1 = field+'_'+tag+'_contp1.ms'
os.system('rm -rf '+SB1_contms_p1)
split2(vis=SB1_initcont, outputvis=SB1_contms_p1, datacolumn='corrected')


SB1_contimage_p1 = field+'_'+tag+'_p1continuum'
os.system('rm -rf '+SB1_contimage_p1+'.*')
clean(vis=SB1_contms_p1, 
      imagename=SB1_contimage_p1, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 20, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[252pix,253pix],0.9arcsec]',
      interactive=True)

# cleaned for 2 cycles with 100 iterations each
# peak: 26.2 mJy/beam
# rms: 38.9 microJy/beam

# second round of phase self-cal didn't yield improvement, so we move on to amp self-cal 

SB1_ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+SB1_ap1)
gaincal(vis=SB1_contms_p1, caltable=SB1_ap1, gaintype='T', 
        spw=contspws, refant=SB1refant, calmode='ap', 
        solint='60s', minsnr=2.0, minblperant=4, solnorm = True)

plotcal(caltable=SB1_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = '2017/05/14/00:00:01~2017/05/14/11:59:59')

plotcal(caltable=SB1_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = '2017/05/17/00:00:01~2017/05/17/11:59:59')

applycal(vis=SB1_contms_p1, spw=contspws, gaintable=[SB1_ap1], calwt=T, flagbackup=F)

SB1_contms_ap1 = field+'_'+tag+'_contap1.ms'
os.system('rm -rf '+SB1_contms_ap1)
split2(vis=SB1_contms_p1, outputvis=SB1_contms_ap1, datacolumn='corrected')

SB1_contimage_ap1 = field+'_'+tag+'_ap1continuum'
os.system('rm -rf '+SB1_contimage_ap1+'.*')
clean(vis=SB1_contms_ap1, 
      imagename=SB1_contimage_ap1, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 20, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[252pix,253pix],0.9arcsec]',
      interactive=True)
# cleaned for 2 cycles of 100 iterations each
# peak: 26.2 mJy/beam
# rms: 37.9 microJy/beam

SB1_contimage_uniform = field+'_'+tag+'_uniform'
os.system('rm -rf '+SB1_contimage_uniform+'.*')
clean(vis=SB1_contms_ap1, 
      imagename=SB1_contimage_uniform, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='uniform', 
      multiscale = [0, 10, 20, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      gain = 0.1,
      imsize=500,
      cell='0.02arcsec', 
      mask='circle[[252pix,253pix],0.9arcsec]',
      interactive=True)


### We are now done with self-cal of the continuum of SB1 and rename the final measurement set. 
SB1_contms_final = field+'_'+tag+'_contfinal.ms'
os.system('cp -r '+SB1_contms_ap1+' '+SB1_contms_final)

##############################
# Reduction of CO data in SB1
#############################

applycal(SB1_field, spwmap = [[0]*8, [0,1,2,3,4,5,6,7]], gaintable=[SB1_p1, SB1_ap1], calwt=T, flagbackup=F)

#split out the CO 2-1 spectral window
linespw = '0, 4'
SB1_CO_ms = field+'_'+tag+'_CO21.ms'
os.system('rm -rf ' + SB1_CO_ms + '*')
split2(vis=SB1_field,
       field = field,
       spw=linespw,      
       outputvis=SB1_CO_ms, 
       datacolumn='corrected')

plotms(vis = SB1_CO_ms, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)

SB1_CO_mscontsub = SB1_CO_ms+'.contsub'
os.system('rm -rf '+SB1_CO_mscontsub) 
fitspw = '0:0~1850;2000~3839, 1:0~1850;2000~3839' # channels for fitting continuum
uvcontsub(vis=SB1_CO_ms,
          spw='0~1', 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=1,
          want_cont=False) 

plotms(vis = SB1_CO_mscontsub, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)


CO_cvel = SB1_CO_mscontsub+'.cvel'

os.system('rm -rf '+ CO_cvel)
mstransform(vis = SB1_CO_mscontsub, outputvis = CO_cvel,  keepflags = False,datacolumn = 'data', regridms = True,mode='velocity',start='-5km/s',width='0.35km/s',nchan=60, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

SB1_CO_image = field+'_'+tag+'_CO21cube'
os.system('rm -rf '+SB1_CO_image+'.*')
clean(vis=CO_cvel, 
      imagename=SB1_CO_image,
      mode = 'velocity',
      psfmode = 'clark',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 30, 50],
      robust = 1.0,
      gain = 0.3, 
      imsize = 500,
      cell = '0.03arcsec',
      start='-5km/s',
      width='0.35km/s',
      nchan=60, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '10mJy',
      interactive=True) 

immoments(axis = "spec",imagename=SB1_CO_image+'.image',moments=[0],outfile =SB1_CO_image+'.mom0', chans = '5~56')
immoments(axis = "spec",imagename=SB1_CO_image+'.image',moments=[1],outfile =SB1_CO_image+'.mom1', chans = '5~56', includepix = [.012, 10])

##################################################################
##################################################################
## long baseline data
##################################################################
##################################################################


#rescaling the flux for the 9/23/17 execution because the calibrator catalog was updated after the original pipeline calibration
#Old flux value of J1517-2422 at 232 GHz: 2.457 Jy
#New flux value at 232.583 GHz:  2.17 Jy

LB_vis = '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X7c/group.uid___A001_X8c5_X7d/member.uid___A001_X8c5_X7e/calibrated/calibrated_final.ms' #this is the long-baseline measurement set being calibrated

field = 'MY_Lupi'
LB1_refant = 'DV08, DV24'
tag = 'LB'

"""
Double-check flux calibration
au.getALMAFlux('J1617-5848', frequency = '232.582GHz', date = '2017/09/24')
Closest Band 3 measurement: 1.120 +- 0.070 (age=+7 days) 103.5 GHz
Closest Band 3 measurement: 1.160 +- 0.060 (age=+7 days) 91.5 GHz
Closest Band 7 measurement: 0.360 +- 0.030 (age=+1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -8 days from 2017/09/24, with age separation of 0 days
  2017/10/02: freqs=[91.46, 103.49, 343.48], fluxes=[1.11, 1.03, 0.4]
Median Monte-Carlo result for 232.582000 = 0.542233 +- 0.089967 (scaled MAD = 0.086537)
Result using spectral index of -0.774750 for 232.582 GHz from 1.120 Jy at 103.490 GHz = 0.598075 +- 0.089967 Jy


Reasonably close to pipeline log 

au.getALMAFlux('J1617-5848', frequency = '232.582GHz', date = '2017/11/25')
Closest Band 3 measurement: 1.130 +- 0.030 (age=+2 days) 91.5 GHz
Closest Band 7 measurement: 0.340 +- 0.030 (age=+2 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 2 days from 2017/11/25, with age separation of 0 days
  2017/11/23: freqs=[91.46, 343.48], fluxes=[1.13, 0.34]
Median Monte-Carlo result for 232.582000 = 0.484686 +- 0.070961 (scaled MAD = 0.069537)
Result using spectral index of -0.907650 for 232.582 GHz from 1.130 Jy at 91.460 GHz = 0.484359 +- 0.070961 Jy

Consistent with pipeline log 
"""


"""
For the purposes of checking the flux offsets between the two execution blocks, we're just splitting out the continuum windows to make a small dataset

"""

split2(vis='MY_Lup_SB1_contap1.ms',
       field = field,
       outputvis='SB.ms',
       width=[8, 16, 16, 16, 8, 16, 16, 16], 
       datacolumn='data')
execfile('ExportMS.py')

split2(vis=LB_vis,
       field = field,
       spw='0~2',      
       outputvis='LB0.ms',
       width=128, 
       timebin = '30s',
       datacolumn='data')

execfile('ExportMS.py')


clean(vis='LB0.ms', 
      imagename='initcont0', 
      mode='mfs', 
      multiscale = [0, 25, 50, 75], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.3,
      imsize=1800,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      imagermode = 'csclean')

split2(vis=LB_vis,
       field = field,
       spw='4~6',      
       outputvis='LB1.ms',
       width=128, 
       timebin = '30s',
       datacolumn='data')

clean(vis='LB1.ms', 
      imagename='initcont1', 
      mode='mfs', 
      multiscale = [0, 25, 50, 75], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.3,
      imsize=1800,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      imagermode = 'csclean')

execfile('ExportMS.py')


# the phase center offset 
# (offx, offy) = (-0.072, +0.064)"	[i.e., to the NW]

# Rough estimate of viewing geometry from Gaussian fit:
# i = 73 degrees.  
# PA = 59 degrees.

#need to rescale 11/25/2017 execution block up by 30% in flux 

gencal(vis = LB_vis, caltable = 'scale.gencal', caltype = 'amp', parameter = [0.877])
applycal(vis = LB_vis, gaintable = ['scale.gencal'], calwt = T, flagbackup = F, spw = '4~7')

#now split out the continuum dataset for proper imaging

# spws 3 and 7 contain the CO 2-1 line, while the others are continuum only
contspws = '0~7'

flagmanager(vis=LB_vis,mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
# velocity range selected for flagging based on compact configuration data
flagchannels='3:1870~1970, 7:1870~1970'

flagdata(vis=LB_vis,mode='manual', spw=flagchannels, flagbackup=False, field = field)

# Average the channels within spws
LB1_initcont = field+'_'+tag+'_initcont.ms'
os.system('rm -rf ' + LB1_initcont + '*')
split2(vis=LB_vis,
       field = field,
       spw=contspws,      
       outputvis=LB1_initcont,
       width=[8,8,8,480, 8, 8, 8, 480], # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
       timebin = '6s',
       datacolumn='corrected')

# Restore flagged line channels
flagmanager(vis=LB_vis,mode='restore',
            versionname='before_cont_flags')

plotms(vis=LB1_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30')

#check individual execution blocks
LB1_initcontimage0 = field+'_'+tag+'_initcontinuum_0'
os.system('rm -rf '+LB1_initcontimage0+'.*')
clean(vis=LB1_initcont, 
      observation = '0', 
      imagename=LB1_initcontimage0, 
      mode='mfs', 
      multiscale = [0, 25, 50, 75], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.3,
      imsize=1800,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      imagermode = 'csclean')


#3 cycles of 100 iterations each 

LB1_initcontimage1 = field+'_'+tag+'_initcontinuum_1'
os.system('rm -rf '+LB1_initcontimage1+'.*')
clean(vis=LB1_initcont, 
      observation = '1', 
      imagename=LB1_initcontimage1, 
      mode='mfs', 
      multiscale = [0, 25, 50, 75], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.3,
      imsize=1800,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      imagermode = 'csclean')


#4 cycles of 100 iterations each

#images look aligned

LB1_initcontimage_LBonly = field+'_'+tag+'_initcontinuum_LBonly'
os.system('rm -rf '+LB1_initcontimage_LBonly+'.*')
clean(vis=LB1_initcont, 
      imagename=LB1_initcontimage_LBonly, 
      mode='mfs', 
      multiscale = [0, 25, 50], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.3,
      imsize=1800,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      imagermode = 'csclean')

#6 cycles of 100 iterations each 


concat(vis = [SB1_contms_final, LB1_initcont], concatvis = 'MY_Lup_contcombined.ms', dirtol = '1arcsec', copypointing = False) 

tag = 'combined'
field = 'MY_Lup'

LB1_initcontimage = field+'_'+tag+'_initcontinuum'
os.system('rm -rf '+LB1_initcontimage+'.*')
clean(vis='MY_Lup_contcombined.ms', 
      imagename=LB1_initcontimage, 
      mode='mfs', 
      multiscale = [0, 25, 50], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.1,
      imsize=1800,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask = 'ellipse[[929pix, 924pix], [0.8arcsec,0.4arcsec],60deg]',
      imagermode = 'csclean')

#17 cycles of 100 iterations each
#rms: 15 microJy/beam
#peak: 1.7 mJy/beam


# First round of phase-only self-cal
LB1_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+LB1_p1)
gaincal(vis='MY_Lup_contcombined.ms', caltable=LB1_p1, gaintype='T', combine = 'spw,scan', 
        spw='0~15', refant='DV24, DA49', calmode='p', 
        solint='300s', minsnr=2.0, minblperant=4)

applycal(vis='MY_Lup_contcombined.ms', spw='0~15', spwmap = [0]*16, gaintable=[LB1_p1], calwt=True, applymode = 'calonly', flagbackup=False, interp = 'linearperobs')

LB1_contms_p1 = field+'_'+tag+'_contp1.ms'
os.system('rm -rf '+LB1_contms_p1)
split2(vis='MY_Lup_contcombined.ms', outputvis=LB1_contms_p1, datacolumn='corrected')

LB1_contimagep1 = field+'_'+tag+'_continuump1'
os.system('rm -rf '+LB1_contimagep1+'.*')
clean(vis=LB1_contms_p1, 
      imagename=LB1_contimagep1, 
      mode='mfs', 
      multiscale = [0, 25, 50], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.1,
      imsize=1800,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask = 'ellipse[[929pix, 924pix], [0.8arcsec,0.4arcsec],60deg]',
      imagermode = 'csclean')

#18 cycles of 100 iterations each
#rms: 14 microJy/beam
#peak: 18 mJy/beam

#second round of phase self-cal makes things worse, so we're stopping with one round 

LB1_robust0 = field+'_'+tag+'_robust0'
os.system('rm -rf '+LB1_robust0+'.*')
clean(vis= LB1_contms_p1, 
      imagename=LB1_robust0, 
      field = field, 
      mode='mfs', 
      multiscale = [0, 25, 50], 
      weighting='briggs', 
      robust=0.0,
      gain = 0.1,
      imsize=1800,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask = 'ellipse[[929pix, 924pix], [0.8arcsec,0.4arcsec],60deg]',
      imagermode = 'csclean')

#20 cycles of 100 iterations each 

