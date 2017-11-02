"""
This script is written for CASA 4.5.3
Note that the imaging algorithms were rewritten significantly between CASA 4.5.3 and CASA 4.7.2 


Datasets calibrated:
SB1: 2013.1.00498.S/HD_142666_a_06_TE (P.I. Perez)
"""

field = 'Elias_24'

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
flagchannels='1:150~250, 5:25~100, 6:790~850' 

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

flagdata(vis=SB1_initcont,mode='manual', spw='3~4,6', flagbackup=False, field = field, timerange = '2015/07/21/22:45:00~2015/07/21/23:10:00', antenna = 'DA41')
flagdata(vis=SB1_initcont,mode='manual', spw='1,3,5', flagbackup=False, field = field, scan = '30', antenna = 'DA46')
flagdata(vis=SB1_initcont,mode='manual', spw='3,4,6', flagbackup=False, field = field, scan='30,35', antenna = 'DA59')
flagdata(vis=SB1_initcont,mode='manual', spw='3,4', flagbackup=False, field = field, scan='30', antenna = 'DV08')
flagdata(vis=SB1_initcont,mode='manual', spw='3', flagbackup=False, field = field, scan='30,35', antenna = 'DV18')

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
      multiscale = [0, 10, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[239pix,257pix],1.5arcsec]',
      interactive=True)

# cleaned for 5 cycles (100 iterations each)
# peak: 38.5 mJy/beam
# rms: 124 microJy/beam

# First phase-self-cal
SB1_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB1_p1)
gaincal(vis=SB1_initcont, caltable=SB1_p1, gaintype='T', combine = 'spw', 
        spw=contspws, refant=SB1refant, calmode='p', 
        solint='15s', minsnr=2.0, minblperant=4)

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
      multiscale = [0, 10, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[239pix,257pix],1.5arcsec]',
      interactive=True)

# cleaned for six cycles of 100 iterations each
# peak: 41.9 mJy/beam
# rms: 82 microJy/beam


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
      multiscale = [0, 10, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[239pix,257pix],1.5arcsec]',
      interactive=True)

# cleaned for six cycles of 100 iterations each
# peak: 41.1 mJy/beam
# rms: 70 microJy/beam

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

applycal(vis=SB1_CO_ms, spw='0', gaintable=[SB1_p1, SB1_ap1], calwt=T, flagbackup=F)

SB1_CO_mscontsub = SB1_CO_ms+'.contsub'
os.system('rm -rf '+SB1_CO_mscontsub) 
fitspw = '0:0~150;250~1919' # channels for fitting continuum
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
mstransform(vis = SB1_CO_mscontsub, outputvis = SB1_CO_cvel,  keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='-5.0km/s',width='0.35km/s',nchan=40, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

#check individual observation
SB1_CO_image = field+'_'+tag+'_CO21cube'
os.system('rm -rf '+SB1_CO_image+'.*')
clean(vis=SB1_CO_cvel, 
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
      start='-5.0km/s',
      width='0.35km/s',
      nchan=40, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '8mJy',
      interactive=True) 



##################################################################
##################################################################
## long baseline data
##################################################################
##################################################################
LB_vis = '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X4c/group.uid___A001_X8c5_X4d/member.uid___A001_X8c5_X4e/calibrated/calibrated_final.ms' #this is the long-baseline measurement set being calibrated
field = 'Elias_24' 

LB1_refant = 'DA61, DV24'
tag = 'EB'

# spws 3 and 7 contain the CO 2-1 line, while the others are continuum only
contspws = '0~7'

flagmanager(vis=LB_vis,mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
# velocity range selected for flagging based on compact configuration data
flagchannels='3:1880~1970, 7:1880~1970'

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
clean(vis=LB1_initcont, 
      observation = '0', 
      imagename=LB1_initcontimage0, 
      mode='mfs', 
      multiscale = [0, 20, 40, 60], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.3,
      imsize=2400,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask = 'ellipse[[1164pix, 1072pix], [1.5arcsec,1.5arcsec],0deg]',
      imagermode = 'csclean')


#20 cycles of 100 iterations each 

LB1_initcontimage1 = field+'_'+tag+'_initcontinuum_1'
os.system('rm -rf '+LB1_initcontimage1+'.*')
clean(vis=LB1_initcont, 
      observation = '1', 
      imagename=LB1_initcontimage1, 
      mode='mfs', 
      multiscale = [0, 20, 40, 80, 160, 320], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.3,
      imsize=2400,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask = 'ellipse[[1164pix, 1072pix], [1.5arcsec,1.5arcsec],0deg]',
      imagermode = 'csclean')


#22 cycles of 100 iterations each

#long baseline and short baseline images look properly aligned


concat(vis = [SB1_contms_final, LB1_initcont], concatvis = 'Elias_24_contcombined.ms', dirtol = '1arcsec', copypointing = False) 



LB1_initcontimage = field+'_'+tag+'_initcontinuum'
os.system('rm -rf '+LB1_initcontimage+'.*')
clean(vis='Elias_24_contcombined.ms', 
      imagename=LB1_initcontimage, 
      mode='mfs', 
      multiscale = [0, 20, 40, 80, 160, 320], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.1,
      imsize=2400,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask = 'ellipse[[1083pix, 1265pix], [1.5arcsec,1.5arcsec],0deg]',
      imagermode = 'csclean')

#80 cycles of 100 iterations each
#rms: 18.5 microJy/beam
#peak: 4.6 mJy/beam

#delmod(vis=LB1_initcont,field=field,otf=True)

#clearcal(vis=LB1_initcont)

# First round of phase-only self-cal
LB1_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+LB1_p1)
gaincal(vis='Elias_24_contcombined.ms', caltable=LB1_p1, gaintype='T', combine = 'spw,scan', 
        spw='0~15', refant=LB1_refant, calmode='p', 
        solint='150s', minsnr=2.0, minblperant=4)

applycal(vis='Elias_24_contcombined.ms', spw='0~15', spwmap = [0]*16, gaintable=[LB1_p1], calwt=True, applymode = 'calonly', flagbackup=False, interp = 'linearperobs')

tag = 'combined'

LB1_contms_p1 = field+'_'+tag+'_contp1.ms'
os.system('rm -rf '+LB1_contms_p1)
split2(vis='Elias_24_contcombined.ms', outputvis=LB1_contms_p1, datacolumn='corrected')

LB1_contimagep1 = field+'_'+tag+'_continuump1'
os.system('rm -rf '+LB1_contimagep1+'.*')
clean(vis=LB1_contms_p1, 
      imagename=LB1_contimagep1, 
      mode='mfs', 
      multiscale = [0, 20, 40, 80, 160, 320], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.1,
      imsize=2400,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask = 'ellipse[[1083pix, 1265pix], [1.5arcsec,1.5arcsec],0deg]',
      imagermode = 'csclean')

