import numpy as np
import sys
import re

"As Gregor Samsa awoke one morning from uneasy dreams he found himself transformed in his bed into a gigantic insect. - Franz Kafka"

field_names = np.array(['AS_205', 'Elias_24', 'Elias_27', 'DoAr_25', 'Elias_20', 
               'SR_4', 'AS_209', 'WSB_52', 'Wa_Oph_6', 'DoAr_33', 
               'IM_Lupi', 'RU_Lupi', 'Sz_129', 'MY_Lupi', 'GW_Lupi', 
               'HT_Lupi', 'Sz_114', 'HD_143006', 'HD_142666', 'HD_163296'])

src_properties = {'AS_205'   :{'CO_start':-9, 'CO_end':12, 'RA':np.array([16, 11, 31.352]), 'DEC':-np.array([18, 38, 26.24]), 'mask':'[1.5arcsec,1.5arcsec],0deg'}, 
                  'Elias_24' :{'CO_start':-4, 'CO_end':8,  'RA':np.array([16, 26, 24.079]), 'DEC':-np.array([24, 16, 13.85]), 'mask':'[1.5arcsec,1.5arcsec],0deg'},
                  'Elias_27' :{'CO_start':-4, 'CO_end':8,  'RA':np.array([16, 26, 45.022]), 'DEC':-np.array([24, 23, 08.25]), 'mask':'[2.5arcsec,1.4arcsec],117deg'}, 
                  'DoAr_25'  :{'CO_start':-5, 'CO_end':12, 'RA':np.array([16, 26, 23.680]), 'DEC':-np.array([24, 43, 14.34]), 'mask':'[1.8arcsec,0.9arcsec],110deg'}, 
                  'Elias_20' :{'CO_start':-7, 'CO_end':13, 'RA':np.array([16, 26, 18.866]), 'DEC':-np.array([24, 28, 20.17]), 'mask':'[1.0arcsec,0.7arcsec],150deg'}, 
                  'SR_4'     :{'CO_start':-7, 'CO_end':13, 'RA':np.array([16, 25, 56.155]), 'DEC':-np.array([24, 20, 48.70]), 'mask':'[0.8arcsec,0.8arcsec],0deg'},
                  'AS_209'   :{'CO_start':-3, 'CO_end':11, 'RA':np.array([16, 49, 15.293]), 'DEC':-np.array([-14, 22, 09.06]),'mask':'[1.4arcsec,1.4arcsec],0deg'}, 
                  'WSB_52'   :{'CO_start':-5, 'CO_end':16, 'RA':np.array([16, 27, 39.421]), 'DEC':-np.array([24, 39, 15.97]), 'mask':'[0.8arcsec,0.8arcsec],0deg'}, 
                  'Wa_Oph_6' :{'CO_start':-4, 'CO_end':13, 'RA':np.array([16, 48, 45.621]), 'DEC':-np.array([-14, 16, 36.26]),'mask':'[1.5arcsec,1.0arcsec],170deg'}, 
                  'DoAr_33'  :{'CO_start':-8, 'CO_end':13, 'RA':np.array([16, 27, 39.003]), 'DEC':-np.array([23, 58, 19.17]), 'mask':'[0.8arcsec,0.8arcsec],0deg'}, 
                  'IM_Lupi'  :{'CO_start':-3, 'CO_end':13, 'RA':np.array([15, 56, 9.1886]), 'DEC':-np.array([37, 56, 6.51]),  'mask':'[3.0arcsec,2.0arcsec],145deg'},
                  'RU_Lupi'  :{'CO_start':-4, 'CO_end':11, 'RA':np.array([15, 56, 42.294]), 'DEC':-np.array([37, 49, 15.89]), 'mask':'[1.0arcsec,1.0arcsec],0deg'},
                  'Sz_129'   :{'CO_start':-1, 'CO_end':9,  'RA':np.array([15, 59, 16.454]), 'DEC':-np.array([41, 57, 10.74]), 'mask':'[1.0arcsec,1.0arcsec],0deg'},
                  'MY_Lupi'  :{'CO_start':-4, 'CO_end':14, 'RA':np.array([16, 00, 44.500]), 'DEC':-np.array([41, 55, 31.34]), 'mask':'[1.6arcsec,0.8arcsec],60deg'}, 
                  'GW_Lupi'  :{'CO_start':-1, 'CO_end':8,  'RA':np.array([15, 46, 44.709]), 'DEC':-np.array([34, 30, 36.11]), 'mask':'[1.5arcsec,1.5arcsec],0deg'}, 
                  'HT_Lupi'  :{'CO_start':-4, 'CO_end':14, 'RA':np.array([15, 45, 12.848]), 'DEC':-np.array([34, 17, 31.04]), 'mask':'[0.8arcsec,0.8arcsec],0deg'}, 
                  'Sz_114'   :{'CO_start':1,  'CO_end':8,  'RA':np.array([16, 9, 1.834]),   'DEC':-np.array([39, 5, 12.85]),  'mask':'[1.0arcsec,1.0arcsec],0deg'}, 
                  'HD_143006':{'CO_start':-4, 'CO_end':14, 'RA':np.array([15, 58, 36.897]), 'DEC':-np.array([22, 57, 15.58]), 'mask':'[1.0arcsec,1.0arcsec],0deg'}, 
                  'HD_142666':{'CO_start':-4, 'CO_end':14, 'RA':np.array([15, 56, 40.005]), 'DEC':-np.array([22, 01, 40.39]), 'mask':'[1.0arcsec,0.7arcsec],165deg'}, 
                  'HD_163296':{'CO_start':-15,'CO_end':20, 'RA':np.array([17, 56, 21.279]), 'DEC':-np.array([21, 57, 22.44]), 'mask':'[3.0arcsec,2.0arcsec],132deg'}}

