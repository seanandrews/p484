"""
This script was run on CASA 5.1.1

- Starting from short baseline data selfcalibrated by Jane and 
long baseline data obtained by Sean

- Note the syntax of the spwmap option in applycal. This is different
from the syntax used in CASA 4.5.3 and erlier. 

- using 'tclean' to perform deconvolution. 
See, script HD_163296_ai_casa5.1.1_tclean.py for tclean.  

- adopting minsnr=1.5

- adopting robust=0.5 for selfcal
"""


##############################################
#
# PERFORM SELF-CALIBRATION
#
##############################################

#delmod(vis=comb_contms_unflagged,field=field,otf=True,scr=True)
#clearcal(vis='')
field = 'HD_163296'

# First round of phase-only self-cal
tag = 'combined'

# Split unflagged data (see casa.nrao.edu/casadocs/casa-5.1.1/introduction/known-issues
comb_contms_unflagged = field+'_'+tag+'_unflagged.ms'
os.system('rm -rf '+comb_contms_unflagged)
split(vis='../HD_163296_contcombined.ms', 
      outputvis=comb_contms_unflagged, 
      keepflags=False, 
      datacolumn='data')

#delmod(vis=comb_contms_unflagged, field=field, otf=True,scr=True)

image = field+'_'+tag+'_p0'
os.system('rm -rf '+image+'.*')
tclean(vis=comb_contms_unflagged, 
      imagename=image, 
      specmode='mfs', 
      gridder='standard',
      deconvolver='multiscale',
      scales = [0, 10, 30, 60, 120, 240, 480], #0, ~1, ~3, ~6, ~12, ~24, ~48 x the beam
      smallscalebias=0.7, 
      weighting='briggs', 
      robust=0.5, ##### Make sure this is what you want
      gain=0.1,
      imsize=2000,
      cell='0.005arcsec', 
      niter = 10000,
      cycleniter=1000,
      interactive = True,
      usemask='user',
      mask='ellipse[[1000pix,1000pix],[2.3arcsec,1.6arcsec],140deg]',
      savemodel='modelcolumn')

# The second invocation of tclen is required to save the model. 
tclean(vis=comb_contms_unflagged, 
      imagename=image, 
      specmode='mfs', 
      gridder='standard',
      calcres=False,
      calcpsf=False,
      interactive = False,
      usemask='user', 
      imsize=2000,
      cell='0.005arcsec', 
      weighting='briggs', 
      robust=0.5, ##### Make sure this is what you want
      mask='',
      savemodel='modelcolumn')

# 7003 iterations
# Beam: 0.070"x0.058", 
# Rms: 41.7 microJy/beam
# peak: 7.5 mJy/beam
# S/N: 180

# First run of phase selfcal: solint=480s
#clearcal(vis=comb_contms_unflagged)
p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+p1)
gaincal(vis=comb_contms_unflagged, 
        caltable=p1, 
        gaintype='T', 
        combine = 'spw,scan', 
        spw='0~23', 
        refant='DA64, DA44, DA63, DA48', 
        calmode='p', 
        solint='480s', 
        minsnr=1.5, 
        minblperant=4)

#plotcal(caltable=p1, 
#        xaxis='time', 
#        yaxis='phase', 
#        subplot=331, 
#        iteration='antenna', 
#        plotrange=[0,0,-180,180],
#        timerange='2017/09/08/22:30:22.5~2017/09/09/00:27:07.7')


applycal(vis=comb_contms_unflagged, 
         spw='0~23', 
         spwmap = [0,0,2,2,4,4,6,6,8,8,10,10,12,12,14,14,16,16,16,16,20,20,20,20], 
         gaintable=[p1], 
         applymode = 'calonly', 
         flagbackup=False, 
         interp = 'linearperobs')

contms_p1 = field+'_'+tag+'_contp1.ms'
os.system('rm -rf '+contms_p1)
split(vis=comb_contms_unflagged, 
      outputvis=contms_p1, 
      datacolumn='corrected', 
      keepflags=False)

# Check the result of the first round of phase selfcal
image = field+'_'+tag+'_p1'
os.system('rm -rf '+image+'.*')
tclean(vis=contms_p1, 
      imagename=image, 
      specmode='mfs', 
      gridder='standard',
      deconvolver='multiscale',
      scales = [0, 10, 30, 60, 120, 240, 480], #0, 1, 3, 6, 12, 24, 48 x the beam
      smallscalebias=0.7, 
      weighting='briggs', 
      robust=0.5,
      gain=0.1,
      imsize=2000,
      cell='0.005arcsec', 
      niter=7003,
      cycleniter=1000,
      interactive = False,
      usemask='user',
      mask='ellipse[[1000pix,1000pix],[2.3arcsec,1.6arcsec],140deg]',
      savemodel='modelcolumn')

