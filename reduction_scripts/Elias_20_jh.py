"""
This script is written for CASA 4.5.3
Note that the imaging algorithms were rewritten significantly between 
CASA 4.5.3 and CASA 4.7.2 
"""

field = 'Elias_20'

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
flagchannels='0:1880~2250, 4:1880~2250, 8:1880~2250' #1880 to 1950 would have been adequate

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
      mask='circle[[252pix,233pix],1.0arcsec]',
      interactive=True)

# cleaned for 1 cycles (100 iterations)
# peak: 34.3 mJy/beam
# rms: 83 microJy/beam

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
      mask='circle[[252pix,233pix],1.0arcsec]',
      interactive=True)

# cleaned for 2 cycles with 100 iterations each
# peak: 37.2 mJy/beam
# rms: 40.9 microJy/beam


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
      mask='circle[[252pix,233pix],1.0arcsec]',
      interactive=True)

# cleaned for 3 cycles of 100 iterations each
# peak: 37.2 mJy/beam
# rms: 40.3 microJy/beam

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
mstransform(vis = SB1_CO_mscontsub, outputvis = CO_cvel,  keepflags = False,datacolumn = 'data', regridms = True,mode='velocity',start='-10km/s',width='0.35km/s',nchan=90, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

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
      start='-10km/s',
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


#rescaling the flux for the 9/23/17 execution because the calibrator catalog was updated after the original pipeline calibration
#Old flux value of J1517-2422 at 232 GHz: 2.457 Jy
#New flux value at 232.583 GHz:  2.17 Jy

LB_vis = '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X58/group.uid___A001_X8c5_X59/member.uid___A001_X8c5_X5a/calibrated/calibrated_final.ms' #this is the long-baseline measurement set being calibrated

LB1_refant = 'DA61'
tag = 'LB'

gencal(vis = LB_vis, caltable = 'scale.gencal', caltype = 'amp', parameter = [1.064])
applycal(vis = LB_vis, gaintable = ['scale.gencal'], calwt = T, flagbackup = F, spw = '0~3') #rescale observation for 9/23/2017

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
       datacolumn='corrected')

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
      multiscale = [0, 10, 25, 50, 100], 
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


#4 cycles of 100 iterations each 

LB1_initcontimage1 = field+'_'+tag+'_initcontinuum_1'
os.system('rm -rf '+LB1_initcontimage1+'.*')
clean(vis=LB1_initcont, 
      observation = '1', 
      imagename=LB1_initcontimage1, 
      mode='mfs', 
      multiscale = [0, 10, 25, 50, 100], 
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


#4 cycles of 100 iterations each 

LB1_initcontimage_LBonly = field+'_'+tag+'_initcontinuum_LBonly'
os.system('rm -rf '+LB1_initcontimage_LBonly+'.*')
clean(vis=LB1_initcont, 
      imagename=LB1_initcontimage_LBonly, 
      mode='mfs', 
      multiscale = [0, 10, 25, 50, 100], 
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

#6 cycles of 100 iterations each 



#looks aligned with short baseline data 

delmod(vis=LB1_initcont,field=field,otf=True)

clearcal(vis=LB1_initcont)

delmod(vis=SB1_contms_final,field=field,otf=True)

clearcal(vis=SB1_contms_final)

#do this in CASA 5.1.1
os.system('rm -rf Elias_20_contcombined.ms')
concat(vis = [SB1_contms_final, LB1_initcont], concatvis = 'Elias_20_contcombined.ms', dirtol = '1arcsec', copypointing = False) 

#Go back to CASA 4.5.3 here 

tag = 'combined'

LB1_initcontimage = field+'_'+tag+'_initcontinuum'
os.system('rm -rf '+LB1_initcontimage+'.*')
clean(vis='Elias_20_contcombined.ms', 
      imagename=LB1_initcontimage, 
      field = field, 
      mode='mfs', 
      multiscale = [0, 10, 25, 50, 100], 
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
      mask='ellipse[[917pix,736pix],[0.8arcsec,0.5arcsec],150deg]',
      imagermode = 'csclean')

#19 cycles of 100 iterations each
#rms: 13 microJy/beam
#peak: 3.3 mJy/beam

LB1_p1 = field+'_'+tag+'.p1'
rmtables(LB1_p1)
gaincal(vis='Elias_20_contcombined.ms', field = field, caltable=LB1_p1, gaintype='T', combine = 'spw,scan', 
        spw='0~19', refant='DA46, DA61', calmode='p', 
        solint='150s', minsnr=2.0, minblperant=4)

applycal(vis='Elias_20_contcombined.ms', field =field, spw='0~19', spwmap = [0]*20, gaintable=[LB1_p1], applymode = 'calonly', flagbackup=False)


LB1_contms_p1 = field+'_'+tag+'_contp1.ms'
os.system('rm -rf '+LB1_contms_p1)
split2(vis='Elias_20_contcombined.ms', outputvis=LB1_contms_p1, datacolumn='corrected')

LB1_contimagep1 = field+'_'+tag+'_continuump1'
os.system('rm -rf '+LB1_contimagep1+'.*')
clean(vis=LB1_contms_p1, 
      imagename=LB1_contimagep1, 
      field = field, 
      mode='mfs', 
      multiscale = [0, 10, 25, 50, 100], 
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
      mask='ellipse[[917pix,736pix],[0.8arcsec,0.5arcsec],150deg]',
      imagermode = 'csclean')


#20 cycles of 100 iterations each
#rms: 12.7 microJy/beam
#peak: 3.3 mJy/beam


# Second round of phase-only self-cal
LB1_p2 = field+'_'+tag+'.p2'
os.system('rm -rf '+LB1_p2)
gaincal(vis=LB1_contms_p1, caltable=LB1_p2, gaintype='T', combine = 'spw,scan', 
        spw='0~20', refant='DA46, DA61', calmode='p', 
        solint='90s', minsnr=2.0, minblperant=4)

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
      multiscale = [0, 10, 25, 50, 100], 
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
      mask='ellipse[[917pix,736pix],[0.8arcsec,0.5arcsec],150deg]',
      imagermode = 'csclean')


#20 cycles of 100 iterations each
#rms: 12.7 microJy/beam
#peak: 3.3 mJy/beam
#essentially no difference from first self-cal

LB1_robust0 = field+'_'+tag+'_robust0'
os.system('rm -rf '+LB1_robust0+'.*')
clean(vis= LB1_contms_p2, 
      imagename=LB1_robust0, 
      field = field, 
      mode='mfs', 
      multiscale = [0, 10, 25, 50, 100], 
      weighting='briggs', 
      robust=0.0,
      gain = 0.1,
      imsize=1800,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask='ellipse[[917pix,736pix],[0.8arcsec,0.5arcsec],150deg]',
      imagermode = 'csclean')

