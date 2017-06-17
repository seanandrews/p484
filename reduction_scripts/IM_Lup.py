"""
This script is written for CASA 4.5.3
Note that the imaging algorithms were rewritten significantly between CASA 4.5.3 and CASA 4.7.2 

Datasets calibrated:
SB1: 2013.1.00798.S/Im_Lup_a_06_TE (P.I. Pinte)
SB2: 2013.1.00694.S/IM_Lup_a_06_TE (P.I. Cleeves)
SB3: 2013.1.00694.S/IM_Lup_a_06_TC (P.I. Cleeves)
SB4: 2013.1.00226.S/im_lup_a_06_TE (P.I. Oberg)
SB5: 2013.1.00226.S/im_lup_b_06_TE (P.I. Oberg)

Incidentally, there are windows covering 13CS 5-4 in SB1 and SB4
There's nothing obvious in either window, but if you're curious, you could consider combining them
"""

##################################################################
##################################################################
## 2013.1.00798.S/Im_Lup_a_06_TE (downloaded from the archive and calibrated w/ CASA pipeline)
##################################################################
##################################################################
field = 'Im_Lupi'

SB1 = 'uid___A002_Xa2ea64_Xa78.ms.split.cal' #replace as appropriate
SB1refant = 'DA59'
tag = 'SB1'

# initial inspection of data before splitting out and averaging the continuum

plotms(vis = SB1, xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')


# spw 0 shows no obvious line emission, spw 1 contains the CO 2-1 line, spw 2 is a wide continuum window
# Other windows are too low in frequency for combination with the extended data if going by the 10% fractional bandwidth guideline
contspws = '0~2'
flagmanager(vis=SB1,mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
flagchannels='1:850~1100' 

flagdata(vis=SB1,mode='manual', spw=flagchannels, flagbackup=False, field = field)

# Average the channels within spws
SB1_initcont = '/pool/firebolt1/LPscratch/IM_Lup/'+field+'_'+tag+'_initcont.ms'
print SB1_initcont #just to double check for yourself that the name is actually ok
os.system('rm -rf ' + SB1_initcont + '*')
split2(vis=SB1,
       field = field,
       spw=contspws,      
       outputvis=SB1_initcont,
       width=[1920, 1920, 8], # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
       datacolumn='data')


# Restore flagged line channels
flagmanager(vis=SB1,mode='restore',
            versionname='before_cont_flags')

# Check that amplitude vs. uvdist looks normal
plotms(vis=SB1_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30')

# Inspect individual antennae. We do this step here rather than before splitting because plotms will load the averaged continuum much faster 

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '8', 
       coloraxis = 'spw', iteraxis = 'antenna')

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '8', 
       coloraxis = 'spw', iteraxis = 'antenna')

flagdata(vis=SB1_initcont,mode='manual', spw='0~1', flagbackup=False, field = field, timerange = '2015/06/10/00:18:30~2015/06/10/00:22:40', antenna = 'DA59')

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
      cell='0.05arcsec', 
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
      cell='0.05arcsec', 
      mask='ellipse[[236pix,249pix],[3arcsec,2arcsec],145deg]',
      interactive=True)

# cleaned for 1 cycles (100 iterations)
# peak: 58.7 mJy/beam
# rms: 0.29 mJy/beam

# First phase-self-cal
SB1_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB1_p1)
gaincal(vis=SB1_initcont, caltable=SB1_p1, gaintype='T', combine = 'spw', 
        spw=contspws, refant=SB1refant, calmode='p', 
        solint='15s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna')

applycal(vis=SB1_initcont, spw=contspws, spwmap = [0,0,0], gaintable=[SB1_p1], calwt=T, flagbackup=F)

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
      cell='0.05arcsec', 
      mask='ellipse[[236pix,249pix],[3arcsec,2arcsec],145deg]',
      interactive=True)

# cleaned for 3 cycles of 100 iterations each
# peak: 63.2 mJy/beam
# rms: 73.5 microJy/beam

# second round of phase-cal produced no obvious improvement

SB1_ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+SB1_ap1)
gaincal(vis=SB1_contms_p1, caltable=SB1_ap1, gaintype='T', combine = 'spw',  
        spw=contspws, refant=SB1refant, calmode='ap', 
        solint='60s', minsnr=2.0, minblperant=4, solnorm = True)

