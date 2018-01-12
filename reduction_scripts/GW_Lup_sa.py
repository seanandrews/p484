"""
This script is written for CASA 4.5.3.  

Note: if you do everything in this script, you'll use up about 260 GB of space.
The final calibrated continuum MS is 4.3 GB.

"""

# Labeling setups
SB_field = 'GW_Lup'
LB_field = 'GW_Lup'
all_field = 'GW_Lup'
SB_tag = 'SB'   
LB_tag = 'LB'
all_tag = 'all'
SB_data = '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_Xbd4641_X1e/group.uid___A001_Xbd4641_X1f/member.uid___A001_Xbd4641_X20/calibrated/calibrated_final.ms'
LB_data = '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X80/group.uid___A001_X8c5_X81/member.uid___A001_X8c5_X82/calibrated/calibrated_final.ms'
SB_refant = 'DA49'
LB_refant = 'DV24'
all_refant = 'DV24, DA57, DV09, DA49'
SB_contspws = '0~7'
LB_contspws = '0~7'
all_contspws = '0~15'
SB_mask = 'circle[[257pix,244pix],0.9arcsec]'
all_mask = 'ellipse[[1580pix, 1442pix], [1.2arcsec,1.0arcsec], 42deg]'


##################################################################
##################################################################
## short baseline (SB) data 
##################################################################
##################################################################

# split out all the data from the given field
SB_ms = SB_field+'_'+SB_tag+'.ms'
os.system('rm -rf '+SB_ms+'*')
split2(vis=SB_data, field = SB_field, outputvis=SB_ms, datacolumn='data')

# @@ initial inspection of data before spectral averaging 
plotms(vis=SB_ms, xaxis='channel', yaxis='amplitude', field=SB_field, 
       ydatacolumn='data', avgtime='1e8', avgscan=True, avgbaseline=True, 
       iteraxis='spw')

# flag the CO 2-1 line
flagmanager(vis=SB_ms, mode='save', versionname='before_cont_flags')
flagchannels = '0:1730~2130, 4:1730~2130' 
flagdata(vis=SB_ms, mode='manual', spw=flagchannels, flagbackup=False, 
         field=SB_field)

# spectral averaging for continuum MS
SB_initcont = SB_field+'_'+SB_tag+'_initcont.ms'
os.system('rm -rf '+SB_initcont+'*')
split2(vis=SB_ms, field = '', spw=SB_contspws, outputvis=SB_initcont,
       width=[480,8,8,8,480,8,8,8], datacolumn='data')

# restore flagged CO 2-1 line channels in the original MS
flagmanager(vis=SB_ms, mode='restore', versionname='before_cont_flags')

# @@ check that amplitude vs. uvdist looks normal
plotms(vis=SB_initcont, xaxis='uvdist', yaxis='amp', coloraxis='spw', 
       avgtime='30', avgchannel='1000')
### both EBs have good overlap (relative flux calibration should be fine)

# initial imaging
SB_initcontimage = SB_field+'_'+SB_tag+'_initcontinuum'
os.system('rm -rf '+SB_initcontimage+'.*')
clean(vis=SB_initcont, imagename=SB_initcontimage, mode='mfs', 
      psfmode='clark', imagermode='csclean', weighting='briggs', robust=0.5,
      gain=0.1, imsize=500, cell='0.03arcsec', mask=SB_mask, interactive=True)
"""
cleaned for 11 cycles (1100 iterations)
peak = 20.3 mJy/beam, flux = 87.8 mJy, rms = 60 uJy/beam, beam = 0.27 x 0.23"
peak SNR = 338

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
      imsize=500, cell='0.03arcsec', mask=SB_mask, interactive=True)
"""
cleaned for 11 cycles (1100 iterations)
peak = 21.3 mJy/beam, flux = 89.2 mJy, rms = 34 uJy/beam, beam = 0.27 x 0.23"
peak SNR = 626

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
      imsize=500, cell='0.03arcsec', mask=SB_mask, interactive=True)
