"""
This script is written for CASA 4.5.3.  

Note: if you do everything in this script, you'll use up about 260 GB of space.
The final calibrated continuum MS is 4.3 GB.

"""

# Labeling setups
SB_field = 'Elias_24'
LB_field = 'Elias_24'
all_field = 'Elias_24'
SB_tag = 'SB'   
LB_tag = 'LB'
all_tag = 'all'
SB_data = '/data/sandrews/LP/archival/2013.1.00498.S/science_goal.uid___A001_X13a_Xeb/group.uid___A001_X13a_Xec/member.uid___A001_X13a_Xed/calibrated/uid___A002_Xa657ad_X736.ms.split.cal'
LB_data = '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X4c/group.uid___A001_X8c5_X4d/member.uid___A001_X8c5_X4e/calibrated/calibrated_final.ms'
SB_refant = 'DV09'
all_refant = 'DA61, DV24, DV09'
SB_contspws = '0~7'
LB_contspws = '0~7'
all_contspws = '0~15'
SB_mask = 'circle[[239pix,257pix], 1.5arcsec]'
all_mask = 'ellipse[[1465pix, 1372pix], [1.6arcsec,1.4arcsec], 30deg]'


##################################################################
##################################################################
## short baseline (SB) data 
##################################################################
##################################################################

# split out all the data from the given field
SB_ms = SB_field+'_'+SB_tag+'.ms'
os.system('rm -rf '+SB_ms+'*')
split2(vis=SB_data, field=SB_field, outputvis=SB_ms, datacolumn='data')

# @@ initial inspection of data before spectral averaging 
plotms(vis=SB_ms, xaxis='channel', yaxis='amplitude', field=SB_field, 
       ydatacolumn='data', avgtime='1e8', avgscan=True, avgbaseline=True, 
       iteraxis='spw')

# flag CO 2-1 line in SPW1, 13CO 2-1 line in SPW5, and C18O 2-1 line in SPW6
flagmanager(vis=SB_ms, mode='save', versionname='before_cont_flags')
flagchannels = '1:150~250, 5:25~100, 6:790~850'
flagdata(vis=SB_ms, mode='manual', spw=flagchannels, flagbackup=False, 
         field=SB_field)

# spectral averaging for continuum MS
SB_initcont = SB_field+'_'+SB_tag+'_initcont.ms'
os.system('rm -rf '+SB_initcont+'*')
split2(vis=SB_ms, field = '', spw=SB_contspws, outputvis=SB_initcont,
       width=[30,480,8,15,15,240,240,8], datacolumn='data')

# restore flagged channels in the original MS
flagmanager(vis=SB_ms, mode='restore', versionname='before_cont_flags')

# @@ check that amplitude vs. uvdist looks normal
plotms(vis=SB_initcont, xaxis='uvdist', yaxis='amp', coloraxis='spw', 
       avgtime='30', avgchannel='1000')

# @@ inspect individual antenna behaviors 
plotms(vis=SB1_initcont, xaxis='time', yaxis='phase', field=SB_field,
       ydatacolumn='data', avgchannel='16', coloraxis='spw', iteraxis='antenna')

# flag some poor behavior for individual antennas/scans/times
flagdata(vis=SB_initcont, mode='manual', spw='3~4,6', flagbackup=False, 
         field=SB_field, timerange='2015/07/21/22:45:00~2015/07/21/23:10:00', 
         antenna='DA41')
flagdata(vis=SB_initcont, mode='manual', spw='1,3,5', flagbackup=False, 
         field=SB_field, scan='30', antenna='DA46')
flagdata(vis=SB_initcont, mode='manual', spw='3,4,6', flagbackup=False, 
         field=SB_field, scan='30,35', antenna='DA59')
flagdata(vis=SB_initcont, mode='manual', spw='3,4', flagbackup=False, 
         field=SB_field, scan='30', antenna='DV08')
flagdata(vis=SB_initcont, mode='manual', spw='3', flagbackup=False, 
         field=SB_field, scan='30,35', antenna='DV18')


# initial imaging
SB_initcontimage = SB_field+'_'+SB_tag+'_initcontinuum'
os.system('rm -rf '+SB_initcontimage+'.*')
clean(vis=SB_initcont, imagename=SB_initcontimage, mode='mfs', 
      multiscale=[0,10,30], psfmode='clark', imagermode='csclean', 
      weighting='briggs', robust=0.5, gain=0.1, imsize=500, cell='0.03arcsec', 
      mask=SB_mask, interactive=True)
