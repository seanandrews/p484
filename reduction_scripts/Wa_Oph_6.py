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
os.system('rm -rf '+SB1_initcontimage+'.*')
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
SB1_CO_ms = '/pool/firebolt1/LPscratch/Wa_Oph_6/'+field+'_'+tag+'_CO21.ms'
os.system('rm -rf ' + SB1_CO_ms + '*')
split2(vis=SB1,
       field = field,
       spw=linespw,      
       outputvis=SB1_CO_ms, 
       datacolumn='data')

applycal(vis=SB1_CO_ms, spw='0', gaintable=[SB1_p1, SB1_p2, SB1_ap1], calwt=T, flagbackup=F)

SB1_CO_mscontsub = SB1_CO_ms+'.contsub'
os.system('rm -rf '+SB1_CO_mscontsub 
fitspw = '0:0~1870;2000~3839' # channels for fitting continuum
uvcontsub(vis=SB1_CO_ms,
          spw=linespw, 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=1,
          want_cont=False) 

plotms(vis = SB1_CO_mscontsub, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8')

SB1_CO_mscontsubsplit = SB1_CO_mscontsub+'.split'
#split out line channels for faster imaging
os.system('rm -rf ' + SB1_CO_mscontsubsplit + '*')
split2(vis=SB1_CO_mscontsub,
       field = field,
       spw='0:1870~2000',      
       outputvis=SB1_CO_mscontsubsplit, 
       datacolumn='data')

plotms(vis = SB1_CO_mscontsubsplit, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8')

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



