"""
This script is written for CASA 4.5.3
Note that the imaging algorithms were rewritten significantly between CASA 4.5.3 and CASA 4.7.2 
"""

###
# To setup CASA 4.5.3 version, run casa45 in command line:
# > casa45
###


##################################################################
##################################################################
## Short baseline data calibrated by ALMA, sent by Sean
## Selfcalibration is done here
##################################################################
##################################################################

field_SB = 'HT_Lup'
tag = 'SB'   # Short Baselines
SB_data = '../Sean_data_SB/HT_Lup_SB.calibrated_final.ms'
SB_refant = 'DA49'

#split out all the data from the given field
SB_ms = field_SB+'_'+tag+'.ms'
os.system('rm -rf ' + SB_ms + '*')
split2(vis=SB_data,
       field = field_SB,    
       outputvis=SB_ms,
       datacolumn='data')

"""
This portion covers self-calibration and imaging of the continuum of the short baseline data
"""
# initial inspection of data before splitting out and averaging the continuum

plotms(vis = SB_ms, xaxis = 'channel', yaxis = 'amplitude', field = field_SB, 
       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
       avgbaseline = True, iteraxis = 'spw')

# spws 0, 4 contain the CO 2-1 line
contspws = '0~7'
flagmanager(vis=SB_ms, mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
flagchannels='0:1730~2130, 4:1730~2130' 
#this flagging is different (wider) from what Jane/Sean did on their script

flagdata(vis=SB_ms,mode='manual', spw=flagchannels, flagbackup=False, field = field_SB)

SB_initcont = field_SB+'_'+tag+'_initcont.ms'
print(SB_initcont)
os.system('rm -rf ' + SB_initcont + '*')
split2(vis=SB_ms,
       field = '',
       spw=contspws,      
       outputvis=SB_initcont,
       width=[480,8,8,8, 480, 8, 8, 8],
       datacolumn='data')

# Restore flagged line channels
flagmanager(vis=SB_ms,mode='restore',versionname='before_cont_flags')

# Check that amplitude vs. uvdist looks normal
plotms(vis=SB_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30', avgchannel='1000')


### Starting selfcalibration of short baselines

# Settled on the folowing parameters for Briggs weighting and cleaning:
# (some will be changed later on in the script)
# ------ Imaging ------ #
robust = 0.7  # better sidelobes than smaller values
gain = 0.1
imsize = 700
cell = '0.03arcsec'
npercycle = 20
niter = 2000
# --------------------- #
# multiscale = [0, 10, 20, 30] 
## NOTE: HTLup is barely resolved in SB, no multiscale used

# Initial clean
SB_initcontimage = field_SB+'_'+tag+'_initcontinuum'
os.system('rm -rf '+SB_initcontimage+'.*')
clean(vis=SB_initcont, 
      imagename=SB_initcontimage, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      robust=robust,
      gain=gain,
      imsize=imsize,
      cell=cell, 
      interactive=True,
      npercycle=npercycle,niter=niter)

# cleaned for 8 cycles (160 iterations)
# peak: 52.4 mJy/beam  (2.9 mJy source off to NW)
# rms: 135 microJy/beam

SB_selfcalp0 = field_SB+'_'+tag+'_selfcalp0.ms'
os.system('rm -rf '+SB_selfcalp0)
os.system('cp -r ' + SB_initcont + ' ' + SB_selfcalp0)

# First round of phase-only self-cal

SB_p1 = field_SB+'_'+tag+'.p1'
os.system('rm -rf '+SB_p1)
gaincal(vis=SB_selfcalp0, caltable=SB_p1, gaintype='T', combine = 'spw', 
        spw=contspws, refant=SB_refant, calmode='p', 
        solint='inf', minsnr=2.0, minblperant=4)

plotcal(caltable=SB_p1,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180])

applycal(vis=SB_selfcalp0, spw=contspws, spwmap = [0]*8, gaintable=[SB_p1], calwt=True, applymode = 'calonly', flagbackup=True,interp='linearPD')

SB_selfcalp1 = field_SB+'_'+tag+'_selfcalp1.ms'
os.system('rm -rf '+SB_selfcalp1)
split2(vis=SB_selfcalp0, outputvis=SB_selfcalp1, datacolumn='corrected')

npercycle=50
SB_contimagep1 = field_SB+'_'+tag+'_continuump1'
os.system('rm -rf '+SB_contimagep1+'.*')
clean(vis=SB_selfcalp1, 
      imagename=SB_contimagep1, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      robust=robust,
      gain=gain,
      imsize=imsize,
      cell=cell,
      mask=SB_initcontimage+'.mask',
      interactive=True,
      npercycle=npercycle,niter=niter,
      threshold='0.044mJy')

# cleaned for 21 cycles (1050 iterations)
# peak: 57.1 mJy/beam  (3.32 mJy source off to NW)
# rms: 43.4 microJy/beam

# Compare SNR improvement:
peak2 = imstat(imagename=SB_contimagep1+'.image')['max'][0]
noise2 = imstat(imagename=SB_contimagep1+'.image',
       region='annulus[[352pix,345pix],[220pix,400pix]]')['rms'][0]
peak1 = imstat(imagename=SB_initcontimage+'.image')['max'][0]
noise1 = imstat(imagename=SB_initcontimage+'.image',
       region='annulus[[352pix,345pix],[220pix,400pix]]')['rms'][0]
print "# SNR before = ", peak1/noise1, '\n', "# SNR after = ", peak2/noise2, '\n', "# Peak improvement factor", peak2/peak1,'\n', "# Noise reduction factor", noise1/noise2
# SNR before =  416.709996609 
# SNR after =  1314.43110248 
# Peak improvement factor 1.08905164346 
# Noise reduction factor 2.89637928807


# Second round of phase-only self-cal

SB_p2 = field_SB+'_'+tag+'.p2'
os.system('rm -rf '+SB_p2)
gaincal(vis=SB_selfcalp1, caltable=SB_p2, gaintype='T', combine = 'spw,scans', 
        spw=contspws, refant=SB_refant, calmode='p', 
        solint='30s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB_p2,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180])

applycal(vis=SB_selfcalp1, spw=contspws, spwmap = [0]*8, gaintable=[SB_p2], calwt=True, applymode = 'calonly', flagbackup=True,interp='linearPD')

SB_selfcalp2 = field_SB+'_'+tag+'_selfcalp2.ms'
os.system('rm -rf '+SB_selfcalp2)
split2(vis=SB_selfcalp1, outputvis=SB_selfcalp2, datacolumn='corrected')

npercycle=100
SB_contimagep2 = field_SB+'_'+tag+'_continuump2'
os.system('rm -rf '+SB_contimagep2+'.*')
clean(vis=SB_selfcalp2, 
      imagename=SB_contimagep2, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      robust=robust,
      gain=gain,
      imsize=imsize,
      cell=cell,
      mask=SB_contimagep1+'.mask',
      interactive=True,
      npercycle=npercycle,niter=niter,
      threshold='0.043mJy')

# cleaned for 13 cycles (1300 iterations)
# peak: 57.9 mJy/beam  (3.4 mJy source off to NW)
# rms: 42.4 microJy/beam

# Compare SNR improvement:
peak2 = imstat(imagename=SB_contimagep2+'.image')['max'][0]
noise2 = imstat(imagename=SB_contimagep2+'.image',
       region='annulus[[352pix,345pix],[220pix,400pix]]')['rms'][0]
peak1 = imstat(imagename=SB_contimagep1+'.image')['max'][0]
noise1 = imstat(imagename=SB_contimagep1+'.image',
       region='annulus[[352pix,345pix],[220pix,400pix]]')['rms'][0]
print "# SNR before = ", peak1/noise1, '\n', "# SNR after = ", peak2/noise2, '\n', "# Peak improvement factor", peak2/peak1,'\n', "# Noise reduction factor", noise1/noise2
# SNR before =  1314.43110248 
# SNR after =  1367.01327875 
# Peak improvement factor 1.01451509039 
# Noise reduction factor 1.02512398502


# Third round of phase-only self-cal

SB_p3 = field_SB+'_'+tag+'.p3'
os.system('rm -rf '+SB_p3)
gaincal(vis=SB_selfcalp2, caltable=SB_p3, gaintype='T', combine = 'spw,scans', 
        spw=contspws, refant=SB_refant, calmode='p', 
        solint='12s', minsnr=2.0, minblperant=4)

plotcal(caltable=SB_p3,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180])

applycal(vis=SB_selfcalp2, spw=contspws, spwmap = [0]*8, gaintable=[SB_p3], calwt=True, applymode = 'calonly', flagbackup=True,interp='linearPD')

SB_selfcalp3 = field_SB+'_'+tag+'_selfcalp3.ms'
os.system('rm -rf '+SB_selfcalp3)
split2(vis=SB_selfcalp2, outputvis=SB_selfcalp3, datacolumn='corrected')

SB_contimagep3 = field_SB+'_'+tag+'_continuump3'
os.system('rm -rf '+SB_contimagep3+'.*')
clean(vis=SB_selfcalp3, 
      imagename=SB_contimagep3, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      robust=robust,
      gain=gain,
      imsize=imsize,
      cell=cell,
      mask=SB_contimagep2+'.mask',
      interactive=True,
      npercycle=npercycle,niter=niter,
      threshold='0.043mJy')

# cleaned for 16 cycles (1600 iterations)
# peak: 58.3 mJy/beam  (3.4 mJy source off to NW)
# rms: 42.4 microJy/beam

# Compare SNR improvement:
peak2 = imstat(imagename=SB_contimagep3+'.image')['max'][0]
noise2 = imstat(imagename=SB_contimagep3+'.image',
       region='annulus[[352pix,345pix],[220pix,400pix]]')['rms'][0]
peak1 = imstat(imagename=SB_contimagep2+'.image')['max'][0]
noise1 = imstat(imagename=SB_contimagep2+'.image',
       region='annulus[[352pix,345pix],[220pix,400pix]]')['rms'][0]
print "# SNR before = ", peak1/noise1, '\n', "# SNR after = ", peak2/noise2, '\n', "# Peak improvement factor", peak2/peak1,'\n', "# Noise reduction factor", noise1/noise2
# SNR before =  1367.01327875 
# SNR after =  1373.70657725 
# Peak improvement factor 1.00651677583 
# Noise reduction factor 0.998390009816


# Small improvement, moving on to amplitude selfcal
SB_ap1 = field_SB+'_'+tag+'.ap1'
os.system('rm -rf '+SB_ap1)
gaincal(vis=SB_selfcalp3, caltable=SB_ap1, gaintype='T', combine = 'spw', 
        spw=contspws, refant=SB_refant, calmode='ap', gaintable=[SB_p3],
        spwmap=[0]*8, solint='inf', minsnr=3.0, minblperant=4)

plotcal(caltable=SB_ap1,xaxis='time',yaxis='amp',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,0,2.5])

