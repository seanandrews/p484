"""
Try to figure out wtf is up with the weights

"""

# copy over the individual MSs, before self-calibration
os.system('rm -rf Elias24_SB0.ms*')
os.system('rm -rf Elias24_LB0.ms*')
os.system('rm -rf Elias24_LB1.ms*')
ddir = '/pool/asha1/HOLD/p484_hold/Elias_24/'
split2(vis=ddir+'Elias_24_SB_initcont.ms', datacolumn='data', keepflags=False,
       spw='0~7', width=[4,4,16,4,4,4,4,16], outputvis='Elias24_SB0.ms')
split2(vis=ddir+'Elias_24_LB_initcont.ms', observation='0', datacolumn='data',
       spw='0~3', width=[16,16,16,8], outputvis='Elias24_LB0.ms', 
       keepflags=False)
split2(vis=ddir+'Elias_24_LB_initcont.ms', observation='1', datacolumn='data',
       spw='4~7', width=[16,16,16,8], outputvis='Elias24_LB1.ms', 
       keepflags=False)

# dirty maps to calcaulte theoretical RMS noise (natural weighting)
scales = [0, 15, 45, 90, 180, 360]
os.system('rm -rf Elias24_SB0_cont.*')
tclean(vis='Elias24_SB0.ms', imagename='Elias24_SB0_cont', field='', spw='',
       imsize=3000, cell=0.003, specmode='mfs', deconvolver='multiscale',
       scales=scales, weighting='natural', niter=0, gain=0.1, 
       threshold='0.01mJy', cyclefactor=10, interactive=True, savemodel='none')
# theoretical noise is 15.54224 uJy/beam

os.system('rm -rf Elias24_LB0_cont.*')
tclean(vis='Elias24_LB0.ms', imagename='Elias24_LB0_cont', field='', spw='',
       imsize=3000, cell=0.003, specmode='mfs', deconvolver='multiscale',
       scales=scales, weighting='natural', niter=0, gain=0.1, 
       threshold='0.01mJy', cyclefactor=10, interactive=True, savemodel='none')
# theoretical noise is 4.5552 uJy/beam

os.system('rm -rf Elias24_LB1_cont.*')
tclean(vis='Elias24_LB1.ms', imagename='Elias24_LB1_cont', field='', spw='',
       imsize=3000, cell=0.003, specmode='mfs', deconvolver='multiscale',
       scales=scales, weighting='natural', niter=0, gain=0.1,
       threshold='0.01mJy', cyclefactor=10, interactive=True, savemodel='none')
# theoretical noise is 4.85937 uJy/beam


# get the weights, sum them, sqrt them, and invert them to get a theoretical 
# rms noise level yourself

# grab the weights
tb.open('Elias24_SB0.ms')
weight = tb.getcol("WEIGHT")
flag   = np.squeeze(tb.getcol("FLAG"))
tb.close()
# toss the flagged points
crap = np.any(flag, axis=0)
good = np.squeeze(crap == False)
weight = weight[:,good]
# calculate the RMS noise
rms = 1./np.sqrt(np.sum(weight))
# = 35.65128 uJy/beam

tb.open('Elias24_LB0.ms')
weight = tb.getcol("WEIGHT")
flag   = np.squeeze(tb.getcol("FLAG"))
tb.close()
crap = np.any(flag, axis=0)
good = np.squeeze(crap == False)
weight = weight[:,good]
rms = 1./np.sqrt(np.sum(weight))
# = 10.53004 uJy/beam

tb.open('Elias24_LB1.ms')
weight = tb.getcol("WEIGHT")
flag   = np.squeeze(tb.getcol("FLAG"))
tb.close()
crap = np.any(flag, axis=0)
good = np.squeeze(crap == False)
weight = weight[:,good]
rms = 1./np.sqrt(np.sum(weight))
# = 11.23318 uJy/beam

"""
the ratio of the visibility weight method to the tclean numbers is:
SB0: 35.65128 / 15.54224 = 2.294
LB0: 10.53004 / 4.5552   = 2.312
LB1: 11.23318 / 4.85937  = 2.312

"""