"""
cleaned for 15 cycles (1500 iterations)
peak = 38.5 mJy/beam, flux = 344.7 mJy, rms = 123 uJy/beam, beam = 0.23 x 0.19"
peak SNR = 313

"""
# @@ Gaussian image fit for astrometry later
imfit(imagename=SB_initcontimage+'.image', mask=SB_initcontimage+'.mask')



# SELF-CALIBRATION

# make a copy of the MS
SB_selfcalp0 = SB_field+'_'+SB_tag+'_selfcalp0.ms'
os.system('rm -rf '+SB_selfcalp0)
os.system('cp -r '+SB_initcont+' '+SB_selfcalp0)

# first round of phase-only self-cal
SB_p1 = SB_field+'_'+SB_tag+'.p1'
os.system('rm -rf ' + SB_p1)
gaincal(vis=SB_selfcalp0, caltable=SB_p1, gaintype='T', combine='spw',
        spw=SB_contspws, refant=SB_refant, calmode='p', solint='inf', 
        minsnr=2.0, minblperant=4)

# @@ look at solutions
plotcal(caltable=SB_p1, xaxis='time', yaxis='phase', spw='', 
        iteration='antenna', subplot=221, plotrange=[0,0,-180,180])

# apply the calibration table
applycal(vis=SB_selfcalp0, spw=SB_contspws, spwmap=[0]*8, gaintable=[SB_p1], 
         calwt=True, applymode='calonly', flagbackup=True, interp='linearPD')

# split out the corrected MS for another round
SB_selfcalp1 = SB_field+'_'+SB_tag+'_selfcalp1.ms'
os.system('rm -rf '+SB_selfcalp1)
split2(vis=SB_selfcalp0, outputvis=SB_selfcalp1, datacolumn='corrected')

# imaging
SB_contimagep1 = SB_field+'_'+SB_tag+'_continuump1'
os.system('rm -rf '+SB_contimagep1+'.*')
clean(vis=SB_selfcalp1, imagename=SB_contimagep1, mode='mfs', psfmode='clark',
      imagermode='csclean', weighting='briggs', robust=0.5, gain=0.1, 
      multiscale=[0,10,30], imsize=500, cell='0.03arcsec', mask=SB_mask, 
      interactive=True)
"""
cleaned for 18 cycles (1800 iterations)
peak = 40.7 mJy/beam, flux = 346.6 mJy, rms = 77 uJy/beam, beam = 0.27 x 0.23"
peak SNR = 529

"""

# second round of phase-only self-cal
SB_p2 = SB_field+'_'+SB_tag+'.p2'
os.system('rm -rf '+SB_p2)
gaincal(vis=SB_selfcalp1, caltable=SB_p2, gaintype='T', combine='spw,scans',
        spw=SB_contspws, refant=SB_refant, calmode='p', solint='30s', 
        minsnr=2.0, minblperant=4)

# @@ look at solutions
plotcal(caltable=SB_p2, xaxis='time', yaxis='phase', spw='', 
        iteration='antenna', subplot=221, plotrange=[0,0,-180,180])

# apply the calibration table
applycal(vis=SB_selfcalp1, spw=SB_contspws, spwmap=[0]*8, gaintable=[SB_p2], 
         calwt=True, applymode='calonly', flagbackup=True, interp='linearPD')

# split out corrected MS for another round
SB_selfcalp2 = SB_field+'_'+SB_tag+'_selfcalp2.ms'
os.system('rm -rf '+SB_selfcalp2)
split2(vis=SB_selfcalp1, outputvis=SB_selfcalp2, datacolumn='corrected')

# imaging
SB_contimagep2 = SB_field+'_'+SB_tag+'_continuump2'
os.system('rm -rf '+SB_contimagep2+'.*')
clean(vis=SB_selfcalp2, imagename=SB_contimagep2, mode='mfs', psfmode='clark',
      imagermode='csclean', weighting='briggs', robust=0.5, gain=0.1, 
      multiscale=[0,10,30], imsize=500, cell='0.03arcsec', mask=SB_mask, 
      interactive=True)
"""
cleaned for 20 cycles (2000 iterations)
peak = 41.6 mJy/beam, flux = 346.5 mJy, rms = 75 uJy/beam, beam = 0.23 x 0.19"
peak SNR = 555

"""

# one round of amplitude self-cal
SB_ap1 = SB_field+'_'+SB_tag+'.ap1'
os.system('rm -rf '+SB_ap1)
gaincal(vis=SB_selfcalp2, caltable=SB_ap1, gaintype='T', combine='spw',
        spw=SB_contspws, refant=SB_refant, calmode='ap', gaintable=[SB_p2],
        spwmap=[0]*8, solint='inf', minsnr=3.0, minblperant=4)

