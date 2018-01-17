"""
This script is written for CASA 4.5.3.  

Note: if you do everything in this script, you'll use up about 260 GB of space.
The final calibrated continuum MS is 3.8 GB.

"""

# Labeling setups
SB_field = 'Wa_Oph_6'
LB_field = 'Wa_Oph_6'
all_field = 'Wa_Oph_6'
SB_tag = 'SB'   
LB_tag = 'LB'
all_tag = 'all'
SB_data = '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_Xbd4641_X1e/group.uid___A001_Xbd4641_X22/member.uid___A001_Xbd4641_X23/calibrated/calibrated_final.ms'
LB_data = '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X68/group.uid___A001_X8c5_X69/member.uid___A001_X8c5_X6a/calibrated/calibrated_final.ms'
SB_refant = 'DA49, DA59'
all_refant = 'DV09, DV24, DA61, DA59, DA49'
SB_contspws = '0~3'
LB_contspws = '0~7'
all_contspws = '0~15'
SB_mask = 'circle[[258pix,238pix], 1.4arcsec]'
all_mask = 'ellipse[[1581pix, 1378pix], [1.3arcsec,1.0arcsec], 162deg]'


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
flagchannels = '0:1700~2200'
flagdata(vis=SB_ms, mode='manual', spw=flagchannels, flagbackup=False, 
         field=SB_field)

# spectral averaging for continuum MS
SB_initcont = SB_field+'_'+SB_tag+'_initcont.ms'
os.system('rm -rf '+SB_initcont+'*')
split2(vis=SB_ms, field = '', spw=SB_contspws, outputvis=SB_initcont,
       width=[480,8,8,8], datacolumn='data')

# restore flagged CO 2-1 line channels in the original MS
flagmanager(vis=SB_ms, mode='restore', versionname='before_cont_flags')

# @@ check that amplitude vs. uvdist looks normal
plotms(vis=SB_initcont, xaxis='uvdist', yaxis='amp', coloraxis='spw', 
       avgtime='30', avgchannel='1000')
### only a single EB; all looks ok

# initial imaging
SB_initcontimage = SB_field+'_'+SB_tag+'_initcontinuum'
os.system('rm -rf '+SB_initcontimage+'.*')
clean(vis=SB_initcont, imagename=SB_initcontimage, mode='mfs', 
      multiscale=[0,10,30,50], psfmode='clark', imagermode='csclean', 
      weighting='briggs', robust=0.5, gain=0.1, imsize=500, cell='0.03arcsec', 
      mask=SB_mask, interactive=True)
"""
cleaned for 2 cycles (200 iterations)
peak = 39.4 mJy/beam, flux = 160 mJy, rms = 153 uJy/beam, beam = 0.26 x 0.23"
peak SNR = 258

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
applycal(vis=SB_selfcalp0, spw=SB_contspws, spwmap=[0]*4, gaintable=[SB_p1], 
         calwt=True, applymode='calonly', flagbackup=True, interp='linearPD')

# split out the corrected MS for another round
SB_selfcalp1 = SB_field+'_'+SB_tag+'_selfcalp1.ms'
os.system('rm -rf '+SB_selfcalp1)
split2(vis=SB_selfcalp0, outputvis=SB_selfcalp1, datacolumn='corrected')

# imaging
SB_contimagep1 = SB_field+'_'+SB_tag+'_continuump1'
os.system('rm -rf '+SB_contimagep1+'.*')
clean(vis=SB_selfcalp1, imagename=SB_contimagep1, mode='mfs', psfmode='clark',
      multiscale=[0,10,30,50], imagermode='csclean', weighting='briggs', 
      robust=0.5, gain=0.1, imsize=500, cell='0.03arcsec', mask=SB_mask, 
      interactive=True)
"""
cleaned for 2 cycles (200 iterations)
peak = 40.4 mJy/beam, flux = 163 mJy, rms = 59 uJy/beam, beam = 0.26 x 0.23"
peak SNR = 685

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
applycal(vis=SB_selfcalp1, spw=SB_contspws, spwmap=[0]*4, gaintable=[SB_p2], 
         calwt=True, applymode='calonly', flagbackup=True, interp='linearPD')

# split out corrected MS for another round
SB_selfcalp2 = SB_field+'_'+SB_tag+'_selfcalp2.ms'
os.system('rm -rf '+SB_selfcalp2)
split2(vis=SB_selfcalp1, outputvis=SB_selfcalp2, datacolumn='corrected')