"""
cleaned for 11 cycles (1100 iterations)
peak = 21.5 mJy/beam, flux = 90.2 mJy, rms = 32 uJy/beam, beam = 0.27 x 0.23"
peak SNR = 672

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
      gain=0.1, imsize=500, cell='0.03arcsec', mask=SB_mask, interactive=True)
"""
cleaned for 19 cycles (1900 iterations)
peak = 21.7 mJy/beam, flux = 89.1 mJy, rms = 32 uJy/beam, beam = 0.27 x 0.23"
peak SNR = 678

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

# somehow the field name was changed from the short baseline data; fix that
au.editFieldname(LB_ms, 'GW_Lupi', LB_field)

# flag the CO 2-1 line (based on its location in in short baseline data)
flagmanager(vis=LB_ms, mode='save', versionname='before_cont_flags')
flagchannels = '3:1730~2130, 7:1730~2130'
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
### the overlap is not perfect between the EBs: this is a flux calibration 
### issue that will need to be checked later.

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
peak = 19.0 mJy/beam, flux = 85.9 mJy, rms = 32 uJy/beam, beam = 70 x 20 mas
peak SNR = 594

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
peak = 1.2 mJy/beam, flux = 56.8 mJy, rms = 17 uJy/beam, beam = 30 x 20 mas
peak SNR = 71

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
pc_SB  = au.radec2deg('15:46:44.728331, -34.30.35.91329')
pc_LB0 = au.radec2deg('15:46:44.728275, -34.30.35.92201')
pc_LB1 = au.radec2deg('15:46:44.728258, -34.30.35.92466')
# disk centroids (from imfit):
peak_SB  = au.radec2deg('15:46:44.709370, -34.30.36.110732')
peak_LB0 = au.radec2deg('15:46:44.71184, -34.30.36.08622')
peak_LB1 = au.radec2deg('15:46:44.70900, -34.30.36.09304')

# measure position shifts
pkoff_SB  = au.angularSeparation(peak_SB[0], peak_SB[1], pc_SB[0], pc_SB[1],  
                                 True)
pkoff_LB0 = au.angularSeparation(peak_LB0[0], peak_LB0[1], pc_LB0[0], 
                                 pc_LB0[1], True)
pkoff_LB1 = au.angularSeparation(peak_LB1[0], peak_LB1[1], pc_LB1[0], 
                                 pc_LB1[1], True)

# peak offsets relative to phase centers (RA, DEC, RA*COS(DEC)):
# SB  :  -0.2844", -0.1974", -0.2344"
# LB0 :  -0.2465", -0.1642", -0.2031"
# LB1 :  -0.2889", -0.1684", -0.2380"

# measure position shifts
shift_SB_LB0  = au.angularSeparation(peak_LB0[0], peak_LB0[1], peak_SB[0], 
				     peak_SB[1], True)
shift_SB_LB1  = au.angularSeparation(peak_LB1[0], peak_LB1[1], peak_SB[0],
                                     peak_SB[1], True)
shift_LB0_LB1 = au.angularSeparation(peak_LB1[0], peak_LB1[1], peak_LB0[0],
				     peak_LB0[1], True)

# absolute peak shifts between observations
# SB-LB0  : +37.1, +24.5, +30.5 mas
# SB-LB1  :  -5.5, +17.7,  -4.6 mas
# LB0-LB1 : -42.6,  -6.8, -35.1 mas  (i.e., you can *see* this)

# note the (rough) UTC times of each observation (from listobs)
# SB  : 2017-05-15 / 15:30
# LB0 : 2017-09-25 / 00:30
# LB1 : 2017-11-04 / 15:30
# delta_t(SB-LB0)  : 0.36 yr
# delta_t(LB0-LB1) : 0.11 yr

# These shifts are on the LB beam scale, so pretty significant.  The implied 
# proper motions are nonsense, well off the USNO data (Zacharias et al 2010).  
# This suggests the shifts are probably due to the atmosphere.  

# We need to manually align before trying a combined self-cal solution.  
# The plan is to shift everything to the LB1 position (best measurement).


# manual astrometric shift for the SB data