plotcal(caltable=SB1_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna')

applycal(vis=SB1_contms_p1, spw=contspws, spwmap = [0,0,0], gaintable=[SB1_ap1], calwt=T, flagbackup=F)

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
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='ellipse[[236pix,249pix],[3arcsec,2arcsec],145deg]',
      interactive=True)

# cleaned for 7 cycles of 100 iterations each
# peak: 63.2 mJy/beam
# rms: 69 microJy/beam

### We are now done with self-cal of the continuum of SB1 and rename the final measurement set. 
SB1_contms_final = 'IM_Lup_'+tag+'_contfinal.ms'
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

applycal(vis=SB1_CO_ms, spw='0', gaintable=[SB1_p1, SB1_ap1], calwt=T, flagbackup=F)

SB1_CO_mscontsub = SB1_CO_ms+'.contsub'
os.system('rm -rf '+SB1_CO_mscontsub) 
fitspw = '0:0~850;1100~1919' # channels for fitting continuum
uvcontsub(vis=SB1_CO_ms,
          spw='0', 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=1,
          want_cont=False) 

plotms(vis = SB1_CO_mscontsub, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)


##################################################################
##################################################################
## 2013.1.00694.S/IM_Lup_a_06_TE (downloaded from the archive and calibrated w/ CASA pipeline)
##################################################################
##################################################################

field = 'IM_Lup'
SB2 = 'uid___A002_Xa055bc_X1360.ms.split.cal' 
SB2refant = 'DA52'
tag = 'SB2'

# initial inspection of data before splitting out and averaging the continuum

plotms(vis = SB2, xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')

contspws = '2~3'
#flagging atmospheric lines at 242.3 and 243.4 GHz
flagchannels = '2:42~45,3:76~87' 
flagmanager(vis=SB2, mode='save', versionname='before_cont_flags')

flagdata(vis=SB2,mode='manual', spw=flagchannels, flagbackup=False, field = field)

# Average the channels within spws
SB2_initcont = field+'_'+tag+'_initcont.ms'
print SB2_initcont #just to double check for yourself that the name is actually ok
os.system('rm -rf ' + SB2_initcont + '*')
split2(vis=SB2,
       field = field,
       spw=contspws,      
       outputvis=SB2_initcont,
       width=[8, 8], # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
       datacolumn='data')


# Restore if desired
# flagmanager(vis=SB2,mode='restore', versionname='before_cont_flags')

# Check that amplitude vs. uvdist looks normal
plotms(vis=SB2_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30')

# Inspect individual antennae. We do this step here rather than before splitting because plotms will load the averaged continuum much faster 

plotms(vis = SB2_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '8', 
       coloraxis = 'spw', iteraxis = 'antenna')

plotms(vis = SB2_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '8', 
       coloraxis = 'spw', iteraxis = 'antenna')

flagdata(vis=SB2_initcont,mode='manual', flagbackup=False, field = field, antenna = 'DV01')

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

# Initial clean
SB2_initcontimage = field+'_'+tag+'_initcontinuum'
os.system('rm -rf '+SB2_initcontimage+'.*')
clean(vis=SB2_initcont, 
      imagename=SB2_initcontimage, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='ellipse[[236pix,249pix],[3arcsec,2arcsec],145deg]',
      interactive=True)

# cleaned for 1 cycles (100 iterations)
# peak: 92.8 mJy/beam
# rms: 0.26 mJy/beam

# First phase-self-cal
SB2_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB2_p1)
gaincal(vis=SB2_initcont, caltable=SB2_p1, gaintype='T', 
        spw='0~1', refant=SB2refant, calmode='p', 
        solint='int', minsnr=2.0, minblperant=4)

plotcal(caltable=SB2_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna')

applycal(vis=SB2_initcont, spw='0~1', gaintable=[SB2_p1], calwt=T, flagbackup=F)

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
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='ellipse[[236pix,249pix],[3arcsec,2arcsec],145deg]',
      interactive=True)

# cleaned for 3 cycles of 100 iterations each
# peak: 94.5 mJy/beam
# rms: 54.8 microJy/beam

# Amp self-cal

SB2_ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+SB2_ap1)
gaincal(vis=SB2_contms_p1, caltable=SB2_ap1, gaintype='T',  
        spw='0~1', refant=SB2refant, calmode='ap', 
        solint='60s', minsnr=2.0, minblperant=4, solnorm = True)

plotcal(caltable=SB2_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna')

applycal(vis=SB2_contms_p1, spw='0~1', gaintable=[SB2_ap1], calwt=T, flagbackup=F)

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
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='ellipse[[236pix,249pix],[3arcsec,2arcsec],145deg]',
      interactive=True)

