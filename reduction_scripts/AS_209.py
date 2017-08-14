"""
This script is written for CASA 4.5.3
Note that the imaging algorithms were rewritten significantly between CASA 4.5.3 and CASA 4.7.2 


Datasets calibrated: 
SB1: 2016.1.00484.L/AS_209_b_06_TM1 (PI: Andrews)
SB2: 2013.1.00226.S/as_209_a_06_TE (PI: Oberg)
SB3: 2013.1.00226.S/as_209_b_06_TE (PI: Oberg)
"""

field = 'AS_209'

##################################################################
##################################################################
## 2016.1.00484.L/AS_209_b_06_TM1 (as delivered to P.I.)
##################################################################
##################################################################

SB1 = 'calibrated_final.ms' #replace as appropriate
SB1refant = 'DA49'
tag = 'SB1'

"""
This portion covers self-calibration and imaging of the continuum of the short baseline data
"""
# initial inspection of data before splitting out and averaging the continuum

plotms(vis = SB1, xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')


# spw 0 contains the CO 2-1 line, while the other three are continuum SPWs
contspws = '0~3'
flagmanager(vis=SB1,mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
flagchannels='0:1890~1960' 

flagdata(vis=SB1,mode='manual', spw=flagchannels, flagbackup=False, field = field)

# Average the channels within spws
SB1_initcont = field+'_'+tag+'_initcont.ms'
print SB1_initcont #just to double check for yourself that the name is actually ok
os.system('rm -rf ' + SB1_initcont + '*')
split2(vis=SB1,
       field = field,
       spw=contspws,      
       outputvis=SB1_initcont,
       width=[480,8,8,8], # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
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

flagdata(vis=SB1_initcont,mode='manual', spw='2', flagbackup=False, field = field, scan = '29', antenna = 'DV15')

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', 
       coloraxis = 'spw', iteraxis = 'antenna')
# As noted in the README from NAASC, SPW 1 does not seem as well-behaved as the other SPWs. We'll see how self-cal does. 

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
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[250pix,250pix],1.4arcsec]',
      interactive=True)

# cleaned for 3 cycles (100 iterations each)
# peak: 27.5 mJy/beam
# rms: 0.15 mJy/beam

# First phase-self-cal
SB1_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB1_p1)
gaincal(vis=SB1_initcont, caltable=SB1_p1, gaintype='T',  
        spw=contspws, refant=SB1refant, calmode='p', 
        solint='30s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna')

applycal(vis=SB1_initcont, spw=contspws, gaintable=[SB1_p1], calwt=T, flagbackup=F)

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
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[250pix,250pix],1.4arcsec]',
      interactive=True)

# cleaned for 6 cycles of 100 iterations each
# peak: 28.2 mJy/beam
# rms: 52 microJy/beam

# Second phase self-cal 

SB1_p2 = field+'_'+tag+'.p2'
os.system('rm -rf '+SB1_p2)
gaincal(vis=SB1_contms_p1, caltable=SB1_p2, gaintype='T',  
        spw=contspws, refant=SB1refant, calmode='p', 
        solint='15s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB1_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna')

applycal(vis=SB1_contms_p1, spw=contspws, gaintable=[SB1_p2], calwt=T, flagbackup=F)

SB1_contms_p2 = field+'_'+tag+'_contp2.ms'
os.system('rm -rf '+SB1_contms_p2)
split2(vis=SB1_contms_p1, outputvis=SB1_contms_p2, datacolumn='corrected')

SB1_contimage_p2 = field+'_'+tag+'_p2continuum'
os.system('rm -rf '+SB1_contimage_p2+'.*')
clean(vis=SB1_contms_p2, 
      imagename=SB1_contimage_p2, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[250pix,250pix],1.4arcsec]',
      interactive=True)

# cleaned for 7 cycles of 100 iterations each
# peak: 28.3 mJy/beam
# rms: 49 microJy/beam


# improvement in rms is small, so we move on to amplitude self-cal

SB1_ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+SB1_ap1)
gaincal(vis=SB1_contms_p2, caltable=SB1_ap1, gaintype='T',  
        spw=contspws, refant=SB1refant, calmode='ap', 
        solint='60s', minsnr=2.0, minblperant=4, solnorm = True)