applycal(vis=SB_selfcalp3, spw=contspws, spwmap = [[0]*8, [0]*8],
         gaintable=[SB_p3,SB_ap1], calwt=True, applymode = 'calonly', 
         flagbackup=True,interp='linearPD')

SB_selfcalap1 = field_SB+'_'+tag+'_selfcalap1.ms'
os.system('rm -rf '+SB_selfcalap1)
split2(vis=SB_selfcalp3, outputvis=SB_selfcalap1, datacolumn='corrected')

SB_contimageap1 = field_SB+'_'+tag+'_continuumap1'
os.system('rm -rf '+SB_contimageap1+'.*')
clean(vis=SB_selfcalap1, 
      imagename=SB_contimageap1, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      robust=robust,
      gain=gain,
      imsize=imsize,
      cell=cell,
      mask=SB_contimagep3+'.mask',
      interactive=True,
      npercycle=npercycle,niter=niter,
      threshold='0.037mJy')

# cleaned for 19 cycles (1900 iterations)
# peak: 58.7 mJy/beam  (3.4 mJy source off to NW)
# rms: 37.0 microJy/beam

# Compare SNR improvement:
peak2 = imstat(imagename=SB_contimageap1+'.image')['max'][0]
noise2 = imstat(imagename=SB_contimageap1+'.image',
       region='annulus[[352pix,345pix],[220pix,400pix]]')['rms'][0]
