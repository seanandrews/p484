"""
This script is written for CASA 4.5.3
Note that the imaging algorithms were rewritten significantly between CASA 4.5.3 and CASA 4.7.2 

Datasets calibrated:
SB1: 2013.1.00798.S/Im_Lup_a_06_TE 
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
