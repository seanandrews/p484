"""
This script is written for CASA 4.5.3
Note that the imaging algorithms were rewritten significantly between 
CASA 4.5.3 and CASA 4.7.2 
Datasets calibrated: 
2016.1.00484.L/AS_205_b_06_TM1 (PI: Andrews)
"""

field = 'AS_205'

##################################################################
##################################################################
## short baseline data
##################################################################
##################################################################

SB1 = '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_Xbd4641_X1e/group.uid___A001_Xbd4641_X25/member.uid___A001_Xbd4641_X26/calibrated/calibrated_final.ms'
SB1refant = 'DA46'
tag = 'SB1'

#split out all the data from the given field
SB1_field = field+'_'+tag+'.ms'
print(SB1_field) 
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


# spws 0, 4, 8 contain the CO 2-1 line
contspws = '0~11'
flagmanager(vis=SB1_field,mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
flagchannels='0:1880~2250, 4:1880~2250, 8:1880~2250' #1880 to 1950 would have been fine 

flagdata(vis=SB1_field,mode='manual', spw=flagchannels, flagbackup=False, field = field)

# Average the channels within spws
SB1_initcont = field+'_'+tag+'_initcont.ms'
print(SB1_initcont)
os.system('rm -rf ' + SB1_initcont + '*')
split2(vis=SB1_field,
       field = field,
       spw=contspws,      
       outputvis=SB1_initcont,
       width=[480,8,8,8, 480, 8, 8, 8, 480, 8, 8, 8], 
       datacolumn='data')


# Restore flagged line channels
flagmanager(vis=SB1_field,mode='restore',
            versionname='before_cont_flags')

# Check that amplitude vs. uvdist looks normal
plotms(vis=SB1_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30')

# Inspect individual antennae. We do this step here rather than before splitting because plotms will load the averaged continuum much faster 
plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '0',
       coloraxis = 'spw', iteraxis = 'antenna')

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '1',
       coloraxis = 'spw', iteraxis = 'antenna')

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '0', 
       coloraxis = 'spw', iteraxis = 'antenna') 

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '1', 
       coloraxis = 'spw', iteraxis = 'antenna') 

# check individual execution blocks
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
# all look consistent

# Initial clean
SB1_initcontimage = field+'_'+tag+'_initcontinuum'
os.system('rm -rf '+SB1_initcontimage+'.*')
clean(vis=SB1_initcont, 
      imagename=SB1_initcontimage, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 20, 30], 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask=['circle[[265pix,210pix],0.8arcsec]', 
            'circle[[292pix,175pix],0.8arcsec]'],
      interactive=True)

# cleaned for 2 cycles (200 iterations)
# peak: 98.4 mJy/beam
# rms: 226 microJy/beam

# First phase-self-cal
SB1_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB1_p1)
gaincal(vis=SB1_initcont, caltable=SB1_p1, gaintype='T',  
        spw=contspws, refant=SB1refant, calmode='p', 
        solint='25s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2017/05/14/00:00:01~2017/05/14/11:59:59')

plotcal(caltable=SB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2017/05/17/00:00:01~2017/05/17/11:59:59')

plotcal(caltable=SB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2017/05/19/00:00:01~2017/05/19/11:59:59')


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
      multiscale = [0, 10, 20, 30], 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask=['circle[[265pix,210pix],0.8arcsec]', 
            'circle[[292pix,175pix],0.8arcsec]'],
      interactive=True)

# cleaned for 4 cycles with 100 iterations each
# peak: 105.7 mJy/beam
# rms: 96.0 microJy/beam

# Second round of phase cal didn't result in any noticeable improvement, so we move on to amplitude self-cal


SB1_ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+SB1_ap1)
gaincal(vis=SB1_contms_p1, caltable=SB1_ap1, gaintype='T',  
        spw=contspws, refant=SB1refant, calmode='ap', 
        solint='60s', minsnr=2.0, minblperant=4, solnorm = True)

plotcal(caltable=SB1_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = '2017/05/14/00:00:01~2017/05/14/11:59:59')

plotcal(caltable=SB1_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = '2017/05/17/00:00:01~2017/05/17/11:59:59')

plotcal(caltable=SB1_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = '2017/05/19/00:00:01~2017/05/19/11:59:59')


applycal(vis=SB1_contms_p1, spw=contspws, gaintable=[SB1_ap1], calwt=T, flagbackup=F)

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
      multiscale = [0, 10, 20, 30], 
      robust=0.5,
      gain = 0.3,
      imsize=500,
      cell='0.03arcsec', 
      mask=['circle[[265pix,210pix],0.8arcsec]',
            'circle[[292pix,175pix],0.8arcsec]'],
      interactive=True)

# cleaned for 4 cycles of 100 iterations each
# peak: 32.5 mJy/beam
# rms: 45.4 microJy/beam