# @@ look at solutions
plotcal(caltable=SB_ap1, xaxis='time', yaxis='amp', spw='', 
        iteration='antenna', subplot=221, plotrange=[0,0,0,2])

# apply the calibration tables
applycal(vis=SB_selfcalp2, spw=SB_contspws, spwmap=[[0]*8,[0]*8],
         gaintable=[SB_p2,SB_ap1], calwt=True, applymode='calonly',
         flagbackup=True, interp='linearPD')

# split out a corrected MS
SB_selfcalap1 = SB_field+'_'+SB_tag+'_selfcalap1.ms'
os.system('rm -rf '+SB_selfcalap1)
split2(vis=SB_selfcalp2, outputvis=SB_selfcalap1, datacolumn='corrected')

# imaging
SB_contimageap1 = SB_field+'_'+SB_tag+'_continuumap1'
os.system('rm -rf '+SB_contimageap1+'.*')
clean(vis=SB_selfcalap1, imagename=SB_contimageap1, mode='mfs', 
      psfmode='clark', imagermode='csclean', weighting='briggs', robust=0.5,
      multiscale=[0,10,30], gain=0.1, imsize=500, cell='0.03arcsec', 
      mask=SB_mask, interactive=True)
"""
cleaned for 20 cycles (2000 iterations)
peak = 41.4 mJy/beam, flux = 360.8 mJy, rms = 71 uJy/beam, beam = 0.23 x 0.19"
peak SNR = 583

"""

# @@ Gaussian image fit for astrometry
imfit(imagename=SB_contimageap1+'.image', mask=SB_contimageap1+'.mask')



##################################################################
##################################################################
## initial look at long baseline (LB) data 
##################################################################
##################################################################

# make a local copy of the long-baseline calibrated MS
LB_ms = LB_field+'_'+LB_tag+'.ms'
os.system('rm -rf '+LB_ms+'*')
os.system('cp -r '+LB_data+' '+LB_ms)

# flag the CO 2-1 line (based on its location in in short baseline data)
flagmanager(vis=LB_ms, mode='save', versionname='before_cont_flags')
flagchannels = '3:1880~1970, 7:1880~1970'
flagdata(vis=LB_ms, mode='manual', spw=flagchannels, flagbackup=False,
         field=LB_field)

# spectral and time averaging for continuum MS
LB_initcont = LB_field+'_'+LB_tag+'_initcont.ms'
os.system('rm -rf '+LB_initcont+'*')
split2(vis=LB_ms, field = '', spw=LB_contspws, outputvis=LB_initcont,
       width=[8,8,8,480,8,8,8,480], timebin='6s', datacolumn='data')

# restore flagged CO 2-1 line channels in this MS
flagmanager(vis=LB_ms, mode='restore', versionname='before_cont_flags')

# @@ check that amplitude vs. uvdist looks normal
plotms(vis=LB_initcont, xaxis='uvdist', yaxis='amp', coloraxis='observation',
       avgtime='30', avgchannel='1000')
### pretty good overlap between the EBs

# initial imaging for LB execution block 0 = LB0, 2017/09/25 (C40-9)
LB0_initcontimage = LB_field+'_'+LB_tag+'0_initcontinuum'
os.system('rm -rf '+LB0_initcontimage+'.*')
clean(vis=LB_initcont, imagename=LB0_initcontimage, observation='0', 
      mode='mfs', multiscale=[0,10,25,50,100], psfmode='hogbom', 
      imagermode='csclean', weighting='briggs', robust=0.5, gain=0.3,
      niter=50000, cyclefactor=5, imsize=1800, cell='0.003arcsec',
      interactive=True)
"""
cleaned for 5 cycles (500 iterations); mask defined interactively
peak = 5.6 mJy/beam, flux = 372 mJy, rms = 43 uJy/beam, beam = 50 x 30 mas
peak SNR = 130

"""

# initial imaging for LB execution block 1 = LB1, 2017/11/04 (C43-9)
LB1_initcontimage = LB_field+'_'+LB_tag+'1_initcontinuum'
os.system('rm -rf '+LB1_initcontimage+'.*')
clean(vis=LB_initcont, imagename=LB1_initcontimage, observation='1',
      mode='mfs', multiscale = [0,10,25,50,100], psfmode='hogbom',
      imagermode='csclean', weighting='briggs', robust=0.5, gain=0.3,
      niter=50000, cyclefactor=5, imsize=1800, cell='0.003arcsec',
      mask=LB0_initcontimage+'.mask', interactive=True)
