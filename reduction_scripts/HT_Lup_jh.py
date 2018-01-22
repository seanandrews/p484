"""
This script is written for CASA 4.5.3
Note that the imaging algorithms were rewritten significantly between 
CASA 4.5.3 and CASA 4.7.2 

Datasets calibrated: 
2016.1.00484.L/GW_Lup_a_06_TM1  (PI: Andrews)
"""

field = 'HT_Lup'

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
      mask='circle[[251pix,245pix],1.2arcsec]',
      interactive=True)

# cleaned for 2 cycles (100 iterations)
# peak: 50.3 mJy/beam  (*2 mJy source off to W)
# rms: 139 microJy/beam

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
      mask='circle[[251pix,245pix],1.2arcsec]',
      interactive=True)

# cleaned for 2 cycles with 100 iterations each
# peak: 56.2 mJy/beam
# rms: 39.0 microJy/beam


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
      mask='circle[[251pix,245pix],1.2arcsec]',
      interactive=True)

# cleaned for 4 cycles of 100 iterations each
# peak: 56.3 mJy/beam (*3.4 mJy source to NW)
# rms: 37.8 microJy/beam

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

##################################################################
##################################################################
## long baseline data
##################################################################
##################################################################

LB_vis = '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X84/group.uid___A001_X8c5_X85/member.uid___A001_X8c5_X86/calibrated/calibrated_final.ms' #this is the long-baseline measurement set being calibrated

field = 'HT_Lupi'
LB1_refant = 'DV24'
tag = 'LB'


"""
Double-check flux calibration
au.getALMAFlux('J1517-2422', frequency = '232.582GHz', date = '2017/09/24')
Closest Band 3 measurement: 3.300 +- 0.330 (age=+7 days) 103.5 GHz
Closest Band 3 measurement: 3.200 +- 0.280 (age=+7 days) 91.5 GHz
Closest Band 7 measurement: 1.770 +- 0.040 (age=+1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -8 days from 2017/09/24, with age separation of 0 days
  2017/10/02: freqs=[91.46, 103.49, 343.48], fluxes=[2.79, 2.77, 1.92]
Median Monte-Carlo result for 232.582000 = 2.170800 +- 0.179639 (scaled MAD = 0.180767)
Result using spectral index of -0.279723 for 232.582 GHz from 3.300 Jy at 103.490 GHz = 2.631126 +- 0.179639 Jy


Reasonably close to pipeline log 

au.getALMAFlux('J1427-4206', frequency = '232.582GHz', date = '2017/09/24')
Closest Band 3 measurement: 3.210 +- 0.100 (age=-4 days) 91.5 GHz
Closest Band 7 measurement: 1.380 +- 0.050 (age=+1 days) 343.5 GHz
getALMAFluxCSV(): Fitting for spectral index with 1 measurement pair of age -27 days from 2017/09/24, with age separation of 0 days
  2017/10/21: freqs=[91.46, 103.49, 343.48], fluxes=[3.71, 3.44, 1.98]
Median Monte-Carlo result for 232.582000 = 2.372582 +- 0.116735 (scaled MAD = 0.117094)
Result using spectral index of -0.467361 for 232.582 GHz from 3.210 Jy at 91.460 GHz = 2.075213 +- 0.116735 Jy


This is way off from the catalog...need to look into the fluxcal further
"""


"""
For the purposes of checking the flux offsets between the two execution blocks, we're just splitting out the continuum windows to make a small dataset

"""

split2(vis='HT_Lup_SB1_contfinal.ms',
       field = field,
       outputvis='SB.ms',
       width=[8, 16, 16, 16, 8, 16, 16, 16], 
       datacolumn='data')
execfile('ExportMS.py')

split2(vis=LB_vis,
       field = field,
       spw='0~2',      
       outputvis='LB0.ms',
       width=128, 
       timebin = '30s',
       datacolumn='data')

execfile('ExportMS.py')


clean(vis='LB0.ms', 
      imagename='initcont0', 
      mode='mfs', 
      multiscale = [0, 25, 50, 75,100], 
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
      imagermode = 'csclean')

split2(vis=LB_vis,
       field = field,
       spw='4~6',      
       outputvis='LB1.ms',
       width=128, 
       timebin = '30s',
       datacolumn='data')

clean(vis='LB1.ms', 
      imagename='initcont1', 
      mode='mfs', 
      multiscale = [0, 25, 50, 75, 100], 
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
      imagermode = 'csclean')

execfile('ExportMS.py')


# the phase center offset 
# (offx, offy) = (-0.045, -0.13)"	[i.e., to the NW]

