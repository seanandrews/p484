"""
This script is written for CASA 5.1.1-5.

Input datasets
   AS_209_SB1_contfinal.ms
   AS_209_SB2_contfinal.ms
   AS_209_SB3_contfinal.ms
   calibrated_final.ms      --> calibrated LB visibilities

Reduction steps:
   1) Spectral average the LB visibilities to reduce the file size
      output = averageLB()

"""
import os

doplot = False

# Set visibilities
SB1 = 'AS_209_SB1_contfinal.ms'
SB2 = 'AS_209_SB2_contfinal.ms'
SB3 = 'AS_209_SB3_contfinal.ms'
LB1 = 'AS_209_LB_initcont.ms'

# Other parameters
field    = 'AS_209'
refant   = 'DA61, DV24'
interactive = True

# Center of the mask in RA/DEC and radius.
# If none, then it will be set to the phase center
RAMASK   = None
DECMASK  = None
MASKTYPE = 'ellipse'
RADIUS   = 1.1  # arcsec
EMAJ     = 1.20  # arcsec
EMIN     = 1.00  # arcsec
EPA      = 90.  # deg

# Default clean parameters
CELL        = '0.003arcsec'
CYCLEFACTOR = 5
FIELD       = field
GAIN        = 0.1
IMAGERMODE  = 'csclean'
IMSIZE      = 2400
MODE        = 'mfs'
MULTISCALE  = [0, 20, 40, 80, 160, 320]
PSFMODE     = 'hogbom'
ROBUST      = 0.5
WEIGHTING   = 'briggs'

# Gain parameters
INTERP      = 'linearperobs'
MINSNR      = 2.
MINBLPERANT = 4

def getNspw(vis):
   """ Returns number of spectral windows in measurement set """
   ms.open(vis)
   nspw = len(ms.getspectralwindowinfo())
   ms.close()
   return nspw


