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