# cleaned for 3 cycles of 100 iterations each
# peak: 94.5 mJy/beam
# rms: 47.3 microJy/beam


### We are now done with self-cal of the continuum of SB1 and rename the final measurement set. 
SB2_contms_final = 'IM_Lup_'+tag+'_contfinal.ms'
os.system('cp -r '+SB2_contms_ap1+' '+SB2_contms_final)

##################################################################
##################################################################
## 2013.1.00694.S/IM_Lup_a_06_TC (downloaded from the archive and calibrated w/ CASA pipeline)
##################################################################
##################################################################

field = 'IM_Lup'
SB3 = 'uid___A002_X9aa6ef_X12b7.ms.split.cal' 
SB3refant = 'DA63'
tag = 'SB3'

# initial inspection of data before splitting out and averaging the continuum

plotms(vis = SB3, xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')

contspws = '2~3'
#flagging atmospheric lines at 243.4 GHz...the weather was better compared to IM_Lup_a_06_TC, so the 242.3 GHz atmospheric feature doesn't seem to affect the data 
flagchannels = '3:83~84' 
flagmanager(vis=SB3, mode='save', versionname='before_cont_flags')

flagdata(vis=SB3,mode='manual', spw=flagchannels, flagbackup=False, field = field)

# Average the channels within spws
SB3_initcont = field+'_'+tag+'_initcont.ms'
print SB3_initcont #just to double check for yourself that the name is actually ok
os.system('rm -rf ' + SB3_initcont + '*')
split2(vis=SB3,
       field = field,
       spw=contspws,      
       outputvis=SB3_initcont,
       width=[8, 8], # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
       datacolumn='data')


# Restore if desired
# flagmanager(vis=SB3,mode='restore', versionname='before_cont_flags')

# Check that amplitude vs. uvdist looks normal
plotms(vis=SB3_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30')

# Inspect individual antennae. We do this step here rather than before splitting because plotms will load the averaged continuum much faster 

plotms(vis = SB3_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '8', 
       coloraxis = 'spw', iteraxis = 'antenna')

plotms(vis = SB3_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '8', 
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
SB3_initcontimage = field+'_'+tag+'_initcontinuum'
os.system('rm -rf '+SB3_initcontimage+'.*')
clean(vis=[SB2_contms_ap1,SB3_initcont], 
      imagename=SB3_initcontimage, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='ellipse[[236pix,249pix],[3arcsec,2arcsec],145deg]',
      interactive=True)

# cleaned for 1 cycles (100 iterations)
# peak: 96.3 mJy/beam
# rms: 0.21 mJy/beam

# First phase-self-cal
SB3_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB3_p1)
gaincal(vis=SB3_initcont, caltable=SB3_p1, gaintype='T', 
        spw='0~1', refant=SB3refant, calmode='p', 
        solint='int', minsnr=2.0, minblperant=4)

plotcal(caltable=SB3_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna')

applycal(vis=SB3_initcont, spw='0~1', gaintable=[SB3_p1], calwt=T, flagbackup=F)

SB3_contms_p1 = field+'_'+tag+'_contp1.ms'
os.system('rm -rf '+SB3_contms_p1)
split2(vis=SB3_initcont, outputvis=SB3_contms_p1, datacolumn='corrected')


SB3_contimage_p1 = field+'_'+tag+'_p1continuum'
os.system('rm -rf '+SB3_contimage_p1+'.*')
clean(vis=[SB2_contms_ap1,SB3_contms_p1], 
      imagename=SB3_contimage_p1, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='ellipse[[236pix,249pix],[3arcsec,2arcsec],145deg]',
      interactive=True)

# cleaned for 3 cycles of 100 iterations each
# peak: 98.2 mJy/beam
# rms: 51.4 microJy/beam

SB3_p2 = field+'_'+tag+'.p2'
os.system('rm -rf '+SB3_p2)
gaincal(vis=SB3_contms_p1, caltable=SB3_p2, gaintype='T', 
        spw='0~1', refant=SB3refant, calmode='p', 
        solint='int', minsnr=2.0, minblperant=4)

# Amp self-cal

SB3_ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+SB3_ap1)
gaincal(vis=SB3_contms_p1, caltable=SB3_ap1, gaintype='T',  
        spw='0~1', refant=SB3refant, calmode='ap', 
        solint='60s', minsnr=2.0, minblperant=4, solnorm = True)

plotcal(caltable=SB3_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna')

applycal(vis=SB3_contms_p1, spw='0~1', gaintable=[SB3_ap1], calwt=T, flagbackup=F)

SB3_contms_ap1 = field+'_'+tag+'_contap1.ms'
os.system('rm -rf '+SB3_contms_ap1)
split2(vis=SB3_contms_p1, outputvis=SB3_contms_ap1, datacolumn='corrected')

SB3_contimage_ap1 = field+'_'+tag+'_ap1continuum'
os.system('rm -rf '+SB3_contimage_ap1+'.*')
clean(vis=[SB2_contms_ap1,SB3_contms_ap1], 
      imagename=SB3_contimage_ap1, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='ellipse[[236pix,249pix],[3arcsec,2arcsec],145deg]',
      interactive=True)

# cleaned for 3 cycles of 100 iterations each
# peak: 98.2 mJy/beam
# rms: 42.9 microJy/beam


### We are now done with self-cal of the continuum of SB1 and rename the final measurement set. 
SB3_contms_final = 'IM_Lup_'+tag+'_contfinal.ms'
os.system('cp -r '+SB3_contms_ap1+' '+SB3_contms_final)

##################################################################
##################################################################
## 2013.1.00226.S/im_lup_a_06_TE (P.I. Oberg) [as delivered to the PI]
##################################################################
##################################################################

field = 'im_lup'
SB4 = 'calibrated.ms' #replace as appropriate
SB4refant = 'DA48'
tag = 'SB4'

# initial inspection of data before splitting out and averaging the continuum

plotms(vis = SB4, xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')

"""
Note that this was a bandwidth switching project, so the calibrators were observed on 4 TDM windows that the target was not observed on. Therefore, if 
you are downloading the data from the archive, you need to change contspws to '12~16' and the CO line to '15:500~630' 
"""

contspws = '8~12' #all upper sideband windows
# Flag the CO 2-1 line
flagchannels = '11:500~630'
flagmanager(vis=SB4, mode='save', versionname='before_cont_flags')

flagdata(vis=SB4,mode='manual', spw=flagchannels, flagbackup=False, field = field)

# Average the channels within spws
SB4_initcont = field+'_'+tag+'_initcont.ms'
print SB4_initcont #just to double check for yourself that the name is actually ok
os.system('rm -rf ' + SB4_initcont + '*')
split2(vis=SB4,
       field = field,
       spw=contspws,      
       outputvis=SB4_initcont,
       width=960, # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
       datacolumn='data')


flagmanager(vis=SB4,mode='restore', versionname='before_cont_flags')

# Check that amplitude vs. uvdist looks normal
plotms(vis=SB4_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30')

# Inspect individual antennae. We do this step here rather than before splitting because plotms will load the averaged continuum much faster 

plotms(vis = SB4_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '4', 
       coloraxis = 'spw', iteraxis = 'antenna')

plotms(vis = SB4_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '4', 
       coloraxis = 'spw', iteraxis = 'antenna')

# Create dirty image 
SB4_initcontimage_dirty = field+'_'+tag+'_initcontinuum_dirty'
os.system('rm -rf '+SB4_initcontimage_dirty+'.*')
clean(vis=SB4_initcont, 
      imagename=SB4_initcontimage_dirty, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      robust=0.5,
      imsize=500,
      cell='0.05arcsec', 
      interactive=False, 
      niter = 0)

#this is offset from SB1, 2, and 3, so we use the model from cleaning Pinte's data to start self-calibration
ft(vis = SB4_initcont, model = 'Im_Lupi_SB1_ap1continuum.model') 

# First phase-self-cal
SB4_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB4_p1)
gaincal(vis=SB4_initcont, caltable=SB4_p1, gaintype='T', combine = 'spw', 
        spw='0~4', refant=SB4refant, calmode='p', 
        solint='10s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB4_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna')

applycal(vis=SB4_initcont, spw='0~4', spwmap = 5*[0], gaintable=[SB4_p1], calwt=T, flagbackup=F)

SB4_contms_p1 = field+'_'+tag+'_contp1.ms'
os.system('rm -rf '+SB4_contms_p1)
split2(vis=SB4_initcont, outputvis=SB4_contms_p1, datacolumn='corrected')


SB4_contimage_p1 = field+'_'+tag+'_p1continuum'
os.system('rm -rf '+SB4_contimage_p1+'.*')
clean(vis=SB4_contms_p1, 
      imagename=SB4_contimage_p1, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='ellipse[[236pix,249pix],[3arcsec,2arcsec],145deg]',
      interactive=True)

# cleaned for 2 cycles of 100 iterations each
# peak: 68.4 mJy/beam
# rms: 99 microJy/beam

SB4_p2 = field+'_'+tag+'.p2'
os.system('rm -rf '+SB4_p2)
gaincal(vis=SB4_contms_p1, caltable=SB4_p2, gaintype='T', combine = 'spw',
        spw='0~4', refant=SB4refant, calmode='p', 
        solint='int', minsnr=2.0, minblperant=4)

plotcal(caltable=SB4_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna')

applycal(vis=SB4_contms_p1, spw='0~4', spwmap = 5*[0], gaintable=[SB4_p2], calwt=T, flagbackup=F)

SB4_contms_p2 = field+'_'+tag+'_contp2.ms'
os.system('rm -rf '+SB4_contms_p2)
split2(vis=SB4_contms_p1, outputvis=SB4_contms_p2, datacolumn='corrected')


SB4_contimage_p2 = field+'_'+tag+'_p2continuum'
os.system('rm -rf '+SB4_contimage_p2+'.*')
clean(vis=SB4_contms_p2, 
      imagename=SB4_contimage_p2, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='ellipse[[236pix,249pix],[3arcsec,2arcsec],145deg]',
      interactive=True)

# cleaned for 2 cycles of 100 iterations each
# peak: 68.6 mJy/beam
# rms: 95.4 microJy/beam

# Amp self-cal

SB4_ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+SB4_ap1)
gaincal(vis=SB4_contms_p2, caltable=SB4_ap1, gaintype='T',  
        spw='0~4', refant=SB4refant, calmode='ap', 
        solint='60s', minsnr=2.0, minblperant=4, solnorm = True)

plotcal(caltable=SB4_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna')

applycal(vis=SB4_contms_p1, spw='0~4', gaintable=[SB4_ap1], calwt=T, flagbackup=F)

SB4_contms_ap1 = field+'_'+tag+'_contap1.ms'
os.system('rm -rf '+SB4_contms_ap1)
split2(vis=SB4_contms_p1, outputvis=SB4_contms_ap1, datacolumn='corrected')

SB4_contimage_ap1 = field+'_'+tag+'_ap1continuum'
os.system('rm -rf '+SB4_contimage_ap1+'.*')
clean(vis=SB4_contms_ap1, 
      imagename=SB4_contimage_ap1, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='ellipse[[236pix,249pix],[3arcsec,2arcsec],145deg]',
      interactive=True)

# cleaned for 3 cycles of 100 iterations each
# peak: 89.6 mJy/beam
# rms: 68.7 microJy/beam


### We are now done with self-cal of the continuum of SB1 and rename the final measurement set. 
SB4_contms_final = 'IM_Lup_'+tag+'_contfinal.ms'
os.system('cp -r '+SB4_contms_ap1+' '+SB4_contms_final)

##################################################################
##################################################################
## 2013.1.00226.S/im_lup_b_06_TE (P.I. Oberg) [downloaded from archive; see Huang et al. 2017 for details]
##################################################################
##################################################################

field = 'im_lup'
SB5 = 'uid___A002_X86e521_X5ed.ms.split.cal' #replace as appropriate
SB5refant = 'DA48'
tag = 'SB5'

# initial inspection of data before splitting out and averaging the continuum

plotms(vis = SB5, xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')

contspws = '12~17' #all lower sideband windows


# Average the channels within spws
SB5_initcont = field+'_'+tag+'_initcont.ms'
print SB5_initcont #just to double check for yourself that the name is actually ok
os.system('rm -rf ' + SB5_initcont + '*')
split2(vis=SB5,
       field = field,
       spw=contspws,      
       outputvis=SB5_initcont,
       width=[1920, 1920, 960,960,960,960], # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
       datacolumn='data')

# Check that amplitude vs. uvdist looks normal
plotms(vis=SB5_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30')

# flagging for what seem to be anomalous amplitudes
flagdata(vis=SB5_initcont, mode='manual', antenna = 'PM03, DV14, DA47, DV15, DA64', flagbackup=False, field = field)

# Inspect individual antennae. We do this step here rather than before splitting because plotms will load the averaged continuum much faster 

plotms(vis = SB5_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',
       coloraxis = 'spw', iteraxis = 'antenna')

flagdata(vis=SB5_initcont, mode='manual', timerange = '2014/07/17/02:27:50~2014/07/17/02:27:57', flagbackup=False, field = field)

plotms(vis = SB5_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',
       coloraxis = 'spw', iteraxis = 'antenna')

# Create dirty image 
SB5_initcontimage_dirty = field+'_'+tag+'_initcontinuum_dirty'
os.system('rm -rf '+SB5_initcontimage_dirty+'.*')
clean(vis=SB5_initcont, 
      imagename=SB5_initcontimage_dirty, 
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

#including previous measurement sets to build better initial model for self-cal
SB5_initcontimage = field+'_'+tag+'_initcontinuum'
os.system('rm -rf '+SB5_initcontimage+'.*')
clean(vis=[SB3_contms_ap1, SB4_contms_ap1, SB5_initcont], 
      imagename=SB5_initcontimage, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='ellipse[[236pix,249pix],[3arcsec,2arcsec],145deg]',
      interactive=True)

# cleaned for 2 cycles (100 iterations)
# peak: 78.3 mJy/beam
# rms: 0.14 mJy/beam

# First phase-self-cal
SB5_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB5_p1)
gaincal(vis=SB5_initcont, caltable=SB5_p1, gaintype='T', combine = 'spw',
        spw='0~5', refant=SB5refant, calmode='p', 
        solint='int', minsnr=2.0, minblperant=4)

plotcal(caltable=SB5_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna')

applycal(vis=SB5_initcont, spw='0~5', spwmap = 6*[0], gaintable=[SB5_p1], calwt=T, flagbackup=F)

SB5_contms_p1 = field+'_'+tag+'_contp1.ms'
os.system('rm -rf '+SB5_contms_p1)
split2(vis=SB5_initcont, outputvis=SB5_contms_p1, datacolumn='corrected')


SB5_contimage_p1 = field+'_'+tag+'_p1continuum'
os.system('rm -rf '+SB5_contimage_p1+'.*')
clean(vis=[SB3_contms_ap1, SB4_contms_ap1, SB5_contms_p1], 
      imagename=SB5_contimage_p1, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='ellipse[[236pix,249pix],[3arcsec,2arcsec],145deg]',
      interactive=True)

# cleaned for 3 cycles of 100 iterations each
# peak: 79.7 mJy/beam
# rms: 79 microJy/beam

SB5_ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+SB5_ap1)
gaincal(vis=SB5_contms_p1, caltable=SB5_ap1, gaintype='T', 
        spw='0~5', refant=SB5refant, calmode='ap', 
        solint='60s', minsnr=2.0, minblperant=4, solnorm = True)

plotcal(caltable=SB5_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna')

applycal(vis=SB5_contms_p1, spw='0~5', gaintable=[SB5_ap1], calwt=T, flagbackup=F)

SB5_contms_ap1 = field+'_'+tag+'_contap1.ms'
os.system('rm -rf '+SB5_contms_ap1)
split2(vis=SB5_contms_p1, outputvis=SB5_contms_ap1, datacolumn='corrected')

SB5_contimage_ap1 = field+'_'+tag+'_ap1continuum'
os.system('rm -rf '+SB5_contimage_ap1+'.*')
clean(vis=[SB3_contms_ap1, SB4_contms_ap1,SB5_contms_ap1], 
      imagename=SB5_contimage_ap1, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='ellipse[[236pix,249pix],[3arcsec,2arcsec],145deg]',
      interactive=True)

# cleaned for 2 cycles of 100 iterations each
# peak: 79.9 mJy/beam
# rms: 77 microJy/beam

# concatenate all short baseline observations

concat(vis = [SB1_contms_ap1, SB2_contms_ap1,SB3_contms_ap1, SB4_contms_ap1,SB5_contms_ap1], concatvis = 'IM_Lup_allSB_cont.ms', freqtol = '20MHz', dirtol = '0.1arcsec', respectname = False, copypointing = False)

clean(vis='IM_Lup_allSB_cont.ms',
      imagename='IM_Lup_allSB_continuum', 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='ellipse[[236pix,249pix],[3arcsec,2arcsec],145deg]',
      interactive=True)

clean(vis='IM_Lup_allSB_cont.ms',
      imagename='IM_Lup_allSB_uniform', 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 30, 50], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=-2,
      gain = 0.1,
      imsize=500,
      cell='0.05arcsec', 
      mask='ellipse[[236pix,249pix],[3arcsec,2arcsec],145deg]',
      interactive=True)


