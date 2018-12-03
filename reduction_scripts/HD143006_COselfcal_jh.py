LB1vis = '/data/sandrews/LP/2016.1.00484.L/science_goal.uid___A001_Xbd4641_X1a/group.uid___A001_Xbd4641_X1b/member.uid___A001_Xbd4641_X1c/calibrated/calibrated_final.ms'
#split out individual observations from long-baseline dataset 
split(vis=LB1vis,
              field = 'HD_143006',
              spw = '0~7',      
              outputvis = 'HD143006_LB1_lines.ms',
              width = [128,128,128,1, 128, 128, 128, 1],
              timebin = '6s',
              datacolumn='data',
              intent = 'OBSERVE_TARGET#ON_SOURCE',
              keepflags = False)

concat(vis = ['HD143006_SB_contp0.ms', 'HD143006_LB1_lines.ms'], concatvis = 'HD143006_concat_LBlines.ms',  dirtol = '0.1arcsec', copypointing = False)

prefix = 'HD143006'

combined_contspws = '0~28'
combined_spwmap =  [0,0,0,3,3,3,6,6,6,9,9,9,9,13,13,13,13,17,17,17,17,21,21,21,21,25,25,25,25]

applycal(vis='HD143006_concat_LBlines.ms', spw=combined_contspws, spwmap = [combined_spwmap]*4, gaintable=[prefix+'_combined.p1',prefix+'_combined.p2', prefix+'_combined.p3', prefix+'_combined.p4'], interp = 'linearPD', calwt = True, applymode = 'calonly')

split(vis ='HD143006_concat_LBlines.ms', outputvis = 'HD143006_LB_COselfcal.ms', datacolumn='corrected', keepflags = False, spw = '24, 28') #add SPW number

fitspw = '0:0~1905;1953~3839, 1:0~1905;1953~3839' # channels for fitting continuum
uvcontsub(vis='HD143006_LB_COselfcal.ms',
          spw='0~1', 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=1,
          want_cont=False) 