# Rough estimate of viewing geometry from Gaussian fit (to the largest disk only):
# i = 44 degrees.  
# PA = 167 degrees.

#now split out the continuum dataset for proper imaging

# spws 3 and 7 contain the CO 2-1 line, while the others are continuum only
contspws = '0~7'


flagmanager(vis=LB_vis,mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
# velocity range selected for flagging based on compact configuration data
flagchannels='3:1870~1970, 7:1870~1970'

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

#to match the short baseline data, the first LB execution block needs to be scaled up by ~20% and the second needs to be scaled up by ~30%


gencal(vis = LB1_initcont, caltable = 'scale.gencal', spw = '0~7', caltype = 'amp', parameter = [0.913,0.913, 0.913, 0.913,0.877, 0.877, 0.877, 0.877])
applycal(vis = LB1_initcont, gaintable = ['scale.gencal'], calwt = T, flagbackup = F)

LB1_rescaledcont = field+'_'+tag+'_rescaledcont.ms'
os.system('rm -rf ' + LB1_rescaledcont + '*')
split2(vis=LB1_initcont,
       outputvis = LB1_rescaledcont,
       datacolumn='corrected')


#check individual execution blocks
LB1_initcontimage0 = field+'_'+tag+'_initcontinuum_0'
os.system('rm -rf '+LB1_initcontimage0+'.*')
clean(vis=LB1_rescaledcont, 
      observation = '0', 
      imagename=LB1_initcontimage0, 
      mode='mfs', 
      multiscale = [0, 25, 50, 75, 100], 
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
      imagermode = 'csclean')


#4 cycles of 100 iterations each 

LB1_initcontimage1 = field+'_'+tag+'_initcontinuum_1'
os.system('rm -rf '+LB1_initcontimage1+'.*')
clean(vis=LB1_rescaledcont, 
      observation = '1', 
      imagename=LB1_initcontimage1, 
      mode='mfs', 
      multiscale = [0, 25, 50, 75, 100], 
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
      imagermode = 'csclean')



#5 cycles of 100 iterations each 


#images look aligned

LB1_initcontimage_LBonly = field+'_'+tag+'_initcontinuum_LBonly'
os.system('rm -rf '+LB1_initcontimage_LBonly+'.*')
clean(vis=LB1_rescaledcont, 
      imagename=LB1_initcontimage_LBonly, 
      mode='mfs', 
      multiscale = [0, 25, 50, 75, 100], 
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
      imagermode = 'csclean')

#6 cycles of 100 iterations each 


#aligning the short and long-baseline observations based on fits to the unresolved point source at ICRS 15:45:12.644-34:17:29.74

#using analysis utils to convert peak coordinates from degrees to sexagesimal values
au.rad2radec(imfitdict = imfit(imagename = 'HT_Lupi_LB_initcontinuum_LBonly.image', region = 'circle[[15h45m12.645s,-34.17.29.74],1arcsec]'))
#result for long-baseline data: ICRS 15:45:12.644497, -34:17:29.73882

au.rad2radec(imfitdict = imfit(imagename = 'HT_Lup_SB1_ap1continuum.image', region = 'circle[[15h45m12.645s,-34.17.29.74],1arcsec]'))
#result for short-baseline data: ICRS 15:45:12.646091, -34:17:29.74805


#shift phase-center of long-baseline data so that the point source has the same relative distance from the phase center as the short baseline data 
#original phase-center of long-baseline data: ICRS 15:45:12.850428-34.17.30.89677
au.ICRSToJ2000('15:45:12.852022 -34:17:30.90600')
#unfortunately, fixplanets doesn't support ICRS yet 
os.system('rm -rf HT_Lupi_LB_shiftedcont.ms')
fixvis(vis = LB1_rescaledcont, outputvis = 'HT_Lupi_LB_shiftedcont.ms', phasecenter = 'ICRS 15h45m12.849736 -034d17m30.8854s')

#then reassign phasecenter to same phasecenter as short baseline data 
au.ICRSToJ2000('15:45:12.851330 -34:17:30.89463')
#J2000 15:45:12.85185, -034:17:30.879737
fixplanets(vis = 'HT_Lupi_LB_shiftedcont.ms', field = field, direction = 'J2000 15h45m12.85185s -034d17m30.879737s')


#also need to reassign phasecenter of short-baseline observations so that it's also in J2000 coordinates (or else concat won't merge the fields)

fixplanets(vis = SB1_contms_final, field = 'HT_Lup', direction = 'J2000 15h45m12.85185s -034d17m30.879737s')

os.system('rm -rf HT_Lup_contcombined.ms')
concat(vis = [SB1_contms_final, 'HT_Lupi_LB_shiftedcont.ms'], concatvis = 'HT_Lup_contcombined.ms', dirtol = '1arcsec',copypointing = False)



tag = 'combined'
field = 'HT_Lup'

LB1_initcontimage = field+'_'+tag+'_initcontinuum'
os.system('rm -rf '+LB1_initcontimage+'.*')
clean(vis='HT_Lup_contcombined.ms', 
      imagename=LB1_initcontimage, 
      mode='mfs', 
      multiscale = [0, 25, 50], 
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
      mask = ['circle[[15h45m12.846s,-34.17.31.025],0.6arcsec]', 'circle[[15h45m12.645s,-34.17.29.74],0.2arcsec]'],
      imagermode = 'csclean')

#15 cycles of 100 iterations each
#rms: 20.6 microJy/beam
#peak: 8.2 mJy/beam


# First round of phase-only self-cal
LB1_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+LB1_p1)
gaincal(vis='HT_Lup_contcombined.ms', caltable=LB1_p1, gaintype='T', combine = 'spw,scan', 
        spw='0~15', refant='DV24, DA49', calmode='p', 
        solint='120s', minsnr=2.0, minblperant=4)

