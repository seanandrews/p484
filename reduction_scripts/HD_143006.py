"""
This script is written for CASA 4.5.3
Note that the imaging algorithms were rewritten significantly between CASA 4.5.3 and CASA 4.7.2 

Datasets calibrated: 
2016.1.00484.L/AS_205_b_06_TM1 (PI: Andrews)
2015.1.00964.S/HD143006_a_06_TE (PI: Oberg)
2015.1.00964.S/HD143006_a_06_TC (PI: Oberg)
"""


##################################################################
##################################################################
## 2016.1.00484.L/AS_205_b_06_TM1 (as delivered to PI)
##################################################################
##################################################################

SB1 = 'calibrated_final.ms' #replace as appropriate
SB1refant = 'DV15, DA59'
tag = 'SB1'
field = 'HD_143006'

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


# spws 0, 4, and 8 contains the CO 2-1 line, while the others are continuum SPWs
contspws = '0~11'
flagmanager(vis=SB1_field,mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
flagchannels='0:1860~2000, 4:1860~2000, 8:1860~2000' #modify as appropriate for the given field

flagdata(vis=SB1_field,mode='manual', spw=flagchannels, flagbackup=False, field = field)

# Average the channels within spws
SB1_initcont = field+'_'+tag+'_initcont.ms'
print SB1_initcont #just to double check for yourself that the name is actually ok
os.system('rm -rf ' + SB1_initcont + '*')
split2(vis=SB1_field,
       field = field,
       spw=contspws,      
       outputvis=SB1_initcont,
       width=[480,8,8,8, 480, 8, 8, 8, 480, 8, 8, 8], # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
       datacolumn='data')


# Restore flagged line channels
flagmanager(vis=SB1_field,mode='restore',
            versionname='before_cont_flags')

# Check that amplitude vs. uvdist looks normal
plotms(vis=SB1_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30s',avgscan = True)

# Inspect individual antennae. We do this step here rather than before splitting because plotms will load the averaged continuum much faster 

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '0',
       coloraxis = 'spw', iteraxis = 'antenna')


plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '1',
       coloraxis = 'spw', iteraxis = 'antenna')

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '2',
       coloraxis = 'spw', iteraxis = 'antenna')

flagdata(vis=SB1_initcont,mode='manual', spw='10', flagbackup=False, field = field, scan = '169, 177', antenna = 'DV15')


plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '0', 
       coloraxis = 'spw', iteraxis = 'antenna') 

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '1', 
       coloraxis = 'spw', iteraxis = 'antenna') 

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '2', 
       coloraxis = 'spw', iteraxis = 'antenna') 

# check the individual execution blocks
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

SB1_EB3_initcontimage_dirty = field+'_'+tag+'_EB3_initcontinuum_dirty'
os.system('rm -rf '+SB1_EB3_initcontimage_dirty+'.*')
clean(vis=SB1_initcont, 
      imagename=SB1_EB3_initcontimage_dirty, 
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
      mask='circle[[250pix,250pix],1.0arcsec]',
      interactive=True)

# cleaned for 2 cycles (100 iterations each)
# peak: 7.0 mJy/beam
# rms: 51 microJy/beam

# First phase-self-cal
SB1_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB1_p1)
#combining SPWs because of relatively weak continuum
gaincal(vis=SB1_initcont, caltable=SB1_p1, gaintype='T', combine = 'spw', 
        spw=contspws, refant=SB1refant, calmode='p', 
        solint='25s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2017/05/14/00:00:01~2017/05/14/11:59:59')


