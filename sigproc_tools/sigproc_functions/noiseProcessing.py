# Basic noise processing functions operating on input waveforms
# Straightforward functions for getting pedestals, rms, etc. and also 
# handling coherent noise
#
# Assuming input waveforms have last dimension to be the waveforms

import numpy as np
import scipy.ndimage as ndimage

def getPedestalsAndRMS(waveforms):
    pedestals = np.median(waveforms,axis=-1)
    if pedestals.ndim > 0:
        waveLessPed = waveforms - pedestals.reshape((pedestals.shape)+(1,))
    else:
        waveLessPed = waveforms - pedestals
    rms = np.sqrt(np.mean(np.square(waveLessPed),axis=-1))
    return waveLessPed,pedestals,rms

def getMedianNoiseCorrection(waveforms):
    median           = np.median(waveforms,axis=0)
    waveLessCoherent = waveforms - median.transpose()
    rms              = np.sqrt(np.mean(np.square(waveLessCoherent),axis=0))
    return waveLessCoherent,median,rms

def removeCoherentNoise(waveforms,grouping,nTicks):
    # Define placeholders for the output arrays
    waveLessCoherent = np.array([0])
    median           = np.array([0])
    intrinsicRMS     = np.array([0])
    
    nChannels = waveforms.shape[0]
    
    for idx in range(0,nChannels,grouping):
        temp,tempMed,tempRMS = getMedianNoiseCorrection(waveforms[idx:idx+grouping,:])
        if idx == 0:
            waveLessCoherent = temp
            median           = tempMed
            intrinsicRMS     = tempRMS
        else:
            waveLessCoherent = np.concatenate((waveLessCoherent,temp),axis=0)
            median           = np.concatenate((median,tempMed),axis=0)
            intrinsicRMS     = np.concatenate((intrinsicRMS,tempRMS),axis=0)
        
    median       = median.transpose().reshape(nChannels//grouping,nTicks)         # Now we make a 2D array of 384 channels by 4096+2 ticks
    intrinsicRMS = intrinsicRMS.transpose().reshape(nChannels//grouping,nTicks)   # Now we make a 2D array of 384 channels by 4096+2 ticks

    return waveLessCoherent,median,intrinsicRMS

def removeCoherentNoiseMorphCollection(waveforms,grouping,nTicks,structuringElement=(3,6)):
    nChannels = waveforms.shape[0]
    nGroups   = nChannels // grouping
    
    # Define placeholders for the output arrays
    waveLessCoherent = np.zeros(waveforms.shape)
    median           = np.zeros((nGroups,nTicks))
    intrinsicRMS     = np.zeros((nGroups,nTicks))
    
    for idx in range(0,nChannels,grouping):
#        erosion      = ndimage.grey_erosion(waveforms[idx:idx+grouping,:],size=structuringElement)
        dilation     = ndimage.grey_dilation(waveforms[idx:idx+grouping,:],size=structuringElement)
        dilationMed  = np.median(dilation,axis=-1)
        dilationBase = dilation - dilationMed[:,None]
        dilationRMS  = np.sqrt(np.mean(np.square(dilationBase),axis=-1))
        selectVals   = dilationMed + 2.5 * dilationRMS
        thisGroup    = idx // grouping

        median[thisGroup,:]                  = np.median(np.where(dilation<selectVals[:,None],waveforms[idx:idx+grouping,:],0.),axis=0)
        waveLessCoherent[idx:idx+grouping,:] = waveforms[idx:idx+grouping,:] - median[thisGroup,:]
        intrinsicRMS[thisGroup,:]            = np.sqrt(np.mean(np.square(waveLessCoherent[idx:idx+grouping,:]),axis=0))
        
    return waveLessCoherent,median,intrinsicRMS

def removeCoherentNoiseMorphInduction(waveforms,grouping,nTicks,structuringElement=(3,6)):
    nChannels = waveforms.shape[0]
    nGroups   = nChannels // grouping
    
    # Define placeholders for the output arrays
    waveLessCoherent = np.zeros(waveforms.shape)
    median           = np.zeros((nGroups,nTicks))
    intrinsicRMS     = np.zeros((nGroups,nTicks))
    
    for idx in range(0,nChannels,grouping):
        gradient     = ndimage.grey_dilation(waveforms[idx:idx+grouping,:],size=structuringElement) \
                     - ndimage.grey_erosion(waveforms[idx:idx+grouping,:],size=structuringElement)
        gradientMed  = np.median(gradient,axis=-1)
        gradientBase = gradient - gradientMed[:,None]
        gradientRMS  = np.sqrt(np.mean(np.square(gradientBase),axis=-1))
        print("Group:",idx,", median:",gradientMed,",\n rms:",gradientRMS)
        selectVals   = 2.5 * gradientRMS
        thisGroup    = idx // grouping

        median[thisGroup,:]                  = np.median(np.where(gradientBase<selectVals[:,None],waveforms[idx:idx+grouping,:],0.),axis=0)
        waveLessCoherent[idx:idx+grouping,:] = waveforms[idx:idx+grouping,:] - median[thisGroup,:]
        intrinsicRMS[thisGroup,:]            = np.sqrt(np.mean(np.square(waveLessCoherent[idx:idx+grouping,:]),axis=0))
        
    return waveLessCoherent,median,intrinsicRMS


