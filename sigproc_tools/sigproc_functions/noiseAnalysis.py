# the source of life
import numpy as np
import scipy.stats as stats
import scipy.signal as signal

import math

# Provide some of the basic functions for doing analysis of waveforms

def computeCorrelations(waveforms,numEvents,nGroups):
    # Assume input waveforms have shape [numEvents,nGroups,nTicks]
    statCorMatrix = np.zeros((nGroups,nGroups))
    xcorCorMatrix = np.zeros((nGroups,nGroups))
    
    print("Computing correlations over",numEvents," events and",nGroups," groups")
    
    for eventToCheck in range(numEvents):
        for outIdx in range(nGroups):
            # Try to prevent double counting... and the result should be obvious but just in case...
            stat,pValue = stats.pearsonr(waveforms[eventToCheck,outIdx,:],waveforms[eventToCheck,outIdx,:])
            statCorMatrix[outIdx,outIdx] += stat    
            corr    = signal.correlate(waveforms[eventToCheck,outIdx,:],waveforms[eventToCheck,outIdx,:],mode='same') / 4096
            xCorMax = corr[2048]
            xcorCorMatrix[outIdx,outIdx] += 1.
            
            # Now loop through off diagonal components
            for inIdx in range(outIdx+1,nGroups,1):
                stat,pValue = stats.pearsonr(waveforms[eventToCheck,outIdx,:],waveforms[eventToCheck,inIdx,:])
                statCorMatrix[outIdx,inIdx] += stat
                statCorMatrix[inIdx,outIdx] += stat
                corr = signal.correlate(waveforms[eventToCheck,outIdx,:],waveforms[eventToCheck,inIdx,:],mode='same') / 4096
                xcorCorMatrix[outIdx,inIdx] += corr[2048]/xCorMax
                xcorCorMatrix[inIdx,outIdx] += corr[2048]/xCorMax
        
        if eventToCheck%10 == 0:
            print("--> Done with event ",eventToCheck)
    
    # Normalize to number of events
    statCorMatrix /= 100.
    xcorCorMatrix /= 100.
    
    return statCorMatrix,xcorCorMatrix

def getPowerVec(waveforms,maxFrequency):
    meanValue = np.mean(waveforms,axis=-1)
    
    newShape = (meanValue.shape)+(1,)
    
    if meanValue.ndim > 0:
        meanValue = meanValue.reshape((meanValue.shape)+(1,))
    
    corWave = waveforms - meanValue
    
    # Use scipy to compute the power spectrum directly
    freqVec, powerVec = signal.periodogram(corWave,maxFrequency) #,axis=-1)
    
    return freqVec,powerVec