"""
cleaned for 6 cycles (600 iterations)
peak = 4.0 mJy/beam, flux = 369 mJy, rms = 34 uJy/beam, beam = 40 x 30 mas
peak SNR = 118

"""

# @@ Gaussian image fits for astrometry
imfit(imagename=LB0_initcontimage+'.image', mask=LB0_initcontimage+'.mask')
imfit(imagename=LB1_initcontimage+'.image', mask=LB1_initcontimage+'.mask')



##################################################################
##################################################################
## spatial alignment
##################################################################
##################################################################

# Some astrometric analysis to calculate positional shifts before self-cal:

# phase centers (from listobs):
pc_SB  = au.radec2deg('16:26:24.053222, -24.16.14.06099')
pc_LB0 = au.radec2deg('16:26:24.070000, -24.16.13.50000')
pc_LB1 = au.radec2deg('16:26:24.070000, -24.16.13.50000')
# disk centroids (from imfit):
peak_SB  = au.radec2deg('16:26:24.07874, -24.16.13.85641')
peak_LB0 = au.radec2deg('16:26:24.07775, -24.16.13.88381')
peak_LB1 = au.radec2deg('16:26:24.078029, -24.16.13.889894')

# measure position shifts
pkoff_SB  = au.angularSeparation(peak_SB[0], peak_SB[1], pc_SB[0], pc_SB[1],  
                                 True)
pkoff_LB0 = au.angularSeparation(peak_LB0[0], peak_LB0[1], pc_LB0[0], 
                                 pc_LB0[1], True)
pkoff_LB1 = au.angularSeparation(peak_LB1[0], peak_LB1[1], pc_LB1[0], 
                                 pc_LB1[1], True)

# peak offsets relative to phase centers (RA, DEC, RA*COS(DEC)):
# SB  :  +0.3828", +0.2046", +0.3489"
# LB0 :  +0.1162", -0.3838", +0.1060"
# LB1 :  +0.1204", -0.3899", +0.1098"

# measure position shifts
shift_SB_LB0  = au.angularSeparation(peak_LB0[0], peak_LB0[1], peak_SB[0], 
				     peak_SB[1], True)
shift_SB_LB1  = au.angularSeparation(peak_LB1[0], peak_LB1[1], peak_SB[0],
                                     peak_SB[1], True)
shift_LB0_LB1 = au.angularSeparation(peak_LB1[0], peak_LB1[1], peak_LB0[0],
				     peak_LB0[1], True)

# absolute peak shifts between observations
# SB-LB0  : -14.8, -27.4, -13.5 mas
# SB-LB1  : -10.7, -33.5,  -9.7 mas
# LB0-LB1 :  +4.2,  -6.1,  +3.8 mas 

# note the (rough) UTC times of each observation (from listobs)
# ***** THESE NEED TO BE UPDATED *****
# SB  : 2017-05-15 / 15:30
# LB0 : 2017-09-25 / 00:30
# LB1 : 2017-11-04 / 15:30
# delta_t(SB-LB0)  : 0.36 yr
# delta_t(LB0-LB1) : 0.11 yr

# These shifts are on the image pixel scale, so not significant. 
# We do not need to align before trying a combined self-cal solution.  
# The plan is to shift everything to the LB1 position (best measurement).


# still need to align the SB phase center to the LB phase center

# copy self-calibrated MS into new file
SB_shift = SB_field+'_'+SB_tag+'_selfcal_shift.ms'
os.system('rm -rf '+SB_shift)
split2(vis=SB_selfcalap1, outputvis=SB_shift, datacolumn='data')

# do the shift
fixvis(vis=SB_shift, outputvis=SB_shift, field=SB_field,
       phasecenter='ICRS 16h26m24.070000s -24d16m13.50000s')

# @@ check that the MS was properly updated
listobs(SB_shift)

# @@ make an image to see if shift was properly applied:
SB_contimage_shift = SB_field+'_'+SB_tag+'_contimage_shift'
os.system('rm -rf '+SB_contimage_shift+'.*')
clean(vis=SB_shift, imagename=SB_contimage_shift, mode='mfs', psfmode='clark',
      imagermode='csclean', weighting='briggs', robust=0.5, gain=0.1,
      multiscale=[0,10,30], imsize=500, cell='0.03arcsec', mask=SB_mask, 
      interactive=True)
# clean as above

# @@ Gaussian image fit
imfit(imagename=SB_contimage_shift+'.image', mask=SB_contimage_shift+'.mask')