# copy self-calibrated MS into new file
SB_shift = SB_field+'_'+SB_tag+'_selfcal_shift.ms'
os.system('rm -rf '+SB_shift)
split2(vis=SB_selfcalap1, outputvis=SB_shift, datacolumn='data')

# compute shifted phase center to account for offsets
ra_SB_new  = pc_SB[0] - shift_SB_LB1[1]
dec_SB_new = pc_SB[1] - shift_SB_LB1[2] 

# do the shift
au.deg2radec(ra_SB_new, dec_SB_new)
# 	15:46:44.728701, -34:30:35.93098
fixvis(vis=SB_shift, outputvis=SB_shift, field=SB_field,
       phasecenter='ICRS 15h46m44.728701s -34d30m35.93098s')

# @@ check that the MS was properly updated
listobs(SB_shift)

# now re-assign to the LB1 phase center (must be in J2000)
radec_pc_LB1 = au.deg2radec(pc_LB1[0], pc_LB1[1])
au.ICRSToJ2000(radec_pc_LB1)
# Separation: radian = 7.81484e-08, degrees = 0.000004, arcsec = 0.016119
#  Out[233]: '15:46:44.72877, -034:30:35.909835'
fixplanets(vis=SB_shift, field=SB_field, 
           direction='J2000 15h46m44.72877s -34d30m35.909835s')

# @@ check that the MS was properly updated
listobs(SB_shift)

# @@ make an image to see if shift was properly applied:
SB_contimage_shift = SB_field+'_'+SB_tag+'_contimage_shift'
os.system('rm -rf '+SB_contimage_shift+'.*')
clean(vis=SB_shift, imagename=SB_contimage_shift, mode='mfs', psfmode='clark',
      imagermode='csclean', weighting='briggs', robust=0.5, gain=0.1,
      imsize=500, cell='0.03arcsec', mask=SB_mask, interactive=True)
# clean as above

# @@ Gaussian image fit
imfit(imagename=SB_contimage_shift+'.image', mask=SB_contimage_shift+'.mask')


# manual astrometric shift for the LB0 data

# split the LB0 data into a new MS
LB0_shift = LB_field+'_'+LB_tag+'0_shift.ms'
os.system('rm -rf '+LB0_shift)
split2(vis=LB_initcont, outputvis=LB0_shift, observation='0', 
       datacolumn='data')

# compute shifted phase center to account for offsets
ra_LB0_new  = pc_LB0[0] - shift_LB0_LB1[1]
dec_LB0_new = pc_LB0[1] - shift_LB0_LB1[2]

# do the shift
au.deg2radec(ra_LB0_new, dec_LB0_new)
#	15:46:44.731115, -34:30:35.91519
fixvis(vis=LB0_shift, outputvis=LB0_shift, field='5',
       phasecenter='ICRS 15h46m44.731115s -34d30m35.91519s')

# @@ check that the MS was properly updated
listobs(LB0_shift)

# now re-assign the phase center
fixplanets(vis=LB0_shift, field='5',
           direction='J2000 15h46m44.72877s -34d30m35.909835s')

# @@ check that the MS was properly updated
listobs(LB0_shift)

# @@ make an image to see if shift was properly applied:
LB0_contimage_shift = LB_field+'_'+LB_tag+'0_contimage_shift'
os.system('rm -rf '+LB0_contimage_shift+'.*')
clean(vis=LB0_shift, imagename=LB0_contimage_shift, field='5', mode='mfs',
      multiscale = [0,10,25,50,100], psfmode='hogbom', imagermode='csclean',
      weighting='briggs', robust=0.5, gain=0.3, niter=50000, cyclefactor=5,
      imsize=1800, cell='0.003arcsec', interactive=True)
# clean as before

# @@ Gaussian image fits for astrometry
imfit(imagename=LB0_contimage_shift+'.image', mask=LB0_contimage_shift+'.mask')


# We are not doing a shift on LB1 (our reference position), but we need to 
# split it out as its own MS and convert it to the appropriate J2000 frame

