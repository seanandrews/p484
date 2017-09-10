"""
This script is written for CASA 4.5.3
Note that the imaging algorithms were rewritten significantly between CASA 4.5.3 and CASA 4.7.2 

Datasets calibrated: 
2013.1.00366.S/HHD_16329_a_06_TE (PI: Hughes)
2013.1.00601.S/HD_16329_a_06_TE (PI: Isella)
"""

##################################################################
##################################################################
## 2013.1.00601.S/HD_16329_a_06_TE (PI: Hughes) (downloaded from archive)
##################################################################
##################################################################
field = 'HD_163296'
tag = 'SB1'
SB1refant = 'DA63,DA48'

SB1_exec0 = '/data/astrochem1/jane/2013.1.00366.S/science_goal.uid___A001_X121_X2aa/group.uid___A001_X121_X2ab/member.uid___A001_X121_X2ac/calibrated/uid___A002_X847097_X125c.ms.split.cal'
SB1_exec1 = '/data/astrochem1/jane/2013.1.00366.S/science_goal.uid___A001_X121_X2aa/group.uid___A001_X121_X2ab/member.uid___A001_X121_X2ac/calibrated/uid___A002_X84187d_X17c0.ms.split.cal'
SB1_exec2 = '/data/astrochem1/jane/2013.1.00366.S/science_goal.uid___A001_X121_X2aa/group.uid___A001_X121_X2ab/member.uid___A001_X121_X2ac/calibrated/uid___A002_X856bb8_X28dd.ms.split.cal'
SB1_exec3 = '/data/astrochem1/jane/2013.1.00366.S/science_goal.uid___A001_X121_X2aa/group.uid___A001_X121_X2ab/member.uid___A001_X121_X2ac/calibrated/uid___A002_X8440e0_X3e97.ms.split.cal'
SB1_exec4 = '/data/astrochem1/jane/2013.1.00366.S/science_goal.uid___A001_X121_X2aa/group.uid___A001_X121_X2ab/member.uid___A001_X121_X2ac/calibrated/uid___A002_X835491_X4bb.ms.split.cal'
#split off USB windows (corrected column is used because fluxes were adjusted with setjy based on the ALMA calibrator catalog)
os.system('rm -rf HD_163296_SB1_exec0.ms')
split2(vis=SB1_exec0,
       spw = '0~1', 
       field = field,    
       outputvis='HD_163296_SB1_exec0.ms',
       datacolumn='corrected')

os.system('rm -rf HD_163296_SB1_exec1.ms')
split2(vis=SB1_exec1,
       spw = '0~1', 
       field = field,    
       outputvis='HD_163296_SB1_exec1.ms',
       datacolumn='corrected')

os.system('rm -rf HD_163296_SB1_exec2.ms')
split2(vis=SB1_exec2,
       spw = '0~1', 
       field = field,    
       outputvis='HD_163296_SB1_exec2.ms',
       datacolumn='corrected')

os.system('rm -rf HD_163296_SB1_exec3.ms')
split2(vis=SB1_exec3,
       spw = '0~1', 
       field = field,    
       outputvis='HD_163296_SB1_exec3.ms',
       datacolumn='corrected')

os.system('rm -rf HD_163296_SB1_exec4.ms')
split2(vis=SB1_exec4,
       spw = '0~1', 
       field = field,    
       outputvis='HD_163296_SB1_exec4.ms',
       datacolumn='corrected')

listobs(vis = 'HD_163296_SB1_exec4.ms')
# initial inspection of data before splitting out and averaging the continuum