# imaging
SB_contimagep2 = SB_field+'_'+SB_tag+'_continuump2'
os.system('rm -rf '+SB_contimagep2+'.*')
clean(vis=SB_selfcalp2, imagename=SB_contimagep2, mode='mfs', psfmode='clark',
      multiscale=[0,10,30,50], imagermode='csclean', weighting='briggs', 
      robust=0.5, gain=0.1, imsize=500, cell='0.03arcsec', mask=SB_mask, 
      interactive=True)
"""
cleaned for 2 cycles (200 iterations)
peak = 40.9 mJy/beam, flux = 164 mJy, rms = 57 uJy/beam, beam = 0.26 x 0.23"
peak SNR = 717

"""

# one round of amplitude self-cal
SB_ap1 = SB_field+'_'+SB_tag+'.ap1'
os.system('rm -rf '+SB_ap1)
gaincal(vis=SB_selfcalp2, caltable=SB_ap1, gaintype='T', combine='spw',
        spw=SB_contspws, refant=SB_refant, calmode='ap', gaintable=[SB_p2],
        spwmap=[0]*4, solint='inf', minsnr=3.0, minblperant=4)

# @@ look at solutions
plotcal(caltable=SB_ap1, xaxis='time', yaxis='amp', spw='', 
        iteration='antenna', subplot=221, plotrange=[0,0,0,2])

# apply the calibration tables
applycal(vis=SB_selfcalp2, spw=SB_contspws, spwmap=[[0]*4,[0]*4],
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
      multiscale=[0,10,30], psfmode='clark', imagermode='csclean', 
      weighting='briggs', robust=0.5, gain=0.1, imsize=500, cell='0.03arcsec', 
      mask=SB_mask, interactive=True)
"""
cleaned for 5 cycles (500 iterations); (note different multiscale)
peak = 40.2 mJy/beam, flux = 165 mJy, rms = 45 uJy/beam, beam = 0.26 x 0.23"
peak SNR = 893

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
flagchannels = '3:1700~2200, 7:1700~2200'
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
### the overlap between EBs looks pretty good

# initial imaging for LB execution block 0 = LB0, 2017/09/09 (C40-8)
LB0_initcontimage = LB_field+'_'+LB_tag+'0_initcontinuum'
os.system('rm -rf '+LB0_initcontimage+'.*')
clean(vis=LB_initcont, imagename=LB0_initcontimage, observation='0', 
      mode='mfs', multiscale=[0,10,25,50,100], psfmode='hogbom', 
      imagermode='csclean', weighting='briggs', robust=0.5, gain=0.3,
      niter=50000, cyclefactor=5, imsize=1800, cell='0.003arcsec',
      interactive=True)
"""
cleaned for 5 cycles (500 iterations); mask defined interactively
peak = 4.1 mJy/beam, flux = 155 mJy, rms = 46 uJy/beam, beam = 90 x 44 mas
peak SNR = 89

"""

# initial imaging for LB execution block 1 = LB1, 2017/09/20 (C40-9)
LB1_initcontimage = LB_field+'_'+LB_tag+'1_initcontinuum'
os.system('rm -rf '+LB1_initcontimage+'.*')
clean(vis=LB_initcont, imagename=LB1_initcontimage, observation='1',
      mode='mfs', multiscale = [0,10,25,50,100], psfmode='hogbom',
      imagermode='csclean', weighting='briggs', robust=0.5, gain=0.3,
      niter=50000, cyclefactor=5, imsize=1800, cell='0.003arcsec',
      mask=LB0_initcontimage+'.mask', interactive=True)
"""
cleaned for 5 cycles (500 iterations)
peak = 4.5 mJy/beam, flux = 149 mJy, rms = 30 uJy/beam, beam = 56 x 30 mas
peak SNR = 150