plotcal(caltable=SB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2017/05/17/00:00:01~2017/05/17/11:59:59')

plotcal(caltable=SB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2017/05/19/00:00:01~2017/05/19/11:59:59')

applycal(vis=SB1_initcont, spw=contspws, spwmap = [0]*12, gaintable=[SB1_p1], calwt=T, flagbackup=F)

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
      mask='circle[[250pix,250pix],1.0arcsec]',
      interactive=True)

# cleaned for 3 cycles with 100 iterations each 
# peak: 7.7 mJy/beam
# rms: 34 microJy/beam


# Second phase self-cal 

SB1_p2 = field+'_'+tag+'.p2'
os.system('rm -rf '+SB1_p2)
gaincal(vis=SB1_contms_p1, caltable=SB1_p2, gaintype='T', combine = 'spw', 
        spw=contspws, refant=SB1refant, calmode='p', 
        solint='20s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB1_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2017/05/14/00:00:01~2017/05/14/11:59:59')

plotcal(caltable=SB1_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2017/05/17/00:00:01~2017/05/17/11:59:59')

plotcal(caltable=SB1_p2, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2017/05/19/00:00:01~2017/05/19/11:59:59')

applycal(vis=SB1_contms_p1, spw=contspws, spwmap = [0]*12, gaintable=[SB1_p2], calwt=T, flagbackup=F)

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
      multiscale = [0, 10, 20, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[250pix,250pix],1.0arcsec]',
      interactive=True)

# cleaned for 3 cycles of 100 iterations each
# peak: 7.7 mJy/beam
# rms: 34 microJy/beam


# difference is small, so we move on to amplitude self-cal

SB1_ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+SB1_ap1)
gaincal(vis=SB1_contms_p2, caltable=SB1_ap1, gaintype='T', combine = 'spw',   
        spw=contspws, refant=SB1refant, calmode='ap', 
        solint='60s', minsnr=2.0, minblperant=4, solnorm = True)

plotcal(caltable=SB1_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = '2017/05/14/00:00:01~2017/05/14/11:59:59')

plotcal(caltable=SB1_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = '2017/05/17/00:00:01~2017/05/17/11:59:59')

plotcal(caltable=SB1_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = '2017/05/19/00:00:01~2017/05/19/11:59:59')

applycal(vis=SB1_contms_p2, spw=contspws, spwmap = [0]*12, gaintable=[SB1_ap1], calwt=T, flagbackup=F)

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
      multiscale = [0, 10, 20, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[250pix,250pix],1.0arcsec]',
      interactive=True)

# cleaned for 3 cycles of 100 iterations each
# peak: 7.6 mJy/beam
# rms: 29 microJy/beam

SB1_contimage_uniform = field+'_'+tag+'_uniform'
os.system('rm -rf '+SB1_contimage_uniform+'.*')
clean(vis=SB1_contms_ap1, 
      imagename=SB1_contimage_uniform, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 20, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=-2,
      gain = 0.05,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[250pix,250pix],1.0arcsec]',
      interactive=True)

### We are now done with self-cal of the continuum of SB1 and rename the final measurement set. 
SB1_contms_final = field+'_'+tag+'_contfinal.ms'
os.system('cp -r '+SB1_contms_ap1+' '+SB1_contms_final)

##############################
# Reduction of CO data in SB1
#############################

#split out the CO 2-1 spectral window
linespw = '0,4,8'
SB1_CO_ms = field+'_'+tag+'_CO21.ms'
os.system('rm -rf ' + SB1_CO_ms + '*')
split2(vis=SB1,
       field = field,
       spw=linespw,      
       outputvis=SB1_CO_ms, 
       datacolumn='data')

applycal(vis=SB1_CO_ms, spw='0~2',spwmap = [[0,0,0],[0,0,0],[0,0,0]], gaintable=[SB1_p1, SB1_p2, SB1_ap1], calwt=T, flagbackup=F)

plotms(vis = SB1_CO_ms, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)

SB1_CO_mscontsub = SB1_CO_ms+'.contsub'
os.system('rm -rf '+SB1_CO_mscontsub) 
fitspw = '0:0~1860;2000~3839, 1:0~1860;2000~3839, 2:0~1860;2000~3839' # channels for fitting continuum
uvcontsub(vis=SB1_CO_ms,
          spw='0~2', 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=1,
          want_cont=False) 

plotms(vis = SB1_CO_mscontsub, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)

SB1_CO_cvel = SB1_CO_mscontsub+'.cvel'