plotms(vis = 'HD_163296_SB1_exec0.ms', xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')

plotms(vis = 'HD_163296_SB1_exec1.ms', xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')

plotms(vis = 'HD_163296_SB1_exec2.ms', xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')


plotms(vis = 'HD_163296_SB1_exec3.ms', xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')

plotms(vis = 'HD_163296_SB1_exec4.ms', xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')


SB1_field = 'HD_163296_SB1.ms'
os.system('rm -rf '+SB1_field)
concat(vis = ['HD_163296_SB1_exec0.ms', 'HD_163296_SB1_exec1.ms','HD_163296_SB1_exec2.ms', 'HD_163296_SB1_exec3.ms', 'HD_163296_SB1_exec4.ms'], concatvis = SB1_field, dirtol = '0.1arcsec', copypointing = False)

# spw 0,2,4,6,8 contains CO 2-1 
contspws = '0~9'
flagmanager(vis=SB1_field,mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
flagchannels='0:1000~2950, 2:1000~2950, 4:1000~2950, 6:1000~2950, 8:1000~2950' #modify as appropriate for the given field

flagdata(vis=SB1_field,mode='manual', spw=flagchannels, flagbackup=False, field = field)

# Average the channels within spws
SB1_initcont = field+'_'+tag+'_initcont.ms'
print SB1_initcont #just to double check for yourself that the name is actually ok
os.system('rm -rf ' + SB1_initcont + '*')
split2(vis=SB1_field,
       field = field,
       spw=contspws,      
       output3vis=SB1_initcont,
       width=[3840,8,3840,8,3840,8, 3840, 8, 3840, 8], # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
       datacolumn='data')


# Restore flagged line channels
flagmanager(vis=SB1_field,mode='restore',
            versionname='before_cont_flags')

# Check amplitude vs. uvdist
plotms(vis=SB1_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30s',avgscan = True)


flagdata(vis=SB1_initcont, spw = '1', antenna = 'DV02&DV17', action='apply', flagbackup=F)
flagdata(vis=SB1_initcont, spw = '1', antenna = 'DV02&DV16', action='apply', flagbackup=F)
flagdata(vis=SB1_initcont, spw = '1', antenna = 'DV02&DA44', action='apply', flagbackup=F)
flagdata(vis=SB1_initcont, spw = '1', antenna = 'DV02&DA46', action='apply', flagbackup=F)

flagdata(vis=SB1_initcont, spw = '3', antenna = 'DV02&DV17', action='apply', flagbackup=F)
flagdata(vis=SB1_initcont, spw = '3', antenna = 'DV02&DV19', action='apply', flagbackup=F)
flagdata(vis=SB1_initcont, spw = '3', antenna = 'DV02&DA44', action='apply', flagbackup=F)

flagdata(vis=SB1_initcont, spw = '5', antenna = 'DV02&DV17', action='apply', flagbackup=F)
flagdata(vis=SB1_initcont, spw = '5', antenna = 'DV02&DV16', action='apply', flagbackup=F)
flagdata(vis=SB1_initcont, spw = '5', antenna = 'DV02&DA44', action='apply', flagbackup=F)

flagdata(vis=SB1_initcont, spw = '7', antenna = 'DV02&DV17', action='apply', flagbackup=F)
flagdata(vis=SB1_initcont, spw = '7', antenna = 'DV02&DV16', action='apply', flagbackup=F)
flagdata(vis=SB1_initcont, spw = '7', antenna = 'DV02&DA44', action='apply', flagbackup=F)


flagdata(vis=SB1_initcont, spw = '1', timerange = '08:22:13.0~08:22:16.0', action='apply', flagbackup=F)
flagdata(vis=SB1_initcont, spw = '2', timerange = '06:38:35.0~06:38:40.0', action='apply', flagbackup=F)
flagdata(vis=SB1_initcont, spw = '2', timerange = '07:23:38.0~07:23:42.0', action='apply', flagbackup=F)
flagdata(vis=SB1_initcont, spw = '6', timerange = '08:14:45.0~08:14:50.0', action='apply', flagbackup=F)
flagdata(vis=SB1_initcont, spw = '9', timerange = '06:00:24.0~06:00:25.0', antenna = 'DA57', action='apply', flagbackup=F)


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
      cell='0.05arcsec', 
      mask='ellipse[[250pix,250pix],[2.5arcsec,1.75arcsec],140deg]',
      interactive=True)

# cleaned for 3 cycles (100 iterations each)
# peak: 169 mJy/beam
# rms: 0.59 mJy/beam

# First phase-self-cal
SB1_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB1_p1)
gaincal(vis=SB1_initcont, caltable=SB1_p1, gaintype='T', combine = 'spw',
        spw=contspws, refant=SB1refant, calmode='p', 
        solint='int', minsnr=2.0, minblperant=4)

plotcal(caltable=SB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2014/06/04/00:00:01~2014/06/04/11:59:59')
plotcal(caltable=SB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2014/06/14/00:00:01~2014/06/14/11:59:59')
plotcal(caltable=SB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2014/06/16/00:00:01~2014/06/16/11:59:59')
plotcal(caltable=SB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2014/06/17/00:00:01~2014/06/17/11:59:59')
plotcal(caltable=SB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2014/06/29/00:00:01~2014/06/29/11:59:59')

applycal(vis=SB1_initcont, spw=contspws, spwmap = [0]*10, gaintable=[SB1_p1], calwt=T, flagbackup=F)

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
      cell='0.05arcsec', 
      mask='ellipse[[250pix,250pix],[2.5arcsec,1.75arcsec],140deg]',
      interactive=True)

# cleaned for 6 cycles with 100 iterations each 
# peak: 180 mJy/beam
# rms: 69 microJy/beam

SB1_ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+SB1_ap1)
gaincal(vis=SB1_contms_p1, caltable=SB1_ap1, gaintype='T', combine = 'spw', 
        spw='0~9', refant=SB1refant, calmode='ap', 
        solint='60s', minsnr=2.0, minblperant=4, solnorm = True)

plotcal(caltable=SB1_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = '2014/06/04/00:00:01~2014/06/04/11:59:59')
plotcal(caltable=SB1_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = '2014/06/14/00:00:01~2014/06/14/11:59:59')
plotcal(caltable=SB1_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = '2014/06/16/00:00:01~2014/06/16/11:59:59')
plotcal(caltable=SB1_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = '2014/06/17/00:00:01~2014/06/17/11:59:59')
plotcal(caltable=SB1_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = '2014/06/29/00:00:01~2014/06/29/11:59:59')

applycal(vis=SB1_contms_p1, spw='0~9', spwmap = 10*[0], gaintable=[SB1_ap1], calwt=T, flagbackup=F)


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
      cell='0.05arcsec', 
      mask='ellipse[[250pix,250pix],[2.5arcsec,1.75arcsec],140deg]',
      interactive=True)

# cleaned for 3 cycles of 100 iterations each
# peak: 180 mJy/beam
# rms: 40 microJy/beam

### We are now done with self-cal of the continuum of SB1 and rename the final measurement set. 
### This is time-averaged to make the dataset smaller (test images indicate that image quality is not degraded)
SB1_contms_final = field+'_'+tag+'_contfinal.ms'
mstransform(vis = SB1_contms_ap1, outputvis =SB1_contms_final, timeaverage = True, timebin = '30s', keepflags = False, datacolumn = 'data')

##############################
# Reduction of CO data in SB1
#############################

#split out the CO 2-1 spectral window
linespw = '0,2,4,6,8'
SB1_CO_ms = field+'_'+tag+'_CO21.ms'
os.system('rm -rf ' + SB1_CO_ms + '*')
split2(vis=SB1_field,
       field = field,
       spw=linespw,      
       outputvis=SB1_CO_ms, 
       datacolumn='data')

applycal(vis=SB1_CO_ms, spw='0~4',spwmap = [[0,0,0,0,0],[0,0,0,0,0]], gaintable=[SB1_p1, SB1_ap1], calwt=T, flagbackup=F)

plotms(vis = SB1_CO_ms, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)

SB1_CO_mscontsub = SB1_CO_ms+'.contsub'
os.system('rm -rf '+SB1_CO_mscontsub) 
fitspw = '0:0~1000;3000~3839, 1:0~1000;3000~3839, 2:0~1000;3000~3839,3:0~1000;3000~3839,4:0~1000;3000~3839 ' # channels for fitting continuum
uvcontsub(vis=SB1_CO_ms,
          spw='0~4', 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=1,
          want_cont=False) 

flagdata(vis=SB1_CO_ms, spw = '1', timerange = '06:38:35.0~06:38:40.0', action='apply', flagbackup=F)
flagdata(vis=SB1_CO_ms, spw = '1', timerange = '07:23:38.0~07:23:42.0', action='apply', flagbackup=F)
flagdata(vis=SB1_CO_ms, spw = '3', timerange = '08:14:45.0~08:14:50.0', action='apply', flagbackup=F)

plotms(vis = SB1_CO_mscontsub, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)

SB1_CO_cvel = SB1_CO_mscontsub+'.cvel'

os.system('rm -rf '+ SB1_CO_cvel)
mstransform(vis = SB1_CO_mscontsub, outputvis = SB1_CO_cvel,  keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='-15km/s',width='0.35km/s',nchan=120, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

SB1_CO_averaged = SB1_CO_mscontsub+'.avg'
split2(vis=SB1_CO_cvel,
       field = field,      
       outputvis=SB1_CO_averaged, 
       timebin = '30s', 
       datacolumn='data')

plotms(vis = SB1_CO_averaged, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)

SB1_CO_image = field+'_'+tag+'_CO21cube'
os.system('rm -rf '+SB1_CO_image+'.*')
clean(vis=SB1_CO_averaged, 
      imagename=SB1_CO_image,
      mode = 'velocity',
      psfmode = 'clark',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 30, 50,100],
      robust = 1.0,
      gain = 0.3, 
      imsize = 500,
      cell = '0.05arcsec',
      start='-15km/s',
      width='0.35km/s',
      nchan=120, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '6mJy',
      interactive=True) 


SB1_CO_image = field+'_'+tag+'_CO21cube_unaveraged'
os.system('rm -rf '+SB1_CO_image+'.*')
clean(vis=SB1_CO_cvel, 
      imagename=SB1_CO_image,
      mode = 'velocity',
      psfmode = 'clark',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 30, 50,100],
      robust = 1.0,
      gain = 0.3, 
      imsize = 500,
      cell = '0.05arcsec',
      start='-15km/s',
      width='0.35km/s',
      nchan=120, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '6mJy',
      mask = 'HD_163296_SB1_CO21cube.mask',
      interactive=True) 
os.system('rm -rf '+SB1_CO_image+'.mom0')
immoments(axis = "spec",imagename=SB1_CO_image+'.image',moments=[0],outfile =SB1_CO_image+'.mom0', chans = '5~45')

os.system('rm -rf '+SB1_CO_image+'.mom1')
immoments(axis = "spec",imagename=SB1_CO_image+'.image',moments=[1],outfile =SB1_CO_image+'.mom1', chans = '5~45', includepix = [.012, 10])

os.system('rm -rf '+SB1_CO_image+'.mom8')
immoments(axis = "spec",imagename=SB1_CO_image+'.image',moments=[8],outfile =SB1_CO_image+'.mom8', chans = '5~45', includepix = [.012, 10])

exportfits(imagename = SB1_CO_image+'.image', fitsimage = SB1_CO_image+'.image.fits')

##################################################################
##################################################################
## 2013.1.00601.S/HD_16329_a_06_TE (PI: Isella) (downloaded from archive)
##################################################################
##################################################################
field = 'HD_163296'
tag = 'SB2'
SB2refant = 'DA55'

SB2_exec0 = 'uid___A002_Xa76868_X14f5.ms.split.cal'
SB2_exec1 = 'uid___A002_Xa7a216_Xce2.ms.split.cal'
SB2_exec2 = 'uid___A002_Xa7b91c_Xd6c.ms.split.cal'

#split off USB windows
os.system('rm -rf HD_163296_SB2_exec0.ms')
split2(vis=SB2_exec0,
       spw = '0~1', 
       field = field,    
       outputvis='HD_163296_SB2_exec0.ms',
       datacolumn='data')

os.system('rm -rf HD_163296_SB2_exec1.ms')
split2(vis=SB2_exec1,
       spw = '0~1', 
       field = field,    
       outputvis='HD_163296_SB2_exec1.ms',
       datacolumn='data')

os.system('rm -rf HD_163296_SB2_exec2.ms')
split2(vis=SB2_exec2,
       spw = '0~1', 
       field = field,    
       outputvis='HD_163296_SB2_exec2.ms',
       datacolumn='data')

# initial inspection of data before splitting out and averaging the continuum

plotms(vis = 'HD_163296_SB2_exec0.ms', xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')

plotms(vis = 'HD_163296_SB2_exec1.ms', xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')

plotms(vis = 'HD_163296_SB2_exec2.ms', xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')

SB2_field = 'HD_163296_SB2.ms'
os.system('rm -rf '+SB2_field)
concat(vis = ['HD_163296_SB2_exec0.ms', 'HD_163296_SB2_exec1.ms','HD_163296_SB2_exec2.ms'], concatvis = SB2_field, dirtol = '0.1arcsec', copypointing = False)

# spw 0,2,4 contains CO 2-1 from chans 1300 to 2800
contspws = '0~5'
flagmanager(vis=SB2_field,mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
flagchannels='0:1300~2800,2:1300~2800,4:1300~2800' #modify as appropriate for the given field

flagdata(vis=SB2_field,mode='manual', spw=flagchannels, flagbackup=False, field = field)

# Average the channels within spws
SB2_initcont = field+'_'+tag+'_initcont.ms'
print SB2_initcont #just to double check for yourself that the name is actually ok
os.system('rm -rf ' + SB2_initcont + '*')
split2(vis=SB2_field,
       field = field,
       spw=contspws,      
       outputvis=SB2_initcont,
       width=[3840,8,3840,8,3840,8], # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
       datacolumn='data')


# Restore flagged line channels
flagmanager(vis=SB2_field,mode='restore',
            versionname='before_cont_flags')

# Check amplitude vs. uvdist looks normal
plotms(vis=SB2_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30s',avgscan = True)




# Inspect individual antennae. We do this step here rather than before splitting because plotms will load the averaged continuum much faster 

plotms(vis = SB2_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '0',
       coloraxis = 'spw', iteraxis = 'antenna')


plotms(vis = SB2_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '1',
       coloraxis = 'spw', iteraxis = 'antenna')

plotms(vis = SB2_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '2',
       coloraxis = 'spw', iteraxis = 'antenna')

flagdata(vis=SB2_initcont,mode='manual', spw='0', flagbackup=False, field = field, scan = '14, 16', antenna = 'DA50')
flagdata(vis=SB2_initcont,mode='manual', spw='0~1', flagbackup=False, field = field, scan = '38,40', antenna = 'DV02')
flagdata(vis=SB2_initcont,mode='manual', spw='2~3', flagbackup=False, field = field, scan = '59', antenna = 'DA62,DV05,DV12')
flagdata(vis = SB2_initcont, mode='manual', spw='2~3', flagbackup=False, field = field, antenna = 'DA63')
flagdata(vis=SB2_initcont,mode='manual', spw='4,5', flagbackup=False, field = field, scan = '76, 78,84, 86')
flagdata(vis=SB2_initcont,mode='manual', spw='4,5', flagbackup=False, field = field, scan = '68,70', antenna = 'DA46&DA55;DA59&DA49;DA59&DV18;DA60&DV05;DA43&DV05')
flagdata(vis=SB2_initcont,mode='manual', spw='4,5', flagbackup=False, field = field, timerange = '2015/08/09/01:18:20~2015/08/09/01:21:00')


plotms(vis = SB2_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '0', 
       coloraxis = 'spw', iteraxis = 'antenna') 

plotms(vis = SB2_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '1', 
       coloraxis = 'spw', iteraxis = 'antenna') 

plotms(vis = SB2_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '2', 
       coloraxis = 'spw', iteraxis = 'antenna') 

# check the individual execution blocks
SB2_EB1_initcontimage_dirty = field+'_'+tag+'_EB1_initcontinuum_dirty'
os.system('rm -rf '+SB2_EB1_initcontimage_dirty+'.*')
clean(vis=SB2_initcont, 
      imagename=SB2_EB1_initcontimage_dirty, 
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

SB2_EB2_initcontimage_dirty = field+'_'+tag+'_EB2_initcontinuum_dirty'
os.system('rm -rf '+SB2_EB2_initcontimage_dirty+'.*')
clean(vis=SB2_initcont, 
      imagename=SB2_EB2_initcontimage_dirty, 
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

SB2_EB3_initcontimage_dirty = field+'_'+tag+'_EB3_initcontinuum_dirty'
os.system('rm -rf '+SB2_EB3_initcontimage_dirty+'.*')
clean(vis=SB2_initcont, 
      imagename=SB2_EB3_initcontimage_dirty, 
      observation = '2', 
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
SB2_initcontimage = field+'_'+tag+'_initcontinuum'
os.system('rm -rf '+SB2_initcontimage+'.*')
clean(vis=['HD_163296_SB1_contfinal.ms', SB2_initcont], 
      imagename=SB2_initcontimage, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 20, 40], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.0,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='ellipse[[250pix,250pix],[2.25arcsec,1.5arcsec],140deg]',
      interactive=True)

# cleaned for 3 cycles (100 iterations each)
# peak: 70 mJy/beam
# rms: 0.19 mJy/beam

# First phase-self-cal
SB2_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB2_p1)
gaincal(vis=SB2_initcont, caltable=SB2_p1, gaintype='T', combine = 'spw',
        spw=contspws, refant=SB2refant, calmode='p', 
        solint='60s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB2_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2015/08/05/00:00:01~2015/08/05/11:59:59')


plotcal(caltable=SB2_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2015/08/08/00:00:01~2015/08/08/11:59:59')

plotcal(caltable=SB2_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2015/08/09/00:00:01~2015/08/09/11:59:59')

applycal(vis=SB2_initcont, spw=contspws, spwmap = [0]*6, gaintable=[SB2_p1], calwt=T, flagbackup=F)

SB2_contms_p1 = field+'_'+tag+'_contp1.ms'
os.system('rm -rf '+SB2_contms_p1)
split2(vis=SB2_initcont, outputvis=SB2_contms_p1, datacolumn='corrected')


SB2_contimage_p1 = field+'_'+tag+'_p1continuum'
os.system('rm -rf '+SB2_contimage_p1+'.*')
clean(vis=['HD_163296_SB1_contfinal.ms', SB2_contms_p1], 
      imagename=SB2_contimage_p1, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 20, 40], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.0,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='ellipse[[250pix,250pix],[2.25arcsec,1.5arcsec],140deg]',
      interactive=True)

# cleaned for 8 cycles with 100 iterations each 
# peak: 75.6 mJy/beam
# rms: 67 microJy/beam


# Second phase self-cal 

SB2_p2 = field+'_'+tag+'.p2'
os.system('rm -rf '+SB2_p2)
gaincal(vis=SB2_contms_p1, caltable=SB2_p2, gaintype='T', combine = 'spw',
        spw=contspws, refant=SB2refant, calmode='p', 
        solint='30s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB2_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2015/08/05/00:00:01~2015/08/05/11:59:59')

plotcal(caltable=SB2_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2015/08/08/00:00:01~2015/08/08/11:59:59')

plotcal(caltable=SB2_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange ='2015/08/09/00:00:01~2015/08/09/11:59:59')

applycal(vis=SB2_contms_p1, spw=contspws, spwmap = [0]*6, gaintable=[SB2_p2], calwt=T, flagbackup=F)

SB2_contms_p2 = field+'_'+tag+'_contp2.ms'
os.system('rm -rf '+SB2_contms_p2)
split2(vis=SB2_contms_p1, outputvis=SB2_contms_p2, datacolumn='corrected')

SB2_contimage_p2 = field+'_'+tag+'_p2continuum'
os.system('rm -rf '+SB2_contimage_p2+'.*')
clean(vis=['HD_163296_SB1_contfinal.ms', SB2_contms_p2], 
      imagename=SB2_contimage_p2, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 20, 40], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.0,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='ellipse[[250pix,250pix],[2.25arcsec,1.5arcsec],140deg]',
      interactive=True)

# cleaned for 14 cycles of 100 iterations each
# peak: 76 mJy/beam
# rms: 60 microJy/beam

SB2_ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+SB2_ap1)
gaincal(vis=SB2_contms_p2, caltable=SB2_ap1, gaintype='T', combine = 'spw',   
        spw=contspws, refant=SB2refant, calmode='ap', 
        solint='inf', minsnr=2.0, minblperant=4, solnorm = True)

plotcal(caltable=SB2_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = '2015/08/05/00:00:01~2015/08/05/11:59:59')

plotcal(caltable=SB2_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = '2015/08/08/00:00:01~2015/08/08/11:59:59')

plotcal(caltable=SB2_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = '2015/08/09/00:00:01~2015/08/09/11:59:59')

applycal(vis=SB2_contms_p2, spw=contspws, spwmap = [0]*6, gaintable=[SB2_ap1], calwt=T, flagbackup=F)

SB2_contms_ap1 = field+'_'+tag+'_contap1.ms'
os.system('rm -rf '+SB2_contms_ap1)
split2(vis=SB2_contms_p2, outputvis=SB2_contms_ap1, datacolumn='corrected')

SB1_contimage_ap1 = field+'_'+tag+'_ap1continuum'
os.system('rm -rf '+SB1_contimage_ap1+'.*')
clean(vis=['HD_163296_SB1_contfinal.ms', SB2_contms_ap1], 
      imagename=SB1_contimage_ap1, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 20, 40], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.0,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='ellipse[[250pix,250pix],[2.4arcsec,1.7arcsec],140deg]',
      interactive=True)

# cleaned for 13 cycles of 100 iterations each
# peak: 78 mJy/beam
# rms: 55 microJy/beam

SB1_contimage_uniform = field+'_'+tag+'_uniform'
os.system('rm -rf '+SB1_contimage_uniform+'.*')
clean(vis=['HD_163296_SB1_contfinal.ms', SB2_contms_ap1], 
      imagename=SB1_contimage_uniform, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='uniform', 
      multiscale = [0, 10, 20, 40], # this is really up to the user. The choices here matter less than they do for the extended data. 
      gain = 0.3,
      imsize=500,
      cell='0.02arcsec', 
      mask='ellipse[[250pix,250pix],[2.4arcsec,1.7arcsec],140deg]',
      interactive=True)

### We are now done with self-cal of the continuum of SB1 and create the final measurement set. 
SB2_contms_final = field+'_'+tag+'_contfinal.ms'
mstransform(vis = SB2_contms_ap1, outputvis =SB2_contms_final, timeaverage = True, timebin = '30s', keepflags = False, datacolumn = 'data')

##############################
# Reduction of CO data in SB2
#############################

#split out the CO 2-1 spectral window
linespw = '0,2,4'
SB2_CO_ms = field+'_'+tag+'_CO21.ms'
os.system('rm -rf ' + SB2_CO_ms + '*')
split2(vis=SB2_field,
       field = field,
       spw=linespw,      
       outputvis=SB2_CO_ms, 
       datacolumn='data')

flagdata(vis=SB2_CO_ms,mode='manual', spw='0', flagbackup=False, field = field, scan = '14, 16', antenna = 'DA50')
flagdata(vis=SB2_CO_ms,mode='manual', spw='0', flagbackup=False, field = field, scan = '38,40', antenna = 'DV02')
flagdata(vis=SB2_CO_ms,mode='manual', spw='1', flagbackup=False, field = field, scan = '59', antenna = 'DA62,DV05,DV12')
flagdata(vis = SB2_CO_ms, mode='manual', spw='1', flagbackup=False, field = field, antenna = 'DA63')
flagdata(vis=SB2_CO_ms,mode='manual', spw='2', flagbackup=False, field = field, scan = '76, 78,84, 86')
flagdata(vis=SB2_CO_ms,mode='manual', spw='2', flagbackup=False, field = field, scan = '68,70', antenna = 'DA46&DA55;DA59&DA49;DA59&DV18;DA60&DV05;DA43&DV05')
flagdata(vis=SB2_CO_ms,mode='manual', spw='2', flagbackup=False, field = field, timerange = '2015/08/09/01:18:20~2015/08/09/01:21:00')


applycal(vis=SB2_CO_ms, spw='0~2',spwmap = [[0,0,0],[0,0,0],[0,0,0]], gaintable=[SB2_p1, SB2_p2, SB2_ap1], calwt=T, flagbackup=F)

plotms(vis = SB2_CO_ms, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True, avgscan = True)

SB2_CO_mscontsub = SB2_CO_ms+'.contsub'
os.system('rm -rf '+SB2_CO_mscontsub) 
fitspw = '0:0~1000;3000~3839, 1:0~1000;3000~3839, 2:0~1000;3000~3839' # channels for fitting continuum
uvcontsub(vis=SB2_CO_ms,
          spw='0~2', 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=1,
          want_cont=False) 

plotms(vis = SB2_CO_mscontsub, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)

SB2_CO_cvel = SB2_CO_mscontsub+'.cvel'

os.system('rm -rf '+ SB2_CO_cvel)
mstransform(vis = SB2_CO_mscontsub, outputvis = SB2_CO_cvel,keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='-15km/s',width='0.35km/s',nchan=120, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

#check individual observation
SB2_CO_image = field+'_'+tag+'_CO21cube'
os.system('rm -rf '+SB2_CO_image+'.*')
clean(vis=SB2_CO_cvel, 
      imagename=SB2_CO_image,
      mode = 'velocity',
      psfmode = 'clark',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 30, 50,100],
      robust = 1.0,
      gain = 0.3, 
      imsize = 750,
      cell = '0.03arcsec',
      start='-15km/s',
      width='0.35km/s',
      nchan=120, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '6mJy',
      interactive=True) 


clean(vis=[SB1_CO_averaged, SB2_CO_cvel], 
      imagename='HD_163296_COcombined',
      mode = 'velocity',
      psfmode = 'clark',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 30, 50,100],
      robust = 0.0,
      gain = 0.1, 
      imsize = 750,
      cell = '0.03arcsec',
      start='-15km/s',
      width='0.35km/s',
      nchan=120, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '5mJy',
      mask = 'HD_163296_SB2_CO21cube.mask', 
      interactive=True) 

