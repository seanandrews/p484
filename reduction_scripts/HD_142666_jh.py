"""
This script is written for CASA 4.5.3
Note that the imaging algorithms were rewritten significantly between CASA 4.5.3 and CASA 4.7.2 


Datasets calibrated:
SB1: 2013.1.00498.S/HD_142666_a_06_TE (P.I. Perez)
"""

field = 'HD_142666'

##################################################################
##################################################################
## short baseline data (from Program 2013.1.00498.S, downloaded from archive)
##################################################################
##################################################################

SB1 = 'uid___A002_Xa657ad_X736.ms.split.cal' #replace as appropriate
SB1refant = 'DV09'
tag = 'SB1'

"""
This portion covers self-calibration and imaging of the continuum of the short baseline data
"""
# initial inspection of data before splitting out and averaging the continuum

plotms(vis = SB1, xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')


# spw 
contspws = '0~7'
flagmanager(vis=SB1,mode='save', versionname='before_cont_flags')

# CO 2-1 line in SPW1, 13CO 2-1 in SPW 5, C18O 2-1 in SPW 6
flagchannels='1:100~250, 5:40~100, 6:790~850' 

flagdata(vis=SB1,mode='manual', spw=flagchannels, flagbackup=False, field = field)

# Average the channels within spws
SB1_initcont = field+'_'+tag+'_initcont.ms'
print SB1_initcont #just to double check for yourself that the name is actually ok
os.system('rm -rf ' + SB1_initcont + '*')
split2(vis=SB1,
       field = field,
       spw=contspws,      
       outputvis=SB1_initcont,
       width=[30, 480, 8,15,15,240,240,8], # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
       datacolumn='data')


# Restore flagged line channels
flagmanager(vis=SB1,mode='restore',
            versionname='before_cont_flags')

# Check that amplitude vs. uvdist looks normal
plotms(vis=SB1_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30')

# Inspect individual antennae. We do this step here rather than before splitting because plotms will load the averaged continuum much faster 


plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '16', 
       coloraxis = 'spw', iteraxis = 'antenna')

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', 
       coloraxis = 'spw', iteraxis = 'antenna')

flagdata(vis=SB1_initcont,mode='manual', spw='0,1,3,4,5,6', flagbackup=False, field = field, scan = '16,21', antenna = 'DA41')
flagdata(vis=SB1_initcont,mode='manual', spw='1', flagbackup=False, field = field, scan = '29,34', antenna = 'DA46')
flagdata(vis=SB1_initcont,mode='manual', spw='3', flagbackup=False, field = field, scan = '16,21,29,34', antenna = 'DA46')
flagdata(vis=SB1_initcont,mode='manual', spw='4,6', flagbackup=False, field = field, scan = '16,21', antenna = 'DA46')
flagdata(vis=SB1_initcont,mode='manual', spw='3,6', flagbackup=False, field = field, scan='34', antenna = 'DA59')
flagdata(vis=SB1_initcont,mode='manual', spw='3', flagbackup=False, field = field, scan='16', antenna = 'DA59')
flagdata(vis=SB1_initcont,mode='manual', spw='4', flagbackup=False, field = field, scan='29,34', antenna = 'DV08')
flagdata(vis=SB1_initcont,mode='manual', spw='3', flagbackup=False, field = field, scan='16,21', antenna = 'DV18')
flagdata(vis=SB1_initcont,mode='manual', spw='3', flagbackup=False, field = field, scan='16,21', antenna = 'DV24')

# Create dirty image 
SB1_initcontimage_dirty = field+'_'+tag+'_initcontinuum_dirty'
os.system('rm -rf '+SB1_initcontimage_dirty+'.*')
clean(vis=SB1_initcont, 
      imagename=SB1_initcontimage_dirty, 
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
      multiscale = [0, 5,10], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[250pix,250pix],1arcsec]',
      interactive=True)

# cleaned for 1 cycles (100 iterations)
# peak: 34.6 mJy/beam
# rms: 172 microJy/beam

# First phase-self-cal
SB1_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB1_p1)
gaincal(vis=SB1_initcont, caltable=SB1_p1, gaintype='T', combine = 'spw', 
        spw=contspws, refant=SB1refant, calmode='p', 
        solint='30s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna')

applycal(vis=SB1_initcont, spw=contspws, spwmap = [0]*8, gaintable=[SB1_p1], calwt=T, flagbackup=F)

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
      multiscale = [0, 5,10], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[250pix,250pix],1arcsec]',
      interactive=True)

# cleaned for one cycle (100 iterations)
# peak: 39.3 mJy/beam
# rms: 83 microJy/beam

# amplitude self-cal

SB1_ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+SB1_ap1)
gaincal(vis=SB1_contms_p1, caltable=SB1_ap1, gaintype='T', combine = 'spw', 
        spw=contspws, refant=SB1refant, calmode='ap', 
        solint='60s', minsnr=2.0, minblperant=4, solnorm = True)

