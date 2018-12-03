import numpy as np
from scipy.integrate import quad


def calc_contrast(gaprad, ringrad, radbins, radprofile, uncertainty, cont, high_incl = False):
    gapindex = np.argmin(np.abs(radbins-gaprad))
    ringindex = np.argmin(np.abs(radbins-ringrad))
    gapintensity = radprofile[gapindex]
    ringintensity = radprofile[ringindex]
    contrast = gapintensity/ringintensity

    if high_incl:
        arc = 2*quad(lambda t: np.sqrt(np.cos(cont.incl*np.pi/180.)**2*np.sin(t)**2+np.cos(t)**2),7/18.*np.pi,11/18.*np.pi )[0]
        gap_p = gaprad*arc
        ring_p = ringrad*arc


    elif '143006' in cont.header['OBJECT']:
        arc = np.pi*(3*(1+np.cos(cont.incl*np.pi/180))-np.sqrt((1+3*np.cos(cont.incl*np.pi/180))*(3+np.cos(cont.incl*np.pi/180))))-quad(lambda t: np.sqrt(np.cos(cont.incl*np.pi/180.)**2*np.sin(t)**2+np.cos(t)**2),4/9.*np.pi,0.8*np.pi )[0]
        gap_p = gaprad*arc
        ring_p = ringrad*arc

    elif '163296' in cont.header['OBJECT']:
        arc = np.pi*(3*(1+np.cos(cont.incl*np.pi/180))-np.sqrt((1+3*np.cos(cont.incl*np.pi/180))*(3+np.cos(cont.incl*np.pi/180))))-quad(lambda t: np.sqrt(np.cos(cont.incl*np.pi/180.)**2*np.sin(t)**2+np.cos(t)**2),5/18.*np.pi,13/18.*np.pi )[0]
        gap_p = gaprad*arc
        ring_p = ringrad*arc
        
        
    else:
        gap_p = np.pi*gaprad*(3*(1+np.cos(cont.incl*np.pi/180))-np.sqrt((1+3*np.cos(cont.incl*np.pi/180))*(3+np.cos(cont.incl*np.pi/180))))
        ring_p = np.pi*ringrad*(3*(1+np.cos(cont.incl*np.pi/180))-np.sqrt((1+3*np.cos(cont.incl*np.pi/180))*(3+np.cos(cont.incl*np.pi/180))))

    gap_n = gap_p/(cont.bmaj*cont.src_distance)
    ring_n = ring_p/(cont.bmaj*cont.src_distance)
    delta_contrast = contrast*np.sqrt((uncertainty[gapindex]/gapintensity)**2/gap_n+(uncertainty[ringindex]/ringintensity)**2/ring_n)
    return contrast, delta_contrast


def measure_widths(gaprad, ringrad, radbins, radprofile, innerlimit, outerlimit):
    radbins2 = np.arange(0.5, np.max(radbins), 0.1)
    interpprofile = np.interp(radbins2, radbins, radprofile)
    gapindex = np.argmin(np.abs(radbins2-gaprad))
    ringindex = np.argmin(np.abs(radbins2-ringrad))
    gapintensity = interpprofile[gapindex]
    ringintensity = interpprofile[ringindex]
    meanintensity = 0.5*(gapintensity+ringintensity)
    rmean = radbins2[np.argmin(np.abs(interpprofile[gapindex:ringindex]-meanintensity))+gapindex]
    print(meanintensity, rmean)
    gapwidth = rmean-radbins2[10*innerlimit:gapindex][np.argmin(np.abs(interpprofile[10*innerlimit:gapindex]-meanintensity))]
    ringwidth = radbins2[ringindex:outerlimit*10][np.argmin(np.abs(interpprofile[ringindex:10*outerlimit]-meanintensity))]-rmean
    return gapwidth, ringwidth