#split2(vis = '../IM_Lup/Im_Lupi_SB1_initcont.ms', outputvis = 'Im_Lupi_SB1_initcont.ms', datacolumn = 'data')

#####################################################
# CHANGE THESE PARAMETERS AS APPROPRIATE
#####################################################
field = 'Im_Lupi'
SB_vis = 'IM_Lup_SB2_contap1.ms' #this is the self-calibrated measurement set that we provided
LB_vis = 'Im_Lupi_SB1_initcont.ms' #this is the long-baseline measurement set being calibrated
command_log_path ='/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_Xbd4641_X1e/group.uid___A001_Xbd4641_X22/member.uid___A001_Xbd4641_X23/log/uid___A001_Xbd4641_X23.casa_commands.log' #this is the path to the casa command log in the 'log' directory after pipeline calibration is completed
interactive = False
CO_start = -3 #starting LSRK velocity for CO emission in km/s
CO_end =  13 #ending LSRK velocity for CO emission in km/s



#parameters for imaging
imsize = 500 #please avoid making this smaller
cell = 0.05 #Cell size in arcseconds. Please avoid making the cell size larger. 
mask = 'ellipse[[236pix,249pix],[3arcsec,2arcsec],145deg]' #feel free to experiment with this 
initthreshold = '0.6mJy' #feel free to experiment with this 
scales  = [0,10,30,50] #feel free to experiment with this

#parameters for self-cal
solint = '30s' #feel free to experiment with this. If too many solutions are being thrown out, make this bigger! 
####################################################
# Constants
####################################################
cc = 299792458.
CO_restfreq = 2.30538e11
#####################################################
# Helper functions
#####################################################

def lookup_refant(casa_command_log):
    #this assumes that there's only one execution block that was run through the pipeline
    f = open(casa_command_log)
    text = f.read()
    f.close()
    position = text.find('refant=')
    return text[position+9:position+13]

def LSRKvel_to_chan(msfile, field, spw, restfreq, LSRKvelocity):
    """
    Identifies the channel(s) corresponding to input LSRK velocities. 
    Useful for choosing which channels to split out or flag if a line is expected to be present

    Parameters:
    msfile: Name of measurement set (string)
    spw: Spectral window number (int)
    restfreq: Rest frequency in Hz (float)
    LSRKvelocity: input velocity in LSRK frame in km/s (float or array of floats)

    Returns: 
    Channel number most closely corresponding to input LSRK velocity 
    """
    tb.open(msfile+"/SPECTRAL_WINDOW")
    chanfreqs = tb.getcol("CHAN_FREQ", startrow = 0, nrow = 1)
    tb.close()
    tb.open(msfile+"/FIELD")
    fieldnames = tb.getcol("NAME")
    tb.close()
    nchan = len(chanfreqs)
    ms.open(msfile)
    lsrkfreqs = ms.cvelfreqs(spwids = [spw], fieldids = np.where(fieldnames==field)[0][0], mode = 'channel', nchan = nchan, start = 0, outframe = 'LSRK')
    chanvelocities = (restfreq-lsrkfreqs)/restfreq*cc/1.e3 #converted to LSRK velocities in km/s
    if type(LSRKvelocity)==np.ndarray:
        outchans = np.zeros_like(LSRKvelocity)
        for i in range(len(LSRKvelocity)):
            outchans[i] = np.argmin(np.abs(chanvelocities - LSRKvelocity[i]))
        return outchans
    else:
        return np.argmin(np.abs(chanvelocities - LSRKvelocity))

