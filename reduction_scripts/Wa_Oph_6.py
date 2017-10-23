"""
This script is written for CASA 4.5.3
Note that the imaging algorithms were rewritten significantly between CASA 4.5.3 and CASA 4.7.2 
"""

field = 'Wa_Oph_6'

##################################################################
##################################################################
## short baseline data
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
flagchannels='0:1870~2000' 

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

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', 
       coloraxis = 'spw', iteraxis = 'antenna')
# As noted in the README, SPW 1 does not seem as well-behaved as the other SPWs. We'll see how self-cal does. 

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
      mask='circle[[258pix,238pix],1.25arcsec]',
      interactive=True)

# cleaned for 1 cycle (100 iterations)
# peak: 39.3 mJy/beam
# rms: 0.15 mJy/beam

# First phase-self-cal
SB1_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB1_p1)
gaincal(vis=SB1_initcont, caltable=SB1_p1, gaintype='T',  
        spw=contspws, refant=SB1refant, calmode='p', 
        solint='int', minsnr=2.0, minblperant=4)

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
      mask='circle[[258pix,238pix],1.25arcsec]',
      interactive=True)

# cleaned for two cycles of 100 iterations each
# peak: 41.1 mJy/beam
# rms: 50 microJy/beam

# Second phase self-cal 

SB1_p2 = field+'_'+tag+'.p2'
os.system('rm -rf '+SB1_p2)
gaincal(vis=SB1_contms_p1, caltable=SB1_p2, gaintype='T',  
        spw=contspws, refant=SB1refant, calmode='p', 
        solint='int', minsnr=2.0, minblperant=4)

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
      mask='circle[[258pix,238pix],1.25arcsec]',
      interactive=True)

# cleaned for two cycles of 100 iterations each
# peak: 41.1 mJy/beam
# rms: 46 microJy/beam

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
      mask='circle[[258pix,238pix],1.25arcsec]',
      interactive=True)

# cleaned for two cycles of 100 iterations each
# peak: 41.1 mJy/beam
# rms: 43 microJy/beam

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
fitspw = '0:0~1870;2000~3839' # channels for fitting continuum
uvcontsub(vis=SB1_CO_ms,
          spw=linespw, 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=1,
          want_cont=False) 

plotms(vis = SB1_CO_mscontsub, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline = True)

SB1_CO_mscontsubsplit = SB1_CO_mscontsub+'.split'
#split out line channels for faster imaging
os.system('rm -rf ' + SB1_CO_mscontsubsplit + '*')
split2(vis=SB1_CO_mscontsub,
       field = field,
       spw='0:1870~2000',      
       outputvis=SB1_CO_mscontsubsplit, 
       datacolumn='data')

plotms(vis = SB1_CO_mscontsubsplit, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline = True)

SB1_CO_image = field+'_'+tag+'_CO21cube'
os.system('rm -rf '+SB1_CO_image+'.*')
clean(vis=SB1_CO_mscontsubsplit, 
      imagename=SB1_CO_image,
      mode = 'velocity',
      psfmode = 'clark',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 30, 50, 100],
      robust = 1.0,
      gain = 0.3, 
      imsize = 500,
      cell = '0.03arcsec',
      start='-5.2km/s',
      width='0.635km/s',
      nchan=30, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '10mJy',
      interactive=True) 

##################################################################
##################################################################
## long baseline data
##################################################################
##################################################################
LB_vis = '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X68/group.uid___A001_X8c5_X69/member.uid___A001_X8c5_X6a/calibrated/calibrated_final.ms' #this is the long-baseline measurement set being calibrated

LB1_refant = 'DV09'
tag = 'EB'

# spws 3 and 7 contain the CO 2-1 line, while the others are continuum only
contspws = '0~7'

flagmanager(vis=LB_vis,mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
# velocity range selected for flagging based on compact configuration data
flagchannels='3:1880~1950, 7:1880~1950'

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
       datacolumn='data')

# Restore flagged line channels
flagmanager(vis=LB_vis,mode='restore',
            versionname='before_cont_flags')

plotms(vis=LB1_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30')

#check individual execution blocks
LB1_initcontimage0 = field+'_'+tag+'_initcontinuum_0'
os.system('rm -rf '+LB1_initcontimage0+'.*')
tclean(vis=LB1_initcont, 
      imagename=LB1_initcontimage0, 
      specmode='mfs', 
      deconvolver = 'multiscale',
      scales = [0, 20, 40, 80], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.3,
      imsize=2000,
      cell='0.005arcsec', 
      niter = 50000,
      observation = '0', 
      interactive = True, 
      nterms = 1)

#4 cycles of 100 iterations each

LB1_initcontimage1 = field+'_'+tag+'_initcontinuum_1'
os.system('rm -rf '+LB1_initcontimage1+'.*')
tclean(vis=LB1_initcont, 
      imagename=LB1_initcontimage1, 
      specmode='mfs', 
      deconvolver = 'multiscale',
      scales = [0, 20, 40, 80], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.3,
      imsize=2000,
      cell='0.005arcsec', 
      niter = 50000,
      observation = '1', 
      interactive = True, 
      nterms = 1)

#5 cycles of 100 iterations each

LB1_initcontimage_noSB = field+'_'+tag+'_initcontinuum_noSB'
os.system('rm -rf '+LB1_initcontimage_noSB+'.*')
tclean(vis=LB1_initcont, 
      imagename=LB1_initcontimage_noSB, 
      specmode='mfs', 
      deconvolver = 'multiscale',
      scales = [0, 20, 40, 80, 160], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.3,
      imsize=1500,
      cell='0.005arcsec', 
      niter = 50000,
      interactive = True, 
      nterms = 1)

#4 cycles of 100 iterations each

#long baseline and short baseline images look properly aligned

LB1_initcontimage = field+'_'+tag+'_initcontinuum'
os.system('rm -rf '+LB1_initcontimage+'.*')
clean(vis=[SB1_contms_final, LB1_initcont], 
      imagename=LB1_initcontimage, 
      mode='mfs', 
      multiscale = [0, 20, 40, 80, 160], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.1,
      imsize=2000,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask = 'circle[[1080pix, 890pix], 1arcsec]',
      imagermode = 'csclean')

#12 cycles of 100 iterations each
#rms: 25 microJy/beam
#peak: 4.7 mJy/beam

#delmod(vis=LB1_initcont,field=field,otf=True)

#clearcal(vis=LB1_initcont)

# First round of phase-only self-cal
LB1_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+LB1_p1)
gaincal(vis=LB1_initcont, caltable=LB1_p1, gaintype='T', combine = 'spw,scan', 
        spw=contspws, refant=LB1_refant, calmode='p', 
        solint='150s', minsnr=2.0, minblperant=4)