plotcal(caltable=SB1_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna')

applycal(vis=SB1_contms_p2, spw=contspws, gaintable=[SB1_ap1], calwt=T, flagbackup=F)

SB1_contms_ap1 = field+'_'+tag+'_contap1.ms'
os.system('rm -rf '+SB1_contms_ap1)
split2(vis=SB1_contms_p2, outputvis=SB1_contms_ap1, datacolumn='corrected')

SB1_contimage_ap1 = field+'_'+tag+'_ap1continuum'
os.system('rm -rf '+SB1_contimage_ap1+'.*')
clean(vis=SB1_contms_ap1, 
      imagename=SB1_contimage_ap1, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[250pix,250pix],1.4arcsec]',
      interactive=True)

# cleaned for 7 cycles of 100 iterations each
# peak: 28.2 mJy/beam
# rms: 47 microJy/beam

### We are now done with self-cal of the continuum of SB1 and rename the final measurement set. 
SB1_contms_final = field+'_'+tag+'_contfinal.ms'
os.system('cp -r '+SB1_contms_ap1+' '+SB1_contms_final)

##############################
# Reduction of CO data in SB1
#############################

#split out the CO 2-1 spectral window
linespw = '0'
SB1_CO_ms = field+'_'+tag+'_CO21.ms'
os.system('rm -rf ' + SB1_CO_ms + '*')
split2(vis=SB1,
       field = field,
       spw=linespw,      
       outputvis=SB1_CO_ms, 
       datacolumn='data')

applycal(vis=SB1_CO_ms, spw='0', gaintable=[SB1_p1, SB1_p2, SB1_ap1], calwt=T, flagbackup=F)

SB1_CO_mscontsub = SB1_CO_ms+'.contsub'
os.system('rm -rf '+SB1_CO_mscontsub) 
fitspw = '0:0~1890;1950~3839' # channels for fitting continuum
uvcontsub(vis=SB1_CO_ms,
          spw=linespw, 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=1,
          want_cont=False) 

plotms(vis = SB1_CO_mscontsub, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)

CO_cvel = SB1_CO_mscontsub+'.cvel'

os.system('rm -rf '+ CO_cvel)
mstransform(vis = SB1_CO_mscontsub, outputvis = CO_cvel,  keepflags = False,datacolumn = 'data', regridms = True,mode='velocity',start='-4km/s',width='0.35km/s',nchan=60, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

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
      start='-4.0km/s',
      width='0.35km/s',
      nchan=60, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '10mJy',
      interactive=True) 

##################################################################
##################################################################
## 2013.1.00226.S/as_209_a_06_TE (P.I. Oberg) [downloaded from archive, see Huang et al. 2017]
##################################################################
##################################################################

field = 'as_209'
SB2 = 'uid___A002_X85c183_Xf7d.ms.split.cal' #replace as appropriate
SB2refant = 'DA48'
tag = 'SB2'

# initial inspection of data before splitting out and averaging the continuum