mstransform(vis = 'HD143006_LB_COselfcal.ms.contsub', outputvis = 'HD143006_LB1_CO.cvel',  keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='-1.0km/s',width='0.35km/s',nchan=60, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

split(vis='/data/astrochem1/jane/HD143006_TC.ms',
              field = 'HD143006',
              spw = '0~2',      
              outputvis = 'HD143006_SB2_lines.ms',
              width = [1, 960, 3840],
              datacolumn='data',
              intent = 'OBSERVE_TARGET#ON_SOURCE',
              keepflags = False)

concat(vis = ['HD143006_SB1_initcont.ms', 'HD143006_SB2_lines.ms', 'HD143006_SB3_initcont.ms'], concatvis = 'HD143006_concat_SBlines.ms',  dirtol = '0.1arcsec', copypointing = False)

applycal(vis='HD143006_concat_SBlines.ms', spw='0~20', gaintable=[prefix+'_SB.p1',prefix+'_SB.p2'], interp = 'linearPD', calwt = True, applymode = 'calonly')

split(vis ='HD143006_concat_SBlines.ms', outputvis = 'HD143006_SB2_COselfcal.ms', datacolumn='corrected', keepflags = False, spw = '6') 

fitspw = '0:200~450;550~959' # channels from 0 to 200 don't look great
uvcontsub(vis='HD143006_SB2_COselfcal.ms',
          spw='0', 
          fitspw=fitspw, 
          excludechans=False, 
          solint='int',
          fitorder=1,
          want_cont=False) 

mstransform(vis = 'HD143006_SB2_COselfcal.ms.contsub', outputvis = 'HD143006_SB2_CO.cvel',  keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='-1.0km/s',width='0.35km/s',nchan=60, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

tclean(vis=['HD143006_SB1_CO.cvel','HD143006_SB2_CO.cvel','HD143006_SB3_CO.cvel', 'HD143006_LB1_CO.cvel'], imagename='HD143006_COhires',specmode = 'cube',imsize=1000, deconvolver = 'multiscale',  
      start='-1km/s',width='0.35km/s',nchan=60,  
      outframe='LSRK', veltype='radio', restfreq='230.538GHz',
      cell='0.01arcsec', scales = [0,10,50,75], gain=0.1,
      weighting='briggs', robust=1.0,threshold = '6.0mJy', niter = 100000, 
      interactive=True, nterms = 1, restoringbeam = 'common') 

immoments(imagename = 'HD143006_COhires.image', moments = [0], includepix = [.003,20], outfile = 'HD143006_COhires.mom0')

immoments(imagename = 'HD143006_COhires.image', moments = [1], includepix = [.005,20], outfile = 'HD143006_COhires.mom1')

immoments(imagename = 'HD143006_COhires.image', moments = [8], includepix = [.005,20], outfile = 'HD143006_COhires.mom8')


mstransform(vis = '/pool/firebolt1/LPscratch/HD_143006/HD143006_SB3_CO21.ms.contsub', outputvis = 'HD143006_SB3_CO.cvel2',  keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='-1.0km/s',width='0.5km/s',nchan=35, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

mstransform(vis = '/data/sandrews/LP/reduced_data/HD_143006/visibilities/HD_143006_SB1_CO21.ms.contsub', outputvis = 'HD143006_SB1_CO.cvel2',  keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='-1.0km/s',width='0.5km/s',nchan=35, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

mstransform(vis = 'HD143006_SB2_COselfcal.ms.contsub', outputvis = 'HD143006_SB2_CO.cvel2',  keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='-1.0km/s',width='0.5km/s',nchan=35, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')

mstransform(vis = 'HD143006_LB_COselfcal.ms.contsub', outputvis = 'HD143006_LB1_CO.cvel2',  keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='-1.0km/s',width='0.5km/s',nchan=35, outframe='LSRK', veltype='radio', restfreq='230.53800GHz')


tclean(vis=['HD143006_SB1_CO.cvel2','HD143006_SB2_CO.cvel2','HD143006_SB3_CO.cvel2', 'HD143006_LB1_CO.cvel2'], imagename='HD143006_CO_test',specmode = 'cube',imsize=1000, deconvolver = 'multiscale',  
      start='-1km/s',width='0.5km/s',nchan=35,  
      outframe='LSRK', veltype='radio', restfreq='230.538GHz',
      cell='0.008arcsec', scales = [0,10,50,75], gain=0.05,
      weighting='briggs', robust=1.0,threshold = '6.0mJy', niter = 100000, 
      interactive=True, nterms = 1, restoringbeam = 'common') 

immoments(imagename = 'HD143006_CO_test.image', moments = [0], includepix = [0,20], mask = 'HD143006_CO_test.mask', outfile = 'HD143006_CO_test.mom0')
immoments(imagename = 'HD143006_CO_test.image', moments = [8], includepix = [.005,20],  outfile = 'HD143006_CO_test.mom8')

mstransform(vis = '/data/astrochem1/jane/diskevol/uppersco/HD143006/data_1.3mm/HD143006_13CO.ms.contsub', outputvis = 'HD143006_SB1_13CO.cvel',  keepflags = False, datacolumn = 'data', regridms = True,mode='velocity',start='3km/s',width='0.2km/s',nchan=40, outframe='LSRK', veltype='radio', restfreq='220.39868420GHz')

tclean(vis='HD143006_SB1_13CO.cvel', imagename='HD143006_13CO',specmode = 'cube',imsize=500, deconvolver = 'multiscale',  
      start='3km/s',width='0.2km/s',nchan=40,  
      outframe='LSRK', veltype='radio', restfreq='220.39868420GHz',
      cell='0.05arcsec', scales = [0,10,20,30], gain=0.1,
      weighting='briggs', robust=1.0,threshold = '10.0mJy', niter = 100000, 
      interactive=True, nterms = 1, restoringbeam = 'common') 

immoments(imagename = 'HD143006_13CO.image', moments = [0], includepix = [.005,20], outfile = 'HD143006_13CO.mom0')
immoments(imagename = 'HD143006_13CO.image', moments = [1], includepix = [.025,20], outfile = 'HD143006_13CO.mom1')