"""

# @@ Gaussian image fits for astrometry
imfit(imagename=LB0_initcontimage+'.image', mask=LB0_initcontimage+'.mask')
imfit(imagename=LB1_initcontimage+'.image', mask=LB1_initcontimage+'.mask')



##################################################################
##################################################################
## spatial alignment
##################################################################
##################################################################

# Some astrometric analysis to calculate positional shifts:

# phase centers (from listobs):  [all aligned]
pc_SB  = au.radec2deg('16:48:45.638000, -14.16.35.90000')
pc_LB0 = au.radec2deg('16:48:45.638000, -14.16.35.90000')
pc_LB1 = au.radec2deg('16:48:45.638000, -14.16.35.90000')
# disk centroids (guided by imfit, but estimated manually in this case):
peak_SB  = au.radec2deg('16:48:45.621, -14.16.36.264')
peak_LB0 = au.radec2deg('16:48:45.618, -14.16.36.227')
peak_LB1 = au.radec2deg('16:48:45.621, -14:16:36.261')

# measure position shifts
pkoff_SB  = au.angularSeparation(peak_SB[0], peak_SB[1], pc_SB[0], pc_SB[1],  
                                 True)
pkoff_LB0 = au.angularSeparation(peak_LB0[0], peak_LB0[1], pc_LB0[0], 
                                 pc_LB0[1], True)
pkoff_LB1 = au.angularSeparation(peak_LB1[0], peak_LB1[1], pc_LB1[0], 
                                 pc_LB1[1], True)

# peak offsets relative to phase centers (RA, DEC):
# SB  :  -0.255", -0.364"
# LB0 :  -0.300", -0.327"
# LB1 :  -0.255", -0.361"

# measure position shifts
shift_SB_LB0  = au.angularSeparation(peak_LB0[0], peak_LB0[1], peak_SB[0], 
				     peak_SB[1], True)
shift_SB_LB1  = au.angularSeparation(peak_LB1[0], peak_LB1[1], peak_SB[0],
                                     peak_SB[1], True)
shift_LB0_LB1 = au.angularSeparation(peak_LB1[0], peak_LB1[1], peak_LB0[0],
				     peak_LB0[1], True)

# absolute peak shifts between observations
# SB-LB0  : -45, +37 mas
# SB-LB1  :   0,  +3 mas
# LB0-LB1 : +45, -34 mas  
# you can see the LB0-LB1 offset, but it is made difficult by the asymmetric 
# peak in the LB0 data (the peaks are clearly shifted, as is the larger-scale
# emission pattern; we need to try and correct for this)

# We need to manually align before trying a combined self-cal solution.  
# The plan is to shift the LB0 data to the LB1 position (best measurement).  No
# shift is necessary for the SB dataset.


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
# 16:48:45.635000, -14:16:35.86600
fixvis(vis=LB0_shift, outputvis=LB0_shift, field='4',
       phasecenter='ICRS 16h48m45.635s -14d16m35.866s')

# @@ check that the MS was properly updated
listobs(LB0_shift)

# now re-assign the phase center (LB1 phase center, in J2000)
radec_pc_LB1 = au.deg2radec(pc_LB1[0], pc_LB1[1])
au.ICRSToJ2000(radec_pc_LB1)
# Separation: radian = 7.66094e-08, degrees = 0.000004, arcsec = 0.015802
#   Out[182]: '16:48:45.63874, -014:16:35.888425'
fixplanets(vis=LB0_shift, field='4',
           direction='J2000 16h48m45.63874s -14d16m35.888425s')

# @@ check that the MS was properly updated
listobs(LB0_shift)


# We are not doing a shift on SB or LB1, but we need to convert to J2000

# split the LB1 data (only) into a new MS
LB1_ref = LB_field+'_'+LB_tag+'1_ref.ms'
os.system('rm -rf '+LB1_ref)
split2(vis=LB_initcont, outputvis=LB1_ref, observation='1', datacolumn='data')

# now re-assign the phase center
fixplanets(vis=LB1_ref, field='4',
           direction='J2000 16h48m45.63874s -14d16m35.888425s')

# @@ check that the MS was properly updated
listobs(LB1_ref)

# split the LB1 data (only) into a new MS
SB_ref = SB_field+'_'+SB_tag+'_ref.ms'
os.system('rm -rf '+SB_ref)
split2(vis=SB_selfcalap1, outputvis=SB_ref, datacolumn='data')

# now re-assign the phase center
fixplanets(vis=SB_ref, field='0',
           direction='J2000 16h48m45.63874s -14d16m35.888425s')

# @@ check that the MS was properly updated
listobs(SB_ref)



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
split2(vis=SB_ref, field='', spw='', outputvis='SB_quick.ms', 
       width=[8,16,16,16], datacolumn='data')
execfile('ExportMS.py')		# for MSname = 'SB_quick'

os.system('rm -rf '+LB_tag+'0_quick.ms*')
split2(vis=LB0_shift, field='4', spw='0~3', outputvis='LB0_quick.ms', 
       width=[16,16,16,8], datacolumn='data')
execfile('ExportMS.py')         # for MSname = 'LB0_quick'

os.system('rm -rf '+LB_tag+'1_quick.ms*')
split2(vis=LB1_ref, field='4', spw='4~7', outputvis='LB1_quick.ms', 
       width=[16,16,16,8], datacolumn='data')
execfile('ExportMS.py')         # for MSname = 'LB1_quick'

# (offx, offy) = (-0.255, -0.361)"	[i.e., to the SW]
# Can also make crude estimate of viewing geometry from Gaussian fits:
# deconvolved minor/major axis ratio = 240 / 328 = 0.732, so i = 42.7 degrees.  
# The deconvolved PA = 161.6 degrees.

"""
With that information, we can directly examine the visibility profiles using 
the script 'check_visprofiles.py' (outside CASA).