### We are now done with self-cal of the continuum of SB1 and rename the final measurement set. 
SB1_contms_final = field+'_'+tag+'_contfinal.ms'
os.system('cp -r '+SB1_contms_ap1+' '+SB1_contms_final)


# pushing the resolution
SB1_contimage_ap1 = field+'_'+tag+'_ap1continuum_highres'
os.system('rm -rf '+SB1_contimage_ap1+'.*')
clean(vis=SB1_contms_ap1,
      imagename=SB1_contimage_ap1,
      mode='mfs',
      psfmode='clark',
      imagermode='csclean',
      weighting='briggs',
      multiscale = [0, 10, 20, 30], 
      robust=-2.0,
      gain = 0.3,
      imsize=500,
      cell='0.02arcsec',
      mask='circle[[251pix,234pix],1.8arcsec]',
      interactive=True)

##############################
# Reduction of CO data in SB1
#############################



applycal(SB1_field, gaintable=[SB1_p1, SB1_ap1], calwt=T, flagbackup=F)

#split out the CO 2-1 spectral window
linespw = '0, 4, 8'
SB1_CO_ms = field+'_'+tag+'_CO21.ms'
os.system('rm -rf ' + SB1_CO_ms + '*')
split2(vis=SB1_field,
       field = field,
       spw=linespw,      
       outputvis=SB1_CO_ms, 
       datacolumn='corrected')

plotms(vis = SB1_CO_ms, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)

SB1_CO_mscontsub = SB1_CO_ms+'.contsub'
os.system('rm -rf '+SB1_CO_mscontsub) 
fitspw = '0:0~1880;1950~3839, 1:0~1880;1950~3839, 2:0~1880; 1950~3839' # channels for fitting continuum
uvcontsub(vis=SB1_CO_ms,
          spw='0~2', 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=1,
          want_cont=False) 

plotms(vis = SB1_CO_mscontsub, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)


CO_cvel = SB1_CO_mscontsub+'.cvel'