# split the LB1 data (only) into a new MS
LB1_ref = LB_field+'_'+LB_tag+'1_ref.ms'
os.system('rm -rf '+LB1_ref)
split2(vis=LB_initcont, outputvis=LB1_ref, observation='1', datacolumn='data')

# now re-assign the phase center
fixplanets(vis=LB1_ref, field='7',
           direction='J2000 15h46m44.72877s -34d30m35.909835s')

# @@ check that the MS was properly updated
listobs(LB1_ref)

# @@ make an image to check
LB1_contimage_ref = LB_field+'_'+LB_tag+'1_contimage_ref'
os.system('rm -rf '+LB1_contimage_ref+'.*')
clean(vis=LB1_ref, imagename=LB1_contimage_ref, field='7', mode='mfs',
      multiscale = [0,10,25,50,100], psfmode='hogbom', imagermode='csclean',
      weighting='briggs', robust=0.5, gain=0.3, niter=50000, cyclefactor=5,
      imsize=1800, cell='0.003arcsec', interactive=True)

# @@ Gaussian image fits 
imfit(imagename=LB1_contimage_ref+'.image', mask=LB1_contimage_ref+'.mask')


# Now we can compare the astrometric alignment of the peaks (J2000):
#  SB : RA = 15:46:44.70944 +/- 0.00006s, DEC = -34:30:36.08958 +/- 0.00079"
# LB0 : RA = 15:46:44.70950 +/- 0.00021s, DEC = -34:30:36.08051 +/- 0.00253"
# LB1 : RA = 15:46:44.70938 +/- 0.00019s, DEC = -34:30:36.07790 +/- 0.00240"

# There are small residual peak offsets:
pc_all   = au.radec2deg('15:46:44.728331, -34.30.35.91329')	# = LB1
peak_SB  = au.radec2deg('15:46:44.709440, -34.30.36.089576')
peak_LB0 = au.radec2deg('15:46:44.70950, -34.30.36.08051')
peak_LB1 = au.radec2deg('15:46:44.70938, -34.30.36.07790')
resid_SB_LB0  = au.angularSeparation(peak_LB0[0], peak_LB0[1], peak_SB[0],
                                     peak_SB[1], True)
resid_SB_LB1  = au.angularSeparation(peak_LB1[0], peak_LB1[1], peak_SB[0],
                                     peak_SB[1], True)
resid_LB0_LB1 = au.angularSeparation(peak_LB1[0], peak_LB1[1], peak_LB0[0],
                                     peak_LB0[1], True)
"""
There is a 12 mas residual offset between SB and LB1, which is attributable to 
pixelization (i.e., not obviously real); some experiments confirm that 
sub-pixel shifts like the one we've done can produce positional shifts of about 
half a pixel width, which is consistent with what we see here.  The LB0--LB1 
residual is now shrunk to 3 mas, 1 pixel.  

"""


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

# full spectral averaging + visibility output
os.system('rm -rf '+SB_tag+'_quick.ms*')
split2(vis=SB_shift, field='', spw='', outputvis='SB_quick.ms', 
       width=[8,16,16,16,8,16,16,16], datacolumn='data')
execfile('ExportMS.py')		# for MSname = 'SB_quick'

os.system('rm -rf '+LB_tag+'0_quick.ms*')
split2(vis=LB0_shift, field='5', spw='0~3', outputvis='LB0_quick.ms', 
       width=[16,16,16,8], datacolumn='data')
execfile('ExportMS.py')         # for MSname = 'LB0_quick'

os.system('rm -rf '+LB_tag+'1_quick.ms*')
split2(vis=LB1_ref, field='7', spw='4~7', outputvis='LB1_quick.ms', 
       width=[16,16,16,8], datacolumn='data')
execfile('ExportMS.py')         # for MSname = 'LB1_quick'

# define the phase center offset shared by all these data (more or less)
off = au.angularSeparation(peak_LB1[0], peak_LB1[1], pc_all[0], pc_all[1], True)
# (offx, offy) = (-0.2843, -0.1646)"	[i.e., to the SW]