def averageLB(output=LB1, input='calibrated_final.ms'):
   LB_vis = 'calibrated_final.ms'
   field = FIELD,

   LB1_refant = 'DA61, DV24'
   tag = 'LB'

   # spws 3 and 7 contain the CO 2-1 line, while the others are continuum only
   spw = '0~%d' % getNspw(LB_vis)

   # save flags
   flagmanager(vis=LB_vis,mode='save', versionname='before_cont_flags')

   # Flag the CO 2-1 line
   # velocity range selected for flagging based on compact configuration data
   flagchannels='3:1870~1970, 7:1870~1970'

   flagdata(vis=LB_vis, mode='manual', spw=flagchannels, flagbackup=False, field = FIELD)

   # Average the channels within spws
   LB1_initcont = FIELD+'_'+tag+'_initcont.ms'
   os.system('rm -rf ' + LB1_initcont + '*')
   split2(vis=LB_vis,
          field = FIELD,
          spw=spw,      
          outputvis=LB1_initcont,
          width=[8,8,8,480, 8, 8, 8, 480], # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
          timebin = '6s',
          datacolumn='data')

   # Restore flagged line channels
   flagmanager(vis=LB_vis,mode='restore',
               versionname='before_cont_flags')

   plotms(vis=LB1_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30')

   # Return output VIS file
   return output


def setMask(vis, radius=RADIUS, emaj=EMAJ, emin=EMIN, epa=EPA, 
            rao=None, deco=None, field=FIELD, type='ellipse'):
   """ Make a circular mask with radius (arcsec) centered on (rao, deco).
       If rao or deco is None, then the phase center is chosen.

       Inputs
          vis   : Input measurement set
          radius: Radius of the mask in arcsecond (floating point)
          rao   : Center RA  of mask (format: 19h45m13.4s)
          deco  : Center Dec of mask (format: 12d23m05.3s)
          field : Name of the field. Used only if rao or dec is None

       Output:
          A string containing the mask.
   """

   # Get centeral ra or dec
   if rao is None or deco is None:
      # Open measurement set and get metadata
      ms.open(vis)
      msmd = ms.metadata()

      # Get field numbers
      try:
         ifield = msmd.fieldsforname(field)
      except:
         raise Exception,'Could not find field number for %s' % field

      # Get ra/dec. There could be multiple field numbers for the source.
      # This assumes the field center does not change between fields.
      mydir = ms.getfielddirmeas('PHASE_DIR', ifield[0])
      ra  = mydir['m0']['value']
      dec = mydir['m1']['value']
      ra  = qa.formxxx('%.12frad'%ra,  format='hms', prec=5)
      dec = qa.formxxx('%.12frad'%dec, format='dms', prec=5)

      # Convert to hms/dms delimiters.
      # For some reason, qa formats ra with ":", while dec is formatted with "."
      ra  = ra.strip(' ').replace(':','h',1).replace(':','m',1) + 's'
      dec = dec.strip(' ').replace('.','d',1).replace('.','m',1) + 's'

      # Close measurement set
      ms.close()
   else:
      ra  = rao
      dec = deco

   # Save mask
   if type == 'ellipse':
      mask = 'ellipse[[%s, %s], [%farcsec, %farcsec], %fdeg]' % (ra, dec, emaj, emin, epa)
   elif type == 'circle':
      mask = 'circle[[%s, %s], %farcsec]' % (ra, dec, radius)
   else:
      raise Exception, 'Mask type is not know: %s' % type

   # Done
   return mask


def makeImage(vis,                     imagename,         mask=None,
              field=FIELD,             observation=None,  niter=5,
              mode=MODE,               psfmode=PSFMODE,   imagermode=IMAGERMODE,
              weighting=WEIGHTING,     robust=ROBUST,     gain=GAIN,
              imsize=IMSIZE,           cell=CELL,         multiscale=MULTISCALE,   
              cyclefactor=CYCLEFACTOR, usescratch=True,   interactive=True):
    print ''
    print '*** Creating continuum image %s from %s with niter=%d' % (imagename, vis, niter)
    os.system('rm -rf %s.*' % imagename)
    clean(vis=vis, 
          field=field,
          mask=mask,
          imagename=imagename, 
          observation=observation,
          niter=niter,
          mode=mode,
          psfmode=psfmode,
          imagermode=imagermode,
          cyclefactor=cyclefactor,
          weighting=weighting,
          robust=robust,
          gain=gain,
          imsize=imsize,
          cell=cell,
          multiscale=multiscale,
          usescratch=usescratch,
          interactive=interactive)


def runSelfcal(vis,               outputvis=None,        caltable='selfcal', 
               spw=None,          spwmap=None,           combine=None,
               gaintype=None,     calmode=None,          refant=None,
               solint=None,       minsnr=MINSNR,         minblperant=MINBLPERANT,
               xaxis='scan',      yaxis='phase',         applymode='calonly',   
               interpmode=None,   calwt=True,            doplot=True,
               apply=True):
   # Clear old files
   os.system('rm -rf %s' % caltable)

   # Run gaincal
   print ''
   print '*** Running selfcal on %s' % vis
   gaincal(vis=vis, caltable=caltable, gaintype=gaintype, spw=spw, combine=combine, 
           refant=refant, calmode=calmode, solint=solint, minsnr=minsnr, minblperant=minblperant)

   # Applying gaincal
   if doplot:
      plotcal(caltable=caltable, xaxis=xaxis, yaxis=yaxis, subplot=441, iteration='antenna')
   if apply:
      print ''
      print '*** Running applycal on %s' % vis
      applycal(vis=vis, spw=spw, spwmap=spwmap, gaintable=[caltable], applymode=applymode,
               flagbackup=False, interp=interpmode, calwt=calwt)

   # Save corrected continuum file
   if outputvis is not None:
      print ''
      print '*** Writing corrected data to %s' % outputvis
      os.system('rm -rf %s' % outputvis)
      split2(vis=vis, outputvis=outputvis, datacolumn='corrected')

# Check the long baseline observations for each execution and the combined image
# makeImage(LB1, observation=0)
# makeImage(LB1, observation=1)
# makeImage(LB1)

# Set visibility file, mask, and spectral windows
vis = LB1
mask = setMask(vis, radius=RADIUS, rao=None, deco=None)
nspw = getNspw(vis)
spw = '0~%d' % (nspw-1)
spwmap = [0] * nspw

# First round of selfcal on LB data
contimage     = field + '_initcontinuum'
caltable      = field + '_gaincal.p1'
vis_selfcal   = field + '_contp1.ms'
# makeImage(vis, imagename=contimage, mask=mask, niter=10000, robust=2, interactive=False)
# runSelfcal(vis, caltable=caltable, gaintype='T', combine='spw,scan', spw=spw, spwmap=spwmap, refant=refant, calmode='p', solint='60s', outputvis=vis_selfcal)

# Second round of selfcal on LB data
if False:
   vis = vis_selfcal
   contimage     = field + '_continuump1'
   caltable      = field + '_gaincal.p2'
   vis_selfcal   = field + '_contp2.ms'
   makeImage(vis, imagename=contimage, mask=mask, niter=100)
   runSelfcal(vis, caltable=caltable, gaintype='T', combine='spw,scan', spw=spw, spwmap=spwmap, 
              refant=refant, calmode='p', solint='90s', outputvis=vis_selfcal)

   # Amplitude selfcal
   vis           = vis_selfcal
   caltable      = field + '_gaincal.ap1'
   vis_selfcal   = field + '_contap1.ms'
   runSelfcal(vis, caltable=caltable, gaintype='T', combine='spw,scan', spw=spw, spwmap=spwmap, refant=refant, calmode='ap', solint='60s', outputvis=vis_selfcal)

# Make final continuum image for LB only
print ''
print '*** Making final continuum image'
vis = vis_selfcal
contimage = field + '_ap1continuum'
# makeImage(vis, imagename=contimage, mask=mask, niter=10000, interactive=False)

# Concatenate LB and SB visibilities
vis_output = 'AS_209_contmerged.ms'
os.system('rm -rf %s' % vis_output)
vis = LB1
visFiles = [SB1, SB2, SB3, vis]
print ''
print '*** Merging visibilities into %s' % vis_output
print '*** Input = %s' % str(visFiles)
concat(visFiles, concatvis=vis_output, dirtol = '1arcsec', copypointing = False)

# First round of selfcal on combined LB+SB image
print ''
print '*** Creating images using ',vis
vis = vis_output
caltable      = field + '_gaincal.p3'
vis_selfcal   = field + '_contp3.ms'
contimage = field + '_combined_contin'
nspw = getNspw(vis)
spw = '0~%d' % (nspw-1)
spwmap = [0] * nspw
makeImage(vis, imagename=contimage, mask=mask, niter=10000, robust=2.0, interactive=False)
runSelfcal(vis, caltable=caltable, gaintype='T', combine='spw,scan', spw=spw, spwmap=spwmap, refant=refant, calmode='p', solint='30s', outputvis=vis_selfcal)
makeImage(vis_selfcal, imagename='test_30_r2', mask=mask, niter=10000, robust=0.5, interactive=False)
stop

# Second round of selfcal on combined LB+SB image
print ''
print '*** Creating images using ',vis
vis = vis_selfcal
caltable      = field + '_gaincal.p4'
vis_selfcal   = field + '_contp4.ms'
contimage = field + '_combined2_contin'
makeImage(vis, imagename=contimage, mask=mask, niter=10000, robust=0.5, interactive=False)
runSelfcal(vis, caltable=caltable, gaintype='T', combine='spw,scan', spw=spw, spwmap=spwmap, refant=refant, calmode='p', outputvis=vis_selfcal, solint='90s')

# Make final image
vis = vis_selfcal
contimage = field + '_final'
makeImage(vis, imagename=contimage, mask=mask, niter=10000, robust=0.0, interactive=False)
