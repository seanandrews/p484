"""
This script is written for CASA 4.5.3
Note that the imaging algorithms were rewritten significantly between 
CASA 4.5.3 and CASA 4.7.2 
"""

field = 'SR_4'

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
flagchannels='0:1800~2100, 4:1800~2100, 8:1800~2100'  

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

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '2',
       coloraxis = 'spw', iteraxis = 'antenna')

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '0', 
       coloraxis = 'spw', iteraxis = 'antenna') 

plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '1', 
       coloraxis = 'spw', iteraxis = 'antenna') 


plotms(vis = SB1_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
       ydatacolumn = 'data',avgchannel = '16', observation = '2', 
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
      mask='circle[[252pix,233pix],0.8arcsec]',
      interactive=True)

# cleaned for 2 cycles (200 iterations)
# peak: 25.6 mJy/beam
# rms: 63.9 microJy/beam

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
      mask='circle[[252pix,233pix],0.8arcsec]',
      interactive=True)

# cleaned for 2 cycles with 100 iterations each
# peak: 27.2 mJy/beam
# rms: 35.0 microJy/beam


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
      mask='circle[[252pix,233pix],0.8arcsec]',
      interactive=True)

# cleaned for 2 cycles of 100 iterations each
# peak: 27.2 mJy/beam
# rms: 35.0 microJy/beam

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
      mask='circle[[252pix,233pix],0.8arcsec]',
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
fitspw = '0:0~1800;2100~3839, 1:0~1800;2100~3839, 2:0~1800; 2100~3839' # channels for fitting continuum
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
mstransform(vis = SB1_CO_mscontsub, outputvis = CO_cvel,  keepflags = False,datacolumn = 'data', regridms = True,mode='velocity',start='-8km/s',width='0.35km/s',nchan=80, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

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
      start='-8km/s',
      width='0.35km/s',
      nchan=70, 
      outframe='LSRK', 
      veltype='radio', 
      restfreq='230.53800GHz',
      negcomponent=1, 
      cyclefactor = 1, 
      threshold = '10mJy',
      interactive=True) 

##################################################################
##################################################################
## long baseline data
##################################################################
##################################################################

LB_vis = '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X5c/group.uid___A001_X8c5_X5d/member.uid___A001_X8c5_X5e/calibrated/calibrated_final.ms' #this is the long-baseline measurement set being calibrated
LB1_refant = 'DA61, DA50'
tag = 'LB'

#need to initialize the weight_spectrum column because the short baselines data have an initialized weight_spectrum column 

initweights(vis = LB_vis, wtmode = 'weight', dowtsp = True)
"""
Double-check flux calibration
au.getALMAFlux('J1517-2422', frequency = '232.582GHz', date = '2017/09/06')
Closest Band 3 measurement: 3.690 +- 0.070 (age=+2 days) 91.5 GHz
Closest Band 7 measurement: 2.370 +- 0.050 (age=+1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 17 days from 2017/09/06, with age separation of 0 days
  2017/08/20: freqs=[91.46, 343.48], fluxes=[3.78, 2.71]
Median Monte-Carlo result for 232.582000 = 2.988214 +- 0.254621 (scaled MAD = 0.249093)
Result using spectral index of -0.251488 for 232.582 GHz from 3.690 Jy at 91.460 GHz = 2.918012 +- 0.254621 Jy

Consistent with pipeline log 

au.getALMAFlux('J1427-4206', frequency = '232.582GHz', date = '2017/11/09')
Closest Band 3 measurement: 4.010 +- 0.110 (age=+2 days) 103.5 GHz
Closest Band 3 measurement: 4.290 +- 0.120 (age=+2 days) 91.5 GHz
Closest Band 7 measurement: 1.960 +- 0.050 (age=-1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age 8 days from 2017/11/09, with age separation of 0 days
  2017/11/01: freqs=[91.46, 103.49, 343.48], fluxes=[4.19, 4.05, 1.92]
Median Monte-Carlo result for 232.582000 = 2.442674 +- 0.141522 (scaled MAD = 0.141623)
Result using spectral index of -0.595755 for 232.582 GHz from 4.010 Jy at 103.490 GHz = 2.475316 +- 0.141522 Jy

The fluxcal here needs to be fixed 
"""

# spws 24 and 98 contain the CO 2-1 line, while the others are continuum only
contspws = '19,21,23,25,92,94,96,98' #spw numbering is weird for this MS 

flagmanager(vis=LB_vis,mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
# velocity range selected for flagging based on compact configuration data
flagchannels='25:1880~1970, 98:1880~1970' 


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
      multiscale = [0, 10, 25, 50, 75], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.3,
      imsize=1800,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      imagermode = 'csclean')


#5 cycles of 100 iterations each 

LB1_initcontimage1 = field+'_'+tag+'_initcontinuum_1'
os.system('rm -rf '+LB1_initcontimage1+'.*')
clean(vis=LB1_initcont, 
      observation = '1', 
      imagename=LB1_initcontimage1, 
      mode='mfs', 
      multiscale = [0, 10, 25, 50, 75], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.3,
      imsize=1800,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      imagermode = 'csclean')