plotcal(caltable=SB1_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna')

applycal(vis=SB1_contms_p1, spw=contspws, spwmap = [0]*8, gaintable=[SB1_ap1], calwt=T, flagbackup=F)

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
      multiscale = [0, 5, 10], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[250pix,250pix],1arcsec]',
      interactive=True)

# cleaned for one cycle (100 iterations)
# peak: 39.9 mJy/beam
# rms: 72 microJy/beam

#The DV24 amplitudes look problematic, so we'll flag it

flagdata(vis=SB1_contms_ap1,mode='manual', flagbackup=False, field = field,  scan='16,21', antenna = 'DV24')


### We are now done with self-cal of the continuum of SB1 and rename the final measurement set. 
SB1_contms_final = field+'_'+tag+'_contfinal.ms'
os.system('cp -r '+SB1_contms_ap1+' '+SB1_contms_final)


##############################
# Reduction of CO data in SB1
#############################

#split out the CO 2-1 spectral window
linespw = '1'
SB1_CO_ms = field+'_'+tag+'_CO21.ms'
os.system('rm -rf ' + SB1_CO_ms + '*')
split2(vis=SB1,
       field = field,
       spw=linespw,      
       outputvis=SB1_CO_ms, 
       datacolumn='data')

flagdata(vis=SB1_CO_ms,mode='manual', spw='0', flagbackup=False, field = field, scan = '16,21', antenna = 'DA41')
flagdata(vis=SB1_CO_ms,mode='manual', spw='0', flagbackup=False, field = field, scan = '29,34', antenna = 'DA46')

applycal(vis=SB1_CO_ms, spw='0', gaintable=[SB1_p1, SB1_ap1], calwt=T, flagbackup=F)

SB1_CO_mscontsub = SB1_CO_ms+'.contsub'
os.system('rm -rf '+SB1_CO_mscontsub) 
fitspw = '0:0~100;250~1919' # channels for fitting continuum
uvcontsub(vis=SB1_CO_ms,
          spw='0', 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=1,
          want_cont=False) 

plotms(vis = SB1_CO_mscontsub, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline = True)

SB1_CO_cvel = SB1_CO_mscontsub+'.cvel'

os.system('rm -rf '+ SB1_CO_cvel)
mstransform(vis = SB1_CO_mscontsub, outputvis = SB1_CO_cvel,  keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='-5.0km/s',width='0.35km/s',nchan=60, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

#check individual observation
SB1_CO_image = field+'_'+tag+'_CO21cube'
os.system('rm -rf '+SB1_CO_image+'.*')
clean(vis=SB1_CO_cvel, 
      imagename=SB1_CO_image,
      mode = 'velocity',
      psfmode = 'clark',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 20,30],
      robust = 1.0,
      gain = 0.3, 
      imsize = 500,
      cell = '0.03arcsec',
      start='-5.0km/s',
      width='0.35km/s',
      nchan=60, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '8mJy',
      interactive=True) 

#re-image this with more channels on the low velocity side and with a higher threshold

immoments(axis = "spec",imagename=SB1_CO_image+'.image',moments=[0],outfile =SB1_CO_image+'.mom0', chans = '1~56')
immoments(axis = "spec",imagename=SB1_CO_image+'.image',moments=[1],outfile =SB1_CO_image+'.mom1', chans = '1~56', includepix = [.025, 10])



##################################################################
##################################################################
## long baseline data
##################################################################
##################################################################
LB_vis = '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X90/group.uid___A001_X8c5_X91/member.uid___A001_X8c5_X92/calibrated/calibrated_final.ms' #this is the long-baseline measurement set being calibrated
field = 'HD_142666' 

LB1_refant = 'DA56, DV24'
tag = 'LB'

"""
Double-check flux calibration
au.getALMAFlux('J1517-2422', frequency = '232.582GHz', date = '2017/09/25')
Closest Band 3 measurement: 2.770 +- 0.050 (age=-7 days) 103.5 GHz
Closest Band 3 measurement: 2.790 +- 0.040 (age=-7 days) 91.5 GHz
Closest Band 7 measurement: 1.770 +- 0.040 (age=+2 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -7 days from 2017/09/25, with age separation of 0 days
  2017/10/02: freqs=[103.49, 91.46, 343.48], fluxes=[2.77, 2.79, 1.92]
Median Monte-Carlo result for 232.582000 = 2.169935 +- 0.180699 (scaled MAD = 0.178941)
Result using spectral index of -0.279723 for 232.582 GHz from 2.770 Jy at 103.490 GHz = 2.208551 +- 0.180699 Jy

Reasonably close to pipeline log 

au.getALMAFlux('J1427-4206', frequency = '232.582GHz', date = '2017/11/09')
Closest Band 3 measurement: 3.230 +- 0.060 (age=+2 days) 91.5 GHz
Closest Band 7 measurement: 1.370 +- 0.060 (age=-3 days) 337.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 15 days from 2017/10/17, with age separation of 0 days
  2017/10/02: freqs=[91.46, 103.49, 343.48], fluxes=[3.25, 3.07, 1.49]
Median Monte-Carlo result for 232.582000 = 1.883770 +- 0.163664 (scaled MAD = 0.163917)
Result using spectral index of -0.593201 for 232.582 GHz from 3.230 Jy at 91.460 GHz = 1.856741 +- 0.163664 Jy

This is inconsistent with the pipeline log because these values weren't present in the catalog during the original calibration
"""


