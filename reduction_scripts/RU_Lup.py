"""
This script is written for CASA 4.5.3
Note that the imaging algorithms were rewritten significantly between 
CASA 4.5.3 and CASA 4.7.2 

Datasets calibrated: 
2016.1.00484.L/GW_Lup_a_06_TM1  (PI: Andrews)
"""

field = 'RU_Lup'

##################################################################
##################################################################
## short baseline data
##################################################################
##################################################################

SB1 = '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_Xbd4641_X1e/group.uid___A001_Xbd4641_X1f/member.uid___A001_Xbd4641_X20/calibrated/calibrated_final.ms' 
SB1refant = 'DA49'
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


# spws 0, 4 contain the CO 2-1 line
contspws = '0~7'
flagmanager(vis=SB1_field,mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
flagchannels='0:1880~2250, 4:1880~2250' #this is probably more conservative than necessary. Flagging 1880 to 1960 looks like it'd be sufficient 

flagdata(vis=SB1_field,mode='manual', spw=flagchannels, flagbackup=False, field = field)

# Average the channels within spws
SB1_initcont = field+'_'+tag+'_initcont.ms'
print(SB1_initcont)
os.system('rm -rf ' + SB1_initcont + '*')
split2(vis=SB1_field,
       field = field,
       spw=contspws,      
       outputvis=SB1_initcont,
       width=[480,8,8,8, 480, 8, 8, 8],
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
      mask='circle[[251pix,252pix],1.2arcsec]',
      interactive=True)

# cleaned for 1 cycles (100 iterations)
# peak: 60.0 mJy/beam
# rms: 109 microJy/beam

# First phase-self-cal
SB1_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+SB1_p1)
gaincal(vis=SB1_initcont, caltable=SB1_p1, gaintype='T',  
        spw=contspws, refant=SB1refant, calmode='p', 
        solint='25s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2017/05/14/00:00:01~2017/05/14/11:59:59')

plotcal(caltable=SB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna', timerange = '2017/05/17/00:00:01~2017/05/17/11:59:59')


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
      mask='circle[[251pix,252pix],1.2arcsec]',
      interactive=True)

# cleaned for 2 cycles with 100 iterations each
# peak: 63.0 mJy/beam
# rms: 46.2 microJy/beam


# Second round of phase cal didn't result in any noticeable improvement, so we move on to amplitude self-cal


SB1_ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+SB1_ap1)
gaincal(vis=SB1_contms_p1, caltable=SB1_ap1, gaintype='T',  
        spw=contspws, refant=SB1refant, calmode='ap', 
        solint='60s', minsnr=2.0, minblperant=4, solnorm = True)

plotcal(caltable=SB1_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = '2017/05/14/00:00:01~2017/05/14/11:59:59')

plotcal(caltable=SB1_ap1, xaxis = 'time', yaxis = 'amp',subplot=441,iteration='antenna', timerange = '2017/05/17/00:00:01~2017/05/17/11:59:59')


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
      mask='circle[[251pix,252pix],1.2arcsec]',
      interactive=True)

# cleaned for 3 cycles of 100 iterations each
# peak: 63.0 mJy/beam
# rms: 45.3 microJy/beam

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
      mask='circle[[251pix,252pix],1.2arcsec]',
      interactive=True)

#large continuum field


clean(vis='/data/sandrews/LP/reduced_data/RU_Lup/visibilities/RU_Lup_SB1_contfinal.ms', 
      imagename='RU_Lup_largefieldcontinuum', 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      multiscale = [0, 10, 20, 30], 
      robust=2.0,
      gain = 0.1,
      imsize=1500,
      cell='0.03arcsec', 
      interactive=True)


##############################
# Reduction of CO data in SB1
#############################

applycal(SB1_field, gaintable=[SB1_p1, SB1_ap1], calwt=T, flagbackup=F)
#split out the CO 2-1 spectral window
linespw = '0, 4'
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
fitspw = '0:0~1880;1960~3839, 1:0~1880;1960~3839' # channels for fitting continuum
uvcontsub(vis=SB1_CO_ms,
          spw='0~1', 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=1,
          want_cont=False) 

plotms(vis = SB1_CO_mscontsub, xaxis = 'channel', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgtime = '1.e8',avgbaseline  =True)


CO_cvel = SB1_CO_mscontsub+'.cvel'

os.system('rm -rf '+ CO_cvel)
mstransform(vis = SB1_CO_mscontsub, outputvis = CO_cvel,  keepflags = False,datacolumn = 'data', regridms = True,mode='velocity',start='-5km/s',width='0.35km/s',nchan=60, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

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
      start='-5km/s',
      width='0.35km/s',
      nchan=60, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '10mJy',
      interactive=True) 

immoments(axis = "spec",imagename=SB1_CO_image+'.image',moments=[0],outfile =SB1_CO_image+'.mom0', chans = '3~46')
immoments(axis = "spec",imagename=SB1_CO_image+'.image',moments=[1],outfile =SB1_CO_image+'.mom1', chans = '3~46', includepix = [.013, 10])

SB1_CO_largeimage = field+'_'+tag+'_CO21largecube'
os.system('rm -rf '+SB1_CO_largeimage+'.*')
clean(vis=CO_cvel, 
      imagename=SB1_CO_largeimage,
      mode = 'velocity',
      psfmode = 'clark',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 30, 50],
      robust = 1.0,
      gain = 0.1, 
      imsize = 1000,
      cell = '0.03arcsec',
      start='-5km/s',
      width='0.35km/s',
      nchan=60, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '10mJy',
      interactive=True) 