##################################################################
##################################################################
## flux alignment
##################################################################
##################################################################

""" 
Before moving on to a combined self-calibration, I want to check the quality of
the flux calibration by comparing the visibility profiles.  First, I do a full 
spectral average to condense the datasets, then I export the MS into a numpy 
save file using the script 'ExportMS.py' and compare the deprojected, 
azimuthally-averaged visibility profiles.

""" 

# first, for clarity, split the LB observations into their individual EBs
LB0_base = LB_field+'_'+LB_tag+'0.ms'
os.system('rm -rf '+LB0_base+'*')
split2(vis=LB_initcont, observation='0', outputvis=LB0_base, datacolumn='data')

LB1_base = LB_field+'_'+LB_tag+'1.ms'
os.system('rm -rf '+LB1_base+'*')
split2(vis=LB_initcont, observation='1', outputvis=LB1_base, datacolumn='data')

# full spectral averaging + visibility output
os.system('rm -rf '+SB_tag+'_quick.ms*')
split2(vis=SB_shift, field='', spw='', outputvis='SB_quick.ms', 
       width=[4,4,16,4,4,4,4,16], datacolumn='data')
execfile('ExportMS.py')		# for MSname = 'SB_quick'

os.system('rm -rf '+LB_tag+'0_quick.ms*')
split2(vis=LB0_base, field='4', spw='0~3', outputvis='LB0_quick.ms', 
       width=[16,16,16,8], datacolumn='data')
execfile('ExportMS.py')         # for MSname = 'LB0_quick'

os.system('rm -rf '+LB_tag+'1_quick.ms*')
split2(vis=LB1_base, field='4', spw='4~7', outputvis='LB1_quick.ms', 
       width=[16,16,16,8], datacolumn='data')
execfile('ExportMS.py')         # for MSname = 'LB1_quick'

# the phase center offset shared by all these data (more or less)
# (offx, offy) = (+0.118, -0.386)"	[i.e., to the SE]

# Can also make crude estimate of viewing geometry from Gaussian fits:
# deconvolved minor/major axis ratio = 448 / 518 = 0.807, so i = 30.1 degrees.  
# The deconvolved PA = 51.7 degrees.

"""
With that information, we can directly examine the visibility profiles using 
the script 'check_visprofiles.py' (outside CASA).

A comparison of these profiles shows that there is excellent agreement.  No 
rescaling of the flux calibrations are necessary.

"""


##################################################################
##################################################################
## combine data and self-calibration
##################################################################
##################################################################

# concatenate all datasets
ms_list = [SB_shift, LB0_base, LB1_base]
all_concat = LB_field + '_concat.ms'
os.system('rm -rf '+all_concat+'*')
concat(vis=ms_list, concatvis=all_concat)

# set some imaging parameters (useful for experimentation)
robust = 0.5  
gain = 0.1
imsize = 3000
cell = '0.003arcsec'
npercycle = 100
niter = 50000
cyclefactor = 5
multiscale = [0, 20, 40, 80, 160, 320] 

# initial clean
all_initcontimage = all_field +'_'+all_tag+'_initcontinuum'
os.system('rm -rf '+all_initcontimage+'.*')
clean(vis=all_concat, imagename=all_initcontimage, mode='mfs', 
      multiscale=multiscale, psfmode='hogbom', imagermode='csclean',
      weighting='briggs', robust=robust, gain=gain, niter=niter, 
      cyclefactor=cyclefactor, npercycle=npercycle, imsize=imsize, cell=cell, 
      interactive=True, usescratch=True, mask=all_mask)
"""
cleaned for 22 cycles (2200 iterations)
peak: 4.6 mJy/beam, flux: 363 mJy, rms: 19 uJy/beam, beam = 40 x 30 mas
peak SNR: 245
"""

# make a copy of the concatenated MS
all_selfcalp0 = all_field+'_'+all_tag+'_selfcalp0.ms'
os.system('rm -rf '+all_selfcalp0+'*')
os.system('cp -r '+all_concat+' '+all_selfcalp0)

# first round of phase-only self-cal
all_p1 = all_field+'_'+all_tag+'.p1'
os.system('rm -rf '+all_p1)
gaincal(vis=all_selfcalp0, caltable=all_p1, gaintype='T', combine='spw,scan', 
        spw=all_contspws, refant=all_refant, calmode='p', field='0,5',
        solint='300s', minsnr=2.0, minblperant=4)