os.system('rm -rf '+ CO_cvel)
mstransform(vis = SB1_CO_mscontsub, outputvis = CO_cvel,  keepflags = False,datacolumn = 'data', regridms = True,mode='velocity',start='-9km/s',width='0.35km/s',nchan=60, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

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
      start='-9km/s',
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
## 2011.0.00531.S/uid://A002/X391d0b/X5e (downloaded from archive)
##################################################################
#################################################################

field = 'AS_205' 
tag = 'SB2'
SB2refant = 'DV12'

SB2_ms1 = 'uid___A002_X3b3400_Xcd7.ms.split.cal'
SB2_ms2 = 'uid___A002_X3f6a86_X5da.ms.split.cal'

SB2_field_ms1 = field+'_'+tag+'_exec1.ms'
os.system('rm -rf ' + SB2_field_ms1 + '*')
split2(vis=SB2_ms1,
       field = 'V866 Sco', #name for AS 205 in the measurement set    
       spw = '0~1',  
       outputvis=SB2_field_ms1,
       datacolumn='data')

SB2_field_ms2 = field+'_'+tag+'_exec2.ms'
os.system('rm -rf ' + SB2_field_ms2 + '*')
split2(vis=SB2_ms2,
       field = 'V866 Sco',   
       spw = '0~1',  
       outputvis=SB2_field_ms2,
       datacolumn='data')


#need to adjust weights since this is from Cycle 0
#excluding CO 2-1 emission 
statwt(vis=SB2_field_ms1 , fitspw='0:0~2600;3200~3839,1:0~3839', datacolumn='data')
statwt(vis=SB2_field_ms2 , fitspw='0:0~2200;2900~3839,1:0~3839', datacolumn='data')

SB2_field = field+'_'+tag+'.ms'
os.system('rm -rf ' + SB2_field)
concat(vis = [SB2_field_ms1, SB2_field_ms2], concatvis = SB2_field, freqtol = '0MHz', copypointing = False)

#changing the field name inside the measurement set
tb.open(SB2_field+'/FIELD',nomodify=False)
st=tb.selectrows(0)
st.putcol('NAME','AS_205')
st.done()
tb.close()

flagmanager(vis=SB2_field,mode='save', versionname='before_cont_flags')

#the SPWs were merged by concat
flagdata(vis=SB2_field,mode='manual', spw='0:0~400;2600~3200, 1:0~500', flagbackup=False, field = field, observation = 0)
flagdata(vis=SB2_field,mode='manual', spw='0:0~300;2200~2900, 1:0~600', flagbackup=False, field = field, observation = 1)

contspws = '0~1'
# Average the channels within spws
SB2_initcont = field+'_'+tag+'_initcont.ms'
print(SB2_initcont)
os.system('rm -rf ' + SB2_initcont + '*')
split2(vis=SB2_field,
       field = field,
       spw=contspws,      
       outputvis=SB2_initcont,
       width=3840, 
       datacolumn='data')

# Check that amplitude vs. uvdist looks normal
plotms(vis=SB2_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30')

# Inspect individual antennae. We do this step here rather than before splitting because plotms will load the averaged continuum much faster 
plotms(vis = SB2_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '0',
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

SB2_EB1_initcontimage = field+'_'+tag+'_EB1_initcontinuum'
os.system('rm -rf '+SB2_EB1_initcontimage+'.*')
clean(vis=SB2_initcont, 
      imagename=SB2_EB1_initcontimage, 
      observation = '0', 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      robust=0.5,
      imsize=500,
      cell='0.05arcsec', 
      interactive=True)

SB2_EB2_initcontimage= field+'_'+tag+'_EB2_initcontinuum'
os.system('rm -rf '+SB2_EB2_initcontimage+'.*')
clean(vis=SB2_initcont, 
      imagename=SB2_EB2_initcontimage, 
      observation = '1', 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      robust=0.5,
      imsize=500,
      cell='0.05arcsec', 
      interactive=True)

#start of self-calibration with model from higher S/N AS 205 observations

ft(vis = SB2_initcont, model = 'AS_205_SB1_ap1continuum.model') 

# First phase-self-cal
SB2_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB2_p1)
gaincal(vis=SB2_initcont, caltable=SB2_p1, gaintype='T', combine = 'spw', 
        spw='0~1', refant=SB2refant, calmode='p', 
        solint='int', minsnr=2.0, minblperant=4)

plotcal(caltable=SB2_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2012/03/27/00:00:01~2012/03/27/11:59:59')
plotcal(caltable=SB2_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2012/05/04/00:00:01~2012/05/04/11:59:59')

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
      robust=0.5,
      gain = 0.1,
      imsize=500,
      cell='0.05arcsec', 
      mask=['circle[[260pix,223pix],1.0arcsec]', 
            'circle[[275pix,203pix],0.8arcsec]'],
      interactive=True)

# cleaned for 2 cycles of 100 iterations each
# peak: 28.5 mJy/beam
# rms: 0.82 mJy/beam


SB2_ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+SB2_ap1)
gaincal(vis=SB2_contms_p1, caltable=SB2_ap1, gaintype='T', 
        spw='0~1', refant=SB2refant, calmode='ap', 
        solint='60s', minsnr=2.0, minblperant=4, solnorm = True)

plotcal(caltable=SB2_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna',timerange = '2012/03/27/00:00:01~2012/03/27/11:59:59')
plotcal(caltable=SB2_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna',timerange = '2012/05/04/00:00:01~2012/05/04/11:59:59')

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
      robust=0.5,
      gain = 0.1,
      imsize=500,
      cell='0.05arcsec', 
      mask=['circle[[260pix,223pix],1.0arcsec]', 
            'circle[[275pix,203pix],0.8arcsec]'],
      interactive=True)

# cleaned for 3 cycles of 100 iterations each
# peak: 28.7 mJy/beam
# rms: 0.54 mJy/beam

### We are now done with self-cal of the continuum of SB1 and rename the final measurement set. 
SB2_contms_final = field+'_'+tag+'_contfinal.ms'
os.system('cp -r '+SB2_contms_ap1+' '+SB2_contms_final)

##############################
# Reduction of CO data in SB2
#############################

applycal(SB2_field, gaintable=[SB2_p1, SB2_ap1], calwt=T, flagbackup=F)


#split out the CO 2-1 spectral window
linespw = '0'
SB2_CO_ms = field+'_'+tag+'_CO21.ms'
os.system('rm -rf ' + SB2_CO_ms + '*')
split2(vis=SB2_field,
       field = field,
       spw=linespw,      
       outputvis=SB2_CO_ms, 
       datacolumn='corrected')

plotms(vis = SB2_CO_ms, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)

SB2_CO_mscontsub = SB2_CO_ms+'.contsub'
os.system('rm -rf '+SB2_CO_mscontsub) 
fitspw = '0:600~2200;3200~3839' # channels for fitting continuum
uvcontsub(vis=SB2_CO_ms,
          spw='0', 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=1,
          want_cont=False) 

plotms(vis = SB2_CO_mscontsub, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)


SB2_CO_cvel = SB2_CO_mscontsub+'.cvel'

os.system('rm -rf '+ SB2_CO_cvel)
mstransform(vis = SB2_CO_mscontsub, outputvis = CO_cvel,  keepflags = False,datacolumn = 'data', regridms = True,mode='velocity',start='-9km/s',width='0.35km/s',nchan=60, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

SB2_CO_image = field+'_'+tag+'_CO21cube'
os.system('rm -rf '+SB2_CO_image+'.*')
clean(vis=CO_cvel, 
      imagename=SB2_CO_image,
      mode = 'velocity',
      psfmode = 'clark',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 30, 50],
      robust = 1.0,
      gain = 0.1, 
      imsize = 500,
      cell = '0.05arcsec',
      start='-9km/s',
      width='0.35km/s',
      nchan=60, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '20mJy',
      interactive=True) 

