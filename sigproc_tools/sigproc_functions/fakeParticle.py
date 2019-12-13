# the source of life
import numpy as np
import math
from sigproc_tools.sigproc_objects.fullresponse import FullResponse


def genWhiteNoiseWaveform(fullResponse,rms,shape):
    # This function will return a set of white noise waveforms, both "raw" 
    # and after convolution with the electronics respponse
    ticks = np.tile(np.arange(shape[1]),shape[0]).reshape(shape)
    
    print("ticks shape:",ticks.shape)
    
    # Ok, now produce a "white noise" waveform
    whiteNoise = np.random.normal(loc=0.,scale=rms,size=shape)

    # FFTs of the two
    whiteFFT = np.fft.rfft(whiteNoise)
    
    # convolve
    whiteResponseFFT = np.multiply(fullResponse.ResponseFFT,whiteFFT) #ElecResponseFFT,whiteFFT)
    
    # back to time domain...
    whiteResponse = no.rint(np.fft.irfft(whiteResponseFFT))

    print("whiteResponse shape",whiteResponse.shape,", whiteNoise shape:",whiteNoise.shape)
    
    return whiteResponse.astype(int),whiteNoise

def genSpikeWaveform(fullResponse,numElectrons,tick,shape):
    # This function will deposit numElectrons into a location "tick" of a set of waveforms of 
    # shape "shape" and then convolve with the response functions input in fullResponse to 
    # create a set of output waveforms
    electronicsGain = 67.4  # e-/tick from 0.027 fC/(ADC*us) x 0.4 us/tick x 6242.2 e-/fC

    if np.isscalar(shape):
        waveformLen = shape
    else:
        waveformLen = shape[-1]
    
    # Ok, now produce a "white noise" waveform
    inputWaveform = np.zeros(waveformLen)

    inputWaveform[tick] = numElectrons / electronicsGain

    # Now do the convolution to get a "real" waveform
    inputWaveformFFT = np.fft.rfft(inputWaveform)

    outputWaveformFFT = np.multiply(inputWaveformFFT,fullResponse.ResponseFFT)

    outputWaveform = np.rint(np.fft.irfft(outputWaveformFFT))

    # Need to roll to take into account the T0 offset
    outputWaveform = np.roll(outputWaveform,-int(fullResponse.T0Offset/fullResponse.TPCTickWidth))

    if not np.isscalar(shape):
        outputWaveform = np.tile(outputWaveform,shape[:-1]).reshape(shape)

    return outputWaveform.astype(int),inputWaveform

def createParticleTrajectory(fullResponse,numElectrons,trackWireRange,trackTickRange,shape):
    """
    This function will create a particle trajectory of the type described by the input "fullResponse" 
    respones functions. The particle will deposit a number of electrons per wire based on the input 
    "numElectrons" which is number of electrons per mm, starting and ending at the coordinates given 
    by trackWireRange and trackTickRange. The output waveforms will have the shape given by "shape"
    """
    # Create an empty waveform array
    waveforms = np.zeros(shape)
    inputWave = np.zeros(shape)

    # Some handy constants
    mmPerTick        = 0.64                   # so this is 1.6 mm/us * 0.4 us/tick
    mmPerWire        = 3.                     # so this is 3 mm/wire
    dTdW             = mmPerTick/mmPerWire    # This changes slope calculated in delta ticks / delta wires to unitless
    deltaWireInTicks = mmPerWire/mmPerTick   # so this is 3 mm / ticks2mm giving us wire spacing in ticks

    # Get track slope for setting tick as we step across wires
    tanThetaTW = (trackTickRange[1]-trackTickRange[0]) / (trackWireRange[1]-trackWireRange[0])
    tanTheta   = dTdW * tanThetaTW
    cosTheta   = 1./math.sqrt(1. + tanTheta*tanTheta)
    sinTheta   = tanTheta * cosTheta

    for wireIdx in range(trackWireRange[0],trackWireRange[1]):
        # The tricky part about this is that as the track angle becomes closer to the direction of 
        # the wire you need to spread the charge over more than a single tick... and so we need
        # to try to calcuate that here...
        # What is the central tick?
        #tick = int(round(tanThetaTW * (wireIdx - trackWireRange[0]) + trackTickRange[0]))
        # Note that convention is to follow the track by increasing wire number
        tickIn  = tanThetaTW * (wireIdx - trackWireRange[0] - 0.5) + trackTickRange[0]
        tickOut = tanThetaTW * (wireIdx - trackWireRange[0] + 0.5) + trackTickRange[0]

        # Watch for out of bounds conditions
        if tickIn < 0 or tickIn > 4095 or tickOut < 0 or tickOut > 4095:
            break;

        # First let's deetermine the total arclength for a 1 wire gap (-1/2 to +1/2) in mm
        arcLenInToOut = mmPerWire / cosTheta

        # how many intervening ticks?
        if tickIn < tickOut:  # equivalent to tanThetaTW > 0
            interveningTicks = math.floor(tickOut) - math.floor(tickIn)
        else:
            interveningTicks = math.floor(tickIn) - math.floor(tickOut)

        # Loop through the steps by the number of intervening wires
        for stepIdx in range(interveningTicks):
            # Here we take steps...
            tick     = math.floor(tickIn)
            tickNext = math.floor(tickIn+1)

            if tickIn > tickOut:
                tickNext = math.floor(tickIn-1)

            stepArcLen = (tickNext - tickIn) * mmPerTick / sinTheta
        
            tempWaveforms,tempInput  = genSpikeWaveform(fullResponse,numElectrons*stepArcLen,tick,shape[-1])
            waveforms[wireIdx]      += tempWaveforms
            inputWave[wireIdx]      += tempInput

            tickIn         = tickNext
            arcLenInToOut -= stepArcLen
 
        # Now handle the final step
        tick   = math.floor(tickOut)

        tempWaveforms,tempInput    = genSpikeWaveform(fullResponse,numElectrons*arcLenInToOut,tick,shape[-1])
        waveforms[wireIdx] += tempWaveforms
        inputWave[wireIdx] += tempInput

    return waveforms,inputWave

# Below code is "old" since it does not use the response functions. Left for reference
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