##################################################################
##################################################################
## flux alignment
##################################################################
##################################################################

"""
For the purposes of checking the flux offsets between the two execution blocks, we're just splitting out the continuum windows to make a small dataset

"""

split2(vis='HD_142666_SB1_contap1.ms',
       field = field,
       outputvis='SB.ms',
       width=[4,4, 16, 4, 4, 4, 4, 16], 
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

split2(vis=LB_vis,
       field = field,
       spw='4~6',      
       outputvis='LB1.ms',
       width=128, 
       timebin = '30s',
       datacolumn='data')

execfile('ExportMS.py')

# the phase center offset 
# (offx, offy) = (-0.041, +0.024)"	[i.e., to the NW]

# Rough estimate of viewing geometry from Gaussian fit:
# i = 61 degrees.  
# PA = 164 degrees.

"""
The flux of the second LB execution block needs to be increased by 30%. 
This is consistent with the flux discrepancy between the two execution blocks of GW Lup, which also used J1427-4206 as a flux calibrator at around the same time. 
"""

gencal(vis = LB_vis, caltable = 'scale.gencal', caltype = 'amp', parameter = [0.877])
applycal(vis = LB_vis, gaintable = ['scale.gencal'], calwt = T, flagbackup = F, spw = '4~7') #rescale observation for 11/09/17

#check flux recalibration
split2(vis=LB_vis,
       field = field,
       spw='4~6',      
       outputvis='LB1_rescaled.ms',
       width=128, 
       timebin = '30s',
       datacolumn='corrected')

execfile('ExportMS.py')

#flux rescaling looks like it worked appropriately

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


#5 cycles of 100 iterations each 

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


#22 cycles of 100 iterations each

#images look aligned

LB1_initcontimage_LBonly = field+'_'+tag+'_initcontinuum_LBonly'
os.system('rm -rf '+LB1_initcontimage_LBonly+'.*')
clean(vis=LB1_initcont, 
      imagename=LB1_initcontimage_LBonly, 
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

#6 cycles of 100 iterations each 

concat(vis = [SB1_contms_final, LB1_initcont], concatvis = 'HD_142666_contcombined.ms', dirtol = '1arcsec', copypointing = False) 

tag = 'combined'

LB1_initcontimage = field+'_'+tag+'_initcontinuum'
os.system('rm -rf '+LB1_initcontimage+'.*')
clean(vis='HD_142666_contcombined.ms', 
      imagename=LB1_initcontimage, 
      mode='mfs', 
      multiscale = [0, 25, 50, 75], 
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
      mask = 'ellipse[[905pix, 879pix], [0.7arcsec,0.5arcsec],164deg]',
      imagermode = 'csclean')

#20 cycles of 100 iterations each
#rms: 16 microJy/beam
#peak: 1.4 mJy/beam

#delmod(vis=LB1_initcont,field=field,otf=True)

#clearcal(vis=LB1_initcont)

# First round of phase-only self-cal
LB1_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+LB1_p1)
gaincal(vis='HD_142666_contcombined.ms', caltable=LB1_p1, gaintype='T', combine = 'spw,scan', 
        spw='0~15', refant='DA56, DV24, DV09', calmode='p', 
        solint='300s', minsnr=2.0, minblperant=4)

applycal(vis='HD_142666_contcombined.ms', spw='0~15', spwmap = [0]*16, gaintable=[LB1_p1], calwt=True, applymode = 'calonly', flagbackup=False, interp = 'linearperobs')

LB1_contms_p1 = field+'_'+tag+'_contp1.ms'
os.system('rm -rf '+LB1_contms_p1)
split2(vis='HD_142666_contcombined.ms', outputvis=LB1_contms_p1, datacolumn='corrected')

LB1_contimagep1 = field+'_'+tag+'_continuump1'
os.system('rm -rf '+LB1_contimagep1+'.*')
clean(vis=LB1_contms_p1, 
      imagename=LB1_contimagep1, 
      mode='mfs', 
      multiscale = [0, 25, 50, 75], 
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
      mask = 'ellipse[[905pix, 879pix], [0.7arcsec,0.5arcsec],164deg]',
      imagermode = 'csclean')

#22 cycles of 100 iterations each
#rms: 14 microJy/beam
#peak: 4.7 mJy/beam

#second round of phase self-cal makes things worse, so I'm stopping with one round  

LB1_controbust0 = field+'_'+tag+'_robust0'
os.system('rm -rf '+LB1_controbust0'.*')
clean(vis=LB1_contms_p1, 
      imagename=LB1_controbust0, 
      mode='mfs', 
      multiscale = [0, 25, 50, 75], 
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
      mask = 'ellipse[[905pix, 879pix], [0.7arcsec,0.5arcsec],164deg]',
      imagermode = 'csclean')

#20 cycles of 100 iterations each 


