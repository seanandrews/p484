"""
This script is written for CASA 4.5.3.  

Note: if you do everything in this script, you'll use up about 430 GB of space.
The final calibrated continuum MS is 5.7 GB.

"""

# Labeling setups
SB_field = 'Elias_20'
LB_field = 'Elias_20'
all_field = 'Elias_20'
SB_tag = 'SB'   
LB_tag = 'LB'
all_tag = 'all'
SB_data = '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_Xbd4641_X1e/group.uid___A001_Xbd4641_X25/member.uid___A001_Xbd4641_X26/calibrated/calibrated_final.ms'
LB_data = '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_X8c5_X58/group.uid___A001_X8c5_X59/member.uid___A001_X8c5_X5a/calibrated/calibrated_final.ms'
SB_refant = 'DV15, DV18'
all_refant = 'DA61'
SB_contspws = '0~11'
LB_contspws = '0~7'
all_contspws = '0~19'
SB_mask = 'circle[[253pix,233pix],1.0arcsec]'
all_mask = 'ellipse[[1517pix, 1336pix], [0.8arcsec,0.6arcsec], 154deg]'


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
flagchannels = '0:1800~2300, 4:1800~2300, 8:1800~2300'
flagdata(vis=SB_ms, mode='manual', spw=flagchannels, flagbackup=False, 
         field=SB_field)

# spectral averaging for continuum MS
SB_initcont = SB_field+'_'+SB_tag+'_initcont.ms'
os.system('rm -rf '+SB_initcont+'*')
split2(vis=SB_ms, field = '', spw=SB_contspws, outputvis=SB_initcont,
       width=[480,8,8,8,480,8,8,8,480,8,8,8], datacolumn='data')

# restore flagged CO 2-1 line channels in the original MS
flagmanager(vis=SB_ms, mode='restore', versionname='before_cont_flags')

# @@ check that amplitude vs. uvdist looks normal
plotms(vis=SB_initcont, xaxis='uvdist', yaxis='amp', coloraxis='observation', 
       avgtime='30', avgchannel='1000')
### all 3 EBs have good overlap (relative flux calibration should be fine)

# initial imaging
SB_initcontimage = SB_field+'_'+SB_tag+'_initcontinuum'
os.system('rm -rf '+SB_initcontimage+'.*')
clean(vis=SB_initcont, imagename=SB_initcontimage, mode='mfs', 
      psfmode='clark', imagermode='csclean', weighting='briggs', robust=0.5,
      gain=0.1, imsize=500, cell='0.03arcsec', mask=SB_mask, interactive=True)
"""
cleaned for 4 cycles (400 iterations)
peak = 34.2 mJy/beam, flux = 100 mJy, rms = 82 uJy/beam, beam = 0.26 x 0.22"
peak SNR = 417

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
applycal(vis=SB_selfcalp0, spw=SB_contspws, spwmap=[0]*12, gaintable=[SB_p1], 
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
cleaned for 6 cycles (600 iterations)
peak = 36.4 mJy/beam, flux = 102 mJy, rms = 42 uJy/beam, beam = 0.26 x 0.22"
peak SNR = 867

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
applycal(vis=SB_selfcalp1, spw=SB_contspws, spwmap=[0]*12, gaintable=[SB_p2], 
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
cleaned for 6 cycles (600 iterations)
peak = 37.0 mJy/beam, flux = 102 mJy, rms = 41 uJy/beam, beam = 0.26 x 0.22"
peak SNR = 902

"""

# one round of amplitude self-cal
SB_ap1 = SB_field+'_'+SB_tag+'.ap1'
os.system('rm -rf '+SB_ap1)
gaincal(vis=SB_selfcalp2, caltable=SB_ap1, gaintype='T', combine='spw',
        spw=SB_contspws, refant=SB_refant, calmode='ap', gaintable=[SB_p2],
        spwmap=[0]*12, solint='inf', minsnr=3.0, minblperant=4)

# @@ look at solutions
plotcal(caltable=SB_ap1, xaxis='time', yaxis='amp', spw='', 
        iteration='antenna', subplot=221, plotrange=[0,0,0,2])

