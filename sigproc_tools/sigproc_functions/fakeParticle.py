# the source of life
import numpy as np
    
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