def check_same_field(ms1, ms2):
    """
    Double-check that the two measurement sets are actually of the same source (by seeing if the phase-centers are within 10 arcsec of one another)
    """
    ms.open(ms1)
    dir1 = ms.getfielddirmeas("PHASE_DIR")
    ms.close()
    RA1 = dir1['m0']['value'] #RA in radians
    DEC1 = dir1['m1']['value'] #DEC in radians

    ms.open(ms2)
    dir2 = ms.getfielddirmeas("PHASE_DIR")
    ms.close()
    RA2 = dir2['m0']['value'] #RA in radians
    DEC2 = dir2['m1']['value'] #DEC in radians

    if np.linalg.norm(np.array([RA1, DEC1])-np.array([RA2, DEC2])) < 10/3600.*np.pi/180.: 
        pass
    else:
       print "Are you sure these two measurement sets are of the same field?"
       sys.exit()

def convert_RA_to_rad(RA_array):
    assert len(RA_array)==3
    return 15*np.pi/180.*((RA_array[0]-12.)+RA_array[1]/60.+RA_array[2]/3600.)-np.pi

def convert_DEC_to_rad(DEC_array):
    assert len(DEC_array)==3
    return np.pi/180.*((DEC_array[0])+DEC_array[1]/60.+DEC_array[2]/3600.)

     
    
def generate_mask(field, vis, imsize, cell):
    """
    Generate string to enter as mask parameter for tclean
    """
    if field=='AS_205':
        pass
    elif field=='HT_Lupi':
        pass
    else:
        ms.open(vis)
        phasedir = ms.getfielddirmeas("PHASE_DIR")
        ms.close()
        fieldRA = phasedir['m0']['value'] #RA in radians
        fieldDEC = phasedir['m1']['value'] #DEC in radians
    sourceRA = convert_RA_to_rad(src_properties[field]['RA'])
    sourceDEC = convert_DEC_to_rad(src_properties[field]['DEC'])
    xpix = 0.5*imsize-(fieldRA-sourceRA)*3600*180/np.pi*1/cell*(-1)
    ypix = 0.5*imsize-(fieldDEC-sourceDEC)*3600*180/np.pi*1/cell
    print 'ellipse[[%dpix,%dpix],'% (xpix, ypix) +src_properties[field]['mask']+']'


#####################################################
# START OF IMAGING AND SELF-CAL
####################################################

#LB1_refant = lookup_refant(command_log_path) #this can also be manually entered
contspws = '0~2'
LB1_initcont = 'Im_Lupi_SB1_initcont.ms'
LB1_refant = 'DA59'
tag = 'EB1'
cellsize = str(cell)+'arcsec'

"""
This portion covers self-calibration and imaging of the continuum of the short baseline data
"""

# initial inspection of data before splitting out and averaging the continuum

#plotms(vis = SB1, xaxis = 'channel', yaxis = 'amplitude', field = field, 
#       ydatacolumn = 'data',avgtime = '1e8', avgscan = True, 
#       avgbaseline = True, iteraxis = 'spw')

print "SPLITTING OUT AND AVERAGING CONTINUUM DATA"

