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

def electronicsReponse(tick,tickWidth):
    shapingTime = 1.3
    #arg = tick * tickWidth / shapingTime
    #return arg * np.exp(-arg)
    timeOffset  = 1.625
    binTime     = tick * tickWidth - timeOffset
    binTime     = np.where(binTime>0.,binTime,0.) / shapingTime
    leftArg     = 0.5 * np.multiply(0.9*binTime,0.9*binTime)
    rightArg    = 0.5 * np.multiply(0.5*binTime,0.5*binTime)
    rawResponse = np.multiply(1. - np.exp(-leftArg),np.exp(-rightArg))
    normFactor  = np.linalg.norm(rawResponse,axis=-1)
    if normFactor.ndim > 0:
        normFactor = normFactor.reshape((normFactor.shape)+(1,))
    return rawResponse / normFactor
    
def genWhiteNoiseWaveform(tickWidth,rms,shape):
    # Let's develop the white noise power spectrum for ICARUS... 
    # we need to start with the electronics response
    ticks = np.tile(np.arange(shape[1]),shape[0]).reshape(shape)
    
    print("ticks shape:",ticks.shape)

    electronicsWaveform = electronicsReponse(ticks,tickWidth)
    
    print("electronicsWaveform shape:",electronicsWaveform.shape)
    
    # Ok, now produce a "white noise" waveform
    whiteNoise = np.random.normal(loc=0.,scale=rms,size=shape)
    
    # Add in a spike just for fun
    #whiteNoise[:,1000] = 10*rms

    # FFTs of the two
    elecFFT  = np.fft.rfft(electronicsWaveform)
    whiteFFT = np.fft.rfft(whiteNoise)
    
    # convolve
    whiteResponse = np.multiply(elecFFT,whiteFFT)
    
    # back to time domain...
    whiteNoiseElec = np.fft.irfft(whiteResponse)
    
    return whiteNoiseElec

# Define model function to be used to fit to the data above:
def gaussParticle(x, *p):
    A, mu, sigma = p
    return A*np.exp(-(x-mu)**2/(2.*sigma**2))

# This intends to overlay a "particle trajectory" on top of input waveforms
# Creates a unipolar signal
def createGaussianParticle(waveforms,trackStartTick,trackAngle,pulseHeight,pulseWid):
    """
    This function will overlay "particle" onto waveforms with a transverse gaussian shape
    args  waveforms      - the waveforms we will overlay our track on - assume nChannels x nTicks
          trackStartTick - the starting tick for the track trajectory
          trackAngle     - angle with respect to wire direction of track trajectory
                           0: track is aligned with wire
                           pi/2: track is perpendicular to wire
          pulseHeight    - pulse height for gaussian charge deposit
          pulseWid       - pulse width for gaussian charge deposit
    """
    # Start with getting the channel coordinates
    # We need to find the maximum range for our gaussian shape 
    maxProjection = 4.*pulseWid/math.sin(trackAngle)
    lowStartTick  = trackStartTick - maxProjection
    hiStartTick   = trackStartTick + maxProjection

    # Remember that a tick in ICARUS is 0.4 us, drift velocity is ~1.6 mm/us so one tick is ~0.64 mm
    # Wire space is 3mm which means the distance between wires is ~4.7 ticks
    channelCoords = 4.7 * np.arange(waveforms.shape[0]) / math.tan(trackAngle)
    lowTicks      = channelCoords + lowStartTick
    hiTicks       = channelCoords + hiStartTick
    
    # We should make sure we don't exceed the tick range <== need to think about how to keep things right...
    #lowTicks = lowTicks[lowTicks>0]
    
    # Define our gauss parameters
    gaussParams = np.array([pulseHeight,0.,pulseWid])
    
    # Directly overlay on top of our input waveforms
    for wireIdx in range(channelCoords.shape[0]):
        # Ok, we calculate the gaussian distributed values perpendicular to the trajectory
        # of the track. If we go +/-4 sigma we are within a tenth of a percent of the area (or something)
        gaussRange = np.arange(-4.*pulseWid,4.*pulseWid,1.)
        gaussVals  = gaussParticle(gaussRange,*gaussParams)
        tickRange  = np.rint(np.arange(lowTicks[wireIdx],hiTicks[wireIdx],1.)).astype(np.int)
        for tickIdx in range(len(gaussVals)):
            # The following should work to project the gaussian shape (centered on the wire)
            # to the ticks along the wire. So, it should stretch the charge deposit.
            waveforms[wireIdx][tickRange[tickIdx]] += gaussVals[tickIdx]
    

# Use this one for creating a bipolar signal
def createGaussDerivativeParticle(waveforms,trackStartTick,trackAngle,pulseHeight,pulseWid):
    """
    args  waveforms      - the waveforms we will overlay our track on - assume nChannels x nTicks
          trackStartTick - the starting tick for the track trajectory
          trackAngle     - angle with respect to wire direction of track trajectory
                           0: track is aligned with wire
                           pi/2: track is perpendicular to wire
          pulseHeight    - pulse height for gaussian charge deposit
          pulseWid       - pulse width for gaussian charge deposit
    """
    # Start with getting the channel coordinates
    # We need to find the maximum range for our gaussian shape 
    maxProjection = 4.*pulseWid/math.sin(trackAngle)
    lowStartTick  = trackStartTick - maxProjection
    hiStartTick   = trackStartTick + maxProjection

    # Remember that a tick in ICARUS is 0.4 us, drift velocity is ~1.6 mm/us so one tick is ~0.64 mm
    # Wire space is 3mm which means the distance between wires is ~4.7 ticks
    channelCoords = 4.7 * np.arange(waveforms.shape[0]) / math.tan(trackAngle)
    lowTicks      = channelCoords + lowStartTick
    hiTicks       = channelCoords + hiStartTick
    
    # We should make sure we don't exceed the tick range <== need to think about how to keep things right...
    #lowTicks = lowTicks[lowTicks>0]
    
    # Define our gauss parameters
    gaussParams = np.array([pulseHeight,0.,pulseWid])
    
    # Directly overlay on top of our input waveforms
    for wireIdx in range(channelCoords.shape[0]):
        gaussRange = np.arange(-4.*pulseWid,4.*pulseWid,1.)
        gaussVals  = gaussParticle(gaussRange,*gaussParams)
        gaussDer   = np.gradient(gaussVals,0.15)
        if wireIdx == 110:
            print("der:",gaussDer[:])
        tickRange  = np.rint(np.arange(lowTicks[wireIdx],hiTicks[wireIdx],1.)).astype(np.int)
        for tickIdx in range(len(gaussDer)):
            waveforms[wireIdx][tickRange[tickIdx]] += gaussDer[tickIdx]



