"""
This script is written for CASA 4.7.0

Calibrated datasets:

- short-baselines
AS_209_SB1_contfinal.ms    2016.1.00484.L/AS_209_b_06_TM1 (PI: Andrews) 
AS_209_SB2_contfinal.ms    2013.1.00226.S/as_209_a_06_TE  (PI: Oberg)   
AS_209_SB3_contfinal.ms    2013.1.00226.S/as_209_b_06_TE  (PI: Oberg)   
- long-baselines
calibrated_final.ms        2016.1.00484.L/AS_209_b_06_TM1 (PI: Andrews) 

"""

field = 'AS_209'

ddir = 'data/'

SB1 = ddir+'AS_209_SB1_contfinal.ms'
SB2 = ddir+'AS_209_SB2_contfinal.ms'
SB3 = ddir+'AS_209_SB3_contfinal.ms'
LB1 = ddir+'calibrated_final.ms'

############################
# look at data

vishead(vis=SB1)
# SpwID    #Chans   Frame   Ch0(MHz)  ChanWid(kHz)  TotBW(kHz) CtrFreq(MHz) BBC Num  Corrs  
# 0            8   TOPO  230964.631   -117187.500   2500312.5 230554.4745        1  XX  YY
# 1           16   TOPO  233554.122   -125000.000   5334000.0 232616.6218        2  XX  YY
# 2           16   TOPO  244068.062    125000.000   5334000.0 245005.5620        3  XX  YY
# 3           16   TOPO  245985.062    125000.000   5334000.0 246922.5620        4  XX  YY
vishead(vis=SB2)
# SpwID   #Chans   Frame   Ch0(MHz)  ChanWid(kHz)  TotBW(kHz) CtrFreq(MHz) BBC Num  Corrs  
# 0            1   TOPO  231206.425     58593.750     58593.8 231206.4246        3  XX  YY
# 1            1   TOPO  230523.746     58593.750     58593.8 230523.7464        3  XX  YY
# 2            4   TOPO  234745.731    117187.500    468750.0 234921.5125        4  XX  YY
vishead(vis=SB3)
# SpwID   #Chans   Frame   Ch0(MHz)  ChanWid(kHz)  TotBW(kHz) CtrFreq(MHz) BBC Num  Corrs  
# 0            1   TOPO  245513.719   -117187.500    117187.5 245513.7193        3  XX  YY
# 1            1   TOPO  245544.267   -117187.500    117187.5 245544.2674        3  XX  YY
# 2            1   TOPO  241542.631    -58593.750     58593.8 241542.6307        4  XX  YY
# 3            1   TOPO  241681.303    -58593.750     58593.8 241681.3026        4  XX  YY
# 4            1   TOPO  241748.319    -58593.750     58593.8 241748.3192        4  XX  YY
# 5            1   TOPO  241772.520    -58593.750     58593.8 241772.5196        4  XX  YY
vishead(vis=LB)
# SpwID   #Chans   Frame   Ch0(MHz)  ChanWid(kHz)  TotBW(kHz) CtrFreq(MHz) BBC Num  Corrs  
# 0          128   TOPO  233576.255    -15625.000   2000000.0 232584.0677        2  XX  YY
# 1          128   TOPO  243979.958     15625.000   2000000.0 244972.1458        3  XX  YY
# 2          128   TOPO  245896.958     15625.000   2000000.0 246889.1458        4  XX  YY
# 3         3840   TOPO  230990.837      -244.141    937500.0 230522.2089        1  XX  YY -> CO 2-1
# 4          128   TOPO  233576.949    -15625.000   2000000.0 232584.7615        2  XX  YY
# 5          128   TOPO  243980.670     15625.000   2000000.0 244972.8580        3  XX  YY
# 6          128   TOPO  245897.670     15625.000   2000000.0 246889.8580        4  XX  YY
# 7         3840   TOPO  230991.525      -244.141    937500.0 230522.8966        1  XX  YY -> CO 2-1