os.system('rm -rf '+ SB1_CO_cvel)
mstransform(vis = SB1_CO_mscontsub, outputvis = SB1_CO_cvel,  keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='-1.0km/s',width='0.35km/s',nchan=60, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

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
      start='-1.0km/s',
      width='0.35km/s',
      nchan=60, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '6mJy',
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
## 2015.1.00964.S/HD143006_a_06_TE (as delivered to PI)
##################################################################
##################################################################

SB2 = 'HD143006_calibrated.ms' #replace as appropriate
SB2refant = 'DV11'
tag = 'SB2'
field = 'HD143006'

# initial inspection of data before splitting out and averaging the continuum

plotms(vis = SB2, xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')

contspws = '0,1,2,9,10,11' #all the upper sideband windows

flagmanager(vis=SB2,mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
flagchannels='0:450~550, 9:450~550' #modify as appropriate for the given field

flagdata(vis=SB2,mode='manual', spw=flagchannels, flagbackup=False, field = field)

# Average the channels within spws
SB2_initcont = field+'_'+tag+'_initcont.ms'
print SB2_initcont #just to double check for yourself that the name is actually ok
os.system('rm -rf ' + SB2_initcont + '*')
split2(vis=SB2,
       field = field,
       spw=contspws,      
       outputvis=SB2_initcont,
       width=[960,960,256, 960,960,256], # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
       datacolumn='data')


# Restore flagged line channels
flagmanager(vis=SB2,mode='restore',
            versionname='before_cont_flags')

# Check that amplitude vs. uvdist looks normal
plotms(vis=SB2_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30s',avgscan = True)

# Inspect individual antennae. We do this step here rather than before splitting because plotms will load the averaged continuum much faster 

plotms(vis = SB2_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '15', observation = '0',
       coloraxis = 'spw', iteraxis = 'antenna')


plotms(vis = SB2_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '1',
       coloraxis = 'spw', iteraxis = 'antenna')

plotms(vis = SB2_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '0', 
       coloraxis = 'spw', iteraxis = 'antenna') 

plotms(vis = SB2_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '1', 
       coloraxis = 'spw', iteraxis = 'antenna') 

# check individual execution blocks
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
      cell='0.05arcsec', 
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
      cell='0.05arcsec', 
      interactive=False, 
      niter = 0)

#start of self-calibration with model from higher S/N HD 143006 observations

ft(vis = SB2_initcont, model = 'HD_143006_SB1_ap1continuum.model') 

# First phase-self-cal
SB2_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB2_p1)
gaincal(vis=SB2_initcont, caltable=SB2_p1, gaintype='T', combine = 'spw', 
        spw='0~5', refant=SB2refant, calmode='p', 
        solint='45s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB2_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna')

applycal(vis=SB2_initcont, spw='0~5', spwmap = 6*[0], gaintable=[SB2_p1], calwt=T, flagbackup=F)

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
      multiscale = [0, 10, 20, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='circle[[250pix,250pix],1.1arcsec]',
      interactive=True)

# cleaned for 2 cycles of 100 iterations each
# peak: 22.2 mJy/beam
# rms: 68.9 microJy/beam


SB2_ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+SB2_ap1)
gaincal(vis=SB2_contms_p1, caltable=SB2_ap1, gaintype='T', combine = 'spw', 
        spw='0~5', refant=SB2refant, calmode='ap', 
        solint='inf', minsnr=2.0, minblperant=4, solnorm = True)

plotcal(caltable=SB2_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna')

applycal(vis=SB2_contms_p1, spw='0~5', spwmap = 6*[0], gaintable=[SB2_ap1], calwt=T, flagbackup=F)

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
      multiscale = [0, 10, 20, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='circle[[250pix,250pix],1.1arcsec]',
      interactive=True)

# cleaned for 2 cycles of 100 iterations each
# peak: 22.2 mJy/beam
# rms: 65.6 microJy/beam

##############################
# Reduction of CO data in SB2
#############################

#split out the CO 2-1 spectral window
linespw = '0,9'
SB2_CO_ms = field+'_'+tag+'_CO21.ms'
os.system('rm -rf ' + SB2_CO_ms + '*')
split2(vis=SB2,
       field = field,
       spw=linespw,      
       outputvis=SB2_CO_ms, 
       datacolumn='data')

applycal(vis=SB2_CO_ms, spw='0~1',spwmap = [[0,0],[0,0]], gaintable=[SB2_p1, SB2_ap1], calwt=T, flagbackup=F)

plotms(vis = SB2_CO_ms, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)

SB2_CO_mscontsub = SB2_CO_ms+'.contsub'
os.system('rm -rf '+SB2_CO_mscontsub) 
fitspw = '0:200~450;550~959,1:200~450;550~959' # channels from 0 to 200 don't look great
uvcontsub(vis=SB2_CO_ms,
          spw='0~1', 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=0,
          want_cont=False) 

plotms(vis = SB2_CO_mscontsub, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)

SB2_CO_cvel = SB2_CO_mscontsub+'.cvel'

os.system('rm -rf '+ SB2_CO_cvel)
mstransform(vis = SB2_CO_mscontsub, outputvis = SB2_CO_cvel,  keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='-1.0km/s',width='0.35km/s',nchan=60, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')


#check individual observation
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
      start='-1.0km/s',
      width='0.35km/s',
      nchan=60, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '7mJy',
      interactive=True) 


SB2_CO_cvel_hires = SB2_CO_mscontsub+'_hires.cvel'

os.system('rm -rf '+ SB2_CO_cvel_hires)
mstransform(vis = SB2_CO_mscontsub, outputvis = SB2_CO_cvel_hires,  keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='-1.0km/s',width='0.2km/s',nchan=80, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

##################################################################
##################################################################
## 2015.1.00964.S/HD143006_a_06_TC (downloaded from archive)
##################################################################
##################################################################

SB3 = '/pool/firebolt1/HD143006_TC.ms' #replace as appropriate
SB3refant = 'DV16'
tag = 'SB3'
field = 'HD143006'

# initial inspection of data before splitting out and averaging the continuum

plotms(vis = SB3, xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')

contspws = '0,1,2' #all the upper sideband windows

flagmanager(vis=SB3,mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
flagchannels='0:100~200, 0:450~550' #modify as appropriate for the given field

flagdata(vis=SB3,mode='manual', spw=flagchannels, flagbackup=False, field = field)

# Average the channels within spws
SB3_initcont = field+'_'+tag+'_initcont.ms'
print SB3_initcont #just to double check for yourself that the name is actually ok
os.system('rm -rf ' + SB3_initcont + '*')
split2(vis=SB3,
       field = field,
       spw=contspws,      
       outputvis=SB3_initcont,
       width=[960,960,256], # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
       datacolumn='data')

# Restore flagged line channels
flagmanager(vis=SB3,mode='restore',
            versionname='before_cont_flags')

# Check that amplitude vs. uvdist looks normal
plotms(vis=SB3_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30s',avgscan = True)

# Inspect individual antennae. We do this step here rather than before splitting because plotms will load the averaged continuum much faster 

plotms(vis = SB3_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '15', observation = '0',
       coloraxis = 'spw', iteraxis = 'antenna')


plotms(vis = SB3_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '0', 
       coloraxis = 'spw', iteraxis = 'antenna') 

#start of self-calibration with model from higher S/N HD 143006 observations

ft(vis = SB3_initcont, model = 'HD_143006_SB1_ap1continuum.model') 

# First phase-self-cal
SB3_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB3_p1)
gaincal(vis=SB3_initcont, caltable=SB3_p1, gaintype='T', combine = 'spw', 
        spw='0~2', refant=SB3refant, calmode='p', 
        solint='45s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB3_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna')

applycal(vis=SB3_initcont, spw='0~2', spwmap = 3*[0], gaintable=[SB3_p1], calwt=T, flagbackup=F)

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
      multiscale = [0, 10, 20, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='circle[[250pix,250pix],1.1arcsec]',
      interactive=True)

# cleaned for 2 cycles of 100 iterations each
# peak: 21.6 mJy/beam
# rms: 76.9 microJy/beam


SB3_ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+SB3_ap1)
gaincal(vis=SB3_contms_p1, caltable=SB3_ap1, gaintype='T', combine = 'spw', 
        spw='0~2', refant=SB3refant, calmode='ap', 
        solint='inf', minsnr=2.0, minblperant=4, solnorm = True)

plotcal(caltable=SB3_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna')

applycal(vis=SB3_contms_p1, spw='0~2', spwmap = 3*[0], gaintable=[SB3_ap1], calwt=T, flagbackup=F)

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
      multiscale = [0, 10, 20, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.05arcsec', 
      mask='circle[[250pix,250pix],1.1arcsec]',
      interactive=True)

# cleaned for 2 cycles of 100 iterations each
# peak: 21.6 mJy/beam
# rms: 72.5 microJy/beam

##############################
# Reduction of CO data in SB3
#############################

#split out the CO 2-1 spectral window
linespw = '0'
SB3_CO_ms = field+'_'+tag+'_CO21.ms'
os.system('rm -rf ' + SB3_CO_ms + '*')
split2(vis=SB3,
       field = field,
       spw=linespw,      
       outputvis=SB3_CO_ms, 
       datacolumn='data')

applycal(vis=SB3_CO_ms, spw='0', gaintable=[SB3_p1, SB3_ap1], calwt=T, flagbackup=F)

plotms(vis = SB3_CO_ms, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)

SB3_CO_mscontsub = SB3_CO_ms+'.contsub'
os.system('rm -rf '+SB3_CO_mscontsub) 
fitspw = '0:200~450;550~959' # channels from 0 to 200 don't look great
uvcontsub(vis=SB3_CO_ms,
          spw='0', 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=0,
          want_cont=False) 

plotms(vis = SB3_CO_mscontsub, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)

SB3_CO_cvel = SB3_CO_mscontsub+'.cvel'

os.system('rm -rf '+ SB3_CO_cvel)
mstransform(vis = SB3_CO_mscontsub, outputvis = SB3_CO_cvel,  keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='-1.0km/s',width='0.35km/s',nchan=60, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')


#check individual observation
SB3_CO_image = field+'_'+tag+'_CO21cube'
os.system('rm -rf '+SB3_CO_image+'.*')
clean(vis=SB3_CO_cvel, 
      imagename=SB3_CO_image,
      mode = 'velocity',
      psfmode = 'clark',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 30, 50],
      robust = 1.0,
      gain = 0.3, 
      imsize = 500,
      cell = '0.05arcsec',
      start='-1.0km/s',
      width='0.35km/s',
      nchan=60, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '10mJy',
      interactive=True) 


SB3_CO_cvel_hires = SB3_CO_mscontsub+'_hires.cvel'

os.system('rm -rf '+ SB3_CO_cvel_hires)
mstransform(vis = SB3_CO_mscontsub, outputvis = SB3_CO_cvel_hires,  keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='-1.0km/s',width='0.2km/s',nchan=80, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

########## Data combinations

# concatenate all short baseline continuum observations

concat(vis = [SB1_contms_ap1,SB2_contms_ap1,SB3_contms_ap1], concatvis = 'HD_143006_allSB_cont.ms', freqtol = '20MHz', dirtol = '0.1arcsec', respectname = False, copypointing = False)



clean(vis='HD_143006_allSB_cont.ms', 
      imagename='HD143006_combinedcont', 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 20, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=-2,
      gain = 0.05,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[250pix,250pix],1.0arcsec]',
      interactive=True)

#currently have a helpdesk ticket pending because of problems with MS incompatibility....

clean(vis=['HD143006_SB2_contap1.ms', 'HD143006_SB3_contap1.ms'] , 
      imagename='HD143006_combinedcont', 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 20, 30], # this is really up to the user. The choices here matter less than they do for the extended data. 
      robust=-2,
      gain = 0.05,
      imsize=500,
      cell='0.03arcsec', 
      mask='circle[[250pix,250pix],1.0arcsec]',
      interactive=True)

os.system('rm -rf HD143006_CO_combined.*')
clean(vis=[SB1_CO_cvel,SB2_CO_cvel,SB3_CO_cvel], 
      imagename='HD143006_CO_combined',
      mode = 'velocity',
      psfmode = 'clark',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 30, 50],
      robust = 1.0,
      gain = 0.3, 
      imsize = 500,
      cell = '0.03arcsec',
      start='-1.0km/s',
      width='0.35km/s',
      nchan=60, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '6mJy',
      mask = 'HD_143006_SB1_CO21cube.mask', 
      interactive=True) 

os.system('rm -rf HD143006_CO_combined.mom0')
immoments(axis = "spec",imagename='HD143006_CO_combined.image',moments=[0],outfile ='HD143006_CO_combined.mom0', chans = '6~45')

os.system('rm -rf HD143006_CO_combined.mom1')
immoments(axis = "spec",imagename='HD143006_CO_combined.image',moments=[1],outfile ='HD143006_CO_combined.mom1', chans = '6~45', includepix = [.01, 10])

os.system('rm -rf HD143006_CO_spectralhires.*')
clean(vis=[SB2_CO_cvel_hires, SB3_CO_cvel_hires], 
      imagename='HD143006_CO_spectralhires',
      mode = 'velocity',
      psfmode = 'clark',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 30, 50],
      robust = 1.0,
      gain = 0.3, 
      imsize = 500,
      cell = '0.05arcsec',
      start='-1.0km/s',
      width='0.2km/s',
      nchan=80, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '5mJy',
      interactive=True) 

immoments(axis = "spec",imagename='HD143006_CO_spectralhires.image',moments=[0],outfile ='HD143006_CO_spectralhires.mom0', chans = '15~70')
immoments(axis = "spec",imagename='HD143006_CO_spectralhires.image',moments=[1],outfile ='HD143006_CO_spectralhires.mom1', chans = '15~70', includepix = [.025, 10])

#immoments(axis = "spec",imagename='HD143006_CO_spectralhighres.image',moments=[0],outfile ='HD143006_CO_spectralhighres.mom0', chans = '11~42')

#immoments(axis = "spec",imagename='HD143006_CO_spectralhighres.image',moments=[1],outfile ='HD143006_CO_spectralhighres.mom1', chans = '11~42', includepix = [.02, 10])




 