# The second invocation of tclen is required to save the model. 
tclean(vis=contms_p1, 
      imagename=image, 
      specmode='mfs', 
      gridder='standard',
      calcres=False,
      calcpsf=False,
      weighting='briggs', 
      robust=0.5,
      imsize=2000,
      cell='0.005arcsec', 
      niter=0,
      interactive = False,
      usemask='user',
      mask='',
      savemodel='modelcolumn')

#7003 iterations
#beam: 0.070"x0.058"
#rms: 30.4 microJy/beam  (-27%)
#peak: 7.7 mJy/beam (+3%)
#S/N: 253 (+41%)

# Second round of phase selfcal: solint=120s
p2 = field+'_'+tag+'.p2'
os.system('rm -rf '+p2)
gaincal(vis=contms_p1, 
        caltable=p2, 
        gaintype='T', 
        combine = 'spw,scan', 
        spw='0~23', 
        refant='DA64, DA44, DA63, DA48', 
        calmode='p', 
        solint='120s', 
        minsnr=1.5, 
        minblperant=4)

#plotcal(caltable=p2, 
#        xaxis='time', 
#        yaxis='phase', 
#        subplot=331, 
#        iteration='antenna', 
#        plotrange=[0,0,-180,180],
#        timerange='2017/09/08/22:30:22.5~2017/09/09/00:27:07.7')

applycal(vis=contms_p1, 
         spw='0~23', 
         spwmap=[0,0,2,2,4,4,6,6,8,8,10,10,12,12,14,14,16,16,16,16,20,20,20,20], 
         gaintable=[p2], 
         applymode='calonly', 
         flagbackup=False, 
         interp='linearperobs')

contms_p2 = field+'_'+tag+'_contp2.ms'
os.system('rm -rf '+contms_p2)
split(vis=contms_p1, 
      outputvis=contms_p2, 
      datacolumn='corrected', 
      keepflags=False)

# Check the result of the second round of phase selfcal
image = field+'_'+tag+'_p2'
os.system('rm -rf '+image+'.*')
tclean(vis=contms_p2, 
      imagename=image,
      specmode='mfs', 
      gridder='standard',
      deconvolver='multiscale',
      scales = [0, 10, 30, 60, 120, 240, 480], #0, 1, 3, 6, 12, 24, 48 x the beam
      smallscalebias=0.7, 
      weighting='briggs', 
      robust=0.5,
      gain=0.1,
      imsize=2000,
      cell='0.005arcsec', 
      niter=7003,
      cycleniter=1000,
      interactive = False,
      usemask='user',
      mask='ellipse[[1000pix,1000pix],[2.3arcsec,1.6arcsec],140deg]',
      savemodel='modelcolumn')

# The second invocation of tclean is required to save the model. 
tclean(vis=contms_p2, 
      imagename=image, 
      specmode='mfs', 
      gridder='standard',
      calcres=False,
      calcpsf=False,
      weighting='briggs', 
      robust=0.5,
      imsize=2000,
      cell='0.005arcsec', 
      niter=0,
      interactive = False,
      usemask='user',
      mask='',
      savemodel='modelcolumn')

#7003 iterations
#beam: 0.070"x0.058"
#rms: 25.6 microJy/beam  (-16%)
#peak: 8.0 mJy/beam (+4%)
#S/N: 312 (+24%)

# Third round of phase selfcal: solint=60s
p3 = field+'_'+tag+'.p3'
os.system('rm -rf '+p3)
gaincal(vis=contms_p2, 
        caltable=p3, 
        gaintype='T', 
        combine = 'spw,scan', 
        spw='0~23', 
        refant='DA64, DA44, DA63, DA48', 
        calmode='p', 
        solint='60s', 
        minsnr=1.5, 
        minblperant=4)

#plotcal(caltable=p3, 
#        xaxis='time', 
#        yaxis='phase', 
#        subplot=331, 
#        iteration='antenna', 
#        plotrange=[0,0,-180,180],
#        timerange='2017/09/08/22:30:22.5~2017/09/09/00:27:07.7')