peak1 = imstat(imagename=SB_contimagep3+'.image')['max'][0]
noise1 = imstat(imagename=SB_contimagep3+'.image',
       region='annulus[[352pix,345pix],[220pix,400pix]]')['rms'][0]
print "# SNR before = ", peak1/noise1, '\n', "# SNR after = ", peak2/noise2, '\n', "# Peak improvement factor", peak2/peak1,'\n', "# Noise reduction factor", noise1/noise2
# SNR before =  1373.70657725 
# SNR after =  1587.13817716 
# Peak improvement factor 1.00656057542 
# Noise reduction factor 1.14783865096

# Further amp selfcal does not improve the SNR of the data
# Will conclude the short baselines self-calibration here!

##################################################################
##################################################################


##################################################################
##################################################################
## Long baseline data calibrated by ALMA, sent by Sean
## Selfcalibration is done here
##################################################################
##################################################################

"""
But first: an offset seems to exist between the images of the SB and LB datasets,
when comparing self-calibrated images at their default angular resolution:

Primary component peaks at:
SB = 'maxposf': '15:45:12.8477, -34.17.31.0386, I, 2.38992e+11Hz',
LB = 'maxposf': '15:45:12.8468, -34.17.31.0288, I, 2.38969e+11Hz',

ra0 = au.radec2deg('15:45:12.8477, -34.17.31.0386')[0]
dec0 = au.radec2deg('15:45:12.8477, -34.17.31.0386')[1]
ra1 = au.radec2deg('15:45:12.8468, -34.17.31.0288')[0]
dec1 = au.radec2deg('15:45:12.8468, -34.17.31.0288')[1]
Offset_mas = au.angularSeparation(ra0, dec0, ra1, dec1, returnComponents=True)[0]*3600*1e3
Offset_RA = au.angularSeparation(ra0, dec0, ra1, dec1, returnComponents=True)[1]*3600*1e3
Offset_Dec = au.angularSeparation(ra0, dec0, ra1, dec1, returnComponents=True)[2]*3600*1e3
Offset_RAcosDec = au.angularSeparation(ra0, dec0, ra1, dec1, returnComponents=True)[3]*3600*1e3

RA*cosDec shift = 13.5 mas
Dec shift       = -9.8 mas
Total shift     = 14.85 mas

Tertiary component peaks at:
SB = 'maxposf': '15:45:12.6460, -34.17.29.7486, I, 2.38992e+11Hz',
LB = 'maxposf': '15:45:12.6444, -34.17.29.7388, I, 2.38969e+11Hz',

ra0,dec0 = au.radec2deg('15:45:12.6460, -34.17.29.7486')
ra1,dec1 = au.radec2deg('15:45:12.6444, -34.17.29.7388')
Offset_mas = au.angularSeparation(ra0, dec0, ra1, dec1, returnComponents=True)[0]*3600*1e3
Offset_RA = au.angularSeparation(ra0, dec0, ra1, dec1, returnComponents=True)[1]*3600*1e3
Offset_Dec = au.angularSeparation(ra0, dec0, ra1, dec1, returnComponents=True)[2]*3600*1e3
Offset_RAcosDec = au.angularSeparation(ra0, dec0, ra1, dec1, returnComponents=True)[3]*3600*1e3

RA*cosDec shift = 19.8 mas
Dec shift       = -9.8 mas
Total shift     = 22.1 mas

Given that the tertiary seems more unresolved at both SB and LB,
it provides a better estimate of the offset between the two datasets.
"""