# apply the calibration tables
applycal(vis=SB_selfcalp2, spw=SB_contspws, spwmap=[[0]*12,[0]*12],
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
cleaned for 6 cycles (600 iterations)
peak = 37.1 mJy/beam, flux = 101 mJy, rms = 34 uJy/beam, beam = 0.26 x 0.22"
peak SNR = 1091

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
# also flag an anomalous spike in SPW6 (247.5--248 GHz)
flagmanager(vis=LB_ms, mode='save', versionname='before_cont_flags')
flagchannels = '3:1800~2100, 7:1800~2100'
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
### looks like a flux calibration issue...tbd later.

# initial imaging for LB execution block 0 = LB0, 2017/09/23 (C40-9)
LB0_initcontimage = LB_field+'_'+LB_tag+'0_initcontinuum'
os.system('rm -rf '+LB0_initcontimage+'.*')
clean(vis=LB_initcont, imagename=LB0_initcontimage, observation='0', 
      mode='mfs', multiscale=[0,10,25,50,100], psfmode='hogbom', 
      imagermode='csclean', weighting='briggs', robust=0.5, gain=0.3,
      niter=50000, cyclefactor=5, imsize=1800, cell='0.003arcsec',
      interactive=True)
"""
cleaned for 5 cycles (500 iterations); mask defined interactively
peak = 4.0 mJy/beam, flux = 118 mJy, rms = 24 uJy/beam, beam = 49 x 27 mas
peak SNR = 167

"""

# initial imaging for LB execution block 1 = LB1, 2017/10/08 (C43-10)
LB1_initcontimage = LB_field+'_'+LB_tag+'1_initcontinuum'
os.system('rm -rf '+LB1_initcontimage+'.*')
clean(vis=LB_initcont, imagename=LB1_initcontimage, observation='1',
      mode='mfs', multiscale = [0,10,25,50,100], psfmode='hogbom',
      imagermode='csclean', weighting='briggs', robust=0.5, gain=0.3,
      niter=50000, cyclefactor=5, imsize=1800, cell='0.003arcsec',
      mask=LB0_initcontimage+'.mask', interactive=True)
"""
cleaned for 5 cycles (500 iterations)
peak = 2.7 mJy/beam, flux = 105 mJy, rms = 20 uJy/beam, beam = 34 x 26 mas
peak SNR = 135

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
pc_SB  = au.radec2deg('16:26:18.870000, -24.28.19.69000')
pc_LB0 = au.radec2deg('16:26:18.870000, -24.28.19.69000')
pc_LB1 = au.radec2deg('16:26:18.870000, -24.28.19.69000')
# disk centroids (from imfit):
peak_SB  = au.radec2deg('16:26:18.865611, -24.28.20.171668')
peak_LB0 = au.radec2deg('16:26:18.866388, -24.28.20.180869')
peak_LB1 = au.radec2deg('16:26:18.866339, -24.28.20.180351')

# measure position shifts
pkoff_SB  = au.angularSeparation(peak_SB[0], peak_SB[1], pc_SB[0], pc_SB[1],  
                                 True)
pkoff_LB0 = au.angularSeparation(peak_LB0[0], peak_LB0[1], pc_LB0[0], 
                                 pc_LB0[1], True)
pkoff_LB1 = au.angularSeparation(peak_LB1[0], peak_LB1[1], pc_LB1[0], 
                                 pc_LB1[1], True)

# peak offsets relative to phase centers (RA, DEC):
# SB  :  -0.0658", -0.4817"
# LB0 :  -0.0542", -0.4909"
# LB1 :  -0.0549", -0.4904"

# measure position shifts
shift_SB_LB0  = au.angularSeparation(peak_LB0[0], peak_LB0[1], peak_SB[0], 
				     peak_SB[1], True)
shift_SB_LB1  = au.angularSeparation(peak_LB1[0], peak_LB1[1], peak_SB[0],
                                     peak_SB[1], True)
shift_LB0_LB1 = au.angularSeparation(peak_LB1[0], peak_LB1[1], peak_LB0[0],
				     peak_LB0[1], True)

# absolute peak shifts between observations
# SB-LB0  : +11.7, -9.2 mas
# SB-LB1  : +10.9, -8.7 mas
# LB0-LB1 :  -0.7, +0.5 mas  

# note the (rough) UTC times of each observation (from listobs)
# **** NEEDS TO BE UPDATED ****
# SB  : 2017-05-15 / 15:30
# LB0 : 2017-09-25 / 00:30
# LB1 : 2017-11-04 / 15:30
# delta_t(SB-LB0)  : 0.36 yr
# delta_t(LB0-LB1) : 0.11 yr

# The datasets are basically in perfect alignment.  And all measurements have 
# the same phase center.  No adjustments needed.



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
split2(vis=SB_selfcalap1, field='', spw='', outputvis='SB_quick.ms', 
       width=[8,16,16,16,8,16,16,16,8,16,16,16], datacolumn='data')
execfile('ExportMS.py')		# for MSname = 'SB_quick'

os.system('rm -rf '+LB_tag+'0_quick.ms*')
split2(vis=LB_initcont, field='3', spw='0~3', outputvis='LB0_quick.ms', 
       width=[16,16,16,8], datacolumn='data')
execfile('ExportMS.py')         # for MSname = 'LB0_quick'

os.system('rm -rf '+LB_tag+'1_quick.ms*')
split2(vis=LB_initcont, field='3', spw='4~7', outputvis='LB1_quick.ms', 
       width=[16,16,16,8], datacolumn='data')
execfile('ExportMS.py')         # for MSname = 'LB1_quick'

# (offx, offy) = (-0.05, -0.49)"	[i.e., to the S]
# Can also make crude estimate of viewing geometry from Gaussian fits:
# deconvolved minor/major axis ratio = 213 / 359, so i = 53.6 degrees.  
# The deconvolved PA = 154 degrees.

"""
With that information, we can directly examine the visibility profiles using 
the script 'check_visprofiles.py' (outside CASA).

A comparison of these profiles shows that the overall flux calibration is good, 
but that LB0 is high by about 13% compared to both SB and LB1.  Lets just check 
the flux calibration for everything:

For the flux (amplitude) calibration, the pipeline used:
	 SB:  J1517-2422, mean Fnu = 1.93 Jy @ 238.7 GHz
	      J1733-1304, mean Fnu = 1.58 Jy @ 238.7 GHz
              J1517-2422, mean Fnu = 2.10 Jy @ 238.7 GHz
	LB0:  J1517-2422, mean Fnu = 2.44 Jy @ 238.7 GHz
	LB1:  J1733-1304, mean Fnu = 1.88 Jy @ 238.7 GHz

Updated queries (see below) find:
	 SB:  J1517-2422, Fnu = 2.03 +/- 0.16 Jy
              J1733-1304, Fnu = 1.58 +/- 0.13 Jy
              J1517-2422, Fnu = 2.03 +/- 0.16 Jy
	LB0:  J1517-2422, Fnu = 2.15 +/- 0.18 Jy
	LB1:  J1733-1304, Fnu = 1.85 +/- 0.16 Jy

au.getALMAFlux('J1517-2422', 238.7, date='2017/05/14')
au.getALMAFlux('J1733-1304', 238.7, date='2017/05/17')
au.getALMAFlux('J1517-2422', 238.7, date='2017/05/19')
au.getALMAFlux('J1517-2422', 238.7, date='2017/09/23')
au.getALMAFlux('J1733-1304', 238.7, date='2017/10/08')

So, this suggests that the SB and LB1 calibrations are actually pretty much 
fine.  The LB0 calibration is in error, in the direction we expect.  The 
renormalization is of the right scale too.  

We manually scale the LB0 flux calibration down into alignment.

"""

# separate the LB0 and LB1 datasets
LB0_base = LB_field + LB_tag+'0_base.ms'
os.system('rm -rf '+LB0_base+'*')
split2(vis=LB_initcont, field='3', observation='0', outputvis=LB0_base,
       datacolumn='data')
LB1_base = LB_field + LB_tag+'1_base.ms'
os.system('rm -rf '+LB1_base+'*')
split2(vis=LB_initcont, field='3', observation='1', outputvis=LB1_base,
       datacolumn='data')

# re-scale the LB0 flux calibration
sf = 1./sqrt(0.87)
os.system('rm -rf scale_LB0.gencal*')
gencal(vis=LB0_base, caltable='scale_LB0.gencal', caltype='amp', parameter=[sf])
applycal(vis=LB0_base, gaintable=['scale_LB0.gencal'], calwt=T, flagbackup=T) 

# now extract the re-scaled LB1 visibilities
LB0_rescaled = LB_field+'_'+LB_tag+'0_rescaled.ms'
os.system('rm -rf '+LB0_rescaled+'*')
split2(vis=LB0_base, outputvis=LB0_rescaled, datacolumn='corrected')

# check that this actually worked:
os.system('rm -rf LB0_quick_rescaled.ms*')
split2(vis=LB0_rescaled, field='0', spw='0~3', 
       outputvis='LB0_quick_rescaled.ms', width=[16,16,16,8], 
       datacolumn='data')
execfile('ExportMS.py')         # for MSname = 'LB0_quick_rescaled'
# OK!  Now finally ready to combine and self-calibrate.



##################################################################
##################################################################
## combine data and self-calibration
##################################################################
##################################################################

# concatenate all datasets
"""
The individual MSs were processed differently; some have full weight spectra, 
and others do not.  To properly concatenate them, we have to use CASA 5.1.1.  
See Jane's post:

https://j6626.github.io/casablanca/casa/2018/01/15/Fun-with-weight-spectrum.html

So, this step is done in CASA 5.1.1, but then we revert to CASA 4.5.3.

(on my machine, I access CASA 5.1.1 with :
	/pool/asha0/casa-release-5.1.1-5.el6/bin/casa
)

"""

ms_list = [SB_selfcalap1, LB0_rescaled, LB1_base]
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
multiscale = [0, 10, 25, 50, 100] 

# initial clean
all_initcontimage = all_field +'_'+all_tag+'_initcontinuum'
os.system('rm -rf '+all_initcontimage+'.*')
clean(vis=all_concat, imagename=all_initcontimage, mode='mfs', 
      multiscale=multiscale, psfmode='hogbom', imagermode='csclean',
      weighting='briggs', robust=robust, gain=gain, niter=niter, 
      cyclefactor=cyclefactor, npercycle=npercycle, imsize=imsize, cell=cell, 
      interactive=True, usescratch=True, mask=all_mask)
"""
cleaned for 13 cycles (1300 iterations)
peak: 3.26 mJy/beam, flux: 105 mJy, rms: 12.9 uJy/beam, beam = 40 x 29 mas
peak SNR: 252

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
        timerange='2017/05/13/00~2017/05/20/00')