#3 cycles of 100 iterations each 

LB1_initcontimage_LBonly = field+'_'+tag+'_initcontinuum_LBonly'
os.system('rm -rf '+LB1_initcontimage_LBonly+'.*')
clean(vis=LB1_initcont, 
      imagename=LB1_initcontimage_LBonly, 
      mode='mfs', 
      multiscale = [0, 10, 25, 50], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.3,
      imsize=1800,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      imagermode = 'csclean')

#5 cycles of 100 iterations each 

#looks aligned with short baseline data 

#do this in CASA 5.1.1
os.system('rm -rf SR_4_contcombined.ms')
concat(vis = [SB1_contms_final, LB1_initcont], concatvis = 'SR_4_contcombined.ms', dirtol = '1arcsec', copypointing = False) 

plotms(vis='SR_4_contcombined.ms',xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30')


#Go back to CASA 4.5.3 here 

tag = 'combined'

LB1_initcontimage = field+'_'+tag+'_initcontinuum'
os.system('rm -rf '+LB1_initcontimage+'.*')
clean(vis='SR_4_contcombined.ms', 
      imagename=LB1_initcontimage, 
      field = field, 
      mode='mfs', 
      multiscale = [0, 10, 25, 50], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.1,
      imsize=1800,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask='circle[[920pix,727pix],0.5arcsec]',
      imagermode = 'csclean')

#15 cycles of 100 iterations each
#rms: 15 microJy/beam
#peak: 3.9 mJy/beam


LB1_p1 = field+'_'+tag+'.p1'
gaincal(vis='SR_4_contcombined.ms', field = field, caltable=LB1_p1, gaintype='T', combine = 'spw,scan', 
        spw='0~19', refant='DA46, DA61, DA50', calmode='p', 
        solint='300s', minsnr=2.0, minblperant=4)

applycal(vis='SR_4_contcombined.ms', field =field, spw='0~19', spwmap = [0]*20, gaintable=[LB1_p1], applymode = 'calonly', flagbackup=False)


LB1_contms_p1 = field+'_'+tag+'_contp1.ms'
os.system('rm -rf '+LB1_contms_p1)
split2(vis='SR_4_contcombined.ms', outputvis=LB1_contms_p1, datacolumn='corrected')

LB1_contimagep1 = field+'_'+tag+'_continuump1'
os.system('rm -rf '+LB1_contimagep1+'.*')
clean(vis=LB1_contms_p1, 
      imagename=LB1_contimagep1, 
      field = field, 
      mode='mfs', 
      multiscale = [0, 10, 25, 50], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.1,
      imsize=1800,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask='circle[[920pix,727pix],0.5arcsec]',
      imagermode = 'csclean')

#18 cycles of 100 iterations each
#rms: 14 microJy/beam
#peak: 4.0 mJy/beam

# Second round of phase-only self-cal
LB1_p2 = field+'_'+tag+'.p2'
os.system('rm -rf '+LB1_p2)
gaincal(vis=LB1_contms_p1, caltable=LB1_p2, gaintype='T', combine = 'spw,scan', 
        spw='0~20', refant='DA46, DA61, DA50', calmode='p', 
        solint='150s', minsnr=2.0, minblperant=4)

applycal(vis=LB1_contms_p1,  spw='0~19', spwmap = [0]*20, gaintable=[LB1_p2], applymode = 'calonly', flagbackup=False)

LB1_contms_p2 = field+'_'+tag+'_contp2.ms'
os.system('rm -rf '+LB1_contms_p2)
split2(vis=LB1_contms_p1, outputvis=LB1_contms_p2, datacolumn='corrected')


LB1_contimagep2 = field+'_'+tag+'_continuump2'
os.system('rm -rf '+LB1_contimagep2+'.*')
clean(vis= LB1_contms_p2, 
      imagename=LB1_contimagep2, 
      field = field, 
      mode='mfs', 
      multiscale = [0, 10, 25, 50], 
      weighting='briggs', 
      robust=0.5,
      gain = 0.1,
      imsize=1800,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask='circle[[920pix,727pix],0.5arcsec]',
      imagermode = 'csclean')


#18 cycles of 100 iterations each
#rms: 14 microJy/beam
#peak: 14 mJy/beam
#marginal difference from first self-cal

LB1_robust0 = field+'_'+tag+'_robust0'
os.system('rm -rf '+LB1_robust0+'.*')
clean(vis= LB1_contms_p2, 
      imagename=LB1_robust0, 
      field = field, 
      mode='mfs', 
      multiscale = [0, 10, 25, 50], 
      weighting='briggs', 
      robust=0,
      gain = 0.1,
      imsize=1800,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask='circle[[920pix,727pix],0.5arcsec]',
      imagermode = 'csclean')

#28 cycles of 100 iterations each 