applycal(vis=contms_p2, 
         spw='0~23', 
         spwmap=[0,0,2,2,4,4,6,6,8,8,10,10,12,12,14,14,16,16,16,16,20,20,20,20], 
         gaintable=[p3], 
         applymode='calonly', 
         flagbackup=False, 
         interp='linearperobs')

contms_p3 = field+'_'+tag+'_contp3.ms'
os.system('rm -rf '+contms_p3)
split(vis=contms_p2, 
      outputvis=contms_p3, 
      datacolumn='corrected', 
      keepflags=False)

# Check the result of the second round of phase selfcal
image = field+'_'+tag+'_p3'
os.system('rm -rf '+image+'.*')
tclean(vis=contms_p3, 
      imagename=image,
      specmode='mfs', 
      gridder='standard',
      deconvolver='multiscale',
      scales = [0, 10, 30, 60, 120, 240, 480], #0, 1, 3, 6, 12, 24, 48 x the beam
      smallscalebias=0.7, 
      weighting='briggs', 
      robust=0.5,
      gain=0.1,
      imsize=2000,
      cell='0.005arcsec', 
      niter=7003,
      cycleniter=1000,
      interactive = False,
      usemask='user',
      mask='ellipse[[1000pix,1000pix],[2.3arcsec,1.6arcsec],140deg]',
      savemodel='modelcolumn')

# The second invocation of tclean is required to save the model. 
tclean(vis=contms_p3, 
      imagename=image, 
      specmode='mfs', 
      gridder='standard',
      calcres=False,
      calcpsf=False,
      weighting='briggs', 
      robust=0.5,
      imsize=2000,
      cell='0.005arcsec', 
      niter=0,
      interactive = False,
      usemask='user',
      mask='',
      savemodel='modelcolumn')

#7003 iterations
#beam: 0.070"x0.058"
#rms: 23.3 microJy/beam  (-9%)
#peak: 8.2 mJy/beam (+2.5%)
#S/N: 352 (+13%)

# Fourth round of phase selfcal: solint=30s
p4 = field+'_'+tag+'.p4'
os.system('rm -rf '+p4)
gaincal(vis=contms_p3, 
        caltable=p4, 
        gaintype='T', 
        combine = 'spw,scan', 
        spw='0~23', 
        refant='DA64, DA44, DA63, DA48', 
        calmode='p', 
        solint='30s', 
        minsnr=1.5, 
        minblperant=4)

#plotcal(caltable=p4, 
#        xaxis='time', 
#        yaxis='phase', 
#        subplot=331, 
#        iteration='antenna', 
#        plotrange=[0,0,-180,180],
#        timerange='2017/09/08/22:30:22.5~2017/09/09/00:27:07.7')

applycal(vis=contms_p3, 
         spw='0~23', 
         spwmap=[0,0,2,2,4,4,6,6,8,8,10,10,12,12,14,14,16,16,16,16,20,20,20,20], 
         gaintable=[p4], 
         applymode='calonly', 
         flagbackup=False, 
         interp='linearperobs')

contms_p4 = field+'_'+tag+'_contp4.ms'
os.system('rm -rf '+contms_p4)
split(vis=contms_p3, 
      outputvis=contms_p4, 
      datacolumn='corrected', 
      keepflags=False)

# Check the result of the second round of phase selfcal
image = field+'_'+tag+'_p4'
os.system('rm -rf '+image+'.*')
tclean(vis=contms_p4, 
      imagename=image,
      specmode='mfs', 
      gridder='standard',
      deconvolver='multiscale',
      scales = [0, 10, 30, 60, 120, 240, 480], #0, 1, 3, 6, 12, 24, 48 x the beam
      smallscalebias=0.7, 
      weighting='briggs', 
      robust=0.5,
      gain=0.1,
      imsize=2000,
      cell='0.005arcsec', 
      niter=7003,
      cycleniter=1000,
      interactive = False,
      usemask='user',
      mask='ellipse[[1000pix,1000pix],[2.3arcsec,1.6arcsec],140deg]',
      savemodel='modelcolumn')

# The second invocation of tclean is required to save the model. 
tclean(vis=contms_p4, 
      imagename=image, 
      specmode='mfs', 
      gridder='standard',
      calcres=False,
      calcpsf=False,
      weighting='briggs', 
      robust=0.5,
      imsize=2000,
      cell='0.005arcsec', 
      niter=0,
      interactive = False,
      usemask='user',
      mask='',
      savemodel='modelcolumn')

