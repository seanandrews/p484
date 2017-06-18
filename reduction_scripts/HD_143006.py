"""
This script is written for CASA 4.5.3
Note that the imaging algorithms were rewritten significantly between CASA 4.5.3 and CASA 4.7.2 

Datasets calibrated: 2016.1.00484.L/AS_205_b_06_TM1
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


plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '1',
       coloraxis = 'spw', iteraxis = 'antenna')

flagdata(vis=SB1_initcont,mode='manual', spw='10', flagbackup=False, field = field, scan = '169, 177', antenna = 'DV15')


plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '0', 
       coloraxis = 'spw', iteraxis = 'antenna') 

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
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
