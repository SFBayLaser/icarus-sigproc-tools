# Basic noise processing functions operating on input waveforms
# Straightforward functions for getting pedestals, rms, etc. and also 
# handling coherent noise
#
# Assuming input waveforms have last dimension to be the waveforms

import numpy as np

def getPedestalsAndRMS(waveforms):
    pedestals = np.mean(waveforms,axis=-1)
    if pedestals.ndim > 0:
        waveLessPed = waveforms - pedestals.reshape((pedestals.shape)+(1,))
    else:
        waveLessPed = waveforms - pedestals
    rms = np.sqrt(np.mean(np.square(waveLessPed),axis=-1))
    return waveLessPed,pedestals,rms

def getCoherentNoiseCorrection(waveforms):
    median           = np.median(waveforms,axis=0)
    waveLessCoherent = waveforms - median.transpose()
    rms              = np.sqrt(np.mean(np.square(waveLessCoherent),axis=0))
    return waveLessCoherent,median,rms

def removeCoherentNoise(waveforms,grouping):
    # Define placeholders for the output arrays
    waveLessCoherent = np.array([0])
    median           = np.array([0])
    intrinsicRMS     = np.array([0])
    
    nChannels = waveforms.shape[0]
    
    for idx in range(0,nChannels,grouping):
        temp,tempMed,tempRMS = getCoherentNoiseCorrection(waveforms[idx:idx+grouping,:])
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

