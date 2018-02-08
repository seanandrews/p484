"""
This script is written for CASA 5.1.1
"""

###
# To run CASA 5.1.1 version, execute in command line:
# > /home/lperez/casa_5.1.1/casa-release-5.1.1-5.el7/bin/casa
###


##################################################################
##################################################################
## Short baseline data calibrated by ALMA, sent by Sean
##
## This portion covers self-calibration and imaging of the 
## continuum of the short baseline data
##################################################################
##################################################################

SB_data = '../Sean_data_SB/HT_Lup_SB.calibrated_final.ms'

listobs(SB_data)
# Two exec, 14 and 17-May-2017
# 8 spws, 0 and 4 have the CO 2-1 line, others are continuum

field_SB = 'HT_Lup'
tag = 'SB'
SB_refant = 'DA49'

#split out all the data from the given field
SB_ms = field_SB+'_'+tag+'.ms'
os.system('rm -rf ' + SB_ms + '*')
split2(vis=SB_data,
       field = field_SB,    
       outputvis=SB_ms,
       datacolumn='data')

# initial inspection of data before splitting out and averaging the continuum

plotms(vis = SB_ms, xaxis = 'channel', yaxis = 'amplitude', field = field_SB, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')

# spws 0, 4 contain the CO 2-1 line
contspws = '0~7'
flagmanager(vis=SB_ms, mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
flagchannels='0:1720~2120, 4:1720~2120' 
#this flagging is different (wider) from what Jane/Sean did on their script

flagdata(vis=SB_ms,mode='manual', spw=flagchannels, flagbackup=False, field = field_SB)

# Split continuum-only dataset, which has been channel averaged
SB_initcont = field_SB+'_'+tag+'_initcont.ms'
os.system('rm -rf ' + SB_initcont + '*')
split2(vis=SB_ms,
       field = '',
       spw=contspws,      
       outputvis=SB_initcont,
       width=[480,8,8,8, 480, 8, 8, 8],
       datacolumn='data')

# Restore flagged line channels
flagmanager(vis=SB_ms,mode='restore',versionname='before_cont_flags')

# Check that amplitude vs. uvdist looks normal for all spws
plotms(vis=SB_initcont,xaxis='uvdist',yaxis='amp',
       coloraxis='spw', avgtime = '30', avgchannel='1000')
# Check that amplitude vs. uvdist looks normal for both executions (14 and 17-May)
plotms(vis=SB_initcont,xaxis='uvdist',yaxis='amp',
       coloraxis='observation', avgtime = '30', avgchannel='1000')
# Total flux ~0.08 Jy

# Starting selfcalibration of short baselines

# Settled on the folowing parameters for Briggs weighting and cleaning:
# ------ Imaging ------ #
robust = 0.7  # better sidelobes than smaller values
gain = 0.1
imsize = 700
cell = '0.03arcsec'
niter = 160
cycleniter = 20
mask = ''  # define mask interactively
# --------------------- #
# NOTE: HTLup is barely resolved in the shorth baselines, no multiscale used

# Initial clean
SB_initcontimage = field_SB+'_'+tag+'_initcontinuum'
os.system('rm -rf '+SB_initcontimage+'.*')
tclean(vis=SB_initcont, 
       imagename=SB_initcontimage, 
       specmode='mfs', 
       gridder='standard',
       deconvolver='hogbom',
       weighting='briggs', 
       robust=robust,
       gain=gain,
       imsize=imsize,
       cell=cell,
       mask=mask,
       interactive=True,
       niter=niter,
       cycleniter=cycleniter,
       savemodel='modelcolumn')

# cleaned for 8 cycles (160 iterations)
# peak: 52.4 mJy/beam  (2.9 mJy source off to NW)
# rms: 1.26 mJy/beam

SB_selfcalp0 = field_SB+'_'+tag+'_selfcalp0.ms'
os.system('rm -rf '+SB_selfcalp0)
os.system('cp -r ' + SB_initcont + ' ' + SB_selfcalp0)

# First round of phase-only self-cal
# ----------------------------------

# Compute phase solutions
SB_p1 = field_SB+'_'+tag+'.p1'
os.system('rm -rf '+SB_p1)
gaincal(vis=SB_selfcalp0, caltable=SB_p1, gaintype='T', combine = 'spw', 
        spw=contspws, refant=SB_refant, calmode='p', 
        solint='inf', minsnr=1.5, minblperant=4)

# Plot phase solutions
plotcal(caltable=SB_p1,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=331,plotrange=[0,0,-180,180])

# Apply phase solutions
applycal(vis=SB_selfcalp0, gaintable=[SB_p1], spw=contspws,
         interp='linearPD', spwmap = [0,0,0,0,4,4,4,4], calwt=True, 
         applymode = 'calonly', flagbackup=True)

# Split dataset with the first selfcalibration applied
SB_selfcalp1 = field_SB+'_'+tag+'_selfcalp1.ms'
os.system('rm -rf '+SB_selfcalp1)
split2(vis=SB_selfcalp0, outputvis=SB_selfcalp1, datacolumn='corrected')

# Update clean/imaging parameters
niter=2000
cycleniter = 50
threshold='0.043mJy'
mask = ''  # define mask interactively

# Clean after first selfcal
SB_contimagep1 = field_SB+'_'+tag+'_continuump1'
os.system('rm -rf '+SB_contimagep1+'.*')
tclean(vis=SB_selfcalp1, 
       imagename=SB_contimagep1, 
       specmode='mfs', 
       gridder='standard',
       deconvolver='hogbom',
       weighting='briggs', 
       robust=robust,
       gain=gain,
       imsize=imsize,
       cell=cell, 
       mask=mask,
       interactive=True,
       niter=niter,
       cycleniter=cycleniter,
       threshold=threshold,
       savemodel='modelcolumn')

# cleaned for 33 cycles (1600 iterations)
# peak: 57.1 mJy/beam  (3.3 mJy source off to NW)
# rms: 42.9 microJy/beam

# Compare SNR improvement:
peak2 = imstat(imagename=SB_contimagep1+'.image')['max'][0]
noise2 = imstat(imagename=SB_contimagep1+'.image',
       region='annulus[[352pix,345pix],[220pix,400pix]]')['rms'][0]
peak1 = imstat(imagename=SB_initcontimage+'.image')['max'][0]
noise1 = imstat(imagename=SB_initcontimage+'.image',
       region='annulus[[352pix,345pix],[220pix,400pix]]')['rms'][0]
print "# SNR before = ", peak1/noise1, '\n', "# SNR after = ", peak2/noise2, '\n', "# Peak improvement factor", peak2/peak1,'\n', "# Noise reduction factor", noise1/noise2
# SNR before =  416.78657199 
# SNR after =  1330.96865361 
# Peak improvement factor 1.08962679544 
# Noise reduction factor 2.93073353811

# Second round of phase-only self-cal
# -----------------------------------

# Compute phase solutions
SB_p2 = field_SB+'_'+tag+'.p2'
os.system('rm -rf '+SB_p2)
gaincal(vis=SB_selfcalp1, caltable=SB_p2, gaintype='T', combine = 'spw', 
        spw=contspws, refant=SB_refant, calmode='p', 
        solint='30s', minsnr=1.5, minblperant=4)

# Plot phase solutions
plotcal(caltable=SB_p2,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=331,plotrange=[0,0,-180,180])

# Apply phase solutions
applycal(vis=SB_selfcalp1, gaintable=[SB_p2], spw=contspws,
         interp='linearPD', spwmap = [0,0,0,0,4,4,4,4], calwt=True, 
         applymode = 'calonly', flagbackup=True)

# Split dataset with the second selfcalibration applied
SB_selfcalp2 = field_SB+'_'+tag+'_selfcalp2.ms'
os.system('rm -rf '+SB_selfcalp2)
split2(vis=SB_selfcalp1, outputvis=SB_selfcalp2, datacolumn='corrected')

# Update clean/imaging parameters
niter=2000
cycleniter = 100
threshold='0.043mJy'
mask=SB_contimagep1+'.mask'

# Clean after second selfcal
SB_contimagep2 = field_SB+'_'+tag+'_continuump2'
os.system('rm -rf '+SB_contimagep2+'.*')
tclean(vis=SB_selfcalp2, 
       imagename=SB_contimagep2, 
       specmode='mfs', 
       gridder='standard',
       deconvolver='hogbom',
       weighting='briggs', 
       robust=robust,
       gain=gain,
       imsize=imsize,
       cell=cell, 
       mask=mask,
       interactive=True,
       niter=niter,
       cycleniter=cycleniter,
       threshold=threshold,
       savemodel='modelcolumn')

# cleaned for 18 cycles (1800 iterations)
# peak: 58.0 mJy/beam  (3.4 mJy source off to NW)
# rms: 42.2 microJy/beam

# Compare SNR improvement:
peak2 = imstat(imagename=SB_contimagep2+'.image')['max'][0]
noise2 = imstat(imagename=SB_contimagep2+'.image',
       region='annulus[[352pix,345pix],[220pix,400pix]]')['rms'][0]
peak1 = imstat(imagename=SB_contimagep1+'.image')['max'][0]
noise1 = imstat(imagename=SB_contimagep1+'.image',
       region='annulus[[352pix,345pix],[220pix,400pix]]')['rms'][0]
print "# SNR before = ", peak1/noise1, '\n', "# SNR after = ", peak2/noise2, '\n', "# Peak improvement factor", peak2/peak1,'\n', "# Noise reduction factor", noise1/noise2
# SNR before =  1330.96865361 
# SNR after =  1373.4203851 
# Peak improvement factor 1.01450430787 
# Noise reduction factor 1.01714241857

# Third round of phase-only self-cal
# -----------------------------------

# Compute phase solutions
SB_p3 = field_SB+'_'+tag+'.p3'
os.system('rm -rf '+SB_p3)
gaincal(vis=SB_selfcalp2, caltable=SB_p3, gaintype='T', combine = 'spw', 
        spw=contspws, refant=SB_refant, calmode='p', 
        solint='12s', minsnr=1.5, minblperant=4)

# Plot phase solutions
plotcal(caltable=SB_p3,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=331,plotrange=[0,0,-180,180])

# Apply phase solutions
applycal(vis=SB_selfcalp2, gaintable=[SB_p3], spw=contspws,
         interp='linearPD', spwmap = [0,0,0,0,4,4,4,4], calwt=True, 
         applymode = 'calonly', flagbackup=True)

# Split dataset with the second selfcalibration applied
SB_selfcalp3 = field_SB+'_'+tag+'_selfcalp3.ms'
os.system('rm -rf '+SB_selfcalp3)
split2(vis=SB_selfcalp2, outputvis=SB_selfcalp3, datacolumn='corrected')

# Update clean/imaging parameters
niter=2000
cycleniter = 100
threshold='0.042mJy'
mask=SB_contimagep2+'.mask'

# Clean after second selfcal
SB_contimagep3 = field_SB+'_'+tag+'_continuump3'
os.system('rm -rf '+SB_contimagep3+'.*')
tclean(vis=SB_selfcalp3, 
       imagename=SB_contimagep3, 
       specmode='mfs', 
       gridder='standard',
       deconvolver='hogbom',
       weighting='briggs', 
       robust=robust,
       gain=gain,
       imsize=imsize,
       cell=cell, 
       mask=mask,
       interactive=True,
       niter=niter,
       cycleniter=cycleniter,
       threshold=threshold,
       savemodel='modelcolumn')

# cleaned for 18 cycles (1800 iterations)
# peak: 58.34 mJy/beam  (3.4 mJy source off to NW)
# rms: 42.3 microJy/beam

# Compare SNR improvement:
peak2 = imstat(imagename=SB_contimagep3+'.image')['max'][0]
noise2 = imstat(imagename=SB_contimagep3+'.image',
       region='annulus[[352pix,345pix],[220pix,400pix]]')['rms'][0]
peak1 = imstat(imagename=SB_contimagep2+'.image')['max'][0]
noise1 = imstat(imagename=SB_contimagep2+'.image',
       region='annulus[[352pix,345pix],[220pix,400pix]]')['rms'][0]
print "# SNR before = ", peak1/noise1, '\n', "# SNR after = ", peak2/noise2, '\n', "# Peak improvement factor", peak2/peak1,'\n', "# Noise reduction factor", noise1/noise2
# SNR before =  1373.4203851 
# SNR after =  1379.27165542 
# Peak improvement factor 1.00648322059 
# Noise reduction factor 0.997791461531

# Small improvement, moving on to amplitude selfcal

# First round of amplitude self-cal
# ---------------------------------

# Compute amplitude solutions
SB_ap1 = field_SB+'_'+tag+'.ap1'
os.system('rm -rf '+SB_ap1)
gaincal(vis=SB_selfcalp3, caltable=SB_ap1, gaintype='T', combine = 'spw', 
        spw=contspws, refant=SB_refant, calmode='ap',
        solint='inf', minsnr=3.0, minblperant=4)

# Plot amplitude solutions
plotcal(caltable=SB_ap1,xaxis='time',yaxis='amp',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,0,0])
plotcal(caltable=SB_ap1,xaxis='time',yaxis='phase',
        spw='',iteration='',subplot=111,plotrange=[0,0,-180,180])

# Apply amplitude solutions
applycal(vis=SB_selfcalp3, gaintable=[SB_ap1], spw=contspws,
         interp='linearPD', spwmap = [0,0,0,0,4,4,4,4], 
         calwt=True, applymode = 'calonly', flagbackup=True)

# Split dataset with the first amp selfcalibration applied
SB_selfcalap1 = field_SB+'_'+tag+'_selfcalap1.ms'
os.system('rm -rf '+SB_selfcalap1)
split2(vis=SB_selfcalp3, outputvis=SB_selfcalap1, datacolumn='corrected')

# Update clean/imaging parameters
niter=3000
cycleniter = 100
threshold='0.037mJy'
mask=SB_contimagep3+'.mask'

# Clean after second selfcal
SB_contimageap1 = field_SB+'_'+tag+'_continuumap1'
os.system('rm -rf '+SB_contimageap1+'.*')
tclean(vis=SB_selfcalap1, 
       imagename=SB_contimageap1, 
       specmode='mfs', 
       gridder='standard',
       deconvolver='hogbom',
       weighting='briggs', 
       robust=robust,
       gain=gain,
       imsize=imsize,
       cell=cell, 
       mask=mask,
       interactive=True,
       niter=niter,
       cycleniter=cycleniter,
       threshold=threshold,
       savemodel='modelcolumn')

# cleaned for 25 cycles (2500 iterations)
# peak: 58.35 mJy/beam  (3.4 mJy source off to NW)
# rms: 36.4 microJy/beam

# Compare SNR improvement:
peak2 = imstat(imagename=SB_contimageap1+'.image')['max'][0]
noise2 = imstat(imagename=SB_contimageap1+'.image',
       region='annulus[[352pix,345pix],[220pix,400pix]]')['rms'][0]
peak1 = imstat(imagename=SB_contimagep3+'.image')['max'][0]
noise1 = imstat(imagename=SB_contimagep3+'.image',
       region='annulus[[352pix,345pix],[220pix,400pix]]')['rms'][0]
print "# SNR before = ", peak1/noise1, '\n', "# SNR after = ", peak2/noise2, '\n', "# Peak improvement factor", peak2/peak1,'\n', "# Noise reduction factor", noise1/noise2
# SNR before =  1379.27165542 
# SNR after =  1604.20044186 
# Peak improvement factor 1.0001429009 
# Noise reduction factor 1.16291176334

# Further amp selfcal does not improve the SNR of the data
# Will conclude the short baselines self-calibration here!