# Can also make crude estimate of viewing geometry from Gaussian fits:
# deconvolved minor/major axis ratio = 313 / 388 = 0.807, so i = 36.2 degrees.  
# The deconvolved PA = 41.8 degrees.

"""
With that information, we can directly examine the visibility profiles using 
the script 'check_visprofiles.py' (outside CASA).

A comparison of these profiles shows that there is non-trivial discrepancies 
between the flux calibrations.  If we use SB as a reference, then we find that 
LB0 is too low (by about 5%) and LB1 is much too low (by about 30%).  However, 
we do not a priori know which calibration is "right".  

For the flux (amplitude) calibration, the pipeline used:
	 SB:  J1427-4206, mean Fnu = 1.78 Jy @ 238.8 GHz
	      J1517-2422, mean Fnu = 2.10 Jy @ 238.8 GHz
	LB0:  J1733-1304, mean Fnu = 1.86 Jy @ 238.7 GHz
	LB1:  J1427-4206, mean Fnu = 2.32 Jy @ 238.8 GHz

Updated queries (see below) find:
	 SB:  J1427-4206, Fnu = 1.80 +/- 0.16 Jy
              J1517-2422, Fnu = 2.05 +/- 0.16 Jy
	LB0:  J1733-1304, Fnu = 1.89 +/- 0.17 Jy
	LB1:  J1427-4206, Fnu = 2.45 +/- 0.14 Jy

au.getALMAFlux('J1427-4206', 232.8, date='2017/05/14')
au.getALMAFlux('J1517-2422', 232.8, date='2017/05/17')
au.getALMAFlux('J1733-1304', 232.7, date='2017/09/25')
au.getALMAFlux('J1427-4206', 232.8, date='2017/11/04')

So, this suggests that the SB and LB0 calibrations are actually pretty much 
fine.  The LB1 calibration is low, but it does not seem off enough to produce 
the large scaling discrepancy seen in the GW Lup visibilities.  

We will manually scale the LB1 flux calibration up into alignment.

"""

# re-scale the LB1 flux calibration
sf = 1./sqrt(1.3)
os.system('rm -rf scale_LB1.gencal*')
gencal(vis=LB1_ref, caltable='scale_LB1.gencal', caltype='amp', parameter=[sf])
applycal(vis=LB1_ref, gaintable=['scale_LB1.gencal'], calwt=T, flagbackup=T) 

# now extract the re-scaled LB1 visibilities
LB1_rescaled = LB_field+'_'+LB_tag+'1_rescaled.ms'
os.system('rm -rf '+LB1_rescaled+'*')
split2(vis=LB1_ref, outputvis=LB1_rescaled, datacolumn='corrected')


# check that this actually worked:
os.system('rm -rf LB1_quick_rescaled.ms*')
split2(vis=LB1_rescaled, field='7', spw='4~7', 
       outputvis='LB1_quick_rescaled.ms', width=[16,16,16,8], 
       datacolumn='data')
execfile('ExportMS.py')         # for MSname = 'LB1_quick_rescaled'
# OK!  Now finally ready to combine and self-calibrate.



##################################################################
##################################################################
## combine data and self-calibration
##################################################################
##################################################################

# concatenate all datasets
ms_list = [SB_shift, LB0_shift, LB1_rescaled]
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
cleaned for 8 cycles (800 iterations)
peak: 1.7 mJy/beam, flux: 88.3 mJy, rms: 16 uJy/beam, beam = 40 x 30 mas
peak SNR: 106
"""

# make a copy of the concatenated MS
all_selfcalp0 = all_field+'_'+all_tag+'_selfcalp0.ms'
os.system('rm -rf '+all_selfcalp0+'*')
os.system('cp -r '+all_concat+' '+all_selfcalp0)

# first round of phase-only self-cal
all_p1 = all_field+'_'+all_tag+'.p1'
os.system('rm -rf '+all_p1)
gaincal(vis=all_selfcalp0, caltable=all_p1, gaintype='T', combine='spw,scan', 
        spw=all_contspws, refant=all_refant, calmode='p', field='0',
        solint='300s', minsnr=2.0, minblperant=4)

# @@ look at the solutions
plotcal(caltable=all_p1,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/05/13/00~2017/05/18/00')
plotcal(caltable=all_p1,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/09/23/00~2017/09/26/00')
plotcal(caltable=all_p1,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/11/03/00~2017/11/05/00')

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
cleaned for 12 cycles (1200 iterations)
peak: 1.95 mJy/beam, flux: 87.3 mJy, rms: 16 uJy/beam, beam = 40 x 30 mas
peak SNR: 122

"""