plotms(vis = SB2, xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')

"""
Note that this was a bandwidth switching project, so the calibrators were observed on 4 TDM windows that the target was not observed on.
"""

contspws = '14~16' #three of the USB windows. Skipping windows 12 and 13 because the noise is high and bandwidth is narrow 
# Flag the CO 2-1 line
flagchannels = '15:500~800'
flagmanager(vis=SB2, mode='save', versionname='before_cont_flags')

flagdata(vis=SB2,mode='manual', spw=flagchannels, flagbackup=False, field = field)

# Average the channels within spws
SB2_initcont = '/pool/firebolt1/LPscratch/AS_209/'+field+'_'+tag+'_initcont.ms'
print SB2_initcont #just to double check for yourself that the name is actually ok
os.system('rm -rf ' + SB2_initcont + '*')
split2(vis=SB2,
       field = field,
       spw=contspws,      
       outputvis=SB2_initcont,
       width=960, # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
       datacolumn='data')


flagmanager(vis=SB2,mode='restore', versionname='before_cont_flags')

# Check that amplitude vs. uvdist looks normal
plotms(vis=SB2_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30')

# Inspect individual antennae. We do this step here rather than before splitting because plotms will load the averaged continuum much faster 

plotms(vis = SB2_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '4', 
       coloraxis = 'spw', iteraxis = 'antenna')

plotms(vis = SB2_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '4', 
       coloraxis = 'spw', iteraxis = 'antenna')

# Create dirty image 
SB2_initcontimage_dirty = field+'_'+tag+'_initcontinuum_dirty'
os.system('rm -rf '+SB2_initcontimage_dirty+'.*')
clean(vis=SB2_initcont, 
      imagename=SB2_initcontimage_dirty, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      robust=0.5,
      imsize=500,
      cell='0.05arcsec', 
      interactive=False, 
      niter = 0)

#we use the model from SB1 to start self-calibration
ft(vis = SB2_initcont, model = 'AS_209_SB1_ap1continuum.model') 

# First phase-self-cal
SB2_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB2_p1)
gaincal(vis=SB2_initcont, caltable=SB2_p1, gaintype='T', combine = 'spw', 
        spw='0~2', refant=SB2refant, calmode='p', 
        solint='60s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB2_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna')

applycal(vis=SB2_initcont, spw='0~2', spwmap = 3*[0], gaintable=[SB2_p1], calwt=T, flagbackup=F)

SB2_contms_p1 = field+'_'+tag+'_contp1.ms'
os.system('rm -rf '+SB2_contms_p1)
split2(vis=SB2_initcont, outputvis=SB2_contms_p1, datacolumn='corrected')


SB2_contimage_p1 = field+'_'+tag+'_p1continuum'
os.system('rm -rf '+SB2_contimage_p1+'.*')
clean(vis=SB2_contms_p1, 
      imagename=SB2_contimage_p1, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='circle[[250pix,250pix],1.75arcsec]',
      interactive=True)

# cleaned for 2 cycles of 100 iterations each
# peak: 67.5 mJy/beam
# rms: 0.28 mJy/beam

SB2_p2 = field+'_'+tag+'.p2'
os.system('rm -rf '+SB2_p2)
gaincal(vis=SB2_contms_p1, caltable=SB2_p2, gaintype='T', combine = 'spw',
        spw='0~2', refant=SB2refant, calmode='p', 
        solint='45s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB2_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna')

applycal(vis=SB2_contms_p1, spw='0~2', spwmap = 3*[0], gaintable=[SB2_p2], calwt=T, flagbackup=F)

SB2_contms_p2 = field+'_'+tag+'_contp2.ms'
os.system('rm -rf '+SB2_contms_p2)
split2(vis=SB2_contms_p1, outputvis=SB2_contms_p2, datacolumn='corrected')


SB2_contimage_p2 = field+'_'+tag+'_p2continuum'
os.system('rm -rf '+SB2_contimage_p2+'.*')
clean(vis=SB2_contms_p2, 
      imagename=SB2_contimage_p2, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='circle[[250pix,250pix],1.75arcsec]',
      interactive=True)

# cleaned for 2 cycles of 100 iterations each
# peak: 71 mJy/beam
# rms: 0.28 mJy/beam

# Amp self-cal

SB2_ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+SB2_ap1)
gaincal(vis=SB2_contms_p2, caltable=SB2_ap1, gaintype='T', combine = 'spw',   
        spw='0~2', refant=SB2refant, calmode='ap', 
        solint='inf', minsnr=2.0, minblperant=4, solnorm = True)