plotcal(caltable=all_p1,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/09/22/00~2017/09/24/00')
plotcal(caltable=all_p1,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/10/06/00~2017/10/09/00')

# apply the calibration table
applycal(vis=all_selfcalp0, spw=all_contspws, spwmap=[0]*20, 
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
cleaned for 15 cycles (1500 iterations)
peak: 3.30 mJy/beam, flux: 104 mJy, rms: 12.7 uJy/beam, beam = 40 x 29 mas
peak SNR: 259

"""

# second round of phase-only self-cal
all_p2 = all_field+'_'+all_tag+'.p2'
os.system('rm -rf '+all_p2)
gaincal(vis=all_selfcalp1, caltable=all_p2, gaintype='T', combine='spw,scan', 
        spw=all_contspws, refant=all_refant, calmode='p', field='0',
        solint='120s', minsnr=2.0, minblperant=4)
# flagging about 10% of the solutions for low SNR

# @@ look at the solutions
plotcal(caltable=all_p2,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/05/13/00~2017/05/20/00')
plotcal(caltable=all_p2,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/09/22/00~2017/09/24/00')
plotcal(caltable=all_p2,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/10/05/00~2017/10/09/00')

# apply the calibration table
applycal(vis=all_selfcalp1, spw=all_contspws, spwmap=[0]*20, 
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
cleaned for 20 cycles (2000 iterations)
peak: 3.37 mJy/beam, flux: 104 mJy, rms: 12.6 uJy/beam, beam = 40 x 29 mas
peak SNR: 267

"""

# stopping phase-only self-cal here; improvements are modest, and when we go to
# shorter solution intervals there are too many flagged solutions 


# first round of amplitude self-cal
all_ap1 = all_field+'_'+all_tag+'.ap1'
os.system('rm -rf '+all_ap1)
gaincal(vis=all_selfcalp2, caltable=all_ap1, gaintype='T', combine='spw,scan', 
        spw=all_contspws, refant=all_refant, calmode='ap', gaintable=[all_p2],
        spwmap=[0]*20, solint='300s', minsnr=3.0, minblperant=4)

# @@ look at the solutions
plotcal(caltable=all_ap1,xaxis='time',yaxis='amp',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,0,2],
        timerange='2017/05/13/00~2017/05/20/00')
plotcal(caltable=all_ap1,xaxis='time',yaxis='amp',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,0,2],
        timerange='2017/09/22/00~2017/09/24/00')
plotcal(caltable=all_ap1,xaxis='time',yaxis='amp',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,0,2],
        timerange='2017/10/05/00~2017/10/09/00')