# Shifting phase center of the SB data by ~22mas in total:
# (change phase center so that peaks in tertiary on both datasets coincide)

# Final dataset from selfcalibration is 'SB_selfcalap1', copy to new ms file to apply shift
SB_shift = field_SB+'_'+tag+'_selfcal_shift.ms'
os.system('rm -rf '+SB_shift)
split2(vis=SB_selfcalap1, outputvis=SB_shift, datacolumn='data')

# First, change the phase center of the data by ~22mas total
"""
Original RA/Dec for HT_Lup SB dataset = 15:45:12.851330 -34.17.30.89463 ICRS
which needs to be shifted by  24mas in RA     -9.8mas in Dec
RA/Dec were calculated using the tasks below from Analysis Utilities (by T. Hunter)

ra_SB,dec_SB = au.radec2deg('15:45:12.851330 -34.17.30.89463') # current phase center
ra0,dec0 = au.radec2deg('15:45:12.6460, -34.17.29.7486')       # tertiary peak in SBs
ra1,dec1 = au.radec2deg('15:45:12.6444, -34.17.29.7388')       # tertiary peak in LBs
# Add the offset to the original RA/Dec of the SB
ra_SB_new  = ra_SB  + au.angularSeparation(ra0, dec0, ra1, dec1, returnComponents=True)[1]
dec_SB_new = dec_SB + au.angularSeparation(ra0, dec0, ra1, dec1, returnComponents=True)[2]
# Since these coordinates are in ICRS frame, we compute them in J2000 frame
# because CASA task 'fixplanets' can only take J2000 coordinates:
au.deg2radec(ra_SB_new,dec_SB_new)
#  Out[277]: '15:45:12.852930, -34:17:30.90443'
au.ICRSToJ2000('15:45:12.852930 -34:17:30.90443')
# Separation: radian = 7.86727e-08, degrees = 0.000005, arcsec = 0.016227
#   Out[278]: '15:45:12.85345, -034:17:30.889537'
# 

"""

"""
Calibrators:
VLBI coordinates (J2000)
J1534-3526 15h34m54.687600s -35d26'23.49706"
J1610-3958 16h10m21.879089s -39d58'58.32848  

ALMA coordinates (ICRS)
J1534-3526 15:34:54.688 -035.26.23.497
J1610-3958 16:10:21.879 -039.58.58.328

au.J2000ToICRS('15:34:54.687600 -35:26:23.49706')
Separation: radian = 8.0679e-08, degrees = 0.000005, arcsec = 0.016641
  Out[280]: '15:34:54.68707, -035:26:23.512389'

au.J2000ToICRS('16:10:21.879089 -39:58:58.32848')
Separation: radian = 6.89171e-08, degrees = 0.000004, arcsec = 0.014215
  Out[281]: '16:10:21.87876, -039:58:58.342183'
"""
# Update phase center on the SB observations:
fixvis(vis=SB_shift,outputvis=SB_shift,field=field_SB,phasecenter='J2000 15h45m12.85345s -34d17m30.889537s')
# Check that ms was updated
listobs(SB_shift)
# Changed to: HT_Lup 15:45:12.853450 -34.17.30.88954 J2000

# As a final step, give the same phase center as the LB data.
# But necause 'fixplanets' can only take J2000 coordinates, 
# we need to convert them between ICRS to J2000:
"""
Listobs on the LB dataset gives: HT_Lupi LB  15:45:12.850428 -34.17.30.89677 ICRS
Using the tasks below from Analysis Utilities (by T. Hunter) we generate the new
phase center in J2000 coordinates:
au.ICRSToJ2000('15:45:12.850428 -34:17:30.89677')
Separation: radian = 7.84831e-08, degrees = 0.000004, arcsec = 0.016188
  Out[258]: '15:45:12.85094, -034:17:30.881877'
"""
fixplanets(vis=SB_shift,field=field_SB,direction='J2000 15h45m12.85094s -34d17m30.881877s')
listobs(SB_shift)
# Checked that the updated phase center of SB ms is correct: 
#   HT_Lup 15:45:12.850940 -34.17.30.88188 J2000

# Make an image to see if shift was properly applied:
SB_contimage_shift = field_SB+'_'+tag+'_shift'
os.system('rm -rf '+SB_contimage_shift+'.*')
clean(vis=SB_shift, 
      imagename=SB_contimage_shift, 
      mode='mfs', 
      psfmode='clark', 
      imagermode='csclean', 
      weighting='briggs', 
      robust=robust,
      gain=gain,
      imsize=imsize,
      cell=cell,
      mask=SB_contimagep3+'.mask',
      interactive=True,
      npercycle=npercycle,niter=niter,
      threshold='0.037mJy')



#### QUESTION: do we need to update phase center of LB so that it is also in J2000???
#### ANSWER: Probably yes, since I am not sure if ms files with phase centers defined in different coordinates can be combined together.