applycal(vis='HT_Lup_contcombined.ms', spw='0~15', spwmap = [0]*16, gaintable=[LB1_p1], calwt=True, applymode = 'calonly', flagbackup=False, interp = 'linearperobs')

LB1_contms_p1 = field+'_'+tag+'_contp1.ms'
os.system('rm -rf '+LB1_contms_p1)
split2(vis='HT_Lup_contcombined.ms', outputvis=LB1_contms_p1, datacolumn='corrected')

LB1_contimagep1 = field+'_'+tag+'_continuump1'
os.system('rm -rf '+LB1_contimagep1+'.*')
clean(vis=LB1_contms_p1, 
      imagename=LB1_contimagep1, 
      mode='mfs', 
      multiscale = [0, 25, 50], 
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
      mask = ['circle[[15h45m12.846s,-34.17.31.025],0.6arcsec]', 'circle[[15h45m12.645s,-34.17.29.74],0.2arcsec]'],
      imagermode = 'csclean')


#20 cycles of 100 iterations each
#peak: 8.7 mJy/beam
#rms: 17 microJy/beam


# Second round of phase-only self-cal
LB1_p2 = field+'_'+tag+'.p2'
os.system('rm -rf '+LB1_p2)
gaincal(vis=LB1_contms_p1, caltable=LB1_p2, gaintype='T', combine = 'spw,scan', 
        spw='0~15', refant='DV24, DA49', calmode='p', 
        solint='90s', minsnr=2.0, minblperant=4)

applycal(vis=LB1_contms_p1, spw='0~15', spwmap = [0]*16, gaintable=[LB1_p2], calwt=True, applymode = 'calonly', flagbackup=False, interp = 'linearperobs')

LB1_contms_p2 = field+'_'+tag+'_contp2.ms'
os.system('rm -rf '+LB1_contms_p2)
split2(vis=LB1_contms_p1, outputvis=LB1_contms_p2, datacolumn='corrected')


LB1_contimagep2 = field+'_'+tag+'_continuump2'
os.system('rm -rf '+LB1_contimagep2+'.*')
clean(vis=LB1_contms_p2, 
      imagename=LB1_contimagep2, 
      mode='mfs', 
      multiscale = [0, 25, 50], 
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
      mask = ['circle[[15h45m12.846s,-34.17.31.025],0.6arcsec]', 'circle[[15h45m12.645s,-34.17.29.74],0.2arcsec]'],
      imagermode = 'csclean')


#20 cycles of 100 iterations each
#peak: 8.9 mJy/beam
#rms: 17 microJy/beam


LB1_robust0 = field+'_'+tag+'_robust0'
os.system('rm -rf '+LB1_robust0+'.*')
clean(vis= LB1_contms_p2, 
      imagename=LB1_robust0, 
      field = field, 
      multiscale = [0, 25, 50], 
      weighting='briggs', 
      robust=0.0,
      gain = 0.1,
      imsize=2400,
      cell='0.003arcsec', 
      niter = 50000,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      cyclefactor = 5, 
      mask = ['circle[[15h45m12.846s,-34.17.31.025],0.6arcsec]', 'circle[[15h45m12.645s,-34.17.29.74],0.2arcsec]'],
      imagermode = 'csclean')

#25 cycles of 100 iterations each 