"""
# spw 0 contains the CO 2-1 line, while the other three are continuum SPWs
contspws = '0~3'

flagmanager(vis=LB_vis,mode='save', versionname='before_cont_flags')

# Flag the CO 2-1 line
flagchannels='0:'+str(LSRKvel_to_chan(LB_vis, field, 0, CO_restfreq, CO_start-2))+'~'+ str(LSRKvel_to_chan(LB_vis, field, 0, CO_restfreq, CO_end+2))

flagdata(vis=LB_vis,mode='manual', spw=flagchannels, flagbackup=False, field = field)

# Average the channels within spws
LB1_initcont = field+'_'+tag+'_initcont.ms'
os.system('rm -rf ' + LB1_initcont + '*')
split2(vis=LB_vis,
       field = field,
       spw=contspws,      
       outputvis=LB1_initcont,
       width=[480,8,8,8], # ALMA recommends channel widths <= 125 MHz in Band 6 to avoid bandwidth smearing
       timebin = '6s',
       datacolumn='data')


# Restore flagged line channels
flagmanager(vis=LB_vis,mode='restore',
            versionname='before_cont_flags')


# Check that amplitude vs. uvdist looks normal
#plotms(vis=LB1_initcont,xaxis='uvdist',yaxis='amp',coloraxis='spw', avgtime = '30')

# Inspect individual antennae. We do this step here rather than before splitting because plotms will load the averaged continuum much faster 

#plotms(vis = LB1_initcont, xaxis = 'time', yaxis = 'phase', field = field, 
#       ydatacolumn = 'data',avgchannel = '16', 
#       coloraxis = 'spw', iteraxis = 'antenna')

#plotms(vis = LB1_initcont, xaxis = 'time', yaxis = 'amp', field = field, 
#       ydatacolumn = 'data',avgchannel = '16', 
#       coloraxis = 'spw', iteraxis = 'antenna')

check_same_field(SB_vis, LB1_initcont)

print "MAKING INITIAL IMAGE"
delmod(vis = SB_vis)
delmod(vis = LB1_initcont)

# Initial clean
LB1_initcontimage = field+'_'+tag+'_initcontinuum'
os.system('rm -rf '+LB1_initcontimage+'.*')
#tclean(vis=[SB_vis, LB1_initcont], 
tclean(vis = LB1_initcont,
      imagename=LB1_initcontimage, 
      specmode='mfs', 
      deconvolver = 'multiscale',
      scales = scales, 
      weighting='briggs', 
      robust=0.5,
      gain = 0.1,
      imsize=imsize,
      cell=cellsize, 
      mask=mask,
      threshold = initthreshold,
      niter = 50000,
      nterms = 1,
      savemodel = 'modelcolumn', 
      interactive=interactive)

print "STARTING PHASE SELF-CAL"

# One round of phase-only self-cal
LB1_p1 = field+'_'+tag+'.p1'
os.system('rm -rf '+LB1_p1)
gaincal(vis=LB1_initcont, caltable=LB1_p1, gaintype='T', combine = 'spw,scan', 
        spw=contspws, refant=LB1_refant, calmode='p', 
        solint=solint, minsnr=2.0, minblperant=4)

#plotcal(caltable=LB1_p1, xaxis = 'time', yaxis = 'phase',subplot=441,iteration='antenna')

#applycal(vis=LB1_initcont, spw=contspws, spwmap = [0]*4, gaintable=[LB1_p1], calwt=True, flagbackup=False)
applycal(vis=LB1_initcont, spw=contspws, spwmap = [0]*3, gaintable=[LB1_p1], calwt=True, flagbackup=False)

LB1_contms_p1 = field+'_'+tag+'_contp1.ms'
os.system('rm -rf '+LB1_contms_p1)
split2(vis=LB1_initcont, outputvis=LB1_contms_p1, datacolumn='corrected')


#delmod(vis = SB_vis)
#delmod(vis = LB1_contms_p1)
LB1_contimage_p1 = field+'_'+tag+'_p1continuum'
os.system('rm -rf '+LB1_contimage_p1+'.*')
#tclean(vis=[SB_vis, LB1_contms_p1], 
tclean(vis= LB1_contms_p1, 
      imagename=LB1_contimage_p1, 
      specmode='mfs', 
      deconvolver = 'multiscale',
      scales = scales, 
      weighting='briggs', 
      robust=0.5,
      gain = 0.1,
      imsize=imsize,
      cell=cellsize, 
      mask=mask,
      threshold = '0.075mJy',
      niter = 50000,
      nterms = 1,
      savemodel = 'modelcolumn', 
      interactive=interactive)

"""