A comparison of these profiles shows that there is non-trivial discrepancies 
between the calibrations.  If we use SB as a reference, then we find that 
LB1 is too low (by about 10%).  LB0 is more problematic: it is too low by about 
10% at short baselines, but much worse at long baselines.  I suspect that this 
is really a phase noise problem in LB0.  

For the flux (amplitude) calibration, the pipeline used:
	 SB:  J1733-1304, mean Fnu = 1.46 Jy @ 238.8 GHz
	LB0:  J1733-1304, mean Fnu = 1.49 Jy @ 238.8 GHz
	LB1:  J1733-1304, mean Fnu = 1.56 Jy @ 238.8 GHz

Updated queries (see below) find:
	 SB:  J1733-1304, Fnu = 1.50 +/- 0.13 Jy
	LB0:  J1733-1304, Fnu = 1.40 +/- 0.15 Jy
	LB1:  J1733-1304, Fnu = 1.85 +/- 0.16 Jy

au.getALMAFlux('J1733-1304', 238.8, date='2017/05/09')
au.getALMAFlux('J1733-1304', 238.8, date='2017/09/09')
au.getALMAFlux('J1733-1304', 238.8, date='2017/09/20')

So, this suggests that the SB and LB0 calibrations are not terrible.  Indeed, 
I see about 10% increases in LB0 and LB1 would give good overlap on shorter 
spacings, which is roughly in line with the updated calibration numbers.

We will manually scale the LB flux calibrations up into alignment.

"""

# re-scale the LB1 flux calibration
sf = 1./sqrt(1.1)
os.system('rm -rf scale_LB0.gencal*')
gencal(vis=LB0_shift, caltable='scale_LB0.gencal', caltype='amp', 
       parameter=[sf])
applycal(vis=LB0_shift, gaintable=['scale_LB0.gencal'], calwt=T, flagbackup=T)

# now extract the re-scaled LB1 visibilities
LB0_rescaled = LB_field+'_'+LB_tag+'0_rescaled.ms'
os.system('rm -rf '+LB0_rescaled+'*')
split2(vis=LB0_shift, outputvis=LB0_rescaled, datacolumn='corrected')

# re-scale the LB1 flux calibration
sf = 1./sqrt(1.1)
os.system('rm -rf scale_LB1.gencal*')
gencal(vis=LB1_ref, caltable='scale_LB1.gencal', caltype='amp', parameter=[sf])
applycal(vis=LB1_ref, gaintable=['scale_LB1.gencal'], calwt=T, flagbackup=T) 

# now extract the re-scaled LB1 visibilities
LB1_rescaled = LB_field+'_'+LB_tag+'1_rescaled.ms'
os.system('rm -rf '+LB1_rescaled+'*')
split2(vis=LB1_ref, outputvis=LB1_rescaled, datacolumn='corrected')



##################################################################
##################################################################
## combine data and self-calibration
##################################################################
##################################################################

# concatenate all datasets
ms_list = [SB_ref, LB0_rescaled, LB1_rescaled]
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
multiscale = [0, 20, 40, 80, 160]

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
peak: 5.4 mJy/beam, flux: 214 mJy, rms: 27 uJy/beam, beam = 70 x 40 mas
peak SNR: 200
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
        timerange='2017/05/08/00~2017/05/10/00')
plotcal(caltable=all_p1,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/09/08/00~2017/09/10/00')
plotcal(caltable=all_p1,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/09/19/00~2017/09/21/00')

# apply the calibration table
applycal(vis=all_selfcalp0, spw=all_contspws, spwmap=[0]*12, 
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
peak: 6.8 mJy/beam, flux: 176 mJy, rms: 16.9 uJy/beam, beam = 70 x 30 mas
peak SNR: 402

"""

# second round of phase-only self-cal
all_p2 = all_field+'_'+all_tag+'.p2'
os.system('rm -rf '+all_p2)
gaincal(vis=all_selfcalp1, caltable=all_p2, gaintype='T', combine='spw,scan', 
        spw=all_contspws, refant=all_refant, calmode='p', field='0',
        solint='120s', minsnr=2.0, minblperant=4)
# flagging <5% of the solutions for low SNR