impbcor(imagename = SB1_CO_largeimage+'.image', pbimage = SB1_CO_largeimage+'.flux', outfile = SB1_CO_largeimage+'.pbcor.image')

immoments(axis = "spec",imagename=SB1_CO_largeimage+'.image',moments=[0],outfile =SB1_CO_largeimage+'.mom0', chans = '3~46')
immoments(axis = "spec",imagename=SB1_CO_largeimage+'.pbcor.image',moments=[0],outfile =SB1_CO_largeimage+'.pbcor.mom0', chans = '3~46')

immoments(axis = "spec",imagename=SB1_CO_largeimage+'.image',moments=[0],outfile =SB1_CO_largeimage+'_1sigcut.mom0', chans = '3~46', includepix = [.0025,10 ])

immoments(axis = "spec",imagename=SB1_CO_largeimage+'.image',moments=[0],outfile =SB1_CO_largeimage+'_2sigcut.mom0', chans = '3~46', includepix = [.005,10 ])

immoments(axis = "spec",imagename=SB1_CO_largeimage+'.image',moments=[0],outfile =SB1_CO_largeimage+'_3sigcut.mom0', chans = '3~46', includepix = [.0075,10 ])
immoments(axis = "spec",imagename=SB1_CO_largeimage+'.pbcor.image',moments=[0],outfile =SB1_CO_largeimage+'_3sigcut.pbcor.mom0', chans = '3~46', includepix = [.0075,10 ])


SB1_CO_naturalimage = field+'_'+tag+'_CO21natural'
os.system('rm -rf '+SB1_CO_naturalimage+'.*')
clean(vis=CO_cvel, 
      imagename=SB1_CO_naturalimage,
      mode = 'velocity',
      psfmode = 'clark',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 30, 50],
      robust = 2.0,
      gain = 0.1, 
      imsize = 1000,
      cell = '0.03arcsec',
      start='-5km/s',
      width='0.35km/s',
      nchan=60, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '6mJy',
      interactive=True) 

immoments(axis = "spec",imagename=SB1_CO_naturalimage+'.image',moments=[0],outfile =SB1_CO_naturalimage+'_3sigcut.mom0', chans = '3~46', includepix = [.0075,10 ])
immoments(axis = "spec",imagename=SB1_CO_naturalimage+'.image',moments=[1],outfile =SB1_CO_naturalimage+'.mom1', chans = '3~46', includepix = [.0125, 10])
immoments(axis = "spec",imagename=SB1_CO_naturalimage+'.image',moments=[8],outfile =SB1_CO_naturalimage+'.mom8', chans = '3~46', includepix = [.0075, 10])

SB1_CO_naturalimage = field+'_'+tag+'_CO21natural'
os.system('rm -rf '+SB1_CO_naturalimage+'.*')
clean(vis=CO_cvel, 
      imagename=SB1_CO_naturalimage,
      mode = 'velocity',
      psfmode = 'clark',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 30, 50],
      robust = 2.0,
      gain = 0.1, 
      imsize = 1000,
      cell = '0.03arcsec',
      start='-5km/s',
      width='0.35km/s',
      nchan=60, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '6mJy',
      interactive=True) 

SB1_CO_taper = field+'_'+tag+'_CO21taper'
os.system('rm -rf '+SB1_CO_taper+'.*')
clean(vis=CO_cvel, 
      imagename=SB1_CO_taper,
      mode = 'velocity',
      psfmode = 'clark',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 20, 30, 50],
      robust = 2.0,
      gain = 0.05, 
      imsize = 1000,
      cell = '0.03arcsec',
      start='-5km/s',
      width='0.35km/s',
      nchan=60, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '6mJy',
      uvtaper = True,
      outertaper = '0.2arcsec',
      interactive=True) 

immoments(axis = "spec",imagename=SB1_CO_taper+'.image',moments=[0],outfile =SB1_CO_taper+'_3sigcut.mom0', chans = '3~46', includepix = [.0075,10 ])

SB1_CO_taper2 = field+'_'+tag+'_CO21taper2'
os.system('rm -rf '+SB1_CO_taper2+'.*')
clean(vis=CO_cvel, 
      imagename=SB1_CO_taper2,
      mode = 'velocity',
      psfmode = 'hogbom',  
      imagermode='csclean',
      weighting = 'briggs',
      multiscale = [0, 10, 20, 30],
      robust = 2.0,
      gain = 0.05, 
      imsize = 500,
      cell = '0.08arcsec',
      start='-5km/s',
      width='0.35km/s',
      nchan=60, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 5, 
      threshold = '8mJy',
      uvtaper = True,
      outertaper = '0.5arcsec',
      interactive=True) 

immoments(axis = "spec",imagename=SB1_CO_taper2+'.image',moments=[0],outfile =SB1_CO_taper2+'_3sigcut.mom0', chans = '3~46', includepix = [.0105,10 ])
immoments(axis = "spec",imagename=SB1_CO_taper2+'.image',moments=[1],outfile =SB1_CO_taper2+'.mom1', chans = '3~46', includepix = [.0175, 10])