#7003 iterations
#beam: 0.070"x0.058"
#rms: 23.2 microJy/beam  (-0.5%)
#peak: 8.4 mJy/beam (+2.4%)
#S/N: 362 (+2.8%)

# Fifth round of phase selfcal: solint=15s
p5 = field+'_'+tag+'.p5'
os.system('rm -rf '+p5)
gaincal(vis=contms_p4, 
        caltable=p5, 
        gaintype='T', 
        combine = 'spw', 
        spw='0~23', 
        refant='DA64, DA44, DA63, DA48', 
        calmode='p', 
        solint='15s', 
        minsnr=1.5, 
        minblperant=4)

#plotcal(caltable=p5, 
#        xaxis='time', 
#        yaxis='phase', 
#        subplot=331, 
#        iteration='antenna', 
#        plotrange=[0,0,-180,180],
#        timerange='2017/09/08/22:30:22.5~2017/09/09/00:27:07.7')

applycal(vis=contms_p4, 
         spw='0~23', 
         spwmap=[0,0,2,2,4,4,6,6,8,8,10,10,12,12,14,14,16,16,16,16,20,20,20,20], 
         gaintable=[p5], 
         applymode='calonly', 
         flagbackup=False, 
         interp='linearperobs')

contms_p5 = field+'_'+tag+'_contp5.ms'
os.system('rm -rf '+contms_p5)
split(vis=contms_p4, 
      outputvis=contms_p5, 
      datacolumn='corrected', 
      keepflags=False)

# Check the result of the second round of phase selfcal
image = field+'_'+tag+'_p5'
os.system('rm -rf '+image+'.*')
tclean(vis=contms_p5, 
      imagename=image,
      specmode='mfs', 
      gridder='standard',
      deconvolver='multiscale',
      scales = [0, 10, 30, 60, 120, 240, 480], #0, 1, 3, 6, 12, 24, 48 x the beam
      smallscalebias=0.7, 
      weighting='briggs', 
      robust=0.5,
      gain=0.1,
      imsize=2000,
      cell='0.005arcsec', 
      niter=7003,
      cycleniter=1000,
      interactive = False,
      usemask='user',
      mask='ellipse[[1000pix,1000pix],[2.3arcsec,1.6arcsec],140deg]',
      savemodel='modelcolumn')

# The second invocation of tclean is required to save the model. 
tclean(vis=contms_p5, 
      imagename=image, 
      specmode='mfs', 
      gridder='standard',
      calcres=False,
      calcpsf=False,
      weighting='briggs', 
      robust=0.5,
      imsize=2000,
      cell='0.005arcsec', 
      niter=0,
      interactive = False,
      usemask='user',
      mask='',
      savemodel='modelcolumn')

#7003 iterations
#beam: 0.070"x0.058"
#rms: 23.4 microJy/beam  (+1.0%)
#peak: 8.5 mJy/beam (+1.2%)
#S/N: 363 (+0.3%)

##################################
# Stopping here with phase selfcal. 
# 
# Performing amp cal
##################################

# First round of amp/phase selfcal: solint=240s
ap1 = field+'_'+tag+'.ap1'
os.system('rm -rf '+ap1)
gaincal(vis=contms_p5, 
        caltable=ap1, 
        gaintype='T', 
        combine = 'spw,scan', 
        spw='0~23', 
        refant='DA64, DA44, DA63, DA48', 
        calmode='ap', 
        solint='240s', 
        minsnr=1.5, 
        minblperant=4)

#plotcal(caltable=ap1, 
#        xaxis='time', 
#        yaxis='phase', 
#        subplot=331, 
#        iteration='antenna', 
#        plotrange=[0,0,0,2],
#        timerange='2017/09/08/22:30:22.5~2017/09/09/00:27:07.7')

applycal(vis=contms_p5, 
         spw='0~23', 
         spwmap=[0,0,2,2,4,4,6,6,8,8,10,10,12,12,14,14,16,16,16,16,20,20,20,20], 
         gaintable=[ap1], 
         applymode='calonly', 
         flagbackup=False, 
         interp='linearperobs')

contms_ap1 = field+'_'+tag+'_contap1.ms'
os.system('rm -rf '+contms_ap1)
split(vis=contms_p5, 
      outputvis=contms_ap1, 
      datacolumn='corrected', 
      keepflags=False)