##################################################################
##################################################################
## long baseline data
##################################################################
##################################################################
LB_vis = '/almadata02/lperez/LP/HTLup/NAASC_data_LB/calibrated_final.ms' #this is the long-baseline measurement set being calibrated

LB_refant = 'DV24, DV09, DV20, DA57, DA61'
tag = 'LB'   # Long Baselines
field_LB = 'HT_Lupi'

listobs(LB_vis)

# spws 3 and 7 contain the CO 2-1 line, while the others are continuum only
contspws = '0~7'

flagmanager(vis=LB_vis,mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
# velocity range selected for flagging based on compact configuration data
flagchannels='3:1880~2250, 7:1880~2250'

flagdata(vis=LB_vis,mode='manual', spw=flagchannels, flagbackup=False, field = field_LB)

# Average the channels within spws
LB_initcont = field_LB+'_'+tag+'_initcont.ms'
os.system('rm -rf ' + LB_initcont + '*')
split2(vis=LB_vis,
       field = field_LB,
       spw=contspws,      
       outputvis=LB_initcont,
       width=[8,8,8,480, 8, 8, 8, 480], # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
       timebin = '6s',
       datacolumn='data')

# Restore flagged line channels in the original dataset
flagmanager(vis=LB_vis,mode='restore',
            versionname='before_cont_flags')

### Use fixplanets task to change the reference system of the LB observations 
#   from ICRS to J2000 (as the SB dataset is in J2000 system)
"""
Listobs on the LB dataset gives: HT_Lupi LB  15:45:12.850428 -34.17.30.89677 ICRS
Using the tasks below from Analysis Utilities (by T. Hunter) we generate the new
phase center in J2000 coordinates:
au.ICRSToJ2000('15:45:12.850428 -34:17:30.89677')
Separation: radian = 7.84831e-08, degrees = 0.000004, arcsec = 0.016188
  Out[258]: '15:45:12.85094, -034:17:30.881877'
"""
fixplanets(vis=LB_initcont,field=field_LB,
           direction='J2000 15h45m12.85094s -34d17m30.881877s')
listobs(LB_initcont)

### Starting selfcalibration of short and long baselines together

# Concatenate SB and LB datasets
LBSB_concat = field_LB + '_LB_SB_concat.ms'
os.system('rm -rf '+LBSB_concat)
concat(vis=[LB_initcont,SB_shift], concatvis = LBSB_concat)

# Settled on the folowing parameters for Briggs weighting and cleaning:
# (some will be changed later on in the script)
# ------ Imaging ------ #
robust = 0.0  
gain = 0.1
imsize = 3000
cell = '0.003arcsec'
npercycle = 100
niter = 5000
cyclefactor = 5
uvtaper=True
outertaper=['45mas','40mas','-30deg']
multiscale = [0, 17, 50, 84] # beam size ~ 50mas (0x,1x,3x,5xbeam)
# --------------------- #


# Initial clean
LBSB_initcontimage = field_LB +'_'+tag+'_initcontinuum'
os.system('rm -rf '+LBSB_initcontimage+'.*')
clean(vis=LBSB_concat, 
      imagename=LBSB_initcontimage, 
      mode='mfs', 
      multiscale = multiscale, 
      weighting='briggs', 
      robust = robust,
      gain = gain,
      imsize = imsize,
      cell = cell, 
      niter = niter,
      npercycle = npercycle,
      cyclefactor = cyclefactor, 
      uvtaper = uvtaper,
      outertaper = outertaper,
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      imagermode = 'csclean',
      threshold='0.09mJy')

# cleaned for 8 cycles (800 iterations)
# peak: 10.4 mJy/beam  (1.7 mJy source off to NW)
# rms: 30.5 microJy/beam

contspws = '0~15' # both LB and SB spws

LB_selfcalp0 = field_LB+'_'+tag+'_selfcalp0.ms'
os.system('rm -rf '+LB_selfcalp0)
os.system('cp -r ' + LBSB_concat + ' ' + LB_selfcalp0)


# First round of phase-only self-cal

LB_p1 = field_LB+'_'+tag+'.p1'
os.system('rm -rf '+LB_p1)
gaincal(vis=LB_selfcalp0, caltable=LB_p1, gaintype='T', combine = 'spw,scan', 
        spw=contspws, refant=LB_refant, calmode='p', field='0',
        solint='1000s', minsnr=2.0, minblperant=4)

plotcal(caltable=LB_p1,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/01/01/00~2017/05/18/00')
plotcal(caltable=LB_p1,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/06/01/00~2017/12/01/00')

applycal(vis=LB_selfcalp0, spw=contspws, spwmap = [0]*16, gaintable=[LB_p1], 
calwt=True, applymode = 'calonly', flagbackup=True,interp='linearPD')

LB_selfcalp1 = field_LB+'_'+tag+'_selfcalp1.ms'
os.system('rm -rf '+LB_selfcalp1)
split2(vis=LB_selfcalp0, outputvis=LB_selfcalp1, datacolumn='corrected')

# clean after first phase selfcal
LBSB_contimagep1 = field_LB +'_'+tag+'_continuum_p1'
os.system('rm -rf '+LBSB_contimagep1+'.*')
clean(vis=LB_selfcalp1, 
      imagename=LBSB_contimagep1, 
      mode='mfs', 
      multiscale = multiscale, 
      weighting='briggs', 
      robust = robust,
      gain = gain,
      imsize = imsize,
      cell = cell, 
      niter = niter,
      npercycle = npercycle,
      cyclefactor = cyclefactor, 
      uvtaper = uvtaper,
      outertaper = outertaper,
      mask=LBSB_initcontimage+'.mask',
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      imagermode = 'csclean',
      threshold='0.05mJy')

# cleaned for 11 cycles (1100 iterations)
# peak: 10.6 mJy/beam  (1.7 mJy source off to NW)
# rms: 24.5 microJy/beam

# Compare SNR improvement:
peak2 = imstat(imagename=LBSB_contimagep1+'.image')['max'][0]
noise2 = imstat(imagename=LBSB_contimagep1+'.image',
       region='annulus[[1515pix,1455pix],[200pix,500pix]]')['rms'][0]
peak1 = imstat(imagename=LBSB_initcontimage+'.image')['max'][0]
noise1 = imstat(imagename=LBSB_initcontimage+'.image',
       region='annulus[[1515pix,1455pix],[200pix,500pix]]')['rms'][0]
print "# SNR before = ", peak1/noise1, '\n', "# SNR after = ", peak2/noise2, '\n', "# Peak improvement factor", peak2/peak1,'\n', "# Noise reduction factor", noise1/noise2
# SNR before =  340.596624421 
# SNR after =  430.803834045 
# Peak improvement factor 1.01610061165 
# Noise reduction factor 1.24480839205


# Second round of phase-only self-cal
LB_p2 = field_LB+'_'+tag+'.p2'
os.system('rm -rf '+LB_p2)
gaincal(vis=LB_selfcalp1, caltable=LB_p2, gaintype='T', combine = 'spw,scan', 
        spw=contspws, refant=LB_refant, calmode='p', field='0',
        solint='400s', minsnr=2.0, minblperant=4)
#1 of 39 solutions flagged due to SNR < 2 in spw=0 at 2017/09/24/17:53:59.4
#1 of 39 solutions flagged due to SNR < 2 in spw=0 at 2017/09/24/18:00:22.4
#1 of 39 solutions flagged due to SNR < 2 in spw=0 at 2017/09/24/18:14:17.9
#1 of 39 solutions flagged due to SNR < 2 in spw=0 at 2017/09/24/18:43:04.5
#1 of 39 solutions flagged due to SNR < 2 in spw=0 at 2017/09/24/19:36:43.5
#1 of 39 solutions flagged due to SNR < 2 in spw=0 at 2017/09/24/19:50:47.1
#1 of 39 solutions flagged due to SNR < 2 in spw=0 at 2017/09/24/20:05:00.1
#1 of 39 solutions flagged due to SNR < 2 in spw=0 at 2017/09/24/20:11:22.2
#1 of 39 solutions flagged due to SNR < 2 in spw=0 at 2017/09/24/20:24:55.4

plotcal(caltable=LB_p2,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/01/01/00~2017/05/18/00')
plotcal(caltable=LB_p2,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/06/01/00~2017/12/01/00')

applycal(vis=LB_selfcalp1, spw=contspws, spwmap = [0]*16, gaintable=[LB_p2], calwt=True, applymode = 'calonly', flagbackup=True,interp='linearPD')

LB_selfcalp2 = field_LB+'_'+tag+'_selfcalp2.ms'
os.system('rm -rf '+LB_selfcalp2)
split2(vis=LB_selfcalp1, outputvis=LB_selfcalp2, datacolumn='corrected')

# clean after first phase selfcal
LBSB_contimagep2 = field_LB +'_'+tag+'_continuum_p2'
os.system('rm -rf '+LBSB_contimagep2+'.*')
clean(vis=LB_selfcalp2, 
      imagename=LBSB_contimagep2, 
      mode='mfs', 
      multiscale = multiscale, 
      weighting='briggs', 
      robust = robust,
      gain = gain,
      imsize = imsize,
      cell = cell, 
      niter = niter,
      npercycle = npercycle,
      cyclefactor = cyclefactor, 
      uvtaper = uvtaper,
      outertaper = outertaper,
      mask=LBSB_contimagep1+'.mask',
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      imagermode = 'csclean',
      threshold='0.023mJy')

# cleaned for 15 iterations (1500 cycles), then non-interactive
# peak: 10.7 mJy/beam  (1.7 mJy source off to NW)
# rms: 22.9 microJy/beam

# Compare SNR improvement:
peak2 = imstat(imagename=LBSB_contimagep2+'.image')['max'][0]
noise2 = imstat(imagename=LBSB_contimagep2+'.image',
       region='annulus[[1515pix,1455pix],[200pix,500pix]]')['rms'][0]
peak1 = imstat(imagename=LBSB_contimagep1+'.image')['max'][0]
noise1 = imstat(imagename=LBSB_contimagep1+'.image',
       region='annulus[[1515pix,1455pix],[200pix,500pix]]')['rms'][0]
print "# SNR before = ", peak1/noise1, '\n', "# SNR after = ", peak2/noise2, '\n', "# Peak improvement factor", peak2/peak1,'\n', "# Noise reduction factor", noise1/noise2
# SNR before =  430.803834045 
# SNR after =  468.477962692 
# Peak improvement factor 1.01457461012 
# Noise reduction factor 1.07182927994

# Third round of phase-only self-cal
LB_p3 = field_LB+'_'+tag+'.p3'
os.system('rm -rf '+LB_p3)
gaincal(vis=LB_selfcalp2, caltable=LB_p3, gaintype='T', combine = 'spw,scan', 
        spw=contspws, refant=LB_refant, calmode='p', field='0',
        solint='220s', minsnr=2.0, minblperant=4)
# too many solutions flagged due to low SNR to list here!

plotcal(caltable=LB_p3,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/01/01/00~2017/05/18/00')
plotcal(caltable=LB_p3,xaxis='time',yaxis='phase',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,-180,180],
        timerange='2017/06/01/00~2017/12/01/00')

applycal(vis=LB_selfcalp2, spw=contspws, spwmap = [0]*16, gaintable=[LB_p3], calwt=True, applymode = 'calonly', flagbackup=True,interp='linearPD')

LB_selfcalp3 = field_LB+'_'+tag+'_selfcalp3.ms'
os.system('rm -rf '+LB_selfcalp3)
split2(vis=LB_selfcalp2, outputvis=LB_selfcalp3, datacolumn='corrected')

# clean after first phase selfcal
LBSB_contimagep3 = field_LB +'_'+tag+'_continuum_p3'
os.system('rm -rf '+LBSB_contimagep3+'.*')
clean(vis=LB_selfcalp3, 
      imagename=LBSB_contimagep3, 
      mode='mfs', 
      multiscale = multiscale, 
      weighting='briggs', 
      robust = robust,
      gain = gain,
      imsize = imsize,
      cell = cell, 
      niter = niter,
      npercycle = npercycle,
      cyclefactor = cyclefactor, 
      uvtaper = uvtaper,
      outertaper = outertaper,
      mask=LBSB_contimagep2+'.mask',
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      imagermode = 'csclean',
      threshold='0.022mJy')

# cleaned for 10 iterations (1000 cycles), then non-interactive
# peak: 10.9 mJy/beam  (1.7 mJy source off to NW)
# rms: 22.0 microJy/beam


# Compare SNR improvement:
peak2 = imstat(imagename=LBSB_contimagep3+'.image')['max'][0]
noise2 = imstat(imagename=LBSB_contimagep3+'.image',
       region='annulus[[1515pix,1455pix],[200pix,500pix]]')['rms'][0]
peak1 = imstat(imagename=LBSB_contimagep2+'.image')['max'][0]
noise1 = imstat(imagename=LBSB_contimagep2+'.image',
       region='annulus[[1515pix,1455pix],[200pix,500pix]]')['rms'][0]
print "# SNR before = ", peak1/noise1, '\n', "# SNR after = ", peak2/noise2, '\n', "# Peak improvement factor", peak2/peak1,'\n', "# Noise reduction factor", noise1/noise2
# SNR before =  468.477962692 
# SNR after =  494.35289074 
# Peak improvement factor 1.01390775052 
# Noise reduction factor 1.04075730715


# Stopping phase-only selfcal here, smaller solution intervals give too many flagged solutions

# Moving on to amplitude self calibration
LB_ap1 = field_LB+'_'+tag+'.ap1'
os.system('rm -rf '+LB_ap1)
gaincal(vis=LB_selfcalp3, caltable=LB_ap1, gaintype='T', combine = 'spw,scan', 
        spw=contspws, refant=LB_refant, calmode='ap', gaintable=[LB_p3],
        spwmap=[0]*16, solint='1000s', minsnr=3.0, minblperant=4)
#2 of 39 solutions flagged due to SNR < 3 in spw=0 at 2017/09/24/17:59:34.5
#1 of 39 solutions flagged due to SNR < 3 in spw=0 at 2017/09/24/18:16:03.2
#1 of 39 solutions flagged due to SNR < 3 in spw=0 at 2017/09/24/18:46:57.8
#1 of 39 solutions flagged due to SNR < 3 in spw=0 at 2017/09/24/19:35:08.6
#1 of 39 solutions flagged due to SNR < 3 in spw=0 at 2017/09/24/19:52:58.0
#2 of 39 solutions flagged due to SNR < 3 in spw=0 at 2017/09/24/20:22:26.5

plotcal(caltable=LB_ap1,xaxis='time',yaxis='amp',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,0,0],
        timerange='2017/01/01/00~2017/05/18/00')
plotcal(caltable=LB_ap1,xaxis='time',yaxis='amp',
        spw='',iteration='antenna',subplot=221,plotrange=[0,0,0,3],
        timerange='2017/06/01/00~2017/12/01/00')

applycal(vis=LB_selfcalp3, spw=contspws, spwmap = [[0]*16, [0]*16],
         gaintable=[LB_p3,LB_ap1], calwt=True, applymode = 'calonly', 
         flagbackup=True,interp='linearPD')

LB_selfcalap1 = field_LB+'_'+tag+'_selfcalap1.ms'
os.system('rm -rf '+LB_selfcalap1)
split2(vis=LB_selfcalp3, outputvis=LB_selfcalap1, datacolumn='corrected')

# clean after first amp selfcal
LBSB_contimageap1 = field_LB +'_'+tag+'_continuum_ap1'
os.system('rm -rf '+LBSB_contimageap1+'.*')
clean(vis=LB_selfcalap1, 
      imagename=LBSB_contimageap1, 
      mode='mfs', 
      multiscale = multiscale, 
      weighting='briggs', 
      robust = robust,
      gain = gain,
      imsize = imsize,
      cell = cell, 
      niter = niter,
      npercycle = npercycle,
      cyclefactor = cyclefactor, 
      uvtaper = uvtaper,
      outertaper = outertaper,
      mask=LBSB_contimagep3+'.mask',
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      imagermode = 'csclean',
      threshold='0.019mJy')

# cleaned for 15 iterations (1500 cycles), then non-interactive
# peak: 11.6 mJy/beam  (1.7 mJy source off to NW)
# rms: 18.9 microJy/beam


# Compare SNR improvement:
peak2 = imstat(imagename=LBSB_contimageap1+'.image')['max'][0]
noise2 = imstat(imagename=LBSB_contimageap1+'.image',
       region='annulus[[1515pix,1455pix],[200pix,500pix]]')['rms'][0]
peak1 = imstat(imagename=LBSB_contimagep3+'.image')['max'][0]
noise1 = imstat(imagename=LBSB_contimagep3+'.image',
       region='annulus[[1515pix,1455pix],[200pix,500pix]]')['rms'][0]
print "# SNR before = ", peak1/noise1, '\n', "# SNR after = ", peak2/noise2, '\n', "# Peak improvement factor", peak2/peak1,'\n', "# Noise reduction factor", noise1/noise2
# SNR before =  494.35289074 
# SNR after =  614.241685683 
# Peak improvement factor 1.06770819304 
# Noise reduction factor 1.16372304132


# Stopping amp selfcal here, further rounds did not improve the data!

# Apply selfcal solutions to final dataset:
LB_selfcalfinal = field_LB+'_'+tag+'_selfcal_final.ms'
os.system('rm -rf '+LB_selfcalfinal)
split2(vis=LB_selfcalp3, outputvis=LB_selfcalfinal, datacolumn='corrected')

# Make final image with better resolution
# ------ Imaging ------ #
robust = -0.5  
cyclefactor = 7
uvtaper=True
outertaper=['25mas']
multiscale = [0, 10, 30, 50] # beam size ~ 30mas (0x,1x,3x,5xbeam)
# --------------------- #

LBSB_contimage = field_LB +'_'+tag+'_continuum_final'
os.system('rm -rf '+LBSB_contimage+'.*')
clean(vis=LB_selfcalfinal,
      imagename=LBSB_contimage, 
      mode='mfs', 
      multiscale = multiscale, 
      weighting='briggs', 
      robust = robust,
      gain = gain,
      imsize = imsize,
      cell = cell, 
      niter = niter,
      npercycle = npercycle,
      cyclefactor = cyclefactor, 
      uvtaper = uvtaper,
      outertaper = outertaper,
      mask=LBSB_contimageap1+'.mask',
      interactive = True, 
      usescratch = True,
      psfmode = 'hogbom',
      imagermode = 'csclean',
      threshold='0.023mJy')

# cleaned for 10 iterations (1000 cycles), then non-interactive
peak = imstat(imagename=LBSB_contimage+'.image')['max'][0]
noise = imstat(imagename=LBSB_contimage+'.image',
       region='annulus[[1515pix,1455pix],[200pix,500pix]]')['rms'][0]
print peak, noise
#0.00607837643474 2.29113611567e-05





"""
### Choosing robust parameter:
- Robust  1.0 : 45x39mas, large shoulders on the beam (at 50% level), sidelobes positive
- Robust  0.5 : 37x32mas, more structure to the sidelobes but they are still mostly positive, large shoulders (at 40% level) remain
- Robust  0.0 : 28x27mas, sidelobe structure results in multiple +/- structure, shoulders on the beam "resolves" into two high peaks (at 30% level)
- Robust -0.5 : 23x22mas, sidelobe structure results in multiple +/- structure, shoulders on the beam "resolves" into two high peaks (still at 30% level)

Beam shape likely requires tapering!

- Robust -0.5, 30mas : 28x27mas, positive sidelobes at 20%, negative 10%, some structure remains.
- Robust -0.5, 40mas : 43x40mas, sidelobes at +/- 10%

- Robust  0.0, 30mas : 40x36mas, positive sidelobes at 25%, negative ones at 10%, some structure remains, as in -0.5,30mas tapering.
- Robust  0.0, 40mas : 50x44mas, positive sidelobes at 10%, negative sidelobes at <5% 
- Robust  0.0, 45mas : 55x48mas, positive sidelobes at <5%, negative sidelobes at <5% 
- Robust  0.0, 45x40mas, -30deg : 50x48mas: more circular beam... positive sidelobes at 10%, negative sidelobes at <5% 

"""