plotcal(caltable=SB2_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna')

applycal(vis=SB2_contms_p2, spw='0~2', spwmap = 3*[0], gaintable=[SB2_ap1], calwt=T, flagbackup=F)

SB2_contms_ap1 = field+'_'+tag+'_contap1.ms'
os.system('rm -rf '+SB2_contms_ap1)
split2(vis=SB2_contms_p1, outputvis=SB2_contms_ap1, datacolumn='corrected')

SB2_contimage_ap1 = field+'_'+tag+'_ap1continuum'
os.system('rm -rf '+SB2_contimage_ap1+'.*')
clean(vis=SB2_contms_ap1, 
      imagename=SB2_contimage_ap1, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='circle[[250pix,250pix],1.75arcsec]',
      interactive=True)

# cleaned for 2 cycles of 100 iterations each
# peak: 71 mJy/beam
# rms: 0.28 mJy/beam


### We are now done with self-cal of the continuum of SB2 and rename the final measurement set. 
SB2_contms_final = 'AS_209_'+tag+'_contfinal.ms'
os.system('cp -r '+SB2_contms_ap1+' '+SB2_contms_final)

##############################
# Reduction of CO data in SB2
#############################

#split out the CO 2-1 spectral window
linespw = '15'
SB2_CO_ms = field+'_'+tag+'_CO21.ms'
os.system('rm -rf ' + SB2_CO_ms + '*')
split2(vis=SB2,
       field = field,
       spw=linespw,      
       outputvis=SB2_CO_ms, 
       datacolumn='data')

applycal(vis=SB2_CO_ms, spw='0', gaintable=[SB2_p1, SB2_p2, SB2_ap1], calwt=T, flagbackup=F)

plotms(vis = SB2_CO_ms, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)


SB2_CO_mscontsub = SB2_CO_ms+'.contsub'
os.system('rm -rf '+SB2_CO_mscontsub) 
fitspw = '0:0~500;800~959' # channels for fitting continuum
uvcontsub(vis=SB2_CO_ms,
          spw='0', 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=1,
          want_cont=False) 

plotms(vis = SB2_CO_mscontsub, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)

# check individual observation


SB2_CO_cvel = SB2_CO_mscontsub+'.cvel'

os.system('rm -rf '+ SB2_CO_cvel)
mstransform(vis = SB2_CO_mscontsub, outputvis = SB2_CO_cvel,  keepflags = False,datacolumn = 'data', regridms = True,mode='velocity',start='-4km/s',width='0.35km/s',nchan=60, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

SB2_CO_image = field+'_'+tag+'_CO21cube'
os.system('rm -rf '+SB2_CO_image+'.*')
clean(vis=SB2_CO_cvel, 
      imagename=SB2_CO_image,
      mode = 'velocity',
      psfmode = 'clark',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 30, 50],
      robust = 1.0,
      gain = 0.3, 
      imsize = 500,
      cell = '0.05arcsec',
      start='-4.0km/s',
      width='0.35km/s',
      nchan=60, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '10mJy',
      interactive=True) 

##################################################################
##################################################################
## 2013.1.00226.S/as_209_b_06_TE (P.I. Oberg) [downloaded from archive; see Huang et al. 2017 for details]
##################################################################
##################################################################

field = 'as_209'
SB3 = 'uid___A002_X86e521_Xb25.ms.split.cal' #replace as appropriate
SB3refant = 'DA48'
tag = 'SB3'

# initial inspection of data before splitting out and averaging the continuum

plotms(vis = SB3, xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')

contspws = '12~17' #all lower sideband windows


# Average the channels within spws
SB3_initcont = field+'_'+tag+'_initcont.ms'
print SB3_initcont #just to double check for yourself that the name is actually ok
os.system('rm -rf ' + SB3_initcont + '*')
split2(vis=SB3,
       field = field,
       spw=contspws,      
       outputvis=SB3_initcont,
       width=[1920, 1920, 960,960,960,960], # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
       datacolumn='data')

# Check that amplitude vs. uvdist looks normal
plotms(vis=SB3_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30')


# Inspect individual antennae. We do this step here rather than before splitting because plotms will load the averaged continuum much faster 

plotms(vis = SB3_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',
       coloraxis = 'spw', iteraxis = 'antenna')

plotms(vis = SB3_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',
       coloraxis = 'spw', iteraxis = 'antenna')

# Create dirty image 
SB3_initcontimage_dirty = field+'_'+tag+'_initcontinuum_dirty'
os.system('rm -rf '+SB3_initcontimage_dirty+'.*')
clean(vis=SB3_initcont, 
      imagename=SB3_initcontimage_dirty, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      robust=0.5,
      imsize=500,
      cell='0.05arcsec', 
      interactive=False, 
      niter = 0)

# Initial clean

#we use the model from SB1 to start self-calibration
ft(vis = SB3_initcont, model = 'AS_209_SB1_ap1continuum.model') 

#First phase-self-cal
SB3_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB3_p1)
gaincal(vis=SB3_initcont, caltable=SB3_p1, gaintype='T', combine = 'spw', 
        spw='0~5', refant=SB3refant, calmode='p', 
        solint='30s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB3_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna')

applycal(vis=SB3_initcont, spw='0~5', spwmap = 6*[0], gaintable=[SB3_p1], calwt=T, flagbackup=F)

SB3_contms_p1 = field+'_'+tag+'_contp1.ms'
os.system('rm -rf '+SB3_contms_p1)
split2(vis=SB3_initcont, outputvis=SB3_contms_p1, datacolumn='corrected')


SB3_contimage_p1 = field+'_'+tag+'_p1continuum'
os.system('rm -rf '+SB3_contimage_p1+'.*')
clean(vis=SB3_contms_p1, 
      imagename=SB3_contimage_p1, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='circle[[250pix,250pix],1.75arcsec]',
      interactive=True)

# cleaned for 2 cycles of 100 iterations each
# peak: 77 mJy/beam
# rms: 0.18 mJy/beam

SB3_p2 = field+'_'+tag+'.p2'
os.system('rm -rf '+SB3_p2)
gaincal(vis=SB3_contms_p1, caltable=SB3_p2, gaintype='T', combine = 'spw',
        spw='0~5', refant=SB3refant, calmode='p', 
        solint='15s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB3_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna')

applycal(vis=SB3_contms_p1, spw='0~5', spwmap = 6*[0], gaintable=[SB3_p2], calwt=T, flagbackup=F)

SB3_contms_p2 = field+'_'+tag+'_contp2.ms'
os.system('rm -rf '+SB3_contms_p2)
split2(vis=SB3_contms_p1, outputvis=SB3_contms_p2, datacolumn='corrected')


SB3_contimage_p2 = field+'_'+tag+'_p2continuum'
os.system('rm -rf '+SB3_contimage_p2+'.*')
clean(vis=SB3_contms_p2, 
      imagename=SB3_contimage_p2, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='circle[[250pix,250pix],1.75arcsec]',
      interactive=True)

# cleaned for 2 cycles of 100 iterations each
# peak: 77 mJy/beam
# rms: 0.17 mJy/beam

# Amp self-cal

SB3_ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+SB3_ap1)
gaincal(vis=SB3_contms_p2, caltable=SB3_ap1, gaintype='T', combine = 'spw',   
        spw='0~5', refant=SB3refant, calmode='ap', 
        solint='60s', minsnr=2.0, minblperant=4, solnorm = True)

plotcal(caltable=SB3_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna')

applycal(vis=SB3_contms_p2, spw='0~5', spwmap = 6*[0], gaintable=[SB3_ap1], calwt=T, flagbackup=F)

SB3_contms_ap1 = field+'_'+tag+'_contap1.ms'
os.system('rm -rf '+SB3_contms_ap1)
split2(vis=SB3_contms_p1, outputvis=SB3_contms_ap1, datacolumn='corrected')

SB3_contimage_ap1 = field+'_'+tag+'_ap1continuum'
os.system('rm -rf '+SB3_contimage_ap1+'.*')
clean(vis=SB3_contms_ap1, 
      imagename=SB3_contimage_ap1, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='circle[[250pix,250pix],1.75arcsec]',
      interactive=True)

# cleaned for 2 cycles of 100 iterations each
# peak: 77 mJy/beam
# rms: 0.17 mJy/beam

### We are now done with self-cal of the continuum of SB3 and rename the final measurement set. 
SB3_contms_final = 'AS_209_'+tag+'_contfinal.ms'
os.system('cp -r '+SB3_contms_ap1+' '+SB3_contms_final)

############################
##############################
################################

clean(vis=['AS_209_SB1_contap1.ms','as_209_SB2_contap1.ms','as_209_SB3_contap1.ms'], 
      imagename='AS_209_allSB_uniform', 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='uniform', 
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      gain = 0.1,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[250pix,250pix],1.4arcsec]',
      interactive=True)

os.system('rm -rf AS_209_CO_combined.*')
clean(vis=['AS_209_SB1_CO21.ms.contsub.cvel', 'as_209_SB2_CO21.ms.contsub.cvel'], 
      imagename='AS_209_CO_combined',
      mode = 'velocity',
      psfmode = 'clark',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 30, 50],
      robust = 1.0,
      gain = 0.1, 
      imsize = 500,
      cell = '0.03arcsec',
      start='-4.0km/s',
      width='0.35km/s',
      nchan=60, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '7mJy',
      mask = 'AS_209_SB1_CO21cube.mask',
      interactive=True) 

os.system('rm -rf AS_209_CO_combined_2.*')
clean(vis=['AS_209_SB1_CO21.ms.contsub.cvel', 'as_209_SB2_CO21.ms.contsub.cvel'], 
      imagename='AS_209_CO_combined_2',
      mode = 'velocity',
      psfmode = 'clark',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 30, 50],
      robust = 0,
      gain = 0.1, 
      imsize = 500,
      cell = '0.03arcsec',
      start='-4.0km/s',
      width='0.35km/s',
      nchan=60, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '6mJy',
      mask = 'AS_209_SB1_CO21cube.mask',
      interactive=True) 