applycal(vis=LB1_initcont, spw=contspws, spwmap = [0]*8, gaintable=[LB1_p1], calwt=True, applymode = 'calonly', flagbackup=False)

LB1_contms_p1 = field+'_'+tag+'_contp1.ms'
os.system('rm -rf '+LB1_contms_p1)
split2(vis=LB1_initcont, outputvis=LB1_contms_p1, datacolumn='corrected')


LB1_contimagep1 = field+'_'+tag+'_continuump1'
os.system('rm -rf '+LB1_contimagep1+'.*')
clean(vis=[SB1_contms_final, LB1_contms_p1], 
      imagename=LB1_contimagep1, 
      mode='mfs', 
      multiscale = [0, 20, 40, 80, 160], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.1,
      imsize=2000,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask = 'circle[[1080pix, 890pix], 1arcsec]',
      imagermode = 'csclean')


#20 cycles of 100 iterations each
# rms: 15.4 microJy/beam
# peak: 6.6 mJy/beam


# Second round of phase-only self-cal
LB1_p2 = field+'_'+tag+'.p2'
os.system('rm -rf '+LB1_p2)
gaincal(vis=LB1_contms_p1, caltable=LB1_p2, gaintype='T', combine = 'spw,scan', 
        spw=contspws, refant=LB1_refant, calmode='p', 
        solint='90s', minsnr=2.0, minblperant=4)

applycal(vis=LB1_contms_p1, spw=contspws, spwmap = [0]*8, gaintable=[LB1_p2], calwt=True, applymode = 'calonly', flagbackup=False, interp='linearperobs')

LB1_contms_p2 = field+'_'+tag+'_contp2.ms'
os.system('rm -rf '+LB1_contms_p2)
split2(vis=LB1_contms_p1, outputvis=LB1_contms_p2, datacolumn='corrected')


LB1_contimagep2 = field+'_'+tag+'_continuump2'
os.system('rm -rf '+LB1_contimagep2+'.*')
clean(vis=[SB1_contms_final, LB1_contms_p2], 
      imagename=LB1_contimagep2, 
      mode='mfs', 
      multiscale = [0, 20, 40, 80, 160], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.1,
      imsize=2000,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask = 'circle[[1080pix, 890pix], 1arcsec]',
      imagermode = 'csclean')

#23 cycles of 100 iterations each
# rms: 14.6 microJy/beam
# peak: 6.9 mJy/beam

# Third round of phase-only self-cal
LB1_p3 = field+'_'+tag+'.p3'
os.system('rm -rf '+LB1_p3)
gaincal(vis=LB1_contms_p2, caltable=LB1_p3, gaintype='T', combine = 'spw', 
        spw=contspws, refant=LB1_refant, calmode='p', 
        solint='60s', minsnr=2.0, minblperant=4)

applycal(vis=LB1_contms_p2, spw=contspws, spwmap = [0]*8, gaintable=[LB1_p3], calwt=True, applymode = 'calonly', flagbackup=False, interp='linearperobs')

LB1_contms_p3 = field+'_'+tag+'_contp3.ms'
os.system('rm -rf '+LB1_contms_p3)
split2(vis=LB1_contms_p2, outputvis=LB1_contms_p3, datacolumn='corrected')

LB1_contimagep3 = field+'_'+tag+'_continuump3'
os.system('rm -rf '+LB1_contimagep3+'.*')
clean(vis=[SB1_contms_final, LB1_contms_p3], 
      imagename=LB1_contimagep3, 
      mode='mfs', 
      multiscale = [0, 20, 40, 80, 160], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.1,
      imsize=2000,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask = 'circle[[1080pix, 890pix], 1arcsec]',
      imagermode = 'csclean')

#24 cycles of 100 iterations each
# rms: 14.2 microJy/beam
# peak: 7.0 mJy/beam

LB1_contimage_robust0 = field+'_'+tag+'_continuum_robust0'
os.system('rm -rf '+LB1_contimage_robust0+'.*')
clean(vis=[SB1_contms_final, LB1_contms_p3], 
      imagename=LB1_contimage_robust0, 
      mode='mfs', 
      multiscale = [0, 20, 40, 80, 160], 
      weighting='briggs', 
      robust=0.0,
      gain = 0.1,
      imsize=2000,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask = 'circle[[1080pix, 890pix], 1arcsec]',
      imagermode = 'csclean')

##22 cycles of 100 iterations each