# @@ look at the solutions
plotcal(caltable=all_p2,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/05/08/00~2017/05/10/00')
plotcal(caltable=all_p2,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/09/08/00~2017/09/10/00')
plotcal(caltable=all_p2,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/09/19/00~2017/09/21/00')

# apply the calibration table
applycal(vis=all_selfcalp1, spw=all_contspws, spwmap=[0]*12, 
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
peak: 7.37 mJy/beam, flux: 170 mJy, rms: 15.4 uJy/beam, beam = 70 x 30 mas
peak SNR: 479

"""

# third round of phase-only self-cal
all_p3 = all_field+'_'+all_tag+'.p3'
os.system('rm -rf '+all_p3)
gaincal(vis=all_selfcalp2, caltable=all_p3, gaintype='T', combine='spw,scan', 
        spw=all_contspws, refant=all_refant, calmode='p', field='0',
        solint='60s', minsnr=2.0, minblperant=4)
# flagging <10% of the solutions for low SNR

# @@ look at the solutions
plotcal(caltable=all_p3,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/05/08/00~2017/05/10/00')
plotcal(caltable=all_p3,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/09/08/00~2017/09/10/00')
plotcal(caltable=all_p3,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/09/19/00~2017/09/21/00')

# apply the calibration table
applycal(vis=all_selfcalp2, spw=all_contspws, spwmap=[0]*12, 
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
peak: 7.72 mJy/beam, flux: 169 mJy, rms: 15.1 uJy/beam, beam = 70 x 30 mas
peak SNR: 511

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
        timerange='2017/05/08/00~2017/05/10/00')
plotcal(caltable=all_p4,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/09/08/00~2017/09/10/00')
plotcal(caltable=all_p4,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/09/19/00~2017/09/21/00')

# apply calibration table
applycal(vis=all_selfcalp3, spw=all_contspws, spwmap=[0]*12, 
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
peak: 7.92 mJy/beam, flux: 168 mJy, rms: 15.1 uJy/beam, beam = 70 x 30 mas
peak SNR: 525

"""

# stopping phase-only self-cal here; improvements are modest, and when we go to
# shorter solution intervals there are too many flagged solutions 


# first round of amplitude self-cal
all_ap1 = all_field+'_'+all_tag+'.ap1'
os.system('rm -rf '+all_ap1)
gaincal(vis=all_selfcalp4, caltable=all_ap1, gaintype='T', combine='spw,scan', 
        spw=all_contspws, refant=all_refant, calmode='ap', gaintable=[all_p4],
        spwmap=[0]*12, solint='300s', minsnr=3.0, minblperant=4)

# @@ look at the solutions
plotcal(caltable=all_ap1,xaxis='time',yaxis='amp',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,0,2],
        timerange='2017/05/08/00~2017/05/10/00')
plotcal(caltable=all_ap1,xaxis='time',yaxis='amp',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,0,2],
        timerange='2017/09/08/00~2017/09/10/00')
plotcal(caltable=all_ap1,xaxis='time',yaxis='amp',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,0,2],
        timerange='2017/09/19/00~2017/09/21/00')

# apply calibration tables
applycal(vis=all_selfcalp4, spw=all_contspws, spwmap=[[0]*12,[0]*12],
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
cleaned deep for 30 cycles (3000 iterations); <30 uJy/beam residuals
peak: 7.55 mJy/beam, flux: 168 mJy, rms: 14.3 uJy/beam, beam = 70 x 30 mas
peak SNR = 528.

"""

# split out the "FINAL" self-calibrated MS
all_selfcalfinal = all_field+'_'+'combined'+'_selfcal_final.ms'
os.system('rm -rf '+all_selfcalfinal)
split2(vis=all_selfcalap1, outputvis=all_selfcalfinal, datacolumn='data')


"""
Worthwhile to take a look at the self-calibrated visibilities:

os.system('rm -rf combined_quick.ms*')
split2(vis='Wa_Oph_6_combined_selfcal_final.ms', field='0', spw='0~12', 
       outputvis='combined_quick.ms', 
       width=[8,16,16,16, 16,16,16,8, 16,16,16,8],
       datacolumn='data')
execfile('ExportMS.py')         # for MSname = 'combined_quick'

pc_all   = au.radec2deg('16:48:45.638470, -14.16.35.88842')
peak_all = au.radec2deg('16:48:45.622, -14.16.36.248')
offsets  = au.angularSeparation(peak_all[0], peak_all[1], pc_all[0],
                                pc_all[1], True)

A Gaussian image-plane fit finds some updated geometric parameters and offsets:
	incl = 44.7
	PA = 169.
	offx = -0.2471
	offy = -0.3596

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
Comments on imaging tests: TBD

"""