# Check the result of the second round of phase selfcal
image = field+'_'+tag+'_ap1'
os.system('rm -rf '+image+'.*')
tclean(vis=contms_ap1, 
      imagename=image,
      specmode='mfs', 
      gridder='standard',
      deconvolver='multiscale',
      scales = [0, 10, 30, 60, 120, 240, 480], #0, 1, 3, 6, 12, 24, 48 x the beam
      smallscalebias=0.7, 
      weighting='briggs', 
      robust=0.5,
      gain=0.1,
      imsize=2000,
      cell='0.005arcsec', 
      niter=7003,
      cycleniter=1000,
      interactive = False,
      usemask='user',
      mask='ellipse[[1000pix,1000pix],[2.3arcsec,1.6arcsec],140deg]',
      savemodel='modelcolumn')

# The second invocation of tclean is required to save the model. 
tclean(vis=contms_ap1, 
      imagename=image, 
      specmode='mfs', 
      gridder='standard',
      calcres=False,
      calcpsf=False,
      weighting='briggs', 
      robust=0.5,
      imsize=2000,
      cell='0.005arcsec', 
      niter=0,
      interactive = False,
      usemask='user',
      mask='',
      savemodel='modelcolumn')

#7003 iterations
#beam: 0.070"x0.058"
#rms: 18.6 mmicroJy/beam  (-21%)
#peak: 7.1 mJy/beam (-15%)
#S/N: 382 (+5.2%)

# Second round of amp/phase selfcal: solint=120s
ap2 = field+'_'+tag+'.ap2'
os.system('rm -rf '+ap2)
gaincal(vis=contms_ap1, 
        caltable=ap2, 
        gaintype='T', 
        combine = 'spw,scan', 
        spw='0~23', 
        refant='DA64, DA44, DA63, DA48', 
        calmode='ap', 
        solint='120s', 
        minsnr=1.5, 
        minblperant=4)

#plotcal(caltable=ap2, 
#        xaxis='time', 
#        yaxis='phase', 
#        subplot=331, 
#        iteration='antenna', 
#        plotrange=[0,0,0,2],
#        timerange='2017/09/08/22:30:22.5~2017/09/09/00:27:07.7')

applycal(vis=contms_ap1, 
         spw='0~23', 
         spwmap=[0,0,2,2,4,4,6,6,8,8,10,10,12,12,14,14,16,16,16,16,20,20,20,20], 
         gaintable=[ap2], 
         applymode='calonly', 
         flagbackup=False, 
         interp='linearperobs')

contms_ap2 = field+'_'+tag+'_contap2.ms'
os.system('rm -rf '+contms_ap2)
split(vis=contms_ap1, 
      outputvis=contms_ap2, 
      datacolumn='corrected', 
      keepflags=False)

# Check the result of the second round of phase selfcal
image = field+'_'+tag+'_ap2'
os.system('rm -rf '+image+'.*')
tclean(vis=contms_ap2, 
      imagename=image,
      specmode='mfs', 
      gridder='standard',
      deconvolver='multiscale',
      scales = [0, 10, 30, 60, 120, 240, 480], #0, 1, 3, 6, 12, 24, 48 x the beam
      smallscalebias=0.7, 
      weighting='briggs', 
      robust=0.5,
      gain=0.1,
      imsize=2000,
      cell='0.005arcsec', 
      niter=7003,
      cycleniter=1000,
      interactive = False,
      usemask='user',
      mask='ellipse[[1000pix,1000pix],[2.3arcsec,1.6arcsec],140deg]',
      savemodel='modelcolumn')

# The second invocation of tclean is required to save the model. 
tclean(vis=contms_ap2, 
      imagename=image, 
      specmode='mfs', 
      gridder='standard',
      calcres=False,
      calcpsf=False,
      weighting='briggs', 
      robust=0.5,
      imsize=2000,
      cell='0.005arcsec', 
      niter=0,
      interactive = False,
      usemask='user',
      mask='',
      savemodel='modelcolumn')

#7003 iterations
#beam: 0.070"x0.058"
#rms: 16.6 mmicroJy/beam  (-11%)
#peak: 6.1 mJy/beam (-14%)
#S/N: 367 378 (-3.1%)


##################################
# Final imaging of the continuum
##################################

# using the result after the first round of amplitude calibration


contms=field+'_'+tag+'_contap1.ms'

# delete the pre-existing model generated by tclean
delmod(vis=contms, field=field, otf=True,scr=True)