# apply calibration tables
applycal(vis=all_selfcalp2, spw=all_contspws, spwmap=[[0]*20,[0]*20],
         gaintable=[all_p2,all_ap1], calwt=True, applymode='calonly', 
         flagbackup=True, interp='linearPD')

# split out a corrected MS 
all_selfcalap1 = all_field+'_'+all_tag+'_selfcalap1.ms'
os.system('rm -rf '+all_selfcalap1)
split2(vis=all_selfcalp2, outputvis=all_selfcalap1, datacolumn='corrected')

# image
all_contimageap1 = all_field +'_'+all_tag+'_continuum_ap1'
os.system('rm -rf '+all_contimageap1+'.*')
clean(vis=all_selfcalap1, imagename=all_contimageap1, mode='mfs',
      multiscale=multiscale, psfmode='hogbom', imagermode='csclean',
      weighting='briggs', robust=robust, gain=gain, niter=niter,
      cyclefactor=cyclefactor, npercycle=npercycle, imsize=imsize, cell=cell,
      interactive=True, usescratch=True, mask=all_mask)
"""
cleaned deep for 25 cycles (2500 iterations); <25 uJy/beam residuals
peak: 3.20 mJy/beam, flux: 103 mJy, rms: 12.3 uJy/beam, beam = 40 x 29 mas
peak SNR = 260

"""

# split out the "FINAL" self-calibrated MS
all_selfcalfinal = all_field+'_'+'combined'+'_selfcal_final.ms'
os.system('rm -rf '+all_selfcalfinal)
split2(vis=all_selfcalap1, outputvis=all_selfcalfinal, datacolumn='data')


"""
Worthwhile to take a look at the self-calibrated visibilities:

os.system('rm -rf combined_quick.ms*')
split2(vis='Elias_20_combined_selfcal_final.ms', field='0', spw='0~19', 
       outputvis='combined_quick.ms', 
       width=[8,16,16,16, 8,16,16,16, 8,16,16,16, 16,16,16,8, 16,16,16,8],
       datacolumn='data')
execfile('ExportMS.py')         # for MSname = 'combined_quick'

pc_all   = au.radec2deg('16:26:18.87000, -24.28.19.69000')
peak_all = au.radec2deg('16:26:18.86603, -24.28.20.17714')
offsets  = au.angularSeparation(peak_all[0], peak_all[1], pc_all[0],
                                pc_all[1], True)

A Gaussian image-plane fit finds some updated geometric parameters and offsets:
	incl = 53.6
	PA = 153.6
	offx = -0.0595
	offy = -0.4871

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

TBD

"""