# @@ look at the solutions
plotcal(caltable=all_p1,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2015/07/20/00~2015/07/22/00')
plotcal(caltable=all_p1,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/09/24/00~2017/09/26/00')
plotcal(caltable=all_p1,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/10/03/00~2017/10/05/00')

# apply the calibration table
applycal(vis=all_selfcalp0, spw=all_contspws, spwmap=[0]*16, 
         gaintable=[all_p1], calwt=True, applymode='calonly', flagbackup=True, 
         interp='linearPD')

# split out a corrected MS for another round
all_selfcalp1 = all_field+'_'+all_tag+'_selfcalp1.ms'
os.system('rm -rf '+all_selfcalp1+'*')
split2(vis=all_selfcalp0, outputvis=all_selfcalp1, datacolumn='corrected')

# image
all_contimagep1 = all_field +'_'+all_tag+'_continuum_p1'
os.system('rm -rf '+all_contimagep1+'.*')
clean(vis=all_selfcalp1, imagename=all_contimagep1, mode='mfs',
      multiscale=multiscale, psfmode='hogbom', imagermode='csclean',
      weighting='briggs', robust=robust, gain=gain, niter=niter,
      cyclefactor=cyclefactor, npercycle=npercycle, imsize=imsize, cell=cell,
      interactive=True, usescratch=True, mask=all_mask)
"""
cleaned for 25 cycles (2500 iterations)
peak: 4.68 mJy/beam, flux: 366 mJy, rms: 18 uJy/beam, beam = 40 x 30 mas
peak SNR: 257

"""

# second round of phase-only self-cal
all_p2 = all_field+'_'+all_tag+'.p2'
os.system('rm -rf '+all_p2)
gaincal(vis=all_selfcalp1, caltable=all_p2, gaintype='T', combine='spw,scan', 
        spw=all_contspws, refant=all_refant, calmode='p', field='0,5',
        solint='120s', minsnr=2.0, minblperant=4)
# flagging about 10-15% of the solutions for low SNR

# @@ look at the solutions
plotcal(caltable=all_p2,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2015/07/20/00~2015/07/22/00')
plotcal(caltable=all_p2,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/09/24/00~2017/09/26/00')
plotcal(caltable=all_p2,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/10/03/00~2017/10/05/00')

# apply the calibration table
applycal(vis=all_selfcalp1, spw=all_contspws, spwmap=[0]*16, 
         gaintable=[all_p2], calwt=True, applymode='calonly', flagbackup=True, 
         interp='linearPD')

# split out a corrected MS for another round
all_selfcalp2 = all_field+'_'+all_tag+'_selfcalp2.ms'
os.system('rm -rf '+all_selfcalp2+'*')
split2(vis=all_selfcalp1, outputvis=all_selfcalp2, datacolumn='corrected')

# image
all_contimagep2 = all_field +'_'+all_tag+'_continuum_p2'
os.system('rm -rf '+all_contimagep2+'.*')
clean(vis=all_selfcalp2, imagename=all_contimagep2, mode='mfs',
      multiscale=multiscale, psfmode='hogbom', imagermode='csclean',
      weighting='briggs', robust=robust, gain=gain, niter=niter,
      cyclefactor=cyclefactor, npercycle=npercycle, imsize=imsize, cell=cell,
      interactive=True, usescratch=True, mask=all_mask)
"""
cleaned for 40 cycles (4000 iterations)
peak: 4.76 mJy/beam, flux: 366 mJy, rms: 18 uJy/beam, beam = 40 x 30 mas
peak SNR: 269

"""

# third round of phase-only self-cal
all_p3 = all_field+'_'+all_tag+'.p3'
os.system('rm -rf '+all_p3)
gaincal(vis=all_selfcalp2, caltable=all_p3, gaintype='T', combine='spw,scan', 
        spw=all_contspws, refant=all_refant, calmode='p', field='0,5',
        solint='60s', minsnr=2.0, minblperant=4)
# flagging about 10-15% of the solutions for low SNR

# @@ look at the solutions
plotcal(caltable=all_p3,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2015/07/20/00~2015/07/22/00')
plotcal(caltable=all_p3,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/09/24/00~2017/09/26/00')
plotcal(caltable=all_p3,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/10/03/00~2017/10/05/00')

# the DA63 and DV08 data for LB1 are crummy; flag them
flagdata(vis=all_selfcalp2, mode='manual', spw='', 
         timerange='2017/10/03/00~2017/10/05/00', flagbackup=False,
         field='', antenna='DA63, DV08')

# apply the calibration table
applycal(vis=all_selfcalp2, spw=all_contspws, spwmap=[0]*16, 
         gaintable=[all_p3], calwt=True, applymode='calonly', flagbackup=True, 
         interp='linearPD')

# split out a corrected MS for another round
all_selfcalp3 = all_field+'_'+all_tag+'_selfcalp3.ms'
os.system('rm -rf '+all_selfcalp3+'*')
split2(vis=all_selfcalp2, outputvis=all_selfcalp3, datacolumn='corrected')

# image
all_contimagep3 = all_field +'_'+all_tag+'_continuum_p3'
os.system('rm -rf '+all_contimagep3+'.*')
clean(vis=all_selfcalp3, imagename=all_contimagep3, mode='mfs',
      multiscale=multiscale, psfmode='hogbom', imagermode='csclean',
      weighting='briggs', robust=robust, gain=gain, niter=niter,
      cyclefactor=cyclefactor, npercycle=npercycle, imsize=imsize, cell=cell,
      interactive=True, usescratch=True, mask=all_mask)
"""
cleaned for 40 cycles (4000 iterations)
peak: 4.92 mJy/beam, flux: 366 mJy, rms: 17 uJy/beam, beam = 50 x 30 mas
peak SNR: 276

"""

# stopping phase-only self-cal here; improvements are modest, and when we go to
# shorter solution intervals there are too many flagged solutions 


# first round of amplitude self-cal
all_ap1 = all_field+'_'+all_tag+'.ap1'
os.system('rm -rf '+all_ap1)
gaincal(vis=all_selfcalp3, caltable=all_ap1, gaintype='T', combine='spw,scan', 
        spw=all_contspws, refant=all_refant, calmode='ap', gaintable=[all_p3],
        spwmap=[0]*16, solint='300s', minsnr=3.0, minblperant=4)

# @@ look at the solutions
plotcal(caltable=all_ap1,xaxis='time',yaxis='amp',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,0,2],
        timerange='2015/07/20/00~2015/07/22/00')
plotcal(caltable=all_ap1,xaxis='time',yaxis='amp',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,0,2],
        timerange='2017/09/24/00~2017/09/26/00')
plotcal(caltable=all_ap1,xaxis='time',yaxis='amp',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,0,2],
        timerange='2017/10/03/00~2017/10/05/00')

# apply calibration tables
applycal(vis=all_selfcalp3, spw=all_contspws, spwmap=[[0]*16,[0]*16],
         gaintable=[all_p3,all_ap1], calwt=True, applymode='calonly', 
         flagbackup=True, interp='linearPD')

# split out a corrected MS 
all_selfcalap1 = all_field+'_'+all_tag+'_selfcalap1.ms'
os.system('rm -rf '+all_selfcalap1)
split2(vis=all_selfcalp3, outputvis=all_selfcalap1, datacolumn='corrected')

# image
all_contimageap1 = all_field +'_'+all_tag+'_continuum_ap1'
os.system('rm -rf '+all_contimageap1+'.*')
clean(vis=all_selfcalap1, imagename=all_contimageap1, mode='mfs',
      multiscale=multiscale, psfmode='hogbom', imagermode='csclean',
      weighting='briggs', robust=robust, gain=gain, niter=niter,
      cyclefactor=cyclefactor, npercycle=npercycle, imsize=imsize, cell=cell,
      interactive=True, usescratch=True, mask=all_mask)
"""
cleaned deep for 60 cycles (6000 iterations); <60 uJy/beam residuals
peak: 4.37 mJy/beam, flux: 379 mJy, rms: 15.6 uJy/beam, beam = 43 x 28 mas
peak SNR = 280.

"""

# split out the "FINAL" self-calibrated MS
all_selfcalfinal = all_field+'_'+'combined'+'_selfcal_final.ms'
os.system('rm -rf '+all_selfcalfinal)
os.system('cp -r '+all_selfcalap1+' '+all_selfcalfinal)


"""
Worthwhile to take a look at the self-calibrated visibilities:

os.system('rm -rf combined_quick.ms*')
split2(vis='Elias_24_combined_selfcal_final.ms', field='0,5', spw='0~15', 
       outputvis='combined_quick.ms', 
       width=[4,4,16,4, 4,4,4,16, 16,16,16,8, 16,16,16,8],
       datacolumn='data')
execfile('ExportMS.py')         # for MSname = 'combined_quick'

Its pretty awesome-looking.

"""


# ***** HAVE NOT PLAYED WITH OPTIMIZING IMAGING ******


# play with the imaging...
# ------ Imaging ------ #
robust = 0.0  
cyclefactor = 5
npercycle = 1000
uvtaper = True
taper0 = ['30mas']
taper1 = ['23mas']
outertaper = taper2
multiscale0 = [0, 20, 40, 80, 120, 360]
multiscale1 = [0, 12, 35, 60]
multiscale2 = [0, 12, 24, 48, 96, 192]
multiscale3 = [0, 12, 24, 48, 96, 192, 384]
multiscale = multiscale0
comments = 'rob00_ms0_taper1'
# --------------------- #

# image
test_image = LB_field +'_'+'all'+'_continuum_'+comments
os.system('rm -rf '+test_image+'.*')
clean(vis=all_selfcalfinal, imagename=test_image, mode='mfs',
      multiscale=multiscale, psfmode='hogbom', imagermode='csclean',
      weighting='briggs', robust=robust, gain=gain, niter=niter,
      cyclefactor=cyclefactor, npercycle=npercycle, imsize=imsize, cell=cell,
      uvtaper=uvtaper, outertaper=outertaper, interactive=True, 
      usescratch=True, mask=all_mask)

"""
Comments on imaging tests:

adjusting the multiscale parameters:
	- ms0 = [0, 20, 40, 80, 120, 360]  # 0, 1.7, 3.4, 6.9, 10.3, 30.9x
				           # the robust = +0.5 beam
	- ms1 = [0, 12, 35, 60]	   	   # 0, 1, 3, 5x beam 
	- ms2 = [0, 12, 24, 48, 96, 192]   # 0, 1, 2, 4, 8, 16x beam
	- ms3 = [0, 12, 24, 48, 96, 192, 384]  # 0, 1, 2, 4, 8, 16, 32x beam

ms1 shows a bit less sharpness around the gap, but that appears to be because 
it recovers a diffuse emission envelope that you can see extending past the 
outer ring (may be real).

ms2 left the lowest clean residuals (and got there with fewest cycles).  But, 
it does not have quite the quality of the default (ms0).  Do not see much 
difference between ms2 and ms3.  


adjusting the robust parameter (for ms0 default):
	- rob05  : robust = +0.5 (default; p4image)
	- rob00  : robust =  0.0 
	- rob-05 : robust = -0.5

rob05 beam (34 x 26 mas) shows a substantial (+) halo of 20% power (and some 
structure) extending out to about 50 mas in radius.  Strong (35%; +) sidelobes 
are present at about 40 mas at PA = +115, +295.  rob05 peak = 2.23 mJy/beam, 
rms = 15.4 uJy/beam; peak SNR = 145.

rob00 beam (28 x 20 mas) shows the same sidelobes, but with much reduced power 
(20%).  The halo structure remains positive, but is substantially reduced (more 
of a speckle pattern now, with peaks at 15% level, about 5% background).  rob00 
peak = 1.40 mJy/beam, rms = 18.6 uJy/beam; peak SNR = 75.  There is no sign of 
additional structures compared to coarser resolution.

rob-05 beam (25 x 17 mas) shows the sidelobes reduced to about 15% power, with 
a near-complete suppression of the halo (but now slightly negative, 5-8%, bowls 
around the core).  rob-05 peak = 1.19 mJy/beam, rms = 25.8 uJy/beam; peak SNR = 
46.  Again I see no new structures.

I did not explore more extreme weighting, given the very low SNR for most of 
the emission.  The optimal solution is to use a taper.


adjusting the taper + robust parameter (for ms0 default):
	- rob-05, taper0 : robust = -0.5, taper = 30mas
	- rob00, taper1  : robust =  0.0, taper = 23mas
	- rob05, taper2  : robust = +0.5, taper = 18mas

With robust = -0.5 and a 30 mas taper (taper0), I get a 35 x 28 mas beam with a 
dramatically improved structure compared to the 34 x 26 mas robust = +0.5 beam 
that provided the best SNR-resolution balance (with sidelobe peaks < 15%, and 
no complicated halo cruff).  peak = 1.98 mJy, rms = 23.2 uJy/beam.  Ugh, that 
is not an improvement: much noisier than default with ugly beam!

With robust = 0.0 and a 23 mas taper (taper1), you get the same 35 x 28 mas 
beam, and a nearly as good beam (sidelobe peaks at 18%, a little more halo 
cruff, but still good).  peak = 1.94 mJy/beam, rms = 17.4 uJy/beam.  

I believe what is happening is that the PSF halo in the default image is a 
beneficial actor in the image, effectively acting as a broader beam to help 
improve the SNR.  But the potential artifacts from the strong sidelobes are 
not ideal, of course.  One possibility is to try a slightly larger beam, given 
that the observed gap is quite wide.  

"""