# Robust=0
image = field+'_'+tag+'_continuum_robust0'
os.system('rm -rf '+image+'.*')
tclean(vis=contms, 
      imagename=image, 
      specmode='mfs', 
      gridder='standard',
      deconvolver='multiscale',
      scales = [0, 10, 30, 60, 120, 240, 480], #0, 1, 3, 6, 12, 24, 48 x the beam
      smallscalebias=0.7, 
      weighting='briggs', 
      robust=0.0,
      gain=0.1,
      imsize=2000,
      cell='0.005arcsec', 
      niter=50000,
      cycleniter=5000,
      interactive=True,
      usemask='user',
      mask='ellipse[[1000pix,1000pix],[2.3arcsec,1.6arcsec],140deg]')

# 29533 iterations
# cleaned flux: 0.724706 Jy
# Beam: 0.049x0.041
# Sidelobes: 26% (no tapering applied)
# rms: 14.3 microJy/beam
# peak: 4.37 mJy/beam
# SNR: 306


# delete the pre-existing model generated by tclean
delmod(vis=contms, field=field, otf=True,scr=True)

# Robust=0.5
image = field+'_'+tag+'_continuum_robust0.5'
os.system('rm -rf '+image+'.*')
tclean(vis=contms, 
      imagename=image, 
      specmode='mfs', 
      gridder='standard',
      deconvolver='multiscale',
      scales = [0, 10, 30, 60, 120, 240, 480], #0, 1, 3, 6, 12, 24, 48 x the beam
      smallscalebias=0.7, 
      weighting='briggs', 
      robust=0.5,
      gain=0.1,
      imsize=2000,
      cell='0.005arcsec', 
      niter=50000,
      cycleniter=10000,
      interactive=True,
      usemask='user',
      mask='ellipse[[1000pix,1000pix],[2.3arcsec,1.6arcsec],140deg]')

# 26069 iterations
# cleaned flux: 0.724199 Jy
# Beam: 0.058x0.050
# Sidelobes: 32% (no tapering applied)
# rms: 13.3 microJy/beam
# peak: 6.05 mJy/beam
# SNR: 455




# Obs ID 7 are  noisier than the other. 
# However, imaging excluding obs 7 leads to very similar results (differences <1%)  

# delete the pre-existing model generated by tclean
delmod(vis=contms, field=field, otf=True,scr=True)

# Robust=0
image = field+'_'+tag+'_continuum_robust0_noobs7'
os.system('rm -rf '+image+'.*')
tclean(vis=contms, 
      observation='0~6,8~9',
      imagename=image, 
      specmode='mfs', 
      gridder='standard',
      deconvolver='multiscale',
      scales = [0, 10, 30, 60, 120, 240, 480], #0, 1, 3, 6, 12, 24, 48 x the beam
      smallscalebias=0.7, 
      weighting='briggs', 
      robust=0.0,
      gain=0.1,
      imsize=2000,
      cell='0.005arcsec', 
      niter=29533,
      cycleniter=5000,
      interactive=False,
      usemask='user',
      mask='ellipse[[1000pix,1000pix],[2.3arcsec,1.6arcsec],140deg]')

# 29533 iterations
# cleaned flux: 0.724706 Jy
# Beam: 0.049x0.041
# Sidelobes: 26% (no tapering applied)
# rms: 14.3 microJy/beam
# peak: 6.09 mJy/beam
# SNR: 426


# delete the pre-existing model generated by tclean
delmod(vis=contms, field=field, otf=True,scr=True)

# Robust=0.5
image = field+'_'+tag+'_continuum_robust0.5_noobs7'
os.system('rm -rf '+image+'.*')
tclean(vis=contms, 
      observation='0~6,8~9', 
      imagename=image, 
      specmode='mfs', 
      gridder='standard',
      deconvolver='multiscale',
      scales = [0, 10, 30, 60, 120, 240, 480], #0, 1, 3, 6, 12, 24, 48 x the beam
      smallscalebias=0.7, 
      weighting='briggs', 
      robust=0.5,
      gain=0.1,
      imsize=2000,
      cell='0.005arcsec', 
      niter=26069,
      cycleniter=5000,
      interactive=False,
      usemask='user',
      mask='ellipse[[1000pix,1000pix],[2.3arcsec,1.6arcsec],140deg]')

# 26069 iterations
# cleaned flux: 0.724199 Jy
# Beam: 0.058x0.050
# Sidelobes: 32% (no tapering applied)
# rms: 13.3 microJy/beam
# peak: 6.05 mJy/beam
# SNR: 455