# second round of phase-only self-cal
all_p2 = all_field+'_'+all_tag+'.p2'
os.system('rm -rf '+all_p2)
gaincal(vis=all_selfcalp1, caltable=all_p2, gaintype='T', combine='spw,scan', 
        spw=all_contspws, refant=all_refant, calmode='p', field='0',
        solint='120s', minsnr=2.0, minblperant=4)
# flagging about 10-15% of the solutions for low SNR

# @@ look at the solutions
plotcal(caltable=all_p2,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/05/13/00~2017/05/18/00')
plotcal(caltable=all_p2,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/09/23/00~2017/09/26/00')
plotcal(caltable=all_p2,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/11/03/00~2017/11/05/00')

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
cleaned for 18 cycles (1800 iterations)
peak: 2.05 mJy/beam, flux: 87.1 mJy, rms: 16 uJy/beam, beam = 40 x 30 mas
peak SNR: 128

"""

# third round of phase-only self-cal
all_p3 = all_field+'_'+all_tag+'.p3'
os.system('rm -rf '+all_p3)
gaincal(vis=all_selfcalp2, caltable=all_p3, gaintype='T', combine='spw,scan', 
        spw=all_contspws, refant=all_refant, calmode='p', field='0',
        solint='60s', minsnr=2.0, minblperant=4)
# flagging about 20% of the solutions for low SNR

# @@ look at the solutions
plotcal(caltable=all_p3,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/05/13/00~2017/05/18/00')
plotcal(caltable=all_p3,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/09/23/00~2017/09/26/00')
plotcal(caltable=all_p3,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/11/03/00~2017/11/05/00')

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
cleaned for 20 cycles (2000 iterations)
peak: 2.16 mJy/beam, flux: 88.3 mJy, rms: 16 uJy/beam, beam = 40 x 30 mas
peak SNR: 138

"""

# fourth round of phase-only self-cal
all_p4 = all_field+'_'+all_tag+'.p4'
os.system('rm -rf '+all_p4)
gaincal(vis=all_selfcalp3, caltable=all_p4, gaintype='T', combine='spw,scan',
        spw=all_contspws, refant=all_refant, calmode='p', field='0',
        solint='30s', minsnr=2.0, minblperant=4)
# flagging about 20% of the solutions for low SNR

# @@ look at the solutions
plotcal(caltable=all_p4,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/05/13/00~2017/05/18/00')
plotcal(caltable=all_p4,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/09/23/00~2017/09/26/00')
plotcal(caltable=all_p4,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/11/03/00~2017/11/05/00')

# apply calibration table
applycal(vis=all_selfcalp3, spw=all_contspws, spwmap=[0]*16, 
         gaintable=[all_p4], calwt=True, applymode='calonly', flagbackup=True, 
         interp='linearPD')

# split out a corrected MS for another round
all_selfcalp4 = all_field+'_'+all_tag+'_selfcalp4.ms'
os.system('rm -rf '+all_selfcalp4+'*')
split2(vis=all_selfcalp3, outputvis=all_selfcalp4, datacolumn='corrected')

# image
all_contimagep4 = all_field +'_'+all_tag+'_continuum_p4'
os.system('rm -rf '+all_contimagep4+'.*')
clean(vis=all_selfcalp4, imagename=all_contimagep4, mode='mfs',
      multiscale=multiscale, psfmode='hogbom', imagermode='csclean',
      weighting='briggs', robust=robust, gain=gain, niter=niter,
      cyclefactor=cyclefactor, npercycle=npercycle, imsize=imsize, cell=cell,
      interactive=True, usescratch=True, mask=all_mask)
"""
cleaned for 25 cycles (2500 iterations)
peak: 2.23 mJy/beam, flux: 87.8 mJy, rms: 15 uJy/beam, beam = 40 x 30 mas
peak SNR: 146

"""

# stopping phase-only self-cal here; improvements are modest, and when we go to
# shorter solution intervals there are too many flagged solutions 


# first round of amplitude self-cal
all_ap1 = all_field+'_'+all_tag+'.ap1'
os.system('rm -rf '+all_ap1)
gaincal(vis=all_selfcalp4, caltable=all_ap1, gaintype='T', combine='spw,scan', 
        spw=all_contspws, refant=all_refant, calmode='ap', gaintable=[all_p4],
        spwmap=[0]*16, solint='300s', minsnr=3.0, minblperant=4)

# @@ look at the solutions
plotcal(caltable=all_ap1,xaxis='time',yaxis='amp',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,0,2],
        timerange='2017/05/13/00~2017/05/18/00')
plotcal(caltable=all_ap1,xaxis='time',yaxis='amp',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,0,2],
        timerange='2017/09/23/00~2017/09/26/00')
plotcal(caltable=all_ap1,xaxis='time',yaxis='amp',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,0,2],
        timerange='2017/11/03/00~2017/11/05/00')

# apply calibration tables
applycal(vis=all_selfcalp4, spw=all_contspws, spwmap=[[0]*16,[0]*16],
         gaintable=[all_p4,all_ap1], calwt=True, applymode='calonly', 
         flagbackup=True, interp='linearPD')

# split out a corrected MS 
all_selfcalap1 = all_field+'_'+all_tag+'_selfcalap1.ms'
os.system('rm -rf '+all_selfcalap1)
split2(vis=all_selfcalp4, outputvis=all_selfcalap1, datacolumn='corrected')

# image
all_contimageap1 = all_field +'_'+all_tag+'_continuum_ap1'
os.system('rm -rf '+all_contimageap1+'.*')
clean(vis=all_selfcalap1, imagename=all_contimageap1, mode='mfs',
      multiscale=multiscale, psfmode='hogbom', imagermode='csclean',
      weighting='briggs', robust=robust, gain=gain, niter=niter,
      cyclefactor=cyclefactor, npercycle=npercycle, imsize=imsize, cell=cell,
      interactive=True, usescratch=True, mask=all_mask)
"""
cleaned deep for 40 cycles (4000 iterations); 30 uJy/beam residuals
peak: 1.84 mJy/beam, flux: 89.4 mJy, rms: 15 uJy/beam, beam = 40 x 30 mas
peak SNR went down (to 126).  Image quality poorer...?

"""

# split out the "FINAL" self-calibrated MS
all_selfcalfinal = all_field+'_'+'combined'+'_selfcal_final.ms'
os.system('rm -rf '+all_selfcalfinal)
split2(vis=all_selfcalp4, outputvis=all_selfcalfinal, datacolumn='corrected')


"""
Worthwhile to take a look at the self-calibrated visibilities:

os.system('rm -rf combined_quick.ms*')
split2(vis='GW_Lup_combined_selfcal_final.ms', field='0', spw='0~15', 
       outputvis='combined_quick.ms', 
       width=[8,16,16,16, 8,16,16,16, 16,16,16,8, 16,16,16,8],
       datacolumn='data')
execfile('ExportMS.py')         # for MSname = 'combined_quick'

pc_all   = au.radec2deg('15:46:44.728770, -34.30.35.90983')
peak_all = au.radec2deg('15:46:44.70931, -34.30.36.08330')
offsets  = au.angularSeparation(peak_all[0], peak_all[1], pc_all[0],
                                pc_all[1], True)

A Gaussian image-plane fit finds some updated geometric parameters and offsets:
	incl = 39.8
	PA = 36.4
	offx = -0.2919
	offy = -0.1735

Its pretty awesome-looking.

"""


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