plotms(vis = SB1, xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')

# CO in LB ms
plotms(vis = LB, xaxis = 'channel', yaxis = 'amplitude', field = field, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, spw = '3,7')


############################
# prepare LB data

# save unflagged data
flagmanager(vis=LB1,mode='save', versionname='before_cont_flags')
# flag CO line
flagchannels='3:1870~1970, 7:1870~1970'
flagdata(vis=LB1,mode='manual', spw=flagchannels, flagbackup=False, field = field)

# average cont data
LB1_initcont = 'AS_209_LB_initcont.ms'
split2(vis=LB1,
       field = field,
       spw='0~7',      
       outputvis= LB1_initcont,
       width=[8,8,8,480, 8, 8, 8, 480], # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
       timebin = '6s',
       datacolumn='data')

# Restore flagged line channels
flagmanager(vis=LB1,mode='restore',versionname='before_cont_flags')

plotms(vis=LB1_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30')

############################
# Self-calibrate all three datasets together
# SB1, SB2 and SB3 have been self-calibrated by Jane already

concat(vis = [SB1, SB2, SB3, LB1_initcont], concatvis = 'AS_209_contcombined.ms', dirtol = '1arcsec', copypointing = False) 
concatvis = 'AS_209_contcombined.ms'

refant = 'DA61, DV24'

# Cleaning continuum to make initial self-cal model
LB1_initcontimage = 'AS_209_combined_initcont'
os.system('rm -rf '+LB1_initcontimage+'.*')
clean(vis=concatvis,
      imagename=LB1_initcontimage, 
      mode='mfs', 
      multiscale = [0, 10, 20, 40, 80, 160], 
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
      mask='ellipse[[1204pix,1175pix],[1.3arcsec,1.03arcsec],86deg]', # R=1.3; a=R; b=R*cos(i)=R*0.788  (inc = 38deg) PA = 86 
      imagermode = 'csclean')
# rms 12.7 muJy/beam

######################################
# First self-cal: phase only

caltable_p1 = 'AS_209_selfcal1.pcal'
gaincaltable1 = 'AS_209_gaincal.p1'

gaincal(vis='AS_209_contcombined.ms', caltable=caltable_p1, gaintype='T', combine = 'spw,scan', 
        spw='0~20', refant=refant, calmode='p', solint='30s', minsnr=2.0, minblperant=4)
# look at the solutions
plotcal(caltable=caltable_p1,xaxis='time',yaxis='phase',iteration='antenna',subplot=331,plotrange=[0,0,-100,100],markersize=5, fontsize=10.0,figfile='AS_209_pcal1.png')

# Save flags
flagmanager(vis=concatvis,mode='save',versionname='AS_209_beforeSelfcal')

# apply self-cal solutions to continuum 
applycal(vis=concatvis, spw='0~20', spwmap = [0]*21, gaintable=[caltable_p1], applymode = 'calonly', flagbackup=False, interp = 'linearperobs')

# Split out a new, self-calibrated continuum data set
scvis1 = 'AS_209_cont_selfcal_p1.ms'
split2(vis=concatvis,datacolumn='corrected',outputvis=scvis1)

#vishead(vis='AS_209_contcombined.ms')

# Cleaning continuum to make initial self-cal model
contimage = 'AS_209_combined_cont_sc1'
clean(vis=scvis1,
      imagename=contimage, 
      mode='mfs', 
      multiscale = [0, 10, 20, 40, 80, 160], 
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
      mask='ellipse[[1204pix,1175pix],[1.3arcsec,1.03arcsec],86deg]', # R=1.3; a=R; b=R*cos(i)=R*0.788  (inc = 38deg) PA = 86 
      imagermode = 'csclean')
# rms   11.7 muJy/beam

imview(raster=[{'file':LB1_initcontimage+'.image'},
               {'file':contimage+'.image'}])
# rms0: 12.7 mJy/beam
# rms1: 11.  mJy/beam

######################################
# Second self-cal: phase only

caltable_p2 = 'AS_209_selfcal2.pcal'

gaincal(vis=scvis1, caltable=caltable_p2, gaintype='T', combine = 'spw,scan', 
        spw='0~20', refant=refant, calmode='p', solint='30s', minsnr=2.0, minblperant=4)
# look at the solutions
plotcal(caltable=caltable_p2,xaxis='time',yaxis='phase',iteration='antenna',subplot=331,plotrange=[0,0,-100,100],markersize=5, fontsize=10.0,figfile='AS_209_pcal2.png')

# Save flags
flagmanager(vis=scvis1,mode='save',versionname='AS_209_beforeSelfcal2')

# apply self-cal solutions to continuum 
applycal(vis=scvis1, spw='0~20', spwmap = [0]*21, gaintable=[caltable_p2], applymode = 'calonly', flagbackup=False, interp = 'linearperobs')

# Split out a new, self-calibrated continuum data set
scvis2 = 'AS_209_cont_selfcal_p2.ms'
split2(vis=scvis1,datacolumn='corrected',outputvis=scvis2)

# Cleaning continuum to make new self-cal model
contimage2 = 'AS_209_combined_cont_sc2'
clean(vis=scvis2,
      imagename=contimage2, 
      mode='mfs', 
      multiscale = [0, 10, 20, 40, 80, 160], 
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
      mask='ellipse[[1204pix,1175pix],[1.3arcsec,1.03arcsec],86deg]', # R=1.3; a=R; b=R*cos(i)=R*0.788  (inc = 38deg) PA = 86 
      imagermode = 'csclean')
# rms   11.7 muJy/beam

imview(raster=[{'file':LB1_initcontimage+'.image'},
               {'file':contimage+'.image'},
               {'file':contimage2+'.image'}])
# rms0: 12.7 mJy/beam
# rms1: 11.  mJy/beam
# rms2: 11.  mJy/beam

######################################
# Make final image

im_robust0 = 'AS_209_robust0'
os.system('rm -rf '+im_robust0+'.*')
clean(vis= scvis2, 
      imagename=im_robust0, 
      mode='mfs', 
      multiscale = [0, 10, 20, 40, 80, 160], #check clean components
      weighting='briggs', 
      robust=0,
      gain = 0.1,
      imsize=2400,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask='ellipse[[1204pix,1175pix],[1.3arcsec,1.03arcsec],86deg]', # R=1.3; a=R; b=R*cos(i)=R*0.788  (inc = 38deg) PA = 86 
      imagermode = 'csclean')
# 700 iterations
# rms   11.7 muJy/beam

# make spectral index map
im_robust0_alpha = 'AS_209_robust0_alpha'
os.system('rm -rf '+im_robust0_alpha+'.*')
clean(vis= scvis2, 
      imagename=im_robust0_alpha, 
      mode='mfs', 
      nterms=2,
      multiscale = [0, 10, 20, 40, 80, 160], #check clean components
      weighting='briggs', 
      robust=0,
      gain = 0.1,
      imsize=2400,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask='ellipse[[1204pix,1175pix],[1.3arcsec,1.03arcsec],86deg]', # R=1.3; a=R; b=R*cos(i)=R*0.788  (inc = 38deg) PA = 86 
      imagermode = 'csclean')


# try uniform weighting  
im_uniform = 'AS_209_uniform'
os.system('rm -rf '+im_uniform+'.*')
clean(vis=scvis2, 
      imagename=im_uniform,
      mode='mfs', 
      multiscale = [0, 10, 20, 40, 80, 160],
      weighting='uniform', 
      gain = 0.1,
      imsize=2400,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode='hogbom', 
      cyclefactor = 5, 
      mask='ellipse[[1204pix,1175pix],[1.3arcsec,1.03arcsec],86deg]', 
      imagermode='csclean')

# try different robust
im_robust_m1 = 'AS_209_robustm1'
os.system('rm -rf '+im_robust_m1+'.*')
clean(vis= scvis2, 
      imagename=im_robust_m1, 
      mode='mfs', 
      multiscale = [0, 10, 20, 40, 80, 160], #check clean components
      weighting='briggs', 
      robust=-1,
      gain = 0.1,
      imsize=2400,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask='ellipse[[1204pix,1175pix],[1.3arcsec,1.03arcsec],86deg]', # R=1.3; a=R; b=R*cos(i)=R*0.788  (inc = 38deg) PA = 86 
      imagermode = 'csclean')

imhead(imagename='AS_209_robust0.image')
# 'beammajor': {'unit': 'arcsec', 'value': 0.04155221953988075},
# 'beamminor': {'unit': 'arcsec', 'value': 0.02925644814968109},
# 'beampa': {'unit': 'deg', 'value': 83.70921325683594},
